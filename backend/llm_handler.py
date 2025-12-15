"""
LLM Handler for Ollama Deepseek Integration
"""
import ollama
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class ChatbotLLM:
    """LLM Handler for HR Chatbot using Ollama Deepseek"""

    def __init__(self):
        self.model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    def create_system_prompt(self) -> str:
        """Create the system prompt for the HR chatbot"""
        return """You are an HR assistant for Itlize Global LLC helping staff with employee information, visa status, benefits, and policies.

Use only the provided context to answer. Be professional and concise. Reference employee IDs and expiration dates when relevant. If information is missing, say so clearly."""

    def format_conversation_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format conversation history for Ollama"""
        messages = []
        for msg in history[-5:]:  # Keep last 5 messages for context
            # Handle both dict and Pydantic model
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                # Pydantic model
                role = getattr(msg, "role", "user")
                content = getattr(msg, "content", "")

            messages.append({
                "role": role,
                "content": content
            })
        return messages

    async def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate response using Ollama Deepseek model

        Args:
            query: User's question
            context: Relevant context from database
            conversation_history: Previous conversation messages

        Returns:
            Generated response string
        """
        try:
            # Build the prompt with context
            user_message = f"""Context from HR Database:
{context}

User Question: {query}

Please provide a helpful and accurate answer based on the context provided. If the context doesn't contain the information needed, acknowledge this and provide general guidance if possible."""

            # Prepare messages
            messages = [
                {"role": "system", "content": self.create_system_prompt()}
            ]

            # Add conversation history if available
            if conversation_history:
                formatted_history = self.format_conversation_history(conversation_history)
                messages.extend(formatted_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call Ollama API
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )

            # Extract response content
            if response and "message" in response:
                return response["message"]["content"]
            else:
                return "I apologize, but I encountered an issue generating a response. Please try again."

        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}. Please ensure Ollama is running with the command 'ollama run deepseek-r1:8b'"

    async def generate_response_stream(
        self,
        query: str,
        context: str,
        conversation_history: List[dict] = None
    ):
        """
        Generate streaming response from LLM with context
        Yields chunks of text as they're generated
        """
        try:
            # Format user message with context
            user_message = f"""Context from HR Database:
{context}

User Question: {query}

Please provide a helpful and accurate answer based on the context provided."""

            # Build messages array
            messages = [{"role": "system", "content": self.create_system_prompt()}]

            # Add conversation history (last 5 messages)
            if conversation_history:
                recent_history = conversation_history[-5:]
                for msg in recent_history:
                    if hasattr(msg, 'role'):
                        messages.append({"role": msg.role, "content": msg.content})
                    else:
                        messages.append({"role": msg["role"], "content": msg["content"]})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Stream response from Ollama
            stream = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=True,  # Enable streaming
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )

            # Yield chunks as they arrive
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            print(f"Error generating streaming response: {e}")
            yield f"Error: Unable to generate response. Please ensure Ollama is running."

    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            print(f"Ollama connection test failed: {e}")
            return False

# Quick test function
if __name__ == "__main__":
    print("Testing Ollama Deepseek connection...")
    llm = ChatbotLLM()

    if llm.test_connection():
        print("✓ Ollama connection successful!")

        # Test query
        import asyncio
        test_query = "What are the health insurance options available?"
        test_context = "Medical Plans: Plan 1 ($168.31/month) and Plan 2 ($151.05/month)"

        async def test():
            response = await llm.generate_response(test_query, test_context)
            print(f"\nTest Query: {test_query}")
            print(f"Response: {response}")

        asyncio.run(test())
    else:
        print("✗ Ollama connection failed. Please ensure Ollama is running.")
        print("Run: ollama run deepseek-r1:8b")

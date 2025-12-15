"""
HRMS AI Chatbot - FastAPI Backend Server
With Role-Based Access Control
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from contextlib import asynccontextmanager

from database import db
from auth import authenticate, AuthRequest, AuthResponse, verify_credentials, verify_password
from llm_handler import ChatbotLLM
from rag_pipeline import rag

# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    password: str
    username: Optional[str] = None  # For RBAC - if provided, uses role-based auth
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    authenticated: bool

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] Starting HRMS AI Chatbot Server...")
    db.connect()
    yield
    # Shutdown
    print("[*] Shutting down HRMS AI Chatbot Server...")
    db.close()

# Create FastAPI app
app = FastAPI(
    title="HRMS AI Chatbot API",
    description="AI-powered HR Management System Chatbot using Deepseek LLM with Role-Based Access Control",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3002"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM handler
chatbot_llm = ChatbotLLM()

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HRMS AI Chatbot API",
        "status": "running",
        "version": "1.1.0",
        "features": ["role-based-access-control", "streaming-responses"]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected",
        "llm": "ready"
    }

@app.post("/api/auth", response_model=AuthResponse)
async def auth_endpoint(auth_request: AuthRequest):
    """Authentication endpoint - supports username/password authentication"""
    return await authenticate(auth_request.username, auth_request.password)

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """
    Main chat endpoint - processes user messages and returns AI responses with streaming
    Supports role-based access control when username is provided
    """
    user_role = "hr_lead"  # Default to full access for backward compatibility
    username = "anonymous"

    # New authentication: username + password (RBAC)
    if chat_request.username:
        user_info = verify_credentials(chat_request.username, chat_request.password)
        if not user_info:
            return StreamingResponse(
                iter(["Authentication failed. Invalid username or password."]),
                media_type="text/plain"
            )
        user_role = user_info["role"]
        username = user_info["username"]
    else:
        # Legacy authentication: password only (backward compatibility)
        if not verify_password(chat_request.password):
            return StreamingResponse(
                iter(["Authentication failed. Please provide valid credentials."]),
                media_type="text/plain"
            )
        # Legacy mode defaults to hr_lead for backward compatibility
        user_role = "hr_lead"
        username = "legacy_user"

    try:
        # Get relevant context using RAG pipeline WITH ROLE-BASED FILTERING
        context, metadata = rag.retrieve_context(
            chat_request.message,
            user_role=user_role  # Pass user role for access control
        )

        print(f"Query: {chat_request.message}")
        print(f"User: {username} (Role: {user_role})")
        print(f"Query Types: {metadata['query_types']}")
        print(f"Access Restricted: {metadata.get('access_restricted', False)}")
        print(f"Sources Used: {metadata['sources_used']}")

        # Generate streaming response
        async def generate():
            async for chunk in chatbot_llm.generate_response_stream(
                query=chat_request.message,
                context=context,
                conversation_history=chat_request.conversation_history
            ):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )

    except Exception as e:
        print(f"Error processing streaming chat request: {e}")
        return StreamingResponse(
            iter([f"Error processing request: {str(e)}"]),
            media_type="text/plain"
        )

@app.get("/api/employees/{employee_id}")
async def get_employee(employee_id: int):
    """Get employee information by ID"""
    employee = db.get_employee_by_id(employee_id)
    if employee:
        # Convert ObjectId to string for JSON serialization
        employee["_id"] = str(employee["_id"])
        return employee
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found"
        )

@app.get("/api/questions")
async def get_possible_questions():
    """Get list of possible/suggested questions"""
    questions = db.get_possible_questions()
    # Convert ObjectId to string
    for q in questions:
        q["_id"] = str(q["_id"])
    return questions

if __name__ == "__main__":
    print("""
    ================================================
        HRMS AI Chatbot Backend Server
        Powered by FastAPI + Deepseek LLM
        With Role-Based Access Control
    ================================================
    """)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

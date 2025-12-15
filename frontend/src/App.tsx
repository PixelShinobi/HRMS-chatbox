import { useState, useEffect, useRef } from 'react';
import Login from './components/Login';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { chatAPI } from './api';
import type { Message, UserSession } from './types';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userSession, setUserSession] = useState<UserSession | null>(null);
  const [password, setPassword] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add welcome message on successful login
  useEffect(() => {
    if (isAuthenticated && userSession && messages.length === 0) {
      const isLead = userSession.role === 'hr_lead';
      const welcomeContent = isLead
        ? `Hello ${userSession.username}! I'm your HR assistant with full access. I can help you with:

- Employee information (ID, join date, position, salary)
- Immigration and visa status with expiration dates
- Termination records and employment history
- Benefits information (health insurance, dental, vision, 401k)
- Company policies (sick days, vacation, holidays)
- Employment agreements and contracts

How can I assist you today?`
        : `Hello ${userSession.username}! I'm your HR assistant. As a Junior HR member, I can help you with:

- Benefits information (health insurance, dental, vision plans)
- Company policies (PTO, sick days, holidays)
- Aggregate statistics (employee counts, visa distributions)
- General employee information (position, join date)

Note: Salary details, specific visa expiration dates, and termination records require HR Lead access.

How can I assist you today?`;

      setMessages([
        {
          role: 'assistant',
          content: welcomeContent,
          timestamp: new Date(),
        },
      ]);
    }
  }, [isAuthenticated, userSession]);

  const handleLogin = async (username: string, pwd: string) => {
    setLoginError('');
    try {
      const response = await chatAPI.authenticate({ username, password: pwd });
      if (response.authenticated) {
        setPassword(pwd);
        setUserSession({
          username: response.username || username,
          role: response.role || 'hr_junior',
        });
        setIsAuthenticated(true);
      } else {
        setLoginError('Invalid username or password. Please try again.');
      }
    } catch (error) {
      setLoginError('Unable to connect to server. Please ensure the backend is running.');
      console.error('Authentication error:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Create placeholder for assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      let fullResponse = '';

      // Stream the response with username for RBAC
      await chatAPI.sendMessageStream(
        {
          message: content,
          password: password,
          username: userSession?.username,
          conversation_history: messages,
        },
        (chunk: string) => {
          fullResponse += chunk;
          // Update the assistant message with accumulated chunks
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: 'assistant',
              content: fullResponse,
              timestamp: new Date(),
            };
            return updated;
          });
        }
      );
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please ensure the backend server and Ollama are running.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPassword('');
    setUserSession(null);
    setMessages([]);
    setLoginError('');
  };

  // Role-specific suggested questions
  const getSuggestedQuestions = () => {
    if (userSession?.role === 'hr_lead') {
      return [
        "What is the salary of employee 1503?",
        "Which employees have visas expiring in 6 months?",
        "Show me all terminated employees",
        "What is employee 1472's visa expiration date?",
      ];
    }
    return [
      "How many employees have H-1B visas?",
      "Tell me about our health insurance plans",
      "What are the sick day and vacation policies?",
      "What dental benefits do we offer?",
    ];
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} error={loginError} />;
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">HRMS AI Chatbot</h1>
            <p className="text-sm text-gray-500">Ask me anything about HR</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* User Info Badge */}
          <div className="flex items-center gap-2">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">{userSession?.username}</div>
              <div className={`text-xs px-2 py-0.5 rounded-full inline-block ${
                userSession?.role === 'hr_lead'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {userSession?.role === 'hr_lead' ? 'HR Lead' : 'HR Junior'}
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              setMessages([]);
              const isLead = userSession?.role === 'hr_lead';
              setMessages([
                {
                  role: 'assistant',
                  content: `Hello ${userSession?.username}! How can I help you today?${!isLead ? '\n\nRemember: Some data is restricted to HR Lead access.' : ''}`,
                  timestamp: new Date(),
                },
              ]);
            }}
            className="text-sm text-gray-600 hover:text-gray-900 font-medium"
          >
            Clear Chat
          </button>
          <button
            onClick={handleLogout}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="bg-gray-100 rounded-2xl px-5 py-3">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="max-w-4xl mx-auto w-full">
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>

      {/* Suggested Questions (shown when only welcome message) */}
      {messages.length === 1 && (
        <div className="max-w-4xl mx-auto w-full px-6 pb-4">
          <div className="text-sm text-gray-600 mb-3 font-medium">Try asking:</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {getSuggestedQuestions().map((question, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(question)}
                className="text-left text-sm bg-white border border-gray-200 px-4 py-3 rounded-lg hover:bg-gray-50 hover:border-indigo-300 transition"
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

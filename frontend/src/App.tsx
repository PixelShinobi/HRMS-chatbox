import { useState, useEffect, useRef } from 'react';
import jsPDF from 'jspdf';
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
  const [darkMode, setDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
  }, []);

  // Update dark mode class on document
  useEffect(() => {
    console.log('Dark mode changed:', darkMode);
    if (darkMode) {
      document.documentElement.classList.add('dark');
      console.log('Added dark class to html element');
    } else {
      document.documentElement.classList.remove('dark');
      console.log('Removed dark class from html element');
    }
    localStorage.setItem('darkMode', darkMode.toString());
  }, [darkMode]);

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
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      let fullResponse = '';

      await chatAPI.sendMessageStream(
        {
          message: content,
          password: password,
          username: userSession?.username,
          conversation_history: messages,
        },
        (chunk: string) => {
          fullResponse += chunk;
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

  const exportToPDF = () => {
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - 2 * margin;
    let yPosition = margin;

    // Title
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('HRMS Chatbot Conversation', margin, yPosition);
    yPosition += 10;

    // User info
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`User: ${userSession?.username} (${userSession?.role === 'hr_lead' ? 'HR Lead' : 'HR Junior'})`, margin, yPosition);
    yPosition += 5;
    pdf.text(`Date: ${new Date().toLocaleString()}`, margin, yPosition);
    yPosition += 10;

    // Messages
    pdf.setFontSize(10);
    messages.forEach((message, index) => {
      // Check if we need a new page
      if (yPosition > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }

      // Message header
      pdf.setFont('helvetica', 'bold');
      const header = message.role === 'user' ? 'You:' : 'HR Assistant:';
      pdf.text(header, margin, yPosition);
      yPosition += 6;

      // Message content
      pdf.setFont('helvetica', 'normal');
      const lines = pdf.splitTextToSize(message.content, maxWidth);

      lines.forEach((line: string) => {
        if (yPosition > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        pdf.text(line, margin, yPosition);
        yPosition += 5;
      });

      yPosition += 5; // Space between messages
    });

    // Save PDF
    const filename = `HRMS_Chat_${userSession?.username}_${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(filename);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPassword('');
    setUserSession(null);
    setMessages([]);
    setLoginError('');
  };

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
    return <Login onLogin={handleLogin} error={loginError} darkMode={darkMode} />;
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 dark:bg-indigo-500 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">HRMS AI Chatbot</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Ask me anything about HR</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* User Info Badge */}
            <div className="flex items-center gap-2">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900 dark:text-white">{userSession?.username}</div>
                <div className={`text-xs px-2 py-0.5 rounded-full inline-block ${
                  userSession?.role === 'hr_lead'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                }`}>
                  {userSession?.role === 'hr_lead' ? 'HR Lead' : 'HR Junior'}
                </div>
              </div>
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? (
                <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>

            {/* Export PDF */}
            <button
              onClick={exportToPDF}
              disabled={messages.length === 0}
              className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              title="Export conversation to PDF"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export PDF
            </button>

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
              className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium"
            >
              Clear Chat
            </button>
            <button
              onClick={handleLogout}
              className="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-4xl mx-auto">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} darkMode={darkMode} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-600 dark:bg-gray-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-5 py-3">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
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
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} darkMode={darkMode} />
        </div>

        {/* Suggested Questions */}
        {messages.length === 1 && (
          <div className="max-w-4xl mx-auto w-full px-6 pb-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-3 font-medium">Try asking:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {getSuggestedQuestions().map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(question)}
                  className="text-left text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-4 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-indigo-300 dark:hover:border-indigo-500 transition text-gray-900 dark:text-gray-100"
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

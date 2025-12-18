import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
  darkMode?: boolean;
}

export default function ChatMessage({ message, darkMode }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fadeIn`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'bg-indigo-600' : darkMode ? 'bg-gray-600' : 'bg-gray-600'
        }`}>
          {isUser ? (
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          )}
        </div>

        {/* Message bubble */}
        <div className={`rounded-2xl px-5 py-3 ${
          isUser
            ? 'bg-indigo-600 text-white'
            : darkMode
            ? 'bg-gray-700 text-gray-100'
            : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="text-sm font-medium mb-1">
            {isUser ? 'You' : 'HR Assistant'}
          </div>
          <div className="text-base whitespace-pre-wrap break-words">
            {message.content}
          </div>
          {message.timestamp && (
            <div className={`text-xs mt-2 ${
              isUser
                ? 'text-indigo-200'
                : darkMode
                ? 'text-gray-400'
                : 'text-gray-500'
            }`}>
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

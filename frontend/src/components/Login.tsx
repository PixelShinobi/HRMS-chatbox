import { useState } from 'react';

interface LoginProps {
  onLogin: (username: string, password: string) => void;
  error?: string;
  darkMode?: boolean;
}

export default function Login({ onLogin, error, darkMode }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim() && password.trim()) {
      onLogin(username, password);
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gradient-to-br from-gray-800 to-gray-900' : 'bg-gradient-to-br from-blue-50 to-indigo-100'}`}>
      <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} p-8 rounded-2xl shadow-xl w-full max-w-md`}>
        <div className="text-center mb-8">
          <div className={`inline-block p-3 ${darkMode ? 'bg-indigo-900' : 'bg-indigo-100'} rounded-full mb-4`}>
            <svg
              className={`w-12 h-12 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-2`}>
            HRMS AI Chatbot
          </h1>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Sign in to access the HR assistant
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-2`}
            >
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full px-4 py-3 border ${darkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900'} rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition`}
              placeholder="Enter username"
              autoFocus
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-2`}
            >
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`w-full px-4 py-3 border ${darkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900'} rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition`}
                placeholder="Enter password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className={`absolute right-3 top-1/2 -translate-y-1/2 ${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'}`}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className={`${darkMode ? 'bg-red-900 border-red-700 text-red-200' : 'bg-red-50 border-red-200 text-red-700'} border px-4 py-3 rounded-lg text-sm`}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 transition duration-200"
          >
            Login
          </button>
        </form>

        <div className={`mt-6 p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'} rounded-lg`}>
          <div className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'} font-medium mb-2`}>Demo Credentials:</div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>HR Lead (Full Access):</span>
              <code className={`${darkMode ? 'bg-gray-800 text-indigo-400' : 'bg-white text-indigo-600'} px-2 py-0.5 rounded`}>alice / lead123</code>
            </div>
            <div className="flex justify-between">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>HR Junior (Restricted):</span>
              <code className={`${darkMode ? 'bg-gray-800 text-indigo-400' : 'bg-white text-indigo-600'} px-2 py-0.5 rounded`}>bob / junior456</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

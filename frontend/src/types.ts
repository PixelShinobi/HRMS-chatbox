export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export interface ChatRequest {
  message: string;
  password: string;
  username?: string;  // For RBAC - if provided, uses role-based auth
  conversation_history?: Message[];
}

export interface ChatResponse {
  response: string;
  authenticated: boolean;
}

export interface AuthRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  authenticated: boolean;
  message: string;
  username?: string;
  role?: 'hr_lead' | 'hr_junior';
}

export interface UserSession {
  username: string;
  role: 'hr_lead' | 'hr_junior';
}

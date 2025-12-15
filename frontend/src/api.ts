import axios from 'axios';
import type { ChatRequest, ChatResponse, AuthRequest, AuthResponse } from './types';

const API_BASE_URL = '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  /**
   * Send a chat message with streaming response
   */
  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error('Failed to get streaming response');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    }
  },

  /**
   * Authenticate with password
   */
  async authenticate(request: AuthRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth', request);
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await api.get('/api/health');
    return response.data;
  },

  /**
   * Get employee by ID
   */
  async getEmployee(employeeId: number): Promise<any> {
    const response = await api.get(`/api/employees/${employeeId}`);
    return response.data;
  },

  /**
   * Get possible questions
   */
  async getPossibleQuestions(): Promise<any[]> {
    const response = await api.get('/api/questions');
    return response.data;
  },
};

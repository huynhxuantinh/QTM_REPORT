import { apiClient } from '@/api/client';
import { LoginRequest, TokenResponse } from '@/types/auth';

export const authService = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', payload);
    return response.data;
  },

  async checkHealth(): Promise<{ status: string }> {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  },
};

import { apiClient } from '@/api/client';
import { SystemSettings } from '@/types/settings';

export const settingsService = {
  async get(): Promise<SystemSettings> {
    const response = await apiClient.get<SystemSettings>('/settings');
    return response.data;
  },

  async update(payload: SystemSettings): Promise<SystemSettings> {
    const response = await apiClient.put<SystemSettings>('/settings', payload);
    return response.data;
  },
};

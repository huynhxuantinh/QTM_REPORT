import { apiClient } from '@/api/client';
import { DashboardSummary } from '@/types/dashboard';

export const dashboardService = {
  async getSummary(): Promise<DashboardSummary> {
    const response = await apiClient.get<DashboardSummary>('/dashboard/summary');
    return response.data;
  },
};

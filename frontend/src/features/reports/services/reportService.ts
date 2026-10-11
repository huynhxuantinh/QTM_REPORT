import { apiClient } from '@/api/client';
import { HealthStatus } from '@/types/health';

export interface ReportFilterParams {
  date_from?: string;
  date_to?: string;
  device_id?: number;
  site?: string;
  status?: HealthStatus;
}

export const reportService = {
  async downloadCsv(filters: ReportFilterParams): Promise<Blob> {
    const response = await apiClient.get('/reports/csv', {
      params: filters,
      responseType: 'blob',
    });
    return response.data;
  },

  async downloadPdf(filters: ReportFilterParams): Promise<Blob> {
    const response = await apiClient.get('/reports/pdf', {
      params: filters,
      responseType: 'blob',
    });
    return response.data;
  },

  async downloadXlsx(filters: ReportFilterParams): Promise<Blob> {
    const response = await apiClient.get('/reports/xlsx', {
      params: filters,
      responseType: 'blob',
    });
    return response.data;
  },
};

import { apiClient } from '@/api/client';
import { CheckAccepted, HealthCheck, HealthCheckPage } from '@/types/health';
import { ScanRun, ScanRunAccepted } from '@/types/scan';

export const checkService = {
  async runAll(): Promise<ScanRunAccepted> {
    const response = await apiClient.post<ScanRunAccepted>('/checks/run-all');
    return response.data;
  },

  async getScanRun(scanId: number): Promise<ScanRun> {
    const response = await apiClient.get<ScanRun>(`/scan-runs/${scanId}`);
    return response.data;
  },

  async startCheck(deviceId: number): Promise<CheckAccepted> {
    const response = await apiClient.post<CheckAccepted>(`/devices/${deviceId}/checks`);
    return response.data;
  },

  async getCheck(checkId: number): Promise<HealthCheck> {
    const response = await apiClient.get<HealthCheck>(`/checks/${checkId}`);
    return response.data;
  },

  async getDeviceHistory(
    deviceId: number,
    params?: { offset?: number; limit?: number }
  ): Promise<HealthCheckPage> {
    const response = await apiClient.get<HealthCheckPage>(`/devices/${deviceId}/history`, {
      params,
    });
    return response.data;
  },
};

import { apiClient } from '@/api/client';
import {
  ConnectionTestResult,
  Device,
  DeviceCreatePayload,
  DevicePage,
  DeviceUpdatePayload,
} from '@/types/device';

export const deviceService = {
  async list(params?: { offset?: number; limit?: number; site?: string }): Promise<DevicePage> {
    const response = await apiClient.get<DevicePage>('/devices', { params });
    return response.data;
  },

  async get(id: number): Promise<Device> {
    const response = await apiClient.get<Device>(`/devices/${id}`);
    return response.data;
  },

  async create(payload: DeviceCreatePayload): Promise<Device> {
    const response = await apiClient.post<Device>('/devices', payload);
    return response.data;
  },

  async update(id: number, payload: DeviceUpdatePayload): Promise<Device> {
    const response = await apiClient.patch<Device>(`/devices/${id}`, payload);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/devices/${id}`);
  },

  async testConnection(id: number): Promise<ConnectionTestResult> {
    const response = await apiClient.post<ConnectionTestResult>(`/devices/${id}/test-connection`);
    return response.data;
  },
};

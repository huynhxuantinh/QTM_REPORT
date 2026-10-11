import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/api/queryKeys';
import { deviceService } from '../services/deviceService';

export const useDevices = (params?: { offset?: number; limit?: number; site?: string }) => {
  return useQuery({
    queryKey: queryKeys.devices.list(params),
    queryFn: () => deviceService.list(params),
    staleTime: 10000,
  });
};

export const useDevice = (id: number) => {
  return useQuery({
    queryKey: queryKeys.devices.detail(id),
    queryFn: () => deviceService.get(id),
    enabled: id > 0,
    staleTime: 10000,
  });
};

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/api/queryKeys';
import { checkService } from '../services/checkService';

export const useRunAllChecks = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => checkService.runAll(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.scans.detail(data.id) });
    },
  });
};

export const useScanPolling = (scanId: number | null) => {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: queryKeys.scans.detail(scanId || 0),
    queryFn: () => checkService.getScanRun(scanId!),
    enabled: typeof scanId === 'number' && scanId > 0,
    refetchInterval: (query) => {
      const status = query.state.data?.execution_status;
      if (status === 'succeeded' || status === 'failed') {
        // Once complete, refresh the dashboard and devices
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
        queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
        return false;
      }
      return 2000; // Poll every 2s
    },
  });
};

export const useStartDeviceCheck = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceId: number) => checkService.startCheck(deviceId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.checks.detail(data.id) });
    },
  });
};

export const useCheckPolling = (checkId: number | null, deviceId?: number) => {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: queryKeys.checks.detail(checkId || 0),
    queryFn: () => checkService.getCheck(checkId!),
    enabled: typeof checkId === 'number' && checkId > 0,
    refetchInterval: (query) => {
      const status = query.state.data?.execution_status;
      if (status === 'succeeded' || status === 'failed') {
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
        if (deviceId) {
          queryClient.invalidateQueries({ queryKey: queryKeys.devices.historyRoot(deviceId) });
          queryClient.invalidateQueries({ queryKey: queryKeys.devices.detail(deviceId) });
        }
        return false;
      }
      return 2000;
    },
  });
};

export const useDeviceHistory = (
  deviceId: number,
  params?: { offset?: number; limit?: number }
) => {
  return useQuery({
    queryKey: queryKeys.devices.history(deviceId, params),
    queryFn: () => checkService.getDeviceHistory(deviceId, params),
    enabled: deviceId > 0,
    staleTime: 10000,
  });
};

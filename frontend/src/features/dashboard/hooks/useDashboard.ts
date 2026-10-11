import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/api/queryKeys';
import { dashboardService } from '../services/dashboardService';

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: queryKeys.dashboard.summary,
    queryFn: () => dashboardService.getSummary(),
    refetchInterval: 10000, // Background poll every 10 seconds for real-time dashboard
    staleTime: 5000,
  });
};

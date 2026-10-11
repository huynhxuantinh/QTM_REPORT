import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/api/queryKeys';
import { settingsService } from '../services/settingsService';
import { SystemSettings } from '@/types/settings';

export const useSettings = () => {
  return useQuery({
    queryKey: queryKeys.settings.current,
    queryFn: () => settingsService.get(),
    staleTime: 60000,
  });
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SystemSettings) => settingsService.update(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.settings.current, data);
    },
  });
};

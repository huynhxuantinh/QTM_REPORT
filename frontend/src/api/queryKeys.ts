export const queryKeys = {
  dashboard: {
    summary: ['dashboard', 'summary'] as const,
  },
  devices: {
    all: ['devices'] as const,
    list: (params?: { offset?: number; limit?: number; site?: string }) =>
      [...queryKeys.devices.all, 'list', params] as const,
    detail: (id: number) => [...queryKeys.devices.all, 'detail', id] as const,
    historyRoot: (id: number) => [...queryKeys.devices.all, 'detail', id, 'history'] as const,
    history: (id: number, params?: { offset?: number; limit?: number }) =>
      [...queryKeys.devices.historyRoot(id), params] as const,
  },
  checks: {
    all: ['checks'] as const,
    detail: (id: number) => [...queryKeys.checks.all, 'detail', id] as const,
  },
  scans: {
    all: ['scans'] as const,
    detail: (id: number) => [...queryKeys.scans.all, 'detail', id] as const,
  },
  settings: {
    current: ['settings', 'current'] as const,
  },
};

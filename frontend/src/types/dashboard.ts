import { HealthStatus } from './health';

export interface RecentCheck {
  check_id: number;
  device_id: number;
  device_name: string;
  overall_status: HealthStatus | null;
  checked_at: string | null;
  cpu_percent: number | null;
  ram_percent: number | null;
}

export interface DashboardSummary {
  total_devices: number;
  healthy_devices: number;
  warning_devices: number;
  critical_devices: number;
  unknown_devices: number;
  last_scan_at: string | null;
  recent_checks: RecentCheck[];
}

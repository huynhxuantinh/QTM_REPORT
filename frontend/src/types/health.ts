export type HealthStatus = 'Healthy' | 'Warning' | 'Critical' | 'Unknown';
export type ExecutionStatus = 'queued' | 'running' | 'succeeded' | 'failed';
export type FindingSeverity = 'Warning' | 'Critical';

export interface InterfaceResult {
  name: string;
  ip_address: string;
  status: string;
  protocol: string;
  input_errors: number;
  crc_errors: number;
  output_errors: number;
  output_drops: number;
}

export interface PingResult {
  source_type: 'backend' | 'device' | string;
  target: string;
  packet_loss_percent: number;
  latency_min_ms: number | null;
  latency_avg_ms: number | null;
  latency_max_ms: number | null;
}

export interface Finding {
  severity: FindingSeverity;
  metric: string;
  message: string;
}

export interface CheckAccepted {
  id: number;
  device_id: number;
  execution_status: ExecutionStatus;
  started_at: string;
}

export interface HealthCheck extends CheckAccepted {
  overall_status: HealthStatus | null;
  finished_at: string | null;
  checked_at: string | null;
  ssh_ok: boolean | null;
  uptime_seconds: number | null;
  cpu_percent: number | null;
  ram_percent: number | null;
  memory_total_bytes: number | null;
  memory_used_bytes: number | null;
  memory_free_bytes: number | null;
  error: string | null;
  interfaces: InterfaceResult[];
  pings: PingResult[];
  findings: Finding[];
}

export interface HealthCheckPage {
  items: HealthCheck[];
  total: number;
  offset: number;
  limit: number;
}

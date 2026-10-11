export interface SystemSettings {
  cpu_warning_percent: number;
  cpu_critical_percent: number;
  ram_warning_percent: number;
  ram_critical_percent: number;
  packet_loss_warning_percent: number;
  packet_loss_critical_percent: number;
  latency_warning_ms: number;
  latency_critical_ms: number;
  scheduler_interval_minutes: number;
  max_concurrent_checks: number;
}

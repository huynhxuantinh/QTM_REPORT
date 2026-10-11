import { CheckAccepted, ExecutionStatus } from './health';

export interface ScanRunAccepted {
  id: number;
  trigger: 'manual' | 'scheduled' | string;
  execution_status: ExecutionStatus;
  started_at: string;
  total_checks: number;
}

export interface ScanRun extends ScanRunAccepted {
  finished_at: string | null;
  completed_checks: number;
  failed_checks: number;
  checks: CheckAccepted[];
}

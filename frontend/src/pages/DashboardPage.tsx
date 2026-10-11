import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useDashboardSummary } from '@/features/dashboard/hooks/useDashboard';
import { useRunAllChecks, useScanPolling } from '@/features/checks/hooks/useChecks';
import { StatusBadge } from '@/components/common/StatusBadge';
import { HealthDoughnutChart } from '@/components/charts/HealthDoughnutChart';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { SkeletonCard } from '@/components/common/SkeletonCard';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import { formatDateTime, formatPercent } from '@/utils/formatters';
import { getErrorMessage } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';
import {
  Server,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  PlayCircle,
  Clock,
  ArrowRight,
  Loader2,
  Cpu,
  Database,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: summary, isLoading, isError, error: dashboardError, refetch } = useDashboardSummary();
  const [activeScanId, setActiveScanId] = useState<number | null>(null);
  const { success, info, error: notifyError } = useNotifications();
  const notifiedScanId = useRef<number | null>(null);

  const runAllMutation = useRunAllChecks();
  const { data: scanData } = useScanPolling(activeScanId);

  useEffect(() => {
    if (!scanData || notifiedScanId.current === scanData.id) return;
    if (scanData.execution_status === 'succeeded') {
      notifiedScanId.current = scanData.id;
      success('Quét toàn bộ đã hoàn tất', `Đã kiểm tra ${scanData.completed_checks}/${scanData.total_checks} thiết bị.`);
    } else if (scanData.execution_status === 'failed') {
      notifiedScanId.current = scanData.id;
      notifyError('Đợt quét thất bại', 'Vui lòng kiểm tra trạng thái backend và thử lại.');
    }
  }, [notifyError, scanData, success]);

  const handleRunAll = async () => {
    try {
      const res = await runAllMutation.mutateAsync();
      setActiveScanId(res.id);
      info('Đã bắt đầu quét', `Đợt quét #${res.id} đang được thực hiện.`);
    } catch (error: unknown) {
      notifyError('Không thể bắt đầu quét', getErrorMessage(error));
    }
  };

  const isScanning =
    runAllMutation.isPending ||
    (scanData && (scanData.execution_status === 'running' || scanData.execution_status === 'queued'));

  if (isLoading) {
    return (
      <div className="py-4">
        <div className="row g-3 mb-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="col-12 col-sm-6 col-xl-3">
              <SkeletonCard rows={2} />
            </div>
          ))}
        </div>
        <LoadingSpinner message="Đang tải dữ liệu tổng quan giám sát..." />
      </div>
    );
  }

  if (isError || !summary) {
    return <ErrorState title="Không thể tải dữ liệu tổng quan" message={getErrorMessage(dashboardError)} onRetry={() => refetch()} />;
  }

  return (
    <div className="fade-in">
      {/* Page Title & Quick Actions */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <h4 className="fw-bold text-dark mb-1">Tổng quan sức khỏe Router</h4>
          <div className="text-muted small d-flex align-items-center gap-2">
            <Clock size={14} />
            <span>Lần quét gần nhất: {formatDateTime(summary.last_scan_at)}</span>
          </div>
        </div>

        <button
          className="btn btn-primary d-flex align-items-center gap-2 shadow-sm"
          onClick={handleRunAll}
          disabled={isScanning}
        >
          {isScanning ? (
            <>
              <Loader2 size={16} className="spinner-border-sm animate-spin" />
              <span>Đang quét thiết bị ({scanData?.completed_checks || 0}/{scanData?.total_checks || '...'})</span>
            </>
          ) : (
            <>
              <PlayCircle size={18} />
              <span className="fw-semibold">Quét tất cả thiết bị</span>
            </>
          )}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-primary border-4 rounded-3 h-100">
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small text-uppercase fw-semibold mb-1">Tổng thiết bị</div>
                <div className="fs-2 fw-bold text-dark">{summary.total_devices}</div>
              </div>
              <div className="p-3 bg-primary-subtle text-primary rounded-circle">
                <Server size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-success border-4 rounded-3 h-100">
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small text-uppercase fw-semibold mb-1">Hoạt động tốt</div>
                <div className="fs-2 fw-bold text-success">{summary.healthy_devices}</div>
              </div>
              <div className="p-3 bg-success-subtle text-success rounded-circle">
                <CheckCircle2 size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-warning border-4 rounded-3 h-100">
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small text-uppercase fw-semibold mb-1">Cảnh báo</div>
                <div className="fs-2 fw-bold text-warning">{summary.warning_devices}</div>
              </div>
              <div className="p-3 bg-warning-subtle text-warning rounded-circle">
                <AlertTriangle size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-danger border-4 rounded-3 h-100">
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small text-uppercase fw-semibold mb-1">Nghiêm trọng</div>
                <div className="fs-2 fw-bold text-danger">{summary.critical_devices}</div>
              </div>
              <div className="p-3 bg-danger-subtle text-danger rounded-circle">
                <XCircle size={24} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Charts & Recent Checks */}
      <div className="row g-4">
        {/* Health Distribution Doughnut */}
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-header bg-white border-0 pt-3 pb-2">
              <h6 className="fw-bold text-dark mb-0">Phân bố sức khỏe thiết bị</h6>
            </div>
            <div className="card-body d-flex align-items-center justify-content-center p-3">
              <HealthDoughnutChart
                healthy={summary.healthy_devices}
                warning={summary.warning_devices}
                critical={summary.critical_devices}
                unknown={summary.unknown_devices}
              />
            </div>
          </div>
        </div>

        {/* Recent Checks Table */}
        <div className="col-12 col-lg-8">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
              <h6 className="fw-bold text-dark mb-0">Lần kiểm tra gần đây nhất</h6>
              <Link to="/devices" className="text-primary small text-decoration-none fw-semibold d-flex align-items-center gap-1">
                <span>Quản lý thiết bị</span>
                <ArrowRight size={14} />
              </Link>
            </div>

            <div className="card-body p-0">
              {summary.recent_checks.length === 0 ? (
                <EmptyState
                  icon={Server}
                  title="Chưa có kết quả kiểm tra nào"
                  description="Hãy thêm router Cisco và nhấn 'Quét tất cả' để bắt đầu đánh giá."
                />
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light small text-muted text-uppercase">
                      <tr>
                        <th className="ps-3 py-2.5">Thiết bị</th>
                        <th className="py-2.5">Trạng thái</th>
                        <th className="py-2.5">CPU (5m)</th>
                        <th className="py-2.5">RAM đã dùng</th>
                        <th className="py-2.5">Thời gian đo</th>
                        <th className="pe-3 py-2.5 text-end">Chi tiết</th>
                      </tr>
                    </thead>
                    <tbody className="small">
                      {summary.recent_checks.map((check) => (
                        <tr key={check.check_id}>
                          <td className="ps-3 fw-semibold text-dark">
                            <Link to={`/devices/${check.device_id}`} className="text-dark text-decoration-none">
                              {check.device_name}
                            </Link>
                          </td>
                          <td>
                            <StatusBadge status={check.overall_status} size="sm" />
                          </td>
                          <td>
                            <span className="d-inline-flex align-items-center gap-1">
                              <Cpu size={14} className="text-muted" />
                              <span className="fw-mono">{formatPercent(check.cpu_percent)}</span>
                            </span>
                          </td>
                          <td>
                            <span className="d-inline-flex align-items-center gap-1">
                              <Database size={14} className="text-muted" />
                              <span className="fw-mono">{formatPercent(check.ram_percent)}</span>
                            </span>
                          </td>
                          <td className="text-muted">{formatDateTime(check.checked_at)}</td>
                          <td className="pe-3 text-end">
                            <Link
                              to={`/devices/${check.device_id}`}
                              className="btn btn-outline-secondary btn-sm py-0.5 px-2"
                              style={{ fontSize: '12px' }}
                            >
                              Xem
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

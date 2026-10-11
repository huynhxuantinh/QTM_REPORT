import React, { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDevice } from '@/features/devices/hooks/useDevices';
import { useDeviceHistory, useStartDeviceCheck, useCheckPolling } from '@/features/checks/hooks/useChecks';
import { useTestConnection } from '@/features/devices/hooks/useDeviceMutations';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import { MetricTrendChart } from '@/components/charts/MetricTrendChart';
import { TestConnectionModal } from '@/components/devices/TestConnectionModal';
import {
  formatDateTime,
  formatTimeOnly,
  formatPercent,
  formatBytes,
  formatUptime,
  formatLatency,
} from '@/utils/formatters';
import {
  Server,
  ArrowLeft,
  Play,
  Wifi,
  Cpu,
  Database,
  Clock,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  XCircle,
  Network,
  History,
  Activity,
  Loader2,
} from 'lucide-react';
import { HealthCheck } from '@/types/health';
import { getErrorMessage, getMetricLabel, getSeverityLabel, translateFindingMessage } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';

export const DeviceDetailPage: React.FC = () => {
  const { success, warning, info, error: notifyError } = useNotifications();
  const notifiedCheckId = useRef<number | null>(null);
  const { id } = useParams<{ id: string }>();
  const deviceId = parseInt(id || '0', 10);

  const [activeTab, setActiveTab] = useState<'overview' | 'interfaces' | 'pings' | 'findings' | 'history'>('overview');
  const [selectedCheckId, setSelectedCheckId] = useState<number | null>(null);

  // Poll single check if user clicks "Quét ngay"
  const [activeRunningCheckId, setActiveRunningCheckId] = useState<number | null>(null);

  // SSH Connection test state
  const [isTestingSsh, setIsTestingSsh] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testError, setTestError] = useState<string | null>(null);

  const {
    data: device,
    isLoading: isDeviceLoading,
    isError: isDeviceError,
    error: deviceError,
    refetch: refetchDevice,
  } = useDevice(deviceId);
  const { data: historyData } = useDeviceHistory(deviceId, {
    limit: 20,
  });

  const startCheckMutation = useStartDeviceCheck();
  const testConnMutation = useTestConnection();

  const { data: runningCheck } = useCheckPolling(activeRunningCheckId, deviceId);

  useEffect(() => {
    if (!runningCheck || notifiedCheckId.current === runningCheck.id) return;
    if (runningCheck.execution_status === 'succeeded') {
      notifiedCheckId.current = runningCheck.id;
      const message = `Trạng thái tổng hợp: ${runningCheck.overall_status === 'Critical' ? 'Nghiêm trọng' : runningCheck.overall_status === 'Warning' ? 'Cảnh báo' : 'Tốt'}.`;
      if (runningCheck.overall_status === 'Critical') warning('Kiểm tra hoàn tất', message);
      else success('Kiểm tra hoàn tất', message);
    } else if (runningCheck.execution_status === 'failed') {
      notifiedCheckId.current = runningCheck.id;
      notifyError('Kiểm tra thiết bị thất bại', getErrorMessage(runningCheck.error));
    }
  }, [notifyError, runningCheck, success, warning]);

  // Derive latest check or selected past check
  const checks = historyData?.items || [];
  const latestCheck: HealthCheck | null = checks.length > 0 ? checks[0] : null;
  const currentCheck: HealthCheck | null =
    selectedCheckId ? checks.find((c) => c.id === selectedCheckId) || latestCheck : latestCheck;

  const handleStartCheck = async () => {
    try {
      const res = await startCheckMutation.mutateAsync(deviceId);
      setActiveRunningCheckId(res.id);
      setSelectedCheckId(null);
      info('Đã bắt đầu kiểm tra', `Đang thu thập dữ liệu sức khỏe của ${device?.name || 'thiết bị'}.`);
    } catch (error: unknown) {
      notifyError('Không thể bắt đầu kiểm tra', getErrorMessage(error));
    }
  };

  const handleTestSsh = async () => {
    setIsTestingSsh(true);
    setTestResult(null);
    setTestError(null);
    try {
      const res = await testConnMutation.mutateAsync(deviceId);
      setTestResult(res);
    } catch (error: unknown) {
      setTestError(getErrorMessage(error, 'Không thể kiểm tra kết nối SSH.'));
    }
  };

  const isScanning =
    startCheckMutation.isPending ||
    (runningCheck && (runningCheck.execution_status === 'running' || runningCheck.execution_status === 'queued'));

  if (isDeviceLoading) {
    return <LoadingSpinner message="Đang tải thông tin router..." />;
  }

  if (isDeviceError) {
    return (
      <ErrorState
        title="Không thể tải thông tin thiết bị"
        message={getErrorMessage(deviceError)}
        onRetry={() => refetchDevice()}
      />
    );
  }

  if (!device) {
    return (
      <div className="alert alert-danger py-4 my-4 text-center">
        <h5>Không tìm thấy thiết bị</h5>
        <Link to="/devices" className="btn btn-outline-danger btn-sm mt-2">
          Quay lại danh sách
        </Link>
      </div>
    );
  }

  // Prepare chart series from history (reverse to chronological order)
  const chronologicalHistory = [...checks].reverse();
  const chartTimestamps = chronologicalHistory.map((c) => formatTimeOnly(c.checked_at || c.started_at));
  const cpuValues = chronologicalHistory.map((c) => c.cpu_percent);
  const ramValues = chronologicalHistory.map((c) => c.ram_percent);

  return (
    <div className="fade-in">
      {/* Back button & Device Header */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <Link to="/devices" className="text-muted small text-decoration-none d-flex align-items-center gap-1 mb-2">
            <ArrowLeft size={14} />
            <span>Danh sách thiết bị</span>
          </Link>
          <div className="d-flex align-items-center gap-3">
            <div className="p-2.5 bg-primary-subtle text-primary rounded-3">
              <Server size={28} />
            </div>
            <div>
              <div className="d-flex align-items-center gap-2">
                <h4 className="fw-bold text-dark mb-0">{device.name}</h4>
                <StatusBadge status={currentCheck?.overall_status} size="md" />
              </div>
              <div className="text-muted small mt-1 font-monospace">
                IP: {device.host}:{device.port} • Khu vực: {device.site || 'Lab'} • Loại: Cisco IOS
              </div>
            </div>
          </div>
        </div>

        <div className="d-flex align-items-center gap-2">
          <button
            className="btn btn-outline-secondary btn-sm d-flex align-items-center gap-1.5"
            onClick={handleTestSsh}
            disabled={testConnMutation.isPending}
          >
            <Wifi size={14} />
            <span>Thử SSH</span>
          </button>

          <button
            className="btn btn-primary btn-sm d-flex align-items-center gap-1.5"
            onClick={handleStartCheck}
            disabled={isScanning || !device.is_active}
          >
            {isScanning ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                <span>Đang quét...</span>
              </>
            ) : (
              <>
                <Play size={14} />
                <span>Kiểm tra ngay</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* KPI Cards: Current Health Metrics */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small text-uppercase fw-semibold">CPU trung bình 5 phút</span>
                <Cpu size={18} className="text-primary" />
              </div>
              <div className="fs-3 fw-bold text-dark font-monospace">
                {formatPercent(currentCheck?.cpu_percent)}
              </div>
              <div className="text-muted small mt-1">Ngưỡng tốt: dưới 70%</div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small text-uppercase fw-semibold">Mức sử dụng RAM</span>
                <Database size={18} className="text-info" />
              </div>
              <div className="fs-3 fw-bold text-dark font-monospace">
                {formatPercent(currentCheck?.ram_percent)}
              </div>
              <div className="text-muted small mt-1">
                {currentCheck?.memory_used_bytes
                  ? `${formatBytes(currentCheck.memory_used_bytes)} / ${formatBytes(currentCheck.memory_total_bytes)}`
                  : 'Processor Pool'}
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small text-uppercase fw-semibold">Thời gian hoạt động</span>
                <Clock size={18} className="text-warning" />
              </div>
              <div className="fs-4 fw-bold text-dark font-monospace">
                {formatUptime(currentCheck?.uptime_seconds)}
              </div>
              <div className="text-muted small mt-1">Thời gian router chạy liên tục</div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 rounded-3 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small text-uppercase fw-semibold">Trạng thái SSH</span>
                {!currentCheck ? (
                  <ShieldAlert size={18} className="text-secondary" />
                ) : currentCheck.ssh_ok ? (
                  <ShieldCheck size={18} className="text-success" />
                ) : (
                  <ShieldAlert size={18} className="text-danger" />
                )}
              </div>
              <div className="fs-4 fw-bold">
                {!currentCheck ? (
                  <span className="text-secondary">Chưa có dữ liệu</span>
                ) : currentCheck.ssh_ok ? (
                  <span className="text-success">Hoạt động tốt</span>
                ) : (
                  <span className="text-danger">Mất kết nối SSH</span>
                )}
              </div>
              <div className="text-muted small mt-1">
                {currentCheck?.checked_at ? formatDateTime(currentCheck.checked_at) : 'Chưa quét'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <ul className="nav nav-pills bg-white p-2 rounded-3 shadow-sm mb-4 gap-1">
        <li className="nav-item">
          <button
            className={`nav-link small py-1.5 px-3 fw-semibold ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <Activity size={15} className="me-1" />
            Biểu đồ xu hướng
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link small py-1.5 px-3 fw-semibold ${activeTab === 'interfaces' ? 'active' : ''}`}
            onClick={() => setActiveTab('interfaces')}
          >
            <Network size={15} className="me-1" />
            Cổng mạng ({currentCheck?.interfaces?.length || 0})
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link small py-1.5 px-3 fw-semibold ${activeTab === 'pings' ? 'active' : ''}`}
            onClick={() => setActiveTab('pings')}
          >
            <Wifi size={15} className="me-1" />
            Đo Ping ({currentCheck?.pings?.length || 0})
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link small py-1.5 px-3 fw-semibold ${activeTab === 'findings' ? 'active' : ''}`}
            onClick={() => setActiveTab('findings')}
          >
            <AlertTriangle size={15} className="me-1" />
            Cảnh báo / Phát hiện ({currentCheck?.findings?.length || 0})
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link small py-1.5 px-3 fw-semibold ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={15} className="me-1" />
            Lịch sử ({checks.length})
          </button>
        </li>
      </ul>

      {/* Tab 1: Overview & Trend Charts */}
      {activeTab === 'overview' && (
        <div className="row g-4">
          <div className="col-12 col-lg-6">
            <div className="card shadow-sm border-0 rounded-3">
              <div className="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
                <h6 className="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                  <Cpu size={16} className="text-primary" />
                  <span>Xu hướng tải CPU (%)</span>
                </h6>
                <span className="badge bg-light text-muted font-monospace">Ngưỡng: 70% / 90%</span>
              </div>
              <div className="card-body p-3">
                <MetricTrendChart
                  timestamps={chartTimestamps}
                  values={cpuValues}
                  label="CPU"
                  unit="%"
                  color="#2563EB"
                  height={220}
                />
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-6">
            <div className="card shadow-sm border-0 rounded-3">
              <div className="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
                <h6 className="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                  <Database size={16} className="text-info" />
                  <span>Xu hướng dung lượng RAM (%)</span>
                </h6>
                <span className="badge bg-light text-muted font-monospace">Ngưỡng: 75% / 90%</span>
              </div>
              <div className="card-body p-3">
                <MetricTrendChart
                  timestamps={chartTimestamps}
                  values={ramValues}
                  label="RAM"
                  unit="%"
                  color="#06B6D4"
                  height={220}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Interfaces */}
      {activeTab === 'interfaces' && (
        <div className="card shadow-sm border-0 rounded-3">
          <div className="card-body p-0">
            {!currentCheck?.interfaces || currentCheck.interfaces.length === 0 ? (
              <EmptyState title="Không có thông tin interface nào" />
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light small text-muted text-uppercase">
                    <tr>
                      <th className="ps-3 py-2.5">Tên Cổng</th>
                      <th className="py-2.5">IP Address</th>
                      <th className="py-2.5">Trạng thái vật lý</th>
                      <th className="py-2.5">Trạng thái giao thức</th>
                      <th className="py-2.5 text-end">Lỗi đầu vào</th>
                      <th className="py-2.5 text-end">Lỗi CRC</th>
                      <th className="pe-3 py-2.5 text-end">Gói đầu ra bị bỏ</th>
                    </tr>
                  </thead>
                  <tbody className="small">
                    {currentCheck.interfaces.map((intf, idx) => (
                      <tr key={idx}>
                        <td className="ps-3 fw-bold font-monospace text-dark">{intf.name}</td>
                        <td className="font-monospace text-muted">{intf.ip_address || 'unassigned'}</td>
                        <td>
                          <span
                            className={`badge ${
                              intf.status.toLowerCase() === 'up'
                                ? 'bg-success-subtle text-success'
                                : 'bg-danger-subtle text-danger'
                            }`}
                          >
                            {intf.status.toLowerCase() === 'up' ? 'Hoạt động' : 'Ngừng'}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`badge ${
                              intf.protocol.toLowerCase() === 'up'
                                ? 'bg-success-subtle text-success'
                                : 'bg-danger-subtle text-danger'
                            }`}
                          >
                            {intf.protocol.toLowerCase() === 'up' ? 'Hoạt động' : 'Ngừng'}
                          </span>
                        </td>
                        <td className="text-end font-monospace">{intf.input_errors}</td>
                        <td className="text-end font-monospace">{intf.crc_errors}</td>
                        <td className="pe-3 text-end font-monospace">{intf.output_drops}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Ping Results */}
      {activeTab === 'pings' && (
        <div className="card shadow-sm border-0 rounded-3">
          <div className="card-body p-0">
            {!currentCheck?.pings || currentCheck.pings.length === 0 ? (
              <EmptyState title="Không có kết quả ping nào trong lần kiểm tra này" />
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light small text-muted text-uppercase">
                    <tr>
                      <th className="ps-3 py-2.5">Nguồn đo</th>
                      <th className="py-2.5">Đích đến</th>
                      <th className="py-2.5">Mất gói (%)</th>
                      <th className="py-2.5">Độ trễ thấp nhất</th>
                      <th className="py-2.5">Độ trễ trung bình</th>
                      <th className="pe-3 py-2.5">Độ trễ cao nhất</th>
                    </tr>
                  </thead>
                  <tbody className="small">
                    {currentCheck.pings.map((p, idx) => (
                      <tr key={idx}>
                        <td className="ps-3">
                          <span className="badge bg-secondary-subtle text-secondary font-monospace">
                            {p.source_type === 'backend' ? 'Máy chủ giám sát' : 'Router'}
                          </span>
                        </td>
                        <td className="font-monospace fw-semibold">{p.target}</td>
                        <td>
                          <span
                            className={`fw-bold font-monospace ${
                              p.packet_loss_percent >= 30
                                ? 'text-danger'
                                : p.packet_loss_percent > 0
                                ? 'text-warning'
                                : 'text-success'
                            }`}
                          >
                            {formatPercent(p.packet_loss_percent)}
                          </span>
                        </td>
                        <td className="font-monospace">{formatLatency(p.latency_min_ms)}</td>
                        <td className="font-monospace fw-bold">{formatLatency(p.latency_avg_ms)}</td>
                        <td className="pe-3 font-monospace">{formatLatency(p.latency_max_ms)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Findings */}
      {activeTab === 'findings' && (
        <div className="card shadow-sm border-0 rounded-3">
          <div className="card-body p-0">
            {!currentCheck?.findings || currentCheck.findings.length === 0 ? (
              <EmptyState
                icon={ShieldCheck}
                title="Không có cảnh báo bất thường nào"
                description="Tất cả các chỉ số của thiết bị đều nằm trong ngưỡng an toàn."
              />
            ) : (
              <div className="list-group list-group-flush">
                {currentCheck.findings.map((f, idx) => (
                  <div key={idx} className="list-group-item p-3 d-flex align-items-start gap-3">
                    <div className="mt-0.5">
                      {f.severity === 'Critical' ? (
                        <XCircle size={20} className="text-danger" />
                      ) : (
                        <AlertTriangle size={20} className="text-warning" />
                      )}
                    </div>
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center gap-2 mb-1">
                        <span
                          className={`badge ${
                            f.severity === 'Critical'
                              ? 'bg-danger-subtle text-danger'
                              : 'bg-warning-subtle text-warning'
                          }`}
                        >
                          {getSeverityLabel(f.severity)}
                        </span>
                        <strong className="text-dark small">{getMetricLabel(f.metric)}</strong>
                      </div>
                      <p className="mb-0 text-muted small">{translateFindingMessage(f.message)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 5: Execution History Table */}
      {activeTab === 'history' && (
        <div className="card shadow-sm border-0 rounded-3">
          <div className="card-body p-0">
            {checks.length === 0 ? (
              <EmptyState title="Chưa có lịch sử kiểm tra" />
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light small text-muted text-uppercase">
                    <tr>
                      <th className="ps-3 py-2.5">Mã lần chạy (ID)</th>
                      <th className="py-2.5">Thời gian thực hiện</th>
                      <th className="py-2.5">Trạng thái tổng hợp</th>
                      <th className="py-2.5">CPU (5m)</th>
                      <th className="py-2.5">RAM</th>
                      <th className="py-2.5">SSH</th>
                      <th className="py-2.5">Cảnh báo</th>
                      <th className="pe-3 py-2.5 text-end">Chọn xem</th>
                    </tr>
                  </thead>
                  <tbody className="small">
                    {checks.map((c) => (
                      <tr
                        key={c.id}
                        className={currentCheck?.id === c.id ? 'table-primary bg-opacity-10' : ''}
                      >
                        <td className="ps-3 fw-mono text-muted">#{c.id}</td>
                        <td>{formatDateTime(c.checked_at || c.started_at)}</td>
                        <td>
                          <StatusBadge status={c.overall_status} size="sm" />
                        </td>
                        <td className="font-monospace">{formatPercent(c.cpu_percent)}</td>
                        <td className="font-monospace">{formatPercent(c.ram_percent)}</td>
                        <td>
                          {c.ssh_ok ? (
                            <span className="badge bg-success-subtle text-success">Tốt</span>
                          ) : (
                            <span className="badge bg-danger-subtle text-danger">Lỗi</span>
                          )}
                        </td>
                        <td>
                          {c.findings?.length > 0 ? (
                            <span className="badge bg-warning-subtle text-warning">
                              {c.findings.length} cảnh báo
                            </span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>
                        <td className="pe-3 text-end">
                          <button
                            className={`btn btn-xs btn-sm py-0.5 px-2 ${
                              currentCheck?.id === c.id ? 'btn-primary' : 'btn-outline-secondary'
                            }`}
                            style={{ fontSize: '12px' }}
                            onClick={() => setSelectedCheckId(c.id)}
                          >
                            {currentCheck?.id === c.id ? 'Đang chọn' : 'Xem'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Test Connection Modal */}
      <TestConnectionModal
        isOpen={isTestingSsh}
        onClose={() => setIsTestingSsh(false)}
        deviceName={device.name}
        isLoading={testConnMutation.isPending}
        result={testResult}
        error={testError}
      />
    </div>
  );
};

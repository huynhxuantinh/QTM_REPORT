import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useDevices } from '@/features/devices/hooks/useDevices';
import {
  useCreateDevice,
  useUpdateDevice,
  useDeleteDevice,
  useTestConnection,
} from '@/features/devices/hooks/useDeviceMutations';
import { useStartDeviceCheck, useCheckPolling } from '@/features/checks/hooks/useChecks';
import { Device, DeviceCreatePayload, DeviceUpdatePayload, ConnectionTestResult } from '@/types/device';
import { DeviceFormModal } from '@/components/devices/DeviceFormModal';
import { TestConnectionModal } from '@/components/devices/TestConnectionModal';
import { ConfirmModal } from '@/components/common/ConfirmModal';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import {
  Plus,
  Search,
  Server,
  Play,
  Activity,
  Edit2,
  Trash2,
  Wifi,
  Loader2,
  ExternalLink,
} from 'lucide-react';
import { getErrorMessage } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';

export const DevicesPage: React.FC = () => {
  const { success, warning, info, error: notifyError } = useNotifications();
  const notifiedCheckId = useRef<number | null>(null);
  const [search, setSearch] = useState('');
  const [siteFilter, setSiteFilter] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [deletingDevice, setDeletingDevice] = useState<Device | null>(null);

  // SSH Connection test state
  const [testingDevice, setTestingDevice] = useState<Device | null>(null);
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  // Single check execution state
  const [activeCheckId, setActiveCheckId] = useState<number | null>(null);
  const [checkingDeviceId, setCheckingDeviceId] = useState<number | null>(null);

  const { data: pageData, isLoading, isError, error: devicesError, refetch } = useDevices();
  const createMutation = useCreateDevice();
  const updateMutation = useUpdateDevice();
  const deleteMutation = useDeleteDevice();
  const testConnMutation = useTestConnection();
  const startCheckMutation = useStartDeviceCheck();

  // Poll single check if running
  const { data: currentCheck } = useCheckPolling(activeCheckId, checkingDeviceId || undefined);

  useEffect(() => {
    if (!currentCheck || notifiedCheckId.current === currentCheck.id) return;
    if (currentCheck.execution_status === 'succeeded') {
      notifiedCheckId.current = currentCheck.id;
      const message = `Kết quả tổng hợp: ${currentCheck.overall_status === 'Critical' ? 'Nghiêm trọng' : currentCheck.overall_status === 'Warning' ? 'Cảnh báo' : 'Tốt'}.`;
      if (currentCheck.overall_status === 'Critical') warning('Kiểm tra hoàn tất', message);
      else success('Kiểm tra hoàn tất', message);
    } else if (currentCheck.execution_status === 'failed') {
      notifiedCheckId.current = currentCheck.id;
      notifyError('Kiểm tra thiết bị thất bại', getErrorMessage(currentCheck.error));
    }
  }, [currentCheck, notifyError, success, warning]);

  const devices = pageData?.items || [];

  // Filter devices
  const filteredDevices = devices.filter((d) => {
    const matchesSearch =
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.host.toLowerCase().includes(search.toLowerCase());
    const matchesSite = !siteFilter || d.site === siteFilter;
    return matchesSearch && matchesSite;
  });

  // Unique sites for filter
  const uniqueSites = Array.from(new Set(devices.map((d) => d.site).filter(Boolean))) as string[];

  const handleOpenCreate = () => {
    setEditingDevice(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (device: Device) => {
    setEditingDevice(device);
    setIsFormOpen(true);
  };

  const handleFormSubmit = async (
    data: DeviceCreatePayload | { id: number; payload: DeviceUpdatePayload }
  ) => {
    if ('id' in data) {
      const updated = await updateMutation.mutateAsync(data);
      success('Đã cập nhật thiết bị', `Thông tin router ${updated.name} đã được lưu.`);
    } else {
      const created = await createMutation.mutateAsync(data);
      success('Đã thêm thiết bị', `Router ${created.name} đã được thêm vào hệ thống.`);
    }
  };

  const handleDelete = async () => {
    if (!deletingDevice) return;
    try {
      await deleteMutation.mutateAsync(deletingDevice.id);
      success('Đã xóa thiết bị', `Router ${deletingDevice.name} đã được xóa khỏi danh sách giám sát.`);
      setDeletingDevice(null);
    } catch (error: unknown) {
      notifyError('Không thể xóa thiết bị', getErrorMessage(error));
    }
  };

  const handleToggleActive = async (device: Device) => {
    try {
      await updateMutation.mutateAsync({
        id: device.id,
        payload: { is_active: !device.is_active },
      });
      success(
        device.is_active ? 'Đã tạm dừng giám sát' : 'Đã kích hoạt giám sát',
        `Router ${device.name} đã được cập nhật trạng thái.`,
      );
    } catch (error: unknown) {
      notifyError('Không thể cập nhật trạng thái', getErrorMessage(error));
    }
  };

  const handleTestConnection = async (device: Device) => {
    setTestingDevice(device);
    setTestResult(null);
    setTestError(null);
    try {
      const res = await testConnMutation.mutateAsync(device.id);
      setTestResult(res);
    } catch (error: unknown) {
      setTestError(getErrorMessage(error, 'Không thể kiểm tra kết nối SSH.'));
    }
  };

  const handleCheckNow = async (device: Device) => {
    try {
      setCheckingDeviceId(device.id);
      const res = await startCheckMutation.mutateAsync(device.id);
      setActiveCheckId(res.id);
      info('Đã bắt đầu kiểm tra', `Router ${device.name} đang được thu thập chỉ số sức khỏe.`);
    } catch (error: unknown) {
      notifyError('Không thể bắt đầu kiểm tra', getErrorMessage(error));
      setCheckingDeviceId(null);
    }
  };

  const isDeviceChecking = (deviceId: number) => {
    return (
      checkingDeviceId === deviceId &&
      currentCheck &&
      (currentCheck.execution_status === 'running' || currentCheck.execution_status === 'queued')
    );
  };

  return (
    <div className="fade-in">
      {/* Header & Add Button */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <h4 className="fw-bold text-dark mb-1">Quản lý Thiết bị Router</h4>
          <p className="text-muted small mb-0">
            Danh sách các router Cisco 3660 trong lab GNS3 được cấu hình giám sát
          </p>
        </div>

        <button
          className="btn btn-primary d-flex align-items-center gap-2 shadow-sm"
          onClick={handleOpenCreate}
        >
          <Plus size={18} />
          <span>Thêm router mới</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="card shadow-sm border-0 rounded-3 mb-4">
        <div className="card-body p-3">
          <div className="row g-2 align-items-center">
            <div className="col-12 col-md-6">
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0 text-muted">
                  <Search size={16} />
                </span>
                <input
                  type="text"
                  className="form-control border-start-0 ps-0 small"
                  placeholder="Tìm kiếm theo tên thiết bị hoặc địa chỉ IP..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </div>

            <div className="col-12 col-md-4">
              <select
                className="form-select small"
                value={siteFilter}
                onChange={(e) => setSiteFilter(e.target.value)}
              >
                <option value="">Tất cả khu vực / chi nhánh</option>
                {uniqueSites.map((site) => (
                  <option key={site} value={site}>
                    {site}
                  </option>
                ))}
              </select>
            </div>

            <div className="col-12 col-md-2 text-md-end text-muted small">
              Tổng số: <strong>{filteredDevices.length}</strong> router
            </div>
          </div>
        </div>
      </div>

      {/* Devices Table */}
      <div className="card shadow-sm border-0 rounded-3">
        <div className="card-body p-0">
          {isLoading ? (
            <LoadingSpinner message="Đang tải danh sách router..." />
          ) : isError ? (
            <ErrorState
              title="Không thể tải danh sách thiết bị"
              message={getErrorMessage(devicesError)}
              onRetry={() => refetch()}
            />
          ) : filteredDevices.length === 0 ? (
            <EmptyState
              icon={Server}
              title="Không tìm thấy router nào"
              description={
                search || siteFilter
                  ? 'Thử điều chỉnh lại bộ lọc tìm kiếm của bạn.'
                  : 'Chưa có router Cisco nào được thêm vào hệ thống.'
              }
              action={
                !search && !siteFilter
                  ? {
                      label: 'Thêm router ngay',
                      onClick: handleOpenCreate,
                    }
                  : undefined
              }
            />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light small text-muted text-uppercase">
                  <tr>
                    <th className="ps-3 py-3">Tên thiết bị</th>
                    <th className="py-3">Địa chỉ IP</th>
                    <th className="py-3">Khu vực</th>
                    <th className="py-3">IP đích kiểm tra ping</th>
                    <th className="py-3 text-center">Giám sát</th>
                    <th className="pe-3 py-3 text-end">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="small">
                  {filteredDevices.map((device) => {
                    const isChecking = isDeviceChecking(device.id);

                    return (
                      <tr key={device.id}>
                        <td className="ps-3 py-3">
                          <div className="d-flex align-items-center gap-2.5">
                            <div className="p-2 bg-light rounded text-primary">
                              <Server size={18} />
                            </div>
                            <div>
                              <Link
                                to={`/devices/${device.id}`}
                                className="fw-bold text-dark text-decoration-none d-flex align-items-center gap-1"
                              >
                                <span>{device.name}</span>
                                <ExternalLink size={12} className="text-muted" />
                              </Link>
                              <div className="text-muted font-monospace" style={{ fontSize: '11px' }}>
                                Cổng: {device.port} • Tài khoản: {device.username}
                              </div>
                            </div>
                          </div>
                        </td>

                        <td className="py-3">
                          <span className="badge bg-light text-dark font-monospace border px-2 py-1">
                            {device.host}
                          </span>
                        </td>

                        <td className="py-3">
                          {device.site ? (
                            <span className="badge bg-secondary-subtle text-secondary">{device.site}</span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>

                        <td className="py-3">
                          {device.path_ping_target ? (
                            <span className="badge bg-light text-muted font-monospace border">
                              {device.path_ping_target}
                            </span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>

                        <td className="py-3 text-center">
                          <div className="form-check form-switch d-inline-block">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={device.is_active}
                              onChange={() => handleToggleActive(device)}
                              title={device.is_active ? 'Đang bật giám sát' : 'Đang tạm dừng giám sát'}
                            />
                          </div>
                        </td>

                        <td className="pe-3 py-3 text-end">
                          <div className="btn-group btn-group-sm">
                            <button
                              className="btn btn-outline-secondary"
                              onClick={() => handleTestConnection(device)}
                              disabled={testConnMutation.isPending && testingDevice?.id === device.id}
                              title="Kiểm tra kết nối SSH"
                            >
                              <Wifi size={14} className="me-1" />
                              <span>Thử SSH</span>
                            </button>

                            <button
                              className="btn btn-outline-primary"
                              onClick={() => handleCheckNow(device)}
                              disabled={isChecking || !device.is_active}
                              title={!device.is_active ? 'Thiết bị đang tắt' : 'Chạy kiểm tra sức khỏe ngay'}
                            >
                              {isChecking ? (
                                <>
                                  <Loader2 size={14} className="animate-spin me-1" />
                                  <span>Đang quét...</span>
                                </>
                              ) : (
                                <>
                                  <Play size={14} className="me-1" />
                                  <span>Quét ngay</span>
                                </>
                              )}
                            </button>

                            <Link
                              to={`/devices/${device.id}`}
                              className="btn btn-outline-info"
                              title="Xem chi tiết & lịch sử"
                            >
                              <Activity size={14} />
                            </Link>

                            <button
                              className="btn btn-outline-secondary"
                              onClick={() => handleOpenEdit(device)}
                              title="Chỉnh sửa thông tin"
                            >
                              <Edit2 size={14} />
                            </button>

                            <button
                              className="btn btn-outline-danger"
                              onClick={() => setDeletingDevice(device)}
                              title="Xóa router"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Form Modal (Add / Edit) */}
      {isFormOpen && (
        <DeviceFormModal
          key={editingDevice?.id ?? 'new-device'}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleFormSubmit}
          initialData={editingDevice}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
        />
      )}

      {/* Test Connection Modal */}
      <TestConnectionModal
        isOpen={!!testingDevice}
        onClose={() => setTestingDevice(null)}
        deviceName={testingDevice?.name || ''}
        isLoading={testConnMutation.isPending}
        result={testResult}
        error={testError}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={!!deletingDevice}
        onClose={() => setDeletingDevice(null)}
        onConfirm={handleDelete}
        title="Xóa thiết bị"
        message={`Bạn có chắc chắn muốn xóa router "${deletingDevice?.name}" (${deletingDevice?.host})? Lịch sử kiểm tra trước đó vẫn sẽ được lưu trữ an toàn.`}
        isConfirming={deleteMutation.isPending}
      />
    </div>
  );
};

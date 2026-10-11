import React, { useState } from 'react';
import { Device, DeviceCreatePayload, DeviceUpdatePayload } from '@/types/device';
import { Server, Lock, Globe, Shield } from 'lucide-react';
import { getErrorMessage } from '@/utils/i18n';

interface DeviceFormModalProps {
  onClose: () => void;
  onSubmit: (data: DeviceCreatePayload | { id: number; payload: DeviceUpdatePayload }) => Promise<void>;
  initialData?: Device | null;
  isSubmitting: boolean;
}

export const DeviceFormModal: React.FC<DeviceFormModalProps> = ({
  onClose,
  onSubmit,
  initialData,
  isSubmitting,
}) => {
  const isEdit = !!initialData;

  const [name, setName] = useState(initialData?.name || '');
  const [host, setHost] = useState(initialData?.host || '');
  const [port, setPort] = useState(initialData?.port || 22);
  const [username, setUsername] = useState(initialData?.username || 'admin');
  const [password, setPassword] = useState('');
  const [secret, setSecret] = useState('');
  const [site, setSite] = useState(initialData?.site || '');
  const [pathPingTarget, setPathPingTarget] = useState(initialData?.path_ping_target || '');
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Vui lòng nhập tên thiết bị.');
      return;
    }
    if (!host.trim()) {
      setError('Vui lòng nhập địa chỉ IP host.');
      return;
    }
    if (!isEdit && !password.trim()) {
      setError('Vui lòng nhập mật khẩu SSH khi thêm mới.');
      return;
    }

    try {
      if (isEdit) {
        const updatePayload: DeviceUpdatePayload = {
          name,
          host,
          port,
          username,
          site: site.trim() || null,
          path_ping_target: pathPingTarget.trim() || null,
          is_active: isActive,
        };
        if (password.trim()) updatePayload.password = password.trim();
        if (secret.trim()) updatePayload.secret = secret.trim();

        await onSubmit({ id: initialData.id, payload: updatePayload });
      } else {
        const createPayload: DeviceCreatePayload = {
          name,
          host,
          port,
          device_type: 'cisco_ios',
          username,
          password,
          secret: secret.trim() || null,
          site: site.trim() || null,
          path_ping_target: pathPingTarget.trim() || null,
          is_active: isActive,
        };
        await onSubmit(createPayload);
      }
      onClose();
    } catch (submitError: unknown) {
      setError(getErrorMessage(submitError, 'Không thể lưu thiết bị.'));
    }
  };

  return (
    <div
      className="modal fade show d-block"
      tabIndex={-1}
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-dialog-centered modal-lg">
        <div className="modal-content shadow border-0">
          <div className="modal-header bg-light">
            <h5 className="modal-title d-flex align-items-center gap-2 fs-6 fw-bold">
              <Server size={18} className="text-primary" />
              <span>{isEdit ? 'Chỉnh sửa Router Cisco' : 'Thêm Router Cisco mới'}</span>
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              disabled={isSubmitting}
              aria-label="Đóng"
            />
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4">
              {error && (
                <div className="alert alert-danger py-2 small" role="alert">
                  {error}
                </div>
              )}

              <div className="row g-3">
                <div className="col-md-8">
                  <label className="form-label small fw-semibold">Tên thiết bị *</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ví dụ: Cisco 3660 R1"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>

                <div className="col-md-4">
                  <label className="form-label small fw-semibold">Khu vực / Chi nhánh</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ví dụ: HN-Core, Lab-GNS3"
                    value={site}
                    onChange={(e) => setSite(e.target.value)}
                  />
                </div>

                <div className="col-md-8">
                  <label className="form-label small fw-semibold">Địa chỉ IP quản trị *</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">
                      <Globe size={16} />
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="192.168.141.11"
                      value={host}
                      onChange={(e) => setHost(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-text small">Thuộc dải IP Lab (192.168.141.0/24 hoặc 192.168.91.0/24)</div>
                </div>

                <div className="col-md-4">
                  <label className="form-label small fw-semibold">Cổng SSH *</label>
                  <input
                    type="number"
                    className="form-control"
                    min={1}
                    max={65535}
                    value={port}
                    onChange={(e) => setPort(parseInt(e.target.value) || 22)}
                    required
                  />
                </div>

                <div className="col-md-4">
                  <label className="form-label small fw-semibold">Tên đăng nhập SSH *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>

                <div className="col-md-4">
                  <label className="form-label small fw-semibold">
                    Mật khẩu SSH {isEdit ? '(để trống nếu không đổi)' : '*'}
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">
                      <Lock size={16} />
                    </span>
                    <input
                      type="password"
                      className="form-control"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required={!isEdit}
                    />
                  </div>
                </div>

                <div className="col-md-4">
                  <label className="form-label small fw-semibold">Mật khẩu đặc quyền (tùy chọn)</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">
                      <Shield size={16} />
                    </span>
                    <input
                      type="password"
                      className="form-control"
                      placeholder="Mật khẩu vào chế độ đặc quyền"
                      value={secret}
                      onChange={(e) => setSecret(e.target.value)}
                    />
                  </div>
                </div>

                <div className="col-md-8">
                  <label className="form-label small fw-semibold">IP đích để router kiểm tra ping</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ví dụ: 192.168.141.128"
                    value={pathPingTarget}
                    onChange={(e) => setPathPingTarget(e.target.value)}
                  />
                </div>

                <div className="col-md-4 d-flex align-items-center">
                  <div className="form-check form-switch mt-4">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="isActiveSwitch"
                      checked={isActive}
                      onChange={(e) => setIsActive(e.target.checked)}
                    />
                    <label className="form-check-label small fw-semibold" htmlFor="isActiveSwitch">
                      Kích hoạt giám sát
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer bg-light">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                className="btn btn-primary btn-sm d-flex align-items-center gap-1.5"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1" role="status" />
                    <span>Đang lưu...</span>
                  </>
                ) : (
                  <span>{isEdit ? 'Cập nhật thiết bị' : 'Thêm thiết bị'}</span>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

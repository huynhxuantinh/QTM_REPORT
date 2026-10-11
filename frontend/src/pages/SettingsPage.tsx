import React, { useState } from 'react';
import { useSettings, useUpdateSettings } from '@/features/settings/hooks/useSettings';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { SystemSettings } from '@/types/settings';
import { Settings as SettingsIcon, Save, AlertCircle, Clock, Cpu, Database, Wifi } from 'lucide-react';
import { getErrorMessage } from '@/utils/i18n';
import { ErrorState } from '@/components/common/ErrorState';
import { useNotifications } from '@/context/useNotifications';

const DEFAULT_SETTINGS: SystemSettings = {
  cpu_warning_percent: 70,
  cpu_critical_percent: 90,
  ram_warning_percent: 75,
  ram_critical_percent: 90,
  packet_loss_warning_percent: 10,
  packet_loss_critical_percent: 30,
  latency_warning_ms: 50,
  latency_critical_ms: 150,
  scheduler_interval_minutes: 15,
  max_concurrent_checks: 3,
};

export const SettingsPage: React.FC = () => {
  const { data: settings, isLoading, isError, error: settingsError, refetch } = useSettings();
  const updateMutation = useUpdateSettings();
  const { success, error: notifyError } = useNotifications();

  const [formDraft, setFormDraft] = useState<SystemSettings | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const formData = formDraft ?? settings ?? DEFAULT_SETTINGS;

  if (isLoading) {
    return <LoadingSpinner message="Đang tải cấu hình hệ thống..." />;
  }

  if (isError) {
    return <ErrorState title="Không thể tải cấu hình" message={getErrorMessage(settingsError)} onRetry={() => refetch()} />;
  }

  const handleChange = (field: keyof SystemSettings, value: number) => {
    setFormDraft((prev) => ({
      ...(prev ?? formData),
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    // Validation
    if (formData.cpu_warning_percent >= formData.cpu_critical_percent) {
      setFeedback({ type: 'error', message: 'Ngưỡng CPU cảnh báo phải nhỏ hơn ngưỡng nghiêm trọng!' });
      return;
    }
    if (formData.ram_warning_percent >= formData.ram_critical_percent) {
      setFeedback({ type: 'error', message: 'Ngưỡng RAM cảnh báo phải nhỏ hơn ngưỡng nghiêm trọng!' });
      return;
    }
    if (formData.packet_loss_warning_percent >= formData.packet_loss_critical_percent) {
      setFeedback({ type: 'error', message: 'Ngưỡng mất gói cảnh báo phải nhỏ hơn ngưỡng nghiêm trọng!' });
      return;
    }
    if (formData.latency_warning_ms >= formData.latency_critical_ms) {
      setFeedback({ type: 'error', message: 'Ngưỡng Độ trễ cảnh báo phải nhỏ hơn ngưỡng nghiêm trọng!' });
      return;
    }

    try {
      await updateMutation.mutateAsync(formData);
      setFormDraft(null);
      success('Đã lưu cấu hình', 'Các ngưỡng đánh giá và chu kỳ kiểm tra đã được cập nhật.');
    } catch (error: unknown) {
      notifyError('Không thể lưu cấu hình', getErrorMessage(error, 'Vui lòng kiểm tra dữ liệu rồi thử lại.'));
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: '800px' }}>
      <div className="mb-4">
        <h4 className="fw-bold text-dark mb-1 d-flex align-items-center gap-2">
          <SettingsIcon size={24} className="text-primary" />
          <span>Cấu hình Ngưỡng & Chu kỳ Hệ thống</span>
        </h4>
        <p className="text-muted small mb-0">
          Thiết lập các mức Tốt / Cảnh báo / Nghiêm trọng và chu kỳ kiểm tra tự động
        </p>
      </div>

      {feedback && (
        <div
          className={`alert ${
            feedback.type === 'success' ? 'alert-success' : 'alert-danger'
          } d-flex align-items-center gap-2 py-2.5 small mb-4 shadow-sm`}
          role="alert"
        >
          <AlertCircle size={18} className="text-danger flex-shrink-0" />
          <span>{feedback.message}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* CPU Thresholds */}
        <div className="card shadow-sm border-0 rounded-3 mb-4">
          <div className="card-header bg-white border-0 pt-3 pb-2 d-flex align-items-center gap-2">
            <Cpu size={18} className="text-primary" />
            <h6 className="fw-bold text-dark mb-0">Ngưỡng Tải CPU (%)</h6>
          </div>
          <div className="card-body p-4 pt-2">
            <div className="row g-3">
              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Ngưỡng cảnh báo (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.cpu_warning_percent}
                    onChange={(e) => handleChange('cpu_warning_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 70%</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Ngưỡng nghiêm trọng (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.cpu_critical_percent}
                    onChange={(e) => handleChange('cpu_critical_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 90%</div>
              </div>
            </div>
          </div>
        </div>

        {/* RAM Thresholds */}
        <div className="card shadow-sm border-0 rounded-3 mb-4">
          <div className="card-header bg-white border-0 pt-3 pb-2 d-flex align-items-center gap-2">
            <Database size={18} className="text-info" />
            <h6 className="fw-bold text-dark mb-0">Ngưỡng Bộ nhớ RAM (%)</h6>
          </div>
          <div className="card-body p-4 pt-2">
            <div className="row g-3">
              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Ngưỡng cảnh báo (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.ram_warning_percent}
                    onChange={(e) => handleChange('ram_warning_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 75%</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Ngưỡng nghiêm trọng (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.ram_critical_percent}
                    onChange={(e) => handleChange('ram_critical_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 90%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Network Ping & Latency */}
        <div className="card shadow-sm border-0 rounded-3 mb-4">
          <div className="card-header bg-white border-0 pt-3 pb-2 d-flex align-items-center gap-2">
            <Wifi size={18} className="text-warning" />
            <h6 className="fw-bold text-dark mb-0">Ngưỡng Độ Mất Gói & Độ Trễ (Ping)</h6>
          </div>
          <div className="card-body p-4 pt-2">
            <div className="row g-3">
              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Mất gói mức cảnh báo (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.packet_loss_warning_percent}
                    onChange={(e) => handleChange('packet_loss_warning_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 10%</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Mất gói mức nghiêm trọng (%)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-control font-monospace"
                    value={formData.packet_loss_critical_percent}
                    onChange={(e) => handleChange('packet_loss_critical_percent', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">%</span>
                </div>
                <div className="form-text small">Mặc định: 30%</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Độ trễ mức cảnh báo (ms)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="1"
                    min="0"
                    className="form-control font-monospace"
                    value={formData.latency_warning_ms}
                    onChange={(e) => handleChange('latency_warning_ms', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">ms</span>
                </div>
                <div className="form-text small">Mặc định: 50 ms</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Độ trễ mức nghiêm trọng (ms)</label>
                <div className="input-group">
                  <input
                    type="number"
                    step="1"
                    min="0"
                    className="form-control font-monospace"
                    value={formData.latency_critical_ms}
                    onChange={(e) => handleChange('latency_critical_ms', parseFloat(e.target.value) || 0)}
                    required
                  />
                  <span className="input-group-text bg-light text-muted">ms</span>
                </div>
                <div className="form-text small">Mặc định: 150 ms</div>
              </div>
            </div>
          </div>
        </div>

        {/* Scheduler & Concurrency */}
        <div className="card shadow-sm border-0 rounded-3 mb-4">
          <div className="card-header bg-white border-0 pt-3 pb-2 d-flex align-items-center gap-2">
            <Clock size={18} className="text-secondary" />
            <h6 className="fw-bold text-dark mb-0">Bộ lập lịch & Khả năng xử lý song song</h6>
          </div>
          <div className="card-body p-4 pt-2">
            <div className="row g-3">
              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Chu kỳ kiểm tra tự động (Phút)</label>
                <input
                  type="number"
                  min="1"
                  max="1440"
                  className="form-control font-monospace"
                  value={formData.scheduler_interval_minutes}
                  onChange={(e) => handleChange('scheduler_interval_minutes', parseInt(e.target.value) || 15)}
                  required
                />
                <div className="form-text small">Khoảng thời gian giữa các lần tự động quét (1 - 1440 phút)</div>
              </div>

              <div className="col-12 col-md-6">
                <label className="form-label small fw-semibold text-muted">Số thiết bị kiểm tra đồng thời</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  className="form-control font-monospace"
                  value={formData.max_concurrent_checks}
                  onChange={(e) => handleChange('max_concurrent_checks', parseInt(e.target.value) || 3)}
                  required
                />
                <div className="form-text small">Số router tối đa kiểm tra đồng thời qua Netmiko (1 - 10 luồng)</div>
              </div>
            </div>
          </div>
        </div>

        <div className="d-flex justify-content-end mb-5">
          <button
            type="submit"
            className="btn btn-primary d-flex align-items-center gap-2 px-4 shadow-sm"
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? (
              <>
                <span className="spinner-border spinner-border-sm" role="status" />
                <span>Đang lưu...</span>
              </>
            ) : (
              <>
                <Save size={18} />
                <span className="fw-semibold">Lưu cấu hình hệ thống</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

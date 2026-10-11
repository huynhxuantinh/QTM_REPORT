import React from 'react';
import { ConnectionTestResult } from '@/types/device';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { translateMessage } from '@/utils/i18n';

interface TestConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  deviceName: string;
  isLoading: boolean;
  result: ConnectionTestResult | null;
  error: string | null;
}

export const TestConnectionModal: React.FC<TestConnectionModalProps> = ({
  isOpen,
  onClose,
  deviceName,
  isLoading,
  result,
  error,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="modal fade show d-block"
      tabIndex={-1}
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content shadow border-0">
          <div className="modal-header">
            <h5 className="modal-title fs-6 fw-bold">Kiểm tra kết nối SSH: {deviceName}</h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              disabled={isLoading}
              aria-label="Đóng"
            />
          </div>

          <div className="modal-body p-4 text-center">
            {isLoading && (
              <div className="py-4">
                <Loader2 size={40} className="text-primary animate-spin mb-3 mx-auto" />
                <h6>Đang thử kết nối SSH tới thiết bị...</h6>
                <p className="text-muted small">Quá trình này có thể mất vài giây phụ thuộc vào mạng GNS3.</p>
              </div>
            )}

            {!isLoading && result && (
              <div className="py-2">
                {result.reachable ? (
                  <div className="text-success mb-3">
                    <CheckCircle2 size={48} className="mx-auto mb-2" />
                    <h5 className="fw-bold">Kết nối thành công!</h5>
                    <p className="text-muted small mt-2">{translateMessage(result.message, 'Kết nối SSH thành công.')}</p>
                  </div>
                ) : (
                  <div className="text-danger mb-3">
                    <XCircle size={48} className="mx-auto mb-2" />
                    <h5 className="fw-bold">Kết nối thất bại!</h5>
                    <p className="text-danger small mt-2">{translateMessage(result.message, 'Không thể kết nối SSH tới thiết bị.')}</p>
                  </div>
                )}
              </div>
            )}

            {!isLoading && error && (
              <div className="text-danger py-3">
                <XCircle size={48} className="mx-auto mb-2" />
                <h5 className="fw-bold">Đã xảy ra lỗi</h5>
                <p className="text-muted small mt-2">{translateMessage(error)}</p>
              </div>
            )}
          </div>

          <div className="modal-footer bg-light">
            <button type="button" className="btn btn-secondary btn-sm" onClick={onClose} disabled={isLoading}>
              Đóng
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

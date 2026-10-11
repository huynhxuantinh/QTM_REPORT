import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmVariant?: 'danger' | 'warning' | 'primary';
  isConfirming?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Xác nhận xóa',
  confirmVariant = 'danger',
  isConfirming = false,
}) => {
  if (!isOpen) return null;

  const variantStyles = {
    danger: 'btn-danger',
    warning: 'btn-warning',
    primary: 'btn-primary',
  }[confirmVariant];

  return (
    <div className="modal fade show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(15, 23, 42, 0.55)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg rounded-3 p-2">
        <div className="modal-header border-0">
          <div className="d-flex align-items-center gap-3">
            <div className="p-2 rounded-3 bg-danger-subtle text-danger">
              <AlertTriangle size={20} />
            </div>
            <h5 className="modal-title fw-bold">{title}</h5>
          </div>
          <button
            onClick={onClose}
            disabled={isConfirming}
            className="btn-close"
            aria-label="Đóng"
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body pt-1 text-muted">{message}</div>

        <div className="modal-footer border-0">
          <button
            type="button"
            onClick={onClose}
            disabled={isConfirming}
            className="btn btn-outline-secondary btn-sm"
          >
            Hủy
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isConfirming}
            className={`btn btn-sm d-flex align-items-center gap-2 ${variantStyles}`}
          >
            {isConfirming && <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />}
            <span>{confirmLabel}</span>
          </button>
        </div>
        </div>
      </div>
    </div>
  );
};

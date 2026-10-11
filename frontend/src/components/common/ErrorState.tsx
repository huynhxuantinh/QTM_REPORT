import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Không thể tải dữ liệu',
  message = 'Vui lòng kiểm tra kết nối tới máy chủ rồi thử lại.',
  onRetry,
}) => (
  <div className="alert alert-danger-subtle border-danger-subtle text-center py-4 my-3" role="alert">
    <AlertCircle size={32} className="text-danger mb-2" aria-hidden="true" />
    <h5 className="text-danger-emphasis">{title}</h5>
    <p className="small text-secondary mb-3">{message}</p>
    {onRetry && (
      <button type="button" className="btn btn-outline-danger btn-sm d-inline-flex align-items-center gap-1" onClick={onRetry}>
        <RefreshCw size={14} aria-hidden="true" />
        Thử lại
      </button>
    )}
  </div>
);

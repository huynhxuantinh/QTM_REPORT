import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullPage?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Đang tải dữ liệu...',
  size = 'md',
  fullPage = false,
}) => {
  const iconSizes = {
    sm: 18,
    md: 28,
    lg: 44,
  }[size];

  const content = (
    <div className="d-flex flex-column align-items-center justify-content-center p-4 text-muted">
      <div>
        <Loader2
          size={iconSizes}
          className="animate-spin text-primary mb-3"
        />
      </div>
      {message && <div className="small fw-medium">{message}</div>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75 loading-overlay">
        {content}
      </div>
    );
  }

  return content;
};

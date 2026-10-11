import React from 'react';
import { HealthStatus } from '@/types/health';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: HealthStatus | string | null | undefined;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
}) => {
  const normalized = (status || 'Unknown') as HealthStatus;

  const config = {
    Healthy: {
      badgeClass: 'bg-success-subtle text-success border border-success-subtle',
      dotClass: 'bg-success',
      pingClass: 'bg-success',
      label: 'Tốt',
      icon: CheckCircle2,
    },
    Warning: {
      badgeClass: 'bg-warning-subtle text-warning-emphasis border border-warning-subtle',
      dotClass: 'bg-warning',
      pingClass: 'bg-warning',
      label: 'Cảnh báo',
      icon: AlertTriangle,
    },
    Critical: {
      badgeClass: 'bg-danger-subtle text-danger border border-danger-subtle',
      dotClass: 'bg-danger',
      pingClass: 'bg-danger',
      label: 'Nghiêm trọng',
      icon: XCircle,
    },
    Unknown: {
      badgeClass: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
      dotClass: 'bg-secondary',
      pingClass: 'bg-secondary',
      label: 'Chưa xác định',
      icon: HelpCircle,
    },
  }[normalized] || {
    badgeClass: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
    dotClass: 'bg-secondary',
    pingClass: 'bg-secondary',
    label: 'Chưa xác định',
    icon: HelpCircle,
  };

  const IconComponent = config.icon;

  const sizeClasses = {
    sm: 'small py-1 px-2 gap-1',
    md: 'small py-1 px-2 gap-1 fw-semibold',
    lg: 'py-2 px-3 gap-2 fw-semibold',
  }[size];

  const iconSizes = {
    sm: 11,
    md: 13,
    lg: 15,
  }[size];

  return (
    <span
      className={`d-inline-flex align-items-center rounded-pill ${config.badgeClass} ${sizeClasses}`}
    >
      <span className="position-relative d-flex status-dot">
        {normalized !== 'Unknown' && (
          <span
            className={`status-dot-ping position-absolute d-inline-flex rounded-circle opacity-75 ${config.pingClass}`}
          />
        )}
        <span className={`position-relative d-inline-flex rounded-circle status-dot ${config.dotClass}`} />
      </span>
      {showIcon && <IconComponent size={iconSizes} strokeWidth={2.5} />}
      <span>{config.label}</span>
    </span>
  );
};

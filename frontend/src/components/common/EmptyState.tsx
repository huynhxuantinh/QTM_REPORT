import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  action,
}) => {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center py-5 px-4 text-center">
      <div className="mb-3">
        <div className="d-flex align-items-center justify-content-center rounded-3 bg-primary-subtle text-primary empty-state-icon">
          <Icon size={30} strokeWidth={1.75} />
        </div>
      </div>
      <h6 className="fw-semibold text-dark mb-1">{title}</h6>
      {description && (
        <p className="small text-muted mb-4 empty-state-description">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="btn btn-primary btn-sm px-3"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

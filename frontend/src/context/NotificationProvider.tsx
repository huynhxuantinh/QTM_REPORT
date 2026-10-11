import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react';
import {
  NotificationContext,
  type AppNotification,
  type NotificationInput,
  type NotificationType,
} from '@/context/notification-context';

const TYPE_CONFIG = {
  success: { icon: CheckCircle2, className: 'border-success', iconClassName: 'text-success' },
  error: { icon: XCircle, className: 'border-danger', iconClassName: 'text-danger' },
  warning: { icon: AlertTriangle, className: 'border-warning', iconClassName: 'text-warning' },
  info: { icon: Info, className: 'border-primary', iconClassName: 'text-primary' },
} satisfies Record<NotificationType, { icon: typeof Info; className: string; iconClassName: string }>;

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const nextId = useRef(1);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());

  const dismiss = useCallback((id: number) => {
    const timer = timers.current.get(id);
    if (timer) clearTimeout(timer);
    timers.current.delete(id);
    setNotifications((current) => current.filter((item) => item.id !== id));
  }, []);

  const notify = useCallback(
    (input: NotificationInput) => {
      const id = nextId.current++;
      const durationMs = input.durationMs === undefined ? (input.type === 'error' ? 8000 : 5000) : input.durationMs;
      setNotifications((current) => [...current.slice(-3), { ...input, id }]);
      if (durationMs !== null) {
        timers.current.set(id, setTimeout(() => dismiss(id), durationMs));
      }
      return id;
    },
    [dismiss],
  );

  useEffect(
    () => () => {
      timers.current.forEach(clearTimeout);
      timers.current.clear();
    },
    [],
  );

  const value = useMemo(
    () => ({
      notify,
      dismiss,
      success: (title: string, message?: string) => notify({ type: 'success', title, message }),
      error: (title: string, message?: string) => notify({ type: 'error', title, message }),
      warning: (title: string, message?: string) => notify({ type: 'warning', title, message }),
      info: (title: string, message?: string) => notify({ type: 'info', title, message }),
    }),
    [dismiss, notify],
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <div className="notification-stack" aria-live="polite" aria-atomic="false">
        {notifications.map((notification) => {
          const config = TYPE_CONFIG[notification.type];
          const Icon = config.icon;
          return (
            <div
              key={notification.id}
              className={`notification-toast bg-white shadow border-start border-4 ${config.className}`}
              role={notification.type === 'error' ? 'alert' : 'status'}
            >
              <Icon size={20} className={`flex-shrink-0 mt-1 ${config.iconClassName}`} aria-hidden="true" />
              <div className="flex-grow-1 min-w-0">
                <div className="fw-bold text-dark small">{notification.title}</div>
                {notification.message && <div className="text-muted small mt-1">{notification.message}</div>}
              </div>
              <button
                type="button"
                className="btn btn-sm p-0 text-muted notification-close"
                onClick={() => dismiss(notification.id)}
                aria-label="Đóng thông báo"
              >
                <X size={17} aria-hidden="true" />
              </button>
            </div>
          );
        })}
      </div>
    </NotificationContext.Provider>
  );
};

import { createContext } from 'react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface NotificationInput {
  type: NotificationType;
  title: string;
  message?: string;
  durationMs?: number | null;
}

export interface AppNotification extends NotificationInput {
  id: number;
}

export interface NotificationContextValue {
  notify: (notification: NotificationInput) => number;
  dismiss: (id: number) => void;
  success: (title: string, message?: string) => number;
  error: (title: string, message?: string) => number;
  warning: (title: string, message?: string) => number;
  info: (title: string, message?: string) => number;
}

export const NotificationContext = createContext<NotificationContextValue | null>(null);

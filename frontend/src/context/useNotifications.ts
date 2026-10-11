import { useContext } from 'react';
import { NotificationContext } from '@/context/notification-context';

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications phải được sử dụng bên trong NotificationProvider.');
  }
  return context;
}

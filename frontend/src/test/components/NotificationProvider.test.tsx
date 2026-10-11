import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { NotificationProvider } from '@/context/NotificationProvider';
import { useNotifications } from '@/context/useNotifications';

const NotificationDemo = () => {
  const { success, error } = useNotifications();
  return (
    <>
      <button onClick={() => success('Lưu thành công', 'Dữ liệu đã được cập nhật.')}>Báo thành công</button>
      <button onClick={() => error('Không thể kết nối', 'Hãy kiểm tra Docker.')}>Báo lỗi</button>
    </>
  );
};

describe('NotificationProvider', () => {
  it('hiển thị và đóng thông báo thành công', () => {
    render(
      <NotificationProvider>
        <NotificationDemo />
      </NotificationProvider>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Báo thành công' }));
    expect(screen.getByRole('status')).toHaveTextContent('Lưu thành công');
    expect(screen.getByText('Dữ liệu đã được cập nhật.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Đóng thông báo' }));
    expect(screen.queryByText('Lưu thành công')).not.toBeInTheDocument();
  });

  it('dùng role alert cho thông báo lỗi', () => {
    render(
      <NotificationProvider>
        <NotificationDemo />
      </NotificationProvider>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Báo lỗi' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Không thể kết nối');
    expect(screen.getByText('Hãy kiểm tra Docker.')).toBeInTheDocument();
  });
});

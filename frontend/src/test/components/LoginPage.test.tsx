import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LoginPage } from '@/pages/LoginPage';

const loginMock = vi.hoisted(() => vi.fn());

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({ login: loginMock }),
}));

const renderLoginPage = () =>
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );

describe('LoginPage', () => {
  beforeEach(() => {
    loginMock.mockReset();
  });

  it('hiển thị nội dung giám sát mạng và form đăng nhập tiếng Việt', () => {
    renderLoginPage();

    expect(
      screen.getByRole('heading', { name: /AI quan sát\.Mạng luôn ổn định\./ }),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Chào mừng trở lại' })).toBeInTheDocument();
    expect(screen.getByLabelText('Tài khoản')).toHaveValue('admin');
    expect(screen.getByLabelText('Mật khẩu')).toHaveAttribute('type', 'password');
  });

  it('cho phép hiện mật khẩu và gửi thông tin đăng nhập', async () => {
    const user = userEvent.setup();
    loginMock.mockResolvedValue(undefined);
    renderLoginPage();

    const passwordInput = screen.getByLabelText('Mật khẩu');
    await user.type(passwordInput, 'qtm');
    await user.click(screen.getByRole('button', { name: 'Hiện mật khẩu' }));
    expect(passwordInput).toHaveAttribute('type', 'text');

    await user.click(screen.getByRole('button', { name: 'Đăng nhập hệ thống' }));
    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({ username: 'admin', password: 'qtm' });
    });
  });
});

import { describe, expect, it } from 'vitest';
import { extractApiErrorMessage } from '@/api/errorMessage';

describe('extractApiErrorMessage', () => {
  it('dịch danh sách lỗi validation và tên trường', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            { loc: ['body', 'host'], msg: 'Input should be a valid IP address' },
            { loc: ['body', 'password'], msg: 'Field required' },
          ],
        },
      },
    };

    expect(extractApiErrorMessage(error)).toBe(
      'Địa chỉ IP: Địa chỉ IP không hợp lệ. Mật khẩu SSH: Không được để trống.',
    );
  });

  it('trả thông báo tiếng Việt theo mã HTTP', () => {
    expect(extractApiErrorMessage({ response: { status: 403, data: {} } })).toContain('không có quyền');
    expect(extractApiErrorMessage({ response: { status: 500, data: {} } })).toContain('Máy chủ đang gặp lỗi');
  });

  it('hướng dẫn kiểm tra môi trường khi mất kết nối backend', () => {
    expect(extractApiErrorMessage({ message: 'Network Error' })).toContain('Ubuntu VM, Docker');
  });
});

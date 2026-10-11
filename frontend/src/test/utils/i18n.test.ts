import { describe, expect, it } from 'vitest';
import {
  getExecutionStatusLabel,
  getHealthStatusLabel,
  translateFindingMessage,
  translateMessage,
} from '@/utils/i18n';

describe('tiện ích dịch giao diện', () => {
  it('dịch trạng thái sức khỏe và thực thi', () => {
    expect(getHealthStatusLabel('Healthy')).toBe('Tốt');
    expect(getHealthStatusLabel('Critical')).toBe('Nghiêm trọng');
    expect(getExecutionStatusLabel('running')).toBe('Đang thực hiện');
  });

  it('dịch lỗi API thường gặp', () => {
    expect(translateMessage('Invalid username or password')).toContain('không đúng');
    expect(translateMessage('Connection refused')).toBe('Thiết bị từ chối kết nối.');
  });

  it('không hiển thị trực tiếp lỗi kỹ thuật tiếng Anh chưa biết', () => {
    expect(translateMessage('Unexpected internal parser failure')).toBe('Đã xảy ra lỗi. Vui lòng thử lại.');
    expect(translateMessage('Device is inactive')).toContain('tạm dừng giám sát');
  });

  it('dịch lỗi kết nối TCP của Netmiko và giữ lại địa chỉ thiết bị', () => {
    const message = `TCP connection to device failed. Common causes of this problem are:\n
1. Incorrect hostname or IP address.\n
2. Wrong TCP port.\n
3. Intermediate firewall blocking access.\n
Device settings: cisco_ios 192.168.141.13:22`;

    expect(translateMessage(message)).toBe(
      'Không thể kết nối SSH tới thiết bị 192.168.141.13:22. Hãy kiểm tra router đang chạy, địa chỉ IP, cổng SSH và tường lửa.',
    );
  });

  it('dịch nội dung cảnh báo động', () => {
    expect(translateFindingMessage('CPU usage is 85.5%')).toBe('Mức sử dụng CPU là 85.5%.');
    expect(translateFindingMessage('Average latency is 120 ms')).toBe('Độ trễ trung bình là 120 ms.');
  });
});

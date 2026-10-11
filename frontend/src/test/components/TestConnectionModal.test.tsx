import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { TestConnectionModal } from '@/components/devices/TestConnectionModal';

describe('TestConnectionModal', () => {
  it('hiển thị lỗi kết nối Netmiko bằng tiếng Việt', () => {
    render(
      <TestConnectionModal
        isOpen
        onClose={vi.fn()}
        deviceName="R3"
        isLoading={false}
        error={null}
        result={{
          device_id: 3,
          reachable: false,
          message:
            'TCP connection to device failed. Common causes of this problem are: 1. Incorrect hostname or IP address. 2. Wrong TCP port. 3. Intermediate firewall blocking access. Device settings: cisco_ios 192.168.141.13:22',
        }}
      />,
    );

    expect(
      screen.getByText(
        'Không thể kết nối SSH tới thiết bị 192.168.141.13:22. Hãy kiểm tra router đang chạy, địa chỉ IP, cổng SSH và tường lửa.',
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText(/TCP connection to device failed/i)).not.toBeInTheDocument();
  });
});

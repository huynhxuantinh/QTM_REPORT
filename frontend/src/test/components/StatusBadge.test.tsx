import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '@/components/common/StatusBadge';

describe('StatusBadge', () => {
  it('hiển thị trạng thái Tốt', () => {
    render(<StatusBadge status="Healthy" />);
    expect(screen.getByText('Tốt')).toBeInTheDocument();
  });

  it('hiển thị trạng thái Cảnh báo', () => {
    render(<StatusBadge status="Warning" />);
    expect(screen.getByText('Cảnh báo')).toBeInTheDocument();
  });

  it('hiển thị trạng thái Nghiêm trọng', () => {
    render(<StatusBadge status="Critical" />);
    expect(screen.getByText('Nghiêm trọng')).toBeInTheDocument();
  });

  it('hiển thị Chưa xác định khi không có trạng thái', () => {
    render(<StatusBadge status={null} />);
    expect(screen.getByText('Chưa xác định')).toBeInTheDocument();
  });
});

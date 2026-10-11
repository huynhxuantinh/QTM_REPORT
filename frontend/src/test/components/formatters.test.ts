import { describe, it, expect } from 'vitest';
import {
  formatPercent,
  formatLatency,
  formatBytes,
  formatUptime,
} from '@/utils/formatters';

describe('Formatters Utilities', () => {
  it('formats percentages correctly', () => {
    expect(formatPercent(45.678)).toBe('45.7%');
    expect(formatPercent(null)).toBe('—');
  });

  it('formats latencies correctly', () => {
    expect(formatLatency(12.34)).toBe('12.3 ms');
    expect(formatLatency(null)).toBe('—');
  });

  it('formats bytes correctly', () => {
    expect(formatBytes(0)).toBe('0 B');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
  });

  it('formats router uptimes correctly', () => {
    expect(formatUptime(3600)).toBe('1 giờ');
    expect(formatUptime(90000)).toBe('1 ngày 1 giờ');
    expect(formatUptime(120)).toBe('2 phút');
    expect(formatUptime(null)).toBe('—');
  });
});

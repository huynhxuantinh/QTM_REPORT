import type { ExecutionStatus, FindingSeverity, HealthStatus } from '@/types/health';

const HEALTH_STATUS_LABELS: Record<HealthStatus, string> = {
  Healthy: 'Tốt',
  Warning: 'Cảnh báo',
  Critical: 'Nghiêm trọng',
  Unknown: 'Chưa xác định',
};

const EXECUTION_STATUS_LABELS: Record<ExecutionStatus, string> = {
  queued: 'Đang chờ',
  running: 'Đang thực hiện',
  succeeded: 'Hoàn thành',
  failed: 'Thất bại',
};

const EXACT_MESSAGES: Record<string, string> = {
  'Invalid username or password': 'Tên đăng nhập hoặc mật khẩu không đúng.',
  'Authentication required': 'Bạn cần đăng nhập để thực hiện thao tác này.',
  'Invalid access token': 'Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.',
  'Token has expired': 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
  'Device not found': 'Không tìm thấy thiết bị.',
  'An active device already uses this host and port': 'Đã có thiết bị đang hoạt động sử dụng IP và cổng này.',
  'Host is outside configured lab CIDRs': 'Địa chỉ IP nằm ngoài dải mạng lab được cho phép.',
  'Health check not found': 'Không tìm thấy lần kiểm tra sức khỏe.',
  'A health check is already running for this device': 'Thiết bị này đang được kiểm tra. Vui lòng chờ hoàn tất.',
  'Device is inactive': 'Thiết bị đang tạm dừng giám sát. Hãy kích hoạt thiết bị trước khi kiểm tra.',
  'Scan run not found': 'Không tìm thấy đợt quét.',
  'A scan is already running': 'Một đợt quét khác đang chạy. Vui lòng chờ hoàn tất.',
  'date_from must be before date_to': 'Ngày bắt đầu phải trước ngày kết thúc.',
  'SSH connection successful': 'Kết nối SSH thành công.',
  'SSH connection failed': 'Kết nối SSH thất bại.',
  'Management ping data is unavailable': 'Không có dữ liệu ping tới địa chỉ quản trị.',
  'Path ping data is unavailable': 'Không có dữ liệu ping đường truyền.',
  'Path latency data is unavailable': 'Không có dữ liệu độ trễ đường truyền.',
  'Network Error': 'Không thể kết nối tới máy chủ. Hãy kiểm tra Ubuntu VM, Docker và kết nối mạng.',
  'Failed to fetch': 'Không thể kết nối tới máy chủ. Hãy kiểm tra Ubuntu VM, Docker và kết nối mạng.',
  'Field required': 'Không được để trống.',
  'An unexpected error occurred': 'Đã xảy ra lỗi không xác định.',
};

export function getHealthStatusLabel(status: HealthStatus | string | null | undefined): string {
  return HEALTH_STATUS_LABELS[(status || 'Unknown') as HealthStatus] || String(status || 'Chưa xác định');
}

export function getExecutionStatusLabel(status: ExecutionStatus | string | null | undefined): string {
  return EXECUTION_STATUS_LABELS[status as ExecutionStatus] || 'Chưa xác định';
}

export function getSeverityLabel(severity: FindingSeverity | string): string {
  return severity === 'Critical' ? 'Nghiêm trọng' : 'Cảnh báo';
}

export function translateMessage(message: unknown, fallback = 'Đã xảy ra lỗi. Vui lòng thử lại.'): string {
  if (typeof message !== 'string' || !message.trim()) return fallback;

  const normalized = message.trim();
  if (EXACT_MESSAGES[normalized]) return EXACT_MESSAGES[normalized];

  const tcpDevice = normalized.match(
    /TCP connection to device failed[\s\S]*?Device settings:\s*\S+\s+([^\s:]+):(\d+)/i,
  );
  if (tcpDevice) {
    return `Không thể kết nối SSH tới thiết bị ${tcpDevice[1]}:${tcpDevice[2]}. Hãy kiểm tra router đang chạy, địa chỉ IP, cổng SSH và tường lửa.`;
  }

  if (/TCP connection to device failed/i.test(normalized)) {
    return 'Không thể kết nối SSH tới thiết bị. Hãy kiểm tra router đang chạy, địa chỉ IP, cổng SSH và tường lửa.';
  }
  if (/authentication (?:to device )?failed|authentication failure/i.test(normalized)) {
    return 'Xác thực SSH thất bại. Vui lòng kiểm tra tên đăng nhập, mật khẩu và mật khẩu đặc quyền.';
  }
  if (/SSH protocol banner|error reading SSH protocol banner/i.test(normalized)) {
    return 'Không đọc được phản hồi SSH từ thiết bị. Hãy kiểm tra dịch vụ SSH và cổng kết nối.';
  }
  if (/pattern not detected/i.test(normalized)) {
    return 'Không nhận diện được dấu nhắc lệnh của thiết bị Cisco. Hãy kiểm tra loại thiết bị và quyền đăng nhập.';
  }
  if (/connection reset by peer/i.test(normalized)) {
    return 'Thiết bị đã đóng kết nối SSH đột ngột.';
  }
  if (/timeout|timed out/i.test(normalized)) return 'Kết nối đã quá thời gian chờ.';
  if (/authentication fail|auth fail/i.test(normalized)) return 'Xác thực thất bại. Vui lòng kiểm tra tài khoản và mật khẩu.';
  if (/connection refused/i.test(normalized)) return 'Thiết bị từ chối kết nối.';
  if (/no route to host|unreachable/i.test(normalized)) return 'Không thể định tuyến tới thiết bị.';
  if (/no matching key exchange/i.test(normalized)) return 'Thiết bị SSH sử dụng thuật toán cũ không tương thích.';
  if (/request failed with status code 5\d\d/i.test(normalized)) return 'Máy chủ đang gặp lỗi. Vui lòng thử lại sau.';
  if (/request failed with status code 4\d\d/i.test(normalized)) return 'Yêu cầu không hợp lệ hoặc bạn không có quyền thực hiện.';

  let match = normalized.match(/^(CPU|RAM|packet loss|latency) warning threshold must be below critical$/i);
  if (match) {
    const metric = match[1].toLowerCase() === 'packet loss' ? 'mất gói' : match[1];
    return `Ngưỡng cảnh báo ${metric} phải nhỏ hơn ngưỡng nghiêm trọng.`;
  }
  if (/valid (IPv4|IPv6|IP) address|valid IP address/i.test(normalized)) return 'Địa chỉ IP không hợp lệ.';
  if (/greater than or equal to/i.test(normalized)) return 'Giá trị nhỏ hơn mức tối thiểu cho phép.';
  if (/less than or equal to/i.test(normalized)) return 'Giá trị vượt quá mức tối đa cho phép.';
  if (/at least \d+ character/i.test(normalized)) return 'Nội dung quá ngắn.';
  if (/at most \d+ character/i.test(normalized)) return 'Nội dung vượt quá độ dài cho phép.';

  // Không đưa chuỗi lỗi kỹ thuật tiếng Anh chưa biết trực tiếp ra giao diện.
  if ([...normalized].every((character) => character.charCodeAt(0) <= 127)) return fallback;

  return normalized;
}

export function getErrorMessage(error: unknown, fallback?: string): string {
  return translateMessage(error instanceof Error ? error.message : error, fallback);
}

export function translateFindingMessage(message: string): string {
  const exact = EXACT_MESSAGES[message];
  if (exact) return exact;

  let match = message.match(/^(CPU|RAM) data is unavailable$/i);
  if (match) return `Không có dữ liệu ${match[1].toUpperCase()}.`;

  match = message.match(/^(CPU|RAM) usage is ([\d.]+)%$/i);
  if (match) return `Mức sử dụng ${match[1].toUpperCase()} là ${match[2]}%.`;

  match = message.match(/^Management packet loss is ([\d.]+)%$/i);
  if (match) return `Tỷ lệ mất gói tới địa chỉ quản trị là ${match[1]}%.`;

  match = message.match(/^Path packet loss is ([\d.]+)%$/i);
  if (match) return `Tỷ lệ mất gói đường truyền là ${match[1]}%.`;

  match = message.match(/^Average latency is ([\d.]+) ms$/i);
  if (match) return `Độ trễ trung bình là ${match[1]} ms.`;

  match = message.match(/^(.+) is (.+)\/(.+)$/i);
  if (match) return `Cổng ${match[1]} đang ở trạng thái ${match[2]}/${match[3]}.`;

  match = message.match(/^(.+) has non-zero error counters$/i);
  if (match) return `Cổng ${match[1]} có bộ đếm lỗi lớn hơn 0.`;

  return translateMessage(message, message);
}

export function getMetricLabel(metric: string): string {
  const labels: Record<string, string> = {
    ssh: 'Kết nối SSH',
    cpu: 'CPU',
    ram: 'RAM',
    management_ping: 'Ping quản trị',
    path_ping: 'Ping đường truyền',
    packet_loss: 'Mất gói',
    latency: 'Độ trễ',
    interface: 'Cổng mạng',
    interface_errors: 'Lỗi cổng mạng',
  };
  return labels[metric] || metric;
}

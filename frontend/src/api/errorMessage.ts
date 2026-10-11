import { translateMessage } from '@/utils/i18n';

interface ValidationIssue {
  loc?: unknown[];
  msg?: unknown;
}

interface ApiErrorLike {
  message?: unknown;
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
}

const FIELD_LABELS: Record<string, string> = {
  name: 'Tên thiết bị',
  host: 'Địa chỉ IP',
  port: 'Cổng SSH',
  username: 'Tên đăng nhập SSH',
  password: 'Mật khẩu SSH',
  secret: 'Mật khẩu đặc quyền',
  site: 'Khu vực',
  path_ping_target: 'IP đích kiểm tra ping',
  date_from: 'Ngày bắt đầu',
  date_to: 'Ngày kết thúc',
};

function validationMessage(issue: ValidationIssue): string {
  const fieldKey = String(issue.loc?.at(-1) ?? 'Dữ liệu');
  const field = FIELD_LABELS[fieldKey] || fieldKey;
  return `${field}: ${translateMessage(issue.msg, 'Giá trị không hợp lệ.')}`;
}

export function extractApiErrorMessage(error: unknown): string {
  const apiError = error as ApiErrorLike;
  const status = apiError?.response?.status;
  const detail = apiError?.response?.data?.detail ?? apiError?.response?.data?.message;

  if (Array.isArray(detail)) {
    const messages = detail
      .filter((item): item is ValidationIssue => Boolean(item) && typeof item === 'object')
      .map(validationMessage);
    if (messages.length > 0) return messages.join(' ');
  }

  if (typeof detail === 'string') return translateMessage(detail);

  if (status === 401) return 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.';
  if (status === 403) return 'Bạn không có quyền thực hiện thao tác này.';
  if (status === 404) return 'Không tìm thấy dữ liệu được yêu cầu.';
  if (status === 409) return 'Dữ liệu đang xung đột với một thao tác khác. Vui lòng thử lại.';
  if (status === 422) return 'Dữ liệu nhập chưa hợp lệ. Vui lòng kiểm tra lại các trường.';
  if (status && status >= 500) return 'Máy chủ đang gặp lỗi. Vui lòng thử lại sau.';

  return translateMessage(apiError?.message);
}

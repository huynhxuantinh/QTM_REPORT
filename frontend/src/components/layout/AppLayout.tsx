import React, { useEffect, useRef, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/useAuth';
import {
  Activity,
  Server,
  FileText,
  Settings as SettingsIcon,
  LogOut,
  PlayCircle,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Menu,
  X,
} from 'lucide-react';
import { useRunAllChecks, useScanPolling } from '@/features/checks/hooks/useChecks';
import { getErrorMessage, getExecutionStatusLabel } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';

export const AppLayout: React.FC = () => {
  const { username, logout } = useAuth();
  const navigate = useNavigate();
  const [activeScanId, setActiveScanId] = useState<number | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { success, info, error: notifyError } = useNotifications();
  const notifiedScanId = useRef<number | null>(null);

  const runAllMutation = useRunAllChecks();
  const { data: scanData } = useScanPolling(activeScanId);

  useEffect(() => {
    if (!scanData || notifiedScanId.current === scanData.id) return;
    if (scanData.execution_status === 'succeeded') {
      notifiedScanId.current = scanData.id;
      success('Quét toàn bộ đã hoàn tất', `Đã kiểm tra ${scanData.completed_checks}/${scanData.total_checks} thiết bị.`);
    } else if (scanData.execution_status === 'failed') {
      notifiedScanId.current = scanData.id;
      notifyError('Đợt quét thất bại', 'Vui lòng kiểm tra trạng thái backend và thử lại.');
    }
  }, [notifyError, scanData, success]);

  const handleRunAll = async () => {
    try {
      const res = await runAllMutation.mutateAsync();
      setActiveScanId(res.id);
      info('Đã bắt đầu quét', `Đợt quét #${res.id} đang kiểm tra các thiết bị hoạt động.`);
    } catch (error: unknown) {
      notifyError('Không thể bắt đầu quét', getErrorMessage(error));
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isScanning =
    runAllMutation.isPending ||
    (scanData && (scanData.execution_status === 'running' || scanData.execution_status === 'queued'));

  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      {/* Top Navigation Bar */}
      <nav className="navbar navbar-expand-lg navbar-light app-navbar sticky-top px-3">
        <div className="container-fluid">
          <NavLink className="navbar-brand d-flex align-items-center gap-2 fw-bold text-dark me-4" to="/">
            <div className="bg-primary p-1.5 rounded text-white d-flex align-items-center justify-content-center">
              <Activity size={20} />
            </div>
            <span>Network Health Check</span>
          </NavLink>

          <button
            className="navbar-toggler border-0"
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Mở hoặc đóng trình đơn điều hướng"
          >
            {isMobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>

          <div className={`app-navbar-collapse navbar-collapse ${isMobileMenuOpen ? 'show' : ''}`}>
            <ul className="navbar-nav me-auto mb-2 mb-lg-0 gap-1">
              <li className="nav-item">
                <NavLink
                  to="/"
                  end
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center gap-1.5 px-3 rounded ${
                      isActive ? 'active bg-primary text-white fw-semibold shadow-sm' : 'text-secondary'
                    }`
                  }
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Activity size={16} />
                  <span>Tổng quan</span>
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/devices"
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center gap-1.5 px-3 rounded ${
                      isActive ? 'active bg-primary text-white fw-semibold shadow-sm' : 'text-secondary'
                    }`
                  }
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Server size={16} />
                  <span>Thiết bị</span>
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/reports"
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center gap-1.5 px-3 rounded ${
                      isActive ? 'active bg-primary text-white fw-semibold shadow-sm' : 'text-secondary'
                    }`
                  }
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <FileText size={16} />
                  <span>Báo cáo</span>
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/settings"
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center gap-1.5 px-3 rounded ${
                      isActive ? 'active bg-primary text-white fw-semibold shadow-sm' : 'text-secondary'
                    }`
                  }
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <SettingsIcon size={16} />
                  <span>Cấu hình</span>
                </NavLink>
              </li>
            </ul>

            <div className="d-flex align-items-center gap-3">
              <button
                className={`btn btn-sm d-flex align-items-center gap-1.5 ${
                  isScanning ? 'btn-warning text-dark' : 'btn-outline-primary bg-white'
                }`}
                onClick={handleRunAll}
                disabled={isScanning}
                title="Quét toàn bộ router trong mạng"
              >
                {isScanning ? (
                  <>
                    <Loader2 size={16} className="spinner-border-sm animate-spin" />
                    <span>Đang quét ({scanData?.completed_checks || 0}/{scanData?.total_checks || '...'})</span>
                  </>
                ) : (
                  <>
                    <PlayCircle size={16} />
                    <span>Quét tất cả</span>
                  </>
                )}
              </button>

              <div className="dropdown">
                <button
                  className="btn btn-sm btn-light border dropdown-toggle d-flex align-items-center gap-2 text-dark"
                  type="button"
                  data-bs-toggle="dropdown"
                  id="userDropdown"
                >
                  <span className="badge bg-secondary rounded-circle px-1.5 py-1">
                    {username?.charAt(0).toUpperCase() || 'A'}
                  </span>
                  <span className="text-dark small">{username || 'Quản trị viên'}</span>
                </button>
                <ul className="dropdown-menu dropdown-menu-end shadow" aria-labelledby="userDropdown">
                  <li>
                    <button className="dropdown-item text-danger d-flex align-items-center gap-2" onClick={handleLogout}>
                      <LogOut size={16} />
                      <span>Đăng xuất</span>
                    </button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Real-time Scan Progress Banner */}
      {activeScanId && scanData && (
        <div
          className={`border-bottom px-4 py-2 d-flex align-items-center justify-content-between text-sm ${
            scanData.execution_status === 'running' || scanData.execution_status === 'queued'
              ? 'bg-warning-subtle text-dark border-warning'
              : scanData.execution_status === 'succeeded'
              ? 'bg-success-subtle text-success-emphasis border-success'
              : 'bg-danger-subtle text-danger-emphasis border-danger'
          }`}
        >
          <div className="d-flex align-items-center gap-2 small">
            {scanData.execution_status === 'running' || scanData.execution_status === 'queued' ? (
              <Loader2 size={16} className="text-warning animate-spin" />
            ) : scanData.execution_status === 'succeeded' ? (
              <CheckCircle2 size={16} className="text-success" />
            ) : (
              <AlertCircle size={16} className="text-danger" />
            )}
            <span>
              <strong>Đợt quét #{scanData.id}:</strong> {getExecutionStatusLabel(scanData.execution_status)} — Đã hoàn thành{' '}
              {scanData.completed_checks}/{scanData.total_checks} thiết bị
              {scanData.failed_checks > 0 && ` (${scanData.failed_checks} lỗi kết nối)`}.
            </span>
          </div>
          {(scanData.execution_status === 'succeeded' || scanData.execution_status === 'failed') && (
            <button
              className="btn btn-link btn-sm p-0 text-decoration-none text-muted"
              onClick={() => setActiveScanId(null)}
            >
              Đóng
            </button>
          )}
        </div>
      )}

      {/* Main Page Content */}
      <main className="flex-grow-1 py-4">
        <div className="container-fluid px-4">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-top py-3 text-center text-muted small mt-auto">
        <div className="container-fluid">
          Hệ thống kiểm tra sức khỏe mạng — Cisco IOS, GNS3 và Netmiko
        </div>
      </footer>
    </div>
  );
};

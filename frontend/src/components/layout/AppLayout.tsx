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
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';
import { useRunAllChecks, useScanPolling } from '@/features/checks/hooks/useChecks';
import { getErrorMessage, getExecutionStatusLabel } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';

export const AppLayout: React.FC = () => {
  const { username, logout } = useAuth();
  const navigate = useNavigate();
  const [activeScanId, setActiveScanId] = useState<number | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(
    () => window.localStorage.getItem('sidebar-collapsed') === 'true',
  );
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

  useEffect(() => {
    if (!isMobileMenuOpen) return;

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsMobileMenuOpen(false);
    };

    document.addEventListener('keydown', closeOnEscape);
    return () => document.removeEventListener('keydown', closeOnEscape);
  }, [isMobileMenuOpen]);

  useEffect(() => {
    window.localStorage.setItem('sidebar-collapsed', String(isSidebarCollapsed));
  }, [isSidebarCollapsed]);

  const navigationItems = [
    { to: '/', label: 'Tổng quan', icon: Activity, end: true },
    { to: '/devices', label: 'Thiết bị', icon: Server },
    { to: '/reports', label: 'Báo cáo', icon: FileText },
    { to: '/settings', label: 'Cấu hình', icon: SettingsIcon },
  ];

  return (
    <div className="app-shell bg-light">
      {isMobileMenuOpen && (
        <button
          type="button"
          className="app-sidebar-backdrop"
          aria-label="Đóng trình đơn điều hướng"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      <aside
        id="main-navigation"
        className={`app-sidebar ${isMobileMenuOpen ? 'is-open' : ''} ${isSidebarCollapsed ? 'is-collapsed' : ''}`}
        aria-label="Điều hướng chính"
      >
        <div className="app-sidebar-header">
          <NavLink className="app-sidebar-brand" to="/" onClick={() => setIsMobileMenuOpen(false)}>
            <span className="app-brand-icon" aria-hidden="true">
              <img className="app-brand-logo" src="/network-health-logo.png" alt="" />
            </span>
            <span className="app-sidebar-brand-copy">
              <strong>Network Health</strong>
              <small>Hệ thống giám sát mạng</small>
            </span>
          </NavLink>
          <button
            type="button"
            className="app-sidebar-toggle"
            onClick={() => setIsSidebarCollapsed((collapsed) => !collapsed)}
            aria-label={isSidebarCollapsed ? 'Mở rộng thanh menu' : 'Thu gọn thanh menu'}
            title={isSidebarCollapsed ? 'Mở rộng menu' : 'Thu gọn menu'}
          >
            {isSidebarCollapsed ? <PanelLeftOpen size={19} /> : <PanelLeftClose size={19} />}
          </button>
          <button
            type="button"
            className="app-sidebar-close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Đóng trình đơn điều hướng"
          >
            <X size={22} />
          </button>
        </div>

        <nav className="app-sidebar-nav">
          <p className="app-sidebar-label">ĐIỀU HƯỚNG</p>
          <ul className="list-unstyled m-0 d-grid gap-1">
            {navigationItems.map(({ to, label, icon: Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) => `app-sidebar-link ${isActive ? 'active' : ''}`}
                  onClick={() => setIsMobileMenuOpen(false)}
                  title={isSidebarCollapsed ? label : undefined}
                >
                  <Icon size={19} aria-hidden="true" />
                  <span className="app-nav-label">{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="app-sidebar-footer">
          <button
            className={`btn app-scan-button ${isScanning ? 'btn-warning text-dark' : 'btn-primary'}`}
            onClick={handleRunAll}
            disabled={isScanning}
            title="Quét toàn bộ router trong mạng"
          >
            {isScanning ? (
              <>
                <Loader2 size={17} className="animate-spin" aria-hidden="true" />
                <span className="app-scan-label">Đang quét ({scanData?.completed_checks || 0}/{scanData?.total_checks || '...'})</span>
              </>
            ) : (
              <>
                <PlayCircle size={18} aria-hidden="true" />
                <span className="app-scan-label">Quét tất cả thiết bị</span>
              </>
            )}
          </button>

          <div className="app-user-card">
            <span className="app-user-avatar" aria-hidden="true">
              {username?.charAt(0).toUpperCase() || 'A'}
            </span>
            <span className="app-user-info">
              <strong>{username || 'Quản trị viên'}</strong>
              <small>Quản trị hệ thống</small>
            </span>
            <button type="button" className="app-logout-button" onClick={handleLogout} aria-label="Đăng xuất" title="Đăng xuất">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      <div className="app-workspace">
        <header className="app-mobile-header">
          <NavLink className="app-mobile-brand" to="/">
            <span className="app-brand-icon" aria-hidden="true">
              <img className="app-brand-logo" src="/network-health-logo.png" alt="" />
            </span>
            <strong>Network Health</strong>
          </NavLink>
          <button
            className="app-mobile-menu-button"
            type="button"
            onClick={() => setIsMobileMenuOpen(true)}
            aria-label="Mở trình đơn điều hướng"
            aria-expanded={isMobileMenuOpen}
            aria-controls="main-navigation"
          >
            <Menu size={22} />
          </button>
        </header>

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
    </div>
  );
};

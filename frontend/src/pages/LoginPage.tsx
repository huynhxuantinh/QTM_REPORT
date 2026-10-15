import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  Router,
  ShieldCheck,
  User,
  Wifi,
} from 'lucide-react';
import { useAuth } from '@/context/useAuth';
import { getErrorMessage } from '@/utils/i18n';
import './LoginPage.css';

interface LoginLocationState {
  from?: {
    pathname?: string;
  };
}

const NetworkScene: React.FC = () => (
  <div className="login-network-scene" aria-hidden="true">
    <svg className="login-network-links" viewBox="0 0 620 360" role="presentation">
      <path className="network-link network-link-one" d="M310 180 L124 76" />
      <path className="network-link network-link-two" d="M310 180 L500 72" />
      <path className="network-link network-link-three" d="M310 180 L538 235" />
      <path className="network-link network-link-four" d="M310 180 L326 316" />
      <path className="network-link network-link-five" d="M310 180 L86 252" />
      <circle className="network-packet network-packet-one" cx="0" cy="0" r="5" />
      <circle className="network-packet network-packet-two" cx="0" cy="0" r="5" />
      <circle className="network-packet network-packet-three" cx="0" cy="0" r="5" />
    </svg>

    <div className="network-core">
      <span className="network-core-ring" />
      <BrainCircuit size={42} />
      <small>AI CORE</small>
    </div>

    <div className="network-node network-node-r1"><Router size={22} /><span>R1</span></div>
    <div className="network-node network-node-r2"><Router size={22} /><span>R2</span></div>
    <div className="network-node network-node-r3"><Router size={22} /><span>R3</span></div>
    <div className="network-node network-node-db"><Activity size={22} /><span>Health</span></div>
    <div className="network-node network-node-wifi"><Wifi size={22} /><span>Network</span></div>

    <div className="network-status-card">
      <span className="network-status-dot" />
      <div>
        <strong>Hệ thống đang trực tuyến</strong>
        <small>Giám sát thiết bị theo thời gian thực</small>
      </div>
    </div>
  </div>
);

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as LoginLocationState | null)?.from?.pathname || '/';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login({ username: username.trim(), password });
      navigate(from, { replace: true });
    } catch (loginError: unknown) {
      setError(getErrorMessage(loginError, 'Tên đăng nhập hoặc mật khẩu không chính xác.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <div className="login-grid" aria-hidden="true" />
      <div className="login-glow login-glow-one" aria-hidden="true" />
      <div className="login-glow login-glow-two" aria-hidden="true" />

      <div className="login-layout">
        <section className="login-hero" aria-labelledby="login-hero-title">
          <div className="login-brand">
            <span className="login-brand-icon" aria-hidden="true">
              <img src="/network-health-logo.png" alt="" />
            </span>
            <span>Network Health Check</span>
          </div>

          <div className="login-hero-copy">
            <div className="login-eyebrow">
              <span className="login-eyebrow-dot" />
              Nền tảng giám sát mạng thông minh
            </div>
            <h1 id="login-hero-title">
              AI quan sát.<br />
              <span>Mạng luôn ổn định.</span>
            </h1>
            <p>
              Thu thập CPU, RAM, trạng thái cổng, độ trễ và cảnh báo từ router Cisco IOS
              trên một giao diện duy nhất.
            </p>
          </div>

          <NetworkScene />

          <div className="login-capabilities" aria-label="Khả năng của hệ thống">
            <div><CheckCircle2 size={16} /><span>Quét tự động</span></div>
            <div><CheckCircle2 size={16} /><span>Cảnh báo tức thời</span></div>
            <div><CheckCircle2 size={16} /><span>Báo cáo trực quan</span></div>
          </div>
        </section>

        <section className="login-panel-wrap" aria-label="Đăng nhập quản trị">
          <div className="login-panel">
            <div className="login-panel-accent" aria-hidden="true" />

            <div className="login-security-chip">
              <ShieldCheck size={15} />
              Kết nối quản trị an toàn
            </div>

            <div className="login-heading">
              <h2>Chào mừng trở lại</h2>
              <p>Đăng nhập để tiếp tục giám sát hệ thống mạng.</p>
            </div>

            {error && (
              <div className="login-alert" role="alert" aria-live="assertive">
                <AlertCircle size={18} aria-hidden="true" />
                <div>
                  <strong>Đăng nhập thất bại</strong>
                  <span>{error}</span>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="login-field">
                <label htmlFor="login-username">Tài khoản</label>
                <div className="login-input-wrap">
                  <User size={19} aria-hidden="true" />
                  <input
                    id="login-username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    placeholder="Nhập tài khoản quản trị"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    required
                    autoFocus
                  />
                </div>
              </div>

              <div className="login-field">
                <label htmlFor="login-password">Mật khẩu</label>
                <div className="login-input-wrap">
                  <LockKeyhole size={19} aria-hidden="true" />
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Nhập mật khẩu"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="login-password-toggle"
                    onClick={() => setShowPassword((current) => !current)}
                    aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button type="submit" className="login-submit" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <span className="login-spinner" aria-hidden="true" />
                    <span>Đang xác thực...</span>
                  </>
                ) : (
                  <>
                    <span>Đăng nhập hệ thống</span>
                    <ArrowRight size={19} aria-hidden="true" />
                  </>
                )}
              </button>
            </form>

            <div className="login-demo-note">
              <span className="login-demo-icon"><Router size={17} /></span>
              <div>
                <strong>Môi trường thực hành GNS3</strong>
                <span>Quản lý tập trung router Cisco IOS qua SSH và Netmiko.</span>
              </div>
            </div>

            <div className="login-trust">
              <ShieldCheck size={14} />
              Phiên đăng nhập được bảo vệ bằng access token
            </div>
          </div>
        </section>
      </div>

      <footer className="login-footer">
        <span>Network Health Check</span>
        <span>FastAPI · PostgreSQL · Netmiko · React</span>
      </footer>
    </main>
  );
};

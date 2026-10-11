import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Giao diện gặp lỗi:', error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="card border-danger shadow-sm my-4">
          <div className="card-body text-center py-4">
            <div className="text-danger mb-2">
              <AlertOctagon size={40} />
            </div>
            <h5 className="card-title text-danger fw-bold">Đã xảy ra lỗi giao diện</h5>
            <p className="card-text text-muted small mb-3">
              {this.state.error?.message || 'Không thể hiển thị thành phần này.'}
            </p>
            <button className="btn btn-outline-danger btn-sm" onClick={this.handleReset}>
              <RotateCcw size={14} className="me-1" /> Thử lại
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

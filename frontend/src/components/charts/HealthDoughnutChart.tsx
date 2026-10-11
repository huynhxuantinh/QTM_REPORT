import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import '@/components/charts/chartSetup';

interface HealthDoughnutChartProps {
  healthy: number;
  warning: number;
  critical: number;
  unknown?: number;
}

export const HealthDoughnutChart: React.FC<HealthDoughnutChartProps> = ({
  healthy,
  warning,
  critical,
  unknown = 0,
}) => {
  const total = healthy + warning + critical + unknown;

  if (total === 0) {
    return (
      <div className="d-flex align-items-center justify-content-center text-muted small" style={{ height: '13rem' }}>
        Chưa có dữ liệu thiết bị
      </div>
    );
  }

  const data = {
    labels: ['Tốt', 'Cảnh báo', 'Nghiêm trọng', 'Chưa xác định'],
    datasets: [
      {
        data: [healthy, warning, critical, unknown],
        backgroundColor: [
          '#10B981', // Emerald 500
          '#F59E0B', // Amber 500
          '#F43F5E', // Rose 500
          '#64748B', // Slate 500
        ],
        hoverBackgroundColor: [
          '#34D399',
          '#FBBF24',
          '#FB7185',
          '#94A3B8',
        ],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '76%',
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#64748b',
          boxWidth: 10,
          boxHeight: 10,
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 16,
          font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
        },
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 10,
        boxPadding: 4,
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            const val = context.raw || 0;
            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
            return ` ${context.label}: ${val} (${pct}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="position-relative w-100 d-flex align-items-center justify-content-center" style={{ height: '14rem' }}>
      <Doughnut data={data} options={options} />
      <div className="position-absolute top-50 start-50 translate-middle text-center pe-none">
        <div className="fs-3 fw-bold text-dark font-monospace">{total}</div>
        <div className="small text-uppercase text-muted fw-semibold">
          Thiết bị
        </div>
      </div>
    </div>
  );
};

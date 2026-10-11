import React from 'react';
import { Line } from 'react-chartjs-2';
import '@/components/charts/chartSetup';

interface MetricTrendChartProps {
  timestamps: string[];
  values: (number | null)[];
  label: string;
  unit: '%' | 'ms';
  color?: string;
  height?: number;
  thresholdWarning?: number;
  thresholdCritical?: number;
}

export const MetricTrendChart: React.FC<MetricTrendChartProps> = ({
  timestamps,
  values,
  label,
  unit,
  color = '#6366F1', // Indigo 500
  height = 240,
}) => {
  if (timestamps.length === 0 || values.every((v) => v === null)) {
    return (
      <div
        className="d-flex align-items-center justify-content-center text-muted small bg-light rounded-3 border"
        style={{ height: `${height}px` }}
      >
        Chưa có dữ liệu lịch sử đo
      </div>
    );
  }

  const chartData = {
    labels: timestamps,
    datasets: [
      {
        label,
        data: values,
        borderColor: color,
        backgroundColor: `${color}1A`, // 10% opacity
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: color,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 7,
        spanGaps: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false as const,
    plugins: {
      legend: {
        display: false,
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
            const val = context.raw;
            if (val === null || val === undefined) return ' Không có dữ liệu';
            return ` ${label}: ${val}${unit}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: unit === '%' ? 100 : undefined,
        ticks: {
          color: '#64748b',
          callback: (value: any) => `${value}${unit}`,
          font: { family: "'JetBrains Mono', monospace", size: 11 },
        },
        grid: {
          color: 'rgba(100, 116, 139, 0.12)',
        },
        border: {
          display: false,
        },
      },
      x: {
        ticks: {
          color: '#64748b',
          maxRotation: 0,
          font: { family: "'JetBrains Mono', monospace", size: 10 },
        },
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
      },
    },
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: `${height}px` }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

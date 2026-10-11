import React from 'react';

export const SkeletonCard: React.FC<{ rows?: number }> = ({ rows = 3 }) => {
  return (
    <div className="card border-0 shadow-sm rounded-3 p-4 placeholder-glow">
      <span className="placeholder col-5 rounded mb-3" style={{ height: '20px' }} />
      {Array.from({ length: rows }).map((_, idx) => (
        <span
          key={idx}
          className="placeholder rounded mb-2 d-block"
          style={{ width: `${100 - idx * 15}%` }}
        />
      ))}
    </div>
  );
};

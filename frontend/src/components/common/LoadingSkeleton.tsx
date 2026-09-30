import React from 'react';

interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className = '',
  lines = 3,
}) => {
  return (
    <div className={`space-y-3 animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, idx) => (
        <div
          key={idx}
          className="h-4 bg-slate-800/60 rounded border border-slate-700/40"
          style={{ width: `${100 - (idx % 3) * 15}%` }}
        />
      ))}
    </div>
  );
};

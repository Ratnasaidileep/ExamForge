import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'indigo' | 'teal';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className = ''
}) => {
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs font-medium'
  };

  const variantStyles = {
    success: 'bg-emerald-50 text-[#15803D] border border-emerald-200',
    warning: 'bg-amber-50 text-[#B45309] border border-amber-200',
    error: 'bg-rose-50 text-[#B91C1C] border border-rose-200',
    info: 'bg-blue-50 text-[#1D4ED8] border border-blue-200',
    indigo: 'bg-indigo-50 text-[#3730A3] border border-indigo-200',
    teal: 'bg-teal-50 text-[#0F766E] border border-teal-200',
    neutral: 'bg-slate-100 text-[#475569] border border-slate-200'
  };

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
};

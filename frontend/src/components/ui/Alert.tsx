import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  action,
  className = ''
}) => {
  const styles = {
    info: {
      bg: 'bg-blue-50 border-blue-200 text-blue-900',
      icon: <Info className="w-5 h-5 text-[#1D4ED8] flex-shrink-0" />
    },
    success: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-900',
      icon: <CheckCircle2 className="w-5 h-5 text-[#15803D] flex-shrink-0" />
    },
    warning: {
      bg: 'bg-amber-50 border-amber-200 text-amber-900',
      icon: <AlertTriangle className="w-5 h-5 text-[#B45309] flex-shrink-0" />
    },
    error: {
      bg: 'bg-rose-50 border-rose-200 text-rose-900',
      icon: <AlertCircle className="w-5 h-5 text-[#B91C1C] flex-shrink-0" />
    }
  };

  const current = styles[type];

  return (
    <div className={`p-4 rounded-xl border flex gap-3 text-sm ${current.bg} ${className}`}>
      {current.icon}
      <div className="flex-1">
        {title && <h4 className="font-semibold mb-0.5">{title}</h4>}
        <div className="text-xs leading-relaxed opacity-95">{children}</div>
      </div>
      {action && <div className="ml-auto self-center">{action}</div>}
    </div>
  );
};

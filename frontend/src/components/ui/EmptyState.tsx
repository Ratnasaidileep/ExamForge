import React from 'react';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white rounded-xl border border-dashed border-[#CBD5E1]">
      {icon && <div className="p-3 bg-slate-50 text-[#64748B] rounded-full mb-3">{icon}</div>}
      <h3 className="text-sm font-semibold text-[#0F172A]">{title}</h3>
      <p className="text-xs text-[#64748B] max-w-sm mt-1 mb-4 leading-relaxed">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
};

import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  leftIcon,
  className = '',
  id,
  ...props
}, ref) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-[#1E293B] mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            {leftIcon}
          </div>
        )}
        <input
          id={inputId}
          ref={ref}
          className={`w-full rounded-lg border text-sm text-[#0F172A] placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
            leftIcon ? 'pl-9' : 'pl-3'
          } pr-3 py-2 ${
            error
              ? 'border-[#B91C1C] focus:ring-rose-200'
              : 'border-[#CBD5E1] focus:border-[#3730A3] focus:ring-indigo-100'
          } ${className}`}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-[#B91C1C] mt-1">{error}</p>}
      {helperText && !error && <p className="text-xs text-[#64748B] mt-1">{helperText}</p>}
    </div>
  );
});

Input.displayName = 'Input';

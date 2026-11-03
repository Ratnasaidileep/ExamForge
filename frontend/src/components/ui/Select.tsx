import React from 'react';

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({
  label,
  options,
  error,
  className = '',
  id,
  ...props
}, ref) => {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-xs font-semibold text-[#1E293B] dark:text-slate-200 mb-1.5">
          {label}
        </label>
      )}
      <select
        id={selectId}
        ref={ref}
        className={`w-full rounded-lg border text-sm text-[#0F172A] dark:text-slate-100 bg-white dark:bg-[#0F172A] px-3 py-2 focus:outline-none focus:ring-2 transition-all ${
          error
            ? 'border-[#B91C1C] focus:ring-rose-200'
            : 'border-[#CBD5E1] dark:border-slate-700 focus:border-[#3730A3] dark:focus:border-indigo-400 focus:ring-indigo-100 dark:focus:ring-indigo-900/40'
        } ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-[#B91C1C] mt-1">{error}</p>}
    </div>
  );
});

Select.displayName = 'Select';

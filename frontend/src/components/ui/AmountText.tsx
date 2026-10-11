import React, { useEffect, useState } from 'react';

interface AmountTextProps {
  amountPaise: number;
  currency?: string;
  type?: 'owed' | 'owes' | 'neutral' | 'auto';
  showSymbol?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const AmountText: React.FC<AmountTextProps> = ({
  amountPaise,
  currency = 'INR',
  type = 'auto',
  showSymbol = true,
  className = '',
  size = 'md',
}) => {
  const [displayPaise, setDisplayPaise] = useState(amountPaise);

  useEffect(() => {
    let start = displayPaise;
    let end = amountPaise;
    if (start === end) return;

    let startTime: number | null = null;
    const duration = 400; // ms

    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const current = Math.round(start + (end - start) * progress);
      setDisplayPaise(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    const animFrame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animFrame);
  }, [amountPaise]);

  const rupees = (Math.abs(displayPaise) / 100).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const getSymbol = () => {
    if (currency === 'INR') return '₹';
    if (currency === 'USD') return '$';
    return `${currency} `;
  };

  const resolvedType =
    type === 'auto'
      ? displayPaise > 0
        ? 'owed'
        : displayPaise < 0
        ? 'owes'
        : 'neutral'
      : type;

  const colorClasses = {
    owed: 'text-emerald-600 dark:text-emerald-400 font-semibold',
    owes: 'text-rose-600 dark:text-rose-400 font-semibold',
    neutral: 'text-slate-700 dark:text-slate-300',
  }[resolvedType];

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base font-medium',
    lg: 'text-lg font-semibold',
    xl: 'text-xl font-bold',
    '2xl': 'text-2xl font-extrabold',
  }[size];

  return (
    <span className={`tabular-nums inline-flex items-center tracking-tight ${colorClasses} ${sizeClasses} ${className}`}>
      {resolvedType === 'owes' && displayPaise !== 0 && '-'}
      {showSymbol && getSymbol()}
      {rupees}
    </span>
  );
};

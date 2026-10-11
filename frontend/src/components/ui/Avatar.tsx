import React from 'react';

interface AvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const COLORS = [
  'bg-indigo-500 text-white dark:bg-indigo-600',
  'bg-emerald-500 text-white dark:bg-emerald-600',
  'bg-rose-500 text-white dark:bg-rose-600',
  'bg-amber-500 text-white dark:bg-amber-600',
  'bg-sky-500 text-white dark:bg-sky-600',
  'bg-purple-500 text-white dark:bg-purple-600',
  'bg-teal-500 text-white dark:bg-teal-600',
  'bg-pink-500 text-white dark:bg-pink-600',
];

export const Avatar: React.FC<AvatarProps> = ({ name, size = 'md', className = '' }) => {
  const getInitials = (str: string) => {
    if (!str) return '?';
    const parts = str.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return str.slice(0, 2).toUpperCase();
  };

  const getHashColor = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const idx = Math.abs(hash) % COLORS.length;
    return COLORS[idx];
  };

  const sizeClasses = {
    sm: 'w-7 h-7 text-xs font-semibold',
    md: 'w-9 h-9 text-sm font-semibold',
    lg: 'w-11 h-11 text-base font-bold',
    xl: 'w-14 h-14 text-lg font-bold',
  }[size];

  return (
    <div
      className={`inline-flex items-center justify-center rounded-full shadow-sm select-none transition-transform hover:scale-105 ${getHashColor(
        name
      )} ${sizeClasses} ${className}`}
      title={name}
    >
      {getInitials(name)}
    </div>
  );
};

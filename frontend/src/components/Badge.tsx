import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'dark' | 'outline' | 'champagne';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  className = '',
}) => {
  const variantStyles = {
    default: 'bg-surface-container text-on-surface',
    secondary: 'bg-secondary-fixed text-on-secondary-fixed',
    dark: 'bg-primary text-on-primary',
    outline: 'border border-outline-variant text-on-surface-variant bg-transparent',
    champagne: 'bg-surface-container-high text-secondary',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-label-sm font-label-sm uppercase tracking-wider',
    md: 'px-3 py-1 text-label-md font-label-md uppercase tracking-wider',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
};

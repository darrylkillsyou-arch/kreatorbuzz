import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: string;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-label-lg transition-all rounded-full select-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-primary text-on-primary hover:bg-primary-container hover:text-on-surface shadow-sm',
    secondary: 'bg-surface-container text-on-surface hover:bg-surface-container-high',
    tertiary: 'bg-surface-container-high text-on-surface hover:bg-surface-container-highest',
    outline: 'border border-outline-variant text-on-surface hover:border-secondary hover:text-secondary bg-transparent',
    ghost: 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-label-md gap-1.5',
    md: 'px-4 py-2 text-label-lg gap-2',
    lg: 'px-6 py-3 text-label-lg gap-2.5',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" />
      ) : icon && iconPosition === 'left' ? (
        <span className="material-symbols-outlined text-[18px]">{icon}</span>
      ) : null}
      <span>{children}</span>
      {!isLoading && icon && iconPosition === 'right' && (
        <span className="material-symbols-outlined text-[18px]">{icon}</span>
      )}
    </button>
  );
};

import React, { useState } from 'react';
import { getInitials } from '../lib/creatorImages';

interface CreatorAvatarProps {
  src?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  shape?: 'circle' | 'rounded';
}

/**
 * Creator profile avatar with automatic initials fallback on image load error or missing src.
 * Matches CODE XERO premium black & gold design language.
 */
export const CreatorAvatar: React.FC<CreatorAvatarProps> = ({
  src,
  name = 'Creator',
  size = 'md',
  className = '',
  shape = 'circle',
}) => {
  const [hasError, setHasError] = useState(false);

  const initials = getInitials(name);

  const sizeClasses: Record<string, string> = {
    xs: 'w-6 h-6 text-[10px]',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-14 h-14 text-base',
    xl: 'w-24 h-24 sm:w-28 sm:h-28 text-2xl',
  };

  const shapeClass = shape === 'circle' ? 'rounded-full' : 'rounded-2xl';

  if (!src || hasError) {
    return (
      <div
        className={`${sizeClasses[size] || sizeClasses.md} ${shapeClass} bg-surface-container-high text-secondary border border-outline-variant/50 font-medium flex items-center justify-center flex-shrink-0 select-none shadow-sm ${className}`}
        title={name}
        aria-label={name}
      >
        <span>{initials}</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={name}
      className={`${sizeClasses[size] || sizeClasses.md} ${shapeClass} object-cover flex-shrink-0 bg-surface-container border border-outline-variant/30 ${className}`}
      onError={() => setHasError(true)}
      loading="lazy"
    />
  );
};

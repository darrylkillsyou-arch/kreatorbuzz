import React from 'react';

interface BrandMarkProps {
  size?: 'sm' | 'md' | 'lg';
  showWordmark?: boolean;
  className?: string;
  markClassName?: string;
}

/**
 * CODE XERO CX monogram used in the navbar, auth screens, and footer.
 */
export const BrandMark: React.FC<BrandMarkProps> = ({
  size = 'md',
  showWordmark = true,
  className = '',
  markClassName = '',
}) => {
  const box =
    size === 'lg' ? 'w-9 h-9' : size === 'sm' ? 'w-7 h-7' : 'w-8 h-8';
  const letters =
    size === 'lg' ? 'text-[11px]' : size === 'sm' ? 'text-[9px]' : 'text-[10px]';

  return (
    <span className={`inline-flex items-center gap-space-xs ${className}`}>
      <span
        className={`${box} rounded-lg bg-primary flex items-center justify-center text-secondary border border-secondary/30 shadow-sm ${markClassName}`}
        aria-hidden="true"
      >
        <span className={`font-display font-bold ${letters} text-secondary leading-none tracking-tight`}>
          CX
        </span>
      </span>
      {showWordmark && (
        <span className="font-headline-sm text-headline-sm tracking-tight text-on-surface ml-1">
          CODE XERO
        </span>
      )}
    </span>
  );
};

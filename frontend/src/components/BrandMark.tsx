import React from 'react';

interface BrandMarkProps {
  size?: 'sm' | 'md' | 'lg';
  showWordmark?: boolean;
  showTagline?: boolean;
  className?: string;
  markClassName?: string;
}

/**
 * KreatorBuzz brand mark and monogram.
 * Brand: KreatorBuzz
 * Tagline: Create Your Own Buzz
 */
export const BrandMark: React.FC<BrandMarkProps> = ({
  size = 'md',
  showWordmark = true,
  showTagline = false,
  className = '',
  markClassName = '',
}) => {
  const box =
    size === 'lg' ? 'w-10 h-10' : size === 'sm' ? 'w-7 h-7' : 'w-8 h-8';
  const letters =
    size === 'lg' ? 'text-[13px]' : size === 'sm' ? 'text-[9px]' : 'text-[11px]';

  return (
    <div className={`inline-flex items-center gap-space-xs ${className}`}>
      <span
        className={`${box} rounded-xl bg-gradient-to-br from-amber-400 via-amber-500 to-amber-600 flex items-center justify-center text-black border border-amber-300/40 shadow-sm shrink-0 transition-transform hover:scale-105 ${markClassName}`}
        aria-hidden="true"
      >
        <span className={`font-display font-extrabold ${letters} text-black leading-none tracking-tighter drop-shadow-xs`}>
          KB
        </span>
      </span>
      {showWordmark && (
        <div className="flex flex-col ml-1 leading-none">
          <span className="font-headline-sm text-headline-sm tracking-tight text-on-surface font-bold flex items-center">
            <span>Kreator</span>
            <span className="text-secondary font-black tracking-normal ml-0.5">Buzz</span>
          </span>
          {showTagline && (
            <span className="font-label-xs text-[10px] text-on-surface-variant font-medium tracking-wider uppercase mt-0.5">
              Create Your Own Buzz
            </span>
          )}
        </div>
      )}
    </div>
  );
};

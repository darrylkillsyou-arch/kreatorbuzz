import React from 'react';

interface IconProps {
  name: string;
  className?: string;
  size?: number | string;
  fill?: boolean;
}

export const Icon: React.FC<IconProps> = ({ name, className = '', size = 20, fill = false }) => {
  const style: React.CSSProperties = {
    fontSize: typeof size === 'number' ? `${size}px` : size,
    fontVariationSettings: fill ? "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24" : "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24",
  };

  return (
    <span className={`material-symbols-outlined select-none inline-block ${className}`} style={style}>
      {name}
    </span>
  );
};

import React from 'react';
import { Button } from './Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  icon?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionText,
  onAction,
  icon = 'auto_stories',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-space-xl bg-surface-container-low rounded-xl border border-outline-variant/30 text-center max-w-md mx-auto my-space-lg">
      <div className="w-14 h-14 rounded-full bg-surface-container-high flex items-center justify-center text-secondary mb-space-sm">
        <span className="material-symbols-outlined text-[28px]">{icon}</span>
      </div>
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-space-xs">{title}</h3>
      <p className="font-body-md text-body-md text-on-surface-variant mb-space-md">{description}</p>
      {actionText && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};

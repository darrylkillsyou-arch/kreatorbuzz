import React from 'react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-space-xl space-y-space-md min-h-[300px]">
      <div className="relative w-12 h-12">
        <div className="w-12 h-12 rounded-full border-2 border-surface-container-high border-t-secondary animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="w-2 h-2 rounded-full bg-secondary"></span>
        </div>
      </div>
      <p className="font-body-md text-body-md text-on-surface-variant animate-pulse">{message}</p>
    </div>
  );
};

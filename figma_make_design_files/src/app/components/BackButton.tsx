import React from 'react';
import { BackArrowIcon } from './Icons';

interface BackButtonProps {
  onClick?: () => void;
  label?: string;
  variant?: 'default' | 'light';
}

export function BackButton({ onClick, label, variant = 'default' }: BackButtonProps) {
  const color = variant === 'light' ? 'white' : 'var(--neutral-dark)';
  
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 p-2.5 rounded-lg hover:bg-neutral-light/30 transition-colors duration-200 min-w-[44px] min-h-[44px]"
      aria-label={label || 'Go back'}
    >
      <BackArrowIcon size={24} color={color} />
      {label && (
        <span className="font-medium" style={{ color }}>
          {label}
        </span>
      )}
    </button>
  );
}

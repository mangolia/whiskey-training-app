import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'error' | 'neutral';
  className?: string;
  onClick?: () => void;
}

export function Badge({ children, variant = 'primary', className = '', onClick }: BadgeProps) {
  const variants = {
    primary: 'bg-primary/10 text-primary border border-primary/20',
    success: 'bg-success/10 text-success border border-success/20',
    error: 'bg-error/10 text-error border border-error/20',
    neutral: 'bg-neutral-light/50 text-neutral-dark border border-neutral-light'
  };
  
  const interactiveClass = onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : '';
  
  return (
    <span 
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${variants[variant]} ${interactiveClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </span>
  );
}
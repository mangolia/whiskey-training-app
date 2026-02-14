import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'bordered';
  padding?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export function Card({ 
  children, 
  className = '', 
  variant = 'default',
  padding = 'md',
  onClick 
}: CardProps) {
  const paddingStyles = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-5'
  };
  
  const variantStyles = {
    default: 'bg-card shadow-[0px_2px_8px_rgba(184,134,11,0.08)]',
    bordered: 'bg-card border border-card-border'
  };
  
  const interactiveClass = onClick ? 'cursor-pointer hover:shadow-[0px_4px_12px_rgba(184,134,11,0.12)] transition-shadow duration-200' : '';
  
  return (
    <div 
      className={`rounded-[12px] ${variantStyles[variant]} ${paddingStyles[padding]} ${interactiveClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

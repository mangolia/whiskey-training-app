import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'disabled';
  children: React.ReactNode;
  fullWidth?: boolean;
}

export function Button({ 
  variant = 'primary', 
  children, 
  fullWidth = true,
  disabled,
  className = '',
  ...props 
}: ButtonProps) {
  const baseStyles = 'h-[52px] rounded-[10px] font-semibold transition-all duration-200 min-h-[var(--touch-min)]';
  
  const variants = {
    primary: `bg-primary text-white ${!disabled ? 'hover:bg-primary-hover active:scale-[0.98]' : ''} shadow-[0px_4px_12px_rgba(184,134,11,0.15)]`,
    secondary: 'bg-transparent text-primary border-2 border-primary hover:bg-primary/5 active:bg-primary/10',
    disabled: 'bg-neutral-light text-[#999999] cursor-not-allowed opacity-50'
  };
  
  const widthClass = fullWidth ? 'w-full' : '';
  const variantClass = disabled ? variants.disabled : variants[variant];
  
  return (
    <button
      className={`${baseStyles} ${variantClass} ${widthClass} ${className}`}
      disabled={disabled || variant === 'disabled'}
      {...props}
    >
      {children}
    </button>
  );
}

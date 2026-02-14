import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export function Input({ 
  label, 
  error, 
  helperText,
  className = '',
  id,
  ...props 
}: InputProps) {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  const [isFocused, setIsFocused] = React.useState(false);
  
  return (
    <div className="w-full">
      {label && (
        <label 
          htmlFor={inputId}
          className="block mb-2 text-sm font-medium text-neutral-dark"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full h-12 px-4 rounded-[10px] bg-input-background text-neutral-dark transition-all duration-200 outline-none ${className}`}
        style={{
          border: error 
            ? '2px solid var(--error)' 
            : isFocused 
              ? '2px solid var(--input-focus)' 
              : '2px solid transparent',
        }}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1 text-sm text-text-caption">{helperText}</p>
      )}
    </div>
  );
}

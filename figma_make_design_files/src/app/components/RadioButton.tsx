import React from 'react';

interface RadioButtonProps {
  checked?: boolean;
  onChange?: () => void;
  label?: string;
  name?: string;
  value?: string;
  id?: string;
}

export function RadioButton({ 
  checked = false, 
  onChange, 
  label, 
  name,
  value,
  id 
}: RadioButtonProps) {
  const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="flex items-center min-h-[44px]">
      <div className="relative">
        <input
          type="radio"
          id={radioId}
          name={name}
          value={value}
          checked={checked}
          onChange={onChange}
          className="sr-only"
        />
        <label
          htmlFor={radioId}
          className="flex items-center justify-center w-6 h-6 rounded-full border-2 cursor-pointer transition-all duration-200"
          style={{
            borderColor: checked ? 'var(--primary)' : 'var(--neutral-light)',
          }}
        >
          {checked && (
            <div 
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: 'white' }}
            />
          )}
        </label>
        {checked && (
          <div 
            className="absolute inset-0 rounded-full -z-10"
            style={{ backgroundColor: 'var(--primary)' }}
          />
        )}
      </div>
      {label && (
        <label 
          htmlFor={radioId} 
          className="ml-3 cursor-pointer select-none text-neutral-dark"
        >
          {label}
        </label>
      )}
    </div>
  );
}

import React from 'react';

interface CheckboxProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  label?: string;
  id?: string;
}

export function Checkbox({ checked = false, onChange, label, id }: CheckboxProps) {
  const handleChange = () => {
    onChange?.(!checked);
  };
  
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="flex items-center min-h-[44px]">
      <div className="relative">
        <input
          type="checkbox"
          id={checkboxId}
          checked={checked}
          onChange={handleChange}
          className="sr-only"
        />
        <label
          htmlFor={checkboxId}
          className="flex items-center justify-center w-6 h-6 rounded-[4px] border-2 cursor-pointer transition-all duration-200"
          style={{
            borderColor: checked ? 'var(--primary)' : 'var(--neutral-light)',
            backgroundColor: checked ? 'var(--primary)' : 'transparent',
          }}
        >
          {checked && (
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 16 16" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                d="M13 4L6 11L3 8" 
                stroke="white" 
                strokeWidth="2.5" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          )}
        </label>
      </div>
      {label && (
        <label 
          htmlFor={checkboxId} 
          className="ml-3 cursor-pointer select-none text-neutral-dark"
        >
          {label}
        </label>
      )}
    </div>
  );
}

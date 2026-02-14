import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onClear?: () => void;
}

export function SearchBar({ 
  placeholder = 'Search...', 
  value: controlledValue,
  onChange,
  onClear 
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  
  const value = controlledValue !== undefined ? controlledValue : internalValue;
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (controlledValue === undefined) {
      setInternalValue(newValue);
    }
    onChange?.(newValue);
  };
  
  const handleClear = () => {
    if (controlledValue === undefined) {
      setInternalValue('');
    }
    onChange?.('');
    onClear?.();
  };
  
  return (
    <div className="relative w-full">
      <div 
        className="flex items-center h-12 px-4 rounded-[24px] bg-input-background transition-all duration-200"
        style={{
          border: isFocused ? '2px solid var(--input-focus)' : '2px solid transparent',
        }}
      >
        <Search 
          className="flex-shrink-0 mr-3" 
          size={20} 
          strokeWidth={2}
          style={{ color: 'var(--neutral-dark)', opacity: 0.6 }}
        />
        <input
          type="text"
          value={value}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="flex-1 bg-transparent outline-none text-neutral-dark placeholder:text-neutral-dark placeholder:opacity-60"
        />
        {value && (
          <button
            onClick={handleClear}
            className="flex-shrink-0 ml-2 p-1 rounded-full hover:bg-neutral-light/50 transition-colors duration-200"
            aria-label="Clear search"
          >
            <X 
              size={18} 
              strokeWidth={2}
              style={{ color: 'var(--neutral-dark)', opacity: 0.6 }}
            />
          </button>
        )}
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { Card } from './Card';
import { Checkbox } from './Checkbox';
import { Button } from './Button';
import { Badge } from './Badge';

interface QuizOption {
  id: string;
  label: string;
}

interface QuizCardProps {
  whiskey: string;
  distillery: string;
  proof: string;
  options: QuizOption[];
  onSubmit?: (selectedIds: string[]) => void;
  sense?: 'nose' | 'palate' | 'finish';
  currentSelections?: string[];
}

export function QuizCard({ 
  whiskey, 
  distillery,
  proof,
  options, 
  onSubmit,
  sense = 'nose',
  currentSelections = []
}: QuizCardProps) {
  const [selectedOptions, setSelectedOptions] = useState<Set<string>>(new Set(currentSelections));
  
  // Update local state when currentSelections prop changes
  React.useEffect(() => {
    setSelectedOptions(new Set(currentSelections));
  }, [currentSelections]);
  
  const handleCheckboxChange = (optionId: string, checked: boolean) => {
    const newSelected = new Set(selectedOptions);
    if (checked) {
      newSelected.add(optionId);
    } else {
      newSelected.delete(optionId);
    }
    setSelectedOptions(newSelected);
  };
  
  const handleSubmit = () => {
    onSubmit?.(Array.from(selectedOptions));
  };
  
  return (
    <Card padding="lg" className="mb-4">
      {/* Whiskey Details Header */}
      <div className="mb-6 pb-5 border-b" style={{ borderColor: 'var(--neutral-light)' }}>
        <h3 className="mb-2 text-lg" style={{ 
          fontFamily: 'var(--font-heading)',
          color: 'var(--neutral-dark)'
        }}>
          {whiskey}
        </h3>
        <div className="flex flex-col gap-1">
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 500 }}>Distillery:</span> {distillery}
          </p>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 500 }}>Proof:</span> {proof}
          </p>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="mb-3 text-sm font-semibold text-neutral-dark">
          Select all flavor notes mentioned in the review:
        </h4>
        <div className="grid grid-cols-3 gap-3">
          {options.map((option) => (
            <button
              key={option.id}
              onClick={() => handleCheckboxChange(option.id, !selectedOptions.has(option.id))}
              className="min-h-[80px] px-3 py-4 rounded-lg border-2 transition-all duration-200 flex items-center justify-center text-center text-sm font-medium"
              style={{
                borderColor: selectedOptions.has(option.id) ? 'var(--primary)' : 'var(--neutral-light)',
                backgroundColor: selectedOptions.has(option.id) ? 'var(--primary)' : 'transparent',
                color: selectedOptions.has(option.id) ? 'white' : 'var(--neutral-dark)',
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
      
      <Button 
        variant="primary" 
        onClick={handleSubmit}
        disabled={selectedOptions.size === 0}
      >
        Submit Answer
      </Button>
    </Card>
  );
}
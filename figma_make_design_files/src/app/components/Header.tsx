import React from 'react';

interface HeaderProps {
  left?: React.ReactNode;
  center?: React.ReactNode;
  right?: React.ReactNode;
  className?: string;
}

export function Header({ left, center, right, className = '' }: HeaderProps) {
  return (
    <header className={`flex items-center justify-between px-5 py-4 ${className}`}>
      <div className="flex items-center min-w-[44px]">
        {left}
      </div>
      <div className="flex-1 flex items-center justify-center px-4">
        {center}
      </div>
      <div className="flex items-center min-w-[44px]">
        {right}
      </div>
    </header>
  );
}

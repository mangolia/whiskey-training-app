import React, { useState } from 'react';
import { MenuIcon, CloseIcon } from './Icons';

interface MenuItem {
  label: string;
  onClick?: () => void;
  active?: boolean;
}

interface HamburgerMenuProps {
  items: MenuItem[];
  logo?: React.ReactNode;
}

export function HamburgerMenu({ items, logo }: HamburgerMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };
  
  const handleItemClick = (item: MenuItem) => {
    item.onClick?.();
    setIsOpen(false);
  };
  
  return (
    <>
      {/* Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="p-2.5 rounded-lg hover:bg-neutral-light/30 transition-colors duration-200 min-w-[44px] min-h-[44px] flex items-center justify-center"
        aria-label="Menu"
      >
        <MenuIcon size={24} color="var(--neutral-dark)" />
      </button>
      
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 transition-opacity duration-300"
          style={{ backgroundColor: 'var(--menu-backdrop)' }}
          onClick={toggleMenu}
        />
      )}
      
      {/* Slide-in Menu Panel */}
      <div
        className={`fixed top-0 left-0 h-full z-50 transition-transform duration-300 ease-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{
          width: '280px',
          backgroundColor: 'var(--menu-bg)',
        }}
      >
        {/* Menu Header */}
        <div className="flex items-center justify-between p-5 border-b border-white/10">
          {logo && <div className="text-white">{logo}</div>}
          <button
            onClick={toggleMenu}
            className="ml-auto p-2 rounded-lg hover:bg-white/10 transition-colors duration-200 min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label="Close menu"
          >
            <CloseIcon size={24} color="white" />
          </button>
        </div>
        
        {/* Menu Items */}
        <nav className="py-4">
          {items.map((item, index) => (
            <button
              key={index}
              onClick={() => handleItemClick(item)}
              className={`w-full px-5 py-4 text-left text-lg transition-all duration-200 relative ${
                item.active 
                  ? 'text-accent' 
                  : 'text-white hover:bg-white/5'
              }`}
            >
              {item.active && (
                <div 
                  className="absolute left-0 top-0 bottom-0 w-1"
                  style={{ backgroundColor: 'var(--accent)' }}
                />
              )}
              <span className={item.active ? 'ml-0' : 'ml-0'}>
                {item.label}
              </span>
            </button>
          ))}
        </nav>
      </div>
    </>
  );
}

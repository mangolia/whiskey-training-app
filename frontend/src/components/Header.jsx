import { useState } from 'react';
import { Link } from 'react-router-dom';
import Menu from './Menu';

function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <header className="bg-unspoken-navy text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-2xl font-bold hover:text-unspoken-gold transition-colors">
              Whiskey Sensory Training
            </Link>

            {/* Hamburger Menu Button */}
            <button
              onClick={() => setMenuOpen(true)}
              className="hover:text-unspoken-gold transition-colors focus:outline-none"
              aria-label="Open menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Slide-out Menu */}
      <Menu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </>
  );
}

export default Header;

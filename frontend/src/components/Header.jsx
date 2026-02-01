import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-unspoken-navy text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold hover:text-unspoken-gold transition-colors">
            Whiskey Sensory Training
          </Link>
          <nav>
            <Link to="/" className="hover:text-unspoken-gold transition-colors">
              Home
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;

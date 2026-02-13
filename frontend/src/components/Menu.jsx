import { Link } from 'react-router-dom';

function Menu({ isOpen, onClose }) {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Menu Drawer */}
      <div
        className={`
          fixed top-0 right-0 h-full w-64 bg-white shadow-2xl z-50
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        {/* Close Button */}
        <div className="flex justify-end p-4">
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-unspoken-navy transition-colors"
            aria-label="Close menu"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Menu Items */}
        <nav className="px-4">
          <Link
            to="/"
            onClick={onClose}
            className="block py-4 text-lg font-semibold text-unspoken-navy hover:text-unspoken-gold border-b border-gray-200 transition-colors"
          >
            Home
          </Link>
          <Link
            to="/distilleries"
            onClick={onClose}
            className="block py-4 text-lg font-semibold text-unspoken-navy hover:text-unspoken-gold border-b border-gray-200 transition-colors"
          >
            Distilleries
          </Link>
        </nav>
      </div>
    </>
  );
}

export default Menu;

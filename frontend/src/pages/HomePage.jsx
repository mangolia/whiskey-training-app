import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle pre-filled search from distilleries page
  useEffect(() => {
    if (location.state?.searchQuery) {
      const query = location.state.searchQuery;
      setSearchQuery(query);
      // Trigger search automatically
      performSearch(query);
      // Clear the state so it doesn't trigger again on back navigation
      navigate('/', { replace: true });
    }
  }, [location.state, navigate]);

  const performSearch = async (query) => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.searchWhiskeys(query);
      setResults(response.results);
    } catch (err) {
      setError('Failed to search whiskeys. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    performSearch(searchQuery);
  };

  const handleSelectWhiskey = (whiskey) => {
    navigate(`/quiz/${whiskey.whiskey_id}/${whiskey.slug}`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-unspoken-navy mb-4">
          Train Your Palate
        </h1>
        <p className="text-lg text-gray-600">
          Test your sensory skills with professional whiskey reviews
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for a whiskey..."
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded focus:border-unspoken-navy focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {results.map((whiskey) => (
            <div
              key={whiskey.whiskey_id}
              onClick={() => handleSelectWhiskey(whiskey)}
              className="card cursor-pointer"
            >
              <h3 className="text-xl font-semibold text-unspoken-navy mb-2">
                {whiskey.name}
              </h3>
              {whiskey.distillery && (
                <p className="text-gray-600">{whiskey.distillery}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && results.length === 0 && searchQuery && (
        <div className="text-center text-gray-500 py-8">
          No whiskeys found. Try a different search term.
        </div>
      )}
    </div>
  );
}

export default HomePage;

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
    <div className="space-y-6 pt-6">
      <div className="text-center mb-8">
        <h1 className="mb-4">Train Your Palate</h1>
        <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
          Test your sensory skills with professional whiskey reviews
        </p>
      </div>

      {/* Featured Whiskey */}
      <div className="mb-8">
        <h3 className="mb-4">Featured Whiskey</h3>
        <div
          className="card cursor-pointer"
          onClick={() => navigate('/quiz/67/eagle-rare-10-year')}
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="mb-1">Eagle Rare 10 Year</h3>
              <p className="text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>
                Buffalo Trace • 90 proof
              </p>
            </div>
            <span className="bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs font-semibold">
              Featured
            </span>
          </div>
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            Test your ability to identify flavor notes from this premium bourbon's professional review.
          </p>
          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span>Daily Challenge • 3 sections</span>
          </div>
        </div>
      </div>

      {/* Search for a Whiskey */}
      <div className="mb-8">
        <h3 className="mb-4">Search for a Whiskey</h3>
        <div className="card">
          <form onSubmit={handleSearch} className="mb-0">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search whiskey brands..."
            className="flex-1 px-4 py-3 border-2 border-neutral-light rounded-lg focus:border-primary focus:outline-none bg-background-alt"
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
        <div className="mt-4 bg-error text-error-foreground px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="mt-4 space-y-3 max-h-96 overflow-y-auto">
          {results.map((whiskey) => (
            <div
              key={whiskey.whiskey_id}
              onClick={() => handleSelectWhiskey(whiskey)}
              className="p-4 rounded-lg border-2 border-neutral-light cursor-pointer transition-all duration-200 hover:border-primary hover:shadow-md"
              style={{ backgroundColor: 'var(--card)' }}
            >
              <h4 className="mb-1">{whiskey.name}</h4>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {whiskey.distillery}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && results.length === 0 && searchQuery && (
        <div className="mt-4 text-center py-4" style={{ color: 'var(--text-secondary)' }}>
          No whiskeys found matching "{searchQuery}"
        </div>
      )}
        </div>
      </div>
    </div>
  );
}

export default HomePage;

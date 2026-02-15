import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Track the current AbortController
  const abortControllerRef = useRef(null);
  // Track last processed navigation query to prevent duplicate searches
  const lastNavigationQueryRef = useRef(null);

  // Memoized search function with race condition prevention
  const performSearch = useCallback(async (query) => {
    if (!query.trim()) return;

    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const response = await api.searchWhiskeys(query, abortControllerRef.current.signal);
      setResults(response.results);
    } catch (err) {
      // Don't set error if request was aborted (expected behavior)
      if (err.name !== 'AbortError') {
        setError('Failed to search whiskeys. Please try again.');
        if (import.meta.env.DEV) {
          console.error('Search error:', err);
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Handle pre-filled search from distilleries page
  useEffect(() => {
    const incomingQuery = location.state?.searchQuery;

    // Only process if we have a query and haven't processed it yet
    if (incomingQuery && incomingQuery !== lastNavigationQueryRef.current) {
      lastNavigationQueryRef.current = incomingQuery;
      setSearchQuery(incomingQuery);
      performSearch(incomingQuery);

      // Clear the navigation state to prevent issues with browser back button
      navigate('/', { replace: true, state: {} });
    }
  }, [location.state?.searchQuery, navigate, performSearch]);

  // Cleanup: abort any pending requests when component unmounts
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

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
          onClick={() => navigate('/quiz/1/eagle-rare-10-year')}
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
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Test your ability to identify flavor notes from this premium bourbon's professional review.
          </p>
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

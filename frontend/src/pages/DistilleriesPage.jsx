import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

function DistilleriesPage() {
  const [distilleries, setDistilleries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadDistilleries = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.getDistilleries();
        setDistilleries(response.distilleries);
        setLoading(false);
      } catch (err) {
        setError('Failed to load distilleries. Please try again.');
        setLoading(false);
        console.error('Distilleries load error:', err);
      }
    };

    loadDistilleries();
  }, []);

  const handleDistilleryClick = (distilleryName) => {
    // Navigate to home page with search functionality
    // Store the search query so HomePage can use it
    navigate('/', { state: { searchQuery: distilleryName } });
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <p className="text-xl">Loading distilleries...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error text-error-foreground px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6 pt-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="mb-2">Distilleries</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Browse {distilleries.length} distilleries in our database
        </p>
      </div>

      {/* Distilleries List */}
      <div className="space-y-3">
        {distilleries.map((distillery, index) => (
          <div
            key={index}
            onClick={() => handleDistilleryClick(distillery.name)}
            className="card cursor-pointer"
          >
            <div className="flex justify-between items-center">
              <span className="font-medium" style={{ color: 'var(--secondary)' }}>
                {distillery.name}
              </span>
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {distillery.whiskey_count} {distillery.whiskey_count === 1 ? 'whiskey' : 'whiskeys'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DistilleriesPage;

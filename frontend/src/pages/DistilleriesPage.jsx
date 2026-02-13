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
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-xl">Loading distilleries...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-unspoken-navy mb-2">
          Distilleries
        </h1>
        <p className="text-gray-600">
          Browse {distilleries.length} distilleries in our database
        </p>
      </div>

      {/* Distilleries List */}
      <div className="bg-white rounded-lg shadow-md">
        {distilleries.map((distillery, index) => (
          <div
            key={index}
            onClick={() => handleDistilleryClick(distillery.name)}
            className="px-6 py-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors flex justify-between items-center last:border-b-0"
          >
            <span className="text-unspoken-navy font-medium">
              {distillery.name}
            </span>
            <span className="text-gray-500 text-sm">
              {distillery.whiskey_count} {distillery.whiskey_count === 1 ? 'whiskey' : 'whiskeys'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DistilleriesPage;

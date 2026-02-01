import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

function QuizPage() {
  const { whiskeyId } = useParams();
  const navigate = useNavigate();
  
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [currentSection, setCurrentSection] = useState('nose');
  const [selections, setSelections] = useState({
    nose: [],
    palate: [],
    finish: []
  });

  useEffect(() => {
    loadQuiz();
  }, [whiskeyId]);

  const loadQuiz = async () => {
    try {
      const response = await api.getQuiz(whiskeyId);
      setQuizData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load quiz. Please try again.');
      setLoading(false);
      console.error('Quiz load error:', err);
    }
  };

  const toggleDescriptor = (descriptorId) => {
    setSelections(prev => ({
      ...prev,
      [currentSection]: prev[currentSection].includes(descriptorId)
        ? prev[currentSection].filter(id => id !== descriptorId)
        : [...prev[currentSection], descriptorId]
    }));
  };

  const handleSubmitSection = () => {
    // Move to next section or results
    if (currentSection === 'nose') {
      setCurrentSection('palate');
    } else if (currentSection === 'palate') {
      setCurrentSection('finish');
    } else {
      // Navigate to results with selections
      navigate('/results', { 
        state: { 
          quizData, 
          selections 
        } 
      });
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-xl">Loading quiz...</p>
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

  const sectionData = quizData.quiz[currentSection];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Whiskey Info */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-unspoken-navy mb-2">
          {quizData.whiskey.name}
        </h1>
        {quizData.whiskey.distillery && (
          <p className="text-gray-600">{quizData.whiskey.distillery}</p>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="flex justify-center gap-4 mb-8">
        <span className={currentSection === 'nose' ? 'font-bold text-unspoken-navy' : 'text-gray-400'}>
          Nose
        </span>
        <span className={currentSection === 'palate' ? 'font-bold text-unspoken-navy' : 'text-gray-400'}>
          Palate
        </span>
        <span className={currentSection === 'finish' ? 'font-bold text-unspoken-navy' : 'text-gray-400'}>
          Finish
        </span>
      </div>

      {/* Section Title */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-semibold text-unspoken-navy mb-2">
          {currentSection.charAt(0).toUpperCase() + currentSection.slice(1)}
        </h2>
        <p className="text-gray-600">
          Select all descriptors you detect ({sectionData.correct_count} correct options)
        </p>
      </div>

      {/* Descriptor Options Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
        {sectionData.options.map((option) => (
          <button
            key={option.id}
            onClick={() => toggleDescriptor(option.id)}
            className={
              selections[currentSection].includes(option.id)
                ? 'descriptor-option descriptor-option-selected'
                : 'descriptor-option'
            }
          >
            {option.name}
          </button>
        ))}
      </div>

      {/* Submit Button */}
      <div className="text-center">
        <button
          onClick={handleSubmitSection}
          disabled={selections[currentSection].length === 0}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {currentSection === 'finish' ? 'See Results' : 'Continue'}
        </button>
      </div>
    </div>
  );
}

export default QuizPage;

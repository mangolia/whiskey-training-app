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
    const loadQuiz = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.getQuiz(whiskeyId);
        setQuizData(response);
        setLoading(false);
      } catch (err) {
        setError('Failed to load quiz. Please try again.');
        setLoading(false);
        console.error('Quiz load error:', err);
      }
    };

    loadQuiz();
  }, [whiskeyId]);

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
      <div className="text-center py-8">
        <p className="text-xl">Loading quiz...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  // Safety check: ensure quizData is properly loaded
  if (!quizData || !quizData.quiz) {
    return null;
  }

  const sectionData = quizData.quiz[currentSection];

  return (
    <div className="space-y-6 pt-4">
      {/* Whiskey Info */}
      <div className="text-center mb-8">
        <h2 className="mb-2">{quizData.whiskey.name}</h2>
        {quizData.whiskey.distillery && (
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {quizData.whiskey.distillery}
          </p>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="grid grid-cols-3 gap-3 mb-8 px-1">
        <button
          onClick={() => setCurrentSection('nose')}
          className={currentSection === 'nose' ? 'tab-button tab-button-active' : 'tab-button tab-button-inactive'}
        >
          Nose
        </button>
        <button
          onClick={() => setCurrentSection('palate')}
          className={currentSection === 'palate' ? 'tab-button tab-button-active' : 'tab-button tab-button-inactive'}
        >
          Palate
        </button>
        <button
          onClick={() => setCurrentSection('finish')}
          className={currentSection === 'finish' ? 'tab-button tab-button-active' : 'tab-button tab-button-inactive'}
        >
          Finish
        </button>
      </div>

      {/* Section Instructions */}
      <div className="text-center mb-6">
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Select all flavor notes you detect ({sectionData.correct_count} correct)
        </p>
      </div>

      {/* Descriptor Options Grid */}
      <div className="grid grid-cols-3 gap-3 mb-8">
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
          className="btn-primary w-full max-w-xs"
        >
          {currentSection === 'finish' ? 'See Results' : `Continue to ${currentSection === 'nose' ? 'Palate' : 'Finish'}`}
        </button>
      </div>
    </div>
  );
}

export default QuizPage;

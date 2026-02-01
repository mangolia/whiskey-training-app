import { useLocation, useNavigate } from 'react-router-dom';

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { quizData, selections } = location.state || {};

  if (!quizData || !selections) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-xl mb-4">No quiz data found</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Calculate results for each section
  const calculateSectionResults = (section) => {
    const sectionData = quizData.quiz[section];
    const userSelections = selections[section];
    
    const correct = sectionData.options.filter(opt => 
      opt.correct && userSelections.includes(opt.id)
    );
    
    const incorrect = sectionData.options.filter(opt => 
      !opt.correct && userSelections.includes(opt.id)
    );
    
    const missed = sectionData.options.filter(opt => 
      opt.correct && !userSelections.includes(opt.id)
    );

    const accuracy = (correct.length / sectionData.correct_count) * 100;

    return {
      correct,
      incorrect,
      missed,
      accuracy: Math.round(accuracy)
    };
  };

  const noseResults = calculateSectionResults('nose');
  const palateResults = calculateSectionResults('palate');
  const finishResults = calculateSectionResults('finish');

  const overallAccuracy = Math.round(
    (noseResults.accuracy + palateResults.accuracy + finishResults.accuracy) / 3
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-unspoken-navy mb-2">
          Results
        </h1>
        <h2 className="text-2xl text-gray-700 mb-4">
          {quizData.whiskey.name}
        </h2>
        <div className="text-6xl font-bold text-unspoken-navy mb-2">
          {overallAccuracy}%
        </div>
        <p className="text-gray-600">Overall Accuracy</p>
      </div>

      {/* Section Results */}
      {['nose', 'palate', 'finish'].map((section) => {
        const results = section === 'nose' ? noseResults : section === 'palate' ? palateResults : finishResults;
        
        return (
          <div key={section} className="card mb-6">
            <h3 className="text-2xl font-semibold text-unspoken-navy mb-4 capitalize">
              {section} - {results.accuracy}%
            </h3>

            {/* Correct */}
            {results.correct.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-green-700 mb-2">
                  ✓ Correct ({results.correct.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {results.correct.map(opt => (
                    <span key={opt.id} className="bg-green-100 text-green-800 px-3 py-1 rounded">
                      {opt.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missed */}
            {results.missed.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-yellow-700 mb-2">
                  ○ Missed ({results.missed.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {results.missed.map(opt => (
                    <span key={opt.id} className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded">
                      {opt.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Incorrect */}
            {results.incorrect.length > 0 && (
              <div>
                <h4 className="font-semibold text-red-700 mb-2">
                  ✗ Incorrect ({results.incorrect.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {results.incorrect.map(opt => (
                    <span key={opt.id} className="bg-red-100 text-red-800 px-3 py-1 rounded">
                      {opt.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Source Reviews */}
      {quizData.source_reviews && quizData.source_reviews.length > 0 && (
        <div className="card mt-6 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Source Reviews
          </h3>
          <div className="space-y-2">
            {quizData.source_reviews.map((review, index) => (
              <div key={index}>
                <a
                  href={review.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-unspoken-navy hover:text-unspoken-navy-dark underline"
                >
                  {review.site} →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="text-center mt-8">
        <button onClick={() => navigate('/')} className="btn-primary">
          Try Another Whiskey
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;

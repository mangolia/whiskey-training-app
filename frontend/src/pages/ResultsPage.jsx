import { useLocation, useNavigate } from 'react-router-dom';

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { quizData, selections } = location.state || {};

  if (!quizData || !quizData.quiz || !quizData.whiskey || !selections) {
    return (
      <div className="text-center py-8">
        <p className="text-xl mb-4">No quiz data found</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go Home
        </button>
      </div>
    );
  }

  // Calculate results for each section
  const calculateSectionResults = (section) => {
    const sectionData = quizData.quiz[section];
    const userSelections = selections[section];

    // Build descriptor analysis for all options
    const descriptors = sectionData.options.map(opt => ({
      label: opt.name,
      isCorrect: opt.correct,
      wasSelected: userSelections.includes(opt.id)
    }));

    const correct = sectionData.options.filter(opt =>
      opt.correct && userSelections.includes(opt.id)
    ).length;

    const total = sectionData.correct_count;

    return {
      sense: section.charAt(0).toUpperCase() + section.slice(1),
      correct,
      total,
      descriptors
    };
  };

  const results = [
    calculateSectionResults('nose'),
    calculateSectionResults('palate'),
    calculateSectionResults('finish')
  ];

  // Calculate overall percentage
  const totalCorrect = results.reduce((sum, r) => sum + r.correct, 0);
  const totalQuestions = results.reduce((sum, r) => sum + r.total, 0);
  const percentage = Math.round((totalCorrect / totalQuestions) * 100);

  return (
    <div className="space-y-6 pt-6 pb-8">
      {/* Decorative flourish and celebration header */}
      <div className="text-center" style={{ marginTop: '24px' }}>
        <div className="flex items-center justify-center gap-4 mb-4">
          <div style={{
            width: '40px',
            height: '1px',
            background: 'linear-gradient(90deg, transparent, var(--accent))',
          }} />
          <h2 style={{
            color: 'var(--accent)',
            fontFamily: 'var(--font-heading)',
            marginBottom: 0,
            fontSize: '28px',
            fontWeight: 500,
          }}>
            You Tasted...
          </h2>
          <div style={{
            width: '40px',
            height: '1px',
            background: 'linear-gradient(90deg, var(--accent), transparent)',
          }} />
        </div>
      </div>

      {/* Whiskey Reveal Card */}
      <div
        className="rounded-lg p-6 text-center"
        style={{
          background: 'linear-gradient(135deg, #1a2456 0%, #2a3c93 100%)',
          border: '2px solid var(--accent)',
          boxShadow: '0 8px 32px rgba(42, 60, 147, 0.3), inset 0 1px 0 rgba(212, 175, 55, 0.2)',
        }}
      >
        <h1
          className="mb-2"
          style={{
            color: 'var(--accent)',
            fontFamily: 'var(--font-heading)',
            fontSize: '32px',
            fontWeight: 600,
            textShadow: '0 2px 8px rgba(0,0,0,0.3)',
          }}
        >
          {quizData.whiskey.name}
        </h1>

        <h3
          style={{
            color: 'rgba(255, 255, 255, 0.9)',
            marginBottom: '16px',
            fontFamily: 'var(--font-heading)',
            fontWeight: 400,
          }}
        >
          {quizData.whiskey.distillery}
        </h3>

        {/* Specs */}
        <div className="flex gap-3 justify-center flex-wrap">
          {quizData.whiskey.proof && (
            <div
              className="px-4 py-2 rounded-full text-sm font-medium"
              style={{
                background: 'rgba(212, 175, 55, 0.15)',
                border: '1px solid var(--accent)',
                color: 'var(--accent)',
              }}
            >
              {quizData.whiskey.proof} proof
            </div>
          )}
          {quizData.whiskey.age && (
            <div
              className="px-4 py-2 rounded-full text-sm font-medium"
              style={{
                background: 'rgba(212, 175, 55, 0.15)',
                border: '1px solid var(--accent)',
                color: 'var(--accent)',
              }}
            >
              {quizData.whiskey.age}
            </div>
          )}
        </div>
      </div>

      {/* Score Breakdown Section */}
      <div>
        <h3
          className="mb-5 text-center"
          style={{
            fontFamily: 'var(--font-heading)',
            color: 'var(--secondary)',
            fontSize: '24px',
            fontWeight: 500,
          }}
        >
          Your Results
        </h3>

        <div className="space-y-5">
          {results.map((result) => {
            const sensePercentage = (result.correct / result.total) * 100;
            return (
              <div key={result.sense} className="space-y-3">
                {/* Sense Header with Progress */}
                <div
                  className="rounded-lg p-4"
                  style={{
                    background: 'var(--card)',
                    border: '2px solid var(--accent)',
                    boxShadow: '0 4px 12px rgba(212, 175, 55, 0.15)',
                  }}
                >
                  <div className="flex items-center justify-between gap-4 mb-3">
                    <h4
                      style={{
                        fontFamily: 'var(--font-heading)',
                        fontSize: '20px',
                        fontWeight: 500,
                        color: 'var(--secondary)',
                        minWidth: '80px',
                      }}
                    >
                      {result.sense}
                    </h4>

                    {/* Progress Bar */}
                    <div className="flex-1">
                      <div
                        className="h-3 rounded-full overflow-hidden"
                        style={{
                          background: 'var(--background-alt)',
                          border: '1px solid var(--accent)',
                        }}
                      >
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${sensePercentage}%`,
                            background: sensePercentage >= 60
                              ? 'linear-gradient(90deg, #d4af37 0%, #f4d03f 100%)'
                              : 'linear-gradient(90deg, #8b3a3a 0%, #a04a4a 100%)',
                          }}
                        />
                      </div>
                    </div>

                    <div
                      className="text-sm font-semibold"
                      style={{
                        minWidth: '80px',
                        textAlign: 'right',
                        color: 'var(--secondary)',
                      }}
                    >
                      {result.correct}/{result.total} correct
                    </div>
                  </div>

                  {/* Descriptors Grid - 3x3 showing all 9 */}
                  <div className="grid grid-cols-3 gap-2">
                    {result.descriptors.map((descriptor, idx) => {
                      const isCorrectAndSelected = descriptor.isCorrect && descriptor.wasSelected;
                      const isCorrectButNotSelected = descriptor.isCorrect && !descriptor.wasSelected;
                      const isIncorrectButSelected = !descriptor.isCorrect && descriptor.wasSelected;
                      const isNeitherCorrectNorSelected = !descriptor.isCorrect && !descriptor.wasSelected;

                      let bgColor = 'var(--background-alt)';
                      let textColor = 'var(--text-secondary)';
                      let borderColor = 'var(--neutral-light)';
                      let icon = '';

                      if (isCorrectAndSelected) {
                        // User got it right - Navy with gold check
                        bgColor = 'var(--primary)';
                        textColor = 'var(--accent)';
                        borderColor = 'var(--accent)';
                        icon = '✓';
                      } else if (isCorrectButNotSelected) {
                        // Correct answer but user missed it - Cream with gold outline
                        bgColor = 'var(--card)';
                        textColor = 'var(--accent)';
                        borderColor = 'var(--accent)';
                        icon = '○';
                      } else if (isIncorrectButSelected) {
                        // User selected wrong answer - Red indicator
                        bgColor = 'var(--card)';
                        textColor = 'var(--error)';
                        borderColor = 'var(--error)';
                        icon = '✗';
                      }

                      return (
                        <div
                          key={idx}
                          className="px-3 py-2.5 rounded-lg text-sm font-medium text-center transition-all"
                          style={{
                            backgroundColor: bgColor,
                            color: textColor,
                            border: `2px solid ${borderColor}`,
                            opacity: isNeitherCorrectNorSelected ? 0.35 : 1,
                            fontFamily: isCorrectAndSelected ? 'var(--font-heading)' : 'var(--font-body)',
                            boxShadow: isCorrectAndSelected
                              ? '0 2px 8px rgba(212, 175, 55, 0.3)'
                              : 'none',
                          }}
                        >
                          {icon && (
                            <span
                              className="mr-1 font-bold"
                              style={{ fontSize: '14px' }}
                            >
                              {icon}
                            </span>
                          )}
                          {descriptor.label}
                        </div>
                      );
                    })}
                  </div>

                  {/* Legend */}
                  <div
                    className="flex gap-4 justify-center mt-4 pt-3 text-xs"
                    style={{
                      borderTop: '1px solid var(--neutral-light)',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <div className="flex items-center gap-1.5">
                      <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>✓</span>
                      <span>Correct</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span style={{ color: 'var(--error)', fontWeight: 'bold' }}>✗</span>
                      <span>Incorrect</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>○</span>
                      <span>Missed</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Total Score */}
      <div
        className="text-center rounded-lg p-6"
        style={{
          margin: '32px 0',
          background: 'var(--card)',
          border: '2px solid var(--accent)',
          boxShadow: '0 4px 16px rgba(212, 175, 55, 0.2)',
        }}
      >
        <div className="mb-2">
          <h1
            style={{
              color: 'var(--accent)',
              fontSize: '48px',
              marginBottom: '8px',
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              textShadow: '0 2px 12px rgba(212, 175, 55, 0.3)',
            }}
          >
            {percentage}%
          </h1>
        </div>
        <p
          className="text-lg font-medium"
          style={{
            color: 'var(--secondary)',
            fontFamily: 'var(--font-heading)',
            marginBottom: '8px',
          }}
        >
          Overall Score
        </p>
        <p
          className="text-sm"
          style={{ color: 'var(--text-secondary)' }}
        >
          {totalCorrect} out of {totalQuestions} notes identified
        </p>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3 pb-4">
        <button
          onClick={() => navigate('/')}
          className="w-full rounded-lg transition-all duration-300"
          style={{
            background: 'linear-gradient(135deg, #2a3c93 0%, #1e2d6e 100%)',
            color: 'var(--accent)',
            padding: '16px 24px',
            fontSize: '16px',
            fontWeight: 600,
            border: '2px solid var(--accent)',
            fontFamily: 'var(--font-heading)',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(42, 60, 147, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          Take Another Quiz
        </button>

        <div className="text-center pt-2">
          <button
            onClick={() => navigate('/')}
            className="text-sm underline hover:opacity-70 transition-opacity"
            style={{
              color: 'var(--text-secondary)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;

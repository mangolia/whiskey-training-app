import React, { useState } from 'react';
import { Header } from './components/Header';
import { HamburgerMenu } from './components/HamburgerMenu';
import { BackButton } from './components/BackButton';
import { ComponentShowcase } from './components/ComponentShowcase';
import { QuizCard } from './components/QuizCard';
import { ResultCard } from './components/ResultCard';
import { QuizResultsScreen } from './components/QuizResultsScreen';
import { Card } from './components/Card';
import { Button } from './components/Button';
import { SearchBar } from './components/SearchBar';
import { Badge } from './components/Badge';
import { StarIcon } from './components/Icons';
import { DevSpecsScreen } from './components/DevSpecsScreen';

type Screen = 'home' | 'components' | 'quiz' | 'quiz-results' | 'results' | 'library' | 'dev-specs';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  const [menuOpen, setMenuOpen] = useState(false);

  const menuItems = [
    { label: 'Home', onClick: () => setCurrentScreen('home'), active: currentScreen === 'home' },
    { label: 'Component Library', onClick: () => setCurrentScreen('components'), active: currentScreen === 'components' },
    { label: 'Quiz Example', onClick: () => setCurrentScreen('quiz'), active: currentScreen === 'quiz' },
    { label: 'Quiz Results Example', onClick: () => setCurrentScreen('quiz-results'), active: currentScreen === 'quiz-results' },
    { label: 'Results Example', onClick: () => setCurrentScreen('results'), active: currentScreen === 'results' },
    { label: 'Whiskey Library', onClick: () => setCurrentScreen('library'), active: currentScreen === 'library' },
    { label: 'Dev Specs', onClick: () => setCurrentScreen('dev-specs'), active: currentScreen === 'dev-specs' },
  ];

  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return <HomeScreen onNavigate={setCurrentScreen} />;
      case 'components':
        return <ComponentShowcase />;
      case 'quiz':
        return <QuizScreen onComplete={(screen) => setCurrentScreen(screen)} />;
      case 'quiz-results':
        return (
          <QuizResultsScreen
            whiskeyName="Buffalo Trace Kentucky Straight Bourbon"
            distillery="Buffalo Trace Distillery"
            proof="90 Proof"
            age="No Age Statement"
            results={[
              { 
                sense: 'Nose', 
                correct: 2, 
                total: 3,
                descriptors: [
                  { label: 'Vanilla', isCorrect: true, wasSelected: true },
                  { label: 'Toasted Oak', isCorrect: true, wasSelected: false },
                  { label: 'Brown Sugar', isCorrect: false, wasSelected: false },
                  { label: 'Honey', isCorrect: false, wasSelected: true },
                  { label: 'Caramel', isCorrect: true, wasSelected: true },
                  { label: 'Cinnamon', isCorrect: false, wasSelected: false },
                  { label: 'Dark Cherry', isCorrect: false, wasSelected: false },
                  { label: 'Leather', isCorrect: false, wasSelected: false },
                  { label: 'Tobacco', isCorrect: false, wasSelected: false },
                ]
              },
              { 
                sense: 'Palate', 
                correct: 3, 
                total: 4,
                descriptors: [
                  { label: 'Butterscotch', isCorrect: true, wasSelected: true },
                  { label: 'Maple Syrup', isCorrect: true, wasSelected: true },
                  { label: 'Toffee', isCorrect: false, wasSelected: false },
                  { label: 'Nutmeg', isCorrect: true, wasSelected: false },
                  { label: 'Black Pepper', isCorrect: true, wasSelected: true },
                  { label: 'Dried Fruit', isCorrect: false, wasSelected: false },
                  { label: 'Chocolate', isCorrect: false, wasSelected: true },
                  { label: 'Spice', isCorrect: false, wasSelected: false },
                  { label: 'Charred Oak', isCorrect: false, wasSelected: false },
                ]
              },
              { 
                sense: 'Finish', 
                correct: 1, 
                total: 3,
                descriptors: [
                  { label: 'Smoky', isCorrect: false, wasSelected: false },
                  { label: 'Warm', isCorrect: true, wasSelected: true },
                  { label: 'Lingering', isCorrect: true, wasSelected: false },
                  { label: 'Sweet', isCorrect: false, wasSelected: true },
                  { label: 'Peppery', isCorrect: true, wasSelected: false },
                  { label: 'Dry', isCorrect: false, wasSelected: false },
                  { label: 'Smooth', isCorrect: false, wasSelected: true },
                  { label: 'Bold', isCorrect: false, wasSelected: false },
                  { label: 'Complex', isCorrect: false, wasSelected: false },
                ]
              },
            ]}
            onViewReview={() => alert('View Full Review')}
            onTakeAnother={() => setCurrentScreen('quiz')}
            onBackHome={() => setCurrentScreen('home')}
          />
        );
      case 'results':
        return <ResultsScreen />;
      case 'library':
        return <LibraryScreen />;
      case 'dev-specs':
        return <DevSpecsScreen />;
      default:
        return <HomeScreen onNavigate={setCurrentScreen} />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Container - max width for mobile optimization */}
      <div className="max-w-[480px] mx-auto min-h-screen bg-background shadow-lg">
        {/* Header */}
        <Header
          left={currentScreen === 'quiz' ? (
            <button 
              onClick={() => setCurrentScreen('home')}
              className="hover:opacity-80 transition-opacity"
              aria-label="Back to home"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0',
                color: 'var(--accent)',
                fontSize: '14px',
                fontWeight: 600,
                fontFamily: 'var(--font-heading)',
              }}
            >
              HOME
            </button>
          ) : currentScreen !== 'home' ? (
            <BackButton onClick={() => setCurrentScreen('home')} />
          ) : (
            <div />
          )}
          center={<h2 className="text-center">Whiskey Tasting Quiz</h2>}
          right={<HamburgerMenu items={menuItems} logo={<h3 className="text-white">Whiskey Quiz</h3>} />}
        />

        {/* Main Content */}
        <main className="px-5 pb-8">
          {renderScreen()}
        </main>
      </div>
    </div>
  );
}

function HomeScreen({ onNavigate }: { onNavigate: (screen: Screen) => void }) {
  const [searchValue, setSearchValue] = useState('');

  const whiskeyList = [
    { name: 'Buffalo Trace', type: 'Bourbon', distillery: 'Buffalo Trace Distillery', proof: '90 proof' },
    { name: 'Eagle Rare 10 Year', type: 'Bourbon', distillery: 'Buffalo Trace', proof: '90 proof' },
    { name: 'Maker\'s Mark', type: 'Bourbon', distillery: 'Maker\'s Mark Distillery', proof: '90 proof' },
    { name: 'Woodford Reserve', type: 'Bourbon', distillery: 'Woodford Reserve Distillery', proof: '90.4 proof' },
    { name: 'Laphroaig 10', type: 'Scotch', distillery: 'Laphroaig Distillery', proof: '86 proof' },
    { name: 'Bulleit Rye', type: 'Rye', distillery: 'Bulleit Distillery', proof: '90 proof' },
  ];

  const filteredList = searchValue
    ? whiskeyList.filter((whiskey) =>
        whiskey.name.toLowerCase().includes(searchValue.toLowerCase())
      )
    : [];

  return (
    <div className="space-y-6">
      {/* Highlighted Whiskey */}
      <div className="pt-6">
        <h3 className="mb-4" style={{ 
          fontFamily: 'var(--font-heading)',
          color: 'var(--neutral-dark)'
        }}>
          Highlighted Whiskey
        </h3>
        <Card padding="lg" onClick={() => onNavigate('quiz')}>
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="mb-1">Eagle Rare 10 Year</h3>
              <p className="text-sm text-text-secondary mb-1">Buffalo Trace • 90 proof</p>
            </div>
            <Badge variant="primary">Featured</Badge>
          </div>
          <p className="text-sm mb-4">
            Test your ability to identify flavor notes from this premium bourbon's professional review.
          </p>
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <StarIcon size={16} color="var(--accent)" filled />
            <span>Daily Challenge • 3 sections</span>
          </div>
        </Card>
      </div>

      {/* Distillery Library */}
      <div>
        <h3 className="mb-4" style={{ 
          fontFamily: 'var(--font-heading)',
          color: 'var(--neutral-dark)'
        }}>
          Distillery Library
        </h3>
        <Card padding="lg" onClick={() => onNavigate('library')}>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h4 className="mb-1">Browse All Whiskeys</h4>
              <p className="text-sm text-text-secondary">Explore 500+ professional reviews</p>
            </div>
          </div>
          <p className="text-sm text-text-secondary">
            Access our complete collection of bourbon, scotch, rye, and more.
          </p>
        </Card>
      </div>

      {/* Search for a Whiskey */}
      <div>
        <h3 className="mb-4" style={{ 
          fontFamily: 'var(--font-heading)',
          color: 'var(--neutral-dark)'
        }}>
          Search for a Whiskey
        </h3>
        <Card padding="lg">
          <SearchBar
            placeholder="Search whiskey brands..."
            value={searchValue}
            onChange={setSearchValue}
          />
          
          {searchValue && (
            <div className="mt-4 space-y-3 max-h-[300px] overflow-y-auto">
              {filteredList.length > 0 ? (
                filteredList.map((whiskey, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md"
                    style={{
                      borderColor: 'var(--neutral-light)',
                      backgroundColor: 'var(--background)',
                    }}
                    onClick={() => {
                      // Navigate to quiz with selected whiskey
                      onNavigate('quiz');
                    }}
                  >
                    <h4 className="text-sm mb-1">{whiskey.name}</h4>
                    <p className="text-xs text-text-secondary">
                      {whiskey.distillery} • {whiskey.proof}
                    </p>
                    <p className="text-xs text-text-secondary mt-1">
                      {whiskey.type}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-center text-sm text-text-secondary py-4">
                  No whiskeys found matching "{searchValue}"
                </p>
              )}
            </div>
          )}
        </Card>
      </div>

      <div className="pt-2">
        <Button variant="primary" onClick={() => onNavigate('components')}>
          View Component Library
        </Button>
      </div>
    </div>
  );
}

function QuizScreen({ onComplete }: { onComplete: (screen: Screen) => void }) {
  const [submitted, setSubmitted] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<'nose' | 'palate' | 'finish'>('nose');
  
  // Store selections for each category separately
  const [noseSelections, setNoseSelections] = useState<string[]>([]);
  const [palateSelections, setPalateSelections] = useState<string[]>([]);
  const [finishSelections, setFinishSelections] = useState<string[]>([]);

  const noseOptions = [
    { id: '1', label: 'Vanilla' },
    { id: '2', label: 'Toasted Oak' },
    { id: '3', label: 'Brown Sugar' },
    { id: '4', label: 'Honey' },
    { id: '5', label: 'Caramel' },
    { id: '6', label: 'Cinnamon' },
    { id: '7', label: 'Dark Cherry' },
    { id: '8', label: 'Leather' },
    { id: '9', label: 'Tobacco' },
  ];

  const palateOptions = [
    { id: '1', label: 'Butterscotch' },
    { id: '2', label: 'Maple Syrup' },
    { id: '3', label: 'Toffee' },
    { id: '4', label: 'Nutmeg' },
    { id: '5', label: 'Black Pepper' },
    { id: '6', label: 'Dried Fruit' },
    { id: '7', label: 'Chocolate' },
    { id: '8', label: 'Spice' },
    { id: '9', label: 'Charred Oak' },
  ];

  const finishOptions = [
    { id: '1', label: 'Smoky' },
    { id: '2', label: 'Warm' },
    { id: '3', label: 'Lingering' },
    { id: '4', label: 'Sweet' },
    { id: '5', label: 'Peppery' },
    { id: '6', label: 'Dry' },
    { id: '7', label: 'Smooth' },
    { id: '8', label: 'Bold' },
    { id: '9', label: 'Complex' },
  ];

  const getOptionsForCategory = () => {
    switch (selectedCategory) {
      case 'nose':
        return noseOptions;
      case 'palate':
        return palateOptions;
      case 'finish':
        return finishOptions;
    }
  };

  const getCurrentSelections = () => {
    switch (selectedCategory) {
      case 'nose':
        return noseSelections;
      case 'palate':
        return palateSelections;
      case 'finish':
        return finishSelections;
    }
  };

  const handleSubmit = (selectedIds: string[]) => {
    console.log('Selected:', selectedIds);
    // Update the appropriate category's selections
    switch (selectedCategory) {
      case 'nose':
        setNoseSelections(selectedIds);
        break;
      case 'palate':
        setPalateSelections(selectedIds);
        break;
      case 'finish':
        setFinishSelections(selectedIds);
        break;
    }
    setSubmitted(true);
  };

  const handleCategoryChange = (category: 'nose' | 'palate' | 'finish') => {
    setSelectedCategory(category);
    setSubmitted(false); // Reset submitted state when changing category
  };

  const handleNext = () => {
    setSubmitted(false);
    if (selectedCategory === 'nose') {
      setSelectedCategory('palate');
    } else if (selectedCategory === 'palate') {
      setSelectedCategory('finish');
    } else if (selectedCategory === 'finish') {
      // Quiz complete - navigate to results
      onComplete('quiz-results');
    }
  };

  const handlePrevious = () => {
    setSubmitted(false);
    if (selectedCategory === 'finish') {
      setSelectedCategory('palate');
    } else if (selectedCategory === 'palate') {
      setSelectedCategory('nose');
    }
  };

  const canGoBack = selectedCategory !== 'nose';
  const canGoForward = true; // Always allow forward navigation

  return (
    <div className="space-y-6">
      <div className="text-center pt-4">
        <h2 className="mb-2">Eagle Rare 10 Year</h2>
        <p className="text-sm text-text-secondary">Identify the flavor notes from the professional review</p>
      </div>

      <div className="grid grid-cols-3 gap-3 px-1">
        <button
          onClick={() => handleCategoryChange('nose')}
          className="rounded-lg transition-all duration-200"
          style={{
            minHeight: '56px',
            padding: '12px 16px',
            background: selectedCategory === 'nose' 
              ? 'linear-gradient(135deg, #2a3c93 0%, #1e2d6e 100%)'
              : 'var(--card)',
            border: `2px solid ${selectedCategory === 'nose' ? 'var(--accent)' : 'var(--neutral-light)'}`,
            color: selectedCategory === 'nose' ? 'var(--accent)' : 'var(--neutral-dark)',
            fontFamily: 'var(--font-heading)',
            fontSize: '16px',
            fontWeight: 600,
            boxShadow: selectedCategory === 'nose' 
              ? '0 4px 12px rgba(42, 60, 147, 0.2)'
              : 'none',
            cursor: 'pointer',
          }}
        >
          Nose
        </button>
        <button
          onClick={() => handleCategoryChange('palate')}
          className="rounded-lg transition-all duration-200"
          style={{
            minHeight: '56px',
            padding: '12px 16px',
            background: selectedCategory === 'palate' 
              ? 'linear-gradient(135deg, #2a3c93 0%, #1e2d6e 100%)'
              : 'var(--card)',
            border: `2px solid ${selectedCategory === 'palate' ? 'var(--accent)' : 'var(--neutral-light)'}`,
            color: selectedCategory === 'palate' ? 'var(--accent)' : 'var(--neutral-dark)',
            fontFamily: 'var(--font-heading)',
            fontSize: '16px',
            fontWeight: 600,
            boxShadow: selectedCategory === 'palate' 
              ? '0 4px 12px rgba(42, 60, 147, 0.2)'
              : 'none',
            cursor: 'pointer',
          }}
        >
          Palate
        </button>
        <button
          onClick={() => handleCategoryChange('finish')}
          className="rounded-lg transition-all duration-200"
          style={{
            minHeight: '56px',
            padding: '12px 16px',
            background: selectedCategory === 'finish' 
              ? 'linear-gradient(135deg, #2a3c93 0%, #1e2d6e 100%)'
              : 'var(--card)',
            border: `2px solid ${selectedCategory === 'finish' ? 'var(--accent)' : 'var(--neutral-light)'}`,
            color: selectedCategory === 'finish' ? 'var(--accent)' : 'var(--neutral-dark)',
            fontFamily: 'var(--font-heading)',
            fontSize: '16px',
            fontWeight: 600,
            boxShadow: selectedCategory === 'finish' 
              ? '0 4px 12px rgba(42, 60, 147, 0.2)'
              : 'none',
            cursor: 'pointer',
          }}
        >
          Finish
        </button>
      </div>

      <QuizCard
        whiskey="Eagle Rare 10 Year"
        distillery="Buffalo Trace"
        proof="90 proof"
        options={getOptionsForCategory()}
        onSubmit={handleSubmit}
        sense={selectedCategory}
        currentSelections={getCurrentSelections()}
      />

      {submitted && (
        <Card padding="lg" variant="bordered">
          <p className="text-center text-success font-medium mb-2">Answer Submitted!</p>
          <p className="text-center text-sm text-text-secondary">
            Great job! Let's move on to the next question.
          </p>
        </Card>
      )}

      <div className="flex gap-3 justify-between">
        <Button
          variant="secondary"
          onClick={handlePrevious}
          disabled={!canGoBack}
        >
          ← Previous
        </Button>
        <Button
          variant="primary"
          onClick={handleNext}
          disabled={!canGoForward}
        >
          Next →
        </Button>
      </div>
    </div>
  );
}

function ResultsScreen() {
  return (
    <div className="space-y-6 pt-4">
      <ResultCard
        correct={true}
        score={4}
        totalQuestions={5}
        correctAnswers={['Vanilla', 'Caramel', 'Oak', 'Honey']}
        yourAnswers={['Vanilla', 'Caramel', 'Oak', 'Honey']}
        message="Excellent palate! You identified all the key flavor notes."
      />

      <div className="text-center">
        <h3 className="mb-4">Recent Quizzes</h3>
        
        <div className="space-y-3">
          <Card padding="md" variant="bordered">
            <div className="flex items-center justify-between">
              <div className="text-left">
                <h4 className="text-sm mb-1">Maker's Mark Quiz</h4>
                <p className="text-xs text-text-secondary">2 days ago</p>
              </div>
              <Badge variant="success">5/5</Badge>
            </div>
          </Card>

          <Card padding="md" variant="bordered">
            <div className="flex items-center justify-between">
              <div className="text-left">
                <h4 className="text-sm mb-1">Woodford Reserve Quiz</h4>
                <p className="text-xs text-text-secondary">5 days ago</p>
              </div>
              <Badge variant="primary">4/5</Badge>
            </div>
          </Card>

          <Card padding="md" variant="bordered">
            <div className="flex items-center justify-between">
              <div className="text-left">
                <h4 className="text-sm mb-1">Eagle Rare Quiz</h4>
                <p className="text-xs text-text-secondary">1 week ago</p>
              </div>
              <Badge variant="error">2/5</Badge>
            </div>
          </Card>
        </div>
      </div>

      <Button variant="primary">Take Another Quiz</Button>
    </div>
  );
}

function LibraryScreen() {
  const [searchValue, setSearchValue] = useState('');

  const whiskeyList = [
    { name: 'Buffalo Trace', type: 'Bourbon', rating: 90, verified: true },
    { name: 'Maker\'s Mark', type: 'Bourbon', rating: 88, verified: true },
    { name: 'Woodford Reserve', type: 'Bourbon', rating: 92, verified: true },
    { name: 'Eagle Rare', type: 'Bourbon', rating: 91, verified: false },
    { name: 'Laphroaig 10', type: 'Scotch', rating: 93, verified: true },
    { name: 'Bulleit Rye', type: 'Rye', rating: 87, verified: false },
  ];

  const filteredList = whiskeyList.filter((whiskey) =>
    whiskey.name.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h2 className="mb-4">Whiskey Library</h2>
        <SearchBar
          placeholder="Search whiskey brands..."
          value={searchValue}
          onChange={setSearchValue}
        />
      </div>

      <div className="space-y-3">
        {filteredList.map((whiskey, idx) => (
          <Card key={idx} padding="md" variant="default">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="mb-1">{whiskey.name}</h4>
                <p className="text-xs text-text-secondary">{whiskey.type}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Badge variant="primary">{whiskey.rating} Points</Badge>
              {whiskey.verified && <Badge variant="success">Verified</Badge>}
            </div>
          </Card>
        ))}
      </div>

      {filteredList.length === 0 && (
        <Card padding="lg">
          <p className="text-center text-text-secondary">
            No whiskeys found matching "{searchValue}"
          </p>
        </Card>
      )}
    </div>
  );
}
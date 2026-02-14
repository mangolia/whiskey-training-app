import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import DistilleriesPage from './pages/DistilleriesPage';
import QuizPage from './pages/QuizPage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        {/* Mobile Container - max width for mobile-first optimization */}
        <div className="max-w-[480px] mx-auto min-h-screen bg-background shadow-lg">
          <Header />
          <main className="px-5 pb-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/distilleries" element={<DistilleriesPage />} />
              <Route path="/quiz/:whiskeyId/:slug" element={<QuizPage />} />
              <Route path="/results" element={<ResultsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;

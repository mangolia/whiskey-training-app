# Whiskey Sensory Training App

A modern web application for training your whiskey tasting palate using scientifically-backed sensory analysis methods. Built with Flask, React, and a comprehensive database of 2,109 whiskeys and their tasting profiles.

**Status**: ✅ Production-ready MVP  
**Version**: 1.0.0  
**Last Updated**: January 28, 2026

---

## 🥃 What Is This?

This app helps whiskey enthusiasts develop their tasting skills by quizzing them on sensory descriptors (nose, palate, finish) for specific whiskeys. Users search for a whiskey, take a quiz identifying its tasting notes, and get instant feedback on their accuracy.

**Key Features:**
- 🔍 Search 2,109+ whiskeys by name
- 🧪 Interactive sensory quizzes (Nose → Palate → Finish)
- 📊 Immediate accuracy feedback with results breakdown
- 🔗 Source review links for verification
- 📱 Mobile-responsive design
- 🎨 Clean, professional UI with Unspoken brand design

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
# Clone and navigate
cd whiskey-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend (defaults to port 5001)
python3 app.py
```

Backend runs at: `http://localhost:5001`

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run dev server (defaults to port 3000)
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Quick Test
1. Open `http://localhost:3000`
2. Search for "eagle rare"
3. Click a whiskey to start quiz
4. Select descriptors for Nose → Palate → Finish
5. View your results!

---

## 📊 Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Production database (15MB)
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Tailwind CSS** - Styling framework
- **Axios** - HTTP client

### Data Processing
- **Conservative NLP** - Prose descriptor extraction
- **Rule-based matching** - Pipe-delimited reviews
- **Compound descriptor system** - Multi-word terms prioritized

---

## 📁 Project Structure

```
whiskey-scraper/
├── app.py                          # Flask API backend
├── requirements.txt                # Python dependencies
├── whiskey_production.db           # Production database (2,109 whiskeys)
├── whiskey_reviews.db              # Source review data
│
├── descriptor_vocabulary.py        # 81 tasting descriptors
├── match_descriptors_v2.py         # Descriptor matching logic
├── extract_prose_descriptors.py    # NLP extraction system
├── rebuild_production.py           # Database rebuild script
│
├── frontend/                       # React application
│   ├── src/
│   │   ├── pages/                  # HomePage, QuizPage, ResultsPage
│   │   ├── components/             # Header, Footer
│   │   ├── api/                    # API client
│   │   └── App.jsx                 # Main app component
│   ├── package.json
│   └── vite.config.js
│
├── docs/                           # Comprehensive documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── DESIGN_SYSTEM.md
│   ├── PRODUCTION_DATABASE_SUMMARY.md
│   ├── COMPOUND_DESCRIPTOR_FIX.md
│   └── DESCRIPTOR_USAGE_REPORT.md
│
├── scrapers/                       # Web scraping tools
├── scripts/                        # Utility scripts
├── migrations/                     # Database migrations
└── archive/                        # Historical files
```

---

## 🎯 Core Features

### Search & Discovery
- Real-time search across 2,109 whiskeys
- Results show whiskey name, distillery, and availability
- Only quiz-ready whiskeys shown (99.2% coverage)

### Sensory Quiz System
- **Sequential flow**: Nose → Palate → Finish
- **9 descriptor options** per section (4-6 correct)
- **Multi-select** with visual feedback
- **Hint system**: Shows number of correct options
- **Mobile-optimized** touch interface

### Results & Feedback
- **Overall accuracy** percentage
- **Section breakdown** (Nose, Palate, Finish)
- **Three categories**:
  - ✓ Correct (green) - Selected and correct
  - ○ Missed (gray) - Not selected but correct
  - ✗ Incorrect (red) - Selected but wrong
- **Source review links** for verification

### Data Quality
- **2,164 reviews** from Breaking Bourbon, Bourbon Banter
- **30,808 descriptor extractions** (70.8% pipe-delimited, 28.5% prose)
- **81 descriptors** across 11 categories
- **Conservative NLP** extraction (97.2% high confidence)

---

## 🎨 Design System

**Brand Colors:**
- Unspoken Navy: `#2a3c93` (primary)
- Unspoken Gold: `#d4af37` (accent)
- Unspoken Cream: `#f5f1e8` (background)

**Typography:**
- Josefin Sans (Google Fonts)
- 12px border radius standard
- Custom card shadows with navy tint

**Mobile-First:**
- 375px baseline
- Responsive breakpoints
- Touch-optimized interactions

See [DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) for complete guidelines.

---

## 📚 Documentation

### Getting Started
- [INSTALLATION.md](INSTALLATION.md) - Detailed setup guide
- [QUICK_START_TASK7.md](QUICK_START_TASK7.md) - Frontend quick start

### Technical Docs
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API endpoints reference
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database structure
- [PRODUCTION_DATABASE_SUMMARY.md](docs/PRODUCTION_DATABASE_SUMMARY.md) - Data stats

### Features & Fixes
- [COMPOUND_DESCRIPTOR_FIX.md](docs/COMPOUND_DESCRIPTOR_FIX.md) - Multi-word descriptors
- [FEATURE_SOURCE_REVIEWS.md](docs/FEATURE_SOURCE_REVIEWS.md) - Source links
- [DESCRIPTOR_USAGE_REPORT.md](DESCRIPTOR_USAGE_REPORT.md) - Descriptor statistics

### Planning & Progress
- [PRD.md](docs/PRD.md) - Product requirements
- [MVP_BUILD_TASKS.md](docs/MVP_BUILD_TASKS.md) - Build task tracking
- [CASE_STUDY.md](docs/CASE_STUDY.md) - Full case study

---

## 🔧 Development

### Running Tests
```bash
# Backend tests
python3 test_api.py
python3 test_database.py

# Frontend tests
cd frontend
npm test
```

### Database Maintenance

**Rebuild production database:**
```bash
python3 rebuild_production.py
```

**Update descriptor vocabulary:**
1. Edit `descriptor_vocabulary.py`
2. Run `rebuild_production.py`
3. Verify with `DESCRIPTOR_USAGE_REPORT.md`

**Add new whiskeys:**
- Add reviews to `whiskey_reviews.db`
- Run `rebuild_production.py`
- Database automatically updates

### Code Quality
- Backend: Flask best practices, REST API standards
- Frontend: React hooks, functional components
- Database: SQLite with proper indexes and foreign keys
- Documentation: Markdown with consistent formatting

---

## 🚢 Deployment

### Backend (Railway/Render)
1. Set up PostgreSQL database
2. Migrate SQLite → PostgreSQL
3. Deploy Flask app
4. Set environment variables

### Frontend (Vercel)
1. Connect GitHub repo
2. Configure build settings
3. Set API URL environment variable
4. Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) _(coming soon)_ for detailed instructions.

---

## 📈 Database Stats

- **Whiskeys**: 2,125 total, 2,109 quiz-ready (99.2%)
- **Reviews**: 2,164 from 2 sources
- **Descriptors**: 81 active (11 compounds, 70 singles)
- **Extractions**: 30,808 total descriptor tags
- **Categories**: 11 (sweet, spicy, woody, fruity, etc.)

**Top Descriptors:**
1. oak - 1,685 reviews (77.9%)
2. spice - 1,434 reviews (66.3%)
3. vanilla - 1,113 reviews (51.4%)
4. caramel - 1,083 reviews (50.0%)
5. rye - 966 reviews (44.6%)

---

## 🤝 Contributing

### Adding Descriptors
1. Check if descriptor appears in reviews
2. Add to `descriptor_vocabulary` table
3. Update `descriptor_vocabulary.py`
4. Run `rebuild_production.py`

### Adding Whiskeys
1. Scrape reviews or add manually to `whiskey_reviews.db`
2. Ensure 2+ reviews per whiskey
3. Run `rebuild_production.py`
4. Verify in search results

### Reporting Issues
- Check existing documentation first
- Provide detailed reproduction steps
- Include screenshots if applicable

---

## 📝 License

This project is for educational and portfolio purposes.

---

## 🙏 Credits

- **Data Sources**: Breaking Bourbon, Bourbon Banter
- **Tech**: Flask, React, Tailwind CSS, Vite
- **Design**: Unspoken brand guidelines

---

## 📞 Contact

Questions or feedback? Check the documentation or open an issue.

---

**Built with ❤️ for whiskey enthusiasts and sensory training**

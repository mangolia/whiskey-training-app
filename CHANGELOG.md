# Changelog

All notable changes to the Whiskey Sensory Training App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-28 - Production Release

### Added
- **Production Database**: Scaled from 30 to 2,109 quiz-ready whiskeys (99.2% coverage)
- **Conservative Prose NLP Extraction**: Rule-based system with negation handling, clause boundaries, and confidence scoring
- **Compound Descriptors**: Added 11 multi-word descriptors (toasted oak, black pepper, dark chocolate, etc.)
- **Source Review Links**: Results page now displays clickable links to original reviews for QA verification
- **Descriptor Usage Report**: Comprehensive documentation of all 81 descriptors with usage statistics
- **Enhanced Vocabulary**: Expanded from 73 to 81 active descriptors
- **Complete Documentation**: README.md, API docs, database schema, design system

### Changed
- **Database Schema**: Moved from `whiskey_mvp_v2.db` to `whiskey_production.db`
- **Descriptor Vocabulary**: Fixed compound matching (e.g., "baking spice" instead of separate "baking" + "spice")
- **Extraction Pipeline**: Combined pipe-delimited (70.8%) and prose (28.5%) review formats
- **Quiz Coverage**: Increased from 30 whiskeys to 2,109 whiskeys (7,030% increase)

### Fixed
- **Compound Descriptor Matching**: Multi-word terms now prioritized before component parts
- **Negation Detection**: Prose extraction properly handles "not X", "lacks X" with clause-aware boundaries
- **Vocabulary Inconsistencies**: Removed incorrect standalone descriptors ("baked", "baking")

### Technical Details
- 2,164 reviews processed from Breaking Bourbon and Bourbon Banter
- 30,808 total descriptor extractions (22,105 pipe + 8,089 prose)
- 28,513 aggregated quiz entries
- 97.2% high confidence prose extractions
- 81 descriptors across 11 categories (sweet, spicy, woody, fruity, floral, grain, bitter, savory, smoky, herbal, nutty)

---

## [0.2.0] - 2026-01-25 - Frontend Complete

### Added
- **React Frontend**: Complete React + Vite application with Tailwind CSS
- **Responsive Design**: Mobile-first approach (375px baseline) with touch optimization
- **Search Functionality**: Real-time debounced search across all whiskeys
- **Quiz Flow**: Sequential three-section quiz (Nose → Palate → Finish)
- **Results Display**: Accuracy breakdown with correct/incorrect/missed categorization
- **Design System**: Unspoken brand integration (Navy #2a3c93, Gold #d4af37, Cream #f5f1e8)

### Components
- HomePage with SearchBar and WhiskeySearchResults
- QuizPage with SenseSection and OptionCard
- ResultsPage with accuracy calculations
- Header and Footer components
- React Router v6 client-side routing

---

## [0.1.0] - 2026-01-24 - Backend Complete

### Added
- **Flask REST API**: Three endpoints for health, search, and quiz generation
- **Quiz Generation Logic**: Smart selection of 9 descriptors (4-6 correct, remaining as distractors)
- **Database Schema**: SQLite production schema with descriptor vocabulary, reviews, and aggregations
- **Automated Extraction**: Pipe-delimited descriptor extraction from structured reviews
- **CORS Support**: Cross-origin resource sharing for local development

### API Endpoints
- `GET /api/health` - Server health check
- `GET /api/whiskeys/search?q={query}` - Search whiskeys by name
- `GET /api/quiz/<whiskey_id>` - Generate quiz for specific whiskey

---

## [0.0.1] - 2026-01-23 - Initial Setup

### Added
- **Project Structure**: Created initial repository with docs, scrapers, scripts folders
- **Design System Documentation**: Comprehensive design guidelines (`DESIGN_SYSTEM.md`)
- **Database Schema**: Initial SQLite schema design
- **MVP Data Curation**: Selected 30 diverse whiskeys for MVP
- **Descriptor Vocabulary**: Defined 74 initial descriptors across 11 categories
- **Product Requirements**: Complete PRD with user stories and technical requirements

### Development
- Virtual environment setup (Python 3.8+)
- Dependencies: Flask, Flask-CORS, SQLite3
- Database migrations framework
- Development workflow documentation

---

## Unreleased

### Planned for v1.1.0
- Deployment to production (Railway + Vercel)
- Custom domain with HTTPS
- Analytics integration (Plausible)
- Error monitoring (Sentry)
- Beta testing program

### Planned for v1.2.0
- User accounts and quiz history
- Progress tracking over time
- Leaderboard functionality
- Additional whiskey sources

### Planned for v2.0.0
- User-submitted whiskey requests
- Advanced filtering (by distillery, region, proof)
- Tasting notes comparison tool
- Social sharing features

---

## Version History

- **v1.0.0** (2026-01-28): Production database with 2,109 whiskeys
- **v0.2.0** (2026-01-25): Complete React frontend
- **v0.1.0** (2026-01-24): Flask backend API
- **v0.0.1** (2026-01-23): Initial project setup

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new descriptors
- Adding new whiskeys
- Reporting issues
- Code style standards

---

## Acknowledgments

**Data Sources**: Breaking Bourbon, Bourbon Banter
**Framework**: Flask, React, Vite, Tailwind CSS
**Design**: Unspoken brand guidelines

---

**Maintained by**: Mike (angoliam@gmail.com)
**License**: Educational and portfolio use

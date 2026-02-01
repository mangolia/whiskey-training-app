# Whiskey Sensory Training - Frontend

React + Vite frontend for the Whiskey Sensory Training App.

## Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The app will run on `http://localhost:3000`

## Prerequisites

- Backend API must be running on `http://localhost:5001`
- Node.js 18+ installed

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── HomePage.jsx      # Search interface
│   │   ├── QuizPage.jsx      # Quiz interface (nose/palate/finish)
│   │   └── ResultsPage.jsx   # Results display
│   ├── components/
│   │   ├── Header.jsx        # Navigation header
│   │   └── Footer.jsx        # Footer
│   ├── api/
│   │   └── client.js         # Axios API client
│   ├── App.jsx               # Main app with routing
│   ├── main.jsx              # Entry point
│   └── index.css             # Tailwind CSS + custom styles
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Design System

**Colors:**
- Primary: `#2a3c93` (Unspoken Navy)
- Gold: `#d4af37` (Unspoken Gold)
- Cream: `#f5f1e8` (Background)

**Font:**
- Josefin Sans (Google Fonts)

**Components:**
- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.card` - Card container
- `.descriptor-option` - Descriptor button
- `.descriptor-option-selected` - Selected descriptor

## API Integration

The frontend communicates with the Flask backend via:
- `/api/health` - Health check
- `/api/whiskeys/search?q=query` - Search whiskeys
- `/api/quiz/<id>` - Get quiz data

Vite proxy configuration handles API routing in development.

## Mobile-First Design

The app is designed mobile-first with a 375px (iPhone SE) baseline. All components are responsive.

## Testing

1. Ensure backend is running: `python3 app.py` (in whiskey-scraper folder)
2. Start frontend: `npm run dev`
3. Visit `http://localhost:3000`
4. Search for a whiskey (e.g., "garrison")
5. Take a quiz
6. View results

## Next Steps

- Add loading skeletons
- Add error boundaries
- Add animations/transitions
- Optimize for production
- Deploy to Vercel

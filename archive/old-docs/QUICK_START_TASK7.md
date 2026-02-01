# Quick Start Guide: Task 7 - Frontend Setup

## Context

You've completed **6 out of 18 tasks (33%)**:
- ✅ Phase 0: Data Preparation (auto-extraction pipeline)
- ✅ Phase 1: Backend API (Flask, 3 endpoints, fully tested)

**Next**: Build the React frontend that consumes the API.

---

## Before You Start

### 1. Ensure Backend is Running

```bash
cd whiskey-scraper
source venv/bin/activate
python3 app.py
```

You should see:
```
Server starting on http://localhost:5001
```

**Keep this terminal running** (it's your API server).

### 2. Verify API Works

In a **new terminal**:
```bash
curl http://localhost:5001/api/health
```

Should return:
```json
{"status": "ok", "database": "connected", "whiskeys": 30}
```

---

## Task 7 Goals

**Build**: React + Vite application with routing and Tailwind CSS  
**Time**: 2-3 hours  
**Output**: Working dev server with placeholder pages  

### What You'll Create

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # Entry point
│   ├── pages/
│   │   ├── HomePage.jsx     # Search interface
│   │   ├── QuizPage.jsx     # Quiz interface
│   │   └── ResultsPage.jsx  # Results display
│   ├── components/
│   │   ├── Header.jsx       # Navigation
│   │   └── Footer.jsx       # Footer
│   └── api/
│       └── client.js        # Axios API client
├── tailwind.config.js       # Tailwind + design system
├── package.json
└── vite.config.js
```

---

## Step-by-Step Plan

### Step 1: Initialize Vite Project (15 min)
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### Step 2: Install Dependencies (10 min)
```bash
npm install react-router-dom axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 3: Configure Tailwind (20 min)
- Add design system colors from `brand-guidelines/`
- Configure fonts (Josefin Sans)
- Set up custom styles

### Step 4: Set Up Routing (30 min)
- Create basic page components
- Configure React Router
- Test navigation

### Step 5: Test API Connection (20 min)
- Create Axios client
- Test fetch from `/api/health`
- Display response in UI

### Step 6: Create Layout (30 min)
- Header with navigation
- Footer
- Mobile-responsive container

---

## Key Files to Reference

**Design System**: `/brand-guidelines/unspoken-brand-guidelines.md`
- Primary color: #2a3c93 (Unspoken Navy)
- Font: Josefin Sans
- Border radius: 12px

**API Documentation**: `/API_DOCUMENTATION.md`
- Endpoints
- Request/response formats
- Error handling

**Product Requirements**: `/docs/PRD.md`
- Mobile-first (375px baseline)
- User flows
- UI specifications

---

## Success Criteria

By end of Task 7, you should have:

- [ ] Vite dev server running on `localhost:3000`
- [ ] Tailwind CSS working with brand colors
- [ ] 3 routes: `/`, `/quiz/:id`, `/results`
- [ ] Placeholder content on each page
- [ ] Successful API call to backend health check
- [ ] Header and footer components
- [ ] Mobile-responsive layout

---

## Common Issues & Solutions

**Issue**: Port 3000 already in use  
**Solution**: Kill existing process or use different port in `vite.config.js`

**Issue**: CORS errors when calling API  
**Solution**: Backend has CORS enabled for `localhost:3000`, should work automatically

**Issue**: Tailwind not applying styles  
**Solution**: Check `tailwind.config.js` content paths include all JSX files

---

## Testing the Setup

Once dev server is running:

1. **Visit** `http://localhost:3000`
2. **See** homepage with Unspoken Navy header
3. **Navigate** to different routes
4. **Check** browser console for API response from health check

---

## After Task 7

**Next tasks**:
- Task 8: Build search interface
- Task 9: Build quiz (nose section)
- Task 10: Complete quiz (palate/finish)
- Task 11: Build results page

**Estimated total frontend time**: 10-12 hours

---

## Questions to Ask Claude

- "Show me the Tailwind config with the brand colors"
- "Help me set up the Axios API client"
- "Create the basic page components with routing"
- "How should I structure the component folders?"

**Ready to build! 🚀**

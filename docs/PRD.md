# **Whiskey Sensory Training App - Product Requirements Document (PRD)**

## **Document Information**
- **Version:** 2.0
- **Date:** January 2025
- **Status:** MVP Development Phase
- **Purpose:** Define requirements for building the MVP web application

---

## **1. Executive Summary**

### **Product Vision**
Build a whiskey tasting education platform that helps enthusiasts train their palate by comparing their sensory perceptions against aggregated professional reviews. The core experience is an interactive quiz where users identify aromas and flavors in whiskey's nose, palate, and finish.

### **MVP Scope - Mobile-First Web Application**
- **PLATFORM:** Progressive Web App (PWA) - mobile-first, responsive design
- **PRIMARY EXPERIENCE:** Mobile devices (phones, tablets)
- **SECONDARY EXPERIENCE:** Desktop browsers
- **IN SCOPE:**
  - Homepage with whiskey search
  - Interactive sensory quiz (nose, palate, finish)
  - Results page showing correct answers
  - Basic whiskey database integration
  - Touch-optimized interactions
  - Responsive design (320px to 1920px)
- **OUT OF SCOPE:**
  - User accounts & authentication
  - Progress tracking & stats dashboard
  - User-generated content
  - Social features
  - Native mobile apps (iOS/Android app stores)
  - Offline functionality (future consideration)

### **Success Criteria**
- **Mobile Experience:** App feels native on mobile devices (touch, gestures, speed)
- Users can search and find whiskeys from the database in < 2 taps
- Users can complete sensory quizzes for each whiskey in < 5 minutes on mobile
- Quiz presents 9 options per sense with 3-5 correct answers
- Results clearly show correct vs incorrect selections
- App loads in < 2 seconds on mobile 4G connection
- All touch targets are minimum 44px × 44px
- App works on iPhone SE (375px) to desktop (1920px)

---

## **2. User Personas**

### **Primary: The Whiskey Enthusiast**
- **Profile:** 25-45 years old, drinks whiskey 2-3x/week, owns 10-30 bottles
- **Goals:** Develop palate, learn to identify flavors, justify purchases with research
- **Pain Points:** Doesn't know if they're "tasting correctly," can't tell if what they detect matches professional reviews
- **Motivation:** Wants to be more confident discussing whiskey with peers, impress friends, make better buying decisions

### **Secondary: The Whiskey Nerd**
- **Profile:** Deep knowledge, active in online communities, attends tastings, owns 50+ bottles
- **Goals:** Challenge their palate, track their accuracy over time, discover new whiskeys
- **Pain Points:** Limited ways to objectively test their tasting skills, wants data-driven validation
- **Motivation:** Competitive self-improvement, credibility in whiskey communities

---

## **3. Core User Flows**

### **Flow 1: Homepage - Search for Whiskey**
**Actor:** User
**Goal:** Find a specific whiskey to quiz on

**Steps:**
1. User lands on homepage
2. User sees search bar with placeholder "Search for a whiskey..."
3. User types whiskey name or distillery
4. System displays matching results as list items showing:
   - Whiskey name
   - Distillery
5. User clicks on a whiskey from results
6. System navigates to quiz page for that whiskey

**UI Components:**
- Search input field (autofocus)
- Results dropdown/list
- Loading state during search
- Empty state if no results

**Technical Requirements:**
- Search against whiskey name and distillery fields
- Case-insensitive search
- Partial matching supported
- Minimum 2 characters before search triggers

---

### **Flow 2: Sensory Quiz - Complete All Three Senses**
**Actor:** User
**Goal:** Test ability to identify aromas and flavors

**Steps:**
1. User arrives at quiz page for selected whiskey
2. System displays whiskey name and current sense section (starts with "Nose")
3. **For each sense (Nose → Palate → Finish):**
   - System displays 9 sensory descriptor options
   - User clicks options to select (options highlight when selected)
   - Hint shows "Select all that you detect" with indicator of correct count (e.g., "3 correct options")
   - User clicks "Submit" button for that sense
   - System reveals results for that sense:
     - Correct selections (green highlight)
     - Incorrect selections (red highlight)
     - Missed correct options (shown with indicator)
   - User clicks "Next" to move to next sense
4. After all three senses submitted, user clicks "View Final Results"
5. System displays complete results page with breakdown per sense

**UI Components:**
- Progress indicator (Nose → Palate → Finish)
- 9 selectable option cards per sense
- Submit button (disabled until at least one option selected)
- Results overlay/section showing correct/incorrect
- Next button to advance to next sense
- View Final Results button (after all three complete)

**Technical Requirements:**
- Each sense presents exactly 9 options
- 3-5 options are correct (sourced from review database)
- Remaining options are random (sourced from master database)
- User can select multiple options (multi-select)
- Hint displays actual number of correct options
- State management tracks selections per sense
- Results stored temporarily until final results viewed

---

### **Flow 3: View Final Results**
**Actor:** User
**Goal:** See comprehensive results across all senses

**Steps:**
1. User clicks "View Final Results" after completing all three senses
2. System displays results page with:
   - Overall accuracy score
   - Breakdown by sense (Nose, Palate, Finish):
     - Correct selections listed
     - Missed correct options listed
     - Incorrect selections listed
   - Option to "Try Another Whiskey" (returns to homepage)
   - Option to "Retake Quiz" (restarts quiz with new random options)

**UI Components:**
- Score summary card
- Three result sections (one per sense)
- Visual indicators (✓ for correct, ✗ for incorrect, ○ for missed)
- Action buttons (Try Another, Retake)

**Technical Requirements:**
- Calculate accuracy: (correct selections) / (total correct options) × 100
- Display all three sense results on single page
- Retake generates new set of random incorrect options
- Results are not persisted (ephemeral for MVP)

---

### **UC-3: Aggregate Tasting Notes from Multiple Reviews**
**Actor:** System (automated process)  
**Goal:** Combine tasting notes from multiple review sources into single master list per whiskey  
**Preconditions:** Multiple reviews exist for same whiskey  

**Flow:**
1. Scraper adds new review to database
2. System identifies whiskey (by whiskey_id)
3. System extracts structured tasting notes from review (manual tagging workflow for MVP)
4. System updates aggregated tasting notes for that whiskey:
   - Combines all unique descriptors from all reviews
   - Maintains link to which review each descriptor came from
   - Marks notes as needing refresh
5. Aggregated notes become available for quiz generation

**Data Requirements:**
- Raw review text (nose, palate, finish) preserved
- Structured descriptor tags extracted and linked to reviews
- Aggregation logic that merges descriptors across reviews
- Track which descriptors came from which reviews (for debugging/quality)

**Database Implications:**
- `reviews` table stores raw text: `nose_text`, `palate_text`, `finish_text`
- `review_descriptors` table links reviews to specific descriptors: `review_id`, `descriptor_id`, `tasting_section`
- `aggregated_whiskey_descriptors` view or table: `whiskey_id`, `descriptor_id`, `tasting_section`, `source_review_ids[]`
- Trigger or scheduled job to refresh aggregations when new reviews added

---

### **UC-4: Handle Whiskey Variants**
**Actor:** System (during scraping/data entry)  
**Goal:** Correctly identify and store whiskey variants as separate entities  
**Preconditions:** Review mentions specific variant attributes (batch, release year, edition)  

**Flow:**
1. Scraper encounters whiskey review
2. System extracts: brand, variant name, attributes (batch, release type, special edition)
3. System checks if this specific variant exists:
   - Match on: brand_family + variant_name + key attributes
4. If new variant: Create new whiskey record with variant metadata
5. If existing variant: Link review to existing whiskey_id
6. Preserve brand family relationships for search/filtering

**Data Requirements:**
- Whiskey identity components: brand_family, variant_name, batch, release_type, edition
- Flexible attribute storage for various release types (limited edition, store pick, international release, barrel proof, etc.)
- Parent-child relationship implicit through brand_family

**Database Implications:**
- `whiskeys` table fields: `brand_family`, `variant_name`, `attributes` (JSON for flexible variant metadata)
- `brand_families` table (future): `brand_family_id`, `name`, `parent_company`, `distillery`
- Compound uniqueness check on brand + variant + key attributes
- Standardize attribute keys (batch, release_year, release_type, edition_name)

---

## **4. Technical Architecture**

### **4.1 Frontend - React Mobile-First Web App**

**Tech Stack:**
- **Framework:** React 18+ with Vite
- **Routing:** React Router v6 (for client-side routing)
- **Styling:** Tailwind CSS v3+ (mobile-first utility classes)
- **State Management:** React useState/useContext (no Redux for MVP)
- **HTTP Client:** Axios (for better error handling than Fetch)
- **Mobile Features:** Touch gestures, responsive images, performance optimization

**Complete URL Structure:**
```
PRODUCTION:
https://whiskeytraining.app/             → Homepage with search
https://whiskeytraining.app/quiz/:whiskeyId/:whiskeySlug  → Quiz page
https://whiskeytraining.app/results      → Results (state-based, no ID)

LOCAL DEVELOPMENT:
http://localhost:5173/                   → Homepage
http://localhost:5173/quiz/42/buffalo-trace  → Quiz page
http://localhost:5173/results            → Results page

API ENDPOINTS (Backend):
http://localhost:5000/api/whiskeys/search?q={query}
http://localhost:5000/api/quiz/:whiskeyId
http://localhost:5000/api/health         → Health check

PRODUCTION API:
https://api.whiskeytraining.app/api/whiskeys/search?q={query}
https://api.whiskeytraining.app/api/quiz/:whiskeyId
```

**URL Parameters:**
- `:whiskeyId` - Database ID (e.g., 42)
- `:whiskeySlug` - SEO-friendly name (e.g., buffalo-trace, eagle-rare-10)
- Query params: `?q=` for search, `?retry=true` for quiz retakes

**Key Components (Mobile-First):**
- `SearchBar` - Touch-optimized input (min 44px height)
- `WhiskeySearchResults` - Large tap targets (min 56px)
- `QuizPage` - Full-screen mobile experience
- `SenseSection` - Swipe-enabled sense navigation
- `OptionCard` - Large touch targets (88px × 88px on mobile)
- `ProgressIndicator` - Fixed top bar (mobile) / sidebar (desktop)
- `ResultsView` - Scrollable mobile layout
- `ResultsSummary` - Slide-up modal (mobile) / inline (desktop)
- `MobileNav` - Bottom navigation bar (mobile only)
- `LoadingSpinner` - Full-screen loading states
- `ErrorBoundary` - Error handling wrapper

**State Management:**
- **Quiz State:** current sense index, selections per sense, submitted flags
- **Results State:** correct/incorrect/missed arrays per sense, overall accuracy
- **Whiskey State:** selected whiskey data (cached in sessionStorage)
- **UI State:** loading, errors, modal visibility
- **Navigation State:** previous URL for "back" functionality

---

### **4.2 Backend API Requirements**

**Endpoints Needed:**

**1. Search Whiskeys**
```
GET /api/whiskeys/search?q={query}
Response: [
  {
    id: string,
    name: string,
    distillery: string
  }
]
```

**2. Get Quiz Data**
```
GET /api/quiz/:whiskeyId
Response: {
  whiskeyId: string,
  whiskeyName: string,
  distillery: string,
  nose: {
    options: [string], // 9 options
    correctOptions: [string] // 3-5 correct
  },
  palate: { ... },
  finish: { ... }
}
```

**3. Validate Quiz (Optional - can be done client-side)**
```
POST /api/quiz/validate
Body: {
  whiskeyId: string,
  selections: {
    nose: [string],
    palate: [string],
    finish: [string]
  }
}
Response: {
  results: {
    nose: { correct: [...], incorrect: [...], missed: [...] },
    palate: { ... },
    finish: { ... }
  },
  accuracy: number
}
```

**Data Sources:**
- **Correct options (3-5):** Query review database for aggregated sensory descriptors
- **Random options (4-6):** Query master sensory descriptor database, excluding correct options
- **Total options:** Exactly 9 per sense

---

### **4.3 Database Schema (Simplified for MVP)**

**Tables:**

**whiskeys**
- id (primary key)
- name
- distillery
- brand_family
- proof (optional)
- classification (optional)

**reviews**
- id (primary key)
- whiskey_id (foreign key)
- source_site
- nose_text (raw text)
- palate_text (raw text)
- finish_text (raw text)

**sensory_descriptors** (master list)
- id (primary key)
- descriptor (e.g., "vanilla", "caramel", "oak")
- category (e.g., "sweet", "woody", "fruity")
- applicable_sections (array: ["nose", "palate", "finish"])

**review_descriptors** (links reviews to descriptors)
- review_id (foreign key)
- descriptor_id (foreign key)
- sense_section (enum: nose/palate/finish)

**aggregated_whiskey_descriptors** (pre-computed for performance)
- whiskey_id (foreign key)
- descriptor_id (foreign key)
- sense_section (enum)
- review_count (how many reviews mention this)

---

### **4.4 Quiz Generation Logic**

**For each sense (Nose, Palate, Finish):**

1. **Fetch correct descriptors:**
   ```sql
   SELECT descriptor
   FROM aggregated_whiskey_descriptors
   WHERE whiskey_id = ? AND sense_section = ?
   LIMIT 5  -- Maximum 5 correct options
   ```

2. **Calculate random options needed:**
   ```
   random_count = 9 - correct_count
   ```

3. **Fetch random descriptors:**
   ```sql
   SELECT descriptor
   FROM sensory_descriptors
   WHERE applicable_sections CONTAINS ?
   AND id NOT IN (correct_descriptor_ids)
   ORDER BY RANDOM()
   LIMIT random_count
   ```

4. **Combine and shuffle:**
   ```javascript
   const allOptions = [...correctDescriptors, ...randomDescriptors]
   const shuffled = allOptions.sort(() => Math.random() - 0.5)
   ```

5. **Return to frontend with metadata:**
   ```javascript
   {
     options: shuffled,
     correctCount: correctDescriptors.length, // For hint
     correctOptions: correctDescriptors // For validation
   }
   ```

---

## **5. User Interface Specifications**

### **5.1 Homepage (Mobile-First)**

**Mobile Layout (320px - 768px):**
- Full-screen experience
- Header: "Whiskey Sensory Training" (20px font, bold)
- Subtitle: "Test your palate" (14px font, centered)
- Search bar: Full width minus 16px padding, 52px height
- Touch target: Entire search area clickable (min 44px)
- Results: Full-width cards, 56px height each
- No keyboard on load (tap to show)

**Tablet Layout (768px - 1024px):**
- Max-width: 640px centered
- Search bar: 56px height
- Results: Card layout with hover states

**Desktop Layout (1024px+):**
- Max-width: 800px centered
- Search bar autofocus on page load
- Results: Hover states, keyboard navigation

**Search Behavior:**
- Mobile: Tap to focus → virtual keyboard appears
- Debounced search (400ms after user stops typing on mobile, 300ms desktop)
- Loading: Subtle spinner inside search box (doesn't jump layout)
- Results: Slide down animation, swipe to dismiss on mobile
- Each result: Whiskey Name (16px bold) | Distillery (14px gray)

**Touch Interactions:**
- Tap search → keyboard appears
- Tap result → navigate to quiz
- Swipe down → dismiss keyboard
- Pull to refresh → refresh search results (future)

---

### **5.2 Quiz Page (Mobile-First)**

**Mobile Layout (320px - 768px):**
- **Fixed Header** (60px height):
  - Back button (left, 44px × 44px)
  - Whiskey name (truncated, 14px font)
  - Progress dots: ● ○ ○ (Nose, Palate, Finish)
- **Sense Title**: Large (24px font, bold), centered
- **Hint**: "Select all that you detect (X correct)" (14px, gray)
- **Option Grid**: 2 columns, 16px gap
  - Each card: Full width, 88px height, 16px border-radius
  - Large touch target, comfortable tapping
- **Fixed Bottom Bar** (72px height, safe area inset):
  - Submit button: Full width minus 32px padding, 52px height
  - Elevated shadow, sticky position

**Tablet Layout (768px - 1024px):**
- Option Grid: 3 columns
- Card height: 80px
- Side padding: 32px

**Desktop Layout (1024px+):**
- Max-width: 900px centered
- Option Grid: 3 columns
- Card height: 72px
- Submit button: Max-width 400px, centered

**Option Card States (Mobile-Optimized):**
- **Default**: White bg, 2px gray border, subtle shadow
- **Tap Feedback**: 50ms scale animation (scale 0.98)
- **Selected**: Blue bg (#3B82F6), white text, checkmark icon (right)
- **Post-Submit - Correct**: Green bg (#10B981), white text, ✓ icon
- **Post-Submit - Incorrect**: Red bg (#EF4444), white text, ✗ icon
- **Post-Submit - Missed**: Yellow border (#F59E0B), gray bg, ○ icon
- **Disabled**: 50% opacity, no pointer events

**Touch Interactions:**
- Tap card → toggle selection (haptic feedback on iOS)
- Double tap → prevent zoom (CSS touch-action)
- Swipe left/right → navigate between senses (after submit)
- Tap outside → no action (focused experience)
- Submit button:
  - Disabled state: Gray, 50% opacity
  - Enabled state: Blue, pulsing animation
  - Loading state: Spinner inside button

**Animations:**
- Sense transition: Slide animation (300ms)
- Card selection: Scale + fade (150ms)
- Results reveal: Stagger animation (100ms delay per card)
- Submit button: Ripple effect on tap

---

### **5.3 Results Page**

**Layout:**
- Header: "Your Results for [Whiskey Name]"
- Overall score card: "X% Accuracy"
- Three sections (Nose, Palate, Finish):
  - Section title
  - Correct selections: ✓ Descriptor names (green)
  - Missed options: ○ Descriptor names (yellow/amber)
  - Incorrect selections: ✗ Descriptor names (red)
- Action buttons:
  - "Try Another Whiskey" (returns to homepage)
  - "Retake Quiz" (resets quiz with new random options)

**Responsive:**
- Stack sections vertically on mobile
- Card-based layout on desktop

---

## **6. MVP Feature Scope**

### **IN SCOPE**
✅ Homepage with whiskey search
✅ Search by whiskey name or distillery
✅ Quiz page with three senses (Nose, Palate, Finish)
✅ 9 options per sense (3-5 correct, remainder random)
✅ Multi-select option selection
✅ Hint showing correct option count
✅ Submit per sense with immediate feedback
✅ Final results page with breakdown
✅ Retake quiz functionality
✅ Responsive design (mobile + desktop)

### **OUT OF SCOPE (Future Phases)**
❌ User accounts & authentication
❌ Progress tracking / historical stats
❌ Leaderboards / social features
❌ User-generated reviews
❌ Whiskey recommendations
❌ Advanced filters (proof, age, region)
❌ Timed quiz mode
❌ Difficulty levels
❌ Native mobile apps

---

## **7. Data Requirements**

### **Minimum Data Needed for Launch:**
- **50-100 whiskeys** with complete sensory data
- **150+ reviews** (average 2-3 reviews per whiskey)
- **50-100 sensory descriptors** in master list
- **Aggregated data** pre-computed for all whiskeys

### **Data Quality Standards:**
- Each whiskey must have at least 3 correct descriptors per sense
- Descriptors must be specific (not vague like "complex" or "balanced")
- Manual review of first 100 descriptors for accuracy

### **Data Preparation Workflow:**
1. Scrape reviews from existing sources
2. Manually tag sensory descriptors per review
3. Aggregate descriptors per whiskey
4. Build master descriptor list
5. Categorize descriptors for better random selection
6. Load into production database

---

### **Epic 3: Data Aggregation & Quality**

**US-3.1: Scrape Review with Structured Data**
*As a system, I need to capture both raw and structured tasting notes so that data can be used for quiz generation.*

**Acceptance Criteria:**
- Store raw text fields: nose_text, palate_text, finish_text
- Store placeholder for structured descriptor tags (manual tagging in MVP)
- Preserve review source URL and metadata

**Data Needed:**
- `reviews` table with text fields
- `review_descriptors` table ready for future tagging

---

**US-3.2: Manual Descriptor Tagging Workflow**
*As an admin, I need to manually tag descriptors in reviews so that they can be used in quizzes.*

**Acceptance Criteria:**
- Admin can view raw review text
- Admin selects descriptors from master vocabulary
- Admin assigns descriptors to nose/palate/finish sections
- System links descriptors to review in database

**Data Needed:**
- `descriptor_vocabulary` table (master list)
- `review_descriptors` join table
- UI to display raw text and descriptor selection interface

---

**US-3.3: Aggregate Descriptors Across Reviews**
*As a system, I need to combine descriptors from multiple reviews into a single master list so that quizzes have comprehensive correct answers.*

**Acceptance Criteria:**
- When new review added, trigger aggregation for that whiskey
- Combine all unique descriptors across all reviews
- Maintain link to which review each descriptor came from
- Mark aggregation timestamp

**Data Needed:**
- `aggregated_whiskey_descriptors` table or view
- Includes: whiskey_id, descriptor_id, tasting_section, source_review_ids[], updated_at

---

**US-3.4: Handle Whiskey Variants**  
*As a system, I need to distinguish between whiskey variants so that different batches/editions are treated as separate entities.*

**Acceptance Criteria:**
- Detect variant attributes from review (batch, edition, release year)
- Check if variant exists in database
- Create new whiskey record if new variant
- Link to existing record if variant exists
- Preserve brand_family for relationship tracking

**Data Needed:**
- `whiskeys.brand_family`, `variant_name`, `attributes` (JSON)
- Standardized attribute keys in JSON

---

### **Epic 4: Master Descriptor Vocabulary**

**US-4.1: Build Master Descriptor List**
*As an admin, I need a comprehensive list of all possible sensory descriptors so that the system can generate quiz options.*

**Acceptance Criteria:**
- List includes all unique descriptors scraped from reviews
- Each descriptor has category (fruity, spicy, woody, floral, grain, etc.)
- Each descriptor tagged with applicable sections (nose, palate, finish, or all)
- List updates as new reviews are scraped

**Data Needed:**
- `descriptor_vocabulary` table: descriptor_name, category, applicable_sections[]

---

**US-4.2: Categorize Descriptors**
*As a system, I need descriptors categorized so that I can generate plausible wrong answers for quizzes.*

**Acceptance Criteria:**
- Descriptors grouped into categories (fruity, spicy, woody, etc.)
- Category used to filter random incorrect options (e.g., don't show "diesel" as wrong answer for bourbon)
- Categories extensible for future complexity

**Data Needed:**
- `descriptor_vocabulary.category` field
- Predefined category list (can be enum or reference table)

---

## **5. Data Quality & Workflows**

### **5.1 Manual Descriptor Tagging Workflow**

**Purpose:** Extract structured descriptors from raw review text for quiz generation

**Process:**
1. Admin selects untagged reviews (where `review_descriptors` doesn't exist for review_id)
2. Admin interface displays:
   - Raw nose_text, palate_text, finish_text
   - Master descriptor_vocabulary searchable list
   - Section selectors (nose, palate, finish)
3. Admin selects applicable descriptors for each section
4. System inserts records into `review_descriptors` table
5. System triggers aggregation refresh for that whiskey

**Database Support:**
- Query for untagged reviews: `SELECT * FROM reviews WHERE review_id NOT IN (SELECT DISTINCT review_id FROM review_descriptors)`
- `review_descriptors.tagged_by = 'manual'` to track tagging source

---

### **5.2 Aggregation Refresh Logic**

**Triggers:**
- New review added for existing whiskey
- Existing review re-tagged with different descriptors

**Process:**
1. Identify whiskey_id that needs refresh
2. Query all `review_descriptors` for that whiskey, grouped by `tasting_section` and `descriptor_id`
3. For each unique (whiskey_id, descriptor_id, tasting_section):
   - Aggregate source_review_ids[]
   - Count number of reviews
   - Update or insert into `aggregated_whiskey_descriptors`
4. Set `last_updated` timestamp

---

### **5.3 Quiz Generation Logic**

**Inputs:**
- `whiskey_id`
- `tasting_section` (nose, palate, or finish)

**Process:**
1. Fetch correct descriptors for whiskey + section from `aggregated_whiskey_descriptors`
2. Count correct descriptors (N)
3. Calculate incorrect descriptors needed: 9 - N
4. Query `descriptor_vocabulary` for random descriptors:
   - Same `category` as correct descriptors (for plausibility)
   - Applicable to this `tasting_section`
   - Exclude correct descriptor_ids
   - LIMIT (9 - N)
5. Combine and shuffle correct + incorrect descriptors
6. Return 9 options to frontend

---

## **6. Future Enhancements (Post-MVP)**

### **Phase 2: User Accounts**
- Implement `users`, `quiz_attempts`, `user_tasting_notes` tables
- Track quiz history and accuracy trends
- Personalized dashboards

### **Phase 3: Social Features**
- Share quiz results
- Compare notes with friends
- Leaderboards (accuracy competitions)

### **Phase 4: Advanced Quiz Modes**
- Difficulty levels (easy vs hard wrong answers)
- Timed challenges
- Blind tastings (no whiskey name revealed upfront)

### **Phase 5: Stats Dashboard**
- Public analytics: proof distributions, release trends, regional patterns
- Requires additional computed tables or data warehouse

### **Phase 6: Brand/Distillery Normalization**
- Implement `brand_families` table
- Migrate brand_family strings to foreign keys
- Enable distillery-level analytics

---

## **8. Development Phases**

### **Phase 1: Foundation (Week 1-2)**
- Set up React + Vite project
- Create basic routing structure
- Design component hierarchy
- Set up Tailwind CSS
- Create static mockups of all pages

### **Phase 2: Frontend Core (Week 2-3)**
- Build Homepage with search UI
- Build Quiz page structure
- Implement quiz state management
- Build Results page
- Add responsive design

### **Phase 3: Backend Integration (Week 3-4)**
- Define API contracts
- Create API endpoints (search, quiz data)
- Connect frontend to backend
- Implement quiz generation logic
- Test with sample data

### **Phase 4: Data & Polish (Week 4-5)**
- Populate database with 50-100 whiskeys
- Manual tagging of sensory descriptors
- Aggregate data for quiz generation
- UI polish and bug fixes
- Performance optimization

### **Phase 5: Testing & Launch (Week 5-6)**
- Cross-browser testing
- Mobile device testing
- Load testing
- Bug fixes
- Deploy to production

---

## **9. Infrastructure & Deployment**

### **9.1 Development Environment**

**Local Setup:**
```bash
# Project structure
whiskey-training-mvp/
├── frontend/          # React + Vite app
│   ├── src/
│   ├── public/
│   ├── vite.config.js
│   └── package.json
├── backend/           # Python Flask API
│   ├── app.py
│   ├── database.py
│   ├── requirements.txt
│   └── whiskey_mvp.db  # SQLite database
└── docs/
```

**Prerequisites:**
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- SQLite3

**Local Development URLs:**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000`
- Database: `./backend/whiskey_mvp.db`

---

### **9.2 Deployment Strategy**

**Phase 1: Local Development (Week 1-4)**
- Develop on local machine
- SQLite database
- No authentication required
- Testing with sample data (20-30 whiskeys)

**Phase 2: Staging Deployment (Week 5)**
- **Frontend**: Vercel (free tier)
  - Auto-deploy from GitHub main branch
  - Preview deployments for PRs
  - Domain: `whiskey-training-mvp.vercel.app`
- **Backend**: Railway or Render (free tier)
  - Deploy Flask API
  - PostgreSQL database (migrate from SQLite)
  - Environment variables for secrets
- **Domain**: Optional custom domain

**Phase 3: Production (Week 6+)**
- Custom domain: `whiskeytraining.app`
- CDN for static assets (Cloudflare)
- Database backups
- Monitoring (Sentry for errors)
- Analytics (Plausible or Simple Analytics)

**Recommended Stack:**
- **Frontend Host**: Vercel or Netlify
- **Backend Host**: Railway, Render, or Fly.io
- **Database**:
  - Local/Staging: SQLite
  - Production: PostgreSQL (Railway/Render managed)
- **File Storage**: Not needed for MVP
- **CDN**: Cloudflare (free tier)

---

### **9.3 Technology Decisions (FINAL)**

**✅ Backend: Python/Flask**
- **Why**: Existing codebase uses Python, database.py already exists
- **Stack**: Flask 3.0+, Flask-CORS, SQLAlchemy
- **Database**: SQLite (local) → PostgreSQL (production)

**✅ Frontend: React + Vite**
- **Why**: Fast development, modern tooling, mobile-first support
- **Stack**: React 18+, Vite 5+, React Router v6, Tailwind CSS
- **Build**: Vite builds to static files, deployed to Vercel

**✅ Database Schema: Use Updated Schema**
- Create fresh `whiskey_mvp.db` with descriptor tables
- Migrate 20-30 whiskeys from existing database
- Manual descriptor tagging workflow for MVP data

**✅ Hosting: Vercel + Railway**
- **Frontend**: Vercel (auto-deploy, preview URLs, fast CDN)
- **Backend**: Railway (easy Python deployment, managed PostgreSQL)
- **Cost**: Free tier for MVP, < $10/month when scaled

---

### **9.4 Data Preparation Decisions**

**MVP Data Set:**
- **Start with**: 30 whiskeys (manually selected popular bottles)
- **Reviews per whiskey**: 2-3 reviews minimum
- **Descriptors**: 60-80 unique descriptors
- **Manual tagging**: 2-3 hours per 10 whiskeys

**Whiskey Selection Criteria:**
- Popular brands (Buffalo Trace, Maker's Mark, Eagle Rare, etc.)
- Variety of types (bourbon, rye, scotch)
- Existing reviews in current database
- Known flavor profiles (easier to tag accurately)

**Data Migration Process:**
1. Create new `whiskey_mvp.db` with updated schema
2. Select 30 whiskeys from existing database
3. Copy review text for selected whiskeys
4. Build descriptor vocabulary (60-80 descriptors)
5. Manually tag descriptors for each review
6. Run aggregation to populate `aggregated_whiskey_descriptors`
7. Test quiz generation for each whiskey

---

## **10. Open Questions & Final Decisions**

### **✅ DECIDED:**
1. **Backend**: Python/Flask (use existing infrastructure)
2. **Database**: SQLite (MVP) → PostgreSQL (production)
3. **Hosting**: Vercel (frontend) + Railway (backend)
4. **Design Approach**: Mobile-first, Tailwind CSS
5. **Data Set**: 30 whiskeys for MVP launch
6. **Descriptor Categories**: Fruity, spicy, woody, floral, grain, sweet, bitter, savory, smoky
7. **Scoring**: Simple percentage (correct / total) × 100
8. **Random Options**: Category-matched to correct options for plausibility

### **❓ NEEDS DECISION:**
1. **Color Scheme**: Blue/green or earth tones? (Whiskey brand colors)
2. **Typography**: System fonts or custom web fonts?
3. **Domain Name**: `whiskeytraining.app` or `palatetrainer.com` or other?
4. **Timeline**: 5-6 weeks realistic for MVP launch?
5. **Beta Testing**: Closed beta with 10-20 users before public launch?

---

## **10. Success Metrics**

### **MVP Launch Criteria:**
- ✅ 50+ whiskeys available with complete data
- ✅ Search returns results in < 500ms
- ✅ Quiz loads in < 1 second
- ✅ App works on Chrome, Firefox, Safari (desktop + mobile)
- ✅ Zero crashes during testing
- ✅ Clean, professional UI

### **User Experience Goals:**
- Users complete quiz in < 5 minutes
- Quiz completion rate > 70%
- Users retry quizzes (engagement indicator)
- Low bounce rate from homepage

### **Technical Performance:**
- Page load time < 2 seconds
- API response time < 500ms
- Mobile-friendly (responsive design)
- Accessible (WCAG 2.1 AA basics)

---

## **11. Appendix: User Flow Examples**

### **Example 1: Complete User Journey**
```
1. User visits homepage
2. Types "Buffalo Trace" in search bar
3. Sees "Buffalo Trace Bourbon" appear in results
4. Clicks on result
5. Quiz page loads showing:
   - Whiskey: Buffalo Trace Bourbon | Distillery: Buffalo Trace
   - Progress: [NOSE] → Palate → Finish
   - Hint: "Select all that you detect (4 correct options)"
   - 9 options: vanilla, caramel, oak, honey, cherry, butterscotch, cinnamon, apple, leather
6. User selects: vanilla, caramel, butterscotch, cinnamon
7. User clicks "Submit"
8. Results overlay shows:
   - ✓ Correct: vanilla, caramel
   - ✗ Incorrect: butterscotch, cinnamon
   - ○ Missed: oak, honey
   - Score: 2/4 (50%)
9. User clicks "Next"
10. Palate section loads with new 9 options
11. User repeats for Palate, then Finish
12. After all three sections, clicks "View Results"
13. Final results page shows:
    - Overall: 65% accuracy
    - Breakdown per sense
14. User clicks "Try Another Whiskey"
15. Returns to homepage
```

### **Example 2: Quiz Generation Process**
```
Whiskey: Eagle Rare 10 Year
Database query for NOSE section:

Correct descriptors (from aggregated reviews):
- caramel (appears in 5 reviews)
- vanilla (appears in 5 reviews)
- cherry (appears in 3 reviews)
- oak (appears in 4 reviews)
Total correct: 4

Random descriptors needed: 9 - 4 = 5

Random selection (excluding correct ones):
- cinnamon
- butterscotch
- apple
- honey
- leather

Final 9 options (shuffled):
[cherry, butterscotch, caramel, apple, vanilla, oak, cinnamon, honey, leather]

Metadata sent to frontend:
- options: [all 9 shuffled]
- correctCount: 4 (for hint)
- correctOptions: [caramel, vanilla, cherry, oak] (for validation)
```

### **Example 3: Results Calculation**
```
User selections for Nose: [caramel, vanilla, butterscotch]
Correct options: [caramel, vanilla, cherry, oak]

Results:
- Correct: [caramel, vanilla] (2)
- Incorrect: [butterscotch] (1)
- Missed: [cherry, oak] (2)

Accuracy: 2 / 4 = 50%

Display:
✓ caramel
✓ vanilla
✗ butterscotch
○ cherry (you missed this)
○ oak (you missed this)
```

---

## **12. Next Steps**

### **Immediate Actions:**
1. ✅ Update PRD with MVP web app specifications
2. Review database schema for MVP needs
3. Set up React + Vite project structure
4. Design wireframes/mockups for three main pages
5. Define API contracts
6. Choose backend technology and hosting platform

### **Questions for Product Owner:**
- Preferred backend technology?
- Design preferences (color scheme, branding)?
- Timeline expectations?
- Any specific whiskeys that MUST be included at launch?

---

**END OF PRD v2.0 - MVP Web Application**
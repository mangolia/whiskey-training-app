# LinkedIn Article Series: Building with Claude - A Practical Guide

**Target Audience**: Developers, product managers, technical founders
**Goal**: Show how to effectively collaborate with Claude to build a production app
**Format**: 6-8 short articles (800-1200 words each)
**Tone**: Practical, honest about what works and what doesn't

---

## Article 1: "Starting with Data: Why I Built a Web Scraper Before Writing Any Product Code"

### Hook
Most people start with the product. I started with data. Here's why that was the right call.

### Key Points

**The Traditional Approach (Wrong)**:
- Idea → Mockups → Build product → Realize you need data → Scramble to find it

**The Data-First Approach (Right)**:
- Idea → Validate data availability → Build scraper → Understand the data → Design product around what's possible

**Why this matters**:
- Data shapes your product more than you think
- Understanding data constraints early saves months of rework
- Real data reveals product opportunities you didn't see

### Claude Collaboration Notes

**What Claude was great at**:
- Writing the initial web scraper code (BeautifulSoup, requests)
- Explaining HTML parsing strategies
- Building automated daily scraping with cron jobs
- Error handling and retry logic

**What required iteration**:
- Understanding specific website structures (needed to show Claude the HTML)
- Handling edge cases (different review formats)
- Rate limiting and politeness strategies

**Key Lesson**: "Claude can write the scraper in 30 minutes, but understanding your data takes weeks. Use Claude to accelerate the technical work while you focus on understanding the domain."

### Practical Takeaways

1. **Before building a product, ask**: Where will the data come from?
2. **Build a scraper first**: Even if you plan to have users contribute data later
3. **Collect for months before building**: I scraped for 3 months before touching product code
4. **Data quality matters more than quantity**: 60 high-quality reviews beat 1000 messy ones

### Code Example to Include
```python
# Show a simple scraper snippet that Claude helped write
# Highlight the parts that were easy (structure) vs hard (domain logic)
```

### Ending
"Three months of scraping taught me more about whiskey reviews than any amount of planning would have. When I finally started building the product, I knew exactly what was possible because I'd spent months living with the data."

---

## Article 2: "The Database Schema That Almost Broke My Product (And How Claude Helped Fix It)"

### Hook
I designed my database schema in 20 minutes. It took 2 months to realize it was completely wrong for what I was building.

### Key Points

**The Original Schema (Naive)**:
- Just stored reviews as blobs of text
- Assumed I'd do text matching later
- No structure for "what descriptors are in this review?"

**The Pivot**:
- Realized I needed structured descriptor data for quizzes
- Had to redesign: `descriptor_vocabulary` → `review_descriptors` → `aggregated_whiskey_descriptors`
- Three tables instead of one

**Why the redesign was necessary**:
- Can't generate quizzes from unstructured text
- Need to know "which descriptors are correct for THIS whiskey"
- Need to pull "incorrect" descriptors from OTHER whiskeys

### Claude Collaboration Notes

**What Claude excelled at**:
- Generating SQL CREATE TABLE statements
- Designing foreign key relationships
- Creating indexes for performance
- Writing migration scripts

**What I had to figure out**:
- The actual business logic (how quizzes work)
- Whether to denormalize for performance
- Deciding on the "aggregated" table approach

**Critical moment**:
When I explained "I need to generate quizzes with correct/incorrect answers," Claude immediately suggested the three-table approach. I had been trying to do it with text search.

### Practical Takeaways

1. **Don't design your schema in isolation**: Describe your use case to Claude first
2. **Many-to-many relationships are your friend**: `review_descriptors` links reviews to descriptors
3. **Denormalization is OK for read-heavy apps**: The aggregated table trades storage for speed
4. **Migrations matter**: Document your schema evolution

### Visual/Diagram to Include
```
Show the before/after schema:
- Before: reviews table with text columns
- After: three tables with relationships
```

### Ending
"The schema redesign felt like starting over, but it made everything else possible. When Claude suggested the aggregated table, I realized I'd been thinking about the problem wrong. Sometimes the 'extra complexity' is actually simplification."

---

## Article 3: "How I Built a Product Spec by Asking Claude Questions (Not Giving Commands)"

### Hook
I didn't tell Claude what to build. I had a conversation with it about what might work. The PRD that emerged was better than anything I would have written alone.

### Key Points

**Traditional Approach**:
- Write complete PRD alone
- Hand it to developer (or Claude)
- Get exactly what you spec'd (which might be wrong)

**Conversational Approach**:
- Start with problem statement
- Ask Claude: "What are the options?"
- Discuss trade-offs together
- Claude asks clarifying questions
- Arrive at solution collaboratively

**Example conversation**:
```
Me: "I want users to test their whiskey tasting ability"
Claude: "Should they select descriptors, or type them in?"
Me: "Select from options"
Claude: "How many options? What happens if they miss one?"
Me: "Good question... let's do 9 options, 3-5 correct"
```

### Claude Collaboration Notes

**What worked well**:
- Claude asked questions I hadn't considered
- "Should this be mobile or desktop?" → Made me think about actual use case
- "How do you handle whiskeys with very few reviews?" → Caught edge case early
- "What happens after they complete the quiz?" → Forced me to think through entire flow

**What I learned**:
- Good AI collaboration is a conversation, not a command
- Claude's questions revealed gaps in my thinking
- Writing alone means you only get your perspective

### Practical Takeaways

1. **Start with "help me think through..."** not "build me..."
2. **Embrace Claude's questions**: They're exposing weaknesses in your plan
3. **Iterate in conversation before writing code**
4. **Document the reasoning**: The PRD should include "why we decided X"

### Screenshot/Example to Include
Show a real conversation snippet where Claude's question changed the approach

### Ending
"The best product decisions came from Claude asking 'why?' or 'what about...?'. I thought I was using AI to speed up documentation. I was actually using it to think better."

---

## Article 4: "The Critical Mistake I Almost Made (And How a Single Question Saved Me)"

### Hook
I was about to throw away half my data. One question from a user made me realize I completely misunderstood how my own product worked.

### Story Arc

**Setup**: Creating descriptor vocabulary for quizzes
**Conflict**: Started filtering out "rare" descriptors (butterscotch, only 1 mention)
**Turning point**: User asked: "Why remove any descriptors at all?"
**Resolution**: Realized rare descriptors are actually valuable for quiz variety

### The Learning Moment

**My thinking (wrong)**:
- Applied traditional data cleaning: remove outliers, deduplicate, normalize
- "Butterscotch only appears once, so it's not useful"
- "Generic terms like 'fruit' are too vague, remove them"
- Goal: Clean, high-quality dataset of ~60 descriptors

**The realization**:
- Quiz pulls correct answers from Whiskey A
- Quiz pulls incorrect answers from Whiskeys B, C, D
- Rare descriptors = unique incorrect answers = more variety
- More descriptors = better quizzes, not worse

**What I learned**:
- Data cleaning isn't always the goal
- Context matters: quiz data ≠ training data ≠ analytics data
- Sometimes messy is better than clean

### Claude's Role

**What Claude did**:
- Initially suggested filtering (same mistake I was making)
- When I explained the quiz mechanics, immediately understood
- Helped re-extract ALL descriptors with no filtering
- Generated the complete 74-descriptor vocabulary

**The meta-lesson**:
- Claude mirrors your assumptions
- If you're thinking about it wrong, Claude will too
- External input (user questions) catch what both you and Claude miss
- AI amplifies your thinking - good and bad

### Practical Takeaways

1. **Question your data cleaning instincts**: Not all data should be "clean"
2. **Understand the full use case**: How will this data actually be used?
3. **Get external feedback early**: Fresh eyes catch blind spots
4. **Claude is a collaborator, not a safety net**: It won't catch your conceptual errors

### Visual to Include
```
Show two vocabulary lists side-by-side:
- Filtered (60 descriptors): Missing variety
- Complete (74 descriptors): Rich and diverse
```

### Ending
"I almost built a worse product because I was following 'best practices' that didn't apply to my use case. The lesson: best practices are contextual. Always ask 'best for what?'"

---

## Article 5: "From Zero to API: Building a Flask Backend with Claude in 4 Hours"

### Hook
I'm not a backend developer. I'd never built an API. With Claude, I had a working Flask backend in one afternoon.

### Key Points

**What I needed**:
- `/api/whiskeys/search` - search endpoint
- `/api/quiz/:id` - quiz generation with correct/incorrect answers
- Database queries with SQLite
- CORS configuration for local frontend

**How Claude helped**:

**Step 1: Setup**
- Generated boilerplate Flask app
- Explained project structure
- Set up virtual environment commands

**Step 2: Database Connection**
- Wrote SQLite connection helper
- Explained connection pooling (for later)
- Handled errors gracefully

**Step 3: Endpoints**
- Wrote search endpoint with fuzzy matching
- **Most complex**: Quiz generation logic
  - Get correct descriptors from aggregated table
  - Get random incorrect descriptors
  - Shuffle and return
- Added CORS headers

**Step 4: Testing**
- Showed me how to test with curl
- Helped debug JSON serialization issues
- Fixed endpoint bugs

### The Tricky Part: Quiz Generation Logic

**My explanation to Claude**:
"For Buffalo Trace nose section, I need 3-5 correct descriptors from the aggregated table, then fill the remaining spots (to reach 9 total) with random descriptors from other whiskeys, but only descriptors that are applicable to 'nose' section."

**Claude's response**:
```python
# Generated this query structure:
# 1. Get correct descriptors
# 2. Count how many we got
# 3. Get random incorrect (9 - correct_count)
# 4. Combine and shuffle
```

**What I had to clarify**:
- "Make sure incorrect descriptors aren't from the same whiskey"
- "Only use descriptors where applicable_sections includes 'nose'"
- Edge cases: What if there are 10 correct descriptors? (Take top 5 by review_count)

### Practical Takeaways

1. **You don't need to be an expert**: Claude fills knowledge gaps
2. **Explain business logic clearly**: Claude handles the code
3. **Iterate on complex logic**: First version never handles all edge cases
4. **Test as you build**: Don't wait until everything is "done"

### Code Example
Show the quiz generation endpoint with annotations

### Ending
"Four hours from 'I've never used Flask' to 'I have a working API.' The magic wasn't that Claude wrote perfect code - it didn't. The magic was that Claude got me 80% of the way there in minutes, so I could spend my time on the 20% that matters."

---

## Article 6: "The Mobile-First Pivot I Almost Missed"

### Hook
I designed the entire app for desktop. Then Claude asked one question that changed everything: "Where will users actually use this?"

### Key Points

**Original assumption**:
- Whiskey enthusiasts are serious people
- Serious people use desktop computers
- Therefore: design for desktop, make it responsive later

**The question**:
Claude: "Will users be at a computer when they're tasting whiskey, or will they have their phone nearby?"

**The realization**:
- Users taste whiskey at home, on the couch
- They have their phone in their hand
- Desktop was the wrong primary experience

**The pivot**:
- Redesigned entire UI for mobile-first
- 44px touch targets (not 32px mouse targets)
- Vertical scrolling (not horizontal layouts)
- Fixed bottom bar for primary action
- Safe area insets for notches

### What Changed

**Before (Desktop-first)**:
- Three-column layout for nose/palate/finish
- Hover states for interactivity
- Mouse-optimized: small buttons, dense information

**After (Mobile-first)**:
- Single-column, swipe between sections
- Touch states (no hover on mobile)
- Large touch targets, generous spacing
- Works great on desktop too (bonus)

### Claude Collaboration Notes

**What Claude provided**:
- Mobile-first Tailwind patterns
- Exact pixel specifications (44px touch targets)
- Safe area inset handling
- Complete responsive breakpoints

**What I had to decide**:
- Which experience is primary?
- How does navigation work on mobile vs desktop?
- What gets hidden on small screens?

### Practical Takeaways

1. **Design for the actual use case**: Where, when, how will this be used?
2. **Mobile-first ≠ mobile-only**: It's about priority
3. **Touch targets matter**: 44px minimum or users will struggle
4. **Claude can help with details**: But you set the strategy

### Visual to Include
Show mobile vs desktop mockups side-by-side

### Ending
"I almost built the wrong thing because I designed for how I *thought* people would use it, not how they *actually* would. Claude's question forced me to confront my assumption. Sometimes the best thing AI can do is make you think."

---

## Article 7: "What I Wish I'd Known Before Starting"

### Hook
Six months, four phases, 18 tasks. Here's what I'd tell my past self.

### Lessons Learned

**1. Start with data, not mockups**
- Data availability shapes what's possible
- 3 months of scraping taught me more than 3 days of brainstorming
- Real data reveals real opportunities

**2. Talk to Claude like a collaborator, not a tool**
- Best results come from conversation
- Ask "what do you think?" not just "do this"
- Claude's questions are valuable

**3. Document as you go, not at the end**
- Case study was easy because I documented each phase
- Captures decisions and reasoning
- Future-you will thank present-you

**4. Iterate in conversation before writing code**
- Exploring options is free
- Changing code is expensive
- Spend time on the design conversation

**5. Don't over-engineer early**
- Started with SQLite, will move to PostgreSQL later
- 30 whiskeys is enough for MVP
- Ship fast, scale later

**6. Manual work is OK for MVP**
- 6-8 hours of manual tagging beats weeks of building automation
- Automation can come in v2
- Focus on validating the concept first

**7. Question your assumptions**
- "Desktop-first" assumption was wrong
- "Filter rare descriptors" assumption was wrong
- Fresh eyes (users, Claude) catch blind spots

**8. The messy middle is where learning happens**
- Schema redesigns feel bad but teach you the domain
- Pivots feel like setbacks but make the product better
- Embrace the iteration

### The Claude-Specific Advice

**Do's**:
- ✅ Explain the business logic, let Claude handle implementation
- ✅ Use Claude to explore options before committing
- ✅ Ask Claude "what am I missing?"
- ✅ Iterate on complex parts (quiz logic took 3 tries)
- ✅ Let Claude write boilerplate, you focus on domain logic

**Don'ts**:
- ❌ Assume Claude catches your conceptual errors (it won't)
- ❌ Accept the first solution without questioning it
- ❌ Skip explaining context (Claude needs to understand the use case)
- ❌ Treat Claude like a code generator (it's better as a thought partner)

### The Honest Part

**What was hard even with Claude**:
- Understanding my own domain (whiskey tasting)
- Making product decisions (what to build, what to cut)
- Manual data work (tagging reviews)
- Testing and iteration

**What Claude made easy**:
- Writing scrapers, APIs, database schemas
- Exploring technical options
- Generating boilerplate
- Explaining concepts I didn't understand

**The real value**:
- Speed: Months → weeks
- Learning: Claude teaches as it builds
- Quality: Iterating is fast, so you can try more approaches
- Confidence: You can tackle technical challenges you couldn't before

### Ending
"Six months ago, I had an idea and no backend experience. Today, I have a working API, a database with 2000+ reviews, and an MVP almost ready to ship. Claude didn't do it for me - it did it *with* me. That's the difference."

---

## Article 8 (Bonus): "The Complete Tech Stack of a One-Person AI-Assisted Startup"

### Hook
Here's every piece of technology I used to build this, and why I chose each one.

### The Stack

**Data Collection**:
- Python + BeautifulSoup (web scraping)
- macOS cron jobs (automation)
- SQLite (storage)
- **Why**: Free, simple, runs on my laptop

**Backend**:
- Flask (Python web framework)
- SQLite → PostgreSQL (database)
- Railway (hosting)
- **Why**: Python for everything = one language to learn

**Frontend**:
- React + Vite (framework + build tool)
- Tailwind CSS (styling)
- Vercel (hosting)
- **Why**: Modern, fast, free tier

**Design**:
- Josefin Sans (Google Fonts)
- Heroicons (icons)
- Figma (mockups - actually just described to Claude)
- **Why**: Free, good enough

**Development Tools**:
- Claude (obviously)
- VS Code (editor)
- GitHub (version control)
- **Why**: Standard tools

### Cost Breakdown

**Monthly costs**:
- Claude subscription: $20
- Domain: $12/year = $1/month
- Hosting (Railway + Vercel free tier): $0
- **Total: ~$21/month**

**Time investment**:
- Phase 1 (Scraping): 2 weeks
- Phase 2 (Database): 1 week
- Phase 3 (Planning): 1 week
- Phase 4 (Building): 3-4 weeks (in progress)
- **Total: ~2 months part-time**

### What I'd Change

**If starting today**:
- ✅ Same stack (it works)
- ✅ Maybe use Supabase instead of Railway (PostgreSQL + API)
- ✅ Consider Next.js instead of Vite (SSR benefits)
- ✅ Start with PostgreSQL, skip SQLite step

**What I wouldn't change**:
- Python for data/backend
- React for frontend
- Mobile-first approach
- Building scraper first

### For Different Projects

**If building a SaaS**:
- Add: Authentication (Auth0 or Clerk)
- Add: Payment processing (Stripe)
- Add: Analytics (PostHog or Plausible)

**If building an AI app**:
- Add: Vector database (Pinecone or Weaviate)
- Add: LLM API (Anthropic or OpenAI)
- Consider: LangChain for orchestration

**If building mobile-first**:
- Consider: React Native instead of web
- Consider: Expo for easier mobile dev
- Keep: API-first architecture

### Ending
"The best stack is the one you can ship with. I chose boring technology that works, learned one language deeply (Python), and used Claude to fill gaps. Two months later, I have something real."

---

## Meta-Notes for Later

### Series Structure
- **Article 1-3**: Foundation (data, database, planning)
- **Article 4**: The learning moment (most important)
- **Article 5-6**: Building (backend, frontend)
- **Article 7**: Reflection and lessons
- **Article 8**: Practical details

### Themes to Weave Throughout
1. **Collaboration over automation**: Claude as partner, not tool
2. **Iteration is normal**: First version is never right
3. **Context matters**: Best practices are contextual
4. **Conversation over commands**: Ask, don't just tell
5. **Ship fast, scale later**: MVP mindset

### Writing Style
- First person, conversational
- Honest about mistakes
- Code examples are short and annotated
- Specific numbers (6 hours, 74 descriptors, 30 whiskeys)
- End each article with actionable takeaway

### Promotion Strategy
- Post one per week for 8 weeks
- Tag: #BuildInPublic #AI #SoftwareDevelopment #Claude
- Engage in comments
- Cross-post to Twitter (threads)
- Maybe turn into a long-form blog post later

---

## Article Ideas That Didn't Make the Cut (But Could)

**"How I Used Claude to Learn Backend Development Without Taking a Course"**
- Learning by doing with AI assistance
- Traditional learning vs AI-assisted learning

**"The Whiskey Tasting App Nobody Asked For (And Why I'm Building It Anyway)"**
- Finding niches
- Building for yourself first

**"Why I Chose Boring Technology (And You Should Too)"**
- FOMO in tech stacks
- Proven tools > shiny new things

**"The 80/20 of Working with AI: What to Delegate, What to Own"**
- When to use Claude vs when to DIY
- Building judgment about AI capabilities

---

## Next Steps (When Ready to Write)

1. **Choose 1-2 articles to write first**: Test the format and tone
2. **Get feedback**: Share with trusted colleagues
3. **Refine**: Adjust based on feedback
4. **Commit to schedule**: One per week for 8 weeks
5. **Track engagement**: See what resonates
6. **Adapt**: Change direction if something isn't working

**Estimated time per article**: 2-3 hours writing + editing
**Total time investment**: 16-24 hours for full series
**Potential reach**: Could become a definitive resource on AI-assisted development

# Git & Production Readiness Guide

**Date**: January 29, 2026
**Purpose**: Learn proper Git workflow and production deployment preparation

---

## 🎯 Learning Objectives

By the end of this guide, you'll understand:
- Why version control matters
- What should (and shouldn't) be committed to Git
- How to prepare code for production
- Best practices for collaborating with code
- Security considerations for public repositories

---

## 📚 Part 1: Understanding Version Control

### What is Git?

Git is like **Time Travel for Code**. It:
- Tracks every change you make
- Lets you revert mistakes
- Enables collaboration with others
- Serves as backup for your code
- Required for deployment to Railway/Vercel

### What is GitHub?

GitHub is:
- A hosting service for Git repositories
- Like Google Drive, but for code
- Where you'll deploy from (Railway and Vercel connect to GitHub)
- Your public portfolio (if you choose)

---

## 🔐 Part 2: Security First - The .gitignore File

### Why .gitignore Matters

**Critical**: Some files should NEVER be committed to Git:

#### ❌ NEVER Commit These:

1. **Secrets and Credentials**
   ```
   .env
   .env.local
   API_KEY=abc123  ← If this gets committed, someone can steal it!
   ```

2. **Virtual Environments** (venv/, node_modules/)
   - Why? They're HUGE (100MB+) and regenerated from requirements.txt
   - Your repo would be 100x larger unnecessarily

3. **Personal IDE Settings**
   - .vscode/, .idea/
   - Every developer has different preferences

4. **Logs and Cache**
   - Temporary data, not needed in repo
   - Can contain sensitive information

### Our Special Case: Databases

**Normally**: Databases are NOT committed to Git
- They can be huge (1GB+)
- User data changes constantly
- Security risk (user emails, passwords)

**Our Case**: We ARE committing our databases because:
- Small (only 16MB total)
- Static reference data (whiskey reviews, not user data)
- Makes deployment simpler
- No sensitive information

**Rule of Thumb**:
- Static data < 50MB → Can commit
- User-generated data → NEVER commit
- > 100MB files → GitHub rejects them anyway

---

## 📋 Part 3: What Gets Committed?

### ✅ DO Commit:

**Source Code**
- `*.py` - Python files
- `*.js`, `*.jsx` - JavaScript/React files
- `*.css` - Stylesheets

**Documentation**
- `README.md` - First thing people see
- `DEPLOYMENT.md` - How to deploy
- `CHANGELOG.md` - Version history
- All docs in `/docs/` folder

**Dependencies**
- `requirements.txt` - Python packages
- `package.json` - Node packages
- These let others recreate your environment

**Configuration**
- `Procfile` - Railway needs this
- `vercel.json` - Vercel configuration
- `.gitignore` - What to ignore

**Our Static Databases** (special case)
- `databases/whiskey_production.db`
- `databases/whiskey_reviews.db`

**Scripts**
- `scripts/verify_deployment.sh`
- Build and deployment automation

### ❌ DON'T Commit:

**Generated Files**
- `__pycache__/` - Python cache
- `frontend/dist/` - Build output
- `*.pyc` - Compiled Python

**Dependencies**
- `venv/` - Virtual environment
- `node_modules/` - Node packages
- Regenerated from requirements.txt/package.json

**Secrets**
- `.env` - Environment variables
- API keys, passwords, tokens
- Anything with "secret" or "credential" in the name

**Logs and Temporary Files**
- `*.log` - Log files
- `*.tmp` - Temporary files
- `backups/` - Database backups

**Personal Files**
- `.DS_Store` - Mac OS metadata
- `Thumbs.db` - Windows thumbnails

---

## 🚀 Part 4: Git Workflow (Step by Step)

### Step 1: Initialize Git Repository

```bash
# Navigate to your project
cd /path/to/whiskey-scraper

# Initialize Git (creates .git folder)
git init

# Verify it worked
git status
```

**What this does**: Creates a hidden `.git` folder that tracks all changes

### Step 2: Configure Git (First Time Only)

```bash
# Set your name (shows on commits)
git config --global user.name "Mike"

# Set your email (GitHub account email)
git config --global user.email "angoliam@gmail.com"

# Check configuration
git config --list
```

**Why**: Every commit is "signed" with your name/email

### Step 3: Stage Files for Commit

```bash
# See what files exist
git status

# Stage specific files
git add README.md
git add app.py
git add databases/whiskey_production.db

# OR stage everything (be careful!)
git add .

# See what's staged
git status
```

**What "staging" means**:
- Git has a 3-step process: Working → Staging → Committed
- Staging lets you review what will be committed
- Like putting items in a shopping cart before checkout

### Step 4: Commit Changes

```bash
# Commit with a descriptive message
git commit -m "Initial commit: Production-ready whiskey training app"

# See commit history
git log --oneline
```

**Good Commit Messages**:
- ✅ "Add user authentication with JWT tokens"
- ✅ "Fix bug in quiz generation for single-review whiskeys"
- ✅ "Update database paths to /databases/ folder"

**Bad Commit Messages**:
- ❌ "stuff"
- ❌ "fixes"
- ❌ "asdf"

**Why**: You'll thank yourself later when looking for when a bug was introduced

### Step 5: Create GitHub Repository

**Option A: Using GitHub Website**
1. Go to github.com
2. Click "New Repository"
3. Name: `whiskey-training-app`
4. Public or Private (your choice)
5. DON'T initialize with README (you already have one)
6. Create repository

**Option B: Using GitHub CLI** (if installed)
```bash
gh repo create whiskey-training-app --public --source=. --remote=origin
```

### Step 6: Push to GitHub

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR-USERNAME/whiskey-training-app.git

# Push code to GitHub
git push -u origin main

# Future pushes (after first time)
git push
```

**What this does**: Uploads your code to GitHub's servers

---

## 🔍 Part 5: Before You Push - Security Checklist

### Run This Checklist BEFORE First Push:

```bash
# 1. Check for accidentally staged .env files
git status | grep -i "\.env"
# Should return nothing!

# 2. Check file sizes (GitHub rejects > 100MB)
git ls-files | xargs ls -lh | sort -k5 -hr | head -20

# 3. Verify .gitignore is working
git status
# Should NOT see: venv/, node_modules/, __pycache__/

# 4. Search for hardcoded secrets in code
grep -r "password" *.py
grep -r "api_key" *.py
grep -r "secret" *.py
# Should return nothing or only commented code

# 5. Check what will be pushed
git log --stat
```

### Common Security Mistakes:

**❌ Mistake 1: Committing .env file**
```bash
# BAD - .env contains secrets
git add .env  # ← NEVER DO THIS
git commit -m "Add environment variables"
```

**✅ Solution:**
```bash
# Good - .gitignore excludes .env
# Create .env.example instead:
echo "API_KEY=your_key_here" > .env.example
git add .env.example
```

**❌ Mistake 2: Hardcoded secrets in code**
```python
# BAD - Secret visible in code
API_KEY = "sk_live_abc123xyz"

# GOOD - Secret from environment variable
import os
API_KEY = os.getenv("API_KEY")
```

**❌ Mistake 3: Committing large files**
```bash
# This will fail on GitHub
git add huge_database.db  # (500MB)
# Error: file exceeds 100MB limit
```

---

## 📦 Part 6: Preparing for Production

### Files to Create Before Deployment

#### 1. Procfile (for Railway)

```bash
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

**What it does**: Tells Railway how to start your app

#### 2. runtime.txt (optional)

```
python-3.11.0
```

**What it does**: Specifies Python version

#### 3. .env.example (for documentation)

```bash
# Example environment variables
# Copy to .env and fill in your values

FLASK_ENV=production
FLASK_APP=app.py
DB_PATH=/app/databases/whiskey_production.db
CORS_ORIGINS=https://yourapp.com
```

**What it does**: Documents required environment variables without exposing secrets

### Update requirements.txt

```bash
# Make sure it includes production dependencies
pip freeze > requirements.txt

# Verify gunicorn is there
grep gunicorn requirements.txt
```

---

## 🔄 Part 7: Common Git Workflows

### Daily Development Workflow

```bash
# 1. Start working
git status  # See what's changed

# 2. Make changes to code
# (edit files in your editor)

# 3. Test changes locally
python3 app.py
# Make sure it works!

# 4. Stage and commit
git add app.py
git commit -m "Add rate limiting to API endpoints"

# 5. Push to GitHub
git push
```

### Fixing a Mistake

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo changes in a file (before commit)
git checkout -- filename.py

# See what changed in a file
git diff app.py
```

### Branching (Advanced)

```bash
# Create feature branch
git checkout -b feature/add-user-auth

# Make changes, commit
git add .
git commit -m "Add user authentication"

# Switch back to main
git checkout main

# Merge feature
git merge feature/add-user-auth
```

**Why use branches?**
- Main branch stays stable
- Test features in isolation
- Can work on multiple features simultaneously

---

## 🎯 Part 8: Production Readiness Checklist

Before deploying, verify:

### Code Quality
- [ ] No `print()` debug statements (use logging instead)
- [ ] No commented-out code blocks
- [ ] No hardcoded passwords or API keys
- [ ] Error handling in place
- [ ] Code is documented

### Security
- [ ] `.env` not committed
- [ ] `.gitignore` properly configured
- [ ] No secrets in code
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled

### Dependencies
- [ ] `requirements.txt` up to date
- [ ] `package.json` up to date
- [ ] No unnecessary dependencies
- [ ] All dependencies have version numbers

### Documentation
- [ ] `README.md` explains what project does
- [ ] `DEPLOYMENT.md` has deployment steps
- [ ] `CHANGELOG.md` tracks versions
- [ ] API endpoints documented

### Testing
- [ ] App runs locally without errors
- [ ] All endpoints tested
- [ ] Frontend connects to backend
- [ ] No console errors

---

## 📊 Part 9: Understanding Your Repository

### Repository Size

```bash
# Check total repo size
du -sh .git

# Check size by file type
git ls-files | xargs wc -l | sort -n
```

**Our Repository**:
- Source code: ~1,500 lines
- Databases: 16MB
- Documentation: ~3,000 lines
- **Total**: ~20MB (very reasonable)

**Good to know**:
- GitHub has 100MB file limit
- 1GB repository size limit
- Our repo is well within limits

### What's Being Tracked

```bash
# See all tracked files
git ls-files

# See ignored files
git status --ignored

# See last 10 commits
git log --oneline -10
```

---

## 🚦 Part 10: Git Best Practices

### DO:
✅ Commit often (every logical change)
✅ Write descriptive commit messages
✅ Pull before you push (if collaborating)
✅ Test before committing
✅ Keep commits focused (one feature per commit)
✅ Use .gitignore properly
✅ Review staged changes before committing

### DON'T:
❌ Commit secrets or credentials
❌ Commit generated files (dist/, __pycache__)
❌ Commit large binary files
❌ Use generic commit messages ("update", "fix")
❌ Commit broken code to main branch
❌ Force push to shared branches

---

## 🎓 Part 11: Learning Resources

### Git Basics
- GitHub Guides: https://guides.github.com/
- Git Handbook: https://guides.github.com/introduction/git-handbook/
- Interactive Git: https://learngitbranching.js.org/

### Troubleshooting
- Git Flight Rules: https://github.com/k88hudson/git-flight-rules
- Oh Shit, Git!: https://ohshitgit.com/

### Best Practices
- Conventional Commits: https://www.conventionalcommits.org/
- Git Style Guide: https://udacity.github.io/git-styleguide/

---

## 🔧 Part 12: Common Issues and Solutions

### Issue: "Git not found"
```bash
# Install Git (Mac)
brew install git

# Install Git (Linux)
sudo apt-get install git
```

### Issue: "Permission denied (publickey)"
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "angoliam@gmail.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output and add at github.com/settings/keys
```

### Issue: "Large file warning"
```bash
# Remove large file from history (if accidentally committed)
git rm --cached large_file.db
git commit -m "Remove large file"
```

### Issue: "Accidentally committed .env"
```bash
# Remove from repository but keep local
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Remove .env from repository"

# Then rotate all secrets in that .env file!
```

---

## 🎯 Summary: Your Action Items

### Right Now:
1. **Initialize Git**: `git init`
2. **Verify .gitignore**: Check what will/won't be committed
3. **Stage files**: `git add .`
4. **First commit**: `git commit -m "Initial commit: Production-ready app"`
5. **Create GitHub repo**: On github.com
6. **Push code**: `git push -u origin main`

### Before Deployment:
1. **Security audit**: No secrets committed
2. **Test locally**: Everything works
3. **Update docs**: README accurate
4. **Create Procfile**: Railway needs this
5. **Verify requirements.txt**: All dependencies listed

### After Deployment:
1. **Tag release**: `git tag v1.0.0`
2. **Push tags**: `git push --tags`
3. **Document deployment**: Note production URL in README

---

**Next Steps**: Let's actually run these commands! I'll walk you through each one.

---

*This guide is part of the Whiskey Sensory Training App documentation.*

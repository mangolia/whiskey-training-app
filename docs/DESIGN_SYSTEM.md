# Whiskey Sensory Training App - Design System

## Based on Unspoken Distilling Brand Guidelines

**Last Updated**: January 23, 2026
**Status**: FINALIZED - Ready for Implementation
**Source**: UNSPOKEN_BrandGuidelines_2023.pdf

---

## ✅ Design Decisions (FINAL)

### 1. Color Palette

**PRIMARY COLORS** (From Unspoken Brand Guidelines):
```css
--unspoken-navy: #2a3c93      /* Primary brand color */
--unspoken-white: #fbfbf5     /* Off-white background */
--emerald: #008159            /* Accent green */
--dark-navy: #1b236a          /* Darker accent */
```

**UI STATE COLORS** (For quiz interactions):
```css
--selected: #3B82F6           /* Blue - selected state */
--correct: #10B981            /* Green - correct answer */
--incorrect: #EF4444          /* Red - incorrect answer */
--missed: #F59E0B             /* Amber - missed correct */
```

**NEUTRAL COLORS**:
```css
--gray-50: #F9FAFB
--gray-100: #F3F4F6
--gray-200: #E5E7EB
--gray-500: #6B7280
--gray-900: #111827
```

**COLOR USAGE RATIOS** (Per Unspoken Guidelines):
- 50% Navy (#2a3c93)
- 40% White/Off-white (#fbfbf5)
- 10% Accent (Emerald #008159 + Gold)

---

### 2. Typography

**PRIMARY FONT: Josefin Sans** (Open Source - Google Fonts)
- **Usage**: 80% of all text (headings, body, UI)
- **Weights**: Light (300), Regular (400), Semibold (600), Bold (700)
- **Why**: Free, web-optimized, clean sans-serif from Unspoken guidelines
- **Google Fonts URL**: https://fonts.google.com/specimen/Josefin+Sans

**SECONDARY FONT: Operetta** (Serif - Licensed)
- **Usage**: 20% of text (accents, special headings)
- **Note**: For MVP, use serif fallback since Operetta requires licensing
- **Fallback**: Georgia, 'Times New Roman', serif

**FONT RATIO**: 80% sans-serif / 20% serif (per Unspoken guidelines)

**Typography Scale (Mobile-First):**
```css
/* Mobile (320px - 768px) */
--text-xs: 12px      /* Captions, hints */
--text-sm: 14px      /* Body text, secondary info */
--text-base: 16px    /* Primary body text */
--text-lg: 18px      /* Subheadings */
--text-xl: 20px      /* Page titles */
--text-2xl: 24px     /* Large headings (Sense titles) */

/* Desktop (1024px+) */
--text-xs: 13px
--text-sm: 15px
--text-base: 16px
--text-lg: 20px
--text-xl: 24px
--text-2xl: 30px
```

---

### 3. Spacing & Layout

**SPACING SCALE** (Based on 4px baseline):
```css
--spacing-1: 4px
--spacing-2: 8px
--spacing-3: 12px
--spacing-4: 16px     /* Standard padding */
--spacing-5: 20px
--spacing-6: 24px     /* Logo margin per guidelines */
--spacing-8: 32px
--spacing-12: 48px
--spacing-16: 64px
```

**LOGO SPACING** (Per Unspoken Guidelines):
- Minimum margin: 0.125" (12px)
- Recommended margin: 0.25" (24px)

**CONTAINER WIDTHS**:
```css
--container-mobile: 100% (with 16px padding)
--container-tablet: 640px
--container-desktop: 900px
```

---

### 4. Border Radius

```css
--radius-sm: 8px      /* Small elements */
--radius-md: 12px     /* Default (buttons, inputs) */
--radius-lg: 16px     /* Cards, option cards */
--radius-xl: 24px     /* Large containers */
--radius-full: 9999px /* Rounded pills, badges */
```

**Standard**: 12px default, 16px for quiz option cards (per PRD)

---

### 5. Shadows & Elevation

**SHADOW SYSTEM**:
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)
```

**USAGE**:
- Cards: shadow-md
- Fixed headers/footers: shadow-lg
- Modals/overlays: shadow-xl
- Hover states: shadow-lg

---

### 6. Icons

**ICON LIBRARY**: Heroicons (Free, Tailwind-designed)
- **Style**: Outline (24px) for most UI
- **Style**: Solid (20px) for smaller elements
- **Colors**: Inherit text color or use brand navy
- **URL**: https://heroicons.com

**COMMON ICONS NEEDED**:
- Search (magnifying glass)
- Back arrow (left chevron)
- Checkmark (correct answer)
- X (incorrect answer)
- Circle (missed answer)
- Loading spinner

---

## Complete Tailwind Config

```javascript
// tailwind.config.js
import defaultTheme from 'tailwindcss/defaultTheme'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Unspoken Brand Colors
        'unspoken': {
          navy: '#2a3c93',
          'dark-navy': '#1b236a',
          white: '#fbfbf5',
          emerald: '#008159',
        },
        // UI State Colors
        primary: '#2a3c93',    // Unspoken Navy
        selected: '#3B82F6',   // Blue for selected state
        success: '#10B981',    // Green for correct
        error: '#EF4444',      // Red for incorrect
        warning: '#F59E0B',    // Amber for missed
        accent: '#008159',     // Emerald
      },
      fontFamily: {
        sans: ['Josefin Sans', ...defaultTheme.fontFamily.sans],
        serif: ['Georgia', 'Times New Roman', ...defaultTheme.fontFamily.serif],
      },
      fontSize: {
        // Mobile-first sizes
        xs: ['12px', { lineHeight: '16px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['16px', { lineHeight: '24px' }],
        lg: ['18px', { lineHeight: '28px' }],
        xl: ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '36px' }],
      },
      spacing: {
        'logo-margin': '24px',  // Per Unspoken guidelines
      },
      borderRadius: {
        DEFAULT: '12px',
        'lg': '16px',
        'xl': '24px',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(42, 60, 147, 0.1)',
        'card-hover': '0 10px 15px -3px rgba(42, 60, 147, 0.15)',
        'bottom-bar': '0 -4px 6px -1px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'slide-in': 'slideIn 300ms ease-out',
        'scale-in': 'scaleIn 150ms ease-out',
        'fade-in': 'fadeIn 200ms ease-out',
        'pulse-subtle': 'pulseSubtle 2s ease-in-out infinite',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(100%)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: 0 },
          '100%': { transform: 'scale(1)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.8 },
        },
      },
    },
  },
  plugins: [],
}
```

---

## Component Patterns

### Button Styles

**Primary Button:**
```jsx
className="bg-unspoken-navy text-white px-6 py-3 rounded-lg
           font-semibold text-base shadow-md hover:shadow-lg
           active:scale-95 transition-all duration-150
           disabled:opacity-50 disabled:cursor-not-allowed
           min-h-[44px] touch-manipulation"
```

**Secondary Button:**
```jsx
className="bg-white text-unspoken-navy border-2 border-unspoken-navy
           px-6 py-3 rounded-lg font-semibold text-base
           hover:bg-unspoken-white active:scale-95
           transition-all duration-150 min-h-[44px]"
```

**Submit Button (Quiz):**
```jsx
className="w-full bg-unspoken-navy text-white px-8 py-4 rounded-lg
           font-bold text-lg shadow-lg hover:bg-unspoken-dark-navy
           active:scale-98 transition-all duration-150
           disabled:bg-gray-300 disabled:text-gray-500
           h-[52px] touch-manipulation"
```

---

### Option Card Styles

**Default State:**
```jsx
className="bg-white border-2 border-gray-200 rounded-lg p-4
           shadow-card hover:shadow-card-hover cursor-pointer
           active:scale-98 transition-all duration-150
           min-h-[88px] flex items-center justify-center
           touch-manipulation select-none"
```

**Selected State:**
```jsx
className="bg-selected border-2 border-selected text-white
           rounded-lg p-4 shadow-md
           min-h-[88px] flex items-center justify-between
           relative"
// Add checkmark icon on right
```

**Correct (Post-Submit):**
```jsx
className="bg-success border-2 border-success text-white
           rounded-lg p-4 shadow-md
           min-h-[88px] flex items-center justify-between"
// Add ✓ icon
```

**Incorrect (Post-Submit):**
```jsx
className="bg-error border-2 border-error text-white
           rounded-lg p-4 shadow-md
           min-h-[88px] flex items-center justify-between"
// Add ✗ icon
```

**Missed (Post-Submit):**
```jsx
className="bg-gray-50 border-2 border-warning text-gray-900
           rounded-lg p-4 shadow-sm
           min-h-[88px] flex items-center justify-between"
// Add ○ icon
```

---

### Search Bar

```jsx
className="w-full px-4 py-3 text-base border-2 border-gray-200
           rounded-lg focus:border-unspoken-navy focus:ring-2
           focus:ring-unspoken-navy focus:ring-opacity-20
           placeholder:text-gray-400 bg-white
           h-[52px] touch-manipulation"
placeholder="Search for a whiskey..."
```

---

### Search Results

```jsx
className="bg-white border border-gray-200 rounded-lg p-4
           hover:bg-unspoken-white hover:border-unspoken-navy
           cursor-pointer active:scale-98 transition-all duration-150
           min-h-[56px] touch-manipulation"
```

---

## Page Layouts

### Homepage

**Container:**
```jsx
<div className="min-h-screen bg-unspoken-white">
  <div className="max-w-2xl mx-auto px-4 py-8">
    <header className="text-center mb-8">
      <h1 className="font-bold text-2xl text-unspoken-navy mb-2">
        Whiskey Sensory Training
      </h1>
      <p className="text-sm text-gray-600">
        Test your palate against professional reviews
      </p>
    </header>

    <SearchBar />
    <SearchResults />
  </div>
</div>
```

---

### Quiz Page

**Fixed Header (Mobile):**
```jsx
<header className="fixed top-0 left-0 right-0 h-[60px]
                   bg-white border-b border-gray-200
                   shadow-md z-50 flex items-center px-4">
  <BackButton />
  <WhiskeyName className="truncate flex-1 text-center text-sm" />
  <ProgressDots />
</header>
```

**Fixed Bottom Bar (Mobile):**
```jsx
<div className="fixed bottom-0 left-0 right-0 h-[72px]
                bg-white border-t border-gray-200 shadow-bottom-bar
                z-50 flex items-center justify-center px-4
                pb-safe">
  <SubmitButton />
</div>
```

**Content Area:**
```jsx
<main className="pt-[60px] pb-[72px] px-4 min-h-screen bg-unspoken-white">
  <SenseTitle className="text-2xl font-bold text-center text-unspoken-navy mb-2" />
  <HintText className="text-sm text-gray-600 text-center mb-6" />

  <OptionGrid className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8" />
</main>
```

---

## Mobile-Specific Tokens

### Touch Targets

```css
--touch-min: 44px     /* WCAG minimum */
--touch-comfortable: 56px   /* Search results */
--touch-large: 88px   /* Quiz option cards */
```

### Safe Areas (iOS)

```css
padding-bottom: env(safe-area-inset-bottom);
padding-top: env(safe-area-inset-top);
```

### Prevent Zoom/Unwanted Touch Behaviors

```css
touch-action: manipulation;  /* Prevents double-tap zoom */
user-select: none;           /* Prevents text selection on cards */
-webkit-tap-highlight-color: transparent;  /* Removes iOS tap flash */
```

---

## Responsive Breakpoints

```javascript
// tailwind.config.js
screens: {
  'sm': '375px',   // iPhone SE baseline
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
}
```

**Mobile-First Approach:**
```jsx
// Default styles = mobile (320px+)
<div className="p-4 grid grid-cols-2 gap-4">

// Tablet adjustments
<div className="md:p-8 md:grid-cols-3 md:gap-6">

// Desktop adjustments
<div className="lg:max-w-4xl lg:mx-auto">
```

---

## Animations & Transitions

### Standard Transitions

```css
transition-all duration-150 ease-out    /* Quick interactions */
transition-all duration-300 ease-in-out /* Page transitions */
```

### Specific Animations

**Card Selection:**
```jsx
active:scale-[0.98] transition-transform duration-150
```

**Sense Navigation:**
```jsx
animate-slide-in  /* 300ms slide from right */
```

**Results Reveal (Stagger):**
```jsx
{options.map((option, index) => (
  <OptionCard
    key={option}
    style={{ animationDelay: `${index * 100}ms` }}
    className="animate-fade-in"
  />
))}
```

**Button Pulse (Enabled State):**
```jsx
animate-pulse-subtle  /* Subtle 2s pulse on submit button */
```

---

## Icon Usage

**Heroicons Implementation:**

```jsx
import {
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  CheckIcon,
  XMarkIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

// Search icon
<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />

// Back button
<ChevronLeftIcon className="h-6 w-6 text-unspoken-navy" />

// Correct answer
<CheckIcon className="h-5 w-5 text-white" />

// Incorrect answer
<XMarkIcon className="h-5 w-5 text-white" />

// Loading spinner
<ArrowPathIcon className="h-5 w-5 animate-spin" />
```

---

## Implementation Checklist

### Setup Tasks
- [x] ✅ Review Unspoken brand guidelines
- [x] ✅ Define color palette from brand colors
- [x] ✅ Choose typography (Josefin Sans)
- [x] ✅ Define spacing scale
- [x] ✅ Define border radius standards
- [x] ✅ Choose icon library (Heroicons)
- [ ] Install Josefin Sans from Google Fonts
- [ ] Install Heroicons package
- [ ] Create Tailwind config with tokens
- [ ] Set up CSS custom properties
- [ ] Test on mobile device

### Component Development
- [ ] Create Button component with variants
- [ ] Create OptionCard component with states
- [ ] Create SearchBar component
- [ ] Create Header/Footer components
- [ ] Create ProgressIndicator component
- [ ] Test all components on mobile

---

## Google Fonts Integration

**Add to index.html:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
```

**Or install via npm:**
```bash
npm install @fontsource/josefin-sans
```

```javascript
// main.jsx
import '@fontsource/josefin-sans/300.css'  // Light
import '@fontsource/josefin-sans/400.css'  // Regular
import '@fontsource/josefin-sans/600.css'  // Semibold
import '@fontsource/josefin-sans/700.css'  // Bold
```

---

## Package Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "@heroicons/react": "^2.1.0",
    "@fontsource/josefin-sans": "^5.0.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "vite": "^5.0.0"
  }
}
```

---

## Design Tokens Summary

**Colors**: Unspoken Navy (#2a3c93) primary, Emerald (#008159) accent
**Typography**: Josefin Sans (Google Fonts, free)
**Spacing**: 24px logo margins, 16px standard padding
**Border Radius**: 12px default, 16px for cards
**Shadows**: Tailwind defaults (shadow-md for cards)
**Icons**: Heroicons (outline style, 24px)
**Ratio**: 50% navy, 40% white, 10% accent (per guidelines)

---

## Brand Compliance Notes

**From Unspoken Guidelines:**
- ✅ Use Josefin Sans as primary open-source font
- ✅ 80% sans-serif, 20% serif ratio
- ✅ Navy (#2a3c93) as primary brand color
- ✅ Emerald (#008159) as accent
- ✅ 24px margins around branded elements
- ✅ 50% navy, 40% white, 10% accent color ratio
- ✅ Clean, non-busy backgrounds
- ✅ No script/ornamental fonts

**Additional UI Colors** (Not in brand guide, added for functionality):
- Blue (#3B82F6) for interactive selected state
- Green (#10B981) for correct answers
- Red (#EF4444) for incorrect answers
- Amber (#F59E0B) for warnings/missed items

These additions complement but don't replace the brand colors.

---

**Status**: ✅ All design decisions finalized based on Unspoken Distilling brand guidelines
**Next Task**: Task 2 - Database Initialization

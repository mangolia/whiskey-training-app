/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Rich Navy Blue
        'primary': '#2a3c93',
        'primary-hover': '#1e2d6e',
        'primary-foreground': '#ffffff',

        // Secondary - Navy Dark
        'secondary': '#1a2456',
        'secondary-dark': '#0f1533',
        'secondary-foreground': '#ffffff',

        // Background - Textured Cream/Aged Paper
        'background': '#f5efe6',
        'background-alt': '#ede5d8',

        // Accent - Brushed Gold
        'accent': '#d4af37',
        'accent-foreground': '#2C2C2C',

        // Neutrals
        'neutral-dark': '#2C2C2C',
        'neutral-light': '#d9d1c5',
        'warm-gray': '#d9d1c5',

        // Success - Gold (for correct answers)
        'success': '#d4af37',
        'success-foreground': '#1a2456',

        // Error - Deep Red
        'error': '#8b3a3a',
        'error-foreground': '#ffffff',

        // Card
        'card': '#fffef9',
        'card-foreground': '#2C2C2C',
        'card-border': '#d4af37',

        // Text
        'text-secondary': 'rgba(44, 44, 44, 0.7)',

        // Legacy aliases (for compatibility)
        'unspoken-navy': '#2a3c93',
        'unspoken-navy-dark': '#1e2d6e',
        'unspoken-gold': '#d4af37',
      },
      fontFamily: {
        'sans': ['Josefin Sans', 'system-ui', 'sans-serif'],
        'heading': ['Josefin Sans', 'system-ui', 'sans-serif'], // Using Josefin for both
      },
      borderRadius: {
        'sm': '4px',
        'DEFAULT': '10px',
        'md': '10px',
        'lg': '16px',
        'xl': '24px',
      },
      boxShadow: {
        'card': '0px 4px 12px rgba(42, 60, 147, 0.15)',
        'button': '0px 4px 16px rgba(212, 175, 55, 0.3)',
        'focus': '0 0 0 3px rgba(212, 175, 55, 0.3)',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      }
    },
  },
  plugins: [],
}

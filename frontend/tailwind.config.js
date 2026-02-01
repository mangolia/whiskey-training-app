/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Unspoken Brand Colors
        'unspoken-navy': '#2a3c93',
        'unspoken-navy-light': '#3d52b8',
        'unspoken-navy-dark': '#1f2d6f',
        'unspoken-gold': '#d4af37',
        'unspoken-cream': '#f5f1e8',
      },
      fontFamily: {
        'sans': ['Josefin Sans', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'DEFAULT': '12px',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(42, 60, 147, 0.1), 0 2px 4px -1px rgba(42, 60, 147, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(42, 60, 147, 0.2), 0 4px 6px -2px rgba(42, 60, 147, 0.1)',
      }
    },
  },
  plugins: [],
}

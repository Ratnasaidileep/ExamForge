/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#3730A3', // Indigo primary
          teal: '#0F766E',    // Teal accent
          bg: '#F8FAFC',      // Slate background
          dark: '#1E293B',    // Dark surface
          text: '#0F172A',    // Main text
          muted: '#64748B',   // Secondary text
          border: '#E2E8F0',  // Borders
          success: '#15803D', // Success
          warning: '#B45309', // Warning
          error: '#B91C1C',   // Error
          info: '#1D4ED8',    // Info
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

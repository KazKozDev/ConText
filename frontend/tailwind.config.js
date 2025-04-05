/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        'background-light': '#FFFFFF',
        'background-dark': '#1F2937',
        secondary: {
          DEFAULT: '#718096',
          light: '#A0AEC0',
          dark: '#4A5568',
        },
        text: {
          light: '#1a1a1a',
          dark: '#f5f5f5',
        },
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      maxHeight: {
        '1/2': '50vh',
        '3/4': '75vh',
      },
    },
  },
  plugins: [],
}


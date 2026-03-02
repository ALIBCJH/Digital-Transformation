/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#00A8E8', // Cyan blue from screenshot
          dark: '#007EA7',
        },
        secondary: {
          DEFAULT: '#5C6B73', // Gray from screenshot
          light: '#9DB4C0',
        },
        dark: {
          DEFAULT: '#253237', // Dark background from screenshot
          light: '#2D3E45',
        },
      },
    },
  },
  plugins: [],
}

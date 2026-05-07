/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'gov-blue': '#1351B4',
        'gov-dark': '#071D41',
        'gov-green': '#168821',
        'gov-yellow': '#FFCD07',
        'gov-gray': '#F8F8F8',
        'gov-border': '#D4D4D4',
        'gov-text': '#1C1C1C',
      },
      fontFamily: {
        sans: ['Rawline', 'Raleway', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

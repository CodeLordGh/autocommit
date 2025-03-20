/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      animation: {
        'code-scroll': 'scrollCode 120s linear infinite',
        'fade-in-code': 'fadeInCode 0.5s ease forwards',
      },
      keyframes: {
        scrollCode: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-50%)' },
        },
        fadeInCode: {
          '0%': {
            opacity: '0',
            transform: 'translateX(-20px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)'
          },
        },
      },
    },
  },
  plugins: [],
}
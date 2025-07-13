/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  safelist: [
    'backdrop-blur-md',
    'shadow-2xl',
    'shadow-glass',
    'rounded-2xl',
    'bg-black/60',
    'border-purple-700',
    'animate-fade-in-up',
    'font-heading',
    'font-body',
    'text-purple-200',
    'text-purple-400',
    'drop-shadow-lg',
    'bg-pink-900',
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Sora', 'sans-serif'],
        body: ['Inter', 'Space Grotesk', 'sans-serif'],
      },
      colors: {
        black: '#0a0a0a',
        purple: {
          50: '#f5e9ff',
          100: '#e6ccff',
          200: '#d1aaff',
          300: '#b980ff',
          400: '#a259ff',
          500: '#8a2be2', // main accent
          600: '#6c1bbd',
          700: '#4e0e8a',
          800: '#2f054d',
          900: '#1a0026',
        },
      },
      boxShadow: {
        '2xl': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        'glass': '0 4px 32px 0 rgba(31, 38, 135, 0.17)',
      },
      backdropBlur: {
        md: '12px',
      },
      borderRadius: {
        '2xl': '1.5rem',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.7s cubic-bezier(0.23, 1, 0.32, 1) both',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(40px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
      },
    },
  },
  plugins: [],
} 
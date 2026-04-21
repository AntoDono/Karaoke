/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './pages/**/*.{vue,ts}',
    './components/**/*.{vue,ts}',
    './layouts/**/*.{vue,ts}',
    './composables/**/*.{ts}',
    './stores/**/*.{ts}',
  ],
  theme: {
    extend: {
      // Custom colors on top of Tailwind's built-in green scale.
      // Tailwind green-400..700 already matches our palette exactly:
      //   green-700 = #15803d  (deep botanical)
      //   green-600 = #16a34a  (mid)
      //   green-500 = #22c55e  (vivid)
      //   green-400 = #4ade80  (lime)
      //   green-300 = #86efac  (border-strong)
      //   green-200 = #bbf7d0  (pale)
      //   green-100 = #dcfce7  (highlight bg)
      //   green-50  = #f0fdf4  (card bg)
      colors: {
        // Page background — faintest green tint
        canvas: '#FAFFF9',
        // Ink / text
        ink: {
          DEFAULT: '#0a0f0a',
          muted:   '#374B3A',
          faint:   '#6B8F72',
        },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        mono:    ['IBM Plex Mono', 'monospace'],
      },
      animation: {
        'pulse-border': 'pulse-border 1.8s ease-in-out infinite',
        'fade-up':      'fadeUp 0.4s ease forwards',
        'ring-pulse':   'ring-pulse 1.6s ease-out infinite',
        'dot-pulse':    'dotPulse 1s ease-in-out infinite',
        'spin-slow':    'spin 0.8s linear infinite',
      },
      keyframes: {
        'pulse-border': {
          '0%, 100%': { borderColor: '#22c55e', opacity: '0.6' },
          '50%':       { borderColor: '#4ade80', opacity: '1' },
        },
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'ring-pulse': {
          '0%':   { opacity: '0.8', transform: 'scale(1)' },
          '100%': { opacity: '0',   transform: 'scale(1.4)' },
        },
        dotPulse: {
          '0%, 100%': { transform: 'scale(1)',   opacity: '1' },
          '50%':       { transform: 'scale(1.5)', opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}

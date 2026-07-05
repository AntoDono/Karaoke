/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app/**/*.vue',
    './plugins/**/*.{js,ts}',
    './composables/**/*.{js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        rice: {
          50:  '#FDFAF0',
          100: '#FAF6E7',
          200: '#F4EDD1',
          300: '#EBE0B0',
          400: '#E1D18F',
        },
        cream: {
          50:  '#FFFBEE',
          100: '#FFF4D6',
          200: '#FCE9B2',
          300: '#F5D888',
          400: '#EAC257',
        },
        moss: {
          50:  '#EEF6EF',
          100: '#D7EBDA',
          200: '#A7D4B0',
          300: '#6FB57F',
          400: '#3F9556',
          500: '#2D8F52',
          600: '#207040',
          700: '#155230',
          800: '#0F3D26',
          900: '#0A2A1A',
        },
        ink: {
          DEFAULT: '#2A2118',
          soft:    '#4A3E30',
          faint:   '#8B7B65',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        sans:    ['"DM Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.06em',
      },
      boxShadow: {
        soft:    '0 4px 24px -6px rgba(15, 61, 38, 0.10)',
        card:    '0 12px 40px -12px rgba(15, 61, 38, 0.18)',
        emboss:  'inset 0 1px 0 rgba(255,255,255,0.5), 0 1px 2px rgba(15, 61, 38, 0.08)',
      },
      animation: {
        'rise': 'rise 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) both',
        'grain': 'grain 8s steps(8) infinite',
      },
      keyframes: {
        rise: {
          '0%':   { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        grain: {
          '0%,100%': { transform: 'translate(0,0)' },
          '10%':     { transform: 'translate(-3%,-2%)' },
          '30%':     { transform: 'translate(3%,-4%)' },
          '50%':     { transform: 'translate(-2%,5%)' },
          '70%':     { transform: 'translate(4%,3%)' },
          '90%':     { transform: 'translate(-4%,1%)' },
        },
      },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          deep: '#020713',
          card: 'rgba(8, 18, 36, 0.65)',
          'card-hover': 'rgba(12, 28, 56, 0.8)',
          blue: '#00bbff',
          cyan: '#00f0ff',
          green: '#39ff14',
          orange: '#ff9900',
          magenta: '#e0a3ff',
          purple: '#9d4edd',
          text: '#e2f1ff',
          muted: '#7da5cc',
          dim: '#41688f',
        }
      },
      fontFamily: {
        hud: ['Orbitron', 'sans-serif'],
        labels: ['Rajdhani', 'sans-serif'],
        mono: ['Fira Code', 'monospace']
      },
      boxShadow: {
        glow: '0 0 15px rgba(0, 187, 255, 0.25)',
        'glow-strong': '0 0 25px rgba(0, 240, 255, 0.5)',
      }
    },
  },
  plugins: [],
}

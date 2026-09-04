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
          DEFAULT: '#1E88E5',
          dark: '#1565C0',
          light: '#64B5F6',
        },
        health: {
          excellent: '#43A047',
          good: '#FBC02D',
          concerning: '#FB8C00',
          critical: '#E53935',
        }
      },
    },
  },
  plugins: [],
}

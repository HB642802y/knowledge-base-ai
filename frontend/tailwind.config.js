/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f5f9",
          100: "#d9e6f0",
          200: "#b3cde1",
          500: "#2c5f8a",
          600: "#1e4a6e",
          700: "#163a57",
          800: "#0f2b42",
          900: "#0a1e30",
        },
      },
      fontFamily: {
        sans: ['"Source Sans 3"', "Segoe UI", "system-ui", "sans-serif"],
        display: ['"IBM Plex Sans"', "Segoe UI", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

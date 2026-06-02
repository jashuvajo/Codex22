/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#080b11",
          panel: "#0f1522",
          accent: "#00e0ff",
          success: "#25f0a4",
          danger: "#ff5a72",
          warning: "#f5cc67"
        }
      },
      boxShadow: {
        bloomberg: "0 0 0 1px rgba(24,35,54,.9), 0 10px 30px rgba(0,0,0,.35)"
      }
    }
  },
  plugins: []
};

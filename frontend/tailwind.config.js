/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#126B5A",
        "primary-dark": "#0B4A3F",
        secondary: "#20A67A",
        mint: "#A7E8D0",
        background: "#F7F9F7",
        surface: "#FFFFFF",
        text: "#17211F",
        muted: "#66736F",
        border: "#DCE4E0",
        success: "#16865B",
        warning: "#D79520",
        danger: "#D9534F",
        info: "#3D73C9",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}


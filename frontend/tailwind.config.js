/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        border: 'rgb(31 41 55)',
        background: 'rgb(17 24 39)',
        primary: {
          DEFAULT: 'rgb(59 130 246)',
          content: 'rgb(255 255 255)',
          hover: 'rgb(37 99 235)',
        },
        secondary: {
          DEFAULT: 'rgb(31 41 55)',
          content: 'rgb(255 255 255)',
          hover: 'rgb(55 65 81)',
        },
        error: {
          DEFAULT: 'rgb(220 38 38)',
          content: 'rgb(254 202 202)',
        },
        content: {
          primary: 'rgb(255 255 255)',
          secondary: 'rgb(156 163 175)',
          tertiary: 'rgb(107 114 128)',
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "calc(0.5rem - 2px)",
        sm: "calc(0.5rem - 4px)",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('tailwindcss-animate'),
  ],
}

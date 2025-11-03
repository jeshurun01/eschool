/* Tailwind CSS configuration pour eSchool */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./*/templates/**/*.html",  // Templates dans les apps
    "./**/*.py"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        // Colors pour les rôles
        student: {
          600: '#2563eb',
          700: '#1d4ed8',
        },
        parent: {
          600: '#16a34a',
          700: '#15803d',
        },
        teacher: {
          600: '#9333ea',
          700: '#7e22ce',
        },
        finance: {
          600: '#0d9488',
          700: '#0f766e',
        },
      }
    },
  },
  plugins: [],
}

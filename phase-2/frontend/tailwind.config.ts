import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Warm neutral palette
        canvas: {
          DEFAULT: "#FAFAF9",
          dark: "#0C0A09",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          dark: "#1C1917",
        },
        // Stone-based neutrals for warm feel
        neutral: {
          50: "#FAFAF9",
          100: "#F5F5F4",
          150: "#EEEEEC",
          200: "#E7E5E4",
          300: "#D6D3D1",
          400: "#A8A29E",
          500: "#78716C",
          600: "#57534E",
          700: "#44403C",
          800: "#292524",
          900: "#1C1917",
          950: "#0C0A09",
        },
        // Primary accent - refined indigo
        accent: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        // Priority colors
        priority: {
          low: "#78716C",
          "low-bg": "#F5F5F4",
          medium: "#3B82F6",
          "medium-bg": "#EFF6FF",
          high: "#F97316",
          "high-bg": "#FFF7ED",
          urgent: "#EF4444",
          "urgent-bg": "#FEF2F2",
        },
        // Semantic colors
        success: {
          DEFAULT: "#10B981",
          light: "#D1FAE5",
          dark: "#059669",
        },
        warning: {
          DEFAULT: "#F59E0B",
          light: "#FEF3C7",
          dark: "#D97706",
        },
        error: {
          DEFAULT: "#EF4444",
          light: "#FEE2E2",
          dark: "#DC2626",
        },
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-satoshi)", "var(--font-dm-sans)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display": ["3rem", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "700" }],
        "h1": ["2.25rem", { lineHeight: "1.2", letterSpacing: "-0.02em", fontWeight: "700" }],
        "h2": ["1.75rem", { lineHeight: "1.3", letterSpacing: "-0.01em", fontWeight: "600" }],
        "h3": ["1.375rem", { lineHeight: "1.4", letterSpacing: "0", fontWeight: "500" }],
        "h4": ["1.125rem", { lineHeight: "1.5", letterSpacing: "0", fontWeight: "500" }],
        "body": ["1rem", { lineHeight: "1.6", letterSpacing: "0" }],
        "body-sm": ["0.875rem", { lineHeight: "1.5", letterSpacing: "0" }],
        "caption": ["0.75rem", { lineHeight: "1.4", letterSpacing: "0.02em" }],
      },
      boxShadow: {
        "soft-xs": "0 1px 2px 0 rgba(28, 25, 23, 0.03)",
        "soft-sm": "0 1px 3px 0 rgba(28, 25, 23, 0.04), 0 1px 2px -1px rgba(28, 25, 23, 0.04)",
        "soft": "0 4px 6px -1px rgba(28, 25, 23, 0.05), 0 2px 4px -2px rgba(28, 25, 23, 0.05)",
        "soft-md": "0 8px 16px -4px rgba(28, 25, 23, 0.06), 0 4px 6px -2px rgba(28, 25, 23, 0.04)",
        "soft-lg": "0 16px 32px -8px rgba(28, 25, 23, 0.08), 0 8px 16px -4px rgba(28, 25, 23, 0.04)",
        "soft-xl": "0 24px 48px -12px rgba(28, 25, 23, 0.12)",
        "inner-soft": "inset 0 2px 4px 0 rgba(28, 25, 23, 0.04)",
        "glow": "0 0 20px -5px rgba(99, 102, 241, 0.4)",
        "glow-lg": "0 0 40px -10px rgba(99, 102, 241, 0.5)",
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      spacing: {
        "4.5": "1.125rem",
        "5.5": "1.375rem",
        "18": "4.5rem",
        "22": "5.5rem",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "fade-in-up": "fadeInUp 0.4s ease-out",
        "fade-in-down": "fadeInDown 0.4s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        "slide-in-left": "slideInLeft 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        "spin-slow": "spin 3s linear infinite",
        "pulse-soft": "pulseSoft 2s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
        "check": "check 0.3s ease-out forwards",
        "bounce-subtle": "bounceSubtle 0.4s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeInDown: {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideInLeft: {
          "0%": { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        check: {
          "0%": { strokeDashoffset: "16" },
          "100%": { strokeDashoffset: "0" },
        },
        bounceSubtle: {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(0.95)" },
          "100%": { transform: "scale(1)" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "gradient-mesh": "linear-gradient(135deg, var(--tw-gradient-stops))",
        "noise": "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
      },
      transitionTimingFunction: {
        "bounce-in": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        "smooth": "cubic-bezier(0.4, 0, 0.2, 1)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;

/**
 * CinemaCompass Design System
 * Cinematic color palette, typography, and design tokens
 */

export const colors = {
  // Primary Colors (Cinematic)
  black: '#000000',
  charcoal: '#141414',
  darkGray: '#1A1F2C',
  elevated: '#1E2330',
  
  // Accent Colors
  accentRed: '#E50914',        // Netflix red - CTAs, highlights
  accentPurple: '#6B4EE6',      // CinemaCompass brand
  gold: '#FFD700',              // Ratings, premium features
  
  // Semantic Colors
  success: '#00C853',
  warning: '#FFA726',
  error: '#E50914',
  info: '#42A5F5',
  
  // Text Colors
  textPrimary: '#FFFFFF',
  textSecondary: '#B3B3B3',
  textTertiary: '#808080',
  textDisabled: '#4D4D4D',
  
  // Background Colors
  bgPrimary: '#000000',
  bgSecondary: '#141414',
  bgTertiary: '#1A1F2C',
  bgElevated: '#1E2330',
  
  // Border Colors
  borderLight: 'rgba(255, 255, 255, 0.1)',
  borderMedium: 'rgba(255, 255, 255, 0.2)',
  borderDark: 'rgba(255, 255, 255, 0.05)',
  
  // Gradients
  gradientHero: 'linear-gradient(135deg, #6B4EE6 0%, #E50914 50%, #FFD700 100%)',
  gradientPurple: 'linear-gradient(135deg, #6B4EE6 0%, #8B5CF6 100%)',
  gradientRed: 'linear-gradient(135deg, #E50914 0%, #FF5722 100%)',
  gradientCard: 'linear-gradient(135deg, rgba(107, 78, 230, 0.1) 0%, rgba(229, 9, 20, 0.1) 100%)',
  
  // Glow Effects
  glowPurple: 'rgba(107, 78, 230, 0.3)',
  glowRed: 'rgba(229, 9, 20, 0.3)',
  glowGold: 'rgba(255, 215, 0, 0.3)',
};

export const typography = {
  fonts: {
    primary: "'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    heading: "'Helvetica Neue', 'Arial', sans-serif",
    accent: "'Cinzel', serif", // Optional for movie titles
  },
  sizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
    '6xl': '4rem',     // 64px
  },
  weights: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  lineHeights: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
};

export const borderRadius = {
  none: '0',
  sm: '0.25rem',   // 4px
  md: '0.375rem',  // 6px
  lg: '0.5rem',    // 8px
  xl: '0.75rem',   // 12px
  '2xl': '1rem',   // 16px
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.5)',
  md: '0 4px 6px rgba(0, 0, 0, 0.5)',
  lg: '0 10px 15px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 25px rgba(0, 0, 0, 0.5)',
  glow: `0 0 30px ${colors.glowPurple}`,
  glowRed: `0 0 30px ${colors.glowRed}`,
};

export const transitions = {
  fast: '150ms ease-in-out',
  normal: '300ms ease-in-out',
  slow: '500ms ease-in-out',
};

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
};

export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  zIndex,
};

export default theme;


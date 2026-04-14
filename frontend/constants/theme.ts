// Divine Waifus - Design System Theme
// Rich gacha game palette with gradients and glow effects

export const COLORS = {
  // Core backgrounds
  bgPrimary: '#07071A',
  bgSecondary: '#0D0D2B',
  bgCard: 'rgba(20, 20, 60, 0.6)',
  bgCardHover: 'rgba(30, 30, 80, 0.7)',
  bgGlass: 'rgba(255, 255, 255, 0.04)',
  bgGlassLight: 'rgba(255, 255, 255, 0.08)',
  bgOverlay: 'rgba(0, 0, 0, 0.85)',

  // Accent colors
  accent: '#FF6B35',
  accentGlow: 'rgba(255, 107, 53, 0.4)',
  gold: '#FFD700',
  goldDark: '#C9A800',
  goldGlow: 'rgba(255, 215, 0, 0.3)',

  // Text colors
  textPrimary: '#FFFFFF',
  textSecondary: '#B8B8D0',
  textMuted: '#6B6B8D',
  textDim: '#4A4A6A',

  // Border colors
  border: 'rgba(255, 255, 255, 0.06)',
  borderLight: 'rgba(255, 255, 255, 0.12)',
  borderAccent: 'rgba(255, 107, 53, 0.3)',
  borderGold: 'rgba(255, 215, 0, 0.3)',

  // Status colors
  success: '#44DD88',
  error: '#FF4466',
  warning: '#FFAA44',
  info: '#44AAFF',

  // Gradient pairs
  gradientDark: ['#07071A', '#0D0D2B'] as const,
  gradientCard: ['rgba(20, 20, 60, 0.8)', 'rgba(10, 10, 40, 0.6)'] as const,
  gradientAccent: ['#FF6B35', '#FF4444'] as const,
  gradientGold: ['#FFD700', '#FF8C00'] as const,
  gradientPurple: ['#8844FF', '#4422CC'] as const,
  gradientHeader: ['rgba(15, 15, 45, 0.95)', 'rgba(7, 7, 26, 0.95)'] as const,
  gradientTabBar: ['rgba(12, 12, 35, 0.98)', 'rgba(7, 7, 20, 0.98)'] as const,
};

// Rarity system
export const RARITY = {
  colors: {
    1: '#8899AA',
    2: '#44BB66',
    3: '#4499FF',
    4: '#BB55FF',
    5: '#FF5544',
    6: '#FFD700',
  } as Record<number, string>,
  names: {
    1: 'Comune',
    2: 'Non Comune',
    3: 'Raro',
    4: 'Epico',
    5: 'Mitico',
    6: 'Divino',
  } as Record<number, string>,
  gradients: {
    1: ['#667788', '#556677'] as const,
    2: ['#44BB66', '#33AA55'] as const,
    3: ['#4499FF', '#3377DD'] as const,
    4: ['#BB55FF', '#9933DD'] as const,
    5: ['#FF5544', '#DD3333'] as const,
    6: ['#FFD700', '#FF8C00'] as const,
  } as Record<number, readonly [string, string]>,
  bgAlpha: {
    1: 'rgba(136, 153, 170, 0.08)',
    2: 'rgba(68, 187, 102, 0.08)',
    3: 'rgba(68, 153, 255, 0.08)',
    4: 'rgba(187, 85, 255, 0.08)',
    5: 'rgba(255, 85, 68, 0.08)',
    6: 'rgba(255, 215, 0, 0.1)',
  } as Record<number, string>,
};

// Element system
export const ELEMENTS = {
  colors: {
    fire: '#FF5544',
    water: '#4499FF',
    earth: '#CC9944',
    wind: '#44DD99',
    thunder: '#FFCC33',
    light: '#FFDD88',
    shadow: '#AA55FF',
    dark: '#AA55FF',
    neutral: '#8899AA',
  } as Record<string, string>,
  icons: {
    fire: '\u{1F525}',
    water: '\u{1F4A7}',
    earth: '\u{1FAA8}',
    wind: '\u{1F4A8}',
    thunder: '\u26A1',
    light: '\u2728',
    shadow: '\u{1F311}',
    dark: '\u{1F311}',
    neutral: '\u26AA',
  } as Record<string, string>,
};

// Class system
export const CLASSES = {
  icons: {
    DPS: '\u2694\uFE0F',
    Tank: '\u{1F6E1}\uFE0F',
    Support: '\u2764\uFE0F',
  } as Record<string, string>,
  colors: {
    DPS: '#FF5544',
    Tank: '#4499FF',
    Support: '#44DD99',
  } as Record<string, string>,
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
};

export const FONT_SIZES = {
  xs: 8,
  sm: 10,
  md: 12,
  lg: 14,
  xl: 16,
  xxl: 20,
  title: 18,
  hero: 24,
};

export const BORDER_RADIUS = {
  sm: 6,
  md: 10,
  lg: 14,
  xl: 18,
  round: 50,
};

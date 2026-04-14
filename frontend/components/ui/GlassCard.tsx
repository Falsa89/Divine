import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, BORDER_RADIUS } from '../../constants/theme';

interface Props {
  children: React.ReactNode;
  style?: ViewStyle;
  borderColor?: string;
  variant?: 'default' | 'accent' | 'gold' | 'dark';
}

export default function GlassCard({ children, style, borderColor, variant = 'default' }: Props) {
  const getBorderColor = () => {
    if (borderColor) return borderColor;
    switch (variant) {
      case 'accent': return COLORS.borderAccent;
      case 'gold': return COLORS.borderGold;
      case 'dark': return COLORS.border;
      default: return COLORS.borderLight;
    }
  };

  const getGradient = (): readonly [string, string] => {
    switch (variant) {
      case 'accent': return ['rgba(255, 107, 53, 0.06)', 'rgba(255, 68, 68, 0.03)'];
      case 'gold': return ['rgba(255, 215, 0, 0.06)', 'rgba(255, 140, 0, 0.03)'];
      case 'dark': return ['rgba(15, 15, 40, 0.8)', 'rgba(10, 10, 30, 0.6)'];
      default: return COLORS.gradientCard;
    }
  };

  const colors = getGradient();

  return (
    <View style={[s.outer, { borderColor: getBorderColor() }, style]}>
      <LinearGradient
        colors={[colors[0], colors[1]]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={s.inner}
      >
        {children}
      </LinearGradient>
    </View>
  );
}

const s = StyleSheet.create({
  outer: {
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    overflow: 'hidden',
  },
  inner: {
    padding: 12,
  },
});

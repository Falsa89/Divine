import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, BORDER_RADIUS } from '../../constants/theme';

interface Props {
  title: string;
  onPress: () => void;
  variant?: 'accent' | 'gold' | 'danger' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: string;
  style?: ViewStyle;
}

export default function GradientButton({ title, onPress, variant = 'accent', size = 'md', loading, disabled, icon, style }: Props) {
  const getGradient = (): readonly [string, string] => {
    switch (variant) {
      case 'gold': return COLORS.gradientGold;
      case 'danger': return ['#FF4466', '#CC2244'];
      case 'outline': return ['transparent', 'transparent'];
      case 'ghost': return ['transparent', 'transparent'];
      default: return COLORS.gradientAccent;
    }
  };

  const getPadding = () => {
    switch (size) {
      case 'sm': return { paddingHorizontal: 12, paddingVertical: 6 };
      case 'lg': return { paddingHorizontal: 24, paddingVertical: 14 };
      default: return { paddingHorizontal: 18, paddingVertical: 10 };
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'sm': return 10;
      case 'lg': return 14;
      default: return 12;
    }
  };

  const isOutline = variant === 'outline' || variant === 'ghost';
  const colors = getGradient();
  const borderColor = variant === 'outline' ? COLORS.accent : variant === 'ghost' ? 'transparent' : 'transparent';

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      style={[{ opacity: disabled ? 0.4 : 1 }, style]}
    >
      <LinearGradient
        colors={[colors[0], colors[1]]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={[
          s.btn,
          getPadding(),
          isOutline && { borderWidth: 1.5, borderColor },
        ]}
      >
        {loading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <>
            {icon && <Text style={[s.icon, { fontSize: getFontSize() + 2 }]}>{icon}</Text>}
            <Text style={[
              s.text,
              { fontSize: getFontSize() },
              isOutline && { color: COLORS.accent },
            ]}>
              {title}
            </Text>
          </>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  btn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: BORDER_RADIUS.md,
    gap: 6,
  },
  icon: {
    color: '#fff',
  },
  text: {
    color: '#fff',
    fontWeight: '900',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
});

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS, SPACING } from '../../constants/theme';

interface Props {
  title: string;
  titleColor?: string;
  showBack?: boolean;
  rightContent?: React.ReactNode;
}

export default function ScreenHeader({ title, titleColor, showBack = false, rightContent }: Props) {
  const router = useRouter();
  return (
    <LinearGradient
      colors={[COLORS.gradientHeader[0], COLORS.gradientHeader[1]]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={s.header}
    >
      <View style={s.headerInner}>
        {showBack && (
          <TouchableOpacity onPress={() => router.back()} style={s.backBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
            <Text style={s.backIcon}>{'\u2190'}</Text>
          </TouchableOpacity>
        )}
        <Text style={[s.title, titleColor ? { color: titleColor } : null]} numberOfLines={1}>{title}</Text>
        <View style={s.right}>{rightContent}</View>
      </View>
      <View style={s.divider} />
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  header: {
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.sm,
    paddingBottom: 0,
  },
  headerInner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingBottom: SPACING.sm,
  },
  backBtn: {
    marginRight: SPACING.md,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.06)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    color: COLORS.gold,
    fontSize: 18,
    fontWeight: '700',
  },
  title: {
    flex: 1,
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },
  right: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.borderAccent,
  },
});

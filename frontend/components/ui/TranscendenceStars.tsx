import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, RadialGradient } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, withDelay,
  withSequence, Easing,
} from 'react-native-reanimated';

interface TranscendenceStarsProps {
  stars: number; // 13, 14, or 15
  size?: number;
}

/** Genera path stella a 5 punte (identico a StarDisplay). */
function starPath(s: number): string {
  const cx = s / 2;
  const cy = s / 2;
  const outerR = s * 0.48;
  const innerR = s * 0.19;
  const pts: string[] = [];
  for (let i = 0; i < 5; i++) {
    const oA = (Math.PI / 2) + (i * 2 * Math.PI / 5);
    pts.push(`${(cx + outerR * Math.cos(-oA)).toFixed(2)},${(cy - outerR * Math.sin(oA)).toFixed(2)}`);
    const iA = oA + Math.PI / 5;
    pts.push(`${(cx + innerR * Math.cos(-iA)).toFixed(2)},${(cy - innerR * Math.sin(iA)).toFixed(2)}`);
  }
  return `M${pts[0]} L${pts.slice(1).join(' L')} Z`;
}

/**
 * TranscendenceStars - Stelle trascendenti per eroi 13-15 stelle.
 *
 * 13★ → 1 stella grande centrale
 * 14★ → 2 stelle affiancate
 * 15★ → 3 stelle (centrale piu grande)
 */
export default function TranscendenceStars({ stars, size = 20 }: TranscendenceStarsProps) {
  const capped = Math.min(Math.max(stars, 13), 15);
  const count = capped - 12; // 1, 2, or 3

  const layouts: { scale: number; offsetX: number }[][] = [
    [{ scale: 1.3, offsetX: 0 }],
    [{ scale: 1, offsetX: -0.6 }, { scale: 1, offsetX: 0.6 }],
    [{ scale: 0.85, offsetX: -1.1 }, { scale: 1.2, offsetX: 0 }, { scale: 0.85, offsetX: 1.1 }],
  ];

  const layout = layouts[count - 1];
  const totalW = size * 3;

  return (
    <View style={[styles.container, { width: totalW, height: size * 1.6 }]}>  
      {layout.map((item, i) => {
        const s = Math.round(size * item.scale);
        const x = (totalW / 2) + (item.offsetX * size) - (s / 2);
        const y = (size * 1.6 - s) / 2;
        return (
          <TransStar key={i} size={s} x={x} y={y} index={i} total={count} />
        );
      })}
    </View>
  );
}

/** Singola stella trascendente con glow, pulsazione e shimmer. */
function TransStar({ size, x, y, index, total }: {
  size: number; x: number; y: number; index: number; total: number;
}) {
  // Pulsazione lenta
  const pulse = useSharedValue(1);
  useEffect(() => {
    pulse.value = withDelay(index * 300,
      withRepeat(
        withSequence(
          withTiming(1.08, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
          withTiming(1, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
        ), -1, true,
      ),
    );
  }, []);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  // Shimmer
  const shimmerX = useSharedValue(-size);
  useEffect(() => {
    const timer = setTimeout(() => {
      shimmerX.value = withRepeat(
        withTiming(size * 1.5, { duration: 3000, easing: Easing.inOut(Easing.ease) }),
        -1, false,
      );
    }, index * 500);
    return () => clearTimeout(timer);
  }, []);

  const shimmerStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: shimmerX.value }, { rotate: '25deg' }],
  }));

  // Particle glow pulse
  const glowOpacity = useSharedValue(0.3);
  useEffect(() => {
    glowOpacity.value = withDelay(index * 200,
      withRepeat(
        withSequence(
          withTiming(0.6, { duration: 2200, easing: Easing.inOut(Easing.ease) }),
          withTiming(0.3, { duration: 2200, easing: Easing.inOut(Easing.ease) }),
        ), -1, true,
      ),
    );
  }, []);

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glowOpacity.value,
  }));

  const d = starPath(size);
  const gradId = `trans_${index}_${total}`;
  const glowId = `glow_${index}_${total}`;

  return (
    <View style={[styles.transWrap, { left: x, top: y, width: size, height: size }]}>
      {/* Outer glow */}
      <Animated.View style={[styles.outerGlow, glowStyle, {
        width: size * 1.8, height: size * 1.8, borderRadius: size * 0.9,
        left: -(size * 0.4), top: -(size * 0.4),
      }]} />

      {/* Pulsating star */}
      <Animated.View style={[{ width: size, height: size }, pulseStyle]}>
        <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <Defs>
            <SvgGradient id={gradId} x1="0.2" y1="0" x2="0.8" y2="1">
              <Stop offset="0%" stopColor="#E8E8FF" stopOpacity={1} />
              <Stop offset="40%" stopColor="#6366F1" stopOpacity={1} />
              <Stop offset="70%" stopColor="#9333EA" stopOpacity={1} />
              <Stop offset="100%" stopColor="#581C87" stopOpacity={1} />
            </SvgGradient>
            <RadialGradient id={glowId} cx="0.4" cy="0.35" rx="0.5" ry="0.5">
              <Stop offset="0%" stopColor="#FFFFFF" stopOpacity={0.4} />
              <Stop offset="100%" stopColor="#FFFFFF" stopOpacity={0} />
            </RadialGradient>
          </Defs>
          {/* Main star body */}
          <Path d={d} fill={`url(#${gradId})`} stroke="#C4B5FD" strokeWidth={0.8} strokeOpacity={0.7} />
          {/* Inner highlight */}
          <Path d={d} fill={`url(#${glowId})`} />
          {/* Edge emboss */}
          <Path d={d} fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth={0.5}
            strokeDasharray={`${size * 0.6}`} strokeDashoffset={size * 0.3} />
        </Svg>
      </Animated.View>

      {/* Shimmer */}
      <View style={[styles.shimmerClip, { width: size, height: size, borderRadius: size * 0.15 }]} pointerEvents="none">
        <Animated.View style={[styles.shimmerBar, shimmerStyle, { width: size * 0.3, height: size * 2 }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  transWrap: { position: 'absolute', alignItems: 'center', justifyContent: 'center' },
  outerGlow: {
    position: 'absolute',
    backgroundColor: 'rgba(139,92,246,0.25)',
  },
  shimmerClip: { position: 'absolute', overflow: 'hidden' },
  shimmerBar: {
    position: 'absolute', left: 0, top: -10,
    backgroundColor: 'rgba(255,255,255,0.18)', borderRadius: 4,
  },
});

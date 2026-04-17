import React, { useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, RadialGradient } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, withDelay,
  withSequence, Easing,
} from 'react-native-reanimated';

let _tIdCounter = 0;
function useUid(prefix: string) {
  const ref = useRef(`${prefix}_${++_tIdCounter}_${Date.now()}`);
  return ref.current;
}

interface TranscendenceStarsProps {
  stars: number;
  size?: number;
}

function starPath(s: number): string {
  const cx = s / 2, cy = s / 2;
  const outerR = s * 0.48, innerR = s * 0.19;
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
 * TranscendenceStars - Stelle 13-15 con gradient bianco→blu→viola.
 * 13★ = 1 stella grande, 14★ = 2, 15★ = 3 (centrale piu grande).
 */
export default function TranscendenceStars({ stars, size = 20 }: TranscendenceStarsProps) {
  const capped = Math.min(Math.max(stars, 13), 15);
  const count = capped - 12;

  const layouts: { scale: number; offsetX: number }[][] = [
    [{ scale: 1.3, offsetX: 0 }],
    [{ scale: 1, offsetX: -0.6 }, { scale: 1, offsetX: 0.6 }],
    [{ scale: 0.85, offsetX: -1.1 }, { scale: 1.2, offsetX: 0 }, { scale: 0.85, offsetX: 1.1 }],
  ];

  const layout = layouts[count - 1];
  const totalW = size * 3;
  const totalH = size * 1.6;

  return (
    <View style={[st.container, { width: totalW, height: totalH }]}>
      {layout.map((item, i) => {
        const sz = Math.round(size * item.scale);
        const xPos = (totalW / 2) + (item.offsetX * size) - (sz / 2);
        const yPos = (totalH - sz) / 2;
        return <TransStar key={i} size={sz} x={xPos} y={yPos} index={i} />;
      })}
    </View>
  );
}

function TransStar({ size, x, y, index }: { size: number; x: number; y: number; index: number }) {
  const gid = useUid('tg');
  const rid = useUid('tr');
  const d = starPath(size);

  // Pulse
  const pulse = useSharedValue(1);
  useEffect(() => {
    pulse.value = withDelay(index * 300,
      withRepeat(withSequence(
        withTiming(1.1, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
      ), -1, true),
    );
  }, []);
  const pulseStyle = useAnimatedStyle(() => ({ transform: [{ scale: pulse.value }] }));

  // Shimmer
  const shimX = useSharedValue(-size * 1.2);
  useEffect(() => {
    const t = setTimeout(() => {
      shimX.value = withRepeat(
        withTiming(size * 1.5, { duration: 3000, easing: Easing.inOut(Easing.ease) }),
        -1, false,
      );
    }, index * 500);
    return () => clearTimeout(t);
  }, []);
  const shimStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: shimX.value }, { rotate: '25deg' }],
  }));

  // Glow pulse
  const glowOp = useSharedValue(0.3);
  useEffect(() => {
    glowOp.value = withDelay(index * 200,
      withRepeat(withSequence(
        withTiming(0.6, { duration: 2200, easing: Easing.inOut(Easing.ease) }),
        withTiming(0.3, { duration: 2200, easing: Easing.inOut(Easing.ease) }),
      ), -1, true),
    );
  }, []);
  const glowStyle = useAnimatedStyle(() => ({ opacity: glowOp.value }));

  return (
    <View style={[st.transWrap, { left: x, top: y, width: size, height: size }]}>
      {/* Outer glow */}
      <Animated.View style={[st.outerGlow, glowStyle, {
        width: size * 1.8, height: size * 1.8, borderRadius: size * 0.9,
        left: -(size * 0.4), top: -(size * 0.4),
      }]} />

      {/* Pulsating star */}
      <Animated.View style={[{ width: size, height: size }, pulseStyle]}>
        <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <Defs>
            <SvgGradient id={gid} x1="0.15" y1="0" x2="0.85" y2="1">
              <Stop offset="0%" stopColor="#E8E8FF" stopOpacity={1} />
              <Stop offset="35%" stopColor="#6366F1" stopOpacity={1} />
              <Stop offset="65%" stopColor="#9333EA" stopOpacity={1} />
              <Stop offset="100%" stopColor="#581C87" stopOpacity={1} />
            </SvgGradient>
            <RadialGradient id={rid} cx="0.4" cy="0.35" rx="0.5" ry="0.5">
              <Stop offset="0%" stopColor="#FFFFFF" stopOpacity={0.45} />
              <Stop offset="100%" stopColor="#FFFFFF" stopOpacity={0} />
            </RadialGradient>
          </Defs>
          <Path d={d} fill={`url(#${gid})`} stroke="#C4B5FD" strokeWidth={0.8} strokeOpacity={0.7} />
          <Path d={d} fill={`url(#${rid})`} />
          <Path d={d} fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth={0.5}
            strokeDasharray={`${size * 0.6}`} strokeDashoffset={size * 0.3} />
        </Svg>
      </Animated.View>

      {/* Shimmer */}
      <View style={[st.shimClip, { width: size, height: size, borderRadius: size * 0.5 }]} pointerEvents="none">
        <Animated.View style={[st.shimBar, shimStyle, { width: size * 0.3, height: size * 1.5, top: -(size * 0.25) }]} />
      </View>
    </View>
  );
}

const st = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  transWrap: { position: 'absolute', alignItems: 'center', justifyContent: 'center' },
  outerGlow: { position: 'absolute', backgroundColor: 'rgba(139,92,246,0.25)' },
  shimClip: { position: 'absolute', overflow: 'hidden' },
  shimBar: {
    position: 'absolute', left: 0,
    backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 2,
  },
});

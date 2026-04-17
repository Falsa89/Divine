import React, { useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing,
} from 'react-native-reanimated';

let _idCounter = 0;
function useUniqueId(prefix: string) {
  const ref = useRef(`${prefix}_${++_idCounter}_${Date.now()}`);
  return ref.current;
}

interface StarDisplayProps {
  stars: number;
  size?: number;
}

function starPath(size: number): string {
  const cx = size / 2;
  const cy = size / 2;
  const outerR = size * 0.48;
  const innerR = size * 0.19;
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
 * StarDisplay - Stelle 1-12 con SVG Path reale.
 * stars <= 6:  tutte gialle
 * stars 7-12:  rosse = stars-6, gialle = 12-stars
 */
export default function StarDisplay({ stars, size = 14 }: StarDisplayProps) {
  if (stars <= 0) return null;
  const capped = Math.min(stars, 12);
  let redCount: number, yellowCount: number;
  if (capped <= 6) { redCount = 0; yellowCount = capped; }
  else { redCount = capped - 6; yellowCount = 12 - capped; }
  const emptyCount = Math.max(0, 6 - redCount - yellowCount);
  const gap = Math.round(size * 0.15);

  return (
    <View style={[st.row, { gap }]}>
      {Array.from({ length: redCount }).map((_, i) => (
        <RedStar key={`r${i}`} size={size} index={i} />
      ))}
      {Array.from({ length: yellowCount }).map((_, i) => (
        <YellowStar key={`y${i}`} size={size} />
      ))}
      {Array.from({ length: emptyCount }).map((_, i) => (
        <EmptyStar key={`e${i}`} size={size} />
      ))}
    </View>
  );
}

function RedStar({ size, index }: { size: number; index: number }) {
  const uid = useUniqueId('rg');
  const d = starPath(size);

  // Shimmer
  const shimX = useSharedValue(-size * 1.2);
  useEffect(() => {
    const t = setTimeout(() => {
      shimX.value = withRepeat(
        withTiming(size * 1.5, { duration: 2500, easing: Easing.inOut(Easing.ease) }),
        -1, false,
      );
    }, index * 400);
    return () => clearTimeout(t);
  }, []);
  const shimStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: shimX.value }, { rotate: '25deg' }],
  }));

  return (
    <View style={[st.wrap, { width: size, height: size }]}>
      <View style={[st.redGlow, { width: size + 4, height: size + 4, borderRadius: (size + 4) / 2 }]} />
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Defs>
          <SvgGradient id={uid} x1="0.1" y1="0" x2="0.9" y2="1">
            <Stop offset="0%" stopColor="#FF5252" stopOpacity={1} />
            <Stop offset="50%" stopColor="#FF1744" stopOpacity={1} />
            <Stop offset="100%" stopColor="#B71C1C" stopOpacity={1} />
          </SvgGradient>
        </Defs>
        <Path d={d} fill={`url(#${uid})`} stroke="#FF8A80" strokeWidth={0.8} strokeOpacity={0.6} />
        <Path d={d} fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth={0.5}
          strokeDasharray={`${size * 0.8}`} strokeDashoffset={size * 0.4} />
      </Svg>
      {/* Shimmer overlay */}
      <View style={[st.shimClip, { width: size, height: size, borderRadius: size * 0.5 }]} pointerEvents="none">
        <Animated.View style={[st.shimBar, shimStyle, { width: size * 0.35, height: size * 1.5, top: -(size * 0.25) }]} />
      </View>
    </View>
  );
}

function YellowStar({ size }: { size: number }) {
  const uid = useUniqueId('yg');
  const d = starPath(size);
  return (
    <View style={[st.wrap, { width: size, height: size }]}>
      <View style={[st.yellowGlow, { width: size + 2, height: size + 2, borderRadius: (size + 2) / 2 }]} />
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Defs>
          <SvgGradient id={uid} x1="0.1" y1="0" x2="0.9" y2="1">
            <Stop offset="0%" stopColor="#FDE68A" stopOpacity={1} />
            <Stop offset="50%" stopColor="#F59E0B" stopOpacity={1} />
            <Stop offset="100%" stopColor="#B45309" stopOpacity={1} />
          </SvgGradient>
        </Defs>
        <Path d={d} fill={`url(#${uid})`} stroke="#FDE68A" strokeWidth={0.5} strokeOpacity={0.5} />
      </Svg>
    </View>
  );
}

function EmptyStar({ size }: { size: number }) {
  const d = starPath(size);
  return (
    <View style={[st.wrap, { width: size, height: size }]}>
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Path d={d} fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.12)" strokeWidth={0.4} />
      </Svg>
    </View>
  );
}

const st = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center' },
  wrap: { alignItems: 'center', justifyContent: 'center' },
  redGlow: { position: 'absolute', backgroundColor: 'rgba(255,23,68,0.2)' },
  yellowGlow: { position: 'absolute', backgroundColor: 'rgba(245,158,11,0.15)' },
  shimClip: { position: 'absolute', overflow: 'hidden' },
  shimBar: {
    position: 'absolute', left: 0,
    backgroundColor: 'rgba(255,255,255,0.18)', borderRadius: 2,
  },
});

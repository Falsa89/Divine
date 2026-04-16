import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing,
} from 'react-native-reanimated';

interface StarDisplayProps {
  stars: number;
  size?: number;
}

/**
 * StarDisplay - Stelle eroe con SVG Path reale a 5 punte.
 *
 * Logica:
 *   stars <= 6  → tutte gialle, nessuna rossa
 *   stars 7–12  → rosse = stars - 6, gialle = 12 - stars
 *   slot vuoti  → 6 - rosse - gialle
 */
export default function StarDisplay({ stars, size = 14 }: StarDisplayProps) {
  if (stars <= 0) return null;

  const capped = Math.min(stars, 12);
  let redCount: number;
  let yellowCount: number;

  if (capped <= 6) {
    redCount = 0;
    yellowCount = capped;
  } else {
    redCount = capped - 6;
    yellowCount = 12 - capped;
  }

  const emptyCount = Math.max(0, 6 - redCount - yellowCount);
  const gap = Math.round(size * 0.15);

  return (
    <View style={[styles.row, { gap }]}>
      {Array.from({ length: redCount }).map((_, i) => (
        <View key={`r${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          <View style={[styles.redGlow, { width: size + 4, height: size + 4, borderRadius: (size + 4) / 2 }]} />
          <StarSvg size={size} type="red" />
          <RedShimmer size={size} delay={i * 400} />
        </View>
      ))}
      {Array.from({ length: yellowCount }).map((_, i) => (
        <View key={`y${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          <View style={[styles.yellowGlow, { width: size + 2, height: size + 2, borderRadius: (size + 2) / 2 }]} />
          <StarSvg size={size} type="yellow" />
        </View>
      ))}
      {Array.from({ length: emptyCount }).map((_, i) => (
        <View key={`e${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          <StarSvg size={size} type="empty" />
        </View>
      ))}
    </View>
  );
}

/** Genera il path d di una stella a 5 punte classica. */
function starPath(size: number): string {
  const cx = size / 2;
  const cy = size / 2;
  const outerR = size * 0.48;
  const innerR = size * 0.19;
  const points: string[] = [];

  for (let i = 0; i < 5; i++) {
    // Outer point
    const oAngle = (Math.PI / 2) + (i * 2 * Math.PI / 5);
    const ox = cx + outerR * Math.cos(-oAngle);
    const oy = cy - outerR * Math.sin(oAngle);
    points.push(`${ox.toFixed(2)},${oy.toFixed(2)}`);

    // Inner point
    const iAngle = oAngle + Math.PI / 5;
    const ix = cx + innerR * Math.cos(-iAngle);
    const iy = cy - innerR * Math.sin(iAngle);
    points.push(`${ix.toFixed(2)},${iy.toFixed(2)}`);
  }

  return `M${points[0]} L${points.slice(1).join(' L')} Z`;
}

/** SVG stella a 5 punte con gradient. */
function StarSvg({ size, type }: { size: number; type: 'red' | 'yellow' | 'empty' }) {
  const d = starPath(size);
  const gradId = `grad_${type}`;

  const config = {
    red: {
      stops: [
        { offset: '0%', color: '#FF5252', opacity: 1 },
        { offset: '50%', color: '#FF1744', opacity: 1 },
        { offset: '100%', color: '#B71C1C', opacity: 1 },
      ],
      stroke: '#FF8A80',
      strokeWidth: 0.8,
    },
    yellow: {
      stops: [
        { offset: '0%', color: '#FDE68A', opacity: 1 },
        { offset: '50%', color: '#F59E0B', opacity: 1 },
        { offset: '100%', color: '#B45309', opacity: 1 },
      ],
      stroke: '#FDE68A',
      strokeWidth: 0.5,
    },
    empty: {
      stops: [
        { offset: '0%', color: '#FFFFFF', opacity: 0.08 },
        { offset: '100%', color: '#FFFFFF', opacity: 0.03 },
      ],
      stroke: '#FFFFFF',
      strokeWidth: 0.4,
    },
  };

  const c = config[type];

  return (
    <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <Defs>
        <SvgGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
          {c.stops.map((s, i) => (
            <Stop key={i} offset={s.offset} stopColor={s.color} stopOpacity={s.opacity} />
          ))}
        </SvgGradient>
      </Defs>
      <Path
        d={d}
        fill={`url(#${gradId})`}
        stroke={c.stroke}
        strokeWidth={c.strokeWidth}
        strokeOpacity={type === 'empty' ? 0.15 : 0.6}
      />
      {/* Emboss highlight for red stars */}
      {type === 'red' && (
        <Path
          d={d}
          fill="none"
          stroke="rgba(255,255,255,0.25)"
          strokeWidth={0.6}
          strokeDasharray={`${size * 0.8}`}
          strokeDashoffset={size * 0.4}
        />
      )}
    </Svg>
  );
}

/** Shimmer per stelle rosse. */
function RedShimmer({ size, delay }: { size: number; delay: number }) {
  const translateX = useSharedValue(-size);

  useEffect(() => {
    const timer = setTimeout(() => {
      translateX.value = withRepeat(
        withTiming(size * 1.5, { duration: 2500, easing: Easing.inOut(Easing.ease) }),
        -1,
        false,
      );
    }, delay);
    return () => clearTimeout(timer);
  }, []);

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }, { rotate: '25deg' }],
  }));

  return (
    <View style={[styles.shimmerClip, { width: size, height: size, borderRadius: size * 0.15 }]} pointerEvents="none">
      <Animated.View style={[styles.shimmerBar, animStyle, { width: size * 0.3, height: size * 2 }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center' },
  starWrap: { alignItems: 'center', justifyContent: 'center' },
  redGlow: { position: 'absolute', backgroundColor: 'rgba(255,23,68,0.2)' },
  yellowGlow: { position: 'absolute', backgroundColor: 'rgba(245,158,11,0.15)' },
  shimmerClip: { position: 'absolute', overflow: 'hidden' },
  shimmerBar: {
    position: 'absolute', left: 0, top: -10,
    backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 4,
  },
});

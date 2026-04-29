/**
 * AnimatedExpBar — progress bar animata per gli HEROES nel post-battle (v16.22)
 * ───────────────────────────────────────────────────────────────
 * Anima da `expBefore/expToNextBefore` a `expAfter/expToNextAfter`.
 * Se `leveledUp=true`: bar arriva al 100%, breve flash, reset a 0%, poi
 * sale fino al expAfter del nuovo livello.
 * Se `leveledUp=false`: anima singola da before a after.
 *
 * Reanimated in shared values per UI thread smooth animation.
 */
import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSequence,
  withDelay,
  Easing,
  runOnJS,
} from 'react-native-reanimated';

export interface AnimatedExpBarProps {
  expBefore: number;
  expAfter: number;
  expToNextBefore: number;
  expToNextAfter: number;
  leveledUp: boolean;
  /** Override durata animation (ms). */
  durationMs?: number;
  /** Delay iniziale prima di partire (ms). */
  startDelayMs?: number;
  /** Callback quando l'animazione finisce. */
  onComplete?: () => void;
  /** Bar height. */
  height?: number;
}

export default function AnimatedExpBar({
  expBefore,
  expAfter,
  expToNextBefore,
  expToNextAfter,
  leveledUp,
  durationMs = 900,
  startDelayMs = 0,
  onComplete,
  height = 8,
}: AnimatedExpBarProps) {
  // pct ∈ [0, 1] — percentage of bar fill
  const pct = useSharedValue(
    expToNextBefore > 0 ? Math.min(1, expBefore / expToNextBefore) : 0
  );

  useEffect(() => {
    const finalPct = expToNextAfter > 0 ? Math.min(1, expAfter / expToNextAfter) : 0;

    if (leveledUp) {
      // Animate to 100% → flash → jump to 0 → fill to finalPct
      pct.value = withSequence(
        withDelay(startDelayMs, withTiming(1, {
          duration: durationMs * 0.55,
          easing: Easing.out(Easing.quad),
        })),
        withTiming(0, { duration: 0 }),
        withTiming(finalPct, {
          duration: durationMs * 0.45,
          easing: Easing.out(Easing.quad),
        }, (finished) => {
          if (finished && onComplete) runOnJS(onComplete)();
        }),
      );
    } else {
      pct.value = withDelay(startDelayMs, withTiming(finalPct, {
        duration: durationMs,
        easing: Easing.out(Easing.quad),
      }, (finished) => {
        if (finished && onComplete) runOnJS(onComplete)();
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fillStyle = useAnimatedStyle(() => ({
    width: `${pct.value * 100}%`,
  }));

  return (
    <View style={[s.track, { height }]}>
      <Animated.View style={[s.fill, { height }, fillStyle]} />
    </View>
  );
}

const s = StyleSheet.create({
  track: {
    width: '100%',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 4,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.18)',
  },
  fill: {
    backgroundColor: '#FFD700',
    borderRadius: 3,
    shadowColor: '#FFD700',
    shadowOpacity: 0.6,
    shadowRadius: 4,
    elevation: 2,
  },
});

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming,
  withSequence, withDelay, Easing,
} from 'react-native-reanimated';

interface HeroIdleAnimationProps {
  children: React.ReactNode;
  stars: number;
  size: number;
  color?: string;
  disableParticles?: boolean;
}

/**
 * HeroIdleAnimation - Wrapper animato per immagini eroi.
 *
 * Tutti:  breathing (scale pulse)
 * 6★+:   aura glow pulsante
 * 7★+:   particelle luce flottanti (max 4)
 */
export default function HeroIdleAnimation({ children, stars, size, color = '#FFD700', disableParticles = false }: HeroIdleAnimationProps) {
  const showAura = stars >= 6;
  const showParticles = stars >= 7 && !disableParticles;

  return (
    <View style={[st.container, { width: size, height: size }]}>
      {showAura && <AuraGlow size={size} color={color} stars={stars} />}
      {showParticles && <Particles size={size} color={color} count={Math.min(stars - 6, 4)} />}
      <Breathing stars={stars}>{children}</Breathing>
    </View>
  );
}

/** Breathing: scale 1 → 1.03, 2500ms loop */
function Breathing({ children, stars }: { children: React.ReactNode; stars: number }) {
  const scale = useSharedValue(1);
  const target = stars >= 10 ? 1.05 : stars >= 7 ? 1.04 : 1.03;

  useEffect(() => {
    scale.value = withRepeat(
      withSequence(
        withTiming(target, { duration: 1300, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 1200, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return <Animated.View style={anim}>{children}</Animated.View>;
}

/** Aura: glow cerchio pulsante dietro l'immagine */
function AuraGlow({ size, color, stars }: { size: number; color: string; stars: number }) {
  const opacity = useSharedValue(0.15);
  const maxOp = stars >= 10 ? 0.4 : stars >= 7 ? 0.3 : 0.2;

  useEffect(() => {
    opacity.value = withRepeat(
      withSequence(
        withTiming(maxOp, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
        withTiming(0.1, { duration: 1800, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  const spread = size * 0.2;
  return (
    <Animated.View style={[st.aura, anim, {
      width: size + spread * 2,
      height: size + spread * 2,
      borderRadius: (size + spread * 2) / 2,
      left: -spread,
      top: -spread,
      backgroundColor: color,
    }]} />
  );
}

/** Particles: punti luce flottanti attorno all'eroe */
function Particles({ size, color, count }: { size: number; color: string; count: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <Particle key={i} size={size} color={color} index={i} total={count} />
      ))}
    </>
  );
}

function Particle({ size, color, index, total }: {
  size: number; color: string; index: number; total: number;
}) {
  // Position: distribute around the hero
  const angle = (index / total) * Math.PI * 2 + Math.PI * 0.3;
  const radius = size * 0.45;
  const baseX = Math.cos(angle) * radius;
  const baseY = Math.sin(angle) * radius;

  const translateY = useSharedValue(0);
  const opacity = useSharedValue(0);
  const pSize = Math.max(2, size * 0.06);

  useEffect(() => {
    const dur = 2000 + index * 400;
    translateY.value = withDelay(index * 300,
      withRepeat(
        withSequence(
          withTiming(-size * 0.15, { duration: dur, easing: Easing.inOut(Easing.ease) }),
          withTiming(size * 0.05, { duration: dur * 0.8, easing: Easing.inOut(Easing.ease) }),
        ), -1, true,
      ),
    );
    opacity.value = withDelay(index * 300,
      withRepeat(
        withSequence(
          withTiming(0.8, { duration: dur * 0.6, easing: Easing.inOut(Easing.ease) }),
          withTiming(0, { duration: dur * 0.4, easing: Easing.inOut(Easing.ease) }),
        ), -1, true,
      ),
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  return (
    <Animated.View
      style={[st.particle, anim, {
        width: pSize,
        height: pSize,
        borderRadius: pSize / 2,
        backgroundColor: color,
        left: size / 2 + baseX - pSize / 2,
        top: size / 2 + baseY - pSize / 2,
      }]}
      pointerEvents="none"
    />
  );
}

const st = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center' },
  aura: { position: 'absolute' },
  particle: {
    position: 'absolute',
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 3,
  },
});

import React, { useEffect } from 'react';
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
 * Il container resta fermo. Solo l'immagine (children) respira.
 * Aura e particelle sono layer separati in position absolute.
 */
export default function HeroIdleAnimation({ children, stars, size, color = '#FFD700', disableParticles = false }: HeroIdleAnimationProps) {
  const showAura = stars >= 6;
  const showParticles = stars >= 7 && !disableParticles;

  return (
    <View style={[st.container, { width: size, height: size }]}>
      {/* Layer 0: Aura glow — behind everything */}
      {showAura && <AuraGlow size={size} color={color} stars={stars} />}
      {/* Layer 1: Breathing image — only children scale, container stays fixed */}
      <BreathingImage stars={stars} size={size}>{children}</BreathingImage>
      {/* Layer 2: Particles — on top, absolute */}
      {showParticles && <Particles size={size} color={color} count={Math.min(stars - 6, 4)} />}
    </View>
  );
}

/** Breathing: very subtle scale on the image only, container untouched */
function BreathingImage({ children, stars, size }: { children: React.ReactNode; stars: number; size: number }) {
  const scale = useSharedValue(1);
  const target = stars >= 10 ? 1.025 : stars >= 7 ? 1.02 : 1.015;

  useEffect(() => {
    scale.value = withRepeat(
      withSequence(
        withTiming(target, { duration: 1400, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 1300, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  // Fixed-size box so scale doesn't push layout
  return (
    <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
      <Animated.View style={anim}>
        {children}
      </Animated.View>
    </View>
  );
}

/** Aura: glow behind image, position absolute, no layout impact */
function AuraGlow({ size, color, stars }: { size: number; color: string; stars: number }) {
  const opacity = useSharedValue(0.1);
  const maxOp = stars >= 10 ? 0.35 : stars >= 7 ? 0.25 : 0.15;

  useEffect(() => {
    opacity.value = withRepeat(
      withSequence(
        withTiming(maxOp, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
        withTiming(0.08, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  const spread = size * 0.18;
  return (
    <Animated.View
      style={[st.aura, anim, {
        width: size + spread * 2,
        height: size + spread * 2,
        borderRadius: (size + spread * 2) / 2,
        left: -spread,
        top: -spread,
        backgroundColor: color,
      }]}
      pointerEvents="none"
    />
  );
}

/** Particles: floating light dots, absolute on top */
function Particles({ size, color, count }: { size: number; color: string; count: number }) {
  return (
    <View style={[st.particleLayer, { width: size, height: size }]} pointerEvents="none">
      {Array.from({ length: count }).map((_, i) => (
        <Particle key={i} size={size} color={color} index={i} total={count} />
      ))}
    </View>
  );
}

function Particle({ size, color, index, total }: {
  size: number; color: string; index: number; total: number;
}) {
  const angle = (index / total) * Math.PI * 2 + Math.PI * 0.3;
  const radius = size * 0.42;
  const baseX = Math.cos(angle) * radius;
  const baseY = Math.sin(angle) * radius;
  const pSize = Math.max(2, size * 0.055);

  const translateY = useSharedValue(0);
  const opacity = useSharedValue(0);

  useEffect(() => {
    const dur = 2200 + index * 350;
    translateY.value = withDelay(index * 250,
      withRepeat(
        withSequence(
          withTiming(-size * 0.12, { duration: dur, easing: Easing.inOut(Easing.ease) }),
          withTiming(size * 0.04, { duration: dur * 0.7, easing: Easing.inOut(Easing.ease) }),
        ), -1, true,
      ),
    );
    opacity.value = withDelay(index * 250,
      withRepeat(
        withSequence(
          withTiming(0.7, { duration: dur * 0.5, easing: Easing.inOut(Easing.ease) }),
          withTiming(0, { duration: dur * 0.5, easing: Easing.inOut(Easing.ease) }),
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
    />
  );
}

const st = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center' },
  aura: { position: 'absolute' },
  particleLayer: { position: 'absolute', top: 0, left: 0 },
  particle: {
    position: 'absolute',
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 2,
  },
});

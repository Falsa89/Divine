import React, { useEffect } from 'react';
import { View, StyleSheet, ImageSourcePropType } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming,
  withSequence, withDelay, Easing,
} from 'react-native-reanimated';
import { heroImageSource } from './hopliteAssets';

const AnimatedImage = Animated.Image;

interface HeroIdleAnimationProps {
  /** Pass imageUri for direct Animated.Image (preferred). */
  imageUri?: string;
  /** Fallback: wrap static children. */
  children?: React.ReactNode;
  stars: number;
  size: number;
  color?: string;
  disableParticles?: boolean;
  /** Border radius for the image. Default 12. */
  borderRadius?: number;
}

/**
 * HeroIdleAnimation
 *
 * Container FERMO. Transform applicato direttamente ad Animated.Image.
 * Aura: layer absolute DIETRO.
 * Particelle: layer absolute SOPRA.
 */
export default function HeroIdleAnimation({
  imageUri, children, stars, size, color = '#FFD700',
  disableParticles = false, borderRadius = 12,
}: HeroIdleAnimationProps) {
  const showAura = stars >= 6;
  const showParticles = stars >= 7 && !disableParticles;

  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);
  const scaleTarget = stars >= 10 ? 1.02 : stars >= 7 ? 1.018 : 1.012;

  useEffect(() => {
    scale.value = withRepeat(
      withSequence(
        withTiming(scaleTarget, { duration: 1400, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 1300, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
    translateY.value = withRepeat(
      withSequence(
        withTiming(-1.5, { duration: 1400, easing: Easing.inOut(Easing.ease) }),
        withTiming(0, { duration: 1300, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const breathStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }, { translateY: translateY.value }],
  }));

  return (
    <View style={[st.root, { width: size, height: size }]}>
      {showAura && <AuraGlow size={size} color={color} stars={stars} />}

      {imageUri ? (
        <AnimatedImage
          source={heroImageSource(imageUri)}
          style={[
            { width: size, height: size, borderRadius, zIndex: 1 },
            breathStyle,
          ]}
          resizeMode="cover"
        />
      ) : (
        <Animated.View style={[st.childLayer, { width: size, height: size }, breathStyle]}>
          {children}
        </Animated.View>
      )}

      {showParticles && <ParticleLayer size={size} color={color} count={Math.min(stars - 6, 4)} />}
    </View>
  );
}

function AuraGlow({ size, color, stars }: { size: number; color: string; stars: number }) {
  const opacity = useSharedValue(0.04);
  const maxOp = stars >= 10 ? 0.15 : stars >= 7 ? 0.10 : 0.06;

  useEffect(() => {
    opacity.value = withRepeat(
      withSequence(
        withTiming(maxOp, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
        withTiming(0.03, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
      ), -1, true,
    );
  }, []);

  const anim = useAnimatedStyle(() => ({ opacity: opacity.value }));
  const sp = size * 0.18;

  return (
    <Animated.View
      style={[st.aura, anim, {
        width: size + sp * 2, height: size + sp * 2,
        borderRadius: (size + sp * 2) / 2,
        left: -sp, top: -sp, backgroundColor: color,
      }]}
      pointerEvents="none"
    />
  );
}

function ParticleLayer({ size, color, count }: { size: number; color: string; count: number }) {
  return (
    <View style={[st.particles, { width: size, height: size }]} pointerEvents="none">
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
  const bx = Math.cos(angle) * radius;
  const by = Math.sin(angle) * radius;
  const ps = Math.max(2, size * 0.05);

  const ty = useSharedValue(0);
  const op = useSharedValue(0);

  useEffect(() => {
    const dur = 2200 + index * 350;
    ty.value = withDelay(index * 250,
      withRepeat(withSequence(
        withTiming(-size * 0.1, { duration: dur, easing: Easing.inOut(Easing.ease) }),
        withTiming(size * 0.03, { duration: dur * 0.7, easing: Easing.inOut(Easing.ease) }),
      ), -1, true),
    );
    op.value = withDelay(index * 250,
      withRepeat(withSequence(
        withTiming(0.65, { duration: dur * 0.5, easing: Easing.inOut(Easing.ease) }),
        withTiming(0, { duration: dur * 0.5, easing: Easing.inOut(Easing.ease) }),
      ), -1, true),
    );
  }, []);

  const anim = useAnimatedStyle(() => ({
    transform: [{ translateY: ty.value }],
    opacity: op.value,
  }));

  return (
    <Animated.View style={[st.dot, anim, {
      width: ps, height: ps, borderRadius: ps / 2, backgroundColor: color,
      left: size / 2 + bx - ps / 2, top: size / 2 + by - ps / 2,
    }]} />
  );
}

const st = StyleSheet.create({
  root: { position: 'relative' },
  aura: { position: 'absolute', zIndex: 0 },
  childLayer: { zIndex: 1, alignItems: 'center', justifyContent: 'center' },
  particles: { position: 'absolute', top: 0, left: 0, zIndex: 2 },
  dot: {
    position: 'absolute',
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 2,
  },
});

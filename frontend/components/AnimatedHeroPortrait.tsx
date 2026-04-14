import React, { useEffect } from 'react';
import { View, Image, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat,
  withTiming, withSequence, Easing, withDelay,
} from 'react-native-reanimated';

const RC: Record<number, string> = { 1:'#888', 2:'#44aa44', 3:'#4488ff', 4:'#aa44ff', 5:'#ff4444', 6:'#ffd700' };
const EC: Record<string, string> = { fire:'#ff4444', water:'#4488ff', earth:'#aa8844', wind:'#44cc88', light:'#ffd700', dark:'#9944ff', neutral:'#888' };

interface Props {
  imageUrl?: string | null;
  name: string;
  rarity: number;
  element?: string;
  size?: number;
  showName?: boolean;
  showStars?: boolean;
}

export default function AnimatedHeroPortrait({ imageUrl, name, rarity, element, size = 60, showName = false, showStars = false }: Props) {
  const rc = RC[rarity] || '#888';
  const ec = EC[element || 'neutral'] || '#888';

  // 5-star animations
  const sparkle1 = useSharedValue(0);
  const sparkle2 = useSharedValue(0);
  const sparkle3 = useSharedValue(0);
  const pulseGlow = useSharedValue(0.3);
  const borderPulse = useSharedValue(1);

  // 6-star animations
  const haloRotate = useSharedValue(0);
  const haloScale = useSharedValue(1);
  const shimmer = useSharedValue(0);
  const floatY = useSharedValue(0);

  useEffect(() => {
    if (rarity >= 5) {
      // Glow pulse
      pulseGlow.value = withRepeat(
        withSequence(
          withTiming(0.8, { duration: 1200, easing: Easing.inOut(Easing.ease) }),
          withTiming(0.3, { duration: 1200, easing: Easing.inOut(Easing.ease) }),
        ), -1, true
      );
      // Border pulse
      borderPulse.value = withRepeat(
        withSequence(
          withTiming(1.08, { duration: 800 }),
          withTiming(1, { duration: 800 }),
        ), -1, true
      );
      // Sparkles
      sparkle1.value = withRepeat(withSequence(
        withTiming(1, { duration: 600 }), withTiming(0, { duration: 600 }),
      ), -1, true);
      sparkle2.value = withDelay(400, withRepeat(withSequence(
        withTiming(1, { duration: 700 }), withTiming(0, { duration: 700 }),
      ), -1, true));
      sparkle3.value = withDelay(800, withRepeat(withSequence(
        withTiming(1, { duration: 500 }), withTiming(0, { duration: 500 }),
      ), -1, true));
    }

    if (rarity >= 6) {
      // Rotating halo
      haloRotate.value = withRepeat(
        withTiming(360, { duration: 6000, easing: Easing.linear }),
        -1
      );
      // Halo scale breathing
      haloScale.value = withRepeat(
        withSequence(
          withTiming(1.15, { duration: 1500 }),
          withTiming(1, { duration: 1500 }),
        ), -1, true
      );
      // Shimmer effect
      shimmer.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 2000 }),
          withTiming(0, { duration: 2000 }),
        ), -1, true
      );
      // Float
      floatY.value = withRepeat(
        withSequence(
          withTiming(-3, { duration: 1500, easing: Easing.inOut(Easing.ease) }),
          withTiming(3, { duration: 1500, easing: Easing.inOut(Easing.ease) }),
        ), -1, true
      );
    }
  }, [rarity]);

  // Animated styles
  const glowStyle = useAnimatedStyle(() => ({
    opacity: pulseGlow.value,
  }));

  const borderStyle = useAnimatedStyle(() => ({
    transform: [{ scale: borderPulse.value }],
  }));

  const spark1Style = useAnimatedStyle(() => ({
    opacity: sparkle1.value,
    transform: [{ scale: sparkle1.value }],
  }));
  const spark2Style = useAnimatedStyle(() => ({
    opacity: sparkle2.value,
    transform: [{ scale: sparkle2.value }],
  }));
  const spark3Style = useAnimatedStyle(() => ({
    opacity: sparkle3.value,
    transform: [{ scale: sparkle3.value }],
  }));

  const haloStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${haloRotate.value}deg` },
      { scale: haloScale.value },
    ],
    opacity: shimmer.value * 0.6 + 0.2,
  }));

  const floatStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: floatY.value }],
  }));

  const imgSize = size;
  const borderRadius = size * 0.16;

  return (
    <View style={[s.wrapper, { width: size + 16, height: size + (showName ? 30 : 8) + (showStars ? 14 : 0) }]}>
      {/* 6-star: Rotating halo ring */}
      {rarity >= 6 && (
        <Animated.View style={[s.haloRing, haloStyle, {
          width: imgSize + 20, height: imgSize + 20, borderRadius: (imgSize + 20) / 2,
          borderColor: '#ffd700', top: -2, left: -2,
        }]} />
      )}

      {/* 5+ star: Background glow */}
      {rarity >= 5 && (
        <Animated.View style={[s.glow, glowStyle, {
          width: imgSize + 12, height: imgSize + 12, borderRadius: (imgSize + 12) / 2,
          backgroundColor: rc, top: -2, left: 2,
        }]} />
      )}

      {/* Main image container with border animation */}
      <Animated.View style={[rarity >= 5 ? borderStyle : {}, rarity >= 6 ? floatStyle : {}]}>
        <View style={[s.imgBorder, {
          width: imgSize + 4, height: imgSize + 4, borderRadius: borderRadius + 2,
          borderColor: rc, borderWidth: rarity >= 5 ? 2.5 : rarity >= 3 ? 2 : 1.5,
        }]}>
          {imageUrl ? (
            <Image source={{ uri: imageUrl }} style={{ width: imgSize, height: imgSize, borderRadius }} resizeMode="cover" />
          ) : (
            <View style={[s.placeholder, { width: imgSize, height: imgSize, borderRadius, backgroundColor: ec + '25' }]}>
              <Text style={[s.initial, { color: ec, fontSize: imgSize * 0.4 }]}>{name?.[0] || '?'}</Text>
            </View>
          )}
        </View>
      </Animated.View>

      {/* 5+ star: Sparkle particles */}
      {rarity >= 5 && (
        <>
          <Animated.View style={[s.sparkle, spark1Style, { top: -2, right: 0 }]}>
            <Text style={[s.sparkleText, { color: rc, fontSize: 10 }]}>{'\u2728'}</Text>
          </Animated.View>
          <Animated.View style={[s.sparkle, spark2Style, { bottom: showName ? 28 : 6, left: -2 }]}>
            <Text style={[s.sparkleText, { color: '#ffd700', fontSize: 8 }]}>{'\u2B50'}</Text>
          </Animated.View>
          <Animated.View style={[s.sparkle, spark3Style, { top: imgSize * 0.3, right: -4 }]}>
            <Text style={[s.sparkleText, { color: '#fff', fontSize: 7 }]}>{'\u2726'}</Text>
          </Animated.View>
        </>
      )}

      {/* 6-star: Extra divine sparkles */}
      {rarity >= 6 && (
        <>
          <Animated.View style={[s.sparkle, spark1Style, { top: imgSize * 0.5, left: -6 }]}>
            <Text style={[s.sparkleText, { color: '#ffd700', fontSize: 9 }]}>{'\u2727'}</Text>
          </Animated.View>
          <Animated.View style={[s.sparkle, spark2Style, { bottom: showName ? 32 : 10, right: -4 }]}>
            <Text style={[s.sparkleText, { color: '#ffd700', fontSize: 11 }]}>{'\u2726'}</Text>
          </Animated.View>
        </>
      )}

      {/* Name */}
      {showName && (
        <Text style={[s.name, { color: rarity >= 5 ? rc : '#fff' }]} numberOfLines={1}>{name}</Text>
      )}

      {/* Stars */}
      {showStars && (
        <Text style={[s.stars, { color: rc }]}>{'\u2B50'.repeat(Math.min(rarity, 6))}</Text>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  glow: {
    position: 'absolute',
  },
  haloRing: {
    position: 'absolute',
    borderWidth: 2,
    borderStyle: 'dashed',
  },
  imgBorder: {
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  initial: {
    fontWeight: '900',
  },
  sparkle: {
    position: 'absolute',
  },
  sparkleText: {},
  name: {
    fontSize: 9,
    fontWeight: '700',
    marginTop: 3,
    textAlign: 'center',
  },
  stars: {
    fontSize: 7,
    marginTop: 1,
  },
});

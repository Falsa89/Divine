import React, { useEffect, useState } from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withSequence,
  withTiming, withDelay, withRepeat, Easing, cancelAnimation, withSpring,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { ELEMENTS, RARITY } from '../constants/theme';
import Constants from 'expo-constants';

type SpriteState = 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';

// Frame mapping: sprite sheet has 4 frames horizontally
// 0=idle, 1=attack, 2=hit, 3=skill
const STATE_TO_FRAME: Record<SpriteState, number> = {
  idle: 0, attack: 1, hit: 2, skill: 3, ultimate: 3, dead: 2, heal: 0, dodge: 0,
};

interface Props {
  character: any;
  state: SpriteState;
  isEnemy?: boolean;
  hpPercent: number;
  showDamage?: number | null;
  showHeal?: number | null;
  isCrit?: boolean;
  size?: number;
}

export default function BattleSprite({
  character, state, isEnemy = false, hpPercent,
  showDamage, showHeal, isCrit, size = 80,
}: Props) {
  const elemColor = ELEMENTS.colors[character?.element || character?.hero_element] || '#888';
  const rarColor = RARITY.colors[Math.min(character?.rarity || character?.hero_rarity || 1, 6)] || '#888';
  const heroName = character?.name || character?.hero_name || '?';

  // Build sprite URL
  const backendUrl = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';
  const spriteUrl = character?.sprite_url ? `${backendUrl}${character.sprite_url}` : null;
  const heroImage = character?.hero_image || character?.image;

  // Current frame based on state
  const [currentFrame, setCurrentFrame] = useState(0);

  useEffect(() => {
    setCurrentFrame(STATE_TO_FRAME[state] || 0);
  }, [state]);

  // Animation values
  const idleY = useSharedValue(0);
  const transX = useSharedValue(0);
  const bodyRot = useSharedValue(0);
  const spriteScale = useSharedValue(1);
  const spriteOp = useSharedValue(1);
  const hitFlash = useSharedValue(0);
  const auraOp = useSharedValue(0.15);
  const auraSc = useSharedValue(1);
  const dmgY = useSharedValue(0);
  const dmgOp = useSharedValue(0);
  const dmgScale = useSharedValue(0.5);
  const healFloatY = useSharedValue(0);
  const healFloatOp = useSharedValue(0);

  // Idle animation
  useEffect(() => {
    if (state === 'dead') return;
    idleY.value = withRepeat(withSequence(
      withTiming(-3, { duration: 1000, easing: Easing.inOut(Easing.ease) }),
      withTiming(3, { duration: 1000, easing: Easing.inOut(Easing.ease) }),
    ), -1, true);
    auraSc.value = withRepeat(withSequence(
      withTiming(1.12, { duration: 1500 }),
      withTiming(0.95, { duration: 1500 }),
    ), -1, true);
    auraOp.value = withRepeat(withSequence(
      withTiming(0.4, { duration: 1200 }),
      withTiming(0.1, { duration: 1200 }),
    ), -1, true);
  }, [state !== 'dead']);

  // State animations
  useEffect(() => {
    const dir = isEnemy ? -1 : 1;
    switch (state) {
      case 'attack':
        transX.value = withSequence(
          withTiming(dir * 22, { duration: 120 }),
          withTiming(dir * 26, { duration: 50 }),
          withTiming(0, { duration: 220 }),
        );
        spriteScale.value = withSequence(withTiming(1.1, { duration: 100 }), withTiming(1, { duration: 200 }));
        break;
      case 'hit':
        transX.value = withSequence(
          withTiming(-dir * 10, { duration: 60 }), withTiming(-dir * 6, { duration: 40 }), withTiming(0, { duration: 200 }),
        );
        hitFlash.value = withSequence(withTiming(0.6, { duration: 50 }), withTiming(0, { duration: 200 }));
        spriteScale.value = withSequence(withTiming(0.92, { duration: 60 }), withTiming(1, { duration: 150 }));
        bodyRot.value = withSequence(withTiming(-dir * 6, { duration: 60 }), withTiming(0, { duration: 180 }));
        break;
      case 'skill':
      case 'ultimate':
        auraOp.value = withSequence(withTiming(0.8, { duration: 150 }), withDelay(400, withTiming(0.15, { duration: 300 })));
        auraSc.value = withSequence(withTiming(1.5, { duration: 200 }), withTiming(1, { duration: 300 }));
        transX.value = withSequence(withTiming(dir * 16, { duration: 150 }), withTiming(0, { duration: 250 }));
        spriteScale.value = withSequence(withTiming(1.15, { duration: 150 }), withTiming(1, { duration: 250 }));
        break;
      case 'heal':
        auraOp.value = withSequence(withTiming(0.6, { duration: 300 }), withTiming(0.15, { duration: 500 }));
        idleY.value = withSequence(withTiming(-5, { duration: 250 }), withTiming(0, { duration: 250 }));
        break;
      case 'dodge':
        transX.value = withSequence(withTiming(-dir * 28, { duration: 100 }), withDelay(200, withTiming(0, { duration: 250 })));
        spriteOp.value = withSequence(withTiming(0.3, { duration: 80 }), withTiming(1, { duration: 200 }));
        break;
      case 'dead':
        cancelAnimation(idleY); cancelAnimation(auraSc); cancelAnimation(auraOp);
        idleY.value = 0;
        bodyRot.value = withTiming(isEnemy ? -20 : 20, { duration: 600 });
        spriteOp.value = withTiming(0.25, { duration: 800 });
        spriteScale.value = withTiming(0.85, { duration: 600 });
        auraOp.value = withTiming(0, { duration: 300 });
        break;
    }
  }, [state, isCrit]);

  // Damage float
  useEffect(() => {
    if (showDamage && showDamage > 0) {
      dmgY.value = 0; dmgOp.value = 0; dmgScale.value = isCrit ? 0.3 : 0.5;
      dmgOp.value = withSequence(withTiming(1, { duration: 80 }), withDelay(700, withTiming(0, { duration: 300 })));
      dmgY.value = withTiming(-50, { duration: 1000, easing: Easing.out(Easing.quad) });
      dmgScale.value = withSpring(isCrit ? 1.5 : 1.1);
    }
  }, [showDamage]);

  useEffect(() => {
    if (showHeal && showHeal > 0) {
      healFloatY.value = 0; healFloatOp.value = 0;
      healFloatOp.value = withSequence(withTiming(1, { duration: 120 }), withDelay(600, withTiming(0, { duration: 300 })));
      healFloatY.value = withTiming(-45, { duration: 900, easing: Easing.out(Easing.quad) });
    }
  }, [showHeal]);

  const mainStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: transX.value },
      { translateY: idleY.value },
      { rotate: `${bodyRot.value}deg` },
      { scale: spriteScale.value },
    ],
    opacity: spriteOp.value,
  }));
  const hitStyle = useAnimatedStyle(() => ({ opacity: hitFlash.value }));
  const auraStyle = useAnimatedStyle(() => ({ opacity: auraOp.value, transform: [{ scale: auraSc.value }] }));
  const dmgStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: dmgY.value }, { scale: dmgScale.value }], opacity: dmgOp.value,
  }));
  const healFStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: healFloatY.value }], opacity: healFloatOp.value,
  }));

  const hpColor = hpPercent > 60 ? '#44DD88' : hpPercent > 30 ? '#FFAA33' : '#FF3344';
  const frameWidth = size;
  const hasSpriteSheet = !!spriteUrl;

  return (
    <View style={[s.root, { width: size + 16 }]}>
      {/* Damage float */}
      <Animated.View style={[s.floatNum, dmgStyle]} pointerEvents="none">
        <Text style={[s.dmgText, isCrit && s.critText, { color: isCrit ? '#FFD700' : '#FF4444' }]}>
          {isCrit ? 'CRIT! ' : ''}-{showDamage?.toLocaleString()}
        </Text>
      </Animated.View>
      {/* Heal float */}
      <Animated.View style={[s.floatNum, healFStyle]} pointerEvents="none">
        <Text style={s.healFText}>+{showHeal?.toLocaleString()}</Text>
      </Animated.View>

      {/* Aura glow */}
      <Animated.View style={[s.aura, { backgroundColor: elemColor, width: size + 20, height: size + 20, borderRadius: (size + 20) / 2 }, auraStyle]} />

      <Animated.View style={mainStyle}>
        {/* Sprite Sheet Display */}
        {hasSpriteSheet ? (
          <View style={[s.spriteFrame, { width: size, height: size, borderRadius: size * 0.1, borderColor: rarColor }]}>
            {/* Clip the sprite sheet to show only the current frame */}
            <View style={{ width: size, height: size, overflow: 'hidden' }}>
              <Image
                source={{ uri: spriteUrl }}
                style={{
                  width: size * 4,
                  height: size,
                  marginLeft: -currentFrame * size,
                }}
                resizeMode="cover"
              />
            </View>
            {/* Hit flash */}
            <Animated.View style={[s.hitFlashOv, { borderRadius: size * 0.08 }, hitStyle]} />
            {/* Element badge */}
            <View style={[s.elemBadge, { backgroundColor: elemColor }]}>
              <Text style={s.elemIcon}>{ELEMENTS.icons[character?.element || character?.hero_element] || ''}</Text>
            </View>
          </View>
        ) : heroImage ? (
          <View style={[s.imgFrame, { width: size, height: size, borderRadius: size * 0.15, borderColor: rarColor, transform: [{ scaleX: isEnemy ? -1 : 1 }] }]}>
            <Image source={{ uri: heroImage }} style={[s.heroImg, { width: size - 4, height: size - 4, borderRadius: size * 0.12 }]} resizeMode="cover" />
            <Animated.View style={[s.hitFlashOv, { borderRadius: size * 0.12 }, hitStyle]} />
            <View style={[s.elemBadge, { backgroundColor: elemColor }]}>
              <Text style={s.elemIcon}>{ELEMENTS.icons[character?.element || character?.hero_element] || ''}</Text>
            </View>
          </View>
        ) : (
          <View style={[s.imgFrame, { width: size, height: size, borderRadius: size * 0.15, borderColor: rarColor, transform: [{ scaleX: isEnemy ? -1 : 1 }] }]}>
            <LinearGradient colors={[elemColor + '40', elemColor + '15']} style={[s.placeholder, { width: size - 4, height: size - 4, borderRadius: size * 0.12 }]}>
              <Text style={[s.initText, { color: elemColor, fontSize: size * 0.4 }]}>{heroName[0]}</Text>
            </LinearGradient>
            <Animated.View style={[s.hitFlashOv, { borderRadius: size * 0.12 }, hitStyle]} />
            <View style={[s.elemBadge, { backgroundColor: elemColor }]}>
              <Text style={s.elemIcon}>{ELEMENTS.icons[character?.element || character?.hero_element] || ''}</Text>
            </View>
          </View>
        )}
        <View style={[s.shadow, { width: size * 0.7, opacity: state === 'dead' ? 0.1 : 0.3 }]} />
      </Animated.View>
    </View>
  );
}

const s = StyleSheet.create({
  root: { alignItems: 'center', marginHorizontal: 2 },
  floatNum: { position: 'absolute', top: -15, zIndex: 200, alignItems: 'center' },
  dmgText: { fontSize: 14, fontWeight: '900', textShadowColor: '#000', textShadowRadius: 6, textShadowOffset: { width: 1, height: 1 } },
  critText: { fontSize: 18, letterSpacing: 2 },
  healFText: { fontSize: 14, fontWeight: '900', color: '#44DD88', textShadowColor: '#000', textShadowRadius: 6, textShadowOffset: { width: 1, height: 1 } },
  aura: { position: 'absolute', top: -2 },
  spriteFrame: {
    borderWidth: 0,
    overflow: 'hidden',
    backgroundColor: 'transparent',
  },
  imgFrame: {
    borderWidth: 0,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  heroImg: {},
  placeholder: { alignItems: 'center', justifyContent: 'center' },
  initText: { fontWeight: '900' },
  hitFlashOv: { ...StyleSheet.absoluteFillObject, backgroundColor: '#FF4444', zIndex: 10 },
  elemBadge: {
    position: 'absolute', bottom: 2, right: 2,
    width: 18, height: 18, borderRadius: 9,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1.5, borderColor: 'rgba(0,0,0,0.4)',
  },
  elemIcon: { fontSize: 10 },
  shadow: { height: 6, borderRadius: 20, backgroundColor: '#000', marginTop: 3 },
  heroName: { fontSize: 9, fontWeight: '900', marginTop: 2, textAlign: 'center', letterSpacing: 0.5 },
  hpWrap: { marginTop: 2, alignItems: 'center' },
  hpBg: { width: '100%', height: 5, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' },
  hpFill: { height: '100%', borderRadius: 3 },
});

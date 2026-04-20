/**
 * HomeHeroSplash
 * ================
 * Splash grande dell'eroe corrente di homepage.
 *
 * Animazioni PREMIUM non-battle-like:
 *  - RESPIRO (robust): scaleY oscilla tra 1.000 e 1.008 su 4500ms con easing
 *    sin. Ampiezza volutamente micro (0.8%) → leggibile ma mai invadente.
 *  - BLINK (robust): opacity dell'Image scende a 0.82 per 90ms ogni 4-7s
 *    random. Simula lo sbattito palpebra SENZA dover mappare la regione
 *    occhi di ogni eroe → funziona su qualsiasi splash (robusto al 100%).
 *
 * Tap → callback onPress (apre /sanctuary).
 * Se l'image_url è null (es. Borea senza asset o Hoplite local), usa
 * HeroPortrait che gestisce le regole di fallback locali.
 */
import React, { useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image as RNImage } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming,
  withSequence, withDelay, Easing, cancelAnimation,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import HeroPortrait, { isHopliteHero } from '../ui/HeroPortrait';

const RARITY_COLOR: Record<number, string> = {
  1: '#9AA5B1', 2: '#4ECDC4', 3: '#46A3FF',
  4: '#B05CFF', 5: '#FFB347', 6: '#FF4D6D',
};

type Props = {
  hero: {
    id: string;
    name: string;
    rarity?: number;
    element?: string;
    hero_class?: string;
    image_url?: string | null;
  } | null;
  source?: string;
  inTutorial?: boolean;
  width: number;
  height: number;
  onPress?: () => void;
};

export default function HomeHeroSplash({ hero, source, inTutorial, width, height, onPress }: Props) {
  const breathScaleY = useSharedValue(1);
  const blinkOpacity = useSharedValue(1);

  useEffect(() => {
    // RESPIRO: ampiezza micro, durata lunga, sinusoidale
    breathScaleY.value = withRepeat(
      withSequence(
        withTiming(1.008, { duration: 2250, easing: Easing.inOut(Easing.sin) }),
        withTiming(1.000, { duration: 2250, easing: Easing.inOut(Easing.sin) }),
      ), -1, false,
    );

    // BLINK: schedulato pseudo-random via withDelay+withRepeat
    const scheduleBlink = () => {
      // Ogni "tick" = 5-7s pausa + 90ms blink + 100ms recover
      const pauseMs = 5000 + Math.random() * 2000;
      blinkOpacity.value = withSequence(
        withDelay(pauseMs, withTiming(0.82, { duration: 90, easing: Easing.out(Easing.quad) })),
        withTiming(1, { duration: 110, easing: Easing.out(Easing.quad) }),
      );
    };
    // Partenza dopo breve delay
    const firstBlink = setTimeout(scheduleBlink, 2000);
    // Ripeti ogni ~6s (robusto anche senza callback onFinish)
    const interval = setInterval(scheduleBlink, 6500);

    return () => {
      cancelAnimation(breathScaleY);
      cancelAnimation(blinkOpacity);
      clearTimeout(firstBlink);
      clearInterval(interval);
    };
  }, []);

  const breathStyle = useAnimatedStyle(() => ({
    transform: [{ scaleY: breathScaleY.value }],
  }));
  const blinkStyle = useAnimatedStyle(() => ({
    opacity: blinkOpacity.value,
  }));

  if (!hero) {
    return (
      <View style={[st.root, { width, height }]}>
        <Text style={st.emptyTxt}>{'\uD83D\uDD2E'} Nessun eroe</Text>
      </View>
    );
  }

  const rarity = hero.rarity || 1;
  const col = RARITY_COLOR[rarity] || '#888';
  const isHop = isHopliteHero(hero.id, hero.name);
  const isBorea = hero.id === 'borea';

  return (
    <TouchableOpacity
      activeOpacity={0.9}
      onPress={onPress}
      style={[st.root, { width, height }]}
    >
      {/* Halo radiale di rarità */}
      <LinearGradient
        colors={[col + '25', col + '08', 'transparent']}
        style={st.halo}
        start={{ x: 0.5, y: 0.2 }}
        end={{ x: 0.5, y: 1 }}
      />

      {/* Splash ANIMATO */}
      <Animated.View style={[st.splashWrap, breathStyle, { height, width }]}>
        <Animated.View style={[blinkStyle, { flex: 1 }]}>
          {isHop ? (
            <HeroPortrait heroId={hero.id} heroName={hero.name} size={Math.min(width, height)} />
          ) : hero.image_url ? (
            <RNImage
              source={{ uri: hero.image_url }}
              style={{ width: '100%', height: '100%' }}
              resizeMode="cover"
            />
          ) : (
            // Fallback stilizzato per Borea / eroi senza asset
            <LinearGradient
              colors={isBorea
                ? ['#4A7BFF', '#1B2A4E', '#0A1020']
                : [col + '60', col + '20', '#0A0612']}
              style={st.fallback}
              start={{ x: 0.3, y: 0 }}
              end={{ x: 0.7, y: 1 }}
            >
              <Text style={[st.fallbackIcon, { color: col }]}>
                {isBorea ? '\uD83C\uDF2C\uFE0F' : hero.name?.[0]}
              </Text>
              {isBorea && (
                <Text style={st.fallbackSub}>Vento del Nord</Text>
              )}
            </LinearGradient>
          )}
        </Animated.View>
      </Animated.View>

      {/* Gradient overlay bottom per leggibilità label */}
      <LinearGradient
        colors={['transparent', 'rgba(10,6,18,0.4)', 'rgba(10,6,18,0.9)']}
        style={st.bottomFade}
        pointerEvents="none"
      />

      {/* Label identity */}
      <View style={st.label} pointerEvents="none">
        <Text style={[st.heroName, { color: col }]} numberOfLines={1}>{hero.name}</Text>
        <Text style={st.heroMeta} numberOfLines={1}>
          {'\u2605'.repeat(Math.min(rarity, 6))} {'\u2022'} {hero.element || ''} {'\u2022'} {hero.hero_class || ''}
        </Text>
        {inTutorial && (
          <View style={st.tutorialBadge}>
            <Text style={st.tutorialTxt}>{'\uD83C\uDF93'} Tutorial</Text>
          </View>
        )}
      </View>

      {/* Tap hint */}
      <View style={st.tapHint} pointerEvents="none">
        <Text style={st.tapHintTxt}>{'\uD83C\uDFDB\uFE0F'} Tocca per aprire il Santuario</Text>
      </View>
    </TouchableOpacity>
  );
}

const st = StyleSheet.create({
  root: {
    position: 'relative',
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#0A0612',
  },
  halo: { ...StyleSheet.absoluteFillObject, zIndex: 0 },
  splashWrap: { position: 'absolute', left: 0, top: 0, zIndex: 1, overflow: 'hidden' },
  fallback: {
    flex: 1, justifyContent: 'center', alignItems: 'center',
    padding: 20,
  },
  fallbackIcon: { fontSize: 96, fontWeight: '900', textAlign: 'center', marginBottom: 10 },
  fallbackName: { fontSize: 28, fontWeight: '900', textAlign: 'center', letterSpacing: 1 },
  fallbackSub: { color: '#AEC6FF', fontSize: 13, fontStyle: 'italic', marginTop: 4 },
  bottomFade: {
    position: 'absolute', bottom: 0, left: 0, right: 0, height: '40%', zIndex: 2,
  },
  label: {
    position: 'absolute', bottom: 34, left: 14, right: 14, zIndex: 3,
  },
  heroName: { fontSize: 22, fontWeight: '900', letterSpacing: 0.5 },
  heroMeta: { color: '#DDD', fontSize: 11, marginTop: 2, fontWeight: '700' },
  tutorialBadge: {
    marginTop: 4,
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(68, 170, 255, 0.25)',
    borderWidth: 1,
    borderColor: '#44AAFF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  tutorialTxt: { color: '#AEC6FF', fontSize: 10, fontWeight: '800' },
  tapHint: {
    position: 'absolute', bottom: 8, left: 14, right: 14, zIndex: 3,
    alignItems: 'center',
  },
  tapHintTxt: { color: 'rgba(255,255,255,0.55)', fontSize: 10, fontWeight: '600' },
  emptyTxt: { color: '#888', fontSize: 14, textAlign: 'center', marginTop: 100 },
});

/**
 * HomeHeroSplash — VERSIONE PROVVISORIA PULITA (Msg 424)
 * ========================================================
 * Splash grande dell'eroe corrente di homepage.
 *
 * STATO ATTUALE (transizione):
 *  - RESPIRO GLOBALE MICRO (scaleY 1.000 → 1.004 in 5000ms, sinusoidale).
 *    Ampiezza volutamente MINIMALE. Lasciato solo per non avere splash
 *    completamente statico. Questa NON è la soluzione finale.
 *  - BLINK GLOBALE RIMOSSO (era opacity pulse su TUTTO lo splash,
 *    riconosciuto come placeholder tecnico non corretto).
 *
 * PROSSIMA FASE (nuovo motore dedicato, non ancora implementato):
 *  - Blink REALE sugli occhi via regione `eyes` da heroAnimationConfig.
 *  - Respiro LOCALIZZATO sul torace via regione `chest`.
 *  - Extra capelli/accessori solo per eroi 5★ e 6★+.
 *  - NESSUN movimento globale dell'intera immagine.
 *
 * Tap → callback onPress (apre /sanctuary).
 */
import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image as RNImage } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming,
  withSequence, Easing, cancelAnimation,
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
  // RESPIRO globale MINIMALE (provvisorio — sarà sostituito da breath localizzato su torace)
  const breathScaleY = useSharedValue(1);

  useEffect(() => {
    breathScaleY.value = withRepeat(
      withSequence(
        withTiming(1.004, { duration: 2500, easing: Easing.inOut(Easing.sin) }),
        withTiming(1.000, { duration: 2500, easing: Easing.inOut(Easing.sin) }),
      ), -1, false,
    );
    return () => { cancelAnimation(breathScaleY); };
  }, []);

  const breathStyle = useAnimatedStyle(() => ({
    transform: [{ scaleY: breathScaleY.value }],
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

      {/* Splash — solo respiro globale MICRO (provvisorio) */}
      <Animated.View style={[st.splashWrap, breathStyle, { height, width }]}>
        {isHop ? (
          <HeroPortrait heroId={hero.id} heroName={hero.name} size={Math.min(width, height)} variant="card" />
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

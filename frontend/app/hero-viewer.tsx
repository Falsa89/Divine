import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Image, useWindowDimensions } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import {
  isGreekHoplite,
  GREEK_HOPLITE_DETAIL,
  GREEK_HOPLITE_ID,
  GREEK_HOPLITE_NAME,
  heroFullscreenSource,
  getHeroContract,
  getHeroUiFraming,
  hasHeroUiContract,
} from '../components/ui/hopliteAssets';
import { RARITY, ELEMENTS } from '../constants/theme';

export default function HeroViewerScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ heroId?: string; heroName?: string }>();
  const heroId = params.heroId;
  const heroNameParam = params.heroName;
  const { width, height } = useWindowDimensions();
  const [hero, setHero] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // RM1.17-R — Fullscreen portrait verticale con height-priority.
  // L'app resta landscape globalmente; qui usiamo height come dimensione
  // guida (portraitHeight = height*0.92) e width ricavato dall'aspect 2:3
  // della sorgente. Se UI contract ha verticalPriority=true applichiamo
  // il fit height-priority. Niente caption/nome sotto.
  const fullscreenFraming =
    hasHeroUiContract(heroId, hero?.name || heroNameParam)
      ? getHeroUiFraming(heroId, hero?.name || heroNameParam, 'fullscreen')
      : null;
  const contract = getHeroContract(heroId, hero?.name || heroNameParam);
  const useHeightPriority = fullscreenFraming?.verticalPriority === true;
  // Aspect della sorgente (portrait 2/3, square 1, landscape 3/2)
  const srcAspect =
    contract.crop.sourceAspect === 'portrait' ? 2 / 3
    : contract.crop.sourceAspect === 'landscape' ? 3 / 2
    : 1;
  // Target box: se height-priority → scala su altezza massimale (92%) e
  // larghezza derivata dall'aspect (clampata a 90% dello schermo per
  // sicurezza). Altrimenti comportamento legacy (square box Hoplite-like).
  let portraitHeight: number;
  let portraitWidth: number;
  if (useHeightPriority) {
    portraitHeight = Math.round(height * 0.92);
    portraitWidth = Math.min(Math.round(portraitHeight * srcAspect), Math.round(width * 0.9));
  } else {
    const fullscreenBox = Math.min(width * 0.78, height * 0.95);
    portraitWidth = fullscreenBox;
    portraitHeight = fullscreenBox;
  }

  // Short-circuit: se è Greek Hoplite usa splash locale, nessuna API necessaria
  const isHoplite =
    isGreekHoplite(heroId, heroNameParam) ||
    (heroId && String(heroId).startsWith(GREEK_HOPLITE_ID));

  useEffect(() => {
    if (isHoplite) {
      setHero({
        id: GREEK_HOPLITE_ID,
        name: GREEK_HOPLITE_NAME,
        hero_name: GREEK_HOPLITE_NAME,
        // FIX: Hoplite è ufficialmente un eroe 3★, non 5★. Override hardcoded
        // forzava 5★ nel viewer locale (short-circuit no-API), generando
        // mismatch con il resto della UI (collection, detail, combat).
        stars: 3,
        hero_rarity: 3,
        element: 'earth',
        hero_element: 'earth',
      });
      setLoading(false);
      return;
    }
    if (!heroId) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        // RM1.17-E: l'endpoint /api/hero/detail/{id} non esiste; usiamo
        // il catalog endpoint /api/heroes/{hero_id} che restituisce il
        // doc canonico con campi image_url e image (sentinel).
        const d = await apiCall(`/api/heroes/${heroId}`);
        setHero(d);
      } catch {}
      finally { setLoading(false); }
    })();
  }, [heroId, isHoplite]);

  if (loading) return (
    <View style={s.root}><ActivityIndicator size="large" color="#9944FF" /></View>
  );

  if (!hero) return (
    <Pressable style={s.root} onPress={() => router.back()}>
      <Text style={s.err}>Eroe non trovato</Text>
    </Pressable>
  );

  const rarCol = RARITY.colors[Math.min(hero.stars || hero.hero_rarity || 1, 6)] || '#888';
  const elemCol = ELEMENTS.colors[hero.element] || ELEMENTS.colors[hero.hero_element] || '#FFD700';
  const imgUri = hero.image || hero.hero_image;

  return (
    <Pressable style={s.root} onPress={() => router.back()}>
      <View style={s.scene}>
        {isHoplite ? (
          // Greek Hoplite: splash art verticale fullscreen (con sfondo).
          <Image
            source={GREEK_HOPLITE_DETAIL}
            style={{ width: portraitWidth, height: portraitHeight }}
            resizeMode="contain"
          />
        ) : (() => {
          // RM1.17-R — Fullscreen via UI contract: portrait verticale grande
          // (height-priority se verticalPriority=true) con contain puro.
          // Nessun crop distruttivo, volto sempre visibile, no caption.
          const fullscreenSrc = heroFullscreenSource(imgUri, heroId, hero.name || hero.hero_name);
          if (fullscreenSrc) {
            return (
              <Image
                source={fullscreenSrc}
                style={{ width: portraitWidth, height: portraitHeight }}
                resizeMode={contract.viewer.useContain ? 'contain' : 'cover'}
              />
            );
          }
          // Fallback placeholder se nessun asset disponibile
          return (
            <View style={[s.ph, { width: portraitHeight, height: portraitHeight, borderColor: rarCol }]}>
              <Text style={[s.phTxt, { color: elemCol, fontSize: portraitHeight * 0.35 }]}>
                {(hero.name || hero.hero_name || '?')[0]}
              </Text>
            </View>
          );
        })()}
      </View>

      <Text style={s.hint}>Tocca per chiudere</Text>
    </Pressable>
  );
}

const s = StyleSheet.create({
  root: {
    flex: 1, backgroundColor: '#000',
    justifyContent: 'center', alignItems: 'center',
    overflow: 'hidden',
  },
  scene: { alignItems: 'center' },
  ph: {
    borderWidth: 2, borderRadius: 0,
    backgroundColor: 'rgba(10,10,30,0.8)',
    alignItems: 'center', justifyContent: 'center',
  },
  phTxt: { fontWeight: '900' },
  hint: { color: 'rgba(255,255,255,0.15)', fontSize: 9, position: 'absolute', bottom: 16 },
  err: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
});

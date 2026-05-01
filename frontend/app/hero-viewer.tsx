import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Image, useWindowDimensions } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import {
  isGreekHoplite,
  GREEK_HOPLITE_DETAIL,
  GREEK_HOPLITE_ID,
  GREEK_HOPLITE_NAME,
  heroFullscreenSource,
  getHeroContract,
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

  // RM1.17-K — Fullscreen sizing Hoplite-like: la box è GRANDE e portrait-safe,
  // identica a Hoplite (square box sized to min(width*0.78, height*0.95)).
  // Il resizeMode='contain' letterboxa l'immagine mantenendo la sua aspect
  // ratio naturale senza ridurla a uno strip stretto. Per Berserker
  // (source 2:3 portrait) l'immagine riempie la larghezza, lascia strisce
  // sopra/sotto (o viceversa) secondo orientation del device.
  const contract = getHeroContract(heroId, hero?.name || heroNameParam);
  const fullscreenBox = Math.min(width * 0.78, height * 0.95);
  const portraitWidth = fullscreenBox;
  const portraitHeight = fullscreenBox;

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

  const stars = hero.stars || hero.hero_rarity || 1;
  const rarCol = RARITY.colors[Math.min(stars, 6)] || '#888';
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
          // RM1.17-G — Fullscreen via contract: usa splash portrait intera
          // con resizeMode='contain' → nessun crop distruttivo, volto
          // sempre visibile, orientation portrait anche se device landscape.
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

        {/* Info overlay al bottom */}
        <View style={s.info}>
          <Text style={[s.name, { color: rarCol }]}>{hero.name || hero.hero_name}</Text>
          <View style={s.starsRow}>
            {stars <= 12
              ? <StarDisplay stars={stars} size={16} />
              : <TranscendenceStars stars={stars} size={16} />}
          </View>
        </View>
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
  info: {
    alignItems: 'center', marginTop: 12, gap: 6,
  },
  name: { fontSize: 20, fontWeight: '900', letterSpacing: 1 },
  starsRow: { height: 22, justifyContent: 'center', alignItems: 'center' },
  hint: { color: 'rgba(255,255,255,0.15)', fontSize: 9, position: 'absolute', bottom: 16 },
  err: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
});

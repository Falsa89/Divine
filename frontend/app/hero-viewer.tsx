import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, useWindowDimensions } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import HeroIdleAnimation from '../components/ui/HeroIdleAnimation';
import HeroHopliteIdle from '../components/ui/HeroHopliteIdle';
import { isHopliteHero } from '../components/ui/HeroPortrait';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import { RARITY, ELEMENTS } from '../constants/theme';

export default function HeroViewerScreen() {
  const router = useRouter();
  const { heroId } = useLocalSearchParams<{ heroId: string }>();
  const { width, height } = useWindowDimensions();
  const [hero, setHero] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Image fills entire screen
  const imgSize = Math.max(width, height);

  useEffect(() => {
    if (!heroId) return;
    (async () => {
      try {
        const d = await apiCall(`/api/hero/detail/${heroId}`);
        setHero(d);
      } catch {}
      finally { setLoading(false); }
    })();
  }, [heroId]);

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
        {isHopliteHero(hero.name || hero.hero_name) ? (
          <HeroHopliteIdle size={imgSize} animated />
        ) : (
          <HeroIdleAnimation
            imageUri={imgUri || undefined}
            stars={stars}
            size={imgSize}
            color={elemCol}
            borderRadius={0}
          >
            {!imgUri && (
              <View style={[s.ph, { width: imgSize, height: imgSize, borderColor: rarCol }]}>
                <Text style={[s.phTxt, { color: elemCol, fontSize: imgSize * 0.35 }]}>
                  {(hero.name || hero.hero_name || '?')[0]}
                </Text>
              </View>
            )}
          </HeroIdleAnimation>
        )}

        {/* Info overlay at bottom */}
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

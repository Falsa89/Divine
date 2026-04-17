import React, { useState, useEffect } from 'react';
import { View, Text, Image, StyleSheet, Pressable, Dimensions, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import HeroIdleAnimation from '../components/ui/HeroIdleAnimation';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import { RARITY, ELEMENTS } from '../constants/theme';

const { width: SW, height: SH } = Dimensions.get('window');
const IMG_SIZE = Math.min(SW, SH) * 0.7;

export default function HeroViewerScreen() {
  const router = useRouter();
  const { heroId } = useLocalSearchParams<{ heroId: string }>();
  const [hero, setHero] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!heroId) return;
    (async () => {
      try {
        const detail = await apiCall(`/api/hero/detail/${heroId}`);
        setHero(detail);
      } catch { }
      finally { setLoading(false); }
    })();
  }, [heroId]);

  if (loading) return (
    <View style={s.root}><ActivityIndicator size="large" color="#9944FF" /></View>
  );

  if (!hero) return (
    <Pressable style={s.root} onPress={() => router.back()}>
      <Text style={s.errorTxt}>Eroe non trovato</Text>
    </Pressable>
  );

  const stars = hero.stars || hero.hero_rarity || 1;
  const rarCol = RARITY.colors[Math.min(stars, 6)] || '#888';
  const elemCol = ELEMENTS.colors[hero.element] || ELEMENTS.colors[hero.hero_element] || '#FFD700';

  return (
    <Pressable style={s.root} onPress={() => router.back()}>
      <View style={s.content}>
        <HeroIdleAnimation stars={stars} size={IMG_SIZE} color={elemCol}>
          {hero.image || hero.hero_image ? (
            <Image
              source={{ uri: hero.image || hero.hero_image }}
              style={{ width: IMG_SIZE, height: IMG_SIZE, borderRadius: 16 }}
              resizeMode="contain"
            />
          ) : (
            <View style={[s.placeholder, { width: IMG_SIZE, height: IMG_SIZE, borderColor: rarCol }]}>
              <Text style={[s.placeholderInit, { color: elemCol }]}>
                {(hero.name || hero.hero_name || '?')[0]}
              </Text>
            </View>
          )}
        </HeroIdleAnimation>

        <Text style={[s.name, { color: rarCol }]}>{hero.name || hero.hero_name}</Text>

        <View style={s.starsWrap}>
          {stars <= 12
            ? <StarDisplay stars={stars} size={18} />
            : <TranscendenceStars stars={stars} size={18} />}
        </View>

        <Text style={s.hint}>Tocca per chiudere</Text>
      </View>
    </Pressable>
  );
}

const s = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: { alignItems: 'center', gap: 12 },
  placeholder: {
    borderRadius: 16,
    borderWidth: 2,
    backgroundColor: 'rgba(10,10,30,0.8)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderInit: { fontSize: 64, fontWeight: '900' },
  name: { fontSize: 22, fontWeight: '900', letterSpacing: 1 },
  starsWrap: { height: 26, justifyContent: 'center', alignItems: 'center' },
  hint: { color: 'rgba(255,255,255,0.2)', fontSize: 10, marginTop: 20 },
  errorTxt: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
});

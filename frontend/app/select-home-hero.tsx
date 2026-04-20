/**
 * SELECT HOME HERO — selezione reale dell'eroe da mostrare in homepage.
 * =====================================================================
 *
 * Apertura: da Santuario → Azioni → "Seleziona eroe homepage".
 *
 * Mostra la LISTA COMPLETA degli eroi posseduti dal player.
 * Tap su un eroe:
 *   1. POST /api/sanctuary/home-hero  → aggiorna home_hero_id sul user
 *   2. Conferma visuale (bordo verde)
 *   3. Torna indietro (router.back) → la home legge il nuovo home-hero.
 *
 * L'eroe attualmente home ha badge "ATTUALE" ben visibile.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, Image as RNImage, Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import HeroPortrait, { isHopliteHero } from '../components/ui/HeroPortrait';

const RARITY_COLOR: Record<number, string> = {
  1: '#9AA5B1', 2: '#4ECDC4', 3: '#46A3FF',
  4: '#B05CFF', 5: '#FFB347', 6: '#FF4D6D',
};
const ELEMENT_EMOJI: Record<string, string> = {
  fire: '\uD83D\uDD25', water: '\uD83D\uDCA7', earth: '\u26F0\uFE0F',
  wind: '\uD83D\uDCA8', air: '\uD83C\uDF2C\uFE0F', thunder: '\u26A1',
  light: '\u2728', dark: '\uD83C\uDF11', neutral: '\u2694\uFE0F',
};

type OwnedHero = {
  id: string;                 // user_hero instance id
  hero_id: string;            // base catalog id (ciò che serve come home_hero_id)
  hero_name: string;
  hero_rarity?: number;
  hero_element?: string;
  hero_class?: string;
  hero_image?: string | null;
  stars?: number;
};

export default function SelectHomeHeroScreen() {
  const router = useRouter();
  const [owned, setOwned] = useState<OwnedHero[]>([]);
  const [currentHomeId, setCurrentHomeId] = useState<string | null>(null);
  const [inTutorial, setInTutorial] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);
  const [justSelectedId, setJustSelectedId] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [uh, hh] = await Promise.all([
          apiCall('/api/user/heroes').catch(() => []),
          apiCall('/api/sanctuary/home-hero').catch(() => null),
        ]);
        setOwned(Array.isArray(uh) ? uh : []);
        if (hh?.hero?.id) setCurrentHomeId(hh.hero.id);
        setInTutorial(!!hh?.in_tutorial);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Ordiniamo per rarità desc, poi nome
  const sorted = useMemo(() => {
    return [...owned].sort((a, b) => {
      const rd = (b.hero_rarity || 0) - (a.hero_rarity || 0);
      if (rd !== 0) return rd;
      return (a.hero_name || '').localeCompare(b.hero_name || '');
    });
  }, [owned]);

  const selectHero = async (h: OwnedHero) => {
    if (acting) return;
    setActing(h.hero_id);
    try {
      await apiCall('/api/sanctuary/home-hero', {
        method: 'POST',
        body: JSON.stringify({ hero_id: h.hero_id }),
      });
      setCurrentHomeId(h.hero_id);
      setJustSelectedId(h.hero_id);
      // Piccolo delay visivo poi torna indietro
      setTimeout(() => {
        router.back();
      }, 700);
    } catch (e: any) {
      Alert.alert('Errore', e?.message || 'Impossibile impostare eroe homepage');
    } finally {
      setActing(null);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={st.root}>
        <View style={st.loading}>
          <ActivityIndicator size="large" color="#FFD700" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={st.root} edges={['top']}>
      <LinearGradient colors={['#1a0e2e', '#0a0612']} style={st.header}>
        <View style={st.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={st.title}>{'\uD83C\uDFE0'} Eroe Homepage</Text>
            <Text style={st.subtitle}>
              Seleziona quale eroe mostrare come splash principale
            </Text>
          </View>
        </View>
      </LinearGradient>

      {inTutorial && (
        <View style={st.tutorialBanner}>
          <Text style={st.tutorialTxt}>
            {'\uD83C\uDF93'} Tutorial in corso: la homepage mostrerà Borea finché non termini il tutorial.
            La scelta qui verrà applicata dopo.
          </Text>
        </View>
      )}

      <ScrollView contentContainerStyle={st.body}>
        {sorted.length === 0 ? (
          <Text style={st.empty}>Nessun eroe posseduto ancora.</Text>
        ) : (
          sorted.map((h, i) => {
            const col = RARITY_COLOR[h.hero_rarity || 1] || '#888';
            const isCurrent = h.hero_id === currentHomeId;
            const isJust = h.hero_id === justSelectedId;
            const isHop = isHopliteHero(h.hero_id, h.hero_name);
            const isActing = acting === h.hero_id;
            return (
              <Animated.View key={h.id} entering={FadeInDown.delay(i * 18).duration(220)}>
                <TouchableOpacity
                  activeOpacity={0.85}
                  onPress={() => selectHero(h)}
                  disabled={!!acting}
                  style={[
                    st.row,
                    { borderColor: col + '40' },
                    isCurrent && { borderColor: '#44DD88', backgroundColor: 'rgba(68,221,136,0.06)' },
                    isJust && { borderColor: '#FFD700', backgroundColor: 'rgba(255,215,0,0.10)' },
                  ]}
                >
                  <View style={[st.portraitBox, { borderColor: col }]}>
                    {isHop ? (
                      <HeroPortrait heroId={h.hero_id} heroName={h.hero_name} size={64} variant="card" />
                    ) : h.hero_image ? (
                      <RNImage
                        source={{ uri: h.hero_image }}
                        style={{ width: 64, height: 64 }}
                        resizeMode="cover"
                      />
                    ) : (
                      <View style={[st.portraitFb, { backgroundColor: col + '22' }]}>
                        <Text style={[st.portraitFbTxt, { color: col }]}>{h.hero_name?.[0] || '?'}</Text>
                      </View>
                    )}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[st.name, { color: col }]} numberOfLines={1}>
                      {h.hero_name}
                    </Text>
                    <Text style={st.meta} numberOfLines={1}>
                      {'\u2605'.repeat(Math.min(h.hero_rarity || 1, 6))}
                      {h.hero_element ? `  ${ELEMENT_EMOJI[h.hero_element.toLowerCase()] || ''} ${h.hero_element}` : ''}
                      {h.hero_class ? `  \u2022 ${h.hero_class}` : ''}
                    </Text>
                  </View>
                  {isCurrent ? (
                    <View style={st.currentChip}>
                      <Text style={st.currentTxt}>{'\u2705'} ATTUALE</Text>
                    </View>
                  ) : isActing ? (
                    <ActivityIndicator size="small" color="#FFD700" />
                  ) : (
                    <Text style={st.arrow}>{'\u203A'}</Text>
                  )}
                </TouchableOpacity>
              </Animated.View>
            );
          })
        )}
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0a0612' },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  header: { paddingHorizontal: 14, paddingBottom: 12, paddingTop: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  backBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 8 },
  backTxt: { color: '#fff', fontSize: 13, fontWeight: '700' },
  title: { color: '#FFD700', fontSize: 17, fontWeight: '900' },
  subtitle: { color: '#BBB', fontSize: 11, marginTop: 2 },

  tutorialBanner: {
    marginHorizontal: 10, marginTop: 10,
    padding: 10,
    backgroundColor: 'rgba(68,170,255,0.08)',
    borderRadius: 8,
    borderWidth: 1, borderColor: 'rgba(68,170,255,0.3)',
  },
  tutorialTxt: { color: '#AEC6FF', fontSize: 11, lineHeight: 15 },

  body: { padding: 10, gap: 8 },
  empty: { color: '#888', fontSize: 13, textAlign: 'center', marginTop: 40 },

  row: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    padding: 10, borderRadius: 12, borderWidth: 1,
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  portraitBox: {
    width: 64, height: 64, borderRadius: 10, overflow: 'hidden',
    borderWidth: 2, backgroundColor: '#000',
  },
  portraitFb: {
    width: 64, height: 64,
    justifyContent: 'center', alignItems: 'center',
  },
  portraitFbTxt: { fontSize: 28, fontWeight: '900' },

  name: { fontSize: 15, fontWeight: '900' },
  meta: { color: '#CCC', fontSize: 11, marginTop: 3 },

  currentChip: {
    backgroundColor: 'rgba(68,221,136,0.14)',
    borderWidth: 1, borderColor: '#44DD88',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6,
  },
  currentTxt: { color: '#44DD88', fontSize: 10, fontWeight: '900' },

  arrow: { color: '#888', fontSize: 22, paddingHorizontal: 6 },
});

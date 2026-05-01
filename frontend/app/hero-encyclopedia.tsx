/**
 * HERO ENCYCLOPEDIA — scheda "catalogo/database" dell'eroe
 * =========================================================
 *
 * Vista di sola lettura per un eroe (posseduto o NON posseduto).
 * Si apre dalla Collezione Eroi con `?id=<base_hero_id>`.
 *
 * Offre un TOGGLE:
 *   [Base (Lv 1)]  [Max Potenziale]
 *
 * Base         → stats grezze al Lv 1 con stelle di base (rarità di evocazione)
 * Max Potenziale → stats scalate al Lv 100 con stelle MASSIME realmente
 *                  raggiungibili per l'eroe (MAX_STARS_BY_BASE),
 *                  skill potenziate, moltiplicatori finali.
 *
 * NB: nessun campo di inventario, nessun pulsante LIVELLA / FUSIONE.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, Image as RNImage,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useLocalSearchParams } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import HeroPortrait, { isHopliteHero } from '../components/ui/HeroPortrait';
import { heroPortraitSource } from '../components/ui/hopliteAssets';
import { apiCall } from '../utils/api';

const STAT_LABELS: Record<string, string> = {
  hp: 'HP', speed: 'VEL', physical_damage: 'DMG FIS', magic_damage: 'DMG MAG',
  physical_defense: 'DEF FIS', magic_defense: 'DEF MAG', healing: 'CURE',
  healing_received: 'CURE RIC', damage_rate: 'DMG RATE', penetration: 'PEN',
  dodge: 'SCHIV', crit_chance: 'CRIT%', crit_damage: 'CRIT DMG',
  hit_rate: 'HIT%', combo_rate: 'COMBO%', block_rate: 'BLOCK%',
};

const RARITY_COLOR: Record<number, string> = {
  1: '#9AA5B1', 2: '#4ECDC4', 3: '#46A3FF',
  4: '#B05CFF', 5: '#FFB347', 6: '#FF4D6D',
};
const RARITY_LABEL: Record<number, string> = {
  1: 'Comune', 2: 'Non Comune', 3: 'Raro',
  4: 'Epico', 5: 'Leggendario', 6: 'Divino',
};
const ELEMENT_EMOJI: Record<string, string> = {
  fire: '\uD83D\uDD25', water: '\uD83D\uDCA7', earth: '\u26F0\uFE0F',
  wind: '\uD83D\uDCA8', air: '\uD83C\uDF2C\uFE0F', thunder: '\u26A1',
  light: '\u2728', dark: '\uD83C\uDF11', neutral: '\u2694\uFE0F',
};

type SkillInfo = {
  id?: string; name?: string; icon?: string; type?: string;
  damage_mult?: number; description?: string; effect?: any;
  enhanced?: boolean;
};

type Projection = {
  level: number;
  level_cap: number;
  stars: number;
  stats: Record<string, any>;
  skills: Record<string, SkillInfo | null> & { star_bonus?: any };
  power?: number | null;
};

type EncyclopediaData = {
  hero_id: string;
  name: string;
  description?: string;
  element: string;
  hero_class: string;
  rarity: number;
  faction?: string;
  image?: string;
  base: Projection;
  max: Projection;
};

type Mode = 'base' | 'max';

export default function HeroEncyclopediaScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const heroId = params.id as string;
  const [data, setData] = useState<EncyclopediaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<Mode>('base');

  useEffect(() => {
    (async () => {
      try {
        const json = await apiCall(`/api/hero/encyclopedia/${heroId}`);
        setData(json);
      } catch (e) {
        console.warn('[encyclopedia] load failed', e);
      } finally {
        setLoading(false);
      }
    })();
  }, [heroId]);

  const proj: Projection | null = useMemo(() => {
    if (!data) return null;
    return mode === 'base' ? data.base : data.max;
  }, [data, mode]);

  if (loading) {
    return (
      <SafeAreaView style={st.root}>
        <View style={st.loading}>
          <ActivityIndicator size="large" color="#FFD700" />
        </View>
      </SafeAreaView>
    );
  }
  if (!data) {
    return (
      <SafeAreaView style={st.root}>
        <View style={st.loading}>
          <Text style={st.err}>Eroe non trovato</Text>
          <TouchableOpacity onPress={() => router.back()} style={[st.backBtn, { marginTop: 20 }]}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const rarity = data.rarity || 1;
  const rarCol = RARITY_COLOR[rarity] || '#999';
  const element = (data.element || 'neutral').toLowerCase();
  const isHop = isHopliteHero(data.hero_id, data.name);

  return (
    <SafeAreaView style={st.root} edges={['top']}>
      <LinearGradient colors={['#1a0e2e', '#0a0612']} style={st.header}>
        <View style={st.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={[st.title, { color: rarCol }]} numberOfLines={1}>
              {'\uD83D\uDCD6'} {data.name}
            </Text>
            <Text style={st.subtitle}>
              Scheda Enciclopedia {'\u2022'} {RARITY_LABEL[rarity]} ({'\u2605'}{rarity})
            </Text>
          </View>
        </View>
      </LinearGradient>

      {/* TOGGLE Base / Max Potenziale */}
      <View style={st.toggleWrap}>
        <TouchableOpacity
          onPress={() => setMode('base')}
          style={[st.toggleBtn, mode === 'base' && st.toggleBtnActive]}
          activeOpacity={0.8}
        >
          <Text style={[st.toggleTxt, mode === 'base' && st.toggleTxtActive]}>
            Base (Lv 1)
          </Text>
          <Text style={[st.toggleSub, mode === 'base' && { color: '#0a0612' }]}>
            {'\u2605'}{data.base.stars}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setMode('max')}
          style={[
            st.toggleBtn,
            mode === 'max' && [st.toggleBtnActive, { backgroundColor: '#FFD700' }],
          ]}
          activeOpacity={0.8}
        >
          <Text style={[st.toggleTxt, mode === 'max' && st.toggleTxtActive]}>
            Max Potenziale
          </Text>
          <Text style={[st.toggleSub, mode === 'max' && { color: '#0a0612' }]}>
            Lv {data.max.level} {'\u2022'} {'\u2605'}{data.max.stars}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={st.body}>
        {/* HERO CARD */}
        <Animated.View entering={FadeIn}>
          <LinearGradient
            colors={[rarCol + '20', 'rgba(10,10,40,0.6)']}
            style={[st.heroCard, { borderColor: rarCol + '60' }]}
          >
            <View style={st.heroRow}>
              <View style={[st.portraitBox, { borderColor: rarCol }]}>
                {isHop ? (
                  <HeroPortrait heroId={data.hero_id} heroName={data.name} size={96} />
                ) : data.image ? (
                  // RM1.17-K — usa HeroPortrait variant='detail' (splash +
                  // focusY crop) invece di raw RNImage cover 96×96 che
                  // tagliava il volto. aspect=1 (square box).
                  <HeroPortrait
                    heroId={data.hero_id}
                    heroName={data.name}
                    imageUri={data.image}
                    size={96}
                    aspect={1}
                    variant="detail"
                  />
                ) : (
                  <View style={st.portraitFallback}>
                    <Text style={st.portraitFallbackTxt}>{data.name?.[0] || '?'}</Text>
                  </View>
                )}
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[st.heroName, { color: rarCol }]} numberOfLines={1}>
                  {data.name}
                </Text>
                <Text style={st.heroMeta}>
                  {ELEMENT_EMOJI[element] || '\u2694\uFE0F'} {data.element} {'\u2022'} {data.hero_class}
                </Text>
                {data.faction ? (
                  <Text style={st.heroMetaSmall}>Fazione: {data.faction}</Text>
                ) : null}
                <View style={st.starsRow}>
                  {Array.from({ length: Math.min(proj!.stars, 15) }).map((_, i) => (
                    <Text key={i} style={[st.star, { color: mode === 'max' ? '#FFD700' : rarCol }]}>
                      {'\u2605'}
                    </Text>
                  ))}
                </View>
                <Text style={st.levelLabel}>
                  Lv {proj!.level} / Cap {proj!.level_cap}
                </Text>
                {proj!.power ? (
                  <View style={st.powerBadge}>
                    <Text style={st.powerTxt}>{'\u26A1'} Potere: {proj!.power.toLocaleString()}</Text>
                  </View>
                ) : null}
              </View>
            </View>
            {data.description ? (
              <Text style={st.heroDesc}>{data.description}</Text>
            ) : null}
          </LinearGradient>
        </Animated.View>

        {/* MODE BANNER */}
        <View style={[
          st.modeBanner,
          mode === 'max' ? { backgroundColor: 'rgba(255,215,0,0.10)', borderColor: '#FFD700' }
                         : { backgroundColor: 'rgba(255,255,255,0.04)', borderColor: '#666' },
        ]}>
          <Text style={[st.modeBannerTxt, mode === 'max' && { color: '#FFD700' }]}>
            {mode === 'base'
              ? `Visualizzazione: Base — stats e skill al Lv 1 con rarità di evocazione (${'\u2605'}${data.base.stars}).`
              : `Visualizzazione: Max Potenziale — Lv ${data.max.level} con stelle massime raggiungibili (${'\u2605'}${data.max.stars}).`}
          </Text>
        </View>

        {/* STATS */}
        <Text style={st.sectionTitle}>{'\uD83D\uDCCA'} Statistiche</Text>
        <View style={st.statsGrid}>
          {Object.entries(proj!.stats || {}).map(([stat, val]: [string, any], i) => (
            <Animated.View key={stat} entering={FadeInDown.delay(i * 12)}>
              <LinearGradient
                colors={['rgba(255,255,255,0.04)', 'rgba(255,255,255,0.01)']}
                style={st.statRow}
              >
                <Text style={st.statLabel}>{STAT_LABELS[stat] || stat}</Text>
                <Text style={[
                  st.statVal,
                  { color: mode === 'max' ? '#FFD700' : rarCol },
                ]}>
                  {typeof val === 'number' && val < 1 && val > 0
                    ? `${(val * 100).toFixed(1)}%`
                    : typeof val === 'number' ? val.toLocaleString() : String(val)}
                </Text>
              </LinearGradient>
            </Animated.View>
          ))}
        </View>

        {/* SKILLS */}
        <Text style={st.sectionTitle}>{'\u2728'} Skill</Text>
        <View style={st.skillsWrap}>
          {['active_1', 'active_2', 'passive_1', 'passive_2', 'passive_3', 'ultimate'].map((key) => {
            const skill = proj!.skills?.[key as keyof typeof proj.skills] as SkillInfo | null;
            if (!skill) {
              return (
                <View key={key} style={[st.skillCard, st.skillLocked]}>
                  <Text style={st.skillLockedTxt}>
                    {'\uD83D\uDD12'} {key.replace('_', ' ').toUpperCase()} {'\u2014'} Bloccata
                  </Text>
                </View>
              );
            }
            const skillCol =
              skill.type === 'ultimate' ? '#FFD700'
              : skill.type === 'passive' ? '#44DD88'
              : rarCol;
            return (
              <Animated.View key={key} entering={FadeInDown}>
                <LinearGradient
                  colors={[skillCol + '15', 'transparent']}
                  style={[st.skillCard, { borderColor: skillCol + '40' }]}
                >
                  <View style={st.skillTop}>
                    <View style={[st.skillIconWrap, { backgroundColor: skillCol + '25' }]}>
                      <Text style={st.skillIconTxt}>{skill.icon || '\u2728'}</Text>
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={[st.skillName, { color: skillCol }]}>{skill.name}</Text>
                      <Text style={st.skillType}>
                        {skill.type === 'ultimate' ? '\uD83D\uDC51 ULTIMATE'
                         : skill.type === 'passive' ? '\uD83D\uDEE1\uFE0F PASSIVA'
                         : '\u2694\uFE0F ATTIVA'}
                        {skill.enhanced ? '  \u2605 POTENZIATA' : ''}
                      </Text>
                    </View>
                    {skill.damage_mult ? (
                      <View style={[st.multBadge, { backgroundColor: skillCol + '20' }]}>
                        <Text style={[st.multTxt, { color: skillCol }]}>{skill.damage_mult}x</Text>
                      </View>
                    ) : null}
                  </View>
                  {skill.description ? (
                    <Text style={st.skillDesc}>{skill.description}</Text>
                  ) : null}
                  {skill.effect && typeof skill.effect === 'object' && (
                    <View style={st.effectsRow}>
                      {Object.entries(skill.effect).map(([ek, ev]) => (
                        <View key={ek} style={st.effectChip}>
                          <Text style={st.effectTxt}>
                            +{typeof ev === 'number' && (ev as number) < 1
                              ? `${((ev as number) * 100).toFixed(0)}%`
                              : String(ev)} {ek}
                          </Text>
                        </View>
                      ))}
                    </View>
                  )}
                </LinearGradient>
              </Animated.View>
            );
          })}
          {proj!.skills?.star_bonus && (
            <LinearGradient
              colors={['rgba(255,215,0,0.10)', 'rgba(255,215,0,0.02)']}
              style={[st.skillCard, { borderColor: '#FFD70060' }]}
            >
              <Text style={st.transcTitle}>
                {'\uD83D\uDC51'} {proj!.skills.star_bonus.name}
              </Text>
              <Text style={st.transcDesc}>{proj!.skills.star_bonus.description}</Text>
            </LinearGradient>
          )}
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0a0612' },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  err: { color: '#FF4D6D', fontSize: 14, fontWeight: '700' },

  header: { paddingHorizontal: 14, paddingBottom: 12, paddingTop: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  backBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 8 },
  backTxt: { color: '#fff', fontSize: 13, fontWeight: '700' },
  title: { fontSize: 18, fontWeight: '900', letterSpacing: 0.3 },
  subtitle: { color: '#BBB', fontSize: 11, marginTop: 2 },

  toggleWrap: {
    flexDirection: 'row', gap: 8, paddingHorizontal: 10, paddingVertical: 10,
    borderBottomColor: 'rgba(255,255,255,0.06)', borderBottomWidth: 1,
  },
  toggleBtn: {
    flex: 1, paddingVertical: 10, borderRadius: 10,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)',
    backgroundColor: 'rgba(255,255,255,0.04)', alignItems: 'center',
  },
  toggleBtnActive: { backgroundColor: '#4ECDC4', borderColor: '#4ECDC4' },
  toggleTxt: { color: '#DDD', fontSize: 13, fontWeight: '800' },
  toggleTxtActive: { color: '#0a0612', fontWeight: '900' },
  toggleSub: { color: '#888', fontSize: 10, marginTop: 2, fontWeight: '700' },

  body: { padding: 10, gap: 10 },

  heroCard: { padding: 12, borderRadius: 14, borderWidth: 1 },
  heroRow: { flexDirection: 'row', gap: 12 },
  portraitBox: {
    width: 96, height: 96, borderRadius: 12, overflow: 'hidden',
    borderWidth: 2, backgroundColor: '#000',
  },
  portraitFallback: {
    width: 96, height: 96, backgroundColor: '#222',
    justifyContent: 'center', alignItems: 'center',
  },
  portraitFallbackTxt: { color: '#666', fontSize: 40, fontWeight: '900' },

  heroName: { fontSize: 18, fontWeight: '900' },
  heroMeta: { color: '#CCC', fontSize: 12, marginTop: 3 },
  heroMetaSmall: { color: '#888', fontSize: 10, marginTop: 2 },
  starsRow: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 6, gap: 1 },
  star: { fontSize: 12 },
  levelLabel: { color: '#999', fontSize: 11, marginTop: 4, fontWeight: '700' },
  powerBadge: {
    alignSelf: 'flex-start', marginTop: 6,
    backgroundColor: 'rgba(255,215,0,0.12)',
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.3)',
  },
  powerTxt: { color: '#FFD700', fontSize: 10, fontWeight: '900' },
  heroDesc: { color: '#BBB', fontSize: 11, marginTop: 10, lineHeight: 16, fontStyle: 'italic' },

  modeBanner: {
    padding: 10, borderRadius: 8, borderWidth: 1,
  },
  modeBannerTxt: { color: '#CCC', fontSize: 11, fontWeight: '600' },

  sectionTitle: { color: '#FFD700', fontSize: 14, fontWeight: '900', marginTop: 6, marginBottom: 2 },

  statsGrid: { gap: 3 },
  statRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingVertical: 7, paddingHorizontal: 12, borderRadius: 6,
  },
  statLabel: { color: '#BBB', fontSize: 11, fontWeight: '700' },
  statVal: { fontSize: 12, fontWeight: '900' },

  skillsWrap: { gap: 6 },
  skillCard: {
    padding: 10, borderRadius: 10, borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  skillLocked: { opacity: 0.35 },
  skillLockedTxt: { color: '#888', fontSize: 10 },
  skillTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  skillIconWrap: {
    width: 34, height: 34, borderRadius: 8,
    alignItems: 'center', justifyContent: 'center',
  },
  skillIconTxt: { fontSize: 18 },
  skillName: { fontSize: 13, fontWeight: '900' },
  skillType: { color: '#888', fontSize: 9, marginTop: 1, fontWeight: '700' },
  multBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  multTxt: { fontSize: 13, fontWeight: '900' },
  skillDesc: { color: '#CCC', fontSize: 10, marginTop: 6, lineHeight: 14 },
  effectsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 5 },
  effectChip: {
    paddingHorizontal: 6, paddingVertical: 2,
    backgroundColor: 'rgba(68,221,136,0.12)', borderRadius: 4,
  },
  effectTxt: { color: '#44DD88', fontSize: 9, fontWeight: '700' },

  transcTitle: { color: '#FFD700', fontSize: 13, fontWeight: '900' },
  transcDesc: { color: '#CCC', fontSize: 10, marginTop: 4 },
});

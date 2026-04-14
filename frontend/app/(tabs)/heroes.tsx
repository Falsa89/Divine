import React, { useState, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeInDown, FadeIn } from 'react-native-reanimated';
import { apiCall } from '../../utils/api';
import { useAuth } from '../../context/AuthContext';
import AnimatedHeroPortrait from '../../components/AnimatedHeroPortrait';
import ScreenHeader from '../../components/ui/ScreenHeader';
import { COLORS, RARITY, ELEMENTS, CLASSES } from '../../constants/theme';

const { width } = Dimensions.get('window');

export default function HeroesTab() {
  const router = useRouter();
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('rarity');

  useEffect(() => { load(); }, []);
  const load = async () => {
    try {
      const d = await apiCall('/api/user/heroes');
      setHeroes(d || []);
    } catch(e){} finally { setLoading(false); }
  };

  const sorted = [...heroes].sort((a: any, b: any) => {
    if (sortBy === 'rarity') return (b.stars || b.hero_rarity || 0) - (a.stars || a.hero_rarity || 0);
    if (sortBy === 'level') return (b.level || 0) - (a.level || 0);
    if (sortBy === 'class') return (a.hero_class || '').localeCompare(b.hero_class || '');
    return 0;
  });

  const elements = ['all', 'fire', 'water', 'earth', 'wind', 'thunder', 'light', 'shadow'];
  const filtered = filter === 'all' ? sorted : sorted.filter((h: any) => h.hero_element === filter);

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.accent} />
    </LinearGradient>
  );

  const starDisplay = (stars: number) => {
    if (stars <= 6) return '\u2B50'.repeat(stars);
    return `${stars}\u2B50`;
  };

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      {/* Header */}
      <ScreenHeader
        title="Collezione Eroi"
        rightContent={
          <View style={s.countBadge}>
            <Text style={s.countText}>{heroes.length} eroi</Text>
          </View>
        }
      />

      {/* Filters */}
      <View style={s.filterRow}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.filters}>
          {elements.map(f => {
            const isActive = filter === f;
            const elemColor = f !== 'all' ? ELEMENTS.colors[f] : COLORS.accent;
            return (
              <TouchableOpacity
                key={f}
                style={[s.fBtn, isActive && { backgroundColor: elemColor + '20', borderColor: elemColor }]}
                onPress={() => setFilter(f)}
              >
                <Text style={[s.fTxt, isActive && { color: elemColor }]}>
                  {f === 'all' ? 'Tutti' : f[0].toUpperCase() + f.slice(1)}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
        <View style={s.sortRow}>
          {(['rarity', 'level', 'class'] as string[]).map(sb => (
            <TouchableOpacity
              key={sb}
              style={[s.sortBtn, sortBy === sb && s.sortBtnA]}
              onPress={() => setSortBy(sb)}
            >
              <Text style={[s.sortTxt, sortBy === sb && s.sortTxtA]}>
                {sb === 'rarity' ? '\u2B50' : sb === 'level' ? 'Lv' : '\u2694'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={s.body}>
        {/* Grid */}
        <ScrollView style={s.grid} contentContainerStyle={s.gridC}>
          {filtered.map((h: any, i: number) => {
            const stars = h.stars || h.hero_rarity || 1;
            const rarityIdx = Math.min(stars, 6);
            const col = RARITY.colors[rarityIdx] || '#888';
            const bgAlpha = RARITY.bgAlpha[rarityIdx] || 'rgba(136,153,170,0.08)';
            const isSelected = selected?.id === h.id;
            return (
              <Animated.View key={h.id} entering={FadeInDown.delay(i * 12).duration(200)}>
                <TouchableOpacity
                  style={[
                    s.card,
                    { borderColor: col + '50', backgroundColor: bgAlpha },
                    isSelected && { borderColor: col, backgroundColor: col + '15' },
                  ]}
                  onPress={() => setSelected(h)}
                  onLongPress={() => router.push({ pathname: '/hero-detail', params: { id: h.id } })}
                  activeOpacity={0.7}
                >
                  <AnimatedHeroPortrait
                    imageUrl={h.hero_image}
                    name={h.hero_name || '?'}
                    rarity={Math.min(h.hero_rarity || 1, 6)}
                    element={h.hero_element}
                    size={48}
                    showName
                    showStars
                  />
                  {stars > 6 && (
                    <LinearGradient
                      colors={[col, col + 'CC']}
                      style={s.starBadge}
                    >
                      <Text style={s.starBadgeTxt}>{stars}\u2B50</Text>
                    </LinearGradient>
                  )}
                  <Text style={s.cardLvl}>Lv.{h.level || 1}</Text>
                </TouchableOpacity>
              </Animated.View>
            );
          })}
          {filtered.length === 0 && (
            <View style={s.emptyState}>
              <Text style={s.emptyIcon}>{'\u2694\uFE0F'}</Text>
              <Text style={s.emptyText}>Nessun eroe trovato</Text>
            </View>
          )}
        </ScrollView>

        {/* Detail panel */}
        {selected && (
          <Animated.View entering={FadeIn.duration(200)} style={s.detailOuter}>
            <LinearGradient
              colors={['rgba(20,20,60,0.9)', 'rgba(10,10,40,0.95)']}
              style={[s.detail, { borderColor: RARITY.colors[Math.min(selected.stars || selected.hero_rarity || 1, 6)] || '#888' }]}
            >
              {selected.hero_image ? (
                <View style={s.detImgWrap}>
                  <Image source={{ uri: selected.hero_image }} style={s.detImg} resizeMode="cover" />
                  <LinearGradient
                    colors={['transparent', 'rgba(10,10,40,0.8)']}
                    style={s.detImgOverlay}
                  />
                </View>
              ) : (
                <View style={[s.detImgPh, { backgroundColor: (ELEMENTS.colors[selected.hero_element] || '#888') + '20' }]}>
                  <Text style={[s.detInit, { color: ELEMENTS.colors[selected.hero_element] }]}>{selected.hero_name?.[0]}</Text>
                </View>
              )}
              <Text style={[s.detName, { color: RARITY.colors[Math.min(selected.stars || selected.hero_rarity || 1, 6)] }]}>
                {selected.hero_name}
              </Text>
              <Text style={s.detStars}>{starDisplay(selected.stars || selected.hero_rarity || 1)}</Text>
              <Text style={[s.detElem, { color: ELEMENTS.colors[selected.hero_element] }]}>
                {CLASSES.icons[selected.hero_class] || ''} {selected.hero_class} {'\u2022'} {selected.hero_element?.toUpperCase()}
              </Text>

              {/* Key stats */}
              <View style={s.statGrid}>
                {selected.hero_stats && Object.entries(selected.hero_stats).slice(0, 8).map(([k, v]: [string, any]) => (
                  <View key={k} style={s.statItem}>
                    <Text style={s.statLabel}>{k.replace(/_/g, ' ').slice(0, 8)}</Text>
                    <Text style={s.statVal}>
                      {typeof v === 'number' && v < 1 && v > 0 ? `${(v * 100).toFixed(0)}%` : typeof v === 'number' ? v.toLocaleString() : String(v)}
                    </Text>
                  </View>
                ))}
              </View>

              <View style={s.detLvlBadge}>
                <Text style={s.detLvl}>Livello {selected.level || 1}</Text>
              </View>

              <TouchableOpacity
                style={s.detailBtn}
                onPress={() => router.push({ pathname: '/hero-detail', params: { id: selected.id } })}
                activeOpacity={0.7}
              >
                <LinearGradient
                  colors={[COLORS.accent, '#FF4444']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={s.detailBtnGrad}
                >
                  <Text style={s.detailBtnTxt}>DETTAGLIO</Text>
                </LinearGradient>
              </TouchableOpacity>
            </LinearGradient>
          </Animated.View>
        )}
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  countBadge: {
    backgroundColor: 'rgba(255,107,53,0.15)',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderAccent,
  },
  countText: { color: COLORS.accent, fontSize: 10, fontWeight: '700' },
  // Filters
  filterRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 4 },
  filters: { gap: 4, paddingHorizontal: 8, alignItems: 'center' },
  fBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  fTxt: { color: COLORS.textDim, fontSize: 9, fontWeight: '700' },
  sortRow: { flexDirection: 'row', gap: 3, paddingRight: 8 },
  sortBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.03)',
  },
  sortBtnA: { backgroundColor: 'rgba(255,215,0,0.12)', borderWidth: 1, borderColor: 'rgba(255,215,0,0.25)' },
  sortTxt: { color: COLORS.textDim, fontSize: 10 },
  sortTxtA: { color: COLORS.gold },
  // Body
  body: { flex: 1, flexDirection: 'row', padding: 4, gap: 6 },
  grid: { flex: 1 },
  gridC: { flexDirection: 'row', flexWrap: 'wrap', gap: 5, paddingBottom: 60 },
  card: {
    width: 70,
    padding: 4,
    borderRadius: 10,
    borderWidth: 1.5,
    alignItems: 'center',
  },
  starBadge: {
    position: 'absolute',
    top: 2,
    right: 2,
    paddingHorizontal: 4,
    paddingVertical: 1,
    borderRadius: 6,
  },
  starBadgeTxt: { color: '#000', fontSize: 7, fontWeight: '900' },
  cardLvl: { color: COLORS.textMuted, fontSize: 8, marginTop: 1, fontWeight: '600' },
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 40 },
  emptyIcon: { fontSize: 32, marginBottom: 8 },
  emptyText: { color: COLORS.textDim, fontSize: 12 },
  // Detail panel
  detailOuter: { width: 180 },
  detail: {
    flex: 1,
    borderRadius: 14,
    borderWidth: 1.5,
    overflow: 'hidden',
  },
  detImgWrap: { width: '100%', height: 90, position: 'relative' },
  detImg: { width: '100%', height: '100%' },
  detImgOverlay: { position: 'absolute', bottom: 0, left: 0, right: 0, height: 40 },
  detImgPh: {
    width: '100%',
    height: 90,
    alignItems: 'center',
    justifyContent: 'center',
  },
  detInit: { fontSize: 36, fontWeight: '900' },
  detName: { fontSize: 13, fontWeight: '900', textAlign: 'center', paddingHorizontal: 8, marginTop: 4 },
  detStars: { color: COLORS.gold, fontSize: 10, textAlign: 'center', marginTop: 2 },
  detElem: { fontSize: 9, fontWeight: '700', textAlign: 'center', marginTop: 2 },
  statGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 2, marginTop: 6, paddingHorizontal: 8 },
  statItem: {
    width: '48%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 4,
    paddingVertical: 2,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 4,
  },
  statLabel: { color: COLORS.textMuted, fontSize: 7, fontWeight: '600' },
  statVal: { color: COLORS.textSecondary, fontSize: 7, fontWeight: '800' },
  detLvlBadge: {
    alignSelf: 'center',
    marginTop: 6,
    paddingHorizontal: 12,
    paddingVertical: 2,
    borderRadius: 8,
    backgroundColor: 'rgba(255,215,0,0.1)',
  },
  detLvl: { color: COLORS.gold, fontSize: 11, fontWeight: '800' },
  detailBtn: {
    marginHorizontal: 8,
    marginTop: 8,
    marginBottom: 10,
    borderRadius: 8,
    overflow: 'hidden',
  },
  detailBtnGrad: {
    paddingVertical: 7,
    alignItems: 'center',
    borderRadius: 8,
  },
  detailBtnTxt: { color: '#fff', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
});

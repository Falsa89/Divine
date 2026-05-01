import React, { useState, useCallback, useMemo } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, Dimensions, TextInput,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useFocusEffect } from 'expo-router';
import Animated, { FadeInDown, FadeIn } from 'react-native-reanimated';
import { apiCall } from '../../utils/api';
import { useAuth } from '../../context/AuthContext';
import AnimatedHeroPortrait from '../../components/AnimatedHeroPortrait';
import { isGreekHoplite, GREEK_HOPLITE_PORTRAIT, heroPortraitSource } from '../../components/ui/hopliteAssets';
import ScreenHeader from '../../components/ui/ScreenHeader';
import StarDisplay from '../../components/ui/StarDisplay';
import TranscendenceStars from '../../components/ui/TranscendenceStars';
import { COLORS, RARITY, ELEMENTS, CLASSES } from '../../constants/theme';

const { width } = Dimensions.get('window');

export default function HeroesTab() {
  const router = useRouter();
  const { userHeroesVersion } = useAuth();
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('rarity');
  const [searchText, setSearchText] = useState('');
  const [minStars, setMinStars] = useState(1);
  const [classFilter, setClassFilter] = useState('all');

  const load = async () => {
    try {
      const d = await apiCall('/api/user/heroes');
      setHeroes(d || []);
    } catch(e){} finally { setLoading(false); }
  };

  // RM1.16-B: refresh on focus + on userHeroesVersion bump (post-summon).
  // Sostituisce il vecchio useEffect(load, []) che caricava una sola volta.
  useFocusEffect(
    useCallback(() => {
      load();
    }, [userHeroesVersion]),
  );

  const elements = ['all', 'fire', 'water', 'earth', 'wind', 'thunder', 'light', 'shadow'];
  const classOptions = ['all', 'DPS', 'Tank', 'Support'];
  const starOptions = [1, 3, 5, 7, 10, 13];

  const filtered = useMemo(() => {
    let list = [...heroes];
    // Search
    if (searchText.trim()) {
      const q = searchText.trim().toLowerCase();
      list = list.filter(h => (h.hero_name || '').toLowerCase().includes(q));
    }
    // Element
    if (filter !== 'all') list = list.filter(h => h.hero_element === filter);
    // Class
    if (classFilter !== 'all') list = list.filter(h => h.hero_class === classFilter);
    // Min stars
    if (minStars > 1) list = list.filter(h => (h.stars || h.hero_rarity || 1) >= minStars);
    // Sort: primary by selected, secondary always stars DESC then level DESC
    list.sort((a: any, b: any) => {
      if (sortBy === 'rarity') {
        const diff = (b.stars || b.hero_rarity || 0) - (a.stars || a.hero_rarity || 0);
        return diff !== 0 ? diff : (b.level || 0) - (a.level || 0);
      }
      if (sortBy === 'level') {
        const diff = (b.level || 0) - (a.level || 0);
        return diff !== 0 ? diff : (b.stars || b.hero_rarity || 0) - (a.stars || a.hero_rarity || 0);
      }
      if (sortBy === 'class') {
        const diff = (a.hero_class || '').localeCompare(b.hero_class || '');
        return diff !== 0 ? diff : (b.stars || b.hero_rarity || 0) - (a.stars || a.hero_rarity || 0);
      }
      return 0;
    });
    return list;
  }, [heroes, searchText, filter, classFilter, minStars, sortBy]);

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.accent} />
    </LinearGradient>
  );

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      {/* Header */}
      <ScreenHeader
        title="Collezione Eroi"
        rightContent={
          <View style={s.countBadge}>
            <Text style={s.countText}>{filtered.length}/{heroes.length}</Text>
          </View>
        }
      />

      {/* Filters */}
      <View style={s.filterSection}>
        {/* Search + sort row */}
        <View style={s.searchRow}>
          <View style={s.searchBox}>
            <Text style={s.searchIcon}>Q</Text>
            <TextInput
              style={s.searchInput}
              placeholder="Cerca eroe..."
              placeholderTextColor="rgba(255,255,255,0.25)"
              value={searchText}
              onChangeText={setSearchText}
            />
            {searchText.length > 0 && (
              <TouchableOpacity onPress={() => setSearchText('')} style={s.searchClear}>
                <Text style={s.searchClearTxt}>X</Text>
              </TouchableOpacity>
            )}
          </View>
          <View style={s.sortRow}>
            {(['rarity', 'level', 'class'] as string[]).map(sb => (
              <TouchableOpacity
                key={sb}
                style={[s.sortBtn, sortBy === sb && s.sortBtnA]}
                onPress={() => setSortBy(sb)}
              >
                <Text style={[s.sortTxt, sortBy === sb && s.sortTxtA]}>
                  {sb === 'rarity' ? 'Stelle' : sb === 'level' ? 'Livello' : 'Classe'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        {/* Element + class + stars filters */}
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
                  {f === 'all' ? 'Tutti' : (ELEMENTS.icons[f] || '') + ' ' + f[0].toUpperCase() + f.slice(1)}
                </Text>
              </TouchableOpacity>
            );
          })}
          <View style={s.filterDivider} />
          {classOptions.map(c => {
            const isActive = classFilter === c;
            const clsColor = c !== 'all' ? (CLASSES.colors[c] || COLORS.accent) : COLORS.accent;
            return (
              <TouchableOpacity
                key={c}
                style={[s.fBtn, isActive && { backgroundColor: clsColor + '20', borderColor: clsColor }]}
                onPress={() => setClassFilter(c)}
              >
                <Text style={[s.fTxt, isActive && { color: clsColor }]}>
                  {c === 'all' ? 'Tutte' : (CLASSES.icons[c] || '') + ' ' + c}
                </Text>
              </TouchableOpacity>
            );
          })}
          <View style={s.filterDivider} />
          {starOptions.map(ms => (
            <TouchableOpacity
              key={ms}
              style={[s.fBtn, minStars === ms && { backgroundColor: COLORS.gold + '20', borderColor: COLORS.gold }]}
              onPress={() => setMinStars(minStars === ms ? 1 : ms)}
            >
              <Text style={[s.fTxt, minStars === ms && { color: COLORS.gold }]}>
                {ms}+
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
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
                    heroId={h.hero_id || h.id}
                    imageUrl={h.hero_image}
                    name={h.hero_name || '?'}
                    rarity={Math.min(h.hero_rarity || 1, 6)}
                    element={h.hero_element}
                    size={48}
                    showName
                    showStars
                  />
                  {stars > 6 && (
                    <View style={s.starBadge}>
                      <View style={s.starBadgeInner}>
                        {stars <= 12
                          ? <StarDisplay stars={stars} size={8} />
                          : <TranscendenceStars stars={stars} size={8} />}
                      </View>
                    </View>
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
              <ScrollView
                style={s.detailScroll}
                contentContainerStyle={s.detailScrollContent}
                showsVerticalScrollIndicator={false}
              >
              {isGreekHoplite(selected.hero_id || selected.id, selected.hero_name) ? (
                <View style={s.detImgPortraitWrap}>
                  <Image
                    source={GREEK_HOPLITE_PORTRAIT}
                    style={s.detImgPortrait}
                    resizeMode="contain"
                  />
                  <LinearGradient
                    colors={['transparent', 'rgba(10,10,40,0.9)']}
                    style={s.detImgOverlay}
                  />
                </View>
              ) : selected.hero_image ? (
                <View style={s.detImgWrap}>
                  <Image
                    source={heroPortraitSource(selected.hero_image, selected.hero_id || selected.id, selected.hero_name)}
                    style={s.detImg}
                    resizeMode="cover"
                  />
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
              <View style={s.detStarsWrap}>
                {(selected.stars || selected.hero_rarity || 1) <= 12
                  ? <StarDisplay stars={selected.stars || selected.hero_rarity || 1} size={10} />
                  : <TranscendenceStars stars={selected.stars || selected.hero_rarity || 1} size={10} />}
              </View>
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
              </ScrollView>
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
  // Filter section
  filterSection: { gap: 3, paddingBottom: 2 },
  searchRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, gap: 6 },
  searchBox: {
    flex: 1, flexDirection: 'row', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 6,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    paddingHorizontal: 8, height: 28,
  },
  searchIcon: { color: 'rgba(255,255,255,0.2)', fontSize: 10, fontWeight: '900', marginRight: 4 },
  searchInput: { flex: 1, color: '#fff', fontSize: 10, padding: 0 },
  searchClear: { padding: 2 },
  searchClearTxt: { color: 'rgba(255,255,255,0.4)', fontSize: 9, fontWeight: '900' },
  filterDivider: { width: 1, height: 14, backgroundColor: 'rgba(255,255,255,0.1)', marginHorizontal: 2 },
  // Filters
  filters: { gap: 3, paddingHorizontal: 8, alignItems: 'center' },
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
    paddingHorizontal: 2,
    paddingVertical: 1,
    borderRadius: 6,
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  starBadgeInner: {
    height: 12,
    justifyContent: 'center',
    alignItems: 'center',
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
  // ScrollView interna al detail panel: garantisce che il bottone "DETTAGLIO"
  // resti raggiungibile anche per eroi con portrait grande (es. Hoplite con
  // detImgPortraitWrap height:170) quando la somma dei children eccede
  // l'altezza disponibile del body in landscape mobile.
  detailScroll: { flex: 1 },
  detailScrollContent: { paddingBottom: 4 },
  detImgWrap: { width: '100%', height: 90, position: 'relative' },
  detImg: { width: '100%', height: '100%' },
  // Layout portrait per splash verticali (es. Hoplite): più alto, image intera con resizeMode contain
  detImgPortraitWrap: {
    width: '100%',
    height: 170,
    position: 'relative',
    backgroundColor: 'rgba(0,0,0,0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  detImgPortrait: { width: '100%', height: '100%' },
  detImgOverlay: { position: 'absolute', bottom: 0, left: 0, right: 0, height: 40 },
  detImgPh: {
    width: '100%',
    height: 90,
    alignItems: 'center',
    justifyContent: 'center',
  },
  detInit: { fontSize: 36, fontWeight: '900' },
  detName: { fontSize: 13, fontWeight: '900', textAlign: 'center', paddingHorizontal: 8, marginTop: 4 },
  detStarsWrap: {
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginTop: 2,
  },
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

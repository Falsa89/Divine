/**
 * HERO COLLECTION — pagina "Collezione Eroi"
 * =================================================================
 *
 * Mostra l'INTERO roster del gioco confrontandolo con il roster posseduto
 * dall'utente. Gli eroi posseduti sono visibili normalmente; quelli non
 * posseduti sono scuri/silhouette ma CLICCABILI (aprono preview).
 *
 * Data sources:
 *   GET /api/heroes        → roster completo del gioco (sempre disponibile)
 *   GET /api/user/heroes   → eroi posseduti dall'utente
 *
 * Routing: accessibile da home.tsx via voce "Collezione" (/hero-collection).
 * Tap su eroe posseduto → /hero-detail?id=<...>
 * Tap su eroe non posseduto → modale locked con preview stats base.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, Modal, Image as RNImage,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useAuth } from '../context/AuthContext';

const API = process.env.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_BACKEND_URL || '';

type Hero = {
  id: string;
  name: string;
  rarity?: number;
  element?: string;
  hero_class?: string;
  faction?: string;
  image_url?: string;
  sprite_url?: string;
  description?: string;
  max_hp?: number;
  attack?: number;
  defense?: number;
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
  air: '\uD83C\uDF2C\uFE0F', light: '\u2728', dark: '\uD83C\uDF11',
  neutral: '\u2694\uFE0F',
};

// Filtri possibili
type FilterRarity = 'all' | 1 | 2 | 3 | 4 | 5 | 6;
type FilterOwned = 'all' | 'owned' | 'locked';

export default function HeroCollection() {
  const router = useRouter();
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [allHeroes, setAllHeroes] = useState<Hero[]>([]);
  const [ownedIds, setOwnedIds] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Hero | null>(null);
  const [filterRarity, setFilterRarity] = useState<FilterRarity>('all');
  const [filterOwned, setFilterOwned] = useState<FilterOwned>('all');

  useEffect(() => {
    (async () => {
      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const [allRes, ownedRes] = await Promise.all([
          fetch(`${API}/api/heroes`),
          fetch(`${API}/api/user/heroes`, { headers }),
        ]);
        const all = await allRes.json();
        const owned = await ownedRes.json();
        setAllHeroes(Array.isArray(all) ? all : []);
        const ids = new Set<string>(
          (Array.isArray(owned) ? owned : [])
            .map((u: any) => u.hero_id || u.id)
            .filter(Boolean),
        );
        setOwnedIds(ids);
      } catch (e) {
        console.warn('[HeroCollection] fetch failed', e);
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  // Ordina per rarità desc, poi per posseduti prima
  const filtered = useMemo(() => {
    let list = [...allHeroes];
    if (filterRarity !== 'all') {
      list = list.filter(h => h.rarity === filterRarity);
    }
    if (filterOwned === 'owned') {
      list = list.filter(h => ownedIds.has(h.id));
    } else if (filterOwned === 'locked') {
      list = list.filter(h => !ownedIds.has(h.id));
    }
    list.sort((a, b) => {
      const ownA = ownedIds.has(a.id) ? 0 : 1;
      const ownB = ownedIds.has(b.id) ? 0 : 1;
      if (ownA !== ownB) return ownA - ownB;  // posseduti prima
      return (b.rarity || 0) - (a.rarity || 0);  // poi rarità desc
    });
    return list;
  }, [allHeroes, ownedIds, filterRarity, filterOwned]);

  const totalOwned = ownedIds.size;
  const totalHeroes = allHeroes.length;
  const completionPct = totalHeroes > 0 ? Math.round((totalOwned / totalHeroes) * 100) : 0;

  const openHero = (h: Hero) => {
    if (ownedIds.has(h.id)) {
      router.push({ pathname: '/hero-detail', params: { id: h.id } } as any);
    } else {
      setSelected(h);
    }
  };

  return (
    <SafeAreaView style={st.root} edges={['top']}>
      <LinearGradient colors={['#1a0e2e', '#0a0612']} style={st.header}>
        <View style={st.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={st.title}>{'\uD83D\uDCDA Collezione Eroi'}</Text>
            <Text style={st.subtitle}>
              {totalOwned} / {totalHeroes} posseduti {'\u2022'} {completionPct}%
            </Text>
          </View>
        </View>
        {/* Progress bar */}
        <View style={st.progressTrack}>
          <View style={[st.progressFill, { width: `${completionPct}%` }]} />
        </View>
      </LinearGradient>

      {/* Filters */}
      <View style={st.filters}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6, paddingHorizontal: 10 }}>
          {(['all', 'owned', 'locked'] as const).map(f => (
            <TouchableOpacity
              key={f}
              onPress={() => setFilterOwned(f)}
              style={[st.filterPill, filterOwned === f && st.filterPillActive]}
            >
              <Text style={[st.filterTxt, filterOwned === f && st.filterTxtActive]}>
                {f === 'all' ? 'Tutti' : f === 'owned' ? 'Posseduti' : 'Non posseduti'}
              </Text>
            </TouchableOpacity>
          ))}
          <View style={{ width: 10 }} />
          {([['all','Tutti'], [6,'★6'], [5,'★5'], [4,'★4'], [3,'★3'], [2,'★2'], [1,'★1']] as const).map(([val, label]) => (
            <TouchableOpacity
              key={String(val)}
              onPress={() => setFilterRarity(val as FilterRarity)}
              style={[
                st.filterPill,
                filterRarity === val && {
                  backgroundColor: (typeof val === 'number' ? RARITY_COLOR[val] : '#FFD700') + '30',
                  borderColor: typeof val === 'number' ? RARITY_COLOR[val] : '#FFD700',
                },
              ]}
            >
              <Text style={[
                st.filterTxt,
                filterRarity === val && {
                  color: typeof val === 'number' ? RARITY_COLOR[val] : '#FFD700',
                  fontWeight: '900',
                },
              ]}>{label}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Grid */}
      {loading ? (
        <View style={st.loading}><ActivityIndicator size="large" color="#FFD700" /></View>
      ) : (
        <ScrollView contentContainerStyle={st.grid}>
          {filtered.length === 0 && (
            <Text style={st.empty}>Nessun eroe trovato con questi filtri.</Text>
          )}
          {filtered.map(h => {
            const owned = ownedIds.has(h.id);
            const rarity = h.rarity || 1;
            const color = RARITY_COLOR[rarity] || '#999';
            const element = (h.element || 'neutral').toLowerCase();
            return (
              <TouchableOpacity
                key={h.id}
                style={[st.card, { borderColor: owned ? color : '#333' }]}
                onPress={() => openHero(h)}
                activeOpacity={0.75}
              >
                <LinearGradient
                  colors={
                    owned
                      ? [color + '38', color + '10', 'transparent']
                      : ['#1a1a1a', '#0a0a0a']
                  }
                  style={st.cardBg}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                >
                  {/* Portrait */}
                  <View style={st.portraitBox}>
                    {h.image_url ? (
                      <RNImage
                        source={{ uri: h.image_url }}
                        style={[st.portrait, !owned && st.portraitLocked]}
                        resizeMode="cover"
                      />
                    ) : (
                      <View style={st.portraitFallback}>
                        <Text style={st.portraitFallbackTxt}>{h.name?.[0] || '?'}</Text>
                      </View>
                    )}
                    {!owned && (
                      <View style={st.lockOverlay} pointerEvents="none">
                        <Text style={st.lockIcon}>{'\uD83D\uDD12'}</Text>
                      </View>
                    )}
                    {/* Rarity badge */}
                    <View style={[st.rarityBadge, { backgroundColor: color }]}>
                      <Text style={st.rarityTxt}>{'\u2605'}{rarity}</Text>
                    </View>
                    {/* Element */}
                    <View style={st.elementBadge}>
                      <Text style={st.elementTxt}>{ELEMENT_EMOJI[element] || '\u2694\uFE0F'}</Text>
                    </View>
                  </View>
                  {/* Name */}
                  <Text
                    numberOfLines={1}
                    style={[st.name, !owned && { color: '#666' }]}
                  >
                    {owned ? h.name : h.name}
                  </Text>
                  <Text style={[st.classTxt, !owned && { color: '#555' }]} numberOfLines={1}>
                    {h.hero_class || '-'}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      )}

      {/* Locked Hero Modal */}
      <Modal
        visible={!!selected}
        transparent
        animationType="fade"
        onRequestClose={() => setSelected(null)}
      >
        <View style={st.modalBackdrop}>
          <View style={st.modalBox}>
            {selected && (
              <>
                <View style={st.modalHeader}>
                  <Text style={st.modalTitle}>{selected.name}</Text>
                  <TouchableOpacity onPress={() => setSelected(null)}>
                    <Text style={st.modalClose}>{'\u2715'}</Text>
                  </TouchableOpacity>
                </View>
                <View style={[st.modalPortrait, { borderColor: RARITY_COLOR[selected.rarity || 1] || '#666' }]}>
                  {selected.image_url ? (
                    <RNImage
                      source={{ uri: selected.image_url }}
                      style={[st.modalImg, st.portraitLocked]}
                      resizeMode="cover"
                    />
                  ) : (
                    <View style={st.portraitFallback}><Text style={st.portraitFallbackTxt}>{selected.name?.[0]}</Text></View>
                  )}
                  <View style={st.modalLockOverlay}>
                    <Text style={st.modalLockIcon}>{'\uD83D\uDD12'}</Text>
                    <Text style={st.modalLockTxt}>NON POSSEDUTO</Text>
                  </View>
                </View>
                <View style={st.modalStats}>
                  <StatRow label="Rarità" value={`${'\u2605'.repeat(selected.rarity || 1)} ${RARITY_LABEL[selected.rarity || 1]}`} color={RARITY_COLOR[selected.rarity || 1]} />
                  <StatRow label="Elemento" value={`${ELEMENT_EMOJI[(selected.element || 'neutral').toLowerCase()] || ''} ${selected.element || '-'}`} />
                  <StatRow label="Classe" value={selected.hero_class || '-'} />
                  <StatRow label="Fazione" value={selected.faction || '-'} />
                  {selected.max_hp && <StatRow label="HP Base" value={String(selected.max_hp)} />}
                  {selected.attack && <StatRow label="ATK Base" value={String(selected.attack)} />}
                  {selected.defense && <StatRow label="DEF Base" value={String(selected.defense)} />}
                </View>
                {selected.description && (
                  <Text style={st.modalDesc}>{selected.description}</Text>
                )}
                <TouchableOpacity
                  style={st.gachaBtn}
                  onPress={() => { setSelected(null); router.push('/(tabs)/gacha' as any); }}
                >
                  <LinearGradient colors={['#FFD700', '#CC9900']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={st.gachaBtnInner}>
                    <Text style={st.gachaBtnTxt}>{'\uD83C\uDFB0 Prova al Gacha'}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

function StatRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <View style={st.statRow}>
      <Text style={st.statLabel}>{label}</Text>
      <Text style={[st.statValue, color && { color }]}>{value}</Text>
    </View>
  );
}

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0a0612' },
  header: { paddingHorizontal: 14, paddingBottom: 12, paddingTop: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  backBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 8 },
  backTxt: { color: '#fff', fontSize: 13, fontWeight: '700' },
  title: { color: '#FFD700', fontSize: 20, fontWeight: '900', letterSpacing: 0.4 },
  subtitle: { color: '#BBB', fontSize: 12, marginTop: 2 },
  progressTrack: { height: 6, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 3, marginTop: 10, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: '#FFD700' },

  filters: { paddingVertical: 8, borderBottomColor: 'rgba(255,255,255,0.06)', borderBottomWidth: 1 },
  filterPill: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)', backgroundColor: 'rgba(255,255,255,0.04)' },
  filterPillActive: { backgroundColor: 'rgba(255,215,0,0.15)', borderColor: '#FFD700' },
  filterTxt: { color: '#CCC', fontSize: 11, fontWeight: '600' },
  filterTxtActive: { color: '#FFD700', fontWeight: '900' },

  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  grid: {
    padding: 8,
    flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'flex-start',
  },
  empty: { color: '#888', fontStyle: 'italic', marginTop: 32, textAlign: 'center', width: '100%' },

  card: { width: '31%', aspectRatio: 0.72, borderWidth: 2, borderRadius: 10, overflow: 'hidden', marginBottom: 4 },
  cardBg: { flex: 1, padding: 6, alignItems: 'center' },
  portraitBox: { width: '100%', aspectRatio: 1, borderRadius: 8, overflow: 'hidden', marginBottom: 4, position: 'relative', backgroundColor: '#000' },
  portrait: { width: '100%', height: '100%' },
  portraitLocked: { opacity: 0.25, tintColor: '#222' },
  portraitFallback: { width: '100%', height: '100%', backgroundColor: '#222', justifyContent: 'center', alignItems: 'center' },
  portraitFallbackTxt: { color: '#666', fontSize: 32, fontWeight: '900' },
  lockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.55)', justifyContent: 'center', alignItems: 'center' },
  lockIcon: { fontSize: 28 },
  rarityBadge: { position: 'absolute', top: 4, left: 4, paddingHorizontal: 5, paddingVertical: 1, borderRadius: 4 },
  rarityTxt: { color: '#fff', fontSize: 9, fontWeight: '900' },
  elementBadge: { position: 'absolute', top: 4, right: 4, backgroundColor: 'rgba(0,0,0,0.7)', width: 22, height: 22, borderRadius: 11, justifyContent: 'center', alignItems: 'center' },
  elementTxt: { fontSize: 12 },
  name: { color: '#FFF', fontSize: 11, fontWeight: '800', textAlign: 'center', width: '100%' },
  classTxt: { color: '#999', fontSize: 9, textAlign: 'center', marginTop: 1 },

  modalBackdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', alignItems: 'center', padding: 16 },
  modalBox: { width: '100%', maxWidth: 400, backgroundColor: '#1a0e2e', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#333' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  modalTitle: { color: '#FFD700', fontSize: 18, fontWeight: '900' },
  modalClose: { color: '#fff', fontSize: 20, padding: 4 },
  modalPortrait: { width: '100%', aspectRatio: 1.4, borderRadius: 10, overflow: 'hidden', borderWidth: 2, marginBottom: 12, backgroundColor: '#000', position: 'relative' },
  modalImg: { width: '100%', height: '100%' },
  modalLockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.55)', justifyContent: 'center', alignItems: 'center' },
  modalLockIcon: { fontSize: 56, marginBottom: 8 },
  modalLockTxt: { color: '#FF4D6D', fontSize: 14, fontWeight: '900', letterSpacing: 2 },
  modalStats: { gap: 6, marginBottom: 10 },
  statRow: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: 'rgba(255,255,255,0.04)', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 6 },
  statLabel: { color: '#999', fontSize: 12 },
  statValue: { color: '#fff', fontSize: 12, fontWeight: '700' },
  modalDesc: { color: '#CCC', fontSize: 12, fontStyle: 'italic', marginBottom: 12, lineHeight: 18 },
  gachaBtn: { borderRadius: 10, overflow: 'hidden' },
  gachaBtnInner: { paddingVertical: 12, alignItems: 'center' },
  gachaBtnTxt: { color: '#1a0e2e', fontSize: 14, fontWeight: '900', letterSpacing: 0.5 },
});

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown, FadeInUp, ZoomIn } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import StarDisplay from '../components/ui/StarDisplay';
import { COLORS, RARITY, ELEMENTS } from '../constants/theme';

const ESSENCE_VALUES: Record<number, number> = { 1: 5, 2: 10, 3: 25, 4: 100, 5: 300 };
const LEVEL_BONUS = 0.02;

function calcEssence(stars: number, level: number): number {
  const base = ESSENCE_VALUES[Math.min(stars, 5)] || 5;
  return Math.floor(base * (1 + level * LEVEL_BONUS));
}

export default function SoulForgeScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [heroes, setHeroes] = useState<any[]>([]);
  const [teamIds, setTeamIds] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [forging, setForging] = useState(false);
  const [balance, setBalance] = useState(0);
  const [result, setResult] = useState<{ gained: number; newBalance: number } | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const [uh, team, user] = await Promise.all([
        apiCall('/api/user/heroes'),
        apiCall('/api/team'),
        apiCall('/api/user/profile').catch(() => null),
      ]);
      setHeroes(uh.sort((a: any, b: any) => (b.hero_rarity || 0) - (a.hero_rarity || 0) || (b.stars || 0) - (a.stars || 0)));
      const ids = new Set<string>((team?.formation || []).filter((f: any) => f.user_hero_id).map((f: any) => f.user_hero_id));
      setTeamIds(ids);
      setBalance(user?.soul_essence || 0);
    } catch (e) {} finally { setLoading(false); }
  };

  const available = useMemo(() => heroes.filter(h => !teamIds.has(h.id)), [heroes, teamIds]);

  const toggle = useCallback((id: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
    setResult(null);
  }, []);

  const selectAll = () => { setSelected(new Set(available.map(h => h.id))); setResult(null); };
  const deselectAll = () => { setSelected(new Set()); setResult(null); };

  const previewEssence = useMemo(() => {
    let total = 0;
    for (const h of available) {
      if (selected.has(h.id)) {
        total += calcEssence(h.stars || h.hero_rarity || 1, h.level || 1);
      }
    }
    return total;
  }, [selected, available]);

  const forge = async () => {
    if (selected.size === 0) return;
    setForging(true);
    try {
      const r = await apiCall('/api/soul/forge', {
        method: 'POST',
        body: JSON.stringify({ hero_ids: Array.from(selected) }),
      });
      setResult({ gained: r.gained_essence, newBalance: r.new_balance });
      setBalance(r.new_balance);
      setSelected(new Set());
      setHeroes(prev => prev.filter(h => !selected.has(h.id)));
      await refreshUser();
    } catch (e: any) {
      setResult({ gained: 0, newBalance: balance });
    } finally { setForging(false); }
  };

  if (loading) return (
    <LinearGradient colors={['#0A0A1A', '#1A0A2E', '#0A0A1A']} style={s.container}>
      <ActivityIndicator size="large" color="#9944FF" />
    </LinearGradient>
  );

  return (
    <LinearGradient colors={['#0A0A1A', '#1A0A2E', '#0D0820']} style={s.container}>
      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>{'\u2190'}</Text>
        </TouchableOpacity>
        <View style={s.headerCenter}>
          <Text style={s.title}>SOUL FORGE</Text>
          <Text style={s.subtitle}>Dissolvi gli eroi in essenza pura</Text>
        </View>
        <View style={s.balanceBadge}>
          <Text style={s.balanceIcon}>{'\uD83D\uDC80'}</Text>
          <Text style={s.balanceVal}>{balance.toLocaleString()}</Text>
        </View>
      </View>

      <View style={s.body}>
        {/* Left: Hero Grid */}
        <View style={s.gridPanel}>
          <View style={s.gridHeader}>
            <Text style={s.gridTitle}>EROI DISPONIBILI ({available.length})</Text>
            <View style={s.gridActions}>
              <TouchableOpacity onPress={selectAll} style={s.miniBtn}>
                <Text style={s.miniBtnTxt}>Tutti</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={deselectAll} style={s.miniBtn}>
                <Text style={s.miniBtnTxt}>Nessuno</Text>
              </TouchableOpacity>
            </View>
          </View>
          <ScrollView style={s.gridScroll} contentContainerStyle={s.gridContent} showsVerticalScrollIndicator={false}>
            <View style={s.grid}>
              {available.map((h: any, i: number) => {
                const isSel = selected.has(h.id);
                const stars = h.stars || h.hero_rarity || 1;
                const rarCol = RARITY.colors[Math.min(stars, 6)] || '#888';
                const essence = calcEssence(stars, h.level || 1);
                return (
                  <Animated.View key={h.id} entering={FadeInDown.delay(Math.min(i, 20) * 30).duration(200)}>
                    <TouchableOpacity
                      style={[s.heroCard, isSel && { borderColor: '#9944FF', backgroundColor: 'rgba(153,68,255,0.12)' }]}
                      onPress={() => toggle(h.id)}
                      activeOpacity={0.7}
                    >
                      {isSel && <View style={s.selBadge}><Text style={s.selCheck}>{'\u2713'}</Text></View>}
                      {h.hero_image ? (
                        <View style={[s.heroImg, { borderColor: rarCol }]}>
                          <Image source={{ uri: h.hero_image }} style={s.heroImgInner} />
                        </View>
                      ) : (
                        <View style={[s.heroImgPh, { borderColor: rarCol, backgroundColor: rarCol + '15' }]}>
                          <Text style={[s.heroInit, { color: rarCol }]}>{(h.hero_name || '?')[0]}</Text>
                        </View>
                      )}
                      <Text style={[s.heroName, { color: rarCol }]} numberOfLines={1}>{h.hero_name}</Text>
                      <View style={s.heroStars}>
                        <StarDisplay stars={stars} size={8} />
                      </View>
                      <Text style={s.heroLvl}>Lv.{h.level || 1}</Text>
                      <Text style={s.heroEssence}>{'\uD83D\uDC80'} {essence}</Text>
                    </TouchableOpacity>
                  </Animated.View>
                );
              })}
            </View>
          </ScrollView>
        </View>

        {/* Right: Forge Panel */}
        <View style={s.forgePanel}>
          <LinearGradient colors={['rgba(153,68,255,0.08)', 'rgba(10,10,30,0.9)']} style={s.forgePanelInner}>
            {/* Preview */}
            <Animated.View entering={FadeIn} style={s.previewBox}>
              <Text style={s.previewLabel}>ESSENZA OTTENIBILE</Text>
              <Animated.Text key={previewEssence} entering={ZoomIn.duration(200)} style={s.previewVal}>
                +{previewEssence.toLocaleString()}
              </Animated.Text>
              <Text style={s.previewIcon}>{'\uD83D\uDC80'}</Text>
              <Text style={s.previewSub}>{selected.size} {selected.size === 1 ? 'eroe' : 'eroi'} selezionati</Text>
            </Animated.View>

            {/* Value Table */}
            <View style={s.valueTable}>
              <Text style={s.tableTitle}>VALORI BASE</Text>
              {Object.entries(ESSENCE_VALUES).map(([star, val]) => (
                  <View key={star} style={s.tableRow}>
                    <StarDisplay stars={Number(star)} size={10} />
                    <Text style={s.tableVal}>{val}</Text>
                  </View>
              ))}
              <Text style={s.tableNote}>+2% per livello eroe</Text>
            </View>

            {/* Warning */}
            <View style={s.warningBox}>
              <Text style={s.warningIcon}>{'\u26A0\uFE0F'}</Text>
              <Text style={s.warningTxt}>Gli eroi forgiati saranno distrutti permanentemente</Text>
            </View>

            {/* Forge Button */}
            <TouchableOpacity
              onPress={forge}
              disabled={selected.size === 0 || forging}
              activeOpacity={0.7}
              style={s.forgeBtnWrap}
            >
              <LinearGradient
                colors={selected.size > 0 ? ['#9944FF', '#6622CC'] : ['#333', '#222']}
                style={[s.forgeBtn, (selected.size === 0 || forging) && { opacity: 0.5 }]}
              >
                {forging ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text style={s.forgeBtnTxt}>{'\uD83D\uDD25'} FORGE SOUL</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            {/* Result */}
            {result && result.gained > 0 && (
              <Animated.View entering={FadeInUp.duration(300)} style={s.resultBox}>
                <Text style={s.resultGained}>+{result.gained.toLocaleString()} Soul Essence</Text>
                <Text style={s.resultBalance}>Bilancio: {result.newBalance.toLocaleString()}</Text>
              </Animated.View>
            )}
          </LinearGradient>
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  // Header
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6,
    borderBottomWidth: 1, borderBottomColor: 'rgba(153,68,255,0.2)',
    backgroundColor: 'rgba(10,10,30,0.95)',
  },
  backBtn: { paddingRight: 10 },
  backTxt: { color: '#fff', fontSize: 18, fontWeight: '700' },
  headerCenter: { flex: 1 },
  title: { color: '#C877FF', fontSize: 14, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: 'rgba(255,255,255,0.4)', fontSize: 8, marginTop: 1 },
  balanceBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(153,68,255,0.12)', paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: 8, borderWidth: 1, borderColor: 'rgba(153,68,255,0.3)',
  },
  balanceIcon: { fontSize: 12 },
  balanceVal: { color: '#C877FF', fontSize: 12, fontWeight: '900' },
  // Body
  body: { flex: 1, flexDirection: 'row', padding: 6, gap: 6 },
  // Grid
  gridPanel: { flex: 1, gap: 4 },
  gridHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  gridTitle: { color: 'rgba(255,255,255,0.5)', fontSize: 8, fontWeight: '800', letterSpacing: 0.5 },
  gridActions: { flexDirection: 'row', gap: 4 },
  miniBtn: {
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 4,
    backgroundColor: 'rgba(153,68,255,0.1)', borderWidth: 1, borderColor: 'rgba(153,68,255,0.2)',
  },
  miniBtnTxt: { color: '#C877FF', fontSize: 7, fontWeight: '700' },
  gridScroll: { flex: 1 },
  gridContent: { paddingBottom: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  // Hero Card
  heroCard: {
    width: 80, alignItems: 'center', padding: 5, borderRadius: 8,
    borderWidth: 1.5, borderColor: 'rgba(255,255,255,0.06)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  selBadge: {
    position: 'absolute', top: 2, right: 2, zIndex: 1,
    width: 14, height: 14, borderRadius: 7,
    backgroundColor: '#9944FF', alignItems: 'center', justifyContent: 'center',
  },
  selCheck: { color: '#fff', fontSize: 8, fontWeight: '900' },
  heroImg: { width: 40, height: 40, borderRadius: 8, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  heroImgInner: { width: '100%', height: '100%' },
  heroImgPh: { width: 40, height: 40, borderRadius: 8, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  heroInit: { fontSize: 18, fontWeight: '900' },
  heroName: { fontSize: 7, fontWeight: '800', marginTop: 3, textAlign: 'center' },
  heroStars: { marginTop: 1 },
  heroLvl: { fontSize: 6, color: 'rgba(255,255,255,0.4)', marginTop: 1 },
  heroEssence: { fontSize: 7, color: '#C877FF', fontWeight: '700', marginTop: 2 },
  // Forge Panel
  forgePanel: { width: 200 },
  forgePanelInner: {
    flex: 1, borderRadius: 10, padding: 10, gap: 8,
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.15)',
  },
  // Preview
  previewBox: { alignItems: 'center', paddingVertical: 8 },
  previewLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 7, fontWeight: '800', letterSpacing: 1 },
  previewVal: { color: '#C877FF', fontSize: 28, fontWeight: '900', marginTop: 2 },
  previewIcon: { fontSize: 20, marginTop: -2 },
  previewSub: { color: 'rgba(255,255,255,0.3)', fontSize: 8, marginTop: 4 },
  // Value Table
  valueTable: {
    backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6, padding: 6, gap: 3,
  },
  tableTitle: { color: 'rgba(255,255,255,0.3)', fontSize: 6, fontWeight: '800', letterSpacing: 0.5, textAlign: 'center', marginBottom: 2 },
  tableRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  tableStar: { fontSize: 8 },
  tableVal: { color: '#C877FF', fontSize: 9, fontWeight: '800' },
  tableNote: { color: 'rgba(255,255,255,0.25)', fontSize: 6, textAlign: 'center', marginTop: 2, fontStyle: 'italic' },
  // Warning
  warningBox: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(255,68,68,0.06)', borderRadius: 6, padding: 6,
    borderWidth: 1, borderColor: 'rgba(255,68,68,0.15)',
  },
  warningIcon: { fontSize: 10 },
  warningTxt: { flex: 1, color: 'rgba(255,100,100,0.7)', fontSize: 7, fontWeight: '600' },
  // Forge Button
  forgeBtnWrap: { marginTop: 2 },
  forgeBtn: { paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
  forgeBtnTxt: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  // Result
  resultBox: {
    alignItems: 'center', padding: 8, borderRadius: 8,
    backgroundColor: 'rgba(153,68,255,0.1)', borderWidth: 1, borderColor: 'rgba(153,68,255,0.3)',
  },
  resultGained: { color: '#C877FF', fontSize: 14, fontWeight: '900' },
  resultBalance: { color: 'rgba(255,255,255,0.4)', fontSize: 8, marginTop: 2 },
});

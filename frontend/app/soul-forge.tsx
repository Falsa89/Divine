import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, Modal, TextInput, Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown, FadeInUp, ZoomIn } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import { heroPortraitSource } from '../components/ui/hopliteAssets';
import { COLORS, RARITY, ELEMENTS } from '../constants/theme';

const ESSENCE_VALUES: Record<number, number> = { 1: 5, 2: 10, 3: 25, 4: 100, 5: 300 };
const LEVEL_BONUS = 0.02;

// BATCH_1_V2 Track D \u2014 Soul Forge Permanent Destruction Guard
// La modalit\u00e0 Soul Forge \u00e8 una funzione intenzionale del gioco (sacrificare eroi
// inutili per ottenere essenza spendibile). Il problema NON \u00e8 la modalit\u00e0 in s\u00e9
// ma la facilit\u00e0 di distruggere accidentalmente eroi rari/preziosi.
// Guardrail aggiunti (solo frontend, nessuna mutazione backend):
//   - HIGH_RARITY_PROTECT_MIN: eroi con stelle >= soglia sono protetti by default
//     e NON pre-selezionabili dal toggle one-tap (richiedono override esplicito).
//   - PROTECTED_FLAGS: locked/favorite/native/event/unique vengono filtrati out
//     dalla griglia "disponibili" (insieme al team attivo gi\u00e0 protetto).
//   - Conferma multi-step (modal) prima del POST /api/soul/forge.
//   - Per distruzioni "rischiose" (>=10 eroi o presenza di overrided high-rarity)
//     richiediamo typed confirmation digitando esattamente CONFERMA.
//   - Preview esatta nel modal: numero eroi, breakdown stelle, essenza totale.
const HIGH_RARITY_PROTECT_MIN = 4; // >=4 stelle = rari (proteggiamo Eroico/Mitico/etc.)
const RISKY_BULK_THRESHOLD = 10;
const PROTECTED_FLAGS = new Set([
  // chiavi possibili in user_heroes per la protezione lato frontend
  'locked', 'is_locked', 'favorite', 'is_favorite',
  'native', 'is_native', 'is_event', 'is_unique', 'is_exclusive',
]);

function calcEssence(stars: number, level: number): number {
  const base = ESSENCE_VALUES[Math.min(stars, 5)] || 5;
  return Math.floor(base * (1 + level * LEVEL_BONUS));
}

function isHeroProtectedByFlags(h: any): boolean {
  for (const k of PROTECTED_FLAGS) {
    if (h && h[k]) return true;
  }
  return false;
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

  // BATCH_1_V2 Track D \u2014 confirm modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [typedConfirm, setTypedConfirm] = useState('');
  const [overrideHighRarity, setOverrideHighRarity] = useState(false);

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

  // BATCH_1_V2 Track D \u2014 filtro multi-livello:
  //  - team attivo (gi\u00e0 escluso)
  //  - flag-protetti (locked/favorite/native/event/unique)
  //  - alta rarit\u00e0 viene mostrata ma DEFAULT NON selezionata
  const available = useMemo(
    () => heroes.filter(h => !teamIds.has(h.id) && !isHeroProtectedByFlags(h)),
    [heroes, teamIds]
  );
  const protectedFlagCount = useMemo(
    () => heroes.filter(h => isHeroProtectedByFlags(h)).length,
    [heroes]
  );

  // Eroi ad alta rarit\u00e0 attualmente selezionati (per UI di warning)
  const selectedHighRarity = useMemo(() => {
    const out: any[] = [];
    for (const h of available) {
      if (selected.has(h.id)) {
        const s = h.stars || h.hero_rarity || 1;
        if (s >= HIGH_RARITY_PROTECT_MIN) out.push(h);
      }
    }
    return out;
  }, [selected, available]);

  // Breakdown per modal
  const selectionBreakdown = useMemo(() => {
    const byStar: Record<number, number> = {};
    for (const h of available) {
      if (selected.has(h.id)) {
        const s = h.stars || h.hero_rarity || 1;
        byStar[s] = (byStar[s] || 0) + 1;
      }
    }
    return byStar;
  }, [selected, available]);

  const isRiskyForge = selected.size >= RISKY_BULK_THRESHOLD || selectedHighRarity.length > 0;

  const toggle = useCallback((id: string, stars: number) => {
    // ALIGNMENT_FIX Track B \u2014 feedback discoverability: tap su 4\u2605+ senza
    // override mostra un alert che spiega come abilitare la selezione.
    // Mantiene la protezione di default ma rende il flusso scopribile.
    if (stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity) {
      Alert.alert(
        '\uD83D\uDD12 Eroe protetto',
        `Gli eroi ${HIGH_RARITY_PROTECT_MIN}\u2605+ sono protetti per evitare distruzioni accidentali.\n\nSe vuoi davvero sacrificarli, attiva prima l'opzione "Sblocca selezione eroi ${HIGH_RARITY_PROTECT_MIN}\u2605+" nel pannello a destra.`,
        [
          { text: 'Annulla', style: 'cancel' },
          {
            text: 'Sblocca ora',
            style: 'destructive',
            onPress: () => setOverrideHighRarity(true),
          },
        ],
      );
      return;
    }
    setSelected(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
    setResult(null);
  }, [overrideHighRarity]);

  // BATCH_1_V2 Track D \u2014 selectAll selezione SOLO eroi non rari di default
  const selectAll = () => {
    const safe = available.filter(h => (h.stars || h.hero_rarity || 1) < HIGH_RARITY_PROTECT_MIN);
    setSelected(new Set(safe.map(h => h.id)));
    setResult(null);
  };
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

  // BATCH_1_V2 Track D \u2014 forge ora apre prima il modal di conferma
  const requestForge = () => {
    if (selected.size === 0) return;
    setTypedConfirm('');
    setConfirmOpen(true);
  };

  const confirmForge = async () => {
    // Per forge rischioso, richiediamo digitazione di CONFERMA
    if (isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA') {
      return;
    }
    setConfirmOpen(false);
    setForging(true);
    try {
      const r = await apiCall('/api/soul/forge', {
        method: 'POST',
        body: JSON.stringify({ hero_ids: Array.from(selected) }),
      });
      setResult({ gained: r.gained_essence, newBalance: r.new_balance });
      setBalance(r.new_balance);
      setSelected(new Set());
      setOverrideHighRarity(false);
      setHeroes(prev => prev.filter(h => !selected.has(h.id)));
      await refreshUser();
    } catch (e: any) {
      setResult({ gained: 0, newBalance: balance });
    } finally {
      setForging(false);
      setTypedConfirm('');
    }
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
          {/* ALIGNMENT_FIX Track B \u2014 banner di stato override (rende ovvio il flusso) */}
          {overrideHighRarity && (
            <View style={s.overrideStatusBannerV2}>
              <Text style={s.overrideStatusIconV2}>{'\uD83D\uDD13'}</Text>
              <Text style={s.overrideStatusTxtV2}>
                Override attivo: ora gli eroi {HIGH_RARITY_PROTECT_MIN}{'\u2605'}+ NON team /
                non bloccati / non preferiti / non nativi-evento sono selezionabili.
                La conferma richieder{'\u00e0'} digitazione di CONFERMA.
              </Text>
            </View>
          )}
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
                      style={[
                        s.heroCard,
                        isSel && { borderColor: '#9944FF', backgroundColor: 'rgba(153,68,255,0.12)' },
                        stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity && { opacity: 0.45 },
                      ]}
                      onPress={() => toggle(h.id, stars)}
                      activeOpacity={stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity ? 1 : 0.7}
                    >
                      {isSel && <View style={s.selBadge}><Text style={s.selCheck}>{'\u2713'}</Text></View>}
                      {stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity && (
                        <View style={s.protectBadgeV2}><Text style={s.protectBadgeTxtV2}>{'\uD83D\uDD12'}</Text></View>
                      )}
                      {h.hero_image ? (
                        <View style={[s.heroImg, { borderColor: rarCol }]}>
                          <Image source={heroPortraitSource(h.hero_image, h.hero_id, h.hero_name)} style={s.heroImgInner} />
                        </View>
                      ) : (
                        <View style={[s.heroImgPh, { borderColor: rarCol, backgroundColor: rarCol + '15' }]}>
                          <Text style={[s.heroInit, { color: rarCol }]}>{(h.hero_name || '?')[0]}</Text>
                        </View>
                      )}
                      <Text style={[s.heroName, { color: rarCol }]} numberOfLines={1}>{h.hero_name}</Text>
                      <View style={s.heroStars}>
                        {stars <= 12 ? <StarDisplay stars={stars} size={8} /> : <TranscendenceStars stars={stars} size={8} />}
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

            {/* BATCH_1_V2 Track D \u2014 Warning + Override + Protection info */}
            <View style={s.warningBox}>
              <Text style={s.warningIcon}>{'\u26A0\uFE0F'}</Text>
              <Text style={s.warningTxt}>Gli eroi forgiati saranno distrutti PERMANENTEMENTE.</Text>
            </View>
            <View style={s.protectInfoBoxV2}>
              <Text style={s.protectInfoTxtV2}>
                {'\uD83D\uDEE1\uFE0F'} Protezione attiva: eroi in team, bloccati,
                preferiti, nativi/evento/unique ({protectedFlagCount}) sono esclusi.
              </Text>
              <Text style={s.protectInfoTxtV2}>
                {'\uD83D\uDD12'} Eroi {HIGH_RARITY_PROTECT_MIN}{'\u2605'}+ richiedono
                lo sblocco esplicito qui sotto per essere selezionati.
              </Text>
              <TouchableOpacity
                style={[s.overrideToggleV2, overrideHighRarity && s.overrideToggleActiveV2]}
                onPress={() => {
                  setOverrideHighRarity(prev => {
                    if (prev) {
                      // disattivando l'override, rimuoviamo dalla selezione gli eroi rari
                      setSelected(currSel => {
                        const next = new Set<string>();
                        for (const id of currSel) {
                          const h = available.find(x => x.id === id);
                          const stars = (h?.stars || h?.hero_rarity || 1);
                          if (stars < HIGH_RARITY_PROTECT_MIN) next.add(id);
                        }
                        return next;
                      });
                    }
                    return !prev;
                  });
                }}
                activeOpacity={0.7}
              >
                <Text style={[s.overrideToggleTxtV2, overrideHighRarity && { color: '#FFB347' }]}>
                  {overrideHighRarity ? '\u2705 Sacrifica anche eroi 4\u2605+ \u2014 ATTIVO' : '\u2B1C Permettimi di sacrificare anche eroi 4\u2605+ (rischio alto)'}
                </Text>
              </TouchableOpacity>
            </View>

            {/* Forge Button */}
            <TouchableOpacity
              onPress={requestForge}
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

      {/* BATCH_1_V2 Track D \u2014 Confirm Modal (multi-step + typed confirmation) */}
      <Modal visible={confirmOpen} transparent animationType="fade" onRequestClose={() => setConfirmOpen(false)}>
        <View style={s.modalBackdropV2}>
          <View style={s.modalCardV2}>
            <Text style={s.modalTitleV2}>{'\u26A0\uFE0F'} CONFERMA FORGE</Text>
            <Text style={s.modalSubV2}>
              Stai per distruggere {selected.size} {selected.size === 1 ? 'eroe' : 'eroi'} in modo PERMANENTE.
            </Text>
            <View style={s.modalBreakdownV2}>
              <Text style={s.modalSectionV2}>Cosa perdi:</Text>
              {Object.keys(selectionBreakdown).sort((a, b) => Number(b) - Number(a)).map(starKey => (
                <Text key={starKey} style={s.modalBreakLineV2}>
                  \u2022 {selectionBreakdown[Number(starKey)]} eroi {starKey}\u2605
                  {Number(starKey) >= HIGH_RARITY_PROTECT_MIN ? '  (\uD83D\uDD12 alta rarit\u00e0)' : ''}
                </Text>
              ))}
              <Text style={[s.modalSectionV2, { marginTop: 8 }]}>Cosa ottieni:</Text>
              <Text style={s.modalBreakLineV2}>{'\uD83D\uDC80'} +{previewEssence.toLocaleString()} Soul Essence</Text>
              <Text style={s.modalBreakLineV2}>Bilancio finale stimato: {(balance + previewEssence).toLocaleString()}</Text>
            </View>

            {isRiskyForge && (
              <View style={s.modalRiskBoxV2}>
                <Text style={s.modalRiskTitleV2}>{'\uD83D\uDEA8'} OPERAZIONE A RISCHIO</Text>
                <Text style={s.modalRiskTxtV2}>
                  {selectedHighRarity.length > 0
                    ? `Stai distruggendo ${selectedHighRarity.length} eroi 4\u2605+. `
                    : ''}
                  {selected.size >= RISKY_BULK_THRESHOLD
                    ? `Distruzione massiva (\u2265${RISKY_BULK_THRESHOLD}). `
                    : ''}
                  Digita CONFERMA per procedere.
                </Text>
                <TextInput
                  value={typedConfirm}
                  onChangeText={setTypedConfirm}
                  placeholder="CONFERMA"
                  placeholderTextColor="rgba(255,255,255,0.25)"
                  style={s.modalInputV2}
                  autoCapitalize="characters"
                  autoCorrect={false}
                />
              </View>
            )}

            <View style={s.modalActionsV2}>
              <TouchableOpacity
                style={s.modalCancelV2}
                onPress={() => { setConfirmOpen(false); setTypedConfirm(''); }}
                activeOpacity={0.7}
              >
                <Text style={s.modalCancelTxtV2}>ANNULLA</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  s.modalConfirmV2,
                  isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA' && { opacity: 0.35 },
                ]}
                onPress={confirmForge}
                disabled={isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA'}
                activeOpacity={0.7}
              >
                <Text style={s.modalConfirmTxtV2}>{'\uD83D\uDD25'} FORGE</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  // BATCH_1_V2 Track D \u2014 Soul Forge guardrail styles
  protectBadgeV2: {
    position: 'absolute', top: 2, left: 2, zIndex: 1,
    width: 18, height: 18, borderRadius: 9,
    backgroundColor: 'rgba(255,165,0,0.85)', alignItems: 'center', justifyContent: 'center',
  },
  protectBadgeTxtV2: { fontSize: 10 },
  protectInfoBoxV2: {
    marginTop: 8, marginBottom: 4,
    padding: 8, borderRadius: 8,
    backgroundColor: 'rgba(255,165,0,0.06)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.30)',
  },
  protectInfoTxtV2: {
    color: 'rgba(255,210,150,0.85)', fontSize: 8, lineHeight: 11, marginBottom: 2,
  },
  overrideToggleV2: {
    marginTop: 6, paddingVertical: 6, paddingHorizontal: 8,
    borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.10)',
  },
  overrideToggleActiveV2: {
    backgroundColor: 'rgba(255,165,0,0.10)', borderColor: 'rgba(255,165,0,0.55)',
  },
  overrideToggleTxtV2: { color: 'rgba(255,255,255,0.70)', fontSize: 9, fontWeight: '700' },
  // ALIGNMENT_FIX Track B \u2014 banner di stato override (prominente)
  overrideStatusBannerV2: {
    flexDirection: 'row', gap: 8, alignItems: 'center',
    paddingHorizontal: 10, paddingVertical: 8, marginBottom: 6,
    borderRadius: 8,
    backgroundColor: 'rgba(255,165,0,0.14)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.55)',
  },
  overrideStatusIconV2: { fontSize: 16 },
  overrideStatusTxtV2: { flex: 1, color: '#FFD089', fontSize: 9, lineHeight: 12, fontWeight: '700' },
  modalBackdropV2: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.78)',
    alignItems: 'center', justifyContent: 'center', padding: 16,
  },
  modalCardV2: {
    width: '100%', maxWidth: 460,
    backgroundColor: '#16102B', borderRadius: 14,
    borderWidth: 2, borderColor: 'rgba(153,68,255,0.6)',
    padding: 18,
  },
  modalTitleV2: {
    color: '#FFB347', fontSize: 16, fontWeight: '900', letterSpacing: 1, textAlign: 'center',
  },
  modalSubV2: {
    color: 'rgba(255,255,255,0.85)', fontSize: 12, lineHeight: 18,
    marginTop: 8, marginBottom: 4, textAlign: 'center',
  },
  modalBreakdownV2: {
    marginTop: 10, padding: 10, borderRadius: 8,
    backgroundColor: 'rgba(0,0,0,0.25)',
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.25)',
  },
  modalSectionV2: { color: '#C877FF', fontSize: 11, fontWeight: '800', marginBottom: 4 },
  modalBreakLineV2: { color: 'rgba(255,255,255,0.78)', fontSize: 11, lineHeight: 16 },
  modalRiskBoxV2: {
    marginTop: 12, padding: 10, borderRadius: 8,
    backgroundColor: 'rgba(255,68,68,0.10)',
    borderWidth: 1, borderColor: 'rgba(255,68,68,0.5)',
  },
  modalRiskTitleV2: { color: '#FF7777', fontSize: 11, fontWeight: '900', marginBottom: 4 },
  modalRiskTxtV2: { color: 'rgba(255,210,210,0.85)', fontSize: 10, lineHeight: 14, marginBottom: 8 },
  modalInputV2: {
    backgroundColor: 'rgba(0,0,0,0.35)',
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,68,68,0.5)',
    color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 1,
    paddingHorizontal: 12, paddingVertical: 8, textAlign: 'center',
  },
  modalActionsV2: { flexDirection: 'row', gap: 10, marginTop: 14 },
  modalCancelV2: {
    flex: 1, paddingVertical: 12, borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)',
    alignItems: 'center',
  },
  modalCancelTxtV2: { color: '#fff', fontSize: 12, fontWeight: '800', letterSpacing: 1 },
  modalConfirmV2: {
    flex: 1, paddingVertical: 12, borderRadius: 8,
    backgroundColor: 'rgba(153,68,255,0.25)',
    borderWidth: 1, borderColor: '#9944FF',
    alignItems: 'center',
  },
  modalConfirmTxtV2: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
});

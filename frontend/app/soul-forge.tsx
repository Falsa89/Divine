import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, Modal, TextInput, Alert,
  KeyboardAvoidingView, Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown, FadeInUp, ZoomIn } from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import { heroPortraitSource } from '../components/ui/hopliteAssets';
import { COLORS, RARITY, ELEMENTS } from '../constants/theme';

const ESSENCE_VALUES: Record<number, number> = { 1: 5, 2: 10, 3: 25, 4: 100, 5: 300 };
const LEVEL_BONUS = 0.02;

// =====================================================================
// EMERGENCY_RESTORE Track A/B/C/D \u2014 ROOT CAUSE & RESTORE
// =====================================================================
// Il pack precedente (SF_MERGE Track B) aveva impostato:
//   body: { flex: 1, flexDirection: 'column' }
// con i due figli (gridPanel, forgePanel) SENZA flex/height. Risultato:
// la gridScroll (flex:1) interna collassava a 0 e il forgePanelInner
// (flex:1) faceva lo stesso \u2014 nessuna card e nessun pannello visibile.
//
// Fix: il body diventa una *ScrollView esterna unica* che avvolge tutto
// (griglia + pannello forge + Anime Hub + materials/shop preview). Le
// inner ScrollView vengono rimosse per evitare height-bound issue e
// per coerenza con il pattern mobile-first one-page-scroll.
//
// Guardrail Soul Forge preservati (BATCH_1_V2 Track D):
//   - HIGH_RARITY_PROTECT_MIN (>=4\u2605 protetti by default)
//   - PROTECTED_FLAGS (locked/favorite/native/event/unique esclusi)
//   - confirm modal multi-step + typed CONFERMA per forge rischiosi
//   - breakdown esatto cosa perdi / cosa ottieni
//
// Nessuna mutazione backend nuova: l'unica POST resta /api/soul/forge.
// Tutto il resto (wallet, soul-forge, shops) \u00e8 GET read-only.
// =====================================================================
const HIGH_RARITY_PROTECT_MIN = 4;
const RISKY_BULK_THRESHOLD = 10;
const PROTECTED_FLAGS = new Set([
  'locked', 'is_locked', 'favorite', 'is_favorite',
  'native', 'is_native', 'is_event', 'is_unique', 'is_exclusive',
]);

// EMERGENCY_RESTORE Track C \u2014 filtri rarit\u00e0 disponibili.
type RarityFilter = 'all' | 'safe' | 'high' | '1' | '2' | '3' | '4' | '5';
const RARITY_FILTERS: { key: RarityFilter; label: string }[] = [
  { key: 'all', label: 'Tutti' },
  { key: 'safe', label: '1-3\u2605 (safe)' },
  { key: 'high', label: '4\u2605+' },
  { key: '1', label: '1\u2605' },
  { key: '2', label: '2\u2605' },
  { key: '3', label: '3\u2605' },
  { key: '4', label: '4\u2605' },
  { key: '5', label: '5\u2605' },
];

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
  const insets = useSafeAreaInsets();
  const { refreshUser } = useAuth();

  // Core state
  const [heroes, setHeroes] = useState<any[]>([]);
  const [teamIds, setTeamIds] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [forging, setForging] = useState(false);
  const [balance, setBalance] = useState(0);
  const [result, setResult] = useState<{ gained: number; newBalance: number } | null>(null);

  // EMERGENCY_RESTORE Track C \u2014 filtri
  const [rarityFilter, setRarityFilter] = useState<RarityFilter>('all');

  // BATCH_1_V2 Track D \u2014 confirm modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [typedConfirm, setTypedConfirm] = useState('');
  const [overrideHighRarity, setOverrideHighRarity] = useState(false);

  // EMERGENCY_RESTORE Track E/F \u2014 read-only legacy economy display state
  const [wallet, setWallet] = useState<any>(null);
  const [soulForgeMeta, setSoulForgeMeta] = useState<any>(null);
  const [shopsPreview, setShopsPreview] = useState<any>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      // Le chiamate "primarie" devono andare a buon fine per popolare la griglia.
      // Le chiamate "secondarie" (wallet/soul-forge/shops) sono best-effort:
      // se falliscono, lo screen continua a funzionare con un fallback.
      const [uh, team, user] = await Promise.all([
        apiCall('/api/user/heroes'),
        apiCall('/api/team').catch(() => ({ formation: [] })),
        apiCall('/api/user/profile').catch(() => null),
      ]);
      const heroesArr = Array.isArray(uh) ? uh : [];
      setHeroes(
        heroesArr.sort(
          (a: any, b: any) =>
            (b.hero_rarity || 0) - (a.hero_rarity || 0) ||
            (b.stars || 0) - (a.stars || 0)
        )
      );
      const ids = new Set<string>(
        (team?.formation || []).filter((f: any) => f.user_hero_id).map((f: any) => f.user_hero_id)
      );
      setTeamIds(ids);
      setBalance(user?.soul_essence || 0);

      // Secondary best-effort reads
      Promise.allSettled([
        apiCall('/api/wallet'),
        apiCall('/api/soul-forge'),
        apiCall('/api/shops'),
      ]).then(([w, sf, sh]) => {
        if (w.status === 'fulfilled') setWallet(w.value);
        if (sf.status === 'fulfilled') setSoulForgeMeta(sf.value);
        if (sh.status === 'fulfilled') setShopsPreview(sh.value);
      });
    } catch (e: any) {
      // EMERGENCY_RESTORE Track B \u2014 lo screen NON deve mai essere blank.
      // Anche con API failure mostriamo card di errore + retry.
      setLoadError(e?.message || 'Impossibile caricare gli eroi. Riprova.');
    } finally {
      setLoading(false);
    }
  };

  // Eroi disponibili = no team, no flag-protetti
  const available = useMemo(
    () => heroes.filter(h => !teamIds.has(h.id) && !isHeroProtectedByFlags(h)),
    [heroes, teamIds]
  );

  // EMERGENCY_RESTORE Track C \u2014 applicazione filtro rarit\u00e0 sopra "available"
  const visible = useMemo(() => {
    if (rarityFilter === 'all') return available;
    if (rarityFilter === 'safe') {
      return available.filter(h => (h.stars || h.hero_rarity || 1) < HIGH_RARITY_PROTECT_MIN);
    }
    if (rarityFilter === 'high') {
      return available.filter(h => (h.stars || h.hero_rarity || 1) >= HIGH_RARITY_PROTECT_MIN);
    }
    const want = parseInt(rarityFilter, 10);
    return available.filter(h => (h.stars || h.hero_rarity || 1) === want);
  }, [available, rarityFilter]);

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
    if (stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity) {
      Alert.alert(
        '\uD83D\uDD12 Eroe protetto',
        `Gli eroi ${HIGH_RARITY_PROTECT_MIN}\u2605+ sono protetti per evitare distruzioni accidentali.\n\nSe vuoi davvero sacrificarli, attiva prima l'opzione "Sblocca selezione eroi ${HIGH_RARITY_PROTECT_MIN}\u2605+" nel pannello.`,
        [
          { text: 'Annulla', style: 'cancel' },
          { text: 'Sblocca ora', style: 'destructive', onPress: () => setOverrideHighRarity(true) },
        ],
      );
      return;
    }
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
    setResult(null);
  }, [overrideHighRarity]);

  // BATCH_1_V2 Track D \u2014 selectAll selezione SOLO eroi non rari di default,
  // ma rispettando anche il filtro corrente: applichiamo l'intersezione.
  const selectAll = () => {
    const safe = visible.filter(h => (h.stars || h.hero_rarity || 1) < HIGH_RARITY_PROTECT_MIN);
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

  const requestForge = () => {
    if (selected.size === 0) return;
    setTypedConfirm('');
    setConfirmOpen(true);
  };

  const confirmForge = async () => {
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
      // refresh secondary read-only data without blocking
      Promise.allSettled([
        apiCall('/api/wallet'),
        apiCall('/api/soul-forge'),
      ]).then(([w, sf]) => {
        if (w.status === 'fulfilled') setWallet(w.value);
        if (sf.status === 'fulfilled') setSoulForgeMeta(sf.value);
      });
    } catch (e: any) {
      setResult({ gained: 0, newBalance: balance });
    } finally {
      setForging(false);
      setTypedConfirm('');
    }
  };

  // =================== EARLY RETURN: LOADING ===================
  if (loading) {
    return (
      <LinearGradient colors={['#0A0A1A', '#1A0A2E', '#0A0A1A']} style={s.container}>
        <View style={s.fullCenter}>
          <ActivityIndicator size="large" color="#9944FF" />
          <Text style={s.loadingTxt}>Caricamento Soul Forge\u2026</Text>
        </View>
      </LinearGradient>
    );
  }

  // =================== EARLY RETURN: ERROR ===================
  if (loadError) {
    return (
      <LinearGradient colors={['#0A0A1A', '#1A0A2E', '#0A0A1A']} style={s.container}>
        <View style={s.header}>
          <TouchableOpacity onPress={() => router.back()} style={s.backBtn} activeOpacity={0.7}>
            <Text style={s.backTxt}>{'\u2190'}</Text>
          </TouchableOpacity>
          <View style={s.headerCenter}>
            <Text style={s.title}>SOUL FORGE</Text>
            <Text style={s.subtitle}>Errore</Text>
          </View>
          <View style={{ width: 30 }} />
        </View>
        <View style={s.fullCenter}>
          <Text style={s.errorIcon}>{'\u26A0\uFE0F'}</Text>
          <Text style={s.errorTitle}>Impossibile caricare la Soul Forge</Text>
          <Text style={s.errorSub}>{loadError}</Text>
          <TouchableOpacity style={s.retryBtn} onPress={load} activeOpacity={0.8}>
            <Text style={s.retryTxt}>{'\u21BB'} Riprova</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  // Sicurezza: se per qualche motivo lo screen renderizza con array vuoto,
  // mostra un'empty state visibile (mai blank).
  const showEmptyState = available.length === 0;

  // =================== MAIN RENDER ===================
  return (
    <LinearGradient colors={['#0A0A1A', '#1A0A2E', '#0D0820']} style={s.container}>
      {/* Header */}
      <View style={[s.header, { paddingTop: Math.max(insets.top, 8) }]}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn} activeOpacity={0.7}>
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

      {/* EMERGENCY_RESTORE Track B \u2014 wrapper ScrollView esterna unica.
          Tutto il body scorre come una pagina mobile-first one-column. */}
      <ScrollView
        style={s.bodyScroll}
        contentContainerStyle={[s.bodyContent, { paddingBottom: Math.max(insets.bottom + 24, 40) }]}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* ===== Filtri rarit\u00e0 ===== */}
        <View style={s.filtersBox}>
          <Text style={s.filtersLabel}>FILTRI</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.filterRow}>
            {RARITY_FILTERS.map(f => {
              const active = rarityFilter === f.key;
              return (
                <TouchableOpacity
                  key={f.key}
                  style={[s.filterChip, active && s.filterChipActive]}
                  onPress={() => setRarityFilter(f.key)}
                  activeOpacity={0.7}
                >
                  <Text style={[s.filterChipTxt, active && s.filterChipTxtActive]}>{f.label}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        {/* ===== Override status banner ===== */}
        {overrideHighRarity && (
          <View style={s.overrideStatusBannerV2}>
            <Text style={s.overrideStatusIconV2}>{'\uD83D\uDD13'}</Text>
            <Text style={s.overrideStatusTxtV2}>
              Override attivo: gli eroi {HIGH_RARITY_PROTECT_MIN}{'\u2605'}+ NON team /
              non bloccati / non preferiti / non nativi-evento sono selezionabili.
              La conferma richiede digitazione di CONFERMA.
            </Text>
          </View>
        )}

        {/* ===== Grid header ===== */}
        <View style={s.gridHeader}>
          <Text style={s.gridTitle}>
            EROI DISPONIBILI ({visible.length}{visible.length !== available.length ? `/${available.length}` : ''})
          </Text>
          <View style={s.gridActions}>
            <TouchableOpacity onPress={selectAll} style={s.miniBtn} activeOpacity={0.7}>
              <Text style={s.miniBtnTxt}>Tutti safe</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={deselectAll} style={s.miniBtn} activeOpacity={0.7}>
              <Text style={s.miniBtnTxt}>Nessuno</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* ===== Hero grid (NO inner ScrollView \u2014 outer one scrolls everything) ===== */}
        {showEmptyState ? (
          <View style={s.emptyBox}>
            <Text style={s.emptyIcon}>{'\uD83D\uDC80'}</Text>
            <Text style={s.emptyTitle}>Nessun eroe sacrificabile</Text>
            <Text style={s.emptySub}>
              Gli eroi in team, bloccati, preferiti o nativi/evento sono protetti.
              Sblocca o togli dal team per renderli disponibili.
            </Text>
          </View>
        ) : visible.length === 0 ? (
          <View style={s.emptyBox}>
            <Text style={s.emptyIcon}>{'\uD83D\uDD0D'}</Text>
            <Text style={s.emptyTitle}>Nessun eroe per questo filtro</Text>
            <Text style={s.emptySub}>Cambia filtro rarit\u00e0 per vedere altri eroi.</Text>
          </View>
        ) : (
          <View style={s.grid}>
            {visible.map((h: any, i: number) => {
              const isSel = selected.has(h.id);
              const stars = h.stars || h.hero_rarity || 1;
              const rarCol = RARITY.colors[Math.min(stars, 6)] || '#888';
              const essence = calcEssence(stars, h.level || 1);
              const isHighProtected = stars >= HIGH_RARITY_PROTECT_MIN && !overrideHighRarity;
              return (
                <Animated.View key={h.id} entering={FadeInDown.delay(Math.min(i, 20) * 20).duration(180)}>
                  <TouchableOpacity
                    style={[
                      s.heroCard,
                      isSel && { borderColor: '#9944FF', backgroundColor: 'rgba(153,68,255,0.12)' },
                      isHighProtected && { opacity: 0.5 },
                    ]}
                    onPress={() => toggle(h.id, stars)}
                    activeOpacity={isHighProtected ? 1 : 0.7}
                  >
                    {isSel && <View style={s.selBadge}><Text style={s.selCheck}>{'\u2713'}</Text></View>}
                    {isHighProtected && (
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
                      {stars <= 12 ? <StarDisplay stars={stars} size={9} /> : <TranscendenceStars stars={stars} size={9} />}
                    </View>
                    <Text style={s.heroLvl}>Lv.{h.level || 1}</Text>
                    <Text style={s.heroEssence}>{'\uD83D\uDC80'} {essence}</Text>
                  </TouchableOpacity>
                </Animated.View>
              );
            })}
          </View>
        )}

        {/* ===== Forge Panel ===== */}
        <View style={s.forgePanel}>
          <LinearGradient
            colors={['rgba(153,68,255,0.10)', 'rgba(10,10,30,0.9)']}
            style={s.forgePanelInner}
          >
            {/* Preview */}
            <Animated.View entering={FadeIn} style={s.previewBox}>
              <Text style={s.previewLabel}>ESSENZA OTTENIBILE</Text>
              <Animated.Text key={previewEssence} entering={ZoomIn.duration(180)} style={s.previewVal}>
                +{previewEssence.toLocaleString()}
              </Animated.Text>
              <Text style={s.previewIcon}>{'\uD83D\uDC80'}</Text>
              <Text style={s.previewSub}>
                {selected.size} {selected.size === 1 ? 'eroe' : 'eroi'} selezionati
              </Text>
            </Animated.View>

            {/* Value Table */}
            <View style={s.valueTable}>
              <Text style={s.tableTitle}>VALORI BASE</Text>
              {Object.entries(ESSENCE_VALUES).map(([star, val]) => (
                <View key={star} style={s.tableRow}>
                  <StarDisplay stars={Number(star)} size={11} />
                  <Text style={s.tableVal}>{val}</Text>
                </View>
              ))}
              <Text style={s.tableNote}>+2% per livello eroe</Text>
            </View>

            {/* Warning + Protection info + Override toggle */}
            <View style={s.warningBox}>
              <Text style={s.warningIcon}>{'\u26A0\uFE0F'}</Text>
              <Text style={s.warningTxt}>
                Gli eroi forgiati saranno distrutti PERMANENTEMENTE.
              </Text>
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
                  {overrideHighRarity
                    ? '\u2705 Sacrifica anche eroi 4\u2605+ \u2014 ATTIVO'
                    : '\u2B1C Permettimi di sacrificare anche eroi 4\u2605+ (rischio alto)'}
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

        {/* ===== ANIME HUB \u2014 Materials / Legacy Shop preview / Rules / Treasury ===== */}
        <View style={s.merge_hub}>
          <Text style={s.merge_sectionTitle}>{'\uD83D\uDC80'} ANIME HUB</Text>

          {/* Materiali Anime: prana/sigilli/polvere/essenza */}
          <View style={s.merge_card}>
            <Text style={s.merge_cardTitle}>{'\u2728'} Materiali Anime</Text>
            <MaterialRow icon={'\uD83D\uDC80'} label="Soul Essence" value={balance} />
            <MaterialRow
              icon={'\uD83C\uDF00'}
              label="Prana"
              value={(soulForgeMeta?.prana ?? wallet?.currencies?.prana?.amount) || 0}
            />
            <MaterialRow
              icon={'\uD83D\uDD2E'}
              label="Sigilli Anima"
              value={(soulForgeMeta?.soul_seals ?? wallet?.currencies?.soul_seals?.amount) || 0}
            />
            <MaterialRow
              icon={'\u2728'}
              label="Polvere Stellare"
              value={(soulForgeMeta?.star_dust ?? wallet?.currencies?.star_dust?.amount) || 0}
            />
            <Text style={s.merge_hint}>
              Soul Essence \u00e8 mutata dal sacrificio attuale. Prana / Sigilli / Polvere
              sono valute legacy in sola lettura (read-only) in attesa del signoff economy.
            </Text>
          </View>

          {/* Tesoreria globale: anteprima top-3 valute globali + link */}
          {wallet?.currencies && (
            <View style={s.merge_card}>
              <Text style={s.merge_cardTitle}>{'\uD83C\uDFE6'} Valute Globali (Tesoreria)</Text>
              {(['gold', 'gems', 'honor'] as const).map(k => {
                const c = wallet.currencies?.[k];
                if (!c) return null;
                return (
                  <View key={k} style={s.merge_row}>
                    <Text style={s.merge_resIcon}>{c.icon}</Text>
                    <Text style={s.merge_resLabel}>{c.name}</Text>
                    <Text style={s.merge_resVal}>{(c.amount || 0).toLocaleString()}</Text>
                  </View>
                );
              })}
              <TouchableOpacity
                style={s.merge_treasuryBtn}
                onPress={() => router.push('/treasury')}
                activeOpacity={0.7}
              >
                <Text style={s.merge_treasuryIcon}>{'\uD83C\uDFE6'}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.merge_treasuryTitle}>Apri Tesoreria</Text>
                  <Text style={s.merge_treasuryDesc}>
                    Tutte le valute globali (gemme, oro, monete missione, frammenti...)
                  </Text>
                </View>
                <Text style={s.merge_treasuryArrow}>{'\u203A'}</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Negozio Anime preview: read-only */}
          {shopsPreview?.shops?.soul_forge && (
            <View style={s.merge_card}>
              <View style={s.merge_shopHead}>
                <Text style={s.merge_cardTitle}>{'\uD83D\uDED2'} Negozio Anime (preview)</Text>
                <View style={s.merge_lockBadge}>
                  <Text style={s.merge_lockTxt}>{'\uD83D\uDD12'} READ-ONLY</Text>
                </View>
              </View>
              {(shopsPreview.shops.soul_forge.items || []).slice(0, 6).map((it: any) => (
                <View key={it.id} style={s.merge_shopItem}>
                  <Text style={s.merge_shopItemIcon}>{it.icon || '\u2728'}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={s.merge_shopItemName} numberOfLines={1}>{it.name}</Text>
                    {it.description ? (
                      <Text style={s.merge_shopItemDesc} numberOfLines={1}>{it.description}</Text>
                    ) : null}
                    <Text style={s.merge_shopItemCost}>
                      {Object.entries(it.cost || {}).map(([c, v]) => `${c}: ${(v as number).toLocaleString()}`).join('  \u00b7  ')}
                    </Text>
                  </View>
                  <Text style={s.merge_shopItemStock}>{it.remaining_stock ?? it.stock ?? '\u221E'}</Text>
                </View>
              ))}
              <Text style={s.merge_hint}>
                Anteprima informativa. Gli acquisti sono disabilitati fino al signoff economy.
              </Text>
            </View>
          )}

          {/* Star Dust shop preview (se disponibile) */}
          {shopsPreview?.shops?.star_dust && (
            <View style={s.merge_card}>
              <View style={s.merge_shopHead}>
                <Text style={s.merge_cardTitle}>{'\u2728'} Negozio Polvere Stellare (preview)</Text>
                <View style={s.merge_lockBadge}>
                  <Text style={s.merge_lockTxt}>{'\uD83D\uDD12'} READ-ONLY</Text>
                </View>
              </View>
              {(shopsPreview.shops.star_dust.items || []).slice(0, 4).map((it: any) => (
                <View key={it.id} style={s.merge_shopItem}>
                  <Text style={s.merge_shopItemIcon}>{it.icon || '\u2728'}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={s.merge_shopItemName} numberOfLines={1}>{it.name}</Text>
                    <Text style={s.merge_shopItemCost}>
                      {Object.entries(it.cost || {}).map(([c, v]) => `${c}: ${(v as number).toLocaleString()}`).join('  \u00b7  ')}
                    </Text>
                  </View>
                  <Text style={s.merge_shopItemStock}>{it.remaining_stock ?? it.stock ?? '\u221E'}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Regole / Protezioni */}
          <View style={s.merge_card}>
            <Text style={s.merge_cardTitle}>{'\uD83D\uDCDC'} Regole / Protezioni</Text>
            <Text style={s.merge_rule}>{'\u2022'} Eroi in team sempre protetti.</Text>
            <Text style={s.merge_rule}>{'\u2022'} Eroi bloccati / preferiti / nativi / evento / unique protetti.</Text>
            <Text style={s.merge_rule}>{'\u2022'} Eroi 4{'\u2605'}+ richiedono override esplicito.</Text>
            <Text style={s.merge_rule}>
              {'\u2022'} Forge {'\u2265'}10 eroi o eroi 4{'\u2605'}+: digitazione CONFERMA obbligatoria.
            </Text>
            <Text style={s.merge_rule}>{'\u2022'} Distruzione PERMANENTE: nessun ripristino disponibile.</Text>
          </View>
        </View>
      </ScrollView>

      {/* ===== Confirm Modal ===== */}
      <Modal visible={confirmOpen} transparent animationType="fade" onRequestClose={() => setConfirmOpen(false)}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={s.modalBackdropV2}
        >
          <View style={s.modalCardV2}>
            {/* EMERGENCY_RESTORE Track D \u2014 modal scrollabile per tastiera + safe-area */}
            <ScrollView
              contentContainerStyle={{ paddingBottom: 8 }}
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={false}
            >
              <Text style={s.modalTitleV2}>{'\u26A0\uFE0F'} CONFERMA FORGE</Text>
              <Text style={s.modalSubV2}>
                Stai per distruggere {selected.size} {selected.size === 1 ? 'eroe' : 'eroi'} in modo PERMANENTE.
              </Text>
              <View style={s.modalBreakdownV2}>
                <Text style={s.modalSectionV2}>Cosa perdi:</Text>
                {Object.keys(selectionBreakdown).sort((a, b) => Number(b) - Number(a)).map(starKey => (
                  <Text key={starKey} style={s.modalBreakLineV2}>
                    {'\u2022'} {selectionBreakdown[Number(starKey)]} eroi {starKey}{'\u2605'}
                    {Number(starKey) >= HIGH_RARITY_PROTECT_MIN ? '  (\uD83D\uDD12 alta rarit\u00e0)' : ''}
                  </Text>
                ))}
                <Text style={[s.modalSectionV2, { marginTop: 8 }]}>Cosa ottieni:</Text>
                <Text style={s.modalBreakLineV2}>
                  {'\uD83D\uDC80'} +{previewEssence.toLocaleString()} Soul Essence
                </Text>
                <Text style={s.modalBreakLineV2}>
                  Bilancio finale stimato: {(balance + previewEssence).toLocaleString()}
                </Text>
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
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </LinearGradient>
  );
}

// Subcomponent: una riga materiale generica.
function MaterialRow({ icon, label, value }: { icon: string; label: string; value: number }) {
  return (
    <View style={s.merge_row}>
      <Text style={s.merge_resIcon}>{icon}</Text>
      <Text style={s.merge_resLabel}>{label}</Text>
      <Text style={s.merge_resVal}>{(value || 0).toLocaleString()}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  fullCenter: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 12 },
  loadingTxt: { color: 'rgba(255,255,255,0.5)', fontSize: 12, marginTop: 8 },
  // Error state
  errorIcon: { fontSize: 42 },
  errorTitle: { color: '#FFB347', fontSize: 16, fontWeight: '900', textAlign: 'center' },
  errorSub: { color: 'rgba(255,210,150,0.85)', fontSize: 12, textAlign: 'center', lineHeight: 18 },
  retryBtn: {
    marginTop: 14,
    paddingHorizontal: 22, paddingVertical: 10, borderRadius: 8,
    backgroundColor: 'rgba(153,68,255,0.25)',
    borderWidth: 1, borderColor: '#9944FF',
  },
  retryTxt: { color: '#fff', fontSize: 13, fontWeight: '900', letterSpacing: 1 },
  // Header
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 8,
    borderBottomWidth: 1, borderBottomColor: 'rgba(153,68,255,0.2)',
    backgroundColor: 'rgba(10,10,30,0.95)',
  },
  backBtn: { paddingRight: 10, paddingVertical: 4 },
  backTxt: { color: '#fff', fontSize: 22, fontWeight: '700' },
  headerCenter: { flex: 1 },
  title: { color: '#C877FF', fontSize: 14, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: 'rgba(255,255,255,0.4)', fontSize: 9, marginTop: 1 },
  balanceBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(153,68,255,0.12)', paddingHorizontal: 10, paddingVertical: 5,
    borderRadius: 8, borderWidth: 1, borderColor: 'rgba(153,68,255,0.3)',
  },
  balanceIcon: { fontSize: 12 },
  balanceVal: { color: '#C877FF', fontSize: 12, fontWeight: '900' },
  // Body (outer ScrollView)
  bodyScroll: { flex: 1 },
  bodyContent: { padding: 10, gap: 10 },
  // Filters
  filtersBox: { gap: 4 },
  filtersLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 9, fontWeight: '800', letterSpacing: 1 },
  filterRow: { gap: 6, paddingVertical: 2 },
  filterChip: {
    paddingHorizontal: 10, paddingVertical: 6, borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.10)',
  },
  filterChipActive: {
    backgroundColor: 'rgba(153,68,255,0.20)',
    borderColor: '#9944FF',
  },
  filterChipTxt: { color: 'rgba(255,255,255,0.65)', fontSize: 10, fontWeight: '700' },
  filterChipTxtActive: { color: '#fff' },
  // Grid header
  gridHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  gridTitle: { color: 'rgba(255,255,255,0.55)', fontSize: 10, fontWeight: '800', letterSpacing: 0.5 },
  gridActions: { flexDirection: 'row', gap: 6 },
  miniBtn: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 6,
    backgroundColor: 'rgba(153,68,255,0.12)',
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.30)',
  },
  miniBtnTxt: { color: '#C877FF', fontSize: 9, fontWeight: '800' },
  // Grid
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  emptyBox: {
    padding: 20, borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    alignItems: 'center', gap: 6,
  },
  emptyIcon: { fontSize: 28 },
  emptyTitle: { color: '#fff', fontSize: 13, fontWeight: '800' },
  emptySub: {
    color: 'rgba(255,255,255,0.55)', fontSize: 11, lineHeight: 16,
    textAlign: 'center', maxWidth: 320,
  },
  // Hero Card
  heroCard: {
    width: 86, alignItems: 'center', padding: 6, borderRadius: 10,
    borderWidth: 1.5, borderColor: 'rgba(255,255,255,0.06)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  selBadge: {
    position: 'absolute', top: 3, right: 3, zIndex: 1,
    width: 16, height: 16, borderRadius: 8,
    backgroundColor: '#9944FF', alignItems: 'center', justifyContent: 'center',
  },
  selCheck: { color: '#fff', fontSize: 9, fontWeight: '900' },
  heroImg: { width: 46, height: 46, borderRadius: 10, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  heroImgInner: { width: '100%', height: '100%' },
  heroImgPh: { width: 46, height: 46, borderRadius: 10, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  heroInit: { fontSize: 20, fontWeight: '900' },
  heroName: { fontSize: 8, fontWeight: '800', marginTop: 4, textAlign: 'center' },
  heroStars: { marginTop: 2 },
  heroLvl: { fontSize: 7, color: 'rgba(255,255,255,0.45)', marginTop: 1 },
  heroEssence: { fontSize: 8, color: '#C877FF', fontWeight: '800', marginTop: 2 },
  // Forge Panel
  forgePanel: { width: '100%' },
  forgePanelInner: {
    borderRadius: 12, padding: 12, gap: 10,
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.20)',
  },
  // Preview
  previewBox: { alignItems: 'center', paddingVertical: 6 },
  previewLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 9, fontWeight: '800', letterSpacing: 1 },
  previewVal: { color: '#C877FF', fontSize: 34, fontWeight: '900', marginTop: 2 },
  previewIcon: { fontSize: 22, marginTop: -2 },
  previewSub: { color: 'rgba(255,255,255,0.4)', fontSize: 10, marginTop: 4 },
  // Value Table
  valueTable: {
    backgroundColor: 'rgba(0,0,0,0.30)', borderRadius: 8, padding: 8, gap: 4,
  },
  tableTitle: { color: 'rgba(255,255,255,0.4)', fontSize: 8, fontWeight: '800', letterSpacing: 0.5, textAlign: 'center', marginBottom: 2 },
  tableRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  tableVal: { color: '#C877FF', fontSize: 10, fontWeight: '800' },
  tableNote: { color: 'rgba(255,255,255,0.30)', fontSize: 8, textAlign: 'center', marginTop: 2, fontStyle: 'italic' },
  // Warning
  warningBox: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: 'rgba(255,68,68,0.08)', borderRadius: 8, padding: 8,
    borderWidth: 1, borderColor: 'rgba(255,68,68,0.20)',
  },
  warningIcon: { fontSize: 12 },
  warningTxt: { flex: 1, color: 'rgba(255,140,140,0.90)', fontSize: 10, fontWeight: '700' },
  // Forge Button
  forgeBtnWrap: { marginTop: 4 },
  forgeBtn: { paddingVertical: 14, borderRadius: 12, alignItems: 'center' },
  forgeBtnTxt: { color: '#fff', fontSize: 14, fontWeight: '900', letterSpacing: 1.5 },
  // Result
  resultBox: {
    alignItems: 'center', padding: 10, borderRadius: 10,
    backgroundColor: 'rgba(153,68,255,0.10)', borderWidth: 1, borderColor: 'rgba(153,68,255,0.30)',
  },
  resultGained: { color: '#C877FF', fontSize: 15, fontWeight: '900' },
  resultBalance: { color: 'rgba(255,255,255,0.45)', fontSize: 10, marginTop: 2 },
  // Soul Forge guardrail styles
  protectBadgeV2: {
    position: 'absolute', top: 3, left: 3, zIndex: 1,
    width: 20, height: 20, borderRadius: 10,
    backgroundColor: 'rgba(255,165,0,0.85)', alignItems: 'center', justifyContent: 'center',
  },
  protectBadgeTxtV2: { fontSize: 11 },
  protectInfoBoxV2: {
    padding: 10, borderRadius: 8,
    backgroundColor: 'rgba(255,165,0,0.08)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.32)',
    gap: 4,
  },
  protectInfoTxtV2: { color: 'rgba(255,210,150,0.90)', fontSize: 10, lineHeight: 14 },
  overrideToggleV2: {
    marginTop: 6, paddingVertical: 8, paddingHorizontal: 10,
    borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.12)',
  },
  overrideToggleActiveV2: {
    backgroundColor: 'rgba(255,165,0,0.14)', borderColor: 'rgba(255,165,0,0.6)',
  },
  overrideToggleTxtV2: { color: 'rgba(255,255,255,0.75)', fontSize: 10, fontWeight: '800' },
  overrideStatusBannerV2: {
    flexDirection: 'row', gap: 8, alignItems: 'center',
    paddingHorizontal: 12, paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: 'rgba(255,165,0,0.14)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.55)',
  },
  overrideStatusIconV2: { fontSize: 18 },
  overrideStatusTxtV2: { flex: 1, color: '#FFD089', fontSize: 10, lineHeight: 14, fontWeight: '700' },
  // Modal
  modalBackdropV2: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.78)',
    alignItems: 'center', justifyContent: 'center', padding: 16,
  },
  modalCardV2: {
    width: '100%', maxWidth: 460, maxHeight: '90%',
    backgroundColor: '#16102B', borderRadius: 14,
    borderWidth: 2, borderColor: 'rgba(153,68,255,0.6)',
    padding: 18,
  },
  modalTitleV2: { color: '#FFB347', fontSize: 16, fontWeight: '900', letterSpacing: 1, textAlign: 'center' },
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
    paddingHorizontal: 12, paddingVertical: 10, textAlign: 'center',
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
  // Anime Hub
  merge_hub: { marginTop: 6, gap: 10 },
  merge_sectionTitle: {
    color: '#C877FF', fontSize: 13, fontWeight: '900', letterSpacing: 1.5,
  },
  merge_card: {
    padding: 12, borderRadius: 10,
    backgroundColor: 'rgba(0,0,0,0.30)',
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.25)',
    gap: 6,
  },
  merge_cardTitle: { color: '#fff', fontSize: 12, fontWeight: '900' },
  merge_row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  merge_resIcon: { fontSize: 16 },
  merge_resLabel: { flex: 1, color: 'rgba(255,255,255,0.85)', fontSize: 11, fontWeight: '700' },
  merge_resVal: { color: '#C877FF', fontSize: 13, fontWeight: '900' },
  merge_hint: { color: 'rgba(255,255,255,0.50)', fontSize: 10, lineHeight: 14, fontStyle: 'italic' },
  merge_lockBadge: {
    paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 6,
    backgroundColor: 'rgba(255,165,0,0.15)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.45)',
  },
  merge_lockTxt: { color: '#FFB347', fontSize: 9, fontWeight: '800', letterSpacing: 0.5 },
  merge_rule: { color: 'rgba(255,255,255,0.70)', fontSize: 10, lineHeight: 15 },
  // Shop preview rows
  merge_shopHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  merge_shopItem: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingVertical: 6,
    borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)',
  },
  merge_shopItemIcon: { fontSize: 18 },
  merge_shopItemName: { color: '#fff', fontSize: 11, fontWeight: '800' },
  merge_shopItemDesc: { color: 'rgba(255,255,255,0.45)', fontSize: 9, marginTop: 1 },
  merge_shopItemCost: { color: '#C877FF', fontSize: 9, fontWeight: '700', marginTop: 2 },
  merge_shopItemStock: { color: 'rgba(255,255,255,0.55)', fontSize: 10, fontWeight: '800' },
  // Treasury button
  merge_treasuryBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 10, borderRadius: 8, marginTop: 6,
    backgroundColor: 'rgba(255,215,0,0.10)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.45)',
  },
  merge_treasuryIcon: { fontSize: 20 },
  merge_treasuryTitle: { color: '#FFD700', fontSize: 11, fontWeight: '900' },
  merge_treasuryDesc: { color: 'rgba(255,215,0,0.7)', fontSize: 9, marginTop: 2 },
  merge_treasuryArrow: { color: '#FFD700', fontSize: 18, fontWeight: '900' },
});

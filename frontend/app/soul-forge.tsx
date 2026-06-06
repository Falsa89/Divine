import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Image, TextInput, Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown, FadeInUp, ZoomIn } from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import {
  isLegacyMutationLocked,
  POSTQA_D_LOCK_MESSAGE_TITLE,
  POSTQA_D_LOCK_MESSAGE_BODY,
} from '../utils/postqa_d_locked_endpoints';
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

  // INLINE_CONFIRM Track B/C \u2014 stato dell'inline confirm panel (NO Modal RN).
  // Su mobile RN, il componente Modal+KeyboardAvoidingView causava crash al primo tap
  // FORGE SOUL. Il path \u00e8 stato sostituito da un pannello inline dentro la ScrollView.
  const [inlineConfirmOpen, setInlineConfirmOpen] = useState(false);
  const [typedConfirm, setTypedConfirm] = useState('');
  const [overrideHighRarity, setOverrideHighRarity] = useState(false);

  // EMERGENCY_RESTORE Track E/F \u2014 read-only legacy economy display state
  const [wallet, setWallet] = useState<any>(null);
  const [soulForgeMeta, setSoulForgeMeta] = useState<any>(null);
  const [shopsPreview, setShopsPreview] = useState<any>(null);

  // FORGE_CRASH Track B \u2014 errore forge visibile (mai crash silenzioso)
  const [forgeError, setForgeError] = useState<string | null>(null);
  // FORGE_CRASH Track D \u2014 warning soft per refresh post-success fallito
  const [postSuccessWarn, setPostSuccessWarn] = useState<string | null>(null);

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
    try {
      if (selected.size === 0) return;
      if (forging) return; // double-submit guard
      // Snapshot the selection to ensure heroes still exist before opening confirm.
      const stillAvailable = available.filter(h => selected.has(h.id));
      if (stillAvailable.length === 0) {
        // Stale selection: clear and show error instead of crashing.
        setSelected(new Set());
        setForgeError('La selezione non \u00e8 pi\u00f9 valida. Ricarica e riprova.');
        return;
      }
      setTypedConfirm('');
      setForgeError(null);
      setPostSuccessWarn(null);
      // INLINE_CONFIRM Track C: open inline panel, NOT a Modal.
      setInlineConfirmOpen(true);
    } catch (e: any) {
      // Track D: handler never crashes.
      setForgeError(e?.message || 'Errore apertura conferma forge.');
    }
  };

  // =====================================================================
  // FORGE_CRASH Track B \u2014 Response normalization.
  // Accetta multiple varianti di field name per resilienza al contratto.
  // Restituisce { ok, gained, newBalance, errorMessage }.
  // Mai lancia eccezioni.
  // =====================================================================
  const normalizeForgeResponse = (r: any): {
    ok: boolean;
    gained: number;
    newBalance: number;
    errorMessage: string | null;
  } => {
    if (r == null || typeof r !== 'object') {
      return { ok: false, gained: 0, newBalance: balance, errorMessage: 'Risposta server vuota o non valida.' };
    }
    // Accept multiple aliases for "gained" amount
    const rawGained =
      r.gained_essence ?? r.gained ?? r.essence_gained ?? r.soul_essence_gained;
    const gainedNum = Number(rawGained);
    // Accept multiple aliases for "new balance"
    const rawBalance =
      r.new_balance ?? r.balance ?? r.soul_essence ?? r.new_soul_essence;
    const balanceNum = Number(rawBalance);
    const gainedOk = Number.isFinite(gainedNum) && gainedNum >= 0;
    // If balance is missing/NaN, fall back to optimistic computation
    const balanceOk = Number.isFinite(balanceNum) && balanceNum >= 0;
    if (!gainedOk) {
      return {
        ok: false,
        gained: 0,
        newBalance: balanceOk ? balanceNum : balance,
        errorMessage: 'Risposta forge non valida (manca essenza guadagnata).',
      };
    }
    return {
      ok: true,
      gained: gainedNum,
      newBalance: balanceOk ? balanceNum : balance + gainedNum,
      errorMessage: null,
    };
  };

  const confirmForge = async () => {
    if (forging) return; // hard double-submit guard
    if (isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA') {
      return;
    }
    // Snapshot selection BEFORE any state mutation to keep heroes alive on failure
    const heroIdsSnapshot = Array.from(selected);
    if (heroIdsSnapshot.length === 0) return;
    // v108_POSTQA_D: blocco player-facing per endpoint legacy gateato lato backend.
    if (isLegacyMutationLocked('/api/soul/forge')) {
      Alert.alert(POSTQA_D_LOCK_MESSAGE_TITLE, POSTQA_D_LOCK_MESSAGE_BODY);
      return;
    }
    // INLINE_CONFIRM Track C: chiudi il pannello inline (NON Modal).
    setInlineConfirmOpen(false);
    setForgeError(null);
    setPostSuccessWarn(null);
    setForging(true);
    try {
      const r = await apiCall('/api/soul/forge', {
        method: 'POST',
        body: JSON.stringify({ hero_ids: heroIdsSnapshot }),
      });
      const norm = normalizeForgeResponse(r);
      if (!norm.ok) {
        // Server accepted but response malformed: DO NOT remove heroes from UI.
        setForgeError(norm.errorMessage || 'Risposta forge non valida.');
        return;
      }
      // Success path: commit state mutations safely with normalized values.
      setResult({ gained: norm.gained, newBalance: norm.newBalance });
      setBalance(norm.newBalance);
      setSelected(new Set());
      setOverrideHighRarity(false);
      // Remove ONLY the heroes we actually requested forge for (snapshot).
      const snapshotSet = new Set(heroIdsSnapshot);
      setHeroes(prev => prev.filter(h => !snapshotSet.has(h.id)));
      // Best-effort refresh: soft warning if it fails, never crash.
      try {
        await refreshUser();
      } catch (re: any) {
        setPostSuccessWarn('Forge riuscita. Aggiornamento profilo fallito \u2014 riapri la schermata per sincronizzare.');
      }
      Promise.allSettled([
        apiCall('/api/wallet'),
        apiCall('/api/soul-forge'),
      ]).then((res) => {
        const [w, sf] = res;
        if (w && w.status === 'fulfilled') setWallet(w.value);
        if (sf && sf.status === 'fulfilled') setSoulForgeMeta(sf.value);
      }).catch(() => { /* swallow secondary errors safely */ });
    } catch (e: any) {
      // Network or API failure: visible error, heroes stay selected.
      const msg = (e && typeof e.message === 'string' && e.message)
        ? e.message
        : 'Errore di rete durante la forge.';
      setForgeError(msg);
      // Do NOT setResult here \u2014 result panel implies success.
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
          <Text style={s.balanceVal}>{(Number.isFinite(balance) ? balance : 0).toLocaleString()}</Text>
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
                <Text style={s.resultGained}>+{(Number(result.gained) || 0).toLocaleString()} Soul Essence</Text>
                <Text style={s.resultBalance}>Bilancio: {(Number(result.newBalance) || 0).toLocaleString()}</Text>
              </Animated.View>
            )}

            {/* FORGE_CRASH Track B \u2014 errore forge visibile (mai crash silenzioso) */}
            {forgeError && (
              <Animated.View entering={FadeInUp.duration(200)} style={s.forgeErrorBox}>
                <Text style={s.forgeErrorIcon}>{'\u26A0\uFE0F'}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.forgeErrorTitle}>Forge non riuscita</Text>
                  <Text style={s.forgeErrorMsg}>{forgeError}</Text>
                  <Text style={s.forgeErrorHint}>
                    I tuoi eroi selezionati sono ancora intatti. Puoi riprovare o annullare.
                  </Text>
                </View>
                <TouchableOpacity
                  style={s.forgeErrorDismiss}
                  onPress={() => setForgeError(null)}
                  activeOpacity={0.7}
                >
                  <Text style={s.forgeErrorDismissTxt}>{'\u2715'}</Text>
                </TouchableOpacity>
              </Animated.View>
            )}

            {/* FORGE_CRASH Track D \u2014 warning soft per refresh post-success */}
            {postSuccessWarn && (
              <View style={s.postWarnBox}>
                <Text style={s.postWarnIcon}>{'\u2139\uFE0F'}</Text>
                <Text style={s.postWarnTxt}>{postSuccessWarn}</Text>
                <TouchableOpacity onPress={() => setPostSuccessWarn(null)} activeOpacity={0.7}>
                  <Text style={s.postWarnDismiss}>{'\u2715'}</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* ================================================================ */}
            {/* INLINE_CONFIRM Track C \u2014 Pannello di conferma INLINE (NO Modal).  */}
            {/* Appare in pagina sotto il Forge button, scorre con la ScrollView   */}
            {/* esterna. Sostituisce il Modal RN che causava crash su mobile.      */}
            {/* ================================================================ */}
            {inlineConfirmOpen && (
              <Animated.View entering={FadeInUp.duration(220)} style={s.inlineConfirmCard}>
                <Text style={s.inlineConfirmTitle}>
                  {'\u26A0\uFE0F'} CONFERMA FORGE
                </Text>
                <Text style={s.inlineConfirmSub}>
                  Stai per distruggere {selected.size} {selected.size === 1 ? 'eroe' : 'eroi'} in modo PERMANENTE.
                </Text>

                <View style={s.inlineConfirmBreakdown}>
                  <Text style={s.inlineConfirmSection}>Cosa perdi:</Text>
                  {Object.keys(selectionBreakdown).sort((a, b) => Number(b) - Number(a)).map(starKey => (
                    <Text key={starKey} style={s.inlineConfirmLine}>
                      {'\u2022'} {selectionBreakdown[Number(starKey)] || 0} eroi {starKey}{'\u2605'}
                      {Number(starKey) >= HIGH_RARITY_PROTECT_MIN ? '  (\uD83D\uDD12 alta rarit\u00e0)' : ''}
                    </Text>
                  ))}
                  <Text style={[s.inlineConfirmSection, { marginTop: 8 }]}>Cosa ottieni:</Text>
                  <Text style={s.inlineConfirmLine}>
                    {'\uD83D\uDC80'} +{(Number(previewEssence) || 0).toLocaleString()} Soul Essence
                  </Text>
                  <Text style={s.inlineConfirmLine}>
                    Bilancio finale stimato:{' '}
                    {((Number.isFinite(balance) ? balance : 0) + (Number(previewEssence) || 0)).toLocaleString()}
                  </Text>
                </View>

                {isRiskyForge && (
                  <View style={s.inlineConfirmRiskBox}>
                    <Text style={s.inlineConfirmRiskTitle}>{'\uD83D\uDEA8'} OPERAZIONE A RISCHIO</Text>
                    <Text style={s.inlineConfirmRiskTxt}>
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
                      style={s.inlineConfirmInput}
                      autoCapitalize="characters"
                      autoCorrect={false}
                    />
                  </View>
                )}

                <View style={s.inlineConfirmActions}>
                  <TouchableOpacity
                    style={s.inlineConfirmCancel}
                    onPress={() => {
                      try {
                        setInlineConfirmOpen(false);
                        setTypedConfirm('');
                      } catch {}
                    }}
                    activeOpacity={0.7}
                  >
                    <Text style={s.inlineConfirmCancelTxt}>ANNULLA</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[
                      s.inlineConfirmConfirm,
                      (isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA') && { opacity: 0.35 },
                      forging && { opacity: 0.5 },
                    ]}
                    onPress={confirmForge}
                    disabled={
                      forging ||
                      (isRiskyForge && typedConfirm.trim().toUpperCase() !== 'CONFERMA')
                    }
                    activeOpacity={0.7}
                  >
                    <Text style={s.inlineConfirmConfirmTxt}>
                      {forging ? '\u2026 IN CORSO' : '\uD83D\uDD25 CONFERMA FORGE'}
                    </Text>
                  </TouchableOpacity>
                </View>
                <Text style={s.inlineConfirmHint}>
                  Suggerimento: scorri se l'azione finale non \u00e8 visibile.
                </Text>
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
              {/* FORGE_CRASH Track E \u2014 nav buttons safe: tesoreria + shop locked */}
              <View style={s.shop_navRow}>
                <TouchableOpacity
                  style={s.shop_navBtn}
                  onPress={() => router.push('/treasury')}
                  activeOpacity={0.7}
                >
                  <Text style={s.shop_navIcon}>{'\uD83C\uDFE6'}</Text>
                  <Text style={s.shop_navTxt}>Apri Tesoreria</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={s.shop_navBtnSecondary}
                  onPress={() => router.push('/shop')}
                  activeOpacity={0.7}
                >
                  <Text style={s.shop_navIcon}>{'\uD83D\uDED2'}</Text>
                  <Text style={s.shop_navTxtSecondary}>Vai al Negozio</Text>
                  <View style={s.shop_navLockMini}>
                    <Text style={s.shop_navLockMiniTxt}>{'\uD83D\uDD12'}</Text>
                  </View>
                </TouchableOpacity>
              </View>
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
              {/* FORGE_CRASH Track E \u2014 nav: item-shop \u00e8 locked read-only */}
              <View style={s.shop_navRow}>
                <TouchableOpacity
                  style={s.shop_navBtnSecondary}
                  onPress={() => router.push('/item-shop')}
                  activeOpacity={0.7}
                >
                  <Text style={s.shop_navIcon}>{'\uD83D\uDCE6'}</Text>
                  <Text style={s.shop_navTxtSecondary}>Apri Negozio Oggetti</Text>
                  <View style={s.shop_navLockMini}>
                    <Text style={s.shop_navLockMiniTxt}>{'\uD83D\uDD12'}</Text>
                  </View>
                </TouchableOpacity>
                <View style={[s.shop_navBtnSecondary, { opacity: 0.55 }]}>
                  <Text style={s.shop_navIcon}>{'\u2728'}</Text>
                  <Text style={s.shop_navTxtSecondary}>Negozio Polvere</Text>
                  <View style={[s.shop_navLockMini, { backgroundColor: 'rgba(255,165,0,0.25)' }]}>
                    <Text style={s.shop_navLockMiniTxt}>IN PREP</Text>
                  </View>
                </View>
              </View>
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
  // FORGE_CRASH Track B \u2014 visible error/warn banners
  forgeErrorBox: {
    flexDirection: 'row', gap: 8, alignItems: 'flex-start',
    padding: 10, borderRadius: 10,
    backgroundColor: 'rgba(255,68,68,0.10)',
    borderWidth: 1, borderColor: 'rgba(255,68,68,0.55)',
  },
  forgeErrorIcon: { fontSize: 18, marginTop: 1 },
  forgeErrorTitle: { color: '#FF8888', fontSize: 12, fontWeight: '900' },
  forgeErrorMsg: { color: 'rgba(255,210,210,0.92)', fontSize: 11, lineHeight: 16, marginTop: 3 },
  forgeErrorHint: { color: 'rgba(255,210,210,0.65)', fontSize: 9, lineHeight: 13, marginTop: 4, fontStyle: 'italic' },
  forgeErrorDismiss: {
    width: 22, height: 22, borderRadius: 11,
    backgroundColor: 'rgba(255,255,255,0.08)',
    alignItems: 'center', justifyContent: 'center',
  },
  forgeErrorDismissTxt: { color: '#fff', fontSize: 11, fontWeight: '900' },
  postWarnBox: {
    flexDirection: 'row', gap: 8, alignItems: 'center',
    padding: 8, borderRadius: 8,
    backgroundColor: 'rgba(255,215,0,0.08)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.30)',
  },
  postWarnIcon: { fontSize: 14 },
  postWarnTxt: { flex: 1, color: 'rgba(255,225,140,0.85)', fontSize: 10, lineHeight: 14 },
  postWarnDismiss: { color: 'rgba(255,225,140,0.65)', fontSize: 14, paddingHorizontal: 4 },
  // FORGE_CRASH Track E \u2014 shop navigation buttons (read-only safe targets)
  shop_navRow: { flexDirection: 'row', gap: 8, marginTop: 8 },
  shop_navBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
    paddingVertical: 10, paddingHorizontal: 8, borderRadius: 8,
    backgroundColor: 'rgba(255,215,0,0.12)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.55)',
  },
  shop_navTxt: { color: '#FFD700', fontSize: 10, fontWeight: '900', letterSpacing: 0.5 },
  shop_navBtnSecondary: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
    paddingVertical: 10, paddingHorizontal: 8, borderRadius: 8,
    backgroundColor: 'rgba(153,68,255,0.10)',
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.50)',
  },
  shop_navTxtSecondary: { color: '#C877FF', fontSize: 10, fontWeight: '900', letterSpacing: 0.5 },
  shop_navIcon: { fontSize: 14 },
  shop_navLockMini: {
    paddingHorizontal: 5, paddingVertical: 2, borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.10)',
  },
  shop_navLockMiniTxt: { color: '#fff', fontSize: 8, fontWeight: '800' },
  // INLINE_CONFIRM Track C \u2014 pannello di conferma inline (sostituisce il Modal RN)
  inlineConfirmCard: {
    marginTop: 6,
    padding: 14, borderRadius: 12,
    backgroundColor: 'rgba(20,8,35,0.95)',
    borderWidth: 2, borderColor: 'rgba(153,68,255,0.6)',
    gap: 8,
  },
  inlineConfirmTitle: {
    color: '#FFB347', fontSize: 14, fontWeight: '900',
    letterSpacing: 1, textAlign: 'center',
  },
  inlineConfirmSub: {
    color: 'rgba(255,255,255,0.85)', fontSize: 11, lineHeight: 16,
    textAlign: 'center',
  },
  inlineConfirmBreakdown: {
    marginTop: 4, padding: 10, borderRadius: 8,
    backgroundColor: 'rgba(0,0,0,0.25)',
    borderWidth: 1, borderColor: 'rgba(153,68,255,0.25)',
  },
  inlineConfirmSection: { color: '#C877FF', fontSize: 11, fontWeight: '800', marginBottom: 4 },
  inlineConfirmLine: { color: 'rgba(255,255,255,0.80)', fontSize: 11, lineHeight: 16 },
  inlineConfirmRiskBox: {
    marginTop: 4, padding: 10, borderRadius: 8,
    backgroundColor: 'rgba(255,68,68,0.10)',
    borderWidth: 1, borderColor: 'rgba(255,68,68,0.5)',
  },
  inlineConfirmRiskTitle: { color: '#FF7777', fontSize: 11, fontWeight: '900', marginBottom: 4 },
  inlineConfirmRiskTxt: { color: 'rgba(255,210,210,0.85)', fontSize: 10, lineHeight: 14, marginBottom: 8 },
  inlineConfirmInput: {
    backgroundColor: 'rgba(0,0,0,0.35)',
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,68,68,0.5)',
    color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 1,
    paddingHorizontal: 12, paddingVertical: 10, textAlign: 'center',
  },
  inlineConfirmActions: { flexDirection: 'row', gap: 10, marginTop: 6 },
  inlineConfirmCancel: {
    flex: 1, paddingVertical: 12, borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)',
    alignItems: 'center',
  },
  inlineConfirmCancelTxt: { color: '#fff', fontSize: 12, fontWeight: '800', letterSpacing: 1 },
  inlineConfirmConfirm: {
    flex: 1, paddingVertical: 12, borderRadius: 8,
    backgroundColor: 'rgba(153,68,255,0.25)',
    borderWidth: 1, borderColor: '#9944FF',
    alignItems: 'center',
  },
  inlineConfirmConfirmTxt: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 0.5 },
  inlineConfirmHint: {
    color: 'rgba(255,255,255,0.45)', fontSize: 9, textAlign: 'center', fontStyle: 'italic', marginTop: 2,
  },
});

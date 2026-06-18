import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Alert, Image, Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useFocusEffect } from 'expo-router';
import { apiCall } from '../../utils/api';
import { useAuth } from '../../context/AuthContext';
import useServerScope from '../../src/hooks/useServerScope';
import useBattlePowerSummary from '../../src/hooks/useBattlePowerSummary';
import AnimatedHeroPortrait from '../../components/AnimatedHeroPortrait';
import StarDisplay from '../../components/ui/StarDisplay';
import TranscendenceStars from '../../components/ui/TranscendenceStars';
import { heroPortraitSource } from '../../components/ui/hopliteAssets';
import { COLORS, RARITY, ELEMENTS, CLASSES } from '../../constants/theme';

const COLUMNS = [
  { role: 'Support', label: 'SUPPORTO', icon: '\u2764\uFE0F', bonus: 'CURE+15% VEL+10%', color: '#44DD99', x: 1 },
  { role: 'DPS', label: 'DPS', icon: '\u2694\uFE0F', bonus: 'ATK+15% CRIT+15%', color: '#FF5544', x: 4 },
  { role: 'Tank', label: 'TANK', icon: '\uD83D\uDEE1\uFE0F', bonus: 'DEF+20% HP+15%', color: '#4499FF', x: 7 },
];
const ROW_YS = [1, 4, 7];

const ELEM_FILTERS = [
  { key: 'all', icon: '\u2605' },
  { key: 'fire', icon: '\uD83D\uDD25' },
  { key: 'water', icon: '\uD83D\uDCA7' },
  { key: 'earth', icon: '\uD83E\uDEA8' },
  { key: 'wind', icon: '\uD83D\uDCA8' },
  { key: 'thunder', icon: '\u26A1' },
  { key: 'light', icon: '\u2728' },
  { key: 'shadow', icon: '\uD83C\uDF11' },
];

type SortKey = 'rarity' | 'level' | 'power' | 'name';

export default function BattleTab() {
  const router = useRouter();
  const { refreshUser, userHeroesVersion } = useAuth();
  // Pack 92 — server scope sweep su roster reader player-facing.
  const { selected_server_id } = useServerScope();
  const [heroes, setHeroes] = useState<any[]>([]);
  // grid[col][row] = hero | null  (col: 0=Support, 1=DPS, 2=Tank; row: 0,1,2)
  const [grid, setGrid] = useState<(any | null)[][]>([[null, null, null], [null, null, null], [null, null, null]]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  // Pre-QA Stabilization 116A — Battle Power foundation (read-only, derived,
  // server-scoped). Sostituisce `team.total_power` (legacy, computed lato
  // backend ma non versionato) con il summary 116A. Mai falso `0`.
  const bp = useBattlePowerSummary();
  const [activeCell, setActiveCell] = useState<{ col: number; row: number } | null>(null);
  const [elemFilter, setElemFilter] = useState('all');
  const [sortBy, setSortBy] = useState<SortKey>('rarity');
  const [constellations, setConstellations] = useState<any[]>([]);
  const [selectedConstellation, setSelectedConstellation] = useState<string | null>(null);
  const [showConstellations, setShowConstellations] = useState(false);
  const [synergies, setSynergies] = useState<any[]>([]);
  // ── RM1.23-C: Team Synergies V2 ID-based UI (read-only fetch) ─────
  // Mostra sinergie V2 attive + near-complete senza modificare V1.
  // Battle apply V2 resta gated da SYNERGY_V2_BATTLE_ENABLED (default false).
  type V2Effect = { stat: string; mode: string; value: number; target: string };
  type V2Synergy = {
    id: string;
    display_name: string;
    description?: string;
    icon?: string;
    rarity_tier?: string;
    matched_hero_ids: string[];
    matched_count: number;
    required_count: number;
    completion: number;
    buffs: Record<string, number>;
    avg_member_stars: number;
  };
  type V2NearComplete = {
    id: string;
    display_name: string;
    matched_count: number;
    required_count: number;
    missing_hero_ids: string[];
    completion: number;
  };
  type TeamSynergyV2Payload = {
    active_team_synergies_v2?: V2Synergy[];
    near_complete?: V2NearComplete[];
    aggregated_buffs?: Record<string, number>;
    members_resolved?: number;
    members_skipped_legacy_or_orphan?: number;
    enabled_synergy_count?: number;
    team_id?: string | null;
  };
  const [synergiesV2, setSynergiesV2] = useState<V2Synergy[]>([]);
  const [synergiesV2Near, setSynergiesV2Near] = useState<V2NearComplete[]>([]);
  const [synergiesV2EnabledCount, setSynergiesV2EnabledCount] = useState<number>(0);

  // RM1.16-B: refresh on focus + on userHeroesVersion bump (post-summon),
  // così la formation picker mostra subito i nuovi eroi pullati senza
  // richiedere restart dell'app. La grid già piazzata viene preservata se
  // tutti i suoi user_hero_id risolvono ancora nel nuovo `uh`.
  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [userHeroesVersion]),
  );

  // Load synergies whenever grid changes
  useEffect(() => {
    const loadSynergies = async () => {
      try {
        const syn = await apiCall('/api/synergies/team');
        setSynergies(syn.active_synergies || []);
      } catch (e) {
        setSynergies([]);
      }
    };
    // RM1.23-C: V2 fetch in parallel; failure-tolerant (no UI block).
    const loadSynergiesV2 = async () => {
      try {
        const v2: TeamSynergyV2Payload = await apiCall('/api/synergies/team_v2');
        setSynergiesV2(Array.isArray(v2?.active_team_synergies_v2) ? v2.active_team_synergies_v2 : []);
        setSynergiesV2Near(Array.isArray(v2?.near_complete) ? v2.near_complete : []);
        setSynergiesV2EnabledCount(typeof v2?.enabled_synergy_count === 'number' ? v2.enabled_synergy_count : 0);
      } catch (e) {
        // Silent fallback — non blocca la UI battaglia.
        setSynergiesV2([]);
        setSynergiesV2Near([]);
      }
    };
    if (filledCount > 0) {
      loadSynergies();
      loadSynergiesV2();
    } else {
      setSynergies([]);
      setSynergiesV2([]);
      setSynergiesV2Near([]);
    }
  }, [grid]);

  const loadData = async () => {
    try {
      // Pre-QA Stabilization 115C — fail-closed se manca server_id.
      if (!selected_server_id) {
        setHeroes([]);
        setConstellations([]);
        setLoading(false);
        return;
      }
      const heroesUrl = `/api/user/heroes?server_id=${encodeURIComponent(selected_server_id)}`;
      // Pre-QA Stabilization 115C — strict team read: get-formation server-scoped.
      const teamUrl = `/api/team/get-formation?server_id=${encodeURIComponent(selected_server_id)}`;
      const [uh, team, constData] = await Promise.all([
        apiCall(heroesUrl),
        apiCall(teamUrl).catch(() => ({ team_formation: [], formation: [], total_power: 0 })),
        apiCall('/api/constellations').catch(() => ({ constellations: [] })),
      ]);
      setHeroes(uh);
      const owned = (constData.constellations || []).filter((c: any) => c.owned);
      setConstellations(owned);
      if (team?.constellation_id) setSelectedConstellation(team.constellation_id);

      // Pack 126 FIX-A — Team formation contract repair (frontend adapter).
      // Backend POST /api/team/save-formation persiste come `team_formation`
      // con slot `{ hero_id, col, row }`. La risposta di GET /api/team/get-formation
      // puo' contenere `team_formation` (Pack 125+) o `formation` (legacy/Pack 87).
      // Normalizziamo entrambi e ricostruiamo la griglia con fallback robusto.
      const savedFormation: any[] = (team?.team_formation || team?.formation || []) as any[];
      if (savedFormation.length) {
        const ng: (any | null)[][] = [[null, null, null], [null, null, null], [null, null, null]];
        // Pre-QA Stabilization 116A-EXT FIX-A + Pack 126 FIX-A — Truth on team source/slot:
        //   - Pack 87 starter: `slot_index`.
        //   - Legacy pre-87: `x`/`y` (1-based).
        //   - Pack 125+ save: `hero_id` + `col`/`row` (0..2).
        //   - In tutti i casi: lookup hero per chiave (user_hero_id | hero_id | canonical_id).
        let cursor = 0;
        savedFormation.forEach((f: any, _i: number) => {
          // Pack 126 FIX-A — chiave eroe robusta: priorita' user_hero_id (legacy)
          // poi hero_id (Pack 125+) poi canonical_id (fallback).
          const savedHeroKey = f?.user_hero_id || f?.hero_id || f?.canonical_id;
          if (!savedHeroKey) return;
          // Pack 126 FIX-A — lookup eroe nel roster `uh` con triplo fallback:
          //   1. uh[].id === savedHeroKey         (Pack 87 ownership id)
          //   2. uh[].hero_id === savedHeroKey    (Pack 125+ canonical id)
          //   3. uh[].canonical_id === savedHeroKey (eventuale alias)
          const h = (uh || []).find((x: any) =>
            x?.id === savedHeroKey ||
            x?.hero_id === savedHeroKey ||
            x?.canonical_id === savedHeroKey
          );
          if (!h) return;
          let ci: number, ri: number;
          // Pack 126 FIX-A — supporto formati di posizione (in priorita'):
          //   1. col/row (Pack 125+): valori 0..2 diretti.
          //   2. x/y legacy: 1-based 1..9.
          //   3. slot_index: 0..8.
          //   4. fallback sequenziale.
          if (typeof f.col === 'number' && typeof f.row === 'number') {
            ci = Math.max(0, Math.min(2, f.col));
            ri = Math.max(0, Math.min(2, f.row));
          } else if (typeof f.x === 'number' && typeof f.y === 'number' && (f.x > 0 || f.y > 0)) {
            // Legacy 1-based grid (Pack pre-87).
            ci = f.x <= 2 ? 0 : f.x <= 5 ? 1 : 2;
            ri = f.y <= 2 ? 0 : f.y <= 5 ? 1 : 2;
          } else if (typeof f.slot_index === 'number') {
            const si = f.slot_index;
            ci = Math.max(0, Math.min(2, Math.floor(si / 3)));
            ri = Math.max(0, Math.min(2, si % 3));
          } else {
            ci = Math.max(0, Math.min(2, Math.floor(cursor / 3)));
            ri = Math.max(0, Math.min(2, cursor % 3));
            cursor++;
          }
          // Se la cella e' gia' occupata, scorri sequenzialmente fino a una
          // libera (truth: mai sovrascrivere un eroe gia' piazzato).
          if (ng[ci][ri]) {
            let placed = false;
            for (let cc = 0; cc < 3 && !placed; cc++) {
              for (let rr = 0; rr < 3 && !placed; rr++) {
                if (!ng[cc][rr]) {
                  ng[cc][rr] = h;
                  placed = true;
                }
              }
            }
          } else {
            ng[ci][ri] = h;
          }
        });
        setGrid(ng);
        // Pre-QA Stabilization 116A — il power NON viene piu' letto da
        // `team.total_power` (sorgente legacy non versionata). Lo prendiamo
        // dall'hook 116A (`useBattlePowerSummary`) per coerenza pre-QA.
      }
      // Pack 126-FIX-B — QA debug trace (dev only, no PII).
      if (__DEV__) {
        try {
          console.log('[pack_126_fix_b][battle.tsx] loadTeamData', {
            selected_server_id,
            heroes_count: Array.isArray(uh) ? uh.length : 'n/a',
            saved_formation_count: ((team?.team_formation || team?.formation) || []).length,
            constellations: (constData?.constellations || []).length,
            team_keys: team ? Object.keys(team) : [],
          });
        } catch (_logE) {}
      }
    } catch (e: any) {
      // Pack 126-FIX-B — no more silent catch. Show readable error in dev log + state.
      if (__DEV__) console.warn('[pack_126_fix_b][battle.tsx] loadTeamData failed:', e?.message || e);
      try { setHeroes([]); } catch (_se) {}
    } finally { setLoading(false); }
  };

  const placedIds = useMemo(() => {
    const ids: string[] = [];
    grid.forEach(col => col.forEach(h => { if (h) ids.push(h.id); }));
    return ids;
  }, [grid]);

  const filledCount = placedIds.length;

  // Auto-filter by class based on active column
  const activeClassFilter = activeCell !== null ? COLUMNS[activeCell.col].role : null;

  const filteredHeroes = useMemo(() => {
    let list = heroes.filter((h: any) => !placedIds.includes(h.id));
    // Filter by column class when a slot is selected
    if (activeClassFilter) {
      list = list.filter((h: any) => h.hero_class === activeClassFilter);
    }
    if (elemFilter !== 'all') {
      list = list.filter((h: any) => h.hero_element === elemFilter);
    }
    list.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'rarity': return (b.hero_rarity || 0) - (a.hero_rarity || 0) || (b.stars || 0) - (a.stars || 0);
        case 'level': return (b.level || 0) - (a.level || 0);
        case 'power': return ((b.hero_stats?.hp || 0) + (b.hero_stats?.physical_damage || 0)) - ((a.hero_stats?.hp || 0) + (a.hero_stats?.physical_damage || 0));
        case 'name': return (a.hero_name || '').localeCompare(b.hero_name || '');
        default: return 0;
      }
    });
    return list;
  }, [heroes, placedIds, activeClassFilter, elemFilter, sortBy]);

  const onCellPress = (col: number, row: number) => {
    if (grid[col][row]) {
      // Remove hero
      const ng = grid.map(c => [...c]);
      ng[col][row] = null;
      setGrid(ng);
      setActiveCell(null);
    } else {
      // Select this cell
      setActiveCell(activeCell?.col === col && activeCell?.row === row ? null : { col, row });
    }
  };

  const onHeroSelect = (hero: any) => {
    if (activeCell && !grid[activeCell.col][activeCell.row]) {
      const ng = grid.map(c => [...c]);
      ng[activeCell.col][activeCell.row] = hero;
      setGrid(ng);
      // Find next empty slot in same column first, then other columns
      let next: { col: number; row: number } | null = null;
      for (let r = activeCell.row + 1; r < 3; r++) {
        if (!ng[activeCell.col][r]) { next = { col: activeCell.col, row: r }; break; }
      }
      if (!next) {
        outer: for (let c = 0; c < 3; c++) {
          for (let r = 0; r < 3; r++) {
            if (!ng[c][r]) { next = { col: c, row: r }; break outer; }
          }
        }
      }
      setActiveCell(next);
    } else {
      // Find first empty slot
      for (let c = 0; c < 3; c++) {
        for (let r = 0; r < 3; r++) {
          if (!grid[c][r]) {
            const ng = grid.map(col => [...col]);
            ng[c][r] = hero;
            setGrid(ng);
            return;
          }
        }
      }
      Alert.alert('Squadra piena', 'Rimuovi un eroe prima.');
    }
  };

  const saveTeam = async () => {
    // Pack 125 FIX D — Team save server-scoped QA dev gated.
    // Endpoint POST /api/team/save-formation richiede:
    //   - server_id (no account-wide save)
    //   - QA_TEAM_SAVE_ENABLED=true env var lato backend
    //   - QA_TEAM_SAVE_ALLOWLIST contenente l'user_id corrente (o '*')
    //   - PSP esistente per (user_id, server_id)
    //   - ownership di tutti gli hero_id su quel server (o tag _qa_seed)
    //   - max 6 eroi, posizioni uniche, no duplicate hero
    // NO economy mutation, NO reward, NO progress: write SOLO su
    // player_server_profiles.team_formation.
    if (!selected_server_id) {
      Alert.alert(
        'Server richiesto',
        'Seleziona un server prima di salvare la formazione.'
      );
      return;
    }
    // Costruisce il payload dalla griglia attuale (col 0=Support, 1=DPS, 2=Tank, row 0..2).
    const team_formation: Array<{ hero_id: string; col: number; row: number }> = [];
    for (let col = 0; col < 3; col++) {
      for (let row = 0; row < 3; row++) {
        const h = grid[col]?.[row];
        if (h && h.id) team_formation.push({ hero_id: h.id, col, row });
      }
    }
    if (team_formation.length === 0) {
      Alert.alert('Squadra vuota', 'Aggiungi almeno un eroe prima di salvare.');
      return;
    }
    if (team_formation.length > 6) {
      Alert.alert('Squadra troppo grande', `Massimo 6 eroi (hai ${team_formation.length}).`);
      return;
    }
    setSaving(true);
    try {
      const res = await apiCall('/api/team/save-formation', {
        method: 'POST',
        body: JSON.stringify({ server_id: selected_server_id, team_formation }),
      });
      if (res?.status === 'OK') {
        Alert.alert(
          'Formazione salvata',
          `Team server-scoped salvato (server=${res.server_id}, ${res.team_size} eroi). Nessuna ricompensa, nessuna mutazione economy.`
        );
      } else {
        // Risposta inattesa: fallback a messaggio generico.
        Alert.alert('Salvataggio riuscito', 'Formazione persistita server-scoped.');
      }
    } catch (e: any) {
      // Gate disabilitato o blocker: messaggio chiaro per device QA.
      const status = e?.status || e?.response?.status;
      const detail = e?.data?.detail || e?.response?.data?.detail || e?.detail;
      const blocker = (detail && typeof detail === 'object' && detail.blocker) || null;
      if (status === 403 && blocker === 'QA_TEAM_SAVE_DISABLED') {
        Alert.alert(
          'Salvataggio formazione in preparazione',
          'TEAM_FORMATION_SAVE_DEFERRED_PRE_QA: l\'endpoint QA dev gated non e\' abilitato in questo ambiente. Per abilitarlo: QA_TEAM_SAVE_ENABLED=true + QA_TEAM_SAVE_ALLOWLIST. Per ora la formazione resta locale.'
        );
      } else if (status === 403 && blocker === 'QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED') {
        Alert.alert(
          'Account non in allowlist',
          'Questo account non e\' abilitato per QA team save. Contatta il dev per aggiungerlo alla allowlist.'
        );
      } else if (status === 404 && blocker === 'PLAYER_SERVER_PROFILE_REQUIRED') {
        Alert.alert('PSP mancante', 'Profilo server non trovato. Crea il PSP prima del save.');
      } else if (status === 400 && blocker === 'OWNERSHIP_VALIDATION_FAILED') {
        const missing = (detail.missing_hero_ids || []).join(', ');
        Alert.alert('Ownership non valida', `Eroi non posseduti su questo server: ${missing}`);
      } else {
        Alert.alert(
          'Errore salvataggio',
          (typeof detail === 'string' ? detail : detail?.message) || `Errore (${status || 'unknown'}).`
        );
      }
    } finally {
      setSaving(false);
    }
  };

  const clearAll = () => { setGrid([[null, null, null], [null, null, null], [null, null, null]]); setActiveCell({ col: 0, row: 0 }); };

  const selConst = constellations.find(c => c.id === selectedConstellation);

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.container}>
      <ActivityIndicator size="large" color={COLORS.accent} />
    </LinearGradient>
  );

  // Pre-QA Stabilization 115C — stato server-required (no fallback account-wide).
  if (!selected_server_id) {
    return (
      <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.container}>
        <View style={{ padding: 24, alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <Text style={{ color: '#FFD27F', fontSize: 18, fontWeight: '700', marginBottom: 12, textAlign: 'center' }}>
            Server richiesto
          </Text>
          <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14, textAlign: 'center', marginBottom: 24 }}>
            La formazione di battaglia richiede un server selezionato. Le superfici account-wide sono disabilitate in pre-QA.
          </Text>
          <TouchableOpacity
            onPress={() => router.push('/servers' as any)}
            activeOpacity={0.85}
            style={{ backgroundColor: '#7B2CBF', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}
          >
            <Text style={{ color: '#fff', fontWeight: '700' }}>Scegli un server</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.container}>
      {/* Header */}
      <View style={s.header}>
        <Text style={s.title}>FORMAZIONE SQUADRA</Text>
        <View style={s.headerMid}>
          <View style={s.powerBadge}>
            <Text style={s.powerIcon}>{'\u26A1'}</Text>
            <Text style={s.powerVal}>{bp.displayTeamPowerLabel}</Text>
          </View>
          <Text style={s.teamCount}>{filledCount}/9</Text>
        </View>
        <View style={s.headerRight}>
          <TouchableOpacity onPress={clearAll} style={s.clearBtn}>
            <Text style={s.clearTxt}>SVUOTA</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={saveTeam} disabled={saving} activeOpacity={0.7}>
            <LinearGradient colors={filledCount > 0 ? [COLORS.accent, '#FF4444'] : ['#333', '#222']} style={[s.saveBtn, saving && { opacity: 0.5 }]}>
              <Text style={s.saveTxt}>{saving ? '...' : '\u2714 SALVA'}</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </View>

      <View style={s.body}>
        {/* LEFT: 3x3 Grid */}
        <View style={s.gridPanel}>
          {/* Column headers */}
          <View style={s.colHeaders}>
            {COLUMNS.map((col, ci) => (
              <View key={col.role} style={[s.colHeader, { borderBottomColor: col.color }]}>
                <Text style={[s.colIcon]}>{col.icon}</Text>
                <Text style={[s.colLabel, { color: col.color }]}>{col.label}</Text>
                <Text style={s.colBonus}>{col.bonus}</Text>
              </View>
            ))}
          </View>

          {/* Grid rows */}
          {[0, 1, 2].map(row => (
            <View key={row} style={s.gridRow}>
              {COLUMNS.map((col, ci) => {
                const hero = grid[ci][row];
                const isActive = activeCell?.col === ci && activeCell?.row === row;
                const rarCol = hero ? RARITY.colors[Math.min(hero.hero_rarity || 1, 6)] || '#888' : 'transparent';

                return (
                  <TouchableOpacity
                    key={ci}
                    style={[
                      s.cell,
                      hero && { borderColor: rarCol + '80', backgroundColor: (ELEMENTS.colors[hero.hero_element] || '#888') + '06' },
                      isActive && !hero && { borderColor: col.color, backgroundColor: col.color + '0A' },
                    ]}
                    onPress={() => onCellPress(ci, row)}
                    activeOpacity={0.7}
                  >
                    {hero ? (
                      <View style={s.cellFilled}>
                        {hero.hero_image ? (
                          <View style={[s.cellImg, { borderColor: rarCol }]}>
                            <Image source={heroPortraitSource(hero.hero_image, hero.hero_id, hero.hero_name)} style={s.cellImgInner} />
                          </View>
                        ) : (
                          <AnimatedHeroPortrait imageUrl={null} name={hero.hero_name || '?'} rarity={hero.hero_rarity || 1} element={hero.hero_element} size={36} />
                        )}
                        <View style={s.cellInfo}>
                          <Text style={[s.cellName, { color: rarCol }]} numberOfLines={1}>{hero.hero_name}</Text>
                          <Text style={s.cellMeta}>{ELEMENTS.icons[hero.hero_element] || ''} {CLASSES.icons[hero.hero_class] || ''} Lv.{hero.level}</Text>
                          <View style={s.cellStars}>
                            {(hero.stars || hero.hero_rarity || 1) <= 12
                              ? <StarDisplay stars={hero.stars || hero.hero_rarity || 1} size={6} />
                              : <TranscendenceStars stars={hero.stars || hero.hero_rarity || 1} size={6} />}
                          </View>
                        </View>
                        <View style={s.removeBtn}><Text style={s.removeX}>{'\u00D7'}</Text></View>
                      </View>
                    ) : (
                      <View style={s.cellEmpty}>
                        <View style={[s.emptyCircle, isActive && { borderColor: col.color, backgroundColor: col.color + '15' }]}>
                          <Text style={[s.emptyPlus, isActive && { color: col.color }]}>+</Text>
                        </View>
                        <Text style={[s.emptyLabel, isActive && { color: col.color }]}>
                          {isActive ? 'SCEGLI' : col.role}
                        </Text>
                      </View>
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          ))}

          {/* Constellation selector */}
          <TouchableOpacity style={s.constBar} onPress={() => setShowConstellations(!showConstellations)} activeOpacity={0.7}>
            <Text style={s.constLabel}>{'\u264C'} Costellazione:</Text>
            {selConst ? (
              <View style={s.constSelected}>
                <Text style={s.constIcon}>{selConst.icon}</Text>
                <Text style={[s.constName, { color: selConst.color || COLORS.gold }]}>{selConst.name}</Text>
                <Text style={s.constBuff}>
                  {Object.entries(selConst.buff || {}).map(([k, v]: [string, any]) => `${k}+${Math.round(v * 100)}%`).join(' ')}
                </Text>
              </View>
            ) : (
              <Text style={s.constNone}>Nessuna - Tocca per scegliere</Text>
            )}
            <Text style={s.constArrow}>{showConstellations ? '\u25B2' : '\u25BC'}</Text>
          </TouchableOpacity>
          {showConstellations && (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.constList}>
              {constellations.map(c => (
                <TouchableOpacity
                  key={c.id}
                  style={[s.constItem, selectedConstellation === c.id && { borderColor: c.color || COLORS.gold, backgroundColor: (c.color || COLORS.gold) + '10' }]}
                  onPress={() => { setSelectedConstellation(c.id); setShowConstellations(false); }}
                >
                  <Text style={s.constItemIcon}>{c.icon}</Text>
                  <Text style={[s.constItemName, { color: c.color || COLORS.gold }]}>{c.name}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}

          {/* Active Synergies Display */}
          {synergies.length > 0 && (
            <View style={s.synergiesBar}>
              <Text style={s.synergiesTitle}>{'\u2728'} SINERGIE ATTIVE ({synergies.length})</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.synergiesList}>
                {synergies.map((syn: any, i: number) => {
                  const catColor = syn.category === 'mythological' ? '#FFD700' : syn.category === 'elemental' ? '#44AAFF' : '#44DD88';
                  return (
                    <View key={syn.id || i} style={[s.synergyChip, { borderColor: catColor + '50', backgroundColor: catColor + '08' }]}>
                      <Text style={s.synergyIcon}>{syn.icon}</Text>
                      <View>
                        <Text style={[s.synergyName, { color: catColor }]} numberOfLines={1}>{syn.name}</Text>
                        <Text style={s.synergyBuffs} numberOfLines={1}>
                          {Object.entries(syn.buffs || {}).map(([k, v]: [string, any]) => `${k}+${Math.round(v * 100)}%`).join(' ')}
                        </Text>
                      </View>
                    </View>
                  );
                })}
              </ScrollView>
            </View>
          )}

          {/* RM1.23-C: V2 Team Synergies (ID-based) — read-only display */}
          {filledCount > 0 && (
            <View style={s.synergiesV2Bar}>
              <Text style={s.synergiesV2Title}>
                {'\u2734'} SINERGIE SQUADRA V2 {synergiesV2.length > 0
                  ? `(${synergiesV2.length})`
                  : synergiesV2EnabledCount > 0
                    ? `(0/${synergiesV2EnabledCount})`
                    : ''}
              </Text>
              {synergiesV2.length > 0 ? (
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.synergiesList}>
                  {synergiesV2.map((syn) => {
                    const tierColor =
                      syn.rarity_tier === 'mythic' ? '#FF44CC'
                      : syn.rarity_tier === 'legendary' ? '#FFB347'
                      : syn.rarity_tier === 'epic' ? '#9966FF'
                      : syn.rarity_tier === 'rare' ? '#44AAFF'
                      : '#88CC88';
                    const buffPairs = Object.entries(syn.buffs || {})
                      .filter(([k]) => !k.endsWith('__flat'))
                      .map(([k, v]) => `${k}+${Math.round((v as number) * 100)}%`)
                      .join(' · ');
                    return (
                      <View
                        key={syn.id}
                        style={[s.synergyV2Chip, { borderColor: tierColor + '70', backgroundColor: tierColor + '10' }]}
                      >
                        <Text style={s.synergyV2Icon}>{syn.icon || '\u2734'}</Text>
                        <View style={{ flexShrink: 1 }}>
                          <Text style={[s.synergyV2Name, { color: tierColor }]} numberOfLines={1}>
                            {syn.display_name}
                          </Text>
                          <Text style={s.synergyV2Meta} numberOfLines={1}>
                            {syn.matched_count}/{syn.required_count}
                            {syn.avg_member_stars ? ` · ${syn.avg_member_stars.toFixed(1)}\u2605` : ''}
                          </Text>
                          <Text style={s.synergyV2Buffs} numberOfLines={1}>
                            {buffPairs || '—'}
                          </Text>
                        </View>
                      </View>
                    );
                  })}
                </ScrollView>
              ) : (
                <Text style={s.synergyV2Empty}>
                  Nessuna sinergia squadra V2 attiva
                </Text>
              )}

              {synergiesV2Near.length > 0 && (
                <View style={s.synergyV2NearWrap}>
                  <Text style={s.synergyV2NearTitle}>Quasi attive</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.synergiesList}>
                    {synergiesV2Near.map((nc) => (
                      <View key={nc.id} style={s.synergyV2NearChip}>
                        <Text style={s.synergyV2NearName} numberOfLines={1}>
                          {nc.display_name}
                        </Text>
                        <Text style={s.synergyV2NearMeta} numberOfLines={1}>
                          {nc.matched_count}/{nc.required_count}
                        </Text>
                      </View>
                    ))}
                  </ScrollView>
                </View>
              )}
            </View>
          )}
        </View>

        {/* RIGHT: Hero Roster */}
        <View style={s.rosterPanel}>
          {activeClassFilter && (
            <View style={[s.classIndicator, { backgroundColor: CLASSES.colors[activeClassFilter] + '15', borderColor: CLASSES.colors[activeClassFilter] + '40' }]}>
              <Text style={[s.classIndicatorTxt, { color: CLASSES.colors[activeClassFilter] }]}>
                {CLASSES.icons[activeClassFilter]} Solo {activeClassFilter}
              </Text>
            </View>
          )}
          {/* Element filter */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.filterRow}>
            {ELEM_FILTERS.map(f => (
              <TouchableOpacity
                key={f.key}
                style={[s.filterBtn, elemFilter === f.key && { backgroundColor: (ELEMENTS.colors[f.key] || COLORS.accent) + '20', borderColor: (ELEMENTS.colors[f.key] || COLORS.accent) + '60' }]}
                onPress={() => setElemFilter(f.key)}
              >
                <Text style={s.filterIcon}>{f.icon}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
          {/* Sort */}
          <View style={s.sortRow}>
            {([['rarity', 'Rarita'], ['level', 'Livello'], ['power', 'Potenza'], ['name', 'Nome']] as [SortKey, string][]).map(([key, label]) => (
              <TouchableOpacity key={key} style={[s.sortBtn, sortBy === key && s.sortActive]} onPress={() => setSortBy(key)}>
                <Text style={[s.sortTxt, sortBy === key && { color: COLORS.accent }]}>{label}</Text>
              </TouchableOpacity>
            ))}
            <Text style={s.rosterCount}>{filteredHeroes.length}</Text>
          </View>
          {/* Hero list */}
          <ScrollView style={s.heroScroll} contentContainerStyle={s.heroScrollContent} showsVerticalScrollIndicator={false}>
            {filteredHeroes.length === 0 ? (
              <Text style={s.noHeroes}>
                {activeClassFilter ? `Nessun ${activeClassFilter} disponibile` : 'Nessun eroe disponibile'}
              </Text>
            ) : (
              <View style={s.heroGrid}>
                {filteredHeroes.map((h: any) => {
                  const rarCol = RARITY.colors[Math.min(h.hero_rarity || 1, 6)] || '#888';
                  const elemCol = ELEMENTS.colors[h.hero_element] || '#888';
                  return (
                    <TouchableOpacity
                      key={h.id}
                      style={[s.heroCard, { borderColor: rarCol + '40' }]}
                      onPress={() => onHeroSelect(h)}
                      activeOpacity={0.7}
                    >
                      {h.hero_image ? (
                        <View style={[s.heroImg, { borderColor: rarCol }]}>
                          <Image source={heroPortraitSource(h.hero_image, h.hero_id, h.hero_name)} style={s.heroImgInner} />
                        </View>
                      ) : (
                        <View style={[s.heroImgPh, { backgroundColor: elemCol + '15', borderColor: rarCol }]}>
                          <Text style={[s.heroInit, { color: elemCol }]}>{(h.hero_name || '?')[0]}</Text>
                        </View>
                      )}
                      <View style={s.heroInfo}>
                        <Text style={[s.heroName, { color: rarCol }]} numberOfLines={1}>{h.hero_name}</Text>
                        <Text style={s.heroMeta}>{ELEMENTS.icons[h.hero_element] || ''} {CLASSES.icons[h.hero_class] || ''} Lv.{h.level}</Text>
                        <View style={s.heroStars}>
                          {(h.stars || h.hero_rarity || 1) <= 12
                            ? <StarDisplay stars={h.stars || h.hero_rarity || 1} size={6} />
                            : <TranscendenceStars stars={h.stars || h.hero_rarity || 1} size={6} />}
                        </View>
                      </View>
                    </TouchableOpacity>
                  );
                })}
              </View>
            )}
          </ScrollView>
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingVertical: 5,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.15)',
    backgroundColor: 'rgba(7,7,26,0.95)',
  },
  title: { color: '#fff', fontSize: 13, fontWeight: '900', letterSpacing: 1.5 },
  headerMid: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  powerBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(255,215,0,0.1)', paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)',
  },
  powerIcon: { fontSize: 10 },
  powerVal: { color: COLORS.gold, fontSize: 11, fontWeight: '800' },
  teamCount: { color: COLORS.textMuted, fontSize: 10, fontWeight: '700' },
  clearBtn: {
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6,
    backgroundColor: 'rgba(255,68,68,0.08)', borderWidth: 1, borderColor: 'rgba(255,68,68,0.2)',
  },
  clearTxt: { color: COLORS.error, fontSize: 8, fontWeight: '800' },
  saveBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  saveTxt: { color: '#fff', fontSize: 10, fontWeight: '900' },
  // Body
  body: { flex: 1, flexDirection: 'row', padding: 6, gap: 6 },
  // Grid Panel
  gridPanel: { width: 340, gap: 3 },
  colHeaders: { flexDirection: 'row', gap: 3, marginBottom: 2 },
  colHeader: { flex: 1, alignItems: 'center', paddingVertical: 3, borderBottomWidth: 2, backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 4 },
  colIcon: { fontSize: 14 },
  colLabel: { fontSize: 9, fontWeight: '900', letterSpacing: 0.5 },
  colBonus: { fontSize: 6, color: COLORS.textDim, marginTop: 1 },
  // Grid
  gridRow: { flexDirection: 'row', gap: 3 },
  cell: {
    flex: 1, minHeight: 58, borderRadius: 8, borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.08)', borderStyle: 'dashed',
    backgroundColor: 'rgba(255,255,255,0.01)', overflow: 'hidden',
  },
  cellFilled: { flex: 1, flexDirection: 'row', alignItems: 'center', padding: 4, gap: 5 },
  cellImg: { width: 38, height: 38, borderRadius: 7, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  cellImgInner: { width: '100%', height: '100%' },
  cellInfo: { flex: 1 },
  cellName: { fontSize: 8, fontWeight: '900' },
  cellMeta: { fontSize: 7, color: COLORS.textMuted, marginTop: 1 },
  cellStars: { fontSize: 6, color: COLORS.gold, marginTop: 1 },
  removeBtn: {
    position: 'absolute', top: 1, right: 1, width: 14, height: 14, borderRadius: 7,
    backgroundColor: 'rgba(255,68,68,0.8)', alignItems: 'center', justifyContent: 'center',
  },
  removeX: { color: '#fff', fontSize: 9, fontWeight: '900', lineHeight: 11 },
  cellEmpty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 4 },
  emptyCircle: {
    width: 28, height: 28, borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)', borderStyle: 'dashed',
    alignItems: 'center', justifyContent: 'center',
  },
  emptyPlus: { color: COLORS.textDim, fontSize: 16, fontWeight: '300' },
  emptyLabel: { color: COLORS.textDim, fontSize: 6, marginTop: 2, fontWeight: '700' },
  // Constellation
  constBar: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    padding: 6, borderRadius: 6, backgroundColor: 'rgba(255,215,0,0.04)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.15)', marginTop: 2,
  },
  constLabel: { color: COLORS.textMuted, fontSize: 8, fontWeight: '700' },
  constSelected: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 4 },
  constIcon: { fontSize: 14 },
  constName: { fontSize: 9, fontWeight: '900' },
  constBuff: { fontSize: 7, color: COLORS.textMuted },
  constNone: { flex: 1, color: COLORS.textDim, fontSize: 8, fontStyle: 'italic' },
  constArrow: { color: COLORS.textMuted, fontSize: 8 },
  constList: { gap: 4, paddingVertical: 4 },
  constItem: {
    alignItems: 'center', paddingHorizontal: 8, paddingVertical: 4,
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.02)', gap: 2,
  },
  constItemIcon: { fontSize: 16 },
  constItemName: { fontSize: 7, fontWeight: '800' },
  // Synergies
  synergiesBar: {
    backgroundColor: 'rgba(255,215,0,0.04)', borderRadius: 6, padding: 5,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.12)', marginTop: 2,
  },
  synergiesTitle: { color: COLORS.gold, fontSize: 7, fontWeight: '900', letterSpacing: 0.5, marginBottom: 3 },
  synergiesList: { gap: 4 },
  synergyChip: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 6, paddingVertical: 3, borderRadius: 5, borderWidth: 1,
  },
  synergyIcon: { fontSize: 12 },
  synergyName: { fontSize: 7, fontWeight: '800' },
  synergyBuffs: { fontSize: 6, color: COLORS.textMuted },

  // ── RM1.23-C: V2 Team Synergies UI (compact, premium) ───────────────
  synergiesV2Bar: {
    backgroundColor: '#1A0F2E',
    borderTopWidth: 1,
    borderTopColor: '#FFB34730',
    paddingHorizontal: 6,
    paddingVertical: 4,
  },
  synergiesV2Title: {
    color: '#FFB347',
    fontSize: 7,
    fontWeight: '900',
    letterSpacing: 0.5,
    marginBottom: 3,
  },
  synergyV2Chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    gap: 4,
    marginRight: 4,
    minWidth: 110,
    maxWidth: 180,
  },
  synergyV2Icon: { fontSize: 12 },
  synergyV2Name: { fontSize: 8, fontWeight: '800' },
  synergyV2Meta: { fontSize: 6, color: COLORS.textMuted, opacity: 0.85 },
  synergyV2Buffs: { fontSize: 6, color: COLORS.gold, fontWeight: '700' },
  synergyV2Empty: {
    fontSize: 6,
    color: COLORS.textMuted,
    fontStyle: 'italic',
    paddingVertical: 2,
  },
  synergyV2NearWrap: {
    marginTop: 4,
    borderTopWidth: 1,
    borderTopColor: '#44444430',
    paddingTop: 3,
  },
  synergyV2NearTitle: {
    color: '#88AABB',
    fontSize: 6,
    fontWeight: '800',
    marginBottom: 2,
    letterSpacing: 0.5,
  },
  synergyV2NearChip: {
    backgroundColor: '#222',
    borderWidth: 1,
    borderColor: '#444',
    borderRadius: 4,
    paddingHorizontal: 5,
    paddingVertical: 2,
    marginRight: 3,
  },
  synergyV2NearName: { fontSize: 7, color: '#AAB4BB', fontWeight: '700' },
  synergyV2NearMeta: { fontSize: 6, color: COLORS.textMuted },
  // Roster Panel
  rosterPanel: { flex: 1, gap: 3 },
  classIndicator: {
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, borderWidth: 1,
    alignSelf: 'flex-start',
  },
  classIndicatorTxt: { fontSize: 9, fontWeight: '800' },
  filterRow: { gap: 3, paddingBottom: 1 },
  filterBtn: {
    paddingHorizontal: 7, paddingVertical: 3, borderRadius: 5,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  filterIcon: { fontSize: 11 },
  sortRow: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  sortBtn: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.02)' },
  sortActive: { backgroundColor: 'rgba(255,107,53,0.1)' },
  sortTxt: { color: COLORS.textMuted, fontSize: 8, fontWeight: '700' },
  rosterCount: { color: COLORS.textDim, fontSize: 8, marginLeft: 'auto', fontWeight: '600' },
  heroScroll: { flex: 1 },
  heroScrollContent: { paddingBottom: 8 },
  heroGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 3 },
  noHeroes: { color: COLORS.textDim, fontSize: 9, textAlign: 'center', padding: 16 },
  heroCard: {
    width: 105, flexDirection: 'row', alignItems: 'center', gap: 4,
    padding: 4, borderRadius: 6, borderWidth: 1, backgroundColor: 'rgba(255,255,255,0.02)',
  },
  heroImg: { width: 32, height: 32, borderRadius: 5, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  heroImgInner: { width: '100%', height: '100%' },
  heroImgPh: { width: 32, height: 32, borderRadius: 5, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  heroInit: { fontSize: 14, fontWeight: '900' },
  heroInfo: { flex: 1 },
  heroName: { fontSize: 7, fontWeight: '900' },
  heroMeta: { fontSize: 7, color: COLORS.textMuted, marginTop: 1 },
  heroStars: { fontSize: 6, color: COLORS.gold, marginTop: 1 },
});

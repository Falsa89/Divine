/**
 * MEGA_RELEASE_ACCELERATION_40_v91_FIXED — Pre-Battle Lobby
 *
 * Schermata intermedia tra il menu modalità e /combat (renderer Home battle reale).
 * Mostra:
 *   - source_type / source_id / encounter_id deterministici (NESSUN random runtime)
 *   - dettagli dell'avversario (team / boss) caricati da catalogo canonico locale
 *   - team del player (saved formation, letto da AsyncStorage / fallback locale)
 *   - bottone "Modifica Team" → /(tabs)/battle (formation editor esistente)
 *   - bottone "Avvia Battaglia" → /combat?mode=X&encounter_id=Y&source_id=Z
 *
 * Garanzie:
 *   - random_opponents_allowed = false (lobby + policy + catalogo)
 *   - runtime_random_enemy_generation_allowed = false
 *   - fallback_random_allowed = false
 *   - NESSUNA mutazione DB / reward / endpoint / battle_engine autoritativo
 *   - NESSUNA modifica a frontend/app/combat.tsx (MD5-locked)
 *
 * Source di dati: catalogo statico importato da
 *   /app/data/design/battle_mode_enemy_sources/*.json
 * I dati sono inseriti inline in questo file come fallback deterministico locale
 * per evitare richieste di rete al backend (preview-only). Una versione successiva
 * potrà sostituire l'inline con un fetch a /api/encounter-source/get (NUOVO pack).
 */
import React, { useMemo, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

// v107D — Battle Launch Contract real binding (MD5 supersede authorized).
// Adopts launchFromLobby() helper as a non-destructive telemetry call.
import { launchFromLobby } from '../src/battle_launch/consumers/preBattleLobbyAdapter';
// v108_POSTQA_A — AsyncStorage per leggere selected server reale (NO hardcoded 's1').
import AsyncStorage from '@react-native-async-storage/async-storage';

// ─────────────────────────────────────────────────────────────────────────
// Inline catalog mirror — DETERMINISTIC, NO RUNTIME RANDOM
// Mirror dei file:
//   data/design/battle_mode_enemy_sources/*_stub_catalog_v1.json
// random_opponents_allowed: false in tutti i casi.
// ─────────────────────────────────────────────────────────────────────────

type EnemyUnit = {
  hero_id: string;
  role: string;
  level: number;
  stars: number;
  power: number;
};

type ModeEncounter = {
  source_type: string;
  source_id: string;
  mode: string;
  encounter_id: string;
  display_title: string;
  display_subtitle: string;
  enemies: EnemyUnit[];
  is_random: false;
  runtime_generated: false;
  fallback_random_allowed: false;
};

const CANONICAL_ENCOUNTERS: Record<string, ModeEncounter> = {
  story: {
    source_type: 'story_stage_encounter_table',
    source_id: 'story_chapter_01_stage_01',
    mode: 'story',
    encounter_id: 'enc_story_1_1_intro_grunts',
    display_title: 'Capitolo 1 · Stage 1-1',
    display_subtitle: 'Pattuglia di Avanguardia',
    enemies: [
      { hero_id: 'story_grunt_a', role: 'dps', level: 1, stars: 1, power: 800 },
      { hero_id: 'story_grunt_b', role: 'dps', level: 1, stars: 1, power: 850 },
      { hero_id: 'story_lieutenant', role: 'tank', level: 2, stars: 1, power: 1200 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  tower: {
    source_type: 'tower_floor_encounter_table',
    source_id: 'tower_season_01_floor_10',
    mode: 'tower',
    encounter_id: 'enc_tower_S01_F10_mid_boss',
    display_title: 'Torre · Piano 10 (S01)',
    display_subtitle: 'Guardiano Intermedio',
    enemies: [
      { hero_id: 'tower_minion_a', role: 'tank', level: 15, stars: 3, power: 4200 },
      { hero_id: 'tower_minion_b', role: 'dps', level: 15, stars: 3, power: 4500 },
      { hero_id: 'tower_minion_c', role: 'healer', level: 15, stars: 3, power: 4000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  arena: {
    source_type: 'persistent_bot_profile_team',
    source_id: 'arena_bot_mid_tier',
    mode: 'arena',
    encounter_id: 'bot_arena_mid_001',
    display_title: 'Arena PvP · Bot Persistente (Mid Tier)',
    display_subtitle: 'Bot ID: bot_arena_mid_001',
    enemies: [
      { hero_id: 'alpha_arena_hero_01', role: 'dps', level: 25, stars: 3, power: 5333 },
      { hero_id: 'alpha_arena_hero_02', role: 'dps', level: 25, stars: 3, power: 5333 },
      { hero_id: 'alpha_arena_hero_03', role: 'support', level: 25, stars: 3, power: 5334 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  training: {
    source_type: 'training_preset_catalog',
    source_id: 'training_frontline',
    mode: 'training',
    encounter_id: 'enc_training_frontline_test',
    display_title: 'Addestramento · Frontline Test',
    display_subtitle: 'Preset: frontline_test_v1',
    enemies: [
      { hero_id: 'alpha_trainee_hero_03', role: 'tank', level: 10, stars: 2, power: 2500 },
      { hero_id: 'alpha_trainee_hero_01', role: 'dps', level: 10, stars: 2, power: 2300 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  boss: {
    source_type: 'raid_boss_catalog',
    source_id: 'raid_world_boss_01',
    mode: 'raid',
    encounter_id: 'enc_raid_world_boss_01',
    display_title: 'Raid · Boss Mondiale 01',
    display_subtitle: 'Raid ID: raid_wb_01',
    enemies: [
      { hero_id: 'alpha_raid_boss_placeholder_01', role: 'boss', level: 40, stars: 5, power: 25000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
};

// Pack 79 — RUNTIME REAL UI FIX (MD5 rebase autorizzato).
// NESSUN fallback fake a 3 slot player-facing. La fallback è ora vuota.
// Quando manca il team reale, viene attivato il blocker PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER.
const PLAYER_SAFE_FALLBACK_TEAM: EnemyUnit[] = [];

// v93/v110 — Real Formation Source resolution.
// Pack 79: fallback rimosso, source label estesa a `blocked_no_team_for_server` con
// blocker chain già attiva nel componente.
type FormationSourceLabel = 'saved_formation' | 'local_cached_formation' | 'safe_fallback_formation' | 'blocked_no_team_for_server';

function resolvePlayerFormation(): { team: EnemyUnit[]; source: FormationSourceLabel; fallback_used: boolean } {
  return { team: PLAYER_SAFE_FALLBACK_TEAM, source: 'blocked_no_team_for_server', fallback_used: true };
}

// ─────────────────────────────────────────────────────────────────────────
// UI
// ─────────────────────────────────────────────────────────────────────────

const ROLE_COLOR: Record<string, string> = {
  tank: '#4499FF',
  dps: '#FF5544',
  healer: '#44DD99',
  support: '#FFD700',
  control: '#BB55FF',
  boss: '#FF44AA',
};

function UnitCard({ unit }: { unit: EnemyUnit }) {
  const c = ROLE_COLOR[unit.role] || '#888';
  return (
    <View style={[s.unitCard, { borderColor: c }]}>
      <View style={[s.unitRoleBadge, { backgroundColor: c }]}>
        <Text style={s.unitRoleText}>{unit.role.toUpperCase()}</Text>
      </View>
      <Text style={s.unitHeroId} numberOfLines={1}>
        {unit.hero_id}
      </Text>
      <Text style={s.unitMeta}>
        Lv.{unit.level} · ★{unit.stars}
      </Text>
      <Text style={s.unitPower}>PWR {unit.power}</Text>
    </View>
  );
}

function SourceBadge({ enc }: { enc: ModeEncounter }) {
  return (
    <View style={s.sourceBadge}>
      <Text style={s.sourceBadgeTitle}>SOURCE CANONICA · NO RANDOM</Text>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>source_type:</Text>
        <Text style={s.sourceVal}>{enc.source_type}</Text>
      </View>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>source_id:</Text>
        <Text style={s.sourceVal}>{enc.source_id}</Text>
      </View>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>encounter_id:</Text>
        <Text style={s.sourceVal}>{enc.encounter_id}</Text>
      </View>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>is_random:</Text>
        <Text style={[s.sourceVal, s.sourceFalse]}>false</Text>
      </View>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>runtime_generated:</Text>
        <Text style={[s.sourceVal, s.sourceFalse]}>false</Text>
      </View>
      <View style={s.sourceBadgeRow}>
        <Text style={s.sourceKey}>fallback_random_allowed:</Text>
        <Text style={[s.sourceVal, s.sourceFalse]}>false</Text>
      </View>
    </View>
  );
}

export default function PreBattleLobbyScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ mode?: string; source_id?: string; encounter_id?: string; enemy_source_id?: string; enemy_source_type?: string; v108_pre?: string }>();
  const modeParam = (params.mode || 'story').toString();
  const mode = (CANONICAL_ENCOUNTERS[modeParam] ? modeParam : 'story') as keyof typeof CANONICAL_ENCOUNTERS;
  // v108_pre — compatibility: story.tsx passa encounter_id / enemy_source_id;
  // legacy passa source_id. Normalizziamo qui senza riscrivere il flow.
  const v108EncounterId = (params.encounter_id || params.source_id || '').toString();
  const v108EnemySourceId = (params.enemy_source_id || params.source_id || params.encounter_id || '').toString();

  const encounter = CANONICAL_ENCOUNTERS[mode];
  const playerFormation = resolvePlayerFormation();
  const playerTeam = playerFormation.team;

  // v107D — Real binding to /api/battle/launch (gated, default OFF, telemetry only).
  useEffect(() => {
    const enabled = (process.env.EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED || '').toString() === 'true';
    if (!enabled) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await launchFromLobby({
          server_id: (selectedServerId || 'unknown'), mode: (mode as 'story') || 'story',
          encounter_id: String(v108EncounterId || params.source_id || mode), enemy_source_type: 'authored',
          enemy_source_id: String(v108EnemySourceId || params.source_id || `${mode}_default`),
          player_team_snapshot: playerTeam, client_trace_id: `v107d-${Date.now()}`,
        });
        if (!cancelled && __DEV__) console.log('[v107D] lobby launch:', res.response_status);
      } catch (_e) { /* preview-only */ }
    })();
    return () => { cancelled = true; };
  }, [mode, params.source_id, v108EncounterId, v108EnemySourceId, playerTeam, selectedServerId]);

  // v95 — Endpoint runtime fetch (read-only catalog) per dichiarare la source attiva.
  //  - endpoint_active=true      → /api/encounter-source/get raggiunto e dati validi
  //  - endpoint_fetch_failed_fallback_local_readonly=true → fallback inline locale dichiarato
  // NESSUNA modifica al dato visualizzato: il fetch serve a confermare che
  // l'endpoint v95 risponde. I mirror inline restano come safe fallback dichiarato.
  const backendUrl = (process.env.EXPO_BACKEND_URL || '').toString();
  const [v95SourceStatus, setV95SourceStatus] = useState<'unknown' | 'endpoint_active' | 'endpoint_fetch_failed_fallback_local_readonly'>('unknown');
  useEffect(() => {
    let cancelled = false;
    const ctrl = new AbortController();
    const url = `${backendUrl}/api/encounter-source/get?mode=${encodeURIComponent(mode)}`;
    fetch(url, { signal: ctrl.signal })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => { if (!cancelled && d && d.v95_readonly === true) setV95SourceStatus('endpoint_active'); else if (!cancelled) setV95SourceStatus('endpoint_fetch_failed_fallback_local_readonly'); })
      .catch(() => { if (!cancelled) setV95SourceStatus('endpoint_fetch_failed_fallback_local_readonly'); });
    return () => { cancelled = true; ctrl.abort(); };
  }, [mode, backendUrl]);

  const playerPower = useMemo(
    () => playerTeam.reduce((sum, u) => sum + u.power, 0),
    [playerTeam],
  );
  const enemyPower = useMemo(
    () => encounter.enemies.reduce((sum, u) => sum + u.power, 0),
    [encounter],
  );

  // v108_POSTQA_A — Selected server reale da AsyncStorage. NO hardcoded 's1'.
  // Se manca, mostriamo blocker SELECTED_SERVER_REQUIRED e disabilitiamo launch.
  const [selectedServerId, setSelectedServerId] = useState<string | null>(null);
  const [selectedServerLoaded, setSelectedServerLoaded] = useState<boolean>(false);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const sid = await AsyncStorage.getItem('selected_server_id');
        if (!cancelled) { setSelectedServerId(sid && sid.trim() ? sid.trim() : null); setSelectedServerLoaded(true); }
      } catch (_e) { if (!cancelled) { setSelectedServerId(null); setSelectedServerLoaded(true); } }
    })();
    return () => { cancelled = true; };
  }, []);

  // v108_POSTQA_A — Blocker chain onesti.
  // 1) REAL_PLAYER_TEAM_SOURCE_PENDING: il team del player e' ancora il safe_fallback,
  //    NON deve essere spacciato per reale. Launch normale disabilitato.
  // 2) AUTHORED_ENCOUNTER_SOURCE_PENDING: encounter non e' da catalogo authored
  //    consolidato. Launch normale disabilitato.
  // 3) SELECTED_SERVER_REQUIRED: server reale assente. Launch normale disabilitato.
  // 4) QA fallback launch dietro flag EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH.
  // Pack 79: il blocker scatta sia con `safe_fallback_formation` sia con `blocked_no_team_for_server`.
  const realPlayerTeamAvailable = (
    playerFormation.source !== 'safe_fallback_formation'
    && playerFormation.source !== 'blocked_no_team_for_server'
    && !playerFormation.fallback_used
    && (playerFormation.team?.length || 0) > 0
  );
  const authoredEncounterAvailable = !!(encounter && encounter.source_type === 'authored' && (encounter.enemies?.length || 0) > 0);
  const selectedServerAvailable = !!(selectedServerLoaded && selectedServerId);
  const blockerReasons: string[] = [];
  if (!realPlayerTeamAvailable) blockerReasons.push('PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER');
  if (!authoredEncounterAvailable) blockerReasons.push('AUTHORED_ENCOUNTER_SOURCE_PENDING');
  if (!selectedServerAvailable) blockerReasons.push('SELECTED_SERVER_REQUIRED');
  const launchAllowedNormal = blockerReasons.length === 0;
  const qaFallbackEnabled = process.env.EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH === 'true';

  const startBattle = () => {
    // v108_POSTQA_A — Bloccatore onesto: se non e' tutto reale, NON entrare in /combat
    // con fallback team/enemy spacciati per reali. Mostriamo i blocker.
    if (!launchAllowedNormal && !qaFallbackEnabled) {
      if (__DEV__) console.log('[v108_POSTQA_A] launch blocked:', blockerReasons);
      return;
    }
    // v108_POSTQA_A — passare a /combat un launch_context valido (Battle Launch Contract v1)
    // affinche' combat.tsx possa applicare PREVIEW_REWARD_LOCK_ACTIVE. Default preview.
    const launchContext = {
      battle_engine_mode: 'preview',
      is_preview: true,
      reward_policy: 'preview',
      progress_policy: 'preview',
      server_id: selectedServerId || 'unknown',
      mode,
      encounter_id: encounter.encounter_id,
      source_id: encounter.source_id,
      source_type: encounter.source_type,
      qa_fallback_used: qaFallbackEnabled && !launchAllowedNormal,
    };
    const battle_launch_id = `v108_postqa_${Date.now()}`;
    const target = `/combat?mode=${encodeURIComponent(mode)}&encounter_id=${encodeURIComponent(
      encounter.encounter_id,
    )}&source_id=${encodeURIComponent(encounter.source_id)}&launch_context=${encodeURIComponent(JSON.stringify(launchContext))}&battle_launch_id=${encodeURIComponent(battle_launch_id)}`;
    router.push(target as any);
  };

  const modifyTeam = () => {
    router.push('/(tabs)/battle' as any);
  };

  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/(tabs)/menu' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#0A1430', '#1A2850']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          {/* Header */}
          <View style={s.header}>
            <TouchableOpacity onPress={goBack} style={s.backBtn}>
              <Text style={s.backTxt}>← Indietro</Text>
            </TouchableOpacity>
            <Text style={s.title}>Pre-Battle Lobby</Text>
            <Text style={s.subtitle}>{encounter.display_title}</Text>
            <Text style={s.subtitleSmall}>{encounter.display_subtitle}</Text>
          </View>

          {/* Source canonica */}
          <SourceBadge enc={encounter} />

          {/* v95 — Catalog source status (endpoint runtime vs fallback locale) */}
          <View style={s.section}>
            <Text style={s.sectionTitle}>v95 Catalog Source</Text>
            <Text style={s.sourceVal}>
              {v95SourceStatus === 'endpoint_active'
                ? '✓ endpoint_active (/api/encounter-source/get)'
                : v95SourceStatus === 'endpoint_fetch_failed_fallback_local_readonly'
                  ? '⚠ endpoint_fetch_failed_fallback_local_readonly=true (mirror locale read-only)'
                  : '… in attesa…'}
            </Text>
          </View>

          {/* Enemy team */}
          <View style={s.section}>
            <View style={s.sectionHeader}>
              <Text style={s.sectionTitle}>Squadra Avversaria</Text>
              <Text style={s.sectionPower}>Potenza totale: {enemyPower}</Text>
            </View>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={s.unitRow}>
                {encounter.enemies.map((u, i) => (
                  <UnitCard key={`enemy-${i}`} unit={u} />
                ))}
              </View>
            </ScrollView>
          </View>

          {/* Player team */}
          <View style={s.section}>
            <View style={s.sectionHeader}>
              <Text style={s.sectionTitle}>
                Il Tuo Team · source: {playerFormation.source}
                {playerFormation.fallback_used ? ' · fallback_used=true' : ''}
              </Text>
              <Text style={s.sectionPower}>Potenza totale: {playerPower}</Text>
            </View>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={s.unitRow}>
                {playerTeam.map((u, i) => (
                  <UnitCard key={`player-${i}`} unit={u} />
                ))}
              </View>
            </ScrollView>
          </View>

          {/* Actions */}
          <View style={s.actions}>
            <TouchableOpacity
              style={[s.actionBtn, s.actionModify]}
              onPress={modifyTeam}
              activeOpacity={0.85}
            >
              <Text style={s.actionTxt}>✎ Modifica Team</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[s.actionBtn, s.actionStart, (!launchAllowedNormal && !qaFallbackEnabled) ? { opacity: 0.4 } : null]}
              onPress={startBattle}
              activeOpacity={0.85}
              disabled={!launchAllowedNormal && !qaFallbackEnabled}
            >
              <Text style={s.actionTxt}>{(!launchAllowedNormal && !qaFallbackEnabled) ? '⛔ Launch bloccato' : (qaFallbackEnabled && !launchAllowedNormal ? '▶ Avvia (QA Fallback)' : '▶ Avvia Battaglia')}</Text>
            </TouchableOpacity>
          </View>

          {/* v108_POSTQA_A — Blocker chain visibili e onesti. */}
          {blockerReasons.length > 0 ? (
            <View style={{ marginTop: 12, padding: 12, borderRadius: 8, backgroundColor: 'rgba(244,67,54,0.10)', borderWidth: 1, borderColor: 'rgba(244,67,54,0.40)' }}>
              <Text style={{ color: '#ff8a80', fontSize: 11, fontWeight: '800', letterSpacing: 1, marginBottom: 6 }}>LAUNCH BLOCKERS (v108_POSTQA_A)</Text>
              {blockerReasons.map(b => (
                <Text key={b} style={{ color: '#ffbcbc', fontSize: 10, fontWeight: '600', marginVertical: 1 }}>• {b}</Text>
              ))}
              <Text style={{ color: '#999', fontSize: 9, marginTop: 6, lineHeight: 13 }}>Il fallback team/enemy non puo' essere spacciato come reale. Sblocca caricando team reale, encounter authored e selected server. QA fallback dietro flag EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH.</Text>
            </View>
          ) : null}

          {/* Safety footer */}
          <View style={s.safetyFooter}>
            <Text style={s.safetyTxt}>
              v91 FIXED · preview-only · db_writes=0 · reward_live=false · endpoint_live=false ·
              battle_engine_authoritative=false · random_opponents_allowed=false
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A1430' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  header: { marginBottom: 16 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#88AAFF', fontSize: 14 },
  title: { color: '#FFD700', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#FFFFFF', fontSize: 16, fontWeight: '600', textAlign: 'center', marginTop: 4 },
  subtitleSmall: { color: '#AABBDD', fontSize: 12, textAlign: 'center', marginTop: 2 },

  sourceBadge: {
    backgroundColor: 'rgba(0,40,80,0.6)',
    borderColor: '#44DDFF',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  sourceBadgeTitle: { color: '#44DDFF', fontSize: 11, fontWeight: '700', marginBottom: 8, letterSpacing: 1 },
  sourceBadgeRow: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 2 },
  sourceKey: { color: '#AABBDD', fontSize: 11, fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace' }) },
  sourceVal: {
    color: '#FFFFFF',
    fontSize: 11,
    fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace' }),
    flexShrink: 1,
    textAlign: 'right',
  },
  sourceFalse: { color: '#FF6644' },

  section: { marginBottom: 16 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  sectionTitle: { color: '#FFD700', fontSize: 14, fontWeight: '700' },
  sectionPower: { color: '#AABBDD', fontSize: 12 },
  unitRow: { flexDirection: 'row', gap: 10 },

  unitCard: {
    width: 100,
    backgroundColor: 'rgba(20,40,80,0.7)',
    borderWidth: 2,
    borderRadius: 8,
    padding: 8,
    alignItems: 'center',
  },
  unitRoleBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, marginBottom: 4 },
  unitRoleText: { color: '#000', fontSize: 9, fontWeight: '800' },
  unitHeroId: { color: '#FFF', fontSize: 10, fontWeight: '600', textAlign: 'center', marginBottom: 4 },
  unitMeta: { color: '#AABBDD', fontSize: 10 },
  unitPower: { color: '#FFD700', fontSize: 11, fontWeight: '700', marginTop: 2 },

  actions: { flexDirection: 'row', gap: 12, marginTop: 8, marginBottom: 16 },
  actionBtn: { flex: 1, paddingVertical: 14, borderRadius: 10, alignItems: 'center', minHeight: 48 },
  actionModify: { backgroundColor: '#444466' },
  actionStart: { backgroundColor: '#22BB66' },
  actionTxt: { color: '#FFFFFF', fontSize: 15, fontWeight: '800' },

  safetyFooter: { marginTop: 8, padding: 8, borderRadius: 6, backgroundColor: 'rgba(0,0,0,0.3)' },
  safetyTxt: {
    color: '#88AAAA',
    fontSize: 9,
    textAlign: 'center',
    fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace' }),
  },
});

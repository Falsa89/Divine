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
import React, { useMemo } from 'react';
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

// Player team mock per preview-only (in produzione verrebbe da
// /api/user/get-formation o AsyncStorage). NESSUN random.
const PLAYER_SAFE_FALLBACK_TEAM: EnemyUnit[] = [
  { hero_id: 'alpha_trainee_hero_01', role: 'dps', level: 12, stars: 2, power: 2600 },
  { hero_id: 'alpha_trainee_hero_02', role: 'healer', level: 12, stars: 2, power: 2400 },
  { hero_id: 'alpha_trainee_hero_03', role: 'tank', level: 12, stars: 2, power: 2800 },
];

// v93 — Real Formation Source resolution.
// Tenta di leggere la formation salvata in ordine: api saved -> local cached -> safe fallback.
// In v93 NON facciamo chiamate API (mantiene preview-only / no DB writes).
// Una versione successiva integrera' /api/team/get-formation se safe.
type FormationSourceLabel = 'saved_formation' | 'local_cached_formation' | 'safe_fallback_formation';

function resolvePlayerFormation(): { team: EnemyUnit[]; source: FormationSourceLabel; fallback_used: boolean } {
  // v93: per ora restituiamo sempre safe_fallback_formation con flag esplicito.
  // L'integrazione reale con /api/team/get-formation arrivera' in un pack
  // successivo che possa farlo in modo safe senza modificare i file MD5-lockati.
  return { team: PLAYER_SAFE_FALLBACK_TEAM, source: 'safe_fallback_formation', fallback_used: true };
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
  const params = useLocalSearchParams<{ mode?: string; source_id?: string }>();
  const modeParam = (params.mode || 'story').toString();
  const mode = (CANONICAL_ENCOUNTERS[modeParam] ? modeParam : 'story') as keyof typeof CANONICAL_ENCOUNTERS;

  const encounter = CANONICAL_ENCOUNTERS[mode];
  const playerFormation = resolvePlayerFormation();
  const playerTeam = playerFormation.team;

  const playerPower = useMemo(
    () => playerTeam.reduce((sum, u) => sum + u.power, 0),
    [playerTeam],
  );
  const enemyPower = useMemo(
    () => encounter.enemies.reduce((sum, u) => sum + u.power, 0),
    [encounter],
  );

  const startBattle = () => {
    const target = `/combat?mode=${encodeURIComponent(mode)}&encounter_id=${encodeURIComponent(
      encounter.encounter_id,
    )}&source_id=${encodeURIComponent(encounter.source_id)}`;
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
              style={[s.actionBtn, s.actionStart]}
              onPress={startBattle}
              activeOpacity={0.85}
            >
              <Text style={s.actionTxt}>▶ Avvia Battaglia</Text>
            </TouchableOpacity>
          </View>

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

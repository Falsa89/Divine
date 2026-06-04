/**
 * MEGA_RELEASE_ACCELERATION_41_v92 — Live Mode Pre-Entry Lobby
 *
 * Pre-entry lobby per modalita' live/guild/special accessibili tramite QA Hub.
 * Mostra:
 *   - source canonica (source_type, source_id, encounter_id)
 *   - QA window status (FORZATO APERTO via QA override, oppure CHIUSO)
 *   - avatar placeholder usage (se richiesto)
 *   - team avversario / boss / wave deterministico da catalogo
 *   - bottoni: Avvia Test Battle / Avvia Test Flow (layout-only) / Indietro
 *
 * Garanzie:
 *   - qa_override_only = true
 *   - production_enabled = false
 *   - reward_live = false
 *   - ranking_live = false
 *   - event_currency_live = false
 *   - guild_score_mutation = 0
 *   - random_opponents_allowed = false
 *   - db_writes = 0
 */
import React, { useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

type EnemyUnit = {
  hero_id: string;
  role: string;
  level: number;
  stars: number;
  power: number;
};

type LiveEncounter = {
  mode_id: string;
  label: string;
  source_type: string;
  source_id: string;
  encounter_id: string | null;
  battle_required: boolean;
  avatar_required: boolean;
  avatar_id?: string;
  guild_required: boolean;
  enemies: EnemyUnit[];
  is_random: false;
  runtime_generated: false;
  fallback_random_allowed: false;
};

// Mirror del catalogo
// /app/data/design/live_mode_testability/live_guild_special_mode_encounter_source_catalog_v1.json
const LIVE_ENCOUNTERS: Record<string, LiveEncounter> = {
  event: {
    mode_id: 'event',
    label: 'Eventi Live (generico)',
    source_type: 'event_schedule_encounter',
    source_id: 'event_summer_invasion_stage_01',
    encounter_id: 'enc_event_summer_invasion_s1_grunts',
    battle_required: true,
    avatar_required: false,
    guild_required: false,
    enemies: [
      { hero_id: 'alpha_event_hero_01', role: 'dps', level: 20, stars: 3, power: 4000 },
      { hero_id: 'alpha_event_hero_02', role: 'healer', level: 20, stars: 3, power: 4200 },
      { hero_id: 'alpha_event_hero_03', role: 'tank', level: 22, stars: 3, power: 5000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  crepuscolo_dei_titani: {
    mode_id: 'crepuscolo_dei_titani',
    label: 'Crepuscolo dei Titani',
    source_type: 'event_schedule_encounter',
    source_id: 'event_crepuscolo_titani_wave_01',
    encounter_id: 'enc_crepuscolo_titani_w1',
    battle_required: true,
    avatar_required: false,
    guild_required: false,
    enemies: [
      { hero_id: 'alpha_boss_hero_02', role: 'boss', level: 45, stars: 5, power: 30000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  assalto_del_ragnarok: {
    mode_id: 'assalto_del_ragnarok',
    label: 'Assalto del Ragnarök',
    source_type: 'event_schedule_encounter',
    source_id: 'event_assalto_ragnarok_wave_01',
    encounter_id: 'enc_assalto_ragnarok_w1',
    battle_required: true,
    avatar_required: false,
    guild_required: false,
    enemies: [
      { hero_id: 'alpha_boss_hero_01', role: 'boss', level: 50, stars: 5, power: 35000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  guild_war: {
    mode_id: 'guild_war',
    label: 'Guerra tra Gilde',
    source_type: 'guild_defense_team',
    source_id: 'gw_defense_team_design_v1',
    encounter_id: 'enc_guild_war_defense_design',
    battle_required: true,
    avatar_required: true,
    avatar_id: 'guild_war_avatar_base_dev',
    guild_required: true,
    enemies: [
      { hero_id: 'alpha_arena_hero_01', role: 'dps', level: 30, stars: 4, power: 8000 },
      { hero_id: 'alpha_arena_hero_02', role: 'dps', level: 30, stars: 4, power: 8000 },
      { hero_id: 'alpha_arena_hero_03', role: 'healer', level: 30, stars: 4, power: 7500 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  guild_raid: {
    mode_id: 'guild_raid',
    label: 'Raid di Gilda',
    source_type: 'raid_boss_catalog',
    source_id: 'guild_raid_boss_design_v1',
    encounter_id: 'enc_guild_raid_boss_design',
    battle_required: true,
    avatar_required: false,
    guild_required: true,
    enemies: [
      { hero_id: 'alpha_raid_boss_placeholder_01', role: 'boss', level: 55, stars: 5, power: 50000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  server_boss: {
    mode_id: 'server_boss',
    label: 'Boss del Server',
    source_type: 'server_boss_catalog',
    source_id: 'server_boss_weekly_design_v1',
    encounter_id: 'enc_server_boss_weekly_design',
    battle_required: true,
    avatar_required: false,
    guild_required: false,
    enemies: [
      { hero_id: 'alpha_raid_boss_placeholder_01', role: 'boss', level: 60, stars: 5, power: 75000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  faction_boss: {
    mode_id: 'faction_boss',
    label: 'Boss di Fazione',
    source_type: 'faction_boss_catalog',
    source_id: 'faction_boss_design_v1',
    encounter_id: 'enc_faction_boss_design',
    battle_required: true,
    avatar_required: true,
    avatar_id: 'faction_boss_avatar_placeholder_dev',
    guild_required: false,
    enemies: [
      { hero_id: 'alpha_boss_hero_04', role: 'boss', level: 35, stars: 4, power: 15000 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  territory: {
    mode_id: 'territory',
    label: 'Conquista Territori',
    source_type: 'authored_encounter_catalog',
    source_id: 'territory_wave_design_v1',
    encounter_id: 'enc_territory_wave_design',
    battle_required: true,
    avatar_required: true,
    avatar_id: 'player_war_avatar_mini_base_dev',
    guild_required: true,
    enemies: [
      { hero_id: 'tower_minion_a', role: 'dps', level: 25, stars: 3, power: 5000 },
      { hero_id: 'tower_minion_b', role: 'tank', level: 25, stars: 3, power: 5500 },
    ],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  war_avatar_mode: {
    mode_id: 'war_avatar_mode',
    label: 'Modalità War Avatar (layout-only)',
    source_type: 'avatar_layout_only',
    source_id: 'war_avatar_layout_design_v1',
    encounter_id: null,
    battle_required: false,
    avatar_required: true,
    avatar_id: 'player_war_avatar_mini_base_dev',
    guild_required: false,
    enemies: [],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
  event_avatar_mode: {
    mode_id: 'event_avatar_mode',
    label: 'Modalità Event Avatar (layout-only)',
    source_type: 'event_layout_only',
    source_id: 'event_avatar_layout_design_v1',
    encounter_id: null,
    battle_required: false,
    avatar_required: true,
    avatar_id: 'event_avatar_base_dev',
    guild_required: false,
    enemies: [],
    is_random: false,
    runtime_generated: false,
    fallback_random_allowed: false,
  },
};

function UnitCard({ unit }: { unit: EnemyUnit }) {
  const color =
    unit.role === 'boss'
      ? '#FF44AA'
      : unit.role === 'tank'
      ? '#4499FF'
      : unit.role === 'healer'
      ? '#44DD99'
      : '#FF5544';
  return (
    <View style={[s.unitCard, { borderColor: color }]}>
      <View style={[s.unitRole, { backgroundColor: color }]}>
        <Text style={s.unitRoleTxt}>{unit.role.toUpperCase()}</Text>
      </View>
      <Text style={s.unitId} numberOfLines={1}>
        {unit.hero_id}
      </Text>
      <Text style={s.unitMeta}>
        Lv.{unit.level} · ★{unit.stars}
      </Text>
      <Text style={s.unitPower}>PWR {unit.power}</Text>
    </View>
  );
}

export default function LiveModePreEntryLobbyScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{
    mode?: string;
    source_id?: string;
    qa_open?: string;
  }>();
  const modeParam = (params.mode || 'event').toString();
  const mode = (LIVE_ENCOUNTERS[modeParam] ? modeParam : 'event') as keyof typeof LIVE_ENCOUNTERS;
  const enc = LIVE_ENCOUNTERS[mode];
  const qaOpen = params.qa_open === '1';

  const totalPower = useMemo(
    () => enc.enemies.reduce((sum, u) => sum + u.power, 0),
    [enc],
  );

  const startTestBattle = () => {
    // Route to /combat with mode + encounter_id from canonical source.
    // The combat renderer (MD5-locked) accept extra params; unknowns ignored safely.
    const path = `/combat?mode=${encodeURIComponent(
      mode,
    )}&encounter_id=${encodeURIComponent(enc.encounter_id || '')}&source_id=${encodeURIComponent(
      enc.source_id,
    )}&qa_test=1`;
    router.push(path as any);
  };

  const startLayoutFlow = () => {
    // Layout-only mode: nothing to launch in battle; for QA we go back to hub.
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };

  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#150825', '#2A1240']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <View style={s.header}>
            <TouchableOpacity onPress={goBack} style={s.backBtn}>
              <Text style={s.backTxt}>← Indietro</Text>
            </TouchableOpacity>
            <Text style={s.title}>Live Mode Pre-Entry Lobby</Text>
            <Text style={s.subtitle}>{enc.label}</Text>
            <Text style={s.subtitleSmall}>v92 · QA · NO LIVE MUTATION</Text>
          </View>

          {/* QA window status */}
          <View
            style={[
              s.qaWindow,
              { borderColor: qaOpen ? '#FFAA22' : '#666', backgroundColor: qaOpen ? 'rgba(80,40,0,0.5)' : 'rgba(40,40,40,0.5)' },
            ]}
          >
            <Text style={[s.qaWindowTxt, { color: qaOpen ? '#FFD700' : '#AAAAAA' }]}>
              {qaOpen ? 'QA TIME OVERRIDE · FORZATO APERTO' : 'GATE: chiuso (real schedule)'}
            </Text>
            <Text style={s.qaWindowSub}>
              production_enabled=false · qa_override_only=true
            </Text>
          </View>

          {/* Source canonica */}
          <View style={s.source}>
            <Text style={s.sourceTitle}>SOURCE CANONICA · NO RANDOM</Text>
            <View style={s.kvRow}><Text style={s.kvKey}>source_type:</Text><Text style={s.kvVal}>{enc.source_type}</Text></View>
            <View style={s.kvRow}><Text style={s.kvKey}>source_id:</Text><Text style={s.kvVal}>{enc.source_id}</Text></View>
            <View style={s.kvRow}><Text style={s.kvKey}>encounter_id:</Text><Text style={s.kvVal}>{enc.encounter_id || 'N/A (layout only)'}</Text></View>
            <View style={s.kvRow}><Text style={s.kvKey}>is_random:</Text><Text style={[s.kvVal, s.kvFalse]}>false</Text></View>
            <View style={s.kvRow}><Text style={s.kvKey}>runtime_generated:</Text><Text style={[s.kvVal, s.kvFalse]}>false</Text></View>
            <View style={s.kvRow}><Text style={s.kvKey}>fallback_random_allowed:</Text><Text style={[s.kvVal, s.kvFalse]}>false</Text></View>
            {enc.avatar_required && (
              <View style={s.kvRow}>
                <Text style={s.kvKey}>avatar (placeholder dev):</Text>
                <Text style={[s.kvVal, s.kvWarn]}>{enc.avatar_id}</Text>
              </View>
            )}
            {enc.guild_required && (
              <View style={s.kvRow}>
                <Text style={s.kvKey}>guild_required:</Text>
                <Text style={[s.kvVal, s.kvWarn]}>YES (QA bypass)</Text>
              </View>
            )}
          </View>

          {/* Enemy team */}
          {enc.battle_required ? (
            <View style={s.section}>
              <View style={s.sectionHeader}>
                <Text style={s.sectionTitle}>Avversario (deterministico)</Text>
                <Text style={s.sectionPower}>PWR totale: {totalPower}</Text>
              </View>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={s.unitRow}>
                  {enc.enemies.map((u, i) => (
                    <UnitCard key={`enemy-${i}`} unit={u} />
                  ))}
                </View>
              </ScrollView>
            </View>
          ) : (
            <View style={s.layoutOnlyBox}>
              <Text style={s.layoutOnlyTitle}>LAYOUT-ONLY MODE</Text>
              <Text style={s.layoutOnlyTxt}>
                Questa modalità non ha encounter battle. Il test serve a validare
                layout/posizionamento/avatar selection con il placeholder dev{' '}
                <Text style={s.layoutOnlyBold}>{enc.avatar_id}</Text>.
              </Text>
            </View>
          )}

          {/* Disabled live flags */}
          <View style={s.flagsBox}>
            <Text style={s.flagsTxt}>NO LIVE REWARD</Text>
            <Text style={s.flagsTxt}>NO RANKING APPLIED</Text>
            <Text style={s.flagsTxt}>NO CURRENCY</Text>
            <Text style={s.flagsTxt}>NO GUILD SCORE</Text>
            <Text style={s.flagsTxt}>NO MMR</Text>
            <Text style={s.flagsTxt}>NO PROGRESS</Text>
          </View>

          {/* Actions */}
          <View style={s.actions}>
            {enc.battle_required ? (
              <TouchableOpacity
                style={[s.actionBtn, s.actionStart, !qaOpen && enc.battle_required && s.actionDisabled]}
                onPress={startTestBattle}
                disabled={!qaOpen && enc.battle_required}
                activeOpacity={0.85}
              >
                <Text style={s.actionTxt}>▶ Avvia Test Battle</Text>
              </TouchableOpacity>
            ) : (
              <TouchableOpacity
                style={[s.actionBtn, s.actionLayout]}
                onPress={startLayoutFlow}
                activeOpacity={0.85}
              >
                <Text style={s.actionTxt}>👁 Avvia Test Flow (Layout)</Text>
              </TouchableOpacity>
            )}
          </View>

          <View style={s.safetyFooter}>
            <Text style={s.safetyTxt}>
              v92 · db_writes=0 · reward_live=false · ranking_live=false ·
              event_currency_live=false · guild_score_mutation=0 ·
              random_opponents_allowed=false
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#150825' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  header: { marginBottom: 12 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#AA88FF', fontSize: 14 },
  title: { color: '#FFD700', fontSize: 20, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#FFFFFF', fontSize: 14, fontWeight: '600', textAlign: 'center', marginTop: 4 },
  subtitleSmall: { color: '#AABBDD', fontSize: 10, textAlign: 'center', marginTop: 2 },

  qaWindow: { borderWidth: 1, borderRadius: 6, padding: 10, marginBottom: 12 },
  qaWindowTxt: { fontSize: 12, fontWeight: '700' },
  qaWindowSub: { color: '#AABBDD', fontSize: 10, marginTop: 2 },

  source: {
    backgroundColor: 'rgba(0,40,80,0.6)',
    borderColor: '#44DDFF',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  sourceTitle: { color: '#44DDFF', fontSize: 11, fontWeight: '700', marginBottom: 6, letterSpacing: 1 },
  kvRow: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 1 },
  kvKey: { color: '#AABBDD', fontSize: 10 },
  kvVal: { color: '#FFFFFF', fontSize: 10, flex: 1, textAlign: 'right' },
  kvFalse: { color: '#FF6644' },
  kvWarn: { color: '#FFAA44' },

  section: { marginBottom: 12 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  sectionTitle: { color: '#FFD700', fontSize: 13, fontWeight: '700' },
  sectionPower: { color: '#AABBDD', fontSize: 11 },
  unitRow: { flexDirection: 'row', gap: 8 },

  unitCard: {
    width: 100,
    backgroundColor: 'rgba(20,15,40,0.7)',
    borderWidth: 2,
    borderRadius: 8,
    padding: 8,
    alignItems: 'center',
  },
  unitRole: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, marginBottom: 4 },
  unitRoleTxt: { color: '#000', fontSize: 9, fontWeight: '800' },
  unitId: { color: '#FFF', fontSize: 10, fontWeight: '600', textAlign: 'center', marginBottom: 4 },
  unitMeta: { color: '#AABBDD', fontSize: 10 },
  unitPower: { color: '#FFD700', fontSize: 11, fontWeight: '700', marginTop: 2 },

  layoutOnlyBox: {
    backgroundColor: 'rgba(40,20,60,0.6)',
    borderColor: '#AA88FF',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  layoutOnlyTitle: { color: '#AA88FF', fontSize: 12, fontWeight: '800', marginBottom: 6 },
  layoutOnlyTxt: { color: '#DDCCFF', fontSize: 12, lineHeight: 18 },
  layoutOnlyBold: { fontWeight: '700' },

  flagsBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  flagsTxt: {
    color: '#FFFFFF',
    backgroundColor: '#774444',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 3,
    fontSize: 9,
    fontWeight: '700',
  },

  actions: { marginBottom: 12 },
  actionBtn: { paddingVertical: 14, borderRadius: 10, alignItems: 'center', minHeight: 48 },
  actionStart: { backgroundColor: '#22BB66' },
  actionLayout: { backgroundColor: '#6644AA' },
  actionDisabled: { backgroundColor: '#444444', opacity: 0.5 },
  actionTxt: { color: '#FFFFFF', fontSize: 15, fontWeight: '800' },

  safetyFooter: { marginTop: 8, padding: 8, borderRadius: 6, backgroundColor: 'rgba(0,0,0,0.3)' },
  safetyTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});

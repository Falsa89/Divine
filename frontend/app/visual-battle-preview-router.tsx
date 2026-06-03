/**
 * frontend/app/visual-battle-preview-router.tsx
 *
 * v55 MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW — Track B
 * Generic Visual Battle Preview Router Shell (DEEPLINK-ONLY).
 *
 * NO home menu wiring. NO backend fetch. NO claim button. NO mutation.
 * NO battle_engine. NO /api/battle/simulate. NO /api/story/battle.
 * Result NON-AUTHORITATIVE. Reward NOT granted.
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  mode?: string;
  source_route?: string;
  track_id?: string;
  stage_id?: string;
  chapter_id?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
  enemy_family_preview?: string;
  // v57 boss preview extension (deeplink-only, no backend, no claim)
  boss_family_id?: string;
  boss_display_name?: string;
  boss_phase_preview?: string;
  // v58 MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH — deeplink-only, no backend, no claim
  // story
  node_id?: string;
  encounter_id?: string;
  encounter_display_name?: string;
  faction_hint?: string;
  background_hint?: string;
  music_hint?: string;
  tutorial_hint?: string;
  // tower
  tower_id?: string;
  floor_id?: string;
  floor_number_preview?: string;
  modifier_hint_preview?: string;
  // event
  event_id?: string;
  event_node_id?: string;
  event_display_name?: string;
  event_theme_hint?: string;
  bonus_rule_hint_preview?: string;
  // arena
  arena_bracket_preview?: string;
  opponent_name_preview?: string;
  opponent_power_preview?: string;
  ruleset_hint_preview?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

export default function VisualBattlePreviewRouterScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const mode = asString(raw.mode) || 'unknown';
  const sourceRoute = asString(raw.source_route);
  const trackId = asString(raw.track_id);
  const stageId = asString(raw.stage_id);
  const chapterId = asString(raw.chapter_id);
  const seed = asString(raw.battle_seed_preview);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);
  const enemyFamily = asString(raw.enemy_family_preview);

  const onBack = () => {
    try {
      router.back();
    } catch {
      // noop fallback
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Visual Battle Preview Router</Text>
          <Text style={styles.subtitle}>v55+v58 · deeplink-only · shell preview multi-mode (story/tower/event/arena)</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Parametri ricevuti</Text>
          <Text style={styles.line}>Modalità: {mode}</Text>
          {sourceRoute ? <Text style={styles.line}>Source route: {sourceRoute}</Text> : null}
          {trackId ? <Text style={styles.line}>Track ID: {trackId}</Text> : null}
          {stageId ? <Text style={styles.line}>Stage ID: {stageId}</Text> : null}
          {chapterId ? <Text style={styles.line}>Chapter ID: {chapterId}</Text> : null}
          {seed ? <Text style={styles.line}>Seed preview: {seed}</Text> : null}
          {teamPower ? <Text style={styles.line}>Potere squadra: {teamPower}</Text> : null}
          {recommendedPower ? (
            <Text style={styles.line}>Potere consigliato: {recommendedPower}</Text>
          ) : null}
          {enemyFamily ? (
            <Text style={styles.line}>Famiglia nemica (preview): {enemyFamily}</Text>
          ) : null}
          {!sourceRoute && !trackId && !stageId && !chapterId && !seed ? (
            <Text style={styles.helper}>
              Nessun parametro fornito. La schermata non crasha: usa il deeplink con i query
              param previsti dal contratto v1.
            </Text>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Placeholder griglia 3x3</Text>
          <View style={styles.grid}>
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <View key={i} style={styles.gridCell}>
                <Text style={styles.gridCellText}>{i + 1}</Text>
              </View>
            ))}
          </View>
          <Text style={styles.helper}>
            Layout placeholder: nessun asset reale, nessuna chiamata backend.
          </Text>
        </View>

        {mode === 'training' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Training Dummy Seed Details</Text>
            <Text style={styles.line}>Stato: local_dummy_seed_wired_v56</Text>
            <Text style={styles.line}>Seed: {seed || 'training-alpha-v56'}</Text>
            <Text style={styles.line}>Pattern: timeline deterministica 5-7 step</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Materiale Raid e altre modalità
              restano invariate.
            </Text>
          </View>
        ) : null}

        {mode === 'boss' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Boss Preview Details</Text>
            <Text style={styles.line}>
              Stato:{' '}
              {seed === 'boss-alpha-v59' ||
              (asString(raw.source_route) || '').toLowerCase().includes('boss')
                ? 'local_dummy_seed_wired_v59'
                : 'preview_shell_v57'}
            </Text>
            <Text style={styles.line}>
              Boss family: {asString(raw.boss_family_id) || 'training_boss_preview'}
            </Text>
            <Text style={styles.line}>
              Display name: {asString(raw.boss_display_name) || 'Boss Preview'}
            </Text>
            <Text style={styles.line}>
              Phase preview: {asString(raw.boss_phase_preview) || 'phase_1'}
            </Text>
            <Text style={styles.line}>Seed: {seed || 'boss-alpha-v59'}</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Material Raid e Training restano
              invariate.
            </Text>
          </View>
        ) : null}

        {mode === 'story' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Story Preview Details</Text>
            <Text style={styles.line}>Stato: preview_shell_v58</Text>
            <Text style={styles.line}>
              Chapter ID: {chapterId || 'chapter_preview_1'}
            </Text>
            <Text style={styles.line}>
              Node ID: {asString(raw.node_id) || 'node_preview_1'}
            </Text>
            <Text style={styles.line}>
              Encounter ID: {asString(raw.encounter_id) || 'story_encounter_preview'}
            </Text>
            <Text style={styles.line}>
              Display name:{' '}
              {asString(raw.encounter_display_name) || 'Story Encounter Preview'}
            </Text>
            <Text style={styles.line}>
              Faction hint: {asString(raw.faction_hint) || 'neutral_preview'}
            </Text>
            <Text style={styles.line}>
              Enemy family: {enemyFamily || 'story_training_enemy'}
            </Text>
            <Text style={styles.line}>
              Background hint: {asString(raw.background_hint) || 'story_chapter1_bg'}
            </Text>
            <Text style={styles.line}>
              Music hint: {asString(raw.music_hint) || 'story_chapter1_theme'}
            </Text>
            <Text style={styles.line}>
              Tutorial hint:{' '}
              {asString(raw.tutorial_hint) || 'first_encounter_tutorial'}
            </Text>
            <Text style={styles.line}>Seed: {seed || 'story-alpha-v58'}</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Material Raid, Training e Boss restano
              invariate. story.tsx, combat.tsx, /api/story/battle e
              /api/battle/simulate non vengono toccati.
            </Text>
          </View>
        ) : null}

        {mode === 'tower' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Tower Preview Details</Text>
            <Text style={styles.line}>
              Stato:{' '}
              {seed === 'tower-alpha-v59' ||
              (asString(raw.source_route) || '').toLowerCase().includes('tower')
                ? 'local_dummy_seed_wired_v59'
                : 'preview_shell_v58'}
            </Text>
            <Text style={styles.line}>
              Tower ID: {asString(raw.tower_id) || 'tower_preview_1'}
            </Text>
            <Text style={styles.line}>
              Floor ID: {asString(raw.floor_id) || 'floor_preview_1'}
            </Text>
            <Text style={styles.line}>
              Floor number: {asString(raw.floor_number_preview) || '1'}
            </Text>
            <Text style={styles.line}>
              Display name:{' '}
              {asString(raw.encounter_display_name) || 'Tower Floor Preview'}
            </Text>
            <Text style={styles.line}>
              Enemy family: {enemyFamily || 'tower_guardian_preview'}
            </Text>
            <Text style={styles.line}>
              Modifier hint:{' '}
              {asString(raw.modifier_hint_preview) || 'attack_buff_low'}
            </Text>
            <Text style={styles.line}>
              Background hint: {asString(raw.background_hint) || 'tower_f1_bg'}
            </Text>
            <Text style={styles.line}>
              Music hint: {asString(raw.music_hint) || 'tower_theme'}
            </Text>
            <Text style={styles.line}>Seed: {seed || 'tower-alpha-v58'}</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Material Raid, Training e Boss restano
              invariate.
            </Text>
          </View>
        ) : null}

        {mode === 'event' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Event Preview Details</Text>
            <Text style={styles.line}>Stato: preview_shell_v58</Text>
            <Text style={styles.line}>
              Event ID: {asString(raw.event_id) || 'event_preview_1'}
            </Text>
            <Text style={styles.line}>
              Event node ID:{' '}
              {asString(raw.event_node_id) || 'event_node_preview_1'}
            </Text>
            <Text style={styles.line}>
              Display name:{' '}
              {asString(raw.event_display_name) || 'Event Battle Preview'}
            </Text>
            <Text style={styles.line}>
              Theme hint:{' '}
              {asString(raw.event_theme_hint) || 'limited_time_preview'}
            </Text>
            <Text style={styles.line}>
              Enemy family: {enemyFamily || 'event_enemy_preview'}
            </Text>
            <Text style={styles.line}>
              Bonus rule hint:{' '}
              {asString(raw.bonus_rule_hint_preview) || 'bonus_drop_preview'}
            </Text>
            <Text style={styles.line}>
              Background hint: {asString(raw.background_hint) || 'event_bg'}
            </Text>
            <Text style={styles.line}>
              Music hint: {asString(raw.music_hint) || 'event_theme'}
            </Text>
            <Text style={styles.line}>Seed: {seed || 'event-alpha-v58'}</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Material Raid, Training e Boss restano
              invariate.
            </Text>
          </View>
        ) : null}

        {mode === 'arena' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Arena Preview Details</Text>
            <Text style={styles.line}>Stato: preview_shell_v58</Text>
            <Text style={styles.line}>
              Bracket:{' '}
              {asString(raw.arena_bracket_preview) || 'bronze_preview'}
            </Text>
            <Text style={styles.line}>
              Opponent name:{' '}
              {asString(raw.opponent_name_preview) || 'Training Rival Preview'}
            </Text>
            <Text style={styles.line}>
              Opponent power:{' '}
              {asString(raw.opponent_power_preview) || '45000'}
            </Text>
            <Text style={styles.line}>
              Enemy family: {enemyFamily || 'arena_rival_preview'}
            </Text>
            <Text style={styles.line}>
              Ruleset hint:{' '}
              {asString(raw.ruleset_hint_preview) || 'standard_ruleset_preview'}
            </Text>
            <Text style={styles.line}>
              Background hint: {asString(raw.background_hint) || 'arena_bg'}
            </Text>
            <Text style={styles.line}>
              Music hint: {asString(raw.music_hint) || 'arena_theme'}
            </Text>
            <Text style={styles.line}>Seed: {seed || 'arena-alpha-v58'}</Text>
            <Text style={styles.helper}>
              Disclaimer: nessuna chiamata backend, nessuna chiamata battle_engine,
              nessun reward verrà assegnato. Material Raid, Training e Boss restano
              invariate.
            </Text>
          </View>
        ) : null}

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>reward_grant_enabled = false</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>home_menu_mandatory_routing = false</Text>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
          <Text style={styles.primaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v55 MEGA_RELEASE_ACCELERATION_4 · deeplink-only · no claim · preview shell
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0c0f14' },
  scrollContent: { padding: 16, paddingBottom: 48 },
  headerCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  warningBox: {
    backgroundColor: '#3a2a14',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#a07020',
  },
  warningText: { color: '#e8c884', fontSize: 12 },
  card: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 8 },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  gridCell: {
    width: '31%',
    aspectRatio: 1,
    backgroundColor: '#1a212b',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2a3340',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  gridCellText: { color: '#5a6473', fontSize: 16 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
    marginTop: 4,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2a3340',
  },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 4,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

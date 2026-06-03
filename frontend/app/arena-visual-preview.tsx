/**
 * frontend/app/arena-visual-preview.tsx
 *
 * v58 MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH — Track B (mode: arena)
 * v60 MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH — Track D
 *      Promotion: preview_shell_v58 -> local_dummy_seed_wired_v60
 *
 * Deeplink-only + LOCAL DETERMINISTIC timeline. NO backend. NO battle_engine.
 * NO claim. NO reward. NO mutation. NO Reanimated. NO import from
 * frontend/app/story.tsx or frontend/app/combat.tsx.
 *
 * v58 backward-compat seed: arena-alpha-v58 — superseded by arena-alpha-v60.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  arena_bracket_preview?: string;
  opponent_name_preview?: string;
  opponent_power_preview?: string;
  enemy_family_preview?: string;
  ruleset_hint_preview?: string;
  background_hint?: string;
  music_hint?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

const DEFAULT_SEED = 'arena-alpha-v60';
const DEFAULTS: Record<string, string> = {
  'arena_bracket_preview': 'bronze_preview',
  'opponent_name_preview': 'Training Rival Preview',
  'opponent_power_preview': '45000',
  'battle_seed_preview': 'arena-alpha-v60',
  'enemy_family_preview': 'arena_rival_preview',
  'ruleset_hint_preview': 'standard_ruleset_preview',
  'background_hint': 'arena_bg',
  'music_hint': 'arena_theme',
};

type ActorSide = 'team' | 'enemy';
type TimelineStep = {
  step_index: number;
  actor_side: ActorSide;
  actor_label: string;
  action_key: string;
  target_label: string;
  floating_text_preview: string;
  hp_delta_preview: number;
  pose_hint: string;
  vfx_hint: string;
  duration_ms: number;
  arena_ruleset_hint_optional?: string;
  bracket_hint_optional?: string;
};

/** Deterministic 6-step arena timeline from seed. Pure function. No randomness. */
function buildArenaTimeline(seed: string): TimelineStep[] {
  void seed;
  return [
    { step_index: 0, actor_side: 'team', actor_label: 'Eroe A', action_key: 'arena_open',
      target_label: 'arena_rival', floating_text_preview: '-135', hp_delta_preview: -135,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
    { step_index: 1, actor_side: 'enemy', actor_label: 'arena_rival', action_key: 'rival_strike',
      target_label: 'Eroe A', floating_text_preview: '-100', hp_delta_preview: -100,
      pose_hint: 'hit', vfx_hint: 'impact', duration_ms: 650,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
    { step_index: 2, actor_side: 'team', actor_label: 'Eroe B', action_key: 'arena_skill',
      target_label: 'arena_rival', floating_text_preview: '-205', hp_delta_preview: -205,
      pose_hint: 'cast', vfx_hint: 'duel_blast', duration_ms: 800,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
    { step_index: 3, actor_side: 'enemy', actor_label: 'arena_rival', action_key: 'rival_taunt',
      target_label: 'team', floating_text_preview: 'TAUNT', hp_delta_preview: 0,
      pose_hint: 'taunt', vfx_hint: 'aura_silver', duration_ms: 700,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
    { step_index: 4, actor_side: 'team', actor_label: 'Eroe A', action_key: 'arena_followup',
      target_label: 'arena_rival', floating_text_preview: '-170', hp_delta_preview: -170,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
    { step_index: 5, actor_side: 'enemy', actor_label: 'arena_rival', action_key: 'rival_finisher',
      target_label: 'team', floating_text_preview: '-115', hp_delta_preview: -115,
      pose_hint: 'heavy', vfx_hint: 'shockwave', duration_ms: 750,
      arena_ruleset_hint_optional: 'standard_ruleset_preview', bracket_hint_optional: 'bronze_preview' },
  ];
}

export default function ArenaVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();
  const [arena_bracket_preview, setArenaBracketPreview] = useState<string>(asString(raw.arena_bracket_preview) || DEFAULTS['arena_bracket_preview']);
  const [opponent_name_preview, setOpponentNamePreview] = useState<string>(asString(raw.opponent_name_preview) || DEFAULTS['opponent_name_preview']);
  const [opponent_power_preview, setOpponentPowerPreview] = useState<string>(asString(raw.opponent_power_preview) || DEFAULTS['opponent_power_preview']);
  const [enemy_family_preview, setEnemyFamilyPreview] = useState<string>(asString(raw.enemy_family_preview) || DEFAULTS['enemy_family_preview']);
  const [ruleset_hint_preview, setRulesetHintPreview] = useState<string>(asString(raw.ruleset_hint_preview) || DEFAULTS['ruleset_hint_preview']);
  const [background_hint, setBackgroundHint] = useState<string>(asString(raw.background_hint) || DEFAULTS['background_hint']);
  const [music_hint, setMusicHint] = useState<string>(asString(raw.music_hint) || DEFAULTS['music_hint']);
  const [seed, setSeed] = useState<string>(asString(raw.battle_seed_preview) || DEFAULT_SEED);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  // v60 local timeline
  const timeline = buildArenaTimeline(seed);
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const clearTimer = () => { if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null; } };
  useEffect(() => {
    if (!isPlaying) { clearTimer(); return; }
    if (stepIndex >= timeline.length - 1) { setIsPlaying(false); return; }
    timerRef.current = setTimeout(() => {
      setStepIndex((s) => Math.min(s + 1, timeline.length - 1));
    }, timeline[stepIndex].duration_ms);
    return () => clearTimer();
  }, [isPlaying, stepIndex, timeline]);
  useEffect(() => () => clearTimer(), []);
  const currentStep = timeline[Math.min(stepIndex, timeline.length - 1)];

  const onResetPreview = () => {
    setArenaBracketPreview(DEFAULTS['arena_bracket_preview'] || '');
    setOpponentNamePreview(DEFAULTS['opponent_name_preview'] || '');
    setOpponentPowerPreview(DEFAULTS['opponent_power_preview'] || '');
    setEnemyFamilyPreview(DEFAULTS['enemy_family_preview'] || '');
    setRulesetHintPreview(DEFAULTS['ruleset_hint_preview'] || '');
    setBackgroundHint(DEFAULTS['background_hint'] || '');
    setMusicHint(DEFAULTS['music_hint'] || '');
    setSeed(DEFAULT_SEED);
    setStepIndex(0);
    setIsPlaying(false);
    clearTimer();
  };

  const onStepNext = () => setStepIndex((s) => Math.min(s + 1, timeline.length - 1));
  const onTogglePlay = () => {
    if (stepIndex >= timeline.length - 1) setStepIndex(0);
    setIsPlaying((p) => !p);
  };

  const openRouter = () => {
    const url = `/visual-battle-preview-router?mode=arena&source_route=arena_visual_preview&battle_seed_preview=${encodeURIComponent(seed)}`;
    try { router.push(url); } catch { /* noop */ }
  };

  const onBack = () => { try { router.back(); } catch { /* noop */ } };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Arena Visual Preview</Text>
          <Text style={styles.subtitle}>v58+v60 · local timeline · deeplink-only · 5-7 step deterministica</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.modeCard}>
          <Text style={styles.sectionTitle}>Arena Visual Preview · Mode Card</Text>
          <Text style={styles.line}>arena_bracket_preview: {arena_bracket_preview}</Text>
          <Text style={styles.line}>opponent_name_preview: {opponent_name_preview}</Text>
          <Text style={styles.line}>opponent_power_preview: {opponent_power_preview}</Text>
          <Text style={styles.line}>enemy_family_preview: {enemy_family_preview}</Text>
          <Text style={styles.line}>ruleset_hint_preview: {ruleset_hint_preview}</Text>
          <Text style={styles.line}>background_hint: {background_hint}</Text>
          <Text style={styles.line}>music_hint: {music_hint}</Text>
          <Text style={styles.line}>Seed: {seed}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Potere</Text>
          <Text style={styles.line}>Potere squadra: {teamPower || '—'}</Text>
          <Text style={styles.line}>Potere consigliato: {recommendedPower || '—'}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Timeline locale (step {stepIndex + 1}/{timeline.length})
          </Text>
          <Text style={styles.line}>Azione: {currentStep.action_key}</Text>
          <Text style={styles.line}>
            Attore: {currentStep.actor_label} ({currentStep.actor_side})
          </Text>
          <Text style={styles.line}>Target: {currentStep.target_label}</Text>
          <Text style={styles.line}>HP delta preview: {currentStep.hp_delta_preview}</Text>
          <Text style={styles.line}>Floating text: {currentStep.floating_text_preview}</Text>
          <Text style={styles.line}>
            Ruleset hint: {currentStep.arena_ruleset_hint_optional || ruleset_hint_preview}
          </Text>
          <Text style={styles.line}>
            Bracket hint: {currentStep.bracket_hint_optional || arena_bracket_preview}
          </Text>
          <Text style={styles.line}>
            VFX/Pose: {currentStep.vfx_hint} / {currentStep.pose_hint}
          </Text>
          <Text style={styles.line}>Durata step: {currentStep.duration_ms}ms · seed: {seed}</Text>

          <View style={styles.rowButtons}>
            <TouchableOpacity style={styles.smallBtn} onPress={onStepNext}>
              <Text style={styles.smallBtnText}>Step succ.</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.smallBtn} onPress={onTogglePlay}>
              <Text style={styles.smallBtnText}>{isPlaying ? 'Pausa' : 'Play'}</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>backend_used = false</Text>
          <Text style={styles.guardLine}>runtime_used = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={openRouter}>
          <Text style={styles.primaryBtnText}>Apri Visual Battle Preview Router</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onResetPreview}>
          <Text style={styles.secondaryBtnText}>Reset preview</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onBack}>
          <Text style={styles.secondaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>v58+v60 · arena local_dummy_seed_wired_v60 · no claim · deeplink-only</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0c0f14' },
  scrollContent: { padding: 16, paddingBottom: 48 },
  headerCard: { backgroundColor: '#141a22', borderRadius: 12, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: '#222b36' },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  warningBox: { backgroundColor: '#3a2a14', borderRadius: 8, padding: 12, marginTop: 12, borderWidth: 1, borderColor: '#a07020' },
  warningText: { color: '#e8c884', fontSize: 12 },
  modeCard: { backgroundColor: '#1a212b', borderRadius: 12, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: '#3b2a40' },
  card: { backgroundColor: '#141a22', borderRadius: 12, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: '#222b36' },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  guardsBox: { backgroundColor: '#1a212b', borderRadius: 8, padding: 10, marginBottom: 12, borderWidth: 1, borderColor: '#2a3340' },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  primaryBtn: { backgroundColor: '#3b6db5', paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginTop: 4, minHeight: 48 },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  secondaryBtn: { backgroundColor: '#222b36', paddingVertical: 12, borderRadius: 10, alignItems: 'center', marginTop: 10, minHeight: 44 },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  rowButtons: { flexDirection: 'row', marginTop: 10, gap: 8 },
  smallBtn: { flex: 1, backgroundColor: '#2a3340', paddingVertical: 10, borderRadius: 8, alignItems: 'center', minHeight: 44 },
  smallBtnText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

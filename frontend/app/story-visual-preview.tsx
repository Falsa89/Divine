/**
 * frontend/app/story-visual-preview.tsx
 *
 * v58 MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH — Track B (mode: story)
 * v61 MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE — Track A+B
 *      Promotion: preview_shell_v58 -> local_dummy_seed_wired_v61
 *
 * Deeplink-only + LOCAL DETERMINISTIC timeline. NO backend. NO battle_engine.
 * NO claim. NO reward. NO mutation. NO Reanimated. NO import from
 * frontend/app/story.tsx or frontend/app/combat.tsx.
 *
 * v58 backward-compat seed: story-alpha-v58 — superseded by story-alpha-v61.
 * story_runtime_used=false, story_tsx_changed=false, api_story_battle_changed=false.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  chapter_id?: string;
  node_id?: string;
  encounter_id?: string;
  encounter_display_name?: string;
  faction_hint?: string;
  enemy_family_preview?: string;
  background_hint?: string;
  music_hint?: string;
  tutorial_hint?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

const DEFAULT_SEED = 'story-alpha-v61';
const DEFAULTS: Record<string, string> = {
  'chapter_id': 'chapter_preview_1',
  'node_id': 'node_preview_1',
  'encounter_id': 'story_encounter_preview',
  'encounter_display_name': 'Story Encounter Preview',
  'battle_seed_preview': 'story-alpha-v61',
  'enemy_family_preview': 'story_training_enemy',
  'faction_hint': 'neutral_preview',
  'background_hint': 'story_chapter1_bg',
  'music_hint': 'story_chapter1_theme',
  'tutorial_hint': 'first_encounter_tutorial',
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
  story_tutorial_hint_optional?: string;
  story_faction_hint_optional?: string;
  chapter_node_hint_optional?: string;
};

/** Deterministic 6-step story timeline from seed. Pure function. No randomness. */
function buildStoryTimeline(seed: string): TimelineStep[] {
  void seed;
  return [
    { step_index: 0, actor_side: 'team', actor_label: 'Eroe A', action_key: 'story_open_attack',
      target_label: 'story_enemy', floating_text_preview: '-125', hp_delta_preview: -125,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600,
      story_tutorial_hint_optional: 'first_encounter_tutorial',
      story_faction_hint_optional: 'neutral_preview', chapter_node_hint_optional: 'ch1_node1' },
    { step_index: 1, actor_side: 'enemy', actor_label: 'story_enemy', action_key: 'enemy_riposte',
      target_label: 'Eroe A', floating_text_preview: '-85', hp_delta_preview: -85,
      pose_hint: 'hit', vfx_hint: 'impact', duration_ms: 650,
      chapter_node_hint_optional: 'ch1_node1' },
    { step_index: 2, actor_side: 'team', actor_label: 'Eroe B', action_key: 'story_skill',
      target_label: 'story_enemy', floating_text_preview: '-195', hp_delta_preview: -195,
      pose_hint: 'cast', vfx_hint: 'arcane_glow', duration_ms: 800,
      story_tutorial_hint_optional: 'skill_introduction_tutorial' },
    { step_index: 3, actor_side: 'enemy', actor_label: 'story_enemy', action_key: 'enemy_defend',
      target_label: 'self', floating_text_preview: 'DEFEND', hp_delta_preview: 0,
      pose_hint: 'guard', vfx_hint: 'shield_glow', duration_ms: 700 },
    { step_index: 4, actor_side: 'team', actor_label: 'Eroe A', action_key: 'story_followup',
      target_label: 'story_enemy', floating_text_preview: '-160', hp_delta_preview: -160,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600 },
    { step_index: 5, actor_side: 'enemy', actor_label: 'story_enemy', action_key: 'enemy_finisher',
      target_label: 'team', floating_text_preview: '-100', hp_delta_preview: -100,
      pose_hint: 'heavy', vfx_hint: 'shockwave', duration_ms: 750,
      chapter_node_hint_optional: 'ch1_node1' },
  ];
}

export default function StoryVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();
  const [chapter_id, setChapterId] = useState<string>(asString(raw.chapter_id) || DEFAULTS['chapter_id']);
  const [node_id, setNodeId] = useState<string>(asString(raw.node_id) || DEFAULTS['node_id']);
  const [encounter_id, setEncounterId] = useState<string>(asString(raw.encounter_id) || DEFAULTS['encounter_id']);
  const [encounter_display_name, setEncounterDisplayName] = useState<string>(asString(raw.encounter_display_name) || DEFAULTS['encounter_display_name']);
  const [faction_hint, setFactionHint] = useState<string>(asString(raw.faction_hint) || DEFAULTS['faction_hint']);
  const [enemy_family_preview, setEnemyFamilyPreview] = useState<string>(asString(raw.enemy_family_preview) || DEFAULTS['enemy_family_preview']);
  const [background_hint, setBackgroundHint] = useState<string>(asString(raw.background_hint) || DEFAULTS['background_hint']);
  const [music_hint, setMusicHint] = useState<string>(asString(raw.music_hint) || DEFAULTS['music_hint']);
  const [tutorial_hint, setTutorialHint] = useState<string>(asString(raw.tutorial_hint) || DEFAULTS['tutorial_hint']);
  const [seed, setSeed] = useState<string>(asString(raw.battle_seed_preview) || DEFAULT_SEED);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  // v61 local timeline state
  const timeline = buildStoryTimeline(seed);
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
    setChapterId(DEFAULTS['chapter_id'] || '');
    setNodeId(DEFAULTS['node_id'] || '');
    setEncounterId(DEFAULTS['encounter_id'] || '');
    setEncounterDisplayName(DEFAULTS['encounter_display_name'] || '');
    setFactionHint(DEFAULTS['faction_hint'] || '');
    setEnemyFamilyPreview(DEFAULTS['enemy_family_preview'] || '');
    setBackgroundHint(DEFAULTS['background_hint'] || '');
    setMusicHint(DEFAULTS['music_hint'] || '');
    setTutorialHint(DEFAULTS['tutorial_hint'] || '');
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
    const url = `/visual-battle-preview-router?mode=story&source_route=story_visual_preview&battle_seed_preview=${encodeURIComponent(seed)}`;
    try { router.push(url); } catch { /* noop */ }
  };

  const onBack = () => { try { router.back(); } catch { /* noop */ } };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Story Visual Preview</Text>
          <Text style={styles.subtitle}>v58+v61 · local timeline · deeplink-only · 5-7 step deterministica</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.modeCard}>
          <Text style={styles.sectionTitle}>Story Visual Preview · Mode Card</Text>
          <Text style={styles.line}>chapter_id: {chapter_id}</Text>
          <Text style={styles.line}>node_id: {node_id}</Text>
          <Text style={styles.line}>encounter_id: {encounter_id}</Text>
          <Text style={styles.line}>encounter_display_name: {encounter_display_name}</Text>
          <Text style={styles.line}>faction_hint: {faction_hint}</Text>
          <Text style={styles.line}>enemy_family_preview: {enemy_family_preview}</Text>
          <Text style={styles.line}>background_hint: {background_hint}</Text>
          <Text style={styles.line}>music_hint: {music_hint}</Text>
          <Text style={styles.line}>tutorial_hint: {tutorial_hint}</Text>
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
            Tutorial hint: {currentStep.story_tutorial_hint_optional || tutorial_hint}
          </Text>
          <Text style={styles.line}>
            Faction hint: {currentStep.story_faction_hint_optional || faction_hint}
          </Text>
          <Text style={styles.line}>
            Chapter/Node: {currentStep.chapter_node_hint_optional || `${chapter_id}/${node_id}`}
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
          <Text style={styles.guardLine}>story_runtime_used = false</Text>
          <Text style={styles.guardLine}>reward_grant_enabled = false</Text>
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
          <Text style={styles.footerText}>v58+v61 · story local_dummy_seed_wired_v61 · no claim · deeplink-only</Text>
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

/**
 * frontend/app/boss-visual-preview.tsx
 *
 * v57 MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE — Track B
 * v59 MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH — Track C
 *      Promotion: preview_shell_v57 -> local_dummy_seed_wired_v59
 *
 * Boss Visual Preview deeplink shell + LOCAL DETERMINISTIC timeline.
 *
 * NO home menu wiring. NO backend. NO battle_engine.
 * NO /api/battle/simulate. NO /api/story/battle.
 * NO claim button. NO reward. NO mutation. NO Reanimated. NO combat.tsx import.
 *
 * v57 default seed: boss-alpha-v57 (kept for backward-compat reference).
 * v59 default seed: boss-alpha-v59 — deterministic 6-step timeline.
 */
import React, { useEffect, useRef, useState } from 'react';
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
  boss_family_id?: string;
  boss_display_name?: string;
  boss_phase_preview?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

const DEFAULT_BOSS_FAMILY = 'training_boss_preview';
const DEFAULT_BOSS_NAME = 'Boss Preview';
const DEFAULT_PHASE = 'phase_1';
// v57 backward-compat reference (previous seed: boss-alpha-v57 — superseded by v59)
const DEFAULT_SEED = 'boss-alpha-v59';

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
  phase_hint_optional?: string;
};

/**
 * Deterministic 6-step boss timeline from seed. Pure function. No randomness.
 * Conforms to local_visual_preview_timeline_schema_v2.
 */
function buildBossTimeline(seed: string): TimelineStep[] {
  // Defensive: behavior stays stable even with unexpected seed.
  void seed;
  return [
    { step_index: 0, actor_side: 'team', actor_label: 'Eroe A', action_key: 'basic_attack',
      target_label: 'boss', floating_text_preview: '-150', hp_delta_preview: -150,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600, phase_hint_optional: 'phase_1' },
    { step_index: 1, actor_side: 'enemy', actor_label: 'boss', action_key: 'boss_smash',
      target_label: 'Eroe A', floating_text_preview: '-110', hp_delta_preview: -110,
      pose_hint: 'heavy', vfx_hint: 'shockwave', duration_ms: 700, phase_hint_optional: 'phase_1' },
    { step_index: 2, actor_side: 'team', actor_label: 'Eroe B', action_key: 'skill_one',
      target_label: 'boss', floating_text_preview: '-220', hp_delta_preview: -220,
      pose_hint: 'cast', vfx_hint: 'fire_ring', duration_ms: 800, phase_hint_optional: 'phase_1' },
    { step_index: 3, actor_side: 'enemy', actor_label: 'boss', action_key: 'boss_enrage_warmup',
      target_label: 'self', floating_text_preview: 'ENRAGE!', hp_delta_preview: 0,
      pose_hint: 'enrage', vfx_hint: 'aura_red', duration_ms: 750, phase_hint_optional: 'phase_2' },
    { step_index: 4, actor_side: 'team', actor_label: 'Eroe A', action_key: 'basic_attack',
      target_label: 'boss', floating_text_preview: '-180', hp_delta_preview: -180,
      pose_hint: 'attack', vfx_hint: 'slash', duration_ms: 600, phase_hint_optional: 'phase_2' },
    { step_index: 5, actor_side: 'enemy', actor_label: 'boss', action_key: 'boss_ultimate',
      target_label: 'team', floating_text_preview: '-200', hp_delta_preview: -200,
      pose_hint: 'ultimate', vfx_hint: 'meteor', duration_ms: 900, phase_hint_optional: 'phase_2' },
  ];
}

// Static hint table — fully local, no backend.
const HINTS: Record<string, { weakness: string; enrage: string; background: string; music: string }> = {
  training_boss_preview: {
    weakness: 'attacchi fisici base',
    enrage: 'enrage_at_50pct_hp',
    background: 'training_arena_bg',
    music: 'training_boss_theme',
  },
};

export default function BossVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const initialFamily = asString(raw.boss_family_id) || DEFAULT_BOSS_FAMILY;
  const initialName = asString(raw.boss_display_name) || DEFAULT_BOSS_NAME;
  const initialPhase = asString(raw.boss_phase_preview) || DEFAULT_PHASE;
  const initialSeed = asString(raw.battle_seed_preview) || DEFAULT_SEED;
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  const [bossFamily, setBossFamily] = useState<string>(initialFamily);
  const [bossName, setBossName] = useState<string>(initialName);
  const [phase, setPhase] = useState<string>(initialPhase);
  const [seed, setSeed] = useState<string>(initialSeed);

  // v59 local timeline state
  const timeline = buildBossTimeline(seed);
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimer = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => {
    if (!isPlaying) {
      clearTimer();
      return;
    }
    if (stepIndex >= timeline.length - 1) {
      setIsPlaying(false);
      return;
    }
    const cur = timeline[stepIndex];
    timerRef.current = setTimeout(() => {
      setStepIndex((s) => Math.min(s + 1, timeline.length - 1));
    }, cur.duration_ms);
    return () => clearTimer();
  }, [isPlaying, stepIndex, timeline]);

  // unmount cleanup
  useEffect(() => () => clearTimer(), []);

  const hints = HINTS[bossFamily] || HINTS[DEFAULT_BOSS_FAMILY];
  const currentStep = timeline[Math.min(stepIndex, timeline.length - 1)];

  const onResetPreview = () => {
    setBossFamily(DEFAULT_BOSS_FAMILY);
    setBossName(DEFAULT_BOSS_NAME);
    setPhase(DEFAULT_PHASE);
    setSeed(DEFAULT_SEED);
    setStepIndex(0);
    setIsPlaying(false);
    clearTimer();
  };

  const onStepNext = () => {
    setStepIndex((s) => Math.min(s + 1, timeline.length - 1));
  };

  const onTogglePlay = () => {
    if (stepIndex >= timeline.length - 1) {
      setStepIndex(0);
    }
    setIsPlaying((p) => !p);
  };

  const openRouter = () => {
    const url = `/visual-battle-preview-router?mode=boss&source_route=boss_visual_preview&boss_family_id=${encodeURIComponent(
      bossFamily,
    )}&boss_display_name=${encodeURIComponent(bossName)}&boss_phase_preview=${encodeURIComponent(
      phase,
    )}&battle_seed_preview=${encodeURIComponent(seed)}`;
    try {
      router.push(url);
    } catch {
      // noop fallback
    }
  };

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
          <Text style={styles.title}>Boss Visual Preview</Text>
          <Text style={styles.subtitle}>
            v57+v59 · local timeline · deeplink-only · 5-7 step deterministica
          </Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale boss non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.bossCard}>
          <Text style={styles.sectionTitle}>Boss Card</Text>
          <Text style={styles.bossName}>{bossName}</Text>
          <Text style={styles.line}>Family: {bossFamily}</Text>
          <Text style={styles.line}>Phase preview: {phase}</Text>
          <Text style={styles.line}>Seed: {seed}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Hint preview</Text>
          <Text style={styles.line}>Weakness hint: {hints.weakness}</Text>
          <Text style={styles.line}>Enrage hint: {hints.enrage}</Text>
          <Text style={styles.helper}>
            Background: {hints.background} · Music: {hints.music}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Potere</Text>
          <Text style={styles.line}>
            Potere squadra: {teamPower || '—'}
          </Text>
          <Text style={styles.line}>
            Potere consigliato: {recommendedPower || '—'}
          </Text>
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
          <Text style={styles.line}>
            HP delta preview: {currentStep.hp_delta_preview}
          </Text>
          <Text style={styles.line}>
            Floating text: {currentStep.floating_text_preview}
          </Text>
          <Text style={styles.line}>
            Phase hint: {currentStep.phase_hint_optional || phase}
          </Text>
          <Text style={styles.line}>
            VFX/Pose: {currentStep.vfx_hint} / {currentStep.pose_hint}
          </Text>
          <Text style={styles.helper}>
            Durata step: {currentStep.duration_ms}ms · seed: {seed}
          </Text>

          <View style={styles.rowButtons}>
            <TouchableOpacity style={styles.smallBtn} onPress={onStepNext}>
              <Text style={styles.smallBtnText}>Step succ.</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.smallBtn} onPress={onTogglePlay}>
              <Text style={styles.smallBtnText}>
                {isPlaying ? 'Pausa' : 'Play'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>backend_used = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>reward_grant_enabled = false</Text>
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
          <Text style={styles.footerText}>
            v57+v59 · boss local_dummy_seed_wired_v59 · no claim · deeplink-only
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
  bossCard: {
    backgroundColor: '#1a212b',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#3b2a40',
  },
  card: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  bossName: { color: '#e8c884', fontSize: 18, fontWeight: '700', marginBottom: 6 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 6 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
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
  secondaryBtn: {
    backgroundColor: '#222b36',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    minHeight: 44,
  },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  rowButtons: { flexDirection: 'row', marginTop: 10, gap: 8 },
  smallBtn: {
    flex: 1,
    backgroundColor: '#2a3340',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 44,
  },
  smallBtnText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

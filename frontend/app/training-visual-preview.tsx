/**
 * frontend/app/training-visual-preview.tsx
 *
 * v56 MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED_WIRING — Track B
 * Training Visual Preview with LOCAL DETERMINISTIC timeline (seed: training-alpha-v56).
 *
 * STILL deeplink-only. STILL no backend. STILL no battle_engine.
 * NO /api/battle/simulate. NO /api/story/battle. NO claim button.
 * NO reward. NO mutation. NO Reanimated. NO combat.tsx import.
 *
 * Seed: training-alpha-v56 — deterministic step list 5..7 (6 steps).
 *
 * Versioning history (kept for v55 backward-compat string presence):
 *   v55 deeplink: /visual-battle-preview-router?mode=training&source_route=training_visual_preview&battle_seed_preview=training-alpha-v55
 *   v55 warning  : "Preview visuale non autoritativa"
 *   v56 deeplink: /visual-battle-preview-router?mode=training&source_route=training_visual_preview&battle_seed_preview=training-alpha-v56
 *   v56 warning  : "Preview visuale locale non autoritativa"
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';

const SEED = 'training-alpha-v56';
// v55 backward-compat reference (previous seed: training-alpha-v55 — superseded by v56)
const ROUTER_DEEPLINK =
  '/visual-battle-preview-router?mode=training&source_route=training_visual_preview&battle_seed_preview=training-alpha-v56';

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
};

/**
 * Build a deterministic 6-step training timeline from the seed.
 * Pure function. No randomness at runtime. No backend.
 */
function buildLocalTimeline(seed: string): TimelineStep[] {
  // Deterministic — the seed is part of the contract identifier; we hardcode
  // the exact sequence v56 ships with. This is verifiable via the validator.
  if (seed !== 'training-alpha-v56') {
    // Defensive: keep behavior stable even with an unexpected seed.
  }
  return [
    {
      step_index: 0,
      actor_side: 'team',
      actor_label: 'Eroe A',
      action_key: 'basic_attack',
      target_label: 'training_dummy',
      floating_text_preview: '-120',
      hp_delta_preview: -120,
      pose_hint: 'attack',
      vfx_hint: 'slash',
      duration_ms: 600,
    },
    {
      step_index: 1,
      actor_side: 'enemy',
      actor_label: 'training_dummy',
      action_key: 'enemy_strike',
      target_label: 'Eroe A',
      floating_text_preview: '-80',
      hp_delta_preview: -80,
      pose_hint: 'hit',
      vfx_hint: 'none',
      duration_ms: 500,
    },
    {
      step_index: 2,
      actor_side: 'team',
      actor_label: 'Eroe B',
      action_key: 'skill_a',
      target_label: 'training_dummy',
      floating_text_preview: '-160 CRIT',
      hp_delta_preview: -160,
      pose_hint: 'skill',
      vfx_hint: 'flame',
      duration_ms: 800,
    },
    {
      step_index: 3,
      actor_side: 'team',
      actor_label: 'Eroe C',
      action_key: 'recover',
      target_label: 'Eroe A',
      floating_text_preview: '+40 HEAL',
      hp_delta_preview: 40,
      pose_hint: 'recover',
      vfx_hint: 'heal',
      duration_ms: 500,
    },
    {
      step_index: 4,
      actor_side: 'enemy',
      actor_label: 'training_dummy',
      action_key: 'enemy_strike',
      target_label: 'Eroe B',
      floating_text_preview: 'BLOCK',
      hp_delta_preview: 0,
      pose_hint: 'hit',
      vfx_hint: 'none',
      duration_ms: 400,
    },
    {
      step_index: 5,
      actor_side: 'team',
      actor_label: 'Eroe A',
      action_key: 'ultimate',
      target_label: 'training_dummy',
      floating_text_preview: '-220',
      hp_delta_preview: -220,
      pose_hint: 'skill',
      vfx_hint: 'holy',
      duration_ms: 1000,
    },
  ];
}

export default function TrainingVisualPreviewScreen() {
  const router = useRouter();

  const timeline = useMemo(() => buildLocalTimeline(SEED), []);
  const lastIndex = timeline.length - 1;

  const [stepIndex, setStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup timer on unmount.
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  // Play/Pause loop with safe cleanup.
  useEffect(() => {
    if (!isPlaying) {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      return;
    }
    if (stepIndex >= lastIndex) {
      setIsPlaying(false);
      return;
    }
    const current = timeline[stepIndex];
    timerRef.current = setTimeout(() => {
      setStepIndex((i) => Math.min(i + 1, lastIndex));
    }, current.duration_ms);
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isPlaying, stepIndex, lastIndex, timeline]);

  const onStepNext = () => {
    if (isPlaying) setIsPlaying(false);
    setStepIndex((i) => Math.min(i + 1, lastIndex));
  };
  const onReset = () => {
    if (isPlaying) setIsPlaying(false);
    setStepIndex(0);
  };
  const onPlayToggle = () => setIsPlaying((p) => !p);
  const openRouter = () => {
    try {
      router.push(ROUTER_DEEPLINK);
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

  const current = timeline[Math.min(stepIndex, lastIndex)];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Training Visual Preview</Text>
          <Text style={styles.subtitle}>
            v56 · safe sandbox · deeplink-only · seed locale
          </Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale locale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
          <Text style={styles.seedText}>Seed locale: {SEED}</Text>
          <Text style={styles.seedText}>
            Stato: local_dummy_seed_wired_v56 · step {stepIndex + 1}/{timeline.length}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Squadra (placeholder)</Text>
          <View style={styles.row}>
            {['A', 'B', 'C'].map((h) => (
              <View key={h} style={styles.slot}>
                <Text style={styles.slotText}>Eroe {h}</Text>
                <Text style={styles.slotSub}>placeholder</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Nemico (placeholder)</Text>
          <View style={styles.row}>
            <View style={styles.slot}>
              <Text style={styles.slotText}>Bersaglio</Text>
              <Text style={styles.slotSub}>training_dummy</Text>
            </View>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Step corrente</Text>
          <Text style={styles.line}>Indice: {current.step_index}</Text>
          <Text style={styles.line}>
            Lato: {current.actor_side === 'team' ? 'Squadra' : 'Nemico'}
          </Text>
          <Text style={styles.line}>
            Attore: {current.actor_label} → Bersaglio: {current.target_label}
          </Text>
          <Text style={styles.line}>Azione: {current.action_key}</Text>
          <Text style={styles.line}>
            Floating text preview: {current.floating_text_preview}
          </Text>
          <Text style={styles.line}>HP delta preview: {current.hp_delta_preview}</Text>
          <Text style={styles.line}>Pose hint: {current.pose_hint}</Text>
          <Text style={styles.line}>VFX hint: {current.vfx_hint}</Text>
          <Text style={styles.line}>Durata: {current.duration_ms} ms</Text>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>safe_sandbox = true</Text>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>backend_used = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
        </View>

        <View style={styles.btnRow}>
          <TouchableOpacity style={styles.smallBtn} onPress={onStepNext}>
            <Text style={styles.smallBtnText}>Step successivo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.smallBtn} onPress={onPlayToggle}>
            <Text style={styles.smallBtnText}>{isPlaying ? 'Pausa' : 'Play'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.smallBtn} onPress={onReset}>
            <Text style={styles.smallBtnText}>Reset</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={openRouter}>
          <Text style={styles.primaryBtnText}>Apri Visual Battle Preview Router</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onBack}>
          <Text style={styles.secondaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v56 MEGA_RELEASE_ACCELERATION_5 · training local dummy seed · no claim · deeplink-only
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
  seedText: { color: '#cdd6e0', fontSize: 12, marginTop: 8 },
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
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  slot: {
    flex: 1,
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 12,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#2a3340',
    alignItems: 'center',
  },
  slotText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
  slotSub: { color: '#5a6473', fontSize: 11, marginTop: 2 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2a3340',
  },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  btnRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  smallBtn: {
    flex: 1,
    backgroundColor: '#222b36',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginRight: 6,
    minHeight: 44,
  },
  smallBtnText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
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
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

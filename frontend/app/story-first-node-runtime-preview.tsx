import React, { useEffect, useMemo, useRef, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';

/**
 * v66 — Story First Node Runtime Preview (DEEPLINK-ONLY).
 *
 * Strictly preview/alpha:
 *  - NO permanent progress
 *  - NO reward grant
 *  - NO DB writes
 *  - NO battle_engine runtime
 *  - NO import from story.tsx / combat.tsx
 *  - NO public menu routing (only reachable via deeplink
 *    `/story-first-node-runtime-preview`)
 *  - NO Reanimated, NO native gestures, NO async storage
 *
 * Renders a local fixture node timeline (6 steps), a result/reward/progress
 * preview, and a runtime payload draft compatible with
 * `runtime_runner_payload_v1_draft` from v62. Pure React Native primitives.
 */

const PACK_TAG = 'PUBLIC_SYNC_TAG_v66_MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA';
const ADAPTER_VERSION = 'story_runtime_adapter_v1';
const NODE_ID = 'story_alpha_node_001';

type Step = {
  id: string;
  label: string;
  kind: 'narration' | 'choice_hint' | 'mock_skill_cast' | 'damage_tick' | 'enemy_phase' | 'result_preview';
  delayMs: number;
};

const LOCAL_TIMELINE: Step[] = [
  { id: 'st1', label: 'Narration — Chapter 1 / Node 1 intro', kind: 'narration', delayMs: 400 },
  { id: 'st2', label: 'Choice hint — guidance only', kind: 'choice_hint', delayMs: 600 },
  { id: 'st3', label: 'Mock skill cast (no real damage)', kind: 'mock_skill_cast', delayMs: 700 },
  { id: 'st4', label: 'Damage tick (visual only)', kind: 'damage_tick', delayMs: 700 },
  { id: 'st5', label: 'Enemy phase (visual only)', kind: 'enemy_phase', delayMs: 700 },
  { id: 'st6', label: 'Result preview (no grant)', kind: 'result_preview', delayMs: 500 },
];

const RUNTIME_PAYLOAD_DRAFT = {
  adapter_version: ADAPTER_VERSION,
  contract_version: 'runtime_runner_payload_v1_draft',
  mode: 'story',
  node_id: NODE_ID,
  authoritative_runtime: false,
  permanent_progress: false,
  reward_grant: false,
  db_writes: 0,
  steps_count: LOCAL_TIMELINE.length,
};

const REWARD_PREVIEW = [
  { item_id: 'mat_alpha_shard', qty: 1, scope: 'preview_only' },
  { item_id: 'mat_alpha_ember', qty: 2, scope: 'preview_only' },
];

export default function StoryFirstNodeRuntimePreviewScreen() {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [playing, setPlaying] = useState<boolean>(false);
  const [completed, setCompleted] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!playing) return;
    if (stepIndex >= LOCAL_TIMELINE.length - 1) {
      setCompleted(true);
      setPlaying(false);
      return;
    }
    const next = LOCAL_TIMELINE[stepIndex + 1];
    timerRef.current = setTimeout(() => {
      setStepIndex((i) => i + 1);
    }, next.delayMs);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [playing, stepIndex]);

  const onPlayPause = () => setPlaying((p) => !p);
  const onReset = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setPlaying(false);
    setCompleted(false);
    setStepIndex(0);
  };

  const adapterSummary = useMemo(
    () =>
      [
        `adapter=${RUNTIME_PAYLOAD_DRAFT.adapter_version}`,
        `node=${RUNTIME_PAYLOAD_DRAFT.node_id}`,
        `mode=${RUNTIME_PAYLOAD_DRAFT.mode}`,
        `authoritative=${RUNTIME_PAYLOAD_DRAFT.authoritative_runtime}`,
        `progress=${RUNTIME_PAYLOAD_DRAFT.permanent_progress}`,
        `reward=${RUNTIME_PAYLOAD_DRAFT.reward_grant}`,
        `db_writes=${RUNTIME_PAYLOAD_DRAFT.db_writes}`,
      ].join(' | '),
    [],
  );

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <Stack.Screen
        options={{
          title: 'Story Runtime Preview (Alpha)',
          headerStyle: { backgroundColor: '#0a0a0a' },
          headerTintColor: '#eaeaea',
        }}
      />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>Story First Node — Runtime Preview (Alpha)</Text>
        <Text style={styles.subtitle}>{PACK_TAG}</Text>
        <Text style={styles.warning}>
          PREVIEW ONLY · NO PERMANENT PROGRESS · NO REWARD GRANT · NO DB WRITES
        </Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Runtime Payload Draft</Text>
          <Text style={styles.mono}>{adapterSummary}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Local Timeline · {LOCAL_TIMELINE.length} steps</Text>
          {LOCAL_TIMELINE.map((s, idx) => {
            const active = idx === stepIndex;
            const done = idx < stepIndex;
            return (
              <View
                key={s.id}
                style={[
                  styles.step,
                  active && styles.stepActive,
                  done && styles.stepDone,
                ]}
              >
                <Text style={styles.stepLabel}>
                  {idx + 1}. [{s.kind}] {s.label}
                </Text>
              </View>
            );
          })}
        </View>

        <View style={styles.controls}>
          <Pressable
            accessibilityRole="button"
            onPress={onPlayPause}
            style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>{playing ? 'Pause' : completed ? 'Replay' : 'Play'}</Text>
          </Pressable>
          <Pressable
            accessibilityRole="button"
            onPress={onReset}
            style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>Reset</Text>
          </Pressable>
        </View>

        {completed ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Result Preview</Text>
            <Text style={styles.mono}>status: result_preview_only</Text>
            <Text style={styles.mono}>reward_grant_executed: false</Text>
            <Text style={styles.mono}>permanent_progress: false</Text>
            <Text style={styles.mono}>db_writes: 0</Text>

            <Text style={styles.sectionTitle}>Reward Preview · scope=preview_only</Text>
            {REWARD_PREVIEW.map((r) => (
              <Text key={r.item_id} style={styles.mono}>
                · {r.item_id} x{r.qty} ({r.scope})
              </Text>
            ))}

            <Text style={styles.sectionTitle}>Progress Preview · transient</Text>
            <Text style={styles.mono}>node_id: {NODE_ID}</Text>
            <Text style={styles.mono}>cleared_in_preview: true</Text>
            <Text style={styles.mono}>persisted: false</Text>
          </View>
        ) : null}

        <Text style={styles.footer}>
          Deeplink-only screen. Not wired to any public menu. Platform: {Platform.OS}
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0a0a0a' },
  scroll: { padding: 16, paddingBottom: 32 },
  title: { color: '#f3f3f3', fontSize: 20, fontWeight: '700', marginBottom: 4 },
  subtitle: { color: '#9a9a9a', fontSize: 11, marginBottom: 8 },
  warning: {
    color: '#ffd166',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 16,
    backgroundColor: '#2a2310',
    padding: 8,
    borderRadius: 6,
  },
  card: {
    backgroundColor: '#141414',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  sectionTitle: {
    color: '#eaeaea',
    fontSize: 14,
    fontWeight: '700',
    marginTop: 8,
    marginBottom: 6,
  },
  mono: { color: '#bcdcff', fontSize: 12, fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace', default: 'monospace' }) },
  step: {
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 6,
    marginBottom: 4,
    backgroundColor: '#1a1a1a',
    borderLeftWidth: 3,
    borderLeftColor: '#333',
  },
  stepActive: { borderLeftColor: '#4cc9f0', backgroundColor: '#0c2030' },
  stepDone: { borderLeftColor: '#52c41a', opacity: 0.7 },
  stepLabel: { color: '#dcdcdc', fontSize: 13 },
  controls: { flexDirection: 'row', gap: 12, marginVertical: 8 },
  btn: {
    flex: 1,
    backgroundColor: '#1f6feb',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  btnSecondary: { backgroundColor: '#333' },
  btnPressed: { opacity: 0.7 },
  btnText: { color: '#fff', fontSize: 14, fontWeight: '700' },
  footer: { color: '#666', fontSize: 11, marginTop: 12, textAlign: 'center' },
});

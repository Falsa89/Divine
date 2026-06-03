import React, { useEffect, useMemo, useRef, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useLocalSearchParams, useRouter } from 'expo-router';

/**
 * v66 + v67 — Story Runtime Preview (DEEPLINK-ONLY).
 *
 * Strict preview/alpha:
 *  - NO permanent progress, NO reward grant, NO DB writes
 *  - NO battle_engine runtime, NO /api calls
 *  - NO import from frontend/app/story.tsx or frontend/app/combat.tsx
 *  - NO public menu routing (deeplink-only)
 *  - NO Reanimated, NO AsyncStorage
 *
 * v67 widens this screen to support 3 alpha nodes via optional
 * query param `node_id` ∈ { story_alpha_node_001, _002, _003 }
 * (fallback: story_alpha_node_001).
 *
 * All text in Italian where user-facing.
 */

const PACK_TAG = 'PUBLIC_SYNC_TAG_v67_MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY';
const ADAPTER_VERSION = 'story_runtime_adapter_v1';

type StepKind = 'narration' | 'choice_hint' | 'mock_skill_cast' | 'damage_tick' | 'enemy_phase' | 'result_preview';
type Step = { id: string; label: string; kind: StepKind; delayMs: number };
type NodeDef = {
  node_id: string;
  chapter_id: string;
  encounter_id: string;
  encounter_display_name: string;
  battle_seed: string;
  enemy_family_preview: string;
  recommended_power_preview: number;
  team_power_preview: number;
  background_hint: string;
  music_hint: string;
  tutorial_hint: string;
  steps: Step[];
};

const NODES: Record<string, NodeDef> = {
  story_alpha_node_001: {
    node_id: 'story_alpha_node_001',
    chapter_id: 'chapter_alpha',
    encounter_id: 'enc_alpha_001',
    encounter_display_name: 'Prologo · Sentiero Silente',
    battle_seed: 'seed_alpha_001',
    enemy_family_preview: 'forest_grunt',
    recommended_power_preview: 1200,
    team_power_preview: 1300,
    background_hint: 'forest_dusk',
    music_hint: 'theme_alpha_intro',
    tutorial_hint: 'Tocca avanti per simulare lo step successivo',
    steps: [
      { id: 'st1', label: 'Narrazione · introduzione del prologo', kind: 'narration', delayMs: 400 },
      { id: 'st2', label: 'Suggerimento di scelta · solo guida', kind: 'choice_hint', delayMs: 600 },
      { id: 'st3', label: 'Lancio abilità simulato', kind: 'mock_skill_cast', delayMs: 700 },
      { id: 'st4', label: 'Tick danno visivo', kind: 'damage_tick', delayMs: 700 },
      { id: 'st5', label: 'Fase nemica visiva', kind: 'enemy_phase', delayMs: 700 },
      { id: 'st6', label: 'Anteprima risultato (no grant)', kind: 'result_preview', delayMs: 500 },
    ],
  },
  story_alpha_node_002: {
    node_id: 'story_alpha_node_002',
    chapter_id: 'chapter_alpha',
    encounter_id: 'enc_alpha_002',
    encounter_display_name: 'Capitolo I · Crepuscolo Spezzato',
    battle_seed: 'seed_alpha_002',
    enemy_family_preview: 'mountain_brigand',
    recommended_power_preview: 1450,
    team_power_preview: 1500,
    background_hint: 'mountain_pass',
    music_hint: 'theme_alpha_tension',
    tutorial_hint: 'I duplicati con lo stesso payload restituiscono il preview esistente',
    steps: [
      { id: 'st1', label: 'Narrazione · valico montano al tramonto', kind: 'narration', delayMs: 400 },
      { id: 'st2', label: 'Suggerimento di scelta · difesa o attacco', kind: 'choice_hint', delayMs: 600 },
      { id: 'st3', label: 'Lancio abilità simulato (AoE preview)', kind: 'mock_skill_cast', delayMs: 700 },
      { id: 'st4', label: 'Tick danno · brigante 1', kind: 'damage_tick', delayMs: 600 },
      { id: 'st5', label: 'Fase nemica · contrattacco visivo', kind: 'enemy_phase', delayMs: 700 },
      { id: 'st6', label: 'Anteprima risultato (no grant)', kind: 'result_preview', delayMs: 500 },
    ],
  },
  story_alpha_node_003: {
    node_id: 'story_alpha_node_003',
    chapter_id: 'chapter_alpha',
    encounter_id: 'enc_alpha_003',
    encounter_display_name: 'Capitolo I · Cripta del Sigillo',
    battle_seed: 'seed_alpha_003',
    enemy_family_preview: 'crypt_warden',
    recommended_power_preview: 1700,
    team_power_preview: 1750,
    background_hint: 'crypt_torchlight',
    music_hint: 'theme_alpha_climax',
    tutorial_hint: 'Replay con payload differente viene rifiutato come duplicate_conflict',
    steps: [
      { id: 'st1', label: 'Narrazione · sigillo antico che pulsa', kind: 'narration', delayMs: 400 },
      { id: 'st2', label: 'Suggerimento di scelta · purificare o forzare', kind: 'choice_hint', delayMs: 600 },
      { id: 'st3', label: 'Lancio abilità simulato (single-target boss)', kind: 'mock_skill_cast', delayMs: 800 },
      { id: 'st4', label: 'Tick danno · custode crepa', kind: 'damage_tick', delayMs: 700 },
      { id: 'st5', label: 'Fase nemica · scudo runico visivo', kind: 'enemy_phase', delayMs: 800 },
      { id: 'st6', label: 'Anteprima risultato (no grant)', kind: 'result_preview', delayMs: 500 },
      { id: 'st7', label: 'Closing narration · sigillo silenziato', kind: 'narration', delayMs: 400 },
    ],
  },
};

const NODE_ORDER = ['story_alpha_node_001', 'story_alpha_node_002', 'story_alpha_node_003'];

export default function StoryFirstNodeRuntimePreviewScreen() {
  const params = useLocalSearchParams<{ node_id?: string }>();
  const router = useRouter();

  const initialId = useMemo(() => {
    const raw = typeof params.node_id === 'string' ? params.node_id : undefined;
    return raw && NODES[raw] ? raw : 'story_alpha_node_001';
  }, [params.node_id]);

  const [nodeId, setNodeId] = useState<string>(initialId);
  const node = NODES[nodeId];
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [playing, setPlaying] = useState<boolean>(false);
  const [completed, setCompleted] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Reset state when node changes.
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setStepIndex(0);
    setPlaying(false);
    setCompleted(false);
  }, [nodeId]);

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current);
  }, []);

  useEffect(() => {
    if (!playing) return;
    if (stepIndex >= node.steps.length - 1) {
      setCompleted(true);
      setPlaying(false);
      return;
    }
    const next = node.steps[stepIndex + 1];
    timerRef.current = setTimeout(() => setStepIndex((i) => i + 1), next.delayMs);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [playing, stepIndex, node]);

  const onPlayPause = () => setPlaying((p) => !p);
  const onStepNext = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setPlaying(false);
    if (stepIndex < node.steps.length - 1) {
      setStepIndex((i) => i + 1);
    } else {
      setCompleted(true);
    }
  };
  const onReset = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setPlaying(false);
    setCompleted(false);
    setStepIndex(0);
  };
  const onPrevNode = () => {
    const i = NODE_ORDER.indexOf(nodeId);
    if (i > 0) setNodeId(NODE_ORDER[i - 1]);
  };
  const onNextNode = () => {
    const i = NODE_ORDER.indexOf(nodeId);
    if (i >= 0 && i < NODE_ORDER.length - 1) setNodeId(NODE_ORDER[i + 1]);
  };
  const onOpenVisualPreview = () => router.push('/visual-battle-preview-router');
  const onBack = () => router.back();

  const payloadDraft = useMemo(() => ({
    adapter_version: ADAPTER_VERSION,
    contract_version: 'runtime_runner_payload_v1_draft',
    mode: 'story',
    node_id: node.node_id,
    chapter_id: node.chapter_id,
    encounter_id: node.encounter_id,
    battle_seed: node.battle_seed,
    not_consumed_by_runtime: true,
    authoritative_runtime: false,
    result_authoritative: false,
    battle_engine_runtime_used: false,
    permanent_progress_enabled: false,
    reward_grant_enabled: false,
    db_writes: 0,
    steps_count: node.steps.length,
  }), [node]);

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
        <Text style={styles.title}>Story Runtime Preview · Alpha (Nodi 1–3)</Text>
        <Text style={styles.subtitle}>{PACK_TAG}</Text>
        <Text style={styles.warning}>
          SOLO ANTEPRIMA · NESSUN PROGRESSO PERMANENTE · NESSUN REWARD · NESSUNA SCRITTURA DB
        </Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Nodo selezionato</Text>
          <Text style={styles.mono}>{node.node_id}</Text>
          <Text style={styles.mono}>{node.encounter_display_name}</Text>
          <Text style={styles.mono}>seed: {node.battle_seed} · enemy: {node.enemy_family_preview}</Text>
          <Text style={styles.mono}>power: rec={node.recommended_power_preview} · team={node.team_power_preview}</Text>
          <Text style={styles.mono}>bg: {node.background_hint} · music: {node.music_hint}</Text>
          <Text style={styles.hint}>Suggerimento: {node.tutorial_hint}</Text>
          <View style={styles.row}>
            <Pressable
              accessibilityRole="button"
              onPress={onPrevNode}
              style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
            >
              <Text style={styles.btnText}>◀ Nodo precedente</Text>
            </Pressable>
            <Pressable
              accessibilityRole="button"
              onPress={onNextNode}
              style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
            >
              <Text style={styles.btnText}>Nodo successivo ▶</Text>
            </Pressable>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Runtime Payload Draft</Text>
          <Text style={styles.mono}>adapter={payloadDraft.adapter_version}</Text>
          <Text style={styles.mono}>contract={payloadDraft.contract_version}</Text>
          <Text style={styles.mono}>mode={payloadDraft.mode} · node={payloadDraft.node_id}</Text>
          <Text style={styles.mono}>chapter={payloadDraft.chapter_id} · encounter={payloadDraft.encounter_id}</Text>
          <Text style={styles.mono}>seed={payloadDraft.battle_seed}</Text>
          <Text style={styles.mono}>not_consumed_by_runtime={String(payloadDraft.not_consumed_by_runtime)}</Text>
          <Text style={styles.mono}>steps_count={payloadDraft.steps_count}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Guardrails</Text>
          <Text style={styles.mono}>result_authoritative=false</Text>
          <Text style={styles.mono}>db_writes=0</Text>
          <Text style={styles.mono}>battle_engine_runtime_used=false</Text>
          <Text style={styles.mono}>reward_grant_enabled=false</Text>
          <Text style={styles.mono}>permanent_progress_enabled=false</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Timeline locale · {node.steps.length} step</Text>
          {node.steps.map((s, idx) => {
            const active = idx === stepIndex;
            const done = idx < stepIndex;
            return (
              <View key={s.id} style={[styles.step, active && styles.stepActive, done && styles.stepDone]}>
                <Text style={styles.stepLabel}>{idx + 1}. [{s.kind}] {s.label}</Text>
              </View>
            );
          })}
        </View>

        <View style={styles.row}>
          <Pressable
            accessibilityRole="button"
            onPress={onPlayPause}
            style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>{playing ? 'Pausa' : completed ? 'Ripeti' : 'Play'}</Text>
          </Pressable>
          <Pressable
            accessibilityRole="button"
            onPress={onStepNext}
            style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>Step successivo</Text>
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
            <Text style={styles.sectionTitle}>Anteprima risultato</Text>
            <Text style={styles.mono}>status: result_preview_only</Text>
            <Text style={styles.mono}>reward_grant_executed: false</Text>
            <Text style={styles.mono}>permanent_progress: false</Text>
            <Text style={styles.mono}>db_writes: 0</Text>

            <Text style={styles.sectionTitle}>Reward preview · DISABILITATO (scope=preview_only)</Text>
            <Text style={styles.mono}>· mat_alpha_shard x1 (preview_only)</Text>
            <Text style={styles.mono}>· mat_alpha_ember x2 (preview_only)</Text>

            <Text style={styles.sectionTitle}>Progress preview · DISABILITATO (transient)</Text>
            <Text style={styles.mono}>node_id: {node.node_id}</Text>
            <Text style={styles.mono}>cleared_in_preview: true</Text>
            <Text style={styles.mono}>persisted: false</Text>
          </View>
        ) : null}

        <View style={styles.row}>
          <Pressable
            accessibilityRole="button"
            onPress={onOpenVisualPreview}
            style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>Apri Visual Preview Router</Text>
          </Pressable>
          <Pressable
            accessibilityRole="button"
            onPress={onBack}
            style={({ pressed }) => [styles.btn, styles.btnSecondary, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>Indietro</Text>
          </Pressable>
        </View>

        <Text style={styles.footer}>
          Schermata deeplink-only. Non collegata ad alcun menu pubblico. Platform: {Platform.OS}
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
    color: '#ffd166', fontSize: 12, fontWeight: '600',
    marginBottom: 16, backgroundColor: '#2a2310', padding: 8, borderRadius: 6,
  },
  card: { backgroundColor: '#141414', borderRadius: 8, padding: 12, marginBottom: 12, borderWidth: 1, borderColor: '#222' },
  sectionTitle: { color: '#eaeaea', fontSize: 14, fontWeight: '700', marginTop: 8, marginBottom: 6 },
  mono: { color: '#bcdcff', fontSize: 12, fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace', default: 'monospace' }) },
  hint: { color: '#a3d9a5', fontSize: 12, marginTop: 6, fontStyle: 'italic' },
  step: {
    paddingVertical: 8, paddingHorizontal: 10, borderRadius: 6, marginBottom: 4,
    backgroundColor: '#1a1a1a', borderLeftWidth: 3, borderLeftColor: '#333',
  },
  stepActive: { borderLeftColor: '#4cc9f0', backgroundColor: '#0c2030' },
  stepDone: { borderLeftColor: '#52c41a', opacity: 0.7 },
  stepLabel: { color: '#dcdcdc', fontSize: 13 },
  row: { flexDirection: 'row', gap: 8, marginVertical: 8, flexWrap: 'wrap' },
  btn: {
    flex: 1, minWidth: 120, backgroundColor: '#1f6feb', paddingVertical: 12, borderRadius: 8,
    alignItems: 'center', minHeight: 44, justifyContent: 'center',
  },
  btnSecondary: { backgroundColor: '#333' },
  btnPressed: { opacity: 0.7 },
  btnText: { color: '#fff', fontSize: 13, fontWeight: '700' },
  footer: { color: '#666', fontSize: 11, marginTop: 12, textAlign: 'center' },
});

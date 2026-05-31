/**
 * frontend/app/story-visual-battle-sandbox.tsx
 *
 * PROJECT_STORY_VISUAL_BATTLE_SANDBOX (v32 PHASE_3).
 *
 * Sandbox visual playback for Story battle synthetic timeline.
 * Reads from /api/story/battle-instance-preview/* (gated by
 * STORY_BATTLE_INSTANCE_PREVIEW_ENABLED). Does NOT call /api/battle/simulate.
 * Does NOT call /api/story/battle. Does NOT write to AsyncStorage. Does NOT
 * advance any story progress. Does NOT grant any reward. Sandbox dev/QA route
 * not linked from Home/menu/tabs.
 */
import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const API_BASE = process.env.EXPO_PUBLIC_BACKEND_URL ?? process.env.EXPO_BACKEND_URL ?? '';

type BattleInstance = {
  battle_instance_id: string;
  idempotency_key: string;
  mode_id: string;
  chapter_id: string;
  stage_id: string;
  battle_seed?: string | null;
  preview_only?: boolean;
  db_writes?: number;
  reward_grant_enabled?: boolean;
  story_progress_enabled?: boolean;
};

type TimelineEvent = {
  tick: number;
  actor: string;
  ability: string;
  target: string;
  synthetic_damage: number;
  is_crit: boolean;
  sandbox: boolean;
};

type PlaybackPayload = {
  status?: string;
  sandbox?: boolean;
  chapter_id?: string;
  stage_id?: string;
  battle_seed?: string;
  timeline?: TimelineEvent[];
  tick_count?: number;
  final_result?: { winner?: string; sandbox?: boolean; note?: string };
  safety?: Record<string, unknown>;
};

export default function StoryVisualBattleSandboxScreen() {
  const [chapterId, setChapterId] = useState<string>('chapter_1');
  const [stageId, setStageId] = useState<string>('1-1');
  const [battleInstance, setBattleInstance] = useState<BattleInstance | null>(null);
  const [playback, setPlayback] = useState<PlaybackPayload | null>(null);
  const [playIndex, setPlayIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorText, setErrorText] = useState<string | null>(null);

  const createPreview = useCallback(async () => {
    setLoading(true);
    setErrorText(null);
    try {
      const r = await fetch(`${API_BASE}/api/story/battle-instance-preview/create-preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chapter_id: chapterId, stage_id: stageId }),
      });
      if (r.status === 503) {
        setErrorText('Sandbox endpoint disabilitato (flag off). Default safe state.');
        return;
      }
      const data = await r.json();
      setBattleInstance(data?.battle_instance ?? null);
    } catch (e: any) {
      setErrorText(`Errore creazione preview: ${e?.message ?? 'unknown'}`);
    } finally {
      setLoading(false);
    }
  }, [chapterId, stageId]);

  const loadPlayback = useCallback(async () => {
    setLoading(true);
    setErrorText(null);
    try {
      const seed = battleInstance?.battle_seed || '';
      const url = new URL(`${API_BASE}/api/story/battle-instance-preview/sandbox-playback`);
      url.searchParams.set('chapter_id', chapterId);
      url.searchParams.set('stage_id', stageId);
      if (seed) url.searchParams.set('battle_seed', seed);
      const r = await fetch(url.toString());
      if (r.status === 503) {
        setErrorText('Sandbox endpoint disabilitato (flag off).');
        return;
      }
      const data = await r.json();
      setPlayback(data);
      setPlayIndex(0);
    } catch (e: any) {
      setErrorText(`Errore playback: ${e?.message ?? 'unknown'}`);
    } finally {
      setLoading(false);
    }
  }, [API_BASE, chapterId, stageId, battleInstance]);

  const playStep = useCallback(() => {
    if (!playback?.timeline) return;
    if (playIndex >= playback.timeline.length) return;
    setPlayIndex((i) => i + 1);
  }, [playback, playIndex]);

  const resetPlayback = useCallback(() => {
    setPlayIndex(0);
  }, []);

  const stepShown = playback?.timeline?.slice(0, playIndex) ?? [];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.bannerSandbox}>
          <Text style={styles.bannerTitle}>🧪 SANDBOX — Story Visual Battle</Text>
          <Text style={styles.bannerSub}>
            Nessun reward. Nessun avanzamento Storia. Nessun replay reward. Nessuna chiamata a /api/battle/simulate o /api/story/battle.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Parametri</Text>
          <View style={styles.row}>
            <Text style={styles.label}>chapter_id: {chapterId}</Text>
            <Text style={styles.label}>stage_id: {stageId}</Text>
          </View>
          <View style={styles.row}>
            <Pressable style={styles.btnSecondary} onPress={() => setStageId('1-1')}>
              <Text style={styles.btnText}>1-1</Text>
            </Pressable>
            <Pressable style={styles.btnSecondary} onPress={() => setStageId('1-3')}>
              <Text style={styles.btnText}>1-3</Text>
            </Pressable>
            <Pressable style={styles.btnSecondary} onPress={() => setStageId('2-1')}>
              <Text style={styles.btnText}>2-1</Text>
            </Pressable>
          </View>
        </View>

        <View style={styles.section}>
          <Pressable style={styles.btnPrimary} onPress={createPreview} disabled={loading}>
            <Text style={styles.btnPrimaryText}>1. Crea Preview Payload</Text>
          </Pressable>
          {battleInstance ? (
            <View style={styles.payloadBox}>
              <Text style={styles.mono}>battle_instance_id: {battleInstance.battle_instance_id}</Text>
              <Text style={styles.mono}>idempotency_key: {battleInstance.idempotency_key}</Text>
              <Text style={styles.mono}>mode_id: {battleInstance.mode_id}</Text>
              <Text style={styles.mono}>battle_seed: {battleInstance.battle_seed ?? '(none)'}</Text>
              <Text style={styles.mono}>db_writes: {battleInstance.db_writes ?? 0}</Text>
              <Text style={styles.mono}>reward_grant_enabled: {String(battleInstance.reward_grant_enabled ?? false)}</Text>
              <Text style={styles.mono}>story_progress_enabled: {String(battleInstance.story_progress_enabled ?? false)}</Text>
            </View>
          ) : null}
        </View>

        <View style={styles.section}>
          <Pressable
            style={[styles.btnPrimary, !battleInstance && styles.btnDisabled]}
            onPress={loadPlayback}
            disabled={loading || !battleInstance}
          >
            <Text style={styles.btnPrimaryText}>2. Carica Sandbox Playback</Text>
          </Pressable>
          {playback ? (
            <View style={styles.payloadBox}>
              <Text style={styles.mono}>sandbox: {String(playback.sandbox)}</Text>
              <Text style={styles.mono}>tick_count: {playback.tick_count}</Text>
              <Text style={styles.mono}>final_result: {playback.final_result?.winner}</Text>
              <Text style={styles.monoMuted}>{playback.final_result?.note}</Text>
            </View>
          ) : null}
        </View>

        <View style={styles.section}>
          <View style={styles.row}>
            <Pressable
              style={[styles.btnPrimary, !playback && styles.btnDisabled]}
              onPress={playStep}
              disabled={!playback || playIndex >= (playback?.tick_count ?? 0)}
            >
              <Text style={styles.btnPrimaryText}>3. Play step</Text>
            </Pressable>
            <Pressable
              style={[styles.btnSecondary, !playback && styles.btnDisabled]}
              onPress={resetPlayback}
              disabled={!playback}
            >
              <Text style={styles.btnText}>Reset</Text>
            </Pressable>
          </View>
          <Text style={styles.progressLabel}>
            Step {playIndex} / {playback?.tick_count ?? 0}
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Timeline (sandbox)</Text>
          {stepShown.map((ev) => (
            <View key={ev.tick} style={styles.tickRow}>
              <Text style={styles.tickHeader}>
                Tick {ev.tick} — {ev.actor} → {ev.target}
              </Text>
              <Text style={styles.mono}>
                {ev.ability} | dmg {ev.synthetic_damage}{ev.is_crit ? ' 💥 crit' : ''}
              </Text>
            </View>
          ))}
        </View>

        {loading ? (
          <View style={styles.section}>
            <ActivityIndicator color="#cf2" />
          </View>
        ) : null}
        {errorText ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{errorText}</Text>
          </View>
        ) : null}

        <View style={styles.footerNote}>
          <Text style={styles.footerText}>
            Sandbox dev/QA only. Non collegata da Home/menu. Nessun reward, nessun progresso Storia, nessun replay reward, nessun DB write.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0b0f17' },
  container: { padding: 16, paddingBottom: 64 },
  bannerSandbox: { backgroundColor: '#3b0a0a', borderColor: '#a02020', borderWidth: 1, borderRadius: 12, padding: 14, marginBottom: 16 },
  bannerTitle: { color: '#ffd6d6', fontSize: 16, fontWeight: '700', marginBottom: 4 },
  bannerSub: { color: '#ffe1e1', fontSize: 12, lineHeight: 18 },
  section: { marginBottom: 16, backgroundColor: '#141a26', borderRadius: 12, padding: 12 },
  sectionTitle: { color: '#cfd8e3', fontSize: 14, fontWeight: '700', marginBottom: 8 },
  row: { flexDirection: 'row', gap: 8, flexWrap: 'wrap', marginBottom: 8 },
  label: { color: '#cfd8e3', fontSize: 12 },
  btnPrimary: { backgroundColor: '#2a4ad2', paddingVertical: 10, paddingHorizontal: 14, borderRadius: 10, alignSelf: 'flex-start', marginBottom: 8 },
  btnPrimaryText: { color: '#ffffff', fontWeight: '700' },
  btnSecondary: { backgroundColor: '#1e2533', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8 },
  btnText: { color: '#cfd8e3', fontWeight: '600' },
  btnDisabled: { opacity: 0.4 },
  payloadBox: { backgroundColor: '#0c1422', borderRadius: 8, padding: 10, marginTop: 8 },
  mono: { color: '#a9e2ff', fontFamily: 'monospace' as any, fontSize: 12 },
  monoMuted: { color: '#6aa0c0', fontFamily: 'monospace' as any, fontSize: 11, marginTop: 4 },
  progressLabel: { color: '#cfd8e3', fontSize: 12, marginTop: 4 },
  tickRow: { backgroundColor: '#0c1422', padding: 8, borderRadius: 8, marginBottom: 6 },
  tickHeader: { color: '#ffe9b0', fontWeight: '600', marginBottom: 2 },
  errorBox: { backgroundColor: '#2a0a0a', borderColor: '#a02020', borderWidth: 1, borderRadius: 8, padding: 10, marginVertical: 8 },
  errorText: { color: '#ffb3b3', fontSize: 12 },
  footerNote: { marginTop: 16, padding: 12, backgroundColor: '#0a1322', borderRadius: 8 },
  footerText: { color: '#7a8aa0', fontSize: 11, lineHeight: 16, fontStyle: 'italic' },
});

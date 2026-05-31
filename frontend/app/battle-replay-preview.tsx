/*
 * PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK (v36 PHASE_6)
 *
 * Deeplink-only Battle Replay Preview screen.
 * - Mounted at /battle-replay-preview
 * - NOT linked from Home / menu / Guild War / Story / combat.
 * - Fetches /api/battle-replay-preview/config first.
 * - If 503 disabled -> shows disabled state with safety summary.
 * - If enabled -> fetches sample Guild War replay, calls validate-replay-payload,
 *   then calls playback-preview, then reuses the v35 VisualBattlePreviewShell.
 *
 * Strict invariants:
 *   - No POST to /api/story/battle.
 *   - No POST to /api/battle/simulate.
 *   - No reward claim button.
 *   - No commit button.
 *   - No war score commit button.
 *   - No AsyncStorage writes.
 *   - No live /battle-replay route created here.
 *
 * Local adapter:
 *   Guild War replay payload -> VisualBattlePreviewShell payload shape.
 *   attacker_snapshot          -> team_snapshot
 *   defender_snapshot          -> enemy_snapshot
 *   battle_seed_or_precomputed_log -> battle_seed_or_precomputed_battle_log
 *   playback_timeline          -> playback_timeline
 *   result_summary             -> result_summary
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Constants from 'expo-constants';
import { VisualBattlePreviewShell } from '../components/visualBattleRunner/VisualBattlePreviewShell';

const BACKEND_URL =
  (Constants?.expoConfig?.extra as any)?.EXPO_BACKEND_URL ||
  (process.env.EXPO_PUBLIC_BACKEND_URL as string | undefined) ||
  '';

const BASE = `${BACKEND_URL}/api/battle-replay-preview`;

type ConfigResp = {
  status?: string;
  feature_flag?: string;
  runtime_enabled?: boolean;
  preview_only?: boolean;
  viewer_kind?: string;
  contract_version?: string;
  schema_source?: string;
  safety_flags?: Record<string, unknown>;
  detail?: any;
};

type ReplayPayload = Record<string, any>;

type PlaybackResp = {
  status?: string;
  runner_mode?: string;
  viewer_kind?: string;
  battle_instance_id?: string;
  guild_war_battle_id?: string;
  timeline?: Array<{ t?: number; event?: string }>;
  result_summary?: Record<string, any>;
  war_score_delta_display_only?: Record<string, any>;
  guild_war_context?: Record<string, any>;
  validation?: { valid?: boolean; missing_fields?: string[] };
  safety_flags?: Record<string, unknown>;
  notes?: string[];
};

/**
 * Pure local adapter: Guild War replay payload -> shell payload shape.
 * Read-only mapping. No mutation of input.
 */
function adaptReplayPayloadForShell(replay: ReplayPayload | null): ReplayPayload | null {
  if (!replay) return null;
  return {
    battle_instance_id: replay.battle_instance_id,
    runner_mode: 'replay_view',
    mode_id: 'guild_war_replay',
    source_entrypoint: 'battle_replay_preview',
    viewer_kind: 'guild_war_view',
    // shell expects team_snapshot.heroes + enemy_snapshot.enemies
    team_snapshot: {
      schema: 'team_snapshot_v1_adapted',
      heroes: (replay?.attacker_snapshot?.heroes || []).map((h: any) => ({
        slot: h?.slot,
        hero_id: h?.hero_id,
        name: h?.name,
        level: h?.level,
        hp: h?.hp,
        atk: h?.atk,
      })),
      immutable_during_playback: true,
    },
    enemy_snapshot: {
      schema: 'enemy_snapshot_v1_adapted',
      enemies: (replay?.defender_snapshot?.heroes || []).map((h: any) => ({
        slot: h?.slot,
        // adapt: defender hero_id becomes enemy_id for the shell
        enemy_id: h?.hero_id,
        name: h?.name,
        level: h?.level,
        hp: h?.hp,
        atk: h?.atk,
      })),
      immutable_during_playback: true,
    },
    formation_snapshot: {
      schema: 'formation_snapshot_v1_adapted',
      layout: 'guild_war_2v1',
      immutable_during_playback: true,
    },
    battle_background_context: {
      background_id: 'bg_preview_guild_war',
      music_id: 'bgm_preview_guild_war',
      weather: 'clear',
      lighting: 'neutral',
      faction_theme: 'guild_war',
    },
    // shell expects the field name battle_seed_or_precomputed_battle_log
    battle_seed_or_precomputed_battle_log: replay?.battle_seed_or_precomputed_log
      ? {
          kind: replay.battle_seed_or_precomputed_log.kind || 'precomputed_battle_log',
          // shell's HP bars look up entry.target against enemy_id; the log already
          // uses defender hero_id as target, which maps to enemy_id in the adapter.
          precomputed_battle_log: replay.battle_seed_or_precomputed_log.precomputed_battle_log || [],
          client_side_simulation_forbidden_in_authoritative_modes: true,
        }
      : { kind: 'precomputed_battle_log', precomputed_battle_log: [] },
    playback_timeline: replay?.playback_timeline || [],
    result_summary: {
      ...(replay?.result_summary || {}),
      display_only_in_runner: true,
    },
    reward_policy: { grant_enabled: false, runner_can_grant: false },
    exp_policy: { grant_enabled: false, runner_can_grant: false },
    progress_policy: { advance_enabled: false, runner_can_advance: false },
    result_commit_policy: { commit_enabled: false, runner_commits: false },
    replay_snapshot_policy: { write_enabled: false },
    ui_policy: {
      show_claim_buttons: false,
      show_commit_buttons: false,
      spectator_only: true,
      skip_speed_auto_allowed: true,
    },
    privacy_policy: replay?.privacy_policy || { share_contains_pii: false, redact_other_players: true },
    created_at: replay?.created_at,
    expires_at: replay?.expires_at,
  };
}

export default function BattleReplayPreviewScreen() {
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [config, setConfig] = useState<ConfigResp | null>(null);
  const [configHttpStatus, setConfigHttpStatus] = useState<number>(0);
  const [replayPayload, setReplayPayload] = useState<ReplayPayload | null>(null);
  const [validationOk, setValidationOk] = useState<boolean | null>(null);
  const [playback, setPlayback] = useState<PlaybackResp | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setErrorMsg(null);
    try {
      const cfgRes = await fetch(`${BASE}/config`, { method: 'GET' });
      setConfigHttpStatus(cfgRes.status);
      const cfgJson: ConfigResp = await cfgRes.json().catch(() => ({}));
      setConfig(cfgJson);

      if (cfgRes.status !== 200) {
        setReplayPayload(null);
        setValidationOk(null);
        setPlayback(null);
        return;
      }

      const spRes = await fetch(`${BASE}/sample-guild-war-replay`, { method: 'GET' });
      const spJson = await spRes.json().catch(() => ({}));
      const pl = (spJson as any)?.payload || null;
      setReplayPayload(pl);

      if (pl) {
        const vRes = await fetch(`${BASE}/validate-replay-payload`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ payload: pl }),
        });
        const vJson = await vRes.json().catch(() => ({}));
        setValidationOk(Boolean((vJson as any)?.validation?.valid));

        const pRes = await fetch(`${BASE}/playback-preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ payload: pl }),
        });
        const pJson: PlaybackResp = await pRes.json().catch(() => ({}));
        setPlayback(pJson);
      }
    } catch (err: any) {
      setErrorMsg(String(err?.message || err));
    }
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      await fetchAll();
      setLoading(false);
    })();
  }, [fetchAll]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchAll();
    setRefreshing(false);
  }, [fetchAll]);

  const isDisabled =
    configHttpStatus === 503 ||
    (config?.detail && (config.detail as any)?.runtime_enabled === false);

  const shellPayload = adaptReplayPayloadForShell(replayPayload);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>Battle Replay Preview</Text>
        <Text style={styles.subtitle}>
          v36 PHASE_6 · BATTLE_REPLAY_PREVIEW_ROUTE_GATED_VIEW_ONLY · viewer_kind=guild_war_view
        </Text>

        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" />
            <Text style={styles.muted}>Caricamento config…</Text>
          </View>
        ) : isDisabled ? (
          <DisabledCard config={config} httpStatus={configHttpStatus} onRetry={onRefresh} />
        ) : (
          <View>
            <ReplayMetadataCard
              replay={replayPayload}
              playback={playback}
              validationOk={validationOk}
            />
            <WarScoreDisplayOnlyCard playback={playback} />
            {shellPayload && playback?.status === 'preview_ok' ? (
              <VisualBattlePreviewShell payload={shellPayload} playback={playback as any} />
            ) : null}
            <SafetyFooter />
          </View>
        )}

        {errorMsg ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>Errore: {errorMsg}</Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function DisabledCard({
  config,
  httpStatus,
  onRetry,
}: {
  config: ConfigResp | null;
  httpStatus: number;
  onRetry: () => void;
}) {
  const detail = (config as any)?.detail || config || {};
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Stato: DISABILITATO (503)</Text>
      <Text style={styles.muted}>HTTP {httpStatus} · feature_flag richiesta</Text>
      <Row label="feature_flag" value={String(detail?.feature_flag || 'BATTLE_REPLAY_PREVIEW_ENABLED')} />
      <Row label="runtime_enabled" value={String(detail?.runtime_enabled ?? false)} />
      <Row label="preview_only" value={String(detail?.preview_only ?? true)} />
      <Row label="viewer_kind" value={String(detail?.viewer_kind ?? 'guild_war_view')} />
      <Row label="db_writes" value={String(detail?.db_writes ?? 0)} />
      <Row label="reward_grant_enabled" value={String(detail?.reward_grant_enabled ?? false)} />
      <Row label="exp_grant_enabled" value={String(detail?.exp_grant_enabled ?? false)} />
      <Row label="progress_enabled" value={String(detail?.progress_enabled ?? false)} />
      <Row label="war_score_mutation_enabled" value={String(detail?.war_score_mutation_enabled ?? false)} />
      <Row label="guild_points_mutation_enabled" value={String(detail?.guild_points_mutation_enabled ?? false)} />
      <TouchableOpacity style={styles.retryBtn} onPress={onRetry}>
        <Text style={styles.retryBtnText}>Riprova fetch config</Text>
      </TouchableOpacity>
    </View>
  );
}

function ReplayMetadataCard({
  replay,
  playback,
  validationOk,
}: {
  replay: ReplayPayload | null;
  playback: PlaybackResp | null;
  validationOk: boolean | null;
}) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Replay Metadata · GUILD_WAR_VIEW</Text>
      <Row label="guild_war_battle_id" value={String(replay?.guild_war_battle_id || '')} />
      <Row label="battle_instance_id" value={String(replay?.battle_instance_id || '')} />
      <Row label="war_id" value={String(replay?.war_id || '')} />
      <Row label="viewer_kind" value={String(playback?.viewer_kind || replay?.viewer_kind || '')} />
      <Row label="runner_mode" value={String(playback?.runner_mode || '')} />
      <Row label="guild_attacker" value={String(replay?.attacker_snapshot?.guild_name || replay?.guild_id_attacker || '')} />
      <Row label="guild_defender" value={String(replay?.defender_snapshot?.guild_name || replay?.guild_id_defender || '')} />
      <Row label="created_at" value={String(replay?.created_at || '')} />
      <Row label="expires_at" value={String(replay?.expires_at || '')} />
      <Row label="validation_valid" value={validationOk === null ? '—' : String(validationOk)} />
    </View>
  );
}

function WarScoreDisplayOnlyCard({ playback }: { playback: PlaybackResp | null }) {
  const ws = (playback?.war_score_delta_display_only as any) || {};
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>War Score Delta · DISPLAY ONLY · NOT APPLIED</Text>
      <Row label="attacker_delta" value={String(ws?.attacker_delta ?? '—')} />
      <Row label="defender_delta" value={String(ws?.defender_delta ?? '—')} />
      <Row label="display_only_in_replay" value={String(ws?.display_only_in_replay ?? true)} />
      <Row label="applied" value={String(ws?.applied ?? false)} />
      <Text style={styles.muted}>
        Questi valori NON vengono applicati: il replay è view-only. Nessuna mutazione di war
        score o guild points.
      </Text>
    </View>
  );
}

function SafetyFooter() {
  return (
    <View style={styles.safetyCard}>
      <Text style={styles.safetyTitle}>Safety guarantees · GUILD_WAR_VIEW · NO REWARDS · NO MUTATION</Text>
      <SafetyRow label="db_writes" value="0" />
      <SafetyRow label="reward_grant_enabled" value="false" />
      <SafetyRow label="exp_grant_enabled" value="false" />
      <SafetyRow label="progress_enabled" value="false" />
      <SafetyRow label="war_score_mutation_enabled" value="false" />
      <SafetyRow label="guild_points_mutation_enabled" value="false" />
      <SafetyRow label="battle_rerun_enabled" value="false" />
      <SafetyRow label="calls_battle_engine" value="false" />
      <SafetyRow label="calls_api_battle_simulate" value="false" />
      <SafetyRow label="calls_api_story_battle" value="false" />
      <SafetyRow label="live_battle_replay_route_created" value="false" />
      <Text style={styles.muted}>
        Deeplink-only · non collegato da Home/menu/Guild War/Story/combat.
      </Text>
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue} numberOfLines={3}>
        {value}
      </Text>
    </View>
  );
}

function SafetyRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={[styles.rowLabel, { color: '#1f8a3a' }]}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0e1116' },
  container: { padding: 16 },
  title: { color: '#f4eccd', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#8d9099', fontSize: 12, marginBottom: 14 },
  loadingBox: { alignItems: 'center', paddingVertical: 40, gap: 8 },
  muted: { color: '#8d9099', fontSize: 12, marginTop: 6 },
  card: {
    backgroundColor: '#1a1e26',
    borderRadius: 10,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#272c36',
  },
  cardTitle: { color: '#f4eccd', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  row: { flexDirection: 'row', paddingVertical: 4, gap: 8 },
  rowLabel: { color: '#aab0ba', fontSize: 12, flex: 1 },
  rowValue: { color: '#e6e8ec', fontSize: 12, flex: 1.6, textAlign: 'right' },
  retryBtn: {
    marginTop: 14,
    backgroundColor: '#2a3142',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  retryBtnText: { color: '#f4eccd', fontWeight: '700', fontSize: 13 },
  safetyCard: {
    backgroundColor: '#0f2415',
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#1f4a30',
    marginTop: 4,
  },
  safetyTitle: { color: '#9fdca7', fontSize: 14, fontWeight: '700', marginBottom: 8 },
  errorBox: {
    backgroundColor: '#2a1414',
    borderColor: '#552525',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  errorText: { color: '#f4cccc', fontSize: 12 },
});

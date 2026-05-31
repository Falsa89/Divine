/*
 * PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK (v34 PHASE_4)
 *
 * Deeplink-only QA/sandbox screen for the Generic Visual Battle Runner Preview.
 * - Mounted at /generic-visual-battle-runner-preview
 * - NOT linked from Home / menu / Story / combat.
 * - Fetches /api/generic-visual-battle-runner-preview/config first.
 * - If 503 disabled -> shows disabled state with safety summary.
 * - If enabled -> fetches sample-payload, calls validate-payload + playback-preview,
 *   renders display-only timeline + safety cards.
 *
 * Strict invariants enforced in this file:
 *   - No POST to /api/story/battle.
 *   - No POST to /api/battle/simulate.
 *   - No reward claim button.
 *   - No commit button.
 *   - No AsyncStorage write tokens.
 *   - No inventory / material / user mutation.
 */
import React, { useEffect, useState, useCallback } from 'react';
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
// PUBLIC_CONTENT_REPAIR_v35b_VISUAL_BATTLE_PREVIEW_SHELL_MOUNT
// v35b: ensures public frontend file imports & mounts the Track A visual shell.
// Parent commit v35: 38c265136cc802ba262255339b021921ba61678a
import { VisualBattlePreviewShell } from '../components/visualBattleRunner/VisualBattlePreviewShell';

const BACKEND_URL =
  // EXPO_BACKEND_URL is injected via .env; fallback to /api on same origin.
  (Constants?.expoConfig?.extra as any)?.EXPO_BACKEND_URL ||
  (process.env.EXPO_PUBLIC_BACKEND_URL as string | undefined) ||
  '';

const BASE = `${BACKEND_URL}/api/generic-visual-battle-runner-preview`;

type ConfigResp = {
  status?: string;
  feature_flag?: string;
  runtime_enabled?: boolean;
  preview_only?: boolean;
  contract_version?: string;
  schema_source?: string;
  default_viewer_kind?: string;
  supported_viewer_kinds?: string[];
  safety_flags?: Record<string, unknown>;
  detail?: any;
};

type SamplePayloadResp = {
  status?: string;
  payload?: Record<string, any>;
  safety_flags?: Record<string, unknown>;
  detail?: any;
};

type PlaybackResp = {
  status?: string;
  runner_mode?: string;
  viewer_kind?: string;
  battle_instance_id?: string;
  timeline?: Array<{ t: number; event: string }>;
  result_summary?: Record<string, any>;
  validation?: { valid?: boolean; missing_fields?: string[] };
  safety_flags?: Record<string, unknown>;
  notes?: string[];
  detail?: any;
};

export default function GenericVisualBattleRunnerPreviewScreen() {
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [config, setConfig] = useState<ConfigResp | null>(null);
  const [configHttpStatus, setConfigHttpStatus] = useState<number>(0);
  const [samplePayload, setSamplePayload] = useState<Record<string, any> | null>(null);
  const [playback, setPlayback] = useState<PlaybackResp | null>(null);
  const [validationOk, setValidationOk] = useState<boolean | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setErrorMsg(null);
    try {
      const cfgRes = await fetch(`${BASE}/config`, { method: 'GET' });
      setConfigHttpStatus(cfgRes.status);
      const cfgJson: ConfigResp = await cfgRes.json().catch(() => ({}));
      setConfig(cfgJson);

      if (cfgRes.status !== 200) {
        // Disabled state; stop here.
        setSamplePayload(null);
        setPlayback(null);
        setValidationOk(null);
        return;
      }

      // Flag-on: fetch sample payload.
      const spRes = await fetch(`${BASE}/sample-payload`, { method: 'GET' });
      const spJson: SamplePayloadResp = await spRes.json().catch(() => ({}));
      const pl = spJson?.payload || null;
      setSamplePayload(pl);

      // Validate.
      if (pl) {
        const vRes = await fetch(`${BASE}/validate-payload`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ payload: pl }),
        });
        const vJson = await vRes.json().catch(() => ({}));
        setValidationOk(Boolean(vJson?.validation?.valid));

        // Playback preview.
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

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>Generic Visual Battle Runner — Preview</Text>
        <Text style={styles.subtitle}>v34 PHASE_4 · PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT</Text>

        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" />
            <Text style={styles.muted}>Caricamento config…</Text>
          </View>
        ) : isDisabled ? (
          <DisabledCard config={config} httpStatus={configHttpStatus} onRetry={onRefresh} />
        ) : (
          <View>
            {/* v35 Track A / v35b public content repair: visual runtime shell renders the playback envelope */}
            {/* Mounted only when sample payload exists AND playback.status === 'preview_ok' */}
            {samplePayload && playback?.status === 'preview_ok' ? (
              <VisualBattlePreviewShell payload={samplePayload} playback={playback as any} />
            ) : null}
            <EnabledView
              config={config}
              samplePayload={samplePayload}
              playback={playback}
              validationOk={validationOk}
            />
          </View>
        )}

        {errorMsg ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>Errore: {errorMsg}</Text>
          </View>
        ) : null}

        <SafetyFooter />
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
      <Row label="feature_flag" value={String(detail?.feature_flag || 'GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED')} />
      <Row label="runtime_enabled" value={String(detail?.runtime_enabled ?? false)} />
      <Row label="preview_only" value={String(detail?.preview_only ?? true)} />
      <Row label="db_writes" value={String(detail?.db_writes ?? 0)} />
      <Row label="reward_grant_enabled" value={String(detail?.reward_grant_enabled ?? false)} />
      <Row label="exp_grant_enabled" value={String(detail?.exp_grant_enabled ?? false)} />
      <Row label="progress_enabled" value={String(detail?.progress_enabled ?? false)} />
      <TouchableOpacity style={styles.retryBtn} onPress={onRetry}>
        <Text style={styles.retryBtnText}>Riprova fetch config</Text>
      </TouchableOpacity>
    </View>
  );
}

function EnabledView({
  config,
  samplePayload,
  playback,
  validationOk,
}: {
  config: ConfigResp | null;
  samplePayload: Record<string, any> | null;
  playback: PlaybackResp | null;
  validationOk: boolean | null;
}) {
  return (
    <View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Config (flag ON)</Text>
        <Row label="contract_version" value={String(config?.contract_version || '')} />
        <Row label="schema_source" value={String(config?.schema_source || '')} />
        <Row label="default_viewer_kind" value={String(config?.default_viewer_kind || '')} />
        <Row
          label="supported_viewer_kinds"
          value={(config?.supported_viewer_kinds || []).join(', ')}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Sample Payload (schema v33)</Text>
        <Row label="battle_instance_id" value={String(samplePayload?.battle_instance_id || '')} />
        <Row label="runner_mode" value={String(samplePayload?.runner_mode || '')} />
        <Row label="mode_id" value={String(samplePayload?.mode_id || '')} />
        <Row label="viewer_kind" value={String(samplePayload?.viewer_kind || '')} />
        <Row label="source_entrypoint" value={String(samplePayload?.source_entrypoint || '')} />
        <Row label="created_at" value={String(samplePayload?.created_at || '')} />
        <Row label="expires_at" value={String(samplePayload?.expires_at || '')} />
        <Row
          label="team_heroes"
          value={String((samplePayload?.team_snapshot?.heroes || []).map((h: any) => h.name).join(', '))}
        />
        <Row
          label="enemies"
          value={String((samplePayload?.enemy_snapshot?.enemies || []).map((e: any) => e.name).join(', '))}
        />
        <Row
          label="validation_valid"
          value={validationOk === null ? '—' : String(validationOk)}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Playback Preview (display-only)</Text>
        <Row label="status" value={String(playback?.status || '')} />
        <Row label="runner_mode" value={String(playback?.runner_mode || '')} />
        <Row label="viewer_kind" value={String(playback?.viewer_kind || '')} />
        <Row label="battle_instance_id" value={String(playback?.battle_instance_id || '')} />
        <Row
          label="result_summary.winner"
          value={String((playback?.result_summary as any)?.winner || '')}
        />
        <Row
          label="result_summary.mvp_hero_id"
          value={String((playback?.result_summary as any)?.mvp_hero_id || '')}
        />
        <Text style={[styles.cardTitle, { marginTop: 12 }]}>Timeline</Text>
        {(playback?.timeline || []).map((evt, idx) => (
          <View key={idx} style={styles.timelineRow}>
            <Text style={styles.timelineT}>t={evt.t}</Text>
            <Text style={styles.timelineEvt}>{evt.event}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

function SafetyFooter() {
  return (
    <View style={styles.safetyCard}>
      <Text style={styles.safetyTitle}>Safety guarantees</Text>
      <SafetyRow label="db_writes" ok value="0" />
      <SafetyRow label="reward_grant_enabled" ok value="false" />
      <SafetyRow label="exp_grant_enabled" ok value="false" />
      <SafetyRow label="progress_enabled" ok value="false" />
      <SafetyRow label="battle_simulation_enabled" ok value="false" />
      <SafetyRow label="calls_battle_engine" ok value="false" />
      <SafetyRow label="calls_api_battle_simulate" ok value="false" />
      <SafetyRow label="calls_api_story_battle" ok value="false" />
      <SafetyRow label="claim_button_enabled" ok value="false" />
      <SafetyRow label="commit_button_enabled" ok value="false" />
      <Text style={styles.muted}>
        Preview-only · deeplink-only · sandbox/QA. Non collegato da Home/menu/Story/combat.
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

function SafetyRow({ label, ok, value }: { label: string; ok: boolean; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={[styles.rowLabel, { color: ok ? '#1f8a3a' : '#a8341c' }]}>{label}</Text>
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
  muted: { color: '#8d9099', fontSize: 12 },
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
  timelineRow: {
    flexDirection: 'row',
    paddingVertical: 3,
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#272c36',
  },
  timelineT: { color: '#cbb064', fontSize: 12, width: 60 },
  timelineEvt: { color: '#e6e8ec', fontSize: 12, flex: 1 },
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

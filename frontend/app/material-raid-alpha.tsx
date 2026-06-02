/**
 * frontend/app/material-raid-alpha.tsx
 *
 * v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK
 * Track B — Frontend Material Raid Playable Alpha Screen.
 *
 * Deeplink-only screen. NO home menu wiring. NO live claim. NO mutation.
 * NO premium users.gems. NO stamina/tickets. NO direct battle_engine call.
 * Safe fallback when backend flag OFF (must not crash).
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  MATERIAL_RAID_TRACKS,
  MATERIAL_RAID_STAGE_IDS,
  MATERIAL_RAID_RECOMMENDED_POWER,
  describeRuntimeState,
  type MaterialRaidStageId,
  type MaterialRaidTrackId,
} from '../constants/materialRaid';

const BACKEND_URL =
  (process.env.EXPO_BACKEND_URL as string | undefined) ||
  (process.env.EXPO_PUBLIC_BACKEND_URL as string | undefined) ||
  '';

type AlphaConfig = {
  status?: string;
  alpha_slice_enabled?: boolean;
  playable_alpha_phase?: string;
  open_tracks?: string[];
  locked_tracks?: string[];
  visual_battle_required?: boolean;
  reward_claim_enabled?: boolean;
  materials_granted?: boolean;
  db_writes?: number;
};

type BattlePreview = {
  status?: string;
  battle_seed_preview?: string;
  recommended_power?: number;
  team_power?: number;
  delta?: number;
  visual_battle_payload_preview?: {
    mode?: string;
    enemy_family_preview?: string;
    battle_visual_required?: boolean;
    auto_resolve_allowed?: boolean;
  };
};

type RewardSummary = {
  status?: string;
  reward_preview?: { materials?: Record<string, number> };
  claim_button_enabled?: boolean;
  claim_flow_state?: string;
  materials_granted?: boolean;
  inventory_mutation?: boolean;
};

async function safeFetch<T>(path: string, init?: RequestInit): Promise<{ ok: boolean; data?: T; status?: number }> {
  if (!BACKEND_URL) return { ok: false, status: 0 };
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    });
    if (!res.ok) return { ok: false, status: res.status };
    const data = (await res.json()) as T;
    return { ok: true, data, status: res.status };
  } catch {
    return { ok: false, status: -1 };
  }
}

export default function MaterialRaidAlphaScreen() {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [config, setConfig] = useState<AlphaConfig | null>(null);
  const [selectedTrack, setSelectedTrack] = useState<MaterialRaidTrackId>('gear_material_raid');
  const [selectedStage, setSelectedStage] = useState<MaterialRaidStageId>('I');
  const [teamPower, setTeamPower] = useState<number>(15000);
  const [battlePreview, setBattlePreview] = useState<BattlePreview | null>(null);
  const [rewardSummary, setRewardSummary] = useState<RewardSummary | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      const r = await safeFetch<AlphaConfig>('/api/material-raid/alpha-slice-config');
      if (!mounted) return;
      setBackendOnline(r.ok && !!r.data?.alpha_slice_enabled);
      setConfig(r.ok ? r.data || null : null);
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const recommendedPower = MATERIAL_RAID_RECOMMENDED_POWER[selectedStage];
  const trackInfo = useMemo(
    () => MATERIAL_RAID_TRACKS.find((t) => t.track_id === selectedTrack),
    [selectedTrack]
  );

  const onPrepareBattle = async () => {
    setLoading(true);
    setBattlePreview(null);
    setRewardSummary(null);
    const r = await safeFetch<BattlePreview>('/api/material-raid/alpha-battle-preview', {
      method: 'POST',
      body: JSON.stringify({
        track_id: selectedTrack,
        stage_id: selectedStage,
        team_power: teamPower,
      }),
    });
    setBattlePreview(r.ok ? r.data || null : { status: 'backend_offline' });
    setLoading(false);
  };

  const onShowRewardSummary = async () => {
    setLoading(true);
    const r = await safeFetch<RewardSummary>('/api/material-raid/alpha-reward-summary-preview', {
      method: 'POST',
      body: JSON.stringify({
        track_id: selectedTrack,
        stage_id: selectedStage,
        battle_result_preview: 'victory_preview',
      }),
    });
    setRewardSummary(r.ok ? r.data || null : { status: 'backend_offline' });
    setLoading(false);
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Material Raid — Alpha Playable</Text>
          <Text style={styles.subtitle}>v51 · PLAYABLE_ALPHA_FOUNDATION_PREVIEW_ONLY</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>
              SOLO PREVIEW — nessun reward live, nessuna mutazione DB, nessun consumo di
              stamina/biglietti.
            </Text>
          </View>
          <Text style={styles.statusLine}>
            Backend:{' '}
            {backendOnline === null ? 'Verifica...' : backendOnline ? 'ONLINE (alpha attivo)' : 'OFFLINE / FLAG OFF'}
          </Text>
          {config?.playable_alpha_phase ? (
            <Text style={styles.statusLine}>Fase: {config.playable_alpha_phase}</Text>
          ) : null}
        </View>

        <Text style={styles.sectionTitle}>Track</Text>
        <View style={styles.row}>
          {MATERIAL_RAID_TRACKS.map((t) => {
            const active = t.track_id === selectedTrack;
            const locked = t.runtime_state === 'locked_deferred';
            return (
              <TouchableOpacity
                key={t.track_id}
                disabled={locked}
                onPress={() => setSelectedTrack(t.track_id)}
                style={[
                  styles.chip,
                  active && styles.chipActive,
                  locked && styles.chipLocked,
                ]}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>
                  {t.label_it}
                </Text>
                <Text style={styles.chipMeta}>{describeRuntimeState(t.runtime_state)}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
        {trackInfo ? <Text style={styles.helper}>{trackInfo.description_it}</Text> : null}

        <Text style={styles.sectionTitle}>Stage</Text>
        <View style={styles.row}>
          {MATERIAL_RAID_STAGE_IDS.map((s) => {
            const active = s === selectedStage;
            return (
              <TouchableOpacity
                key={s}
                onPress={() => setSelectedStage(s)}
                style={[styles.stageChip, active && styles.stageChipActive]}
              >
                <Text style={[styles.stageChipText, active && styles.stageChipTextActive]}>{s}</Text>
                <Text style={styles.stageMeta}>Pot. {MATERIAL_RAID_RECOMMENDED_POWER[s]}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={styles.sectionTitle}>Potere squadra (preview)</Text>
        <View style={styles.row}>
          {[5000, 15000, 45000, 120000, 320000, 500000].map((p) => (
            <TouchableOpacity
              key={p}
              onPress={() => setTeamPower(p)}
              style={[styles.powerChip, teamPower === p && styles.powerChipActive]}
            >
              <Text style={[styles.chipText, teamPower === p && styles.chipTextActive]}>{p}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <Text style={styles.helper}>
          Potere consigliato per lo stage selezionato: {recommendedPower}
        </Text>

        <TouchableOpacity
          style={[styles.primaryBtn, !backendOnline && styles.btnDisabled]}
          onPress={onPrepareBattle}
          disabled={!backendOnline || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryBtnText}>Prepara battaglia (preview)</Text>
          )}
        </TouchableOpacity>

        {!backendOnline ? (
          <View style={styles.offlineBox}>
            <Text style={styles.offlineText}>
              Modalità offline / flag OFF: la schermata mostra i dati locali, ma le chiamate
              di preview backend non sono disponibili. Nessun crash, nessuna mutazione.
            </Text>
          </View>
        ) : null}

        {battlePreview ? (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Battle preview</Text>
            <Text style={styles.resultLine}>Status: {battlePreview.status}</Text>
            {battlePreview.battle_seed_preview ? (
              <Text style={styles.resultLine}>Seed: {battlePreview.battle_seed_preview}</Text>
            ) : null}
            {battlePreview.visual_battle_payload_preview ? (
              <Text style={styles.resultLine}>
                Visual battle: required · enemy_family ={' '}
                {battlePreview.visual_battle_payload_preview.enemy_family_preview}
              </Text>
            ) : null}
            <View style={styles.visualPendingCard}>
              <Text style={styles.visualPendingText}>
                Visual battle runner sarà cablato nel prossimo pack di release acceleration.
              </Text>
            </View>
            <TouchableOpacity
              style={[styles.secondaryBtn, !backendOnline && styles.btnDisabled]}
              onPress={onShowRewardSummary}
              disabled={!backendOnline || loading}
            >
              <Text style={styles.secondaryBtnText}>Mostra reward summary (preview)</Text>
            </TouchableOpacity>
          </View>
        ) : null}

        {rewardSummary ? (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Reward summary (preview)</Text>
            <Text style={styles.resultLine}>Status: {rewardSummary.status}</Text>
            <Text style={styles.resultLine}>
              Materiali grantati: {String(rewardSummary.materials_granted)}
            </Text>
            <Text style={styles.resultLine}>
              Inventory mutation: {String(rewardSummary.inventory_mutation)}
            </Text>
            <Text style={styles.resultLine}>
              Claim button enabled: {String(rewardSummary.claim_button_enabled)}
            </Text>
            {rewardSummary.claim_flow_state ? (
              <Text style={styles.resultLine}>
                Claim flow: {rewardSummary.claim_flow_state}
              </Text>
            ) : null}
            {rewardSummary.reward_preview?.materials ? (
              <View style={styles.rewardList}>
                {Object.entries(rewardSummary.reward_preview.materials).map(([k, v]) => (
                  <Text key={k} style={styles.rewardLine}>
                    • {k}: {v}
                  </Text>
                ))}
              </View>
            ) : null}
            <Text style={styles.warningText}>
              Nessun claim live disponibile in alpha. I materiali non verranno aggiunti
              all'inventario.
            </Text>
          </View>
        ) : null}

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION · deeplink-only
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
  statusLine: { color: '#cdd6e0', marginTop: 8, fontSize: 12 },
  sectionTitle: { color: '#fff', fontSize: 16, fontWeight: '600', marginTop: 16, marginBottom: 8 },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: '#1a212b',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#2a3340',
    minHeight: 48,
  },
  chipActive: { backgroundColor: '#2b4f7a', borderColor: '#4a7fbe' },
  chipLocked: { opacity: 0.45 },
  chipText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
  chipTextActive: { color: '#fff' },
  chipMeta: { color: '#7e8896', fontSize: 10, marginTop: 2 },
  stageChip: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: '#1a212b',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#2a3340',
    alignItems: 'center',
    minWidth: 64,
    minHeight: 48,
  },
  stageChipActive: { backgroundColor: '#2b7a4f', borderColor: '#4abe7f' },
  stageChipText: { color: '#cdd6e0', fontSize: 14, fontWeight: '700' },
  stageChipTextActive: { color: '#fff' },
  stageMeta: { color: '#7e8896', fontSize: 10, marginTop: 2 },
  powerChip: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: '#1a212b',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#2a3340',
    minHeight: 48,
  },
  powerChipActive: { backgroundColor: '#7a2b4f', borderColor: '#be4a7f' },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 8 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 16,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  secondaryBtn: {
    backgroundColor: '#26313f',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#3a4554',
    minHeight: 48,
  },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  btnDisabled: { opacity: 0.4 },
  offlineBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#2a3340',
  },
  offlineText: { color: '#9aa4b2', fontSize: 12 },
  resultCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  resultTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  resultLine: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  visualPendingCard: {
    backgroundColor: '#1a2630',
    borderRadius: 8,
    padding: 10,
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#2a4554',
  },
  visualPendingText: { color: '#8ab8d8', fontSize: 12 },
  rewardList: { marginTop: 8, marginBottom: 8 },
  rewardLine: { color: '#cdd6e0', fontSize: 13 },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

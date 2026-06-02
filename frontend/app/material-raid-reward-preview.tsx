/**
 * frontend/app/material-raid-reward-preview.tsx
 *
 * v53 MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE
 * Track B — Reward Summary Preview screen (DEEPLINK-ONLY).
 *
 * NO home menu wiring. NO claim button. NO inventory/material mutation.
 * NO live grant. NO direct battle_engine call. NO /api/battle/simulate.
 * NO /api/story/battle. Result NON-AUTHORITATIVE.
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

const BACKEND_URL =
  (process.env.EXPO_BACKEND_URL as string | undefined) ||
  (process.env.EXPO_PUBLIC_BACKEND_URL as string | undefined) ||
  '';

type Params = {
  track_id?: string;
  stage_id?: string;
  battle_seed_preview?: string;
  battle_result_preview?: string;
  mvp_hero_id?: string;
  team_power?: string;
  recommended_power?: string;
};

type RewardSummary = {
  status?: string;
  reward_preview?: { materials?: Record<string, number> };
  materials_granted?: boolean;
  inventory_mutation?: boolean;
  claim_button_enabled?: boolean;
  claim_flow_state?: string;
  result_authoritative?: boolean;
  reward_claim_enabled?: boolean;
  reward_grant_enabled?: boolean;
  battle_engine_runtime_used?: boolean;
  source_visual_preview_supported?: boolean;
  next_allowed_action?: string;
  compatible_with_future_material_raid_claim_safety?: boolean;
  db_writes?: number;
  battle_result_preview?: string;
  mvp_hero_id_preview?: string | null;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

async function safePost<T>(path: string, body: object): Promise<{ ok: boolean; data?: T; status?: number }> {
  if (!BACKEND_URL) return { ok: false, status: 0 };
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) return { ok: false, status: res.status };
    const data = (await res.json()) as T;
    return { ok: true, data, status: res.status };
  } catch {
    return { ok: false, status: -1 };
  }
}

export default function MaterialRaidRewardPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const trackId = asString(raw.track_id);
  const stageId = asString(raw.stage_id);
  const seed = asString(raw.battle_seed_preview);
  const battleResult = asString(raw.battle_result_preview) || 'victory_preview';
  const mvpHeroId = asString(raw.mvp_hero_id);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  const hasMinimumParams = !!trackId && !!stageId;

  const [loading, setLoading] = useState<boolean>(false);
  const [summary, setSummary] = useState<RewardSummary | null>(null);
  const [backendError, setBackendError] = useState<boolean>(false);

  useEffect(() => {
    if (!hasMinimumParams) return;
    let mounted = true;
    (async () => {
      setLoading(true);
      setBackendError(false);
      const r = await safePost<RewardSummary>('/api/material-raid/alpha-reward-summary-preview', {
        track_id: trackId,
        stage_id: stageId,
        battle_result_preview: battleResult,
        mvp_hero_id: mvpHeroId,
      });
      if (!mounted) return;
      if (r.ok && r.data) setSummary(r.data);
      else { setSummary(null); setBackendError(true); }
      setLoading(false);
    })();
    return () => { mounted = false; };
  }, [hasMinimumParams, trackId, stageId, battleResult, mvpHeroId]);

  const onBack = () => {
    try {
      router.replace('/material-raid-alpha');
    } catch {
      // noop — navigation fallback
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Reward Summary Preview</Text>
          <Text style={styles.subtitle}>v53 · MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Nessun materiale verrà assegnato.</Text>
            <Text style={styles.warningText}>Claim live disabilitato.</Text>
          </View>
        </View>

        {!hasMinimumParams ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>Parametri mancanti</Text>
            <Text style={styles.errorBody}>
              Apri questa schermata da Material Raid Visual Preview dopo un
              alpha_battle_preview_ready valido. Nessun crash: torna ad Alpha.
            </Text>
            <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
              <Text style={styles.primaryBtnText}>Torna ad Alpha</Text>
            </TouchableOpacity>
          </View>
        ) : loading ? (
          <View style={styles.resultCard}>
            <ActivityIndicator color="#fff" />
            <Text style={styles.helper}>Recupero reward summary preview...</Text>
          </View>
        ) : backendError || !summary ? (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Backend non disponibile o flag OFF</Text>
            <Text style={styles.resultLine}>
              La schermata mostra comunque le garanzie preview-only. Nessun reward
              live in nessun caso.
            </Text>
            <View style={styles.guardsBox}>
              <Text style={styles.guardLine}>materials_granted = false</Text>
              <Text style={styles.guardLine}>inventory_mutation = false</Text>
              <Text style={styles.guardLine}>claim_button_enabled = false</Text>
              <Text style={styles.guardLine}>db_writes = 0</Text>
              <Text style={styles.guardLine}>result_authoritative = false</Text>
            </View>
            <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
              <Text style={styles.primaryBtnText}>Torna ad Alpha</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Riepilogo (preview)</Text>
            <Text style={styles.resultLine}>Track: {trackId}</Text>
            <Text style={styles.resultLine}>Stage: {stageId}</Text>
            {seed ? <Text style={styles.resultLine}>Seed: {seed}</Text> : null}
            {teamPower ? <Text style={styles.resultLine}>Potere squadra: {teamPower}</Text> : null}
            {recommendedPower ? (
              <Text style={styles.resultLine}>Potere consigliato: {recommendedPower}</Text>
            ) : null}
            <Text style={styles.resultLine}>
              Risultato preview: {summary.battle_result_preview || battleResult}
            </Text>
            {summary.mvp_hero_id_preview ? (
              <Text style={styles.resultLine}>MVP: {summary.mvp_hero_id_preview}</Text>
            ) : null}

            <View style={styles.divider} />
            <Text style={styles.sectionTitle}>Materiali (anteprima, non assegnati)</Text>
            {summary.reward_preview?.materials ? (
              Object.entries(summary.reward_preview.materials).map(([k, v]) => (
                <Text key={k} style={styles.rewardLine}>• {k}: {v}</Text>
              ))
            ) : (
              <Text style={styles.helper}>Nessun reward preview disponibile.</Text>
            )}

            <View style={styles.guardsBox}>
              <Text style={styles.guardLine}>status: {summary.status}</Text>
              <Text style={styles.guardLine}>materials_granted: {String(summary.materials_granted)}</Text>
              <Text style={styles.guardLine}>inventory_mutation: {String(summary.inventory_mutation)}</Text>
              <Text style={styles.guardLine}>claim_button_enabled: {String(summary.claim_button_enabled)}</Text>
              <Text style={styles.guardLine}>db_writes: {String(summary.db_writes ?? 0)}</Text>
              <Text style={styles.guardLine}>result_authoritative: {String(summary.result_authoritative)}</Text>
              {summary.next_allowed_action ? (
                <Text style={styles.guardLine}>next_allowed_action: {summary.next_allowed_action}</Text>
              ) : null}
            </View>

            <View style={styles.disclaimerBox}>
              <Text style={styles.disclaimerText}>
                Reward Summary Preview: nessun materiale aggiunto all'inventario, nessuna
                mutazione di gemme premium, nessuna scrittura su DB. Il claim live arriverà
                con un pack futuro di safety hardening (idempotency ledger + audit + rollback).
              </Text>
            </View>

            <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
              <Text style={styles.primaryBtnText}>Torna ad Alpha</Text>
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v53 MEGA_RELEASE_ACCELERATION_3 · deeplink-only · reward_claim_enabled=false
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
    backgroundColor: '#141a22', borderRadius: 12, padding: 16, marginBottom: 16,
    borderWidth: 1, borderColor: '#222b36',
  },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  warningBox: {
    backgroundColor: '#3a2a14', borderRadius: 8, padding: 12, marginTop: 12,
    borderWidth: 1, borderColor: '#a07020',
  },
  warningText: { color: '#e8c884', fontSize: 12 },
  errorCard: {
    backgroundColor: '#141a22', borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: '#222b36',
  },
  errorTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  errorBody: { color: '#cdd6e0', fontSize: 13, marginBottom: 12, lineHeight: 19 },
  resultCard: {
    backgroundColor: '#141a22', borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: '#222b36',
  },
  resultTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  resultLine: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 8 },
  divider: { height: 1, backgroundColor: '#222b36', marginVertical: 12 },
  sectionTitle: { color: '#fff', fontSize: 14, fontWeight: '600', marginBottom: 8 },
  rewardLine: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  guardsBox: {
    backgroundColor: '#1a212b', borderRadius: 8, padding: 10, marginTop: 12,
    borderWidth: 1, borderColor: '#2a3340',
  },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  disclaimerBox: {
    backgroundColor: '#1a2630', borderRadius: 8, padding: 10, marginTop: 12,
    borderWidth: 1, borderColor: '#2a4554',
  },
  disclaimerText: { color: '#8ab8d8', fontSize: 12, lineHeight: 17 },
  primaryBtn: {
    backgroundColor: '#3b6db5', paddingVertical: 14, borderRadius: 10,
    alignItems: 'center', marginTop: 16, minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

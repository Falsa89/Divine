/**
 * frontend/app/material-raid-visual-preview.tsx
 *
 * v52 MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK
 * Track B — Visual battle preview runner (DEEPLINK-ONLY).
 *
 * No home menu wiring. No claim button. No direct battle_engine call.
 * No /api/battle/simulate call. No /api/story/battle call. No DB writes.
 * Result is NON-AUTHORITATIVE. NO reward will ever be granted.
 */
import React, { useMemo } from 'react';
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
  track_id?: string;
  stage_id?: string;
  team_power?: string;
  recommended_power?: string;
  enemy_family_preview?: string;
  battle_seed_preview?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

function asInt(v: unknown): number | undefined {
  const s = asString(v);
  if (!s) return undefined;
  const n = parseInt(s, 10);
  return Number.isFinite(n) ? n : undefined;
}

export default function MaterialRaidVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const trackId = asString(raw.track_id);
  const stageId = asString(raw.stage_id);
  const teamPower = asInt(raw.team_power);
  const recommendedPower = asInt(raw.recommended_power);
  const enemyFamily = asString(raw.enemy_family_preview);
  const seed = asString(raw.battle_seed_preview);

  const hasMinimumParams = !!trackId && !!stageId && !!seed;
  const powerDelta = useMemo(() => {
    if (teamPower === undefined || recommendedPower === undefined) return undefined;
    return teamPower - recommendedPower;
  }, [teamPower, recommendedPower]);

  const onBack = () => {
    try {
      if (router.canGoBack()) router.back();
      else router.replace('/material-raid-alpha');
    } catch {
      router.replace('/material-raid-alpha');
    }
  };

  // v53 — Open Reward Summary Preview button handler (deeplink with query params).
  const onOpenRewardPreview = () => {
    if (!hasMinimumParams) return;
    const params: Record<string, string> = {
      track_id: String(trackId),
      stage_id: String(stageId),
      battle_seed_preview: String(seed),
      battle_result_preview: 'victory_preview',
    };
    if (teamPower !== undefined) params.team_power = String(teamPower);
    if (recommendedPower !== undefined) params.recommended_power = String(recommendedPower);
    router.push({ pathname: '/material-raid-reward-preview', params });
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Battaglia visuale — Preview</Text>
          <Text style={styles.subtitle}>v52 · MATERIAL_RAID_VISUAL_PREVIEW_RUNNER</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
          </View>
        </View>

        {!hasMinimumParams ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>Parametri mancanti</Text>
            <Text style={styles.errorBody}>
              Apri questa schermata da Material Raid Alpha dopo aver ottenuto un
              “alpha_battle_preview_ready”. La schermata non crasha: torna indietro
              o vai alla pagina alpha.
            </Text>
            <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
              <Text style={styles.primaryBtnText}>Torna ad Alpha</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Setup battaglia (preview)</Text>
            <Text style={styles.resultLine}>Mode: material_raid</Text>
            <Text style={styles.resultLine}>Track: {trackId}</Text>
            <Text style={styles.resultLine}>Stage: {stageId}</Text>
            {teamPower !== undefined ? (
              <Text style={styles.resultLine}>Potere squadra: {teamPower}</Text>
            ) : null}
            {recommendedPower !== undefined ? (
              <Text style={styles.resultLine}>Potere consigliato: {recommendedPower}</Text>
            ) : null}
            {powerDelta !== undefined ? (
              <Text style={styles.resultLine}>
                Delta: {powerDelta >= 0 ? `+${powerDelta}` : powerDelta}
              </Text>
            ) : null}
            {enemyFamily ? (
              <Text style={styles.resultLine}>Nemico preview: {enemyFamily}</Text>
            ) : null}
            <Text style={styles.resultLine}>Seed: {seed}</Text>

            <View style={styles.divider} />
            <Text style={styles.sectionTitle}>Anteprima sequenza</Text>
            {[1, 2, 3, 4, 5].map((turn) => (
              <View key={turn} style={styles.turnRow}>
                <Text style={styles.turnLabel}>Turno {turn}</Text>
                <Text style={styles.turnDetail}>
                  Azione preview deterministica (seed {seed?.slice(-6)})
                </Text>
              </View>
            ))}

            <View style={styles.disclaimerBox}>
              <Text style={styles.disclaimerText}>
                Questa preview NON consuma stamina, NON consuma biglietti, NON applica reward,
                NON modifica inventario, NON chiama battle_engine.py, NON chiama
                /api/battle/simulate o /api/story/battle, NON scrive su DB.
              </Text>
            </View>

            <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
              <Text style={styles.primaryBtnText}>Torna ad Alpha</Text>
            </TouchableOpacity>
            {hasMinimumParams ? (
              <TouchableOpacity style={styles.rewardBtn} onPress={onOpenRewardPreview}>
                <Text style={styles.rewardBtnText}>Apri reward summary preview</Text>
              </TouchableOpacity>
            ) : null}
          </View>
        )}

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v52 MEGA_RELEASE_ACCELERATION_2 · deeplink-only · result_authoritative=false
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
  errorCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  errorTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  errorBody: { color: '#cdd6e0', fontSize: 13, marginBottom: 12, lineHeight: 19 },
  resultCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  resultTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  resultLine: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  divider: { height: 1, backgroundColor: '#222b36', marginVertical: 12 },
  sectionTitle: { color: '#fff', fontSize: 14, fontWeight: '600', marginBottom: 8 },
  turnRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#1a212b',
  },
  turnLabel: { color: '#fff', fontSize: 13, fontWeight: '600' },
  turnDetail: { color: '#9aa4b2', fontSize: 12, flexShrink: 1, marginLeft: 8 },
  disclaimerBox: {
    backgroundColor: '#1a2630',
    borderRadius: 8,
    padding: 10,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#2a4554',
  },
  disclaimerText: { color: '#8ab8d8', fontSize: 12, lineHeight: 17 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 16,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  rewardBtn: {
    backgroundColor: '#2b7a4f',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#4abe7f',
    minHeight: 48,
  },
  rewardBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});

/**
 * AF2-N Public UI Preview — READ-ONLY (V19)
 * ───────────────────────────────────────────────────
 * Pure read-only screen showing sanitized canary status from
 *   GET /api/affinity/gift-spend/canary-status
 *
 * SAFETY:
 *   - NO POST/PUT/PATCH/DELETE.
 *   - NO Pressable invoking gift-spend.
 *   - NO claim/give/spend button.
 *   - NO Borea alias displayed.
 *   - NO runtime toggle.
 *   - NO inventory mutation.
 *   - Public, design-only preview labelled "Preview — Design only — Spend disabled".
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8001';

type CanaryStatus = {
  task_origin: string;
  feature_flag_currently_enabled: boolean;
  applied_to_combat: boolean;
  battle_runtime_attached: boolean;
  buffs_enabled: boolean;
  inventory_mutation_enabled?: boolean;
  affinity_points_mutation_enabled?: boolean;
  hidden_aliases_blocked: string[];
};

export default function AffinityGiftsPreview() {
  const [status, setStatus] = useState<CanaryStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/affinity/gift-spend/canary-status`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as CanaryStatus;
      // Sanitize: never display canary_allowlist_size, ledger counts, or user_ids.
      const sanitized: CanaryStatus = {
        task_origin: data.task_origin,
        feature_flag_currently_enabled: !!data.feature_flag_currently_enabled,
        applied_to_combat: !!data.applied_to_combat,
        battle_runtime_attached: !!data.battle_runtime_attached,
        buffs_enabled: !!data.buffs_enabled,
        inventory_mutation_enabled: !!data.inventory_mutation_enabled,
        affinity_points_mutation_enabled: !!data.affinity_points_mutation_enabled,
        hidden_aliases_blocked: Array.isArray(data.hidden_aliases_blocked)
          ? data.hidden_aliases_blocked.length > 0
            ? ['__hidden_aliases_blocked_count__: ' + data.hidden_aliases_blocked.length]
            : []
          : [],
      };
      setStatus(sanitized);
    } catch (e: any) {
      setError(String(e?.message || e));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchStatus();
  }, [fetchStatus]);

  return (
    <SafeAreaView style={styles.safe} edges={['top','left','right']}>
      <Stack.Screen options={{ title: 'Affinity Gifts — Preview' }} />
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.headerBox}>
          <Text style={styles.h1}>Affinity Gifts — Preview</Text>
          <Text style={styles.badge}>Design only — Spend disabled</Text>
          <Text style={styles.subtitle}>Read-only public preview. No spend, claim or give actions are available here.</Text>
        </View>

        {loading ? (
          <ActivityIndicator size="large" style={{ marginTop: 24 }} />
        ) : error ? (
          <View style={styles.errorBox} accessibilityLabel="Status fetch error">
            <Text style={styles.errorText}>Status temporarily unavailable</Text>
            <Text style={styles.errorDetail}>{error}</Text>
          </View>
        ) : status ? (
          <View style={styles.card}>
            <Row label="Feature flag" value={status.feature_flag_currently_enabled ? 'enabled' : 'disabled'} />
            <Row label="Combat application" value={status.applied_to_combat ? 'on' : 'off (safe)'} good={!status.applied_to_combat} />
            <Row label="Battle runtime" value={status.battle_runtime_attached ? 'attached' : 'detached (safe)'} good={!status.battle_runtime_attached} />
            <Row label="Buffs" value={status.buffs_enabled ? 'enabled' : 'disabled (safe)'} good={!status.buffs_enabled} />
            <Row label="Inventory writes" value={status.inventory_mutation_enabled ? 'enabled (allowlist only)' : 'disabled'} />
            <Row label="Affinity points writes" value={status.affinity_points_mutation_enabled ? 'enabled (allowlist only)' : 'disabled'} />
            <Row label="Hidden aliases protection" value={status.hidden_aliases_blocked.length > 0 ? 'active' : 'inactive'} good={status.hidden_aliases_blocked.length > 0} />
          </View>
        ) : null}

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>About this preview</Text>
          <Text style={styles.infoText}>
            This is a public read-only preview of the Affinity Gifts safety state. No interaction here mutates inventory, affinity, ledger or battle state.
            Spend, claim and give actions remain restricted to controlled allowlist QA flows.
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>v19 • read-only</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function Row({ label, value, good }: { label: string; value: string; good?: boolean }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={[styles.rowValue, good ? styles.rowGood : null]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0b0f17' },
  scroll: { padding: 16, paddingBottom: 48 },
  headerBox: {
    padding: 16,
    backgroundColor: '#111827',
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  h1: { color: '#e5e7eb', fontSize: 20, fontWeight: '700' },
  badge: {
    alignSelf: 'flex-start',
    marginTop: 6,
    color: '#fbbf24',
    backgroundColor: '#3f2d10',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    fontSize: 12,
    fontWeight: '600',
  },
  subtitle: { color: '#9ca3af', marginTop: 8, fontSize: 13 },
  card: {
    padding: 12,
    backgroundColor: '#0f1623',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#1f2937',
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: Platform.OS === 'web' ? 1 : StyleSheet.hairlineWidth,
    borderBottomColor: '#1f2937',
  },
  rowLabel: { color: '#9ca3af', flex: 1 },
  rowValue: { color: '#e5e7eb', fontWeight: '600' },
  rowGood: { color: '#34d399' },
  errorBox: {
    padding: 14,
    backgroundColor: '#1f1115',
    borderColor: '#7f1d1d',
    borderWidth: 1,
    borderRadius: 10,
  },
  errorText: { color: '#fca5a5', fontWeight: '700' },
  errorDetail: { color: '#9ca3af', marginTop: 4, fontSize: 12 },
  infoBox: {
    padding: 12,
    backgroundColor: '#0f1623',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  infoTitle: { color: '#e5e7eb', fontWeight: '700', marginBottom: 4 },
  infoText: { color: '#9ca3af', fontSize: 13, lineHeight: 18 },
  footer: { alignItems: 'center', marginTop: 16 },
  footerText: { color: '#6b7280', fontSize: 11 },
});

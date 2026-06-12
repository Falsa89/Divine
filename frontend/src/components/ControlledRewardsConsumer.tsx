/**
 * Pack 106 — Controlled Rewards UI consumer (read-only, server-scoped, guarded).
 *
 * Triple gate di sicurezza:
 *  1. Master flag `EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED` === 'true' (default OFF).
 *  2. `useServerScope().serverId` presente.
 *  3. `useAuth().token` presente.
 *
 * Sotto-flag opzionali (tutti default OFF):
 *   - EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED
 *   - EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED
 *   - EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED
 *
 * Mostra esclusivamente health + catalog read-only via GET. Nessun POST mutating.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const MASTER_FLAG = (process.env.EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED || 'false').toString().toLowerCase();
const MAIL_FLAG = (process.env.EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const ACH_FLAG = (process.env.EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const DWR_FLAG = (process.env.EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED || 'false').toString().toLowerCase();

const UI_ENABLED = MASTER_FLAG === 'true';

type State =
  | { kind: 'loading' }
  | { kind: 'ready'; health: any; catalog: any }
  | { kind: 'error'; message: string };

export type ControlledRewardsConsumerProps = {
  forceVisible?: boolean;
};

export const ControlledRewardsConsumer: React.FC<ControlledRewardsConsumerProps> = ({ forceVisible = false }) => {
  if (!UI_ENABLED && !forceVisible) return null;
  const { token } = useAuth();
  const { serverId } = useServerScope();
  const [state, setState] = useState<State>({ kind: 'loading' });

  const fetchData = useCallback(async () => {
    if (!token || !serverId) return;
    setState({ kind: 'loading' });
    try {
      const [hRes, cRes] = await Promise.all([
        fetch(`${BACKEND}/api/controlled-rewards/health`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${BACKEND}/api/controlled-rewards/catalog`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (!hRes.ok) throw new Error(`health http ${hRes.status}`);
      if (!cRes.ok) throw new Error(`catalog http ${cRes.status}`);
      setState({ kind: 'ready', health: await hRes.json(), catalog: await cRes.json() });
    } catch (e: any) {
      setState({ kind: 'error', message: e?.message || 'unknown error' });
    }
  }, [token, serverId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (state.kind === 'loading') {
    return (
      <View style={styles.container}>
        <ActivityIndicator />
        <Text style={styles.label}>Caricamento Controlled Rewards...</Text>
      </View>
    );
  }
  if (state.kind === 'error') {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>Errore: {state.message}</Text>
        <Pressable style={styles.btn} onPress={fetchData}>
          <Text style={styles.btnText}>Riprova</Text>
        </Pressable>
      </View>
    );
  }
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Controlled Rewards (server-scoped, gated)</Text>
      <Text style={styles.label}>Server: {serverId}</Text>
      <Text style={styles.label}>Catalog: {state.catalog.catalog_version}</Text>
      <Text style={styles.warn}>Reward live general: {String(state.health.reward_live_general)}</Text>
      <Text style={styles.warn}>Battlepass/Event/AFK/PvP/Guild live: {String(state.health.no_battlepass_event_afk_pvp_guild_live === false)}</Text>
      <Text style={styles.label}>Sources:</Text>
      {Object.entries(state.health.sources || {}).map(([k, v]: any) => (
        <Text key={k} style={styles.subLabel}>  - {k}: {v}</Text>
      ))}
      {MAIL_FLAG === 'true' && (
        <View style={styles.block}>
          <Text style={styles.blockTitle}>Mail rewards (read-only)</Text>
          {(state.catalog.mail_rewards || []).map((m: any) => (
            <Text key={m.mail_id} style={styles.itemLine}>• {m.title} → {JSON.stringify(m.reward)}</Text>
          ))}
        </View>
      )}
      {ACH_FLAG === 'true' && (
        <View style={styles.block}>
          <Text style={styles.blockTitle}>Achievement rewards (read-only)</Text>
          {(state.catalog.achievement_rewards || []).map((a: any) => (
            <Text key={a.achievement_id} style={styles.itemLine}>• {a.title} → {JSON.stringify(a.reward)}</Text>
          ))}
        </View>
      )}
      {DWR_FLAG === 'true' && (
        <View style={styles.block}>
          <Text style={styles.blockTitle}>Daily/Weekly tasks (read-only)</Text>
          {(state.catalog.daily_weekly_tasks || []).map((t: any) => (
            <Text key={t.task_id} style={styles.itemLine}>• [{t.period}] {t.title} → {JSON.stringify(t.reward)}</Text>
          ))}
        </View>
      )}
      <Pressable style={styles.btn} onPress={fetchData}>
        <Text style={styles.btnText}>Refresh</Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 12, backgroundColor: '#1a1a1a', borderRadius: 8, margin: 8 },
  title: { color: '#ffd700', fontSize: 16, fontWeight: 'bold', marginBottom: 6 },
  label: { color: '#fff', fontSize: 13, marginTop: 4 },
  subLabel: { color: '#aaa', fontSize: 12 },
  warn: { color: '#90ee90', fontSize: 12, marginTop: 2 },
  error: { color: '#ff6464', fontSize: 13, marginVertical: 8 },
  block: { marginTop: 8, paddingLeft: 8, borderLeftWidth: 2, borderLeftColor: '#444' },
  blockTitle: { color: '#fff', fontWeight: 'bold' },
  itemLine: { color: '#ddd', fontSize: 11 },
  btn: { marginTop: 10, backgroundColor: '#2a4', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 6, alignSelf: 'flex-start' },
  btnText: { color: '#fff', fontWeight: 'bold' },
});

export default ControlledRewardsConsumer;

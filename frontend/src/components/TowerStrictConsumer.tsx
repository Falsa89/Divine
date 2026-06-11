/**
 * Pack 101 — Tower Strict UI consumer (read-only, server-scoped, quarantena reward).
 *
 * Triple gate di sicurezza:
 *  1. Flag UI `EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED` === 'true' (default OFF).
 *  2. `useServerScope().serverId` presente (no fallback s1).
 *  3. `useAuth().token` presente.
 *
 * Comportamento:
 *  - Mostra solo lo stato strict server-scoped letto da `GET /api/tower/strict/status`.
 *  - Bottone "Anteprima battaglia" chiama `POST /api/tower/strict/battle/preview` SENZA grant reward.
 *  - NESSUN call al path legacy `/api/tower/battle` o `/api/tower/status`.
 *  - Etichetta esplicita "Reward in quarantena" per evitare aspettative utente.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const UI_FLAG = (process.env.EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED || 'false').toString().toLowerCase();
const UI_ENABLED = UI_FLAG === 'true';

type StrictProgress = {
  initialized: boolean;
  floor: number;
  highest_floor: number;
  rewards_claimed: string[];
  last_battle_at: string | null;
};

type Preview = {
  floor: number;
  team_power: number;
  enemy_power: number;
  victory_predicted: boolean;
  deterministic: boolean;
};

type State =
  | { kind: 'loading' }
  | { kind: 'ready'; progress: StrictProgress; preview: Preview | null }
  | { kind: 'psp_missing' }
  | { kind: 'error'; message: string };

export type TowerStrictConsumerProps = {
  forceVisible?: boolean;
};

export const TowerStrictConsumer: React.FC<TowerStrictConsumerProps> = ({ forceVisible = false }) => {
  if (!UI_ENABLED && !forceVisible) return null;
  return <TowerStrictConsumerInner />;
};

const TowerStrictConsumerInner: React.FC = () => {
  const auth = useAuth();
  const scope = useServerScope();
  const serverId = scope?.serverId;
  const token = auth?.token;
  const [state, setState] = useState<State>({ kind: 'loading' });

  const fetchStatus = useCallback(async () => {
    if (!serverId || !token) return;
    setState({ kind: 'loading' });
    try {
      const res = await fetch(
        `${BACKEND}/api/tower/strict/status?server_id=${encodeURIComponent(serverId)}`,
        { method: 'GET', headers: { Authorization: `Bearer ${token}` } },
      );
      if (res.status === 409) {
        setState({ kind: 'psp_missing' });
        return;
      }
      if (res.status !== 200) {
        const t = await res.text().catch(() => '');
        setState({ kind: 'error', message: `HTTP ${res.status}: ${t.slice(0, 80)}` });
        return;
      }
      const data = await res.json().catch(() => ({}));
      const progress = (data?.progress || {}) as StrictProgress;
      setState({ kind: 'ready', progress, preview: null });
    } catch (e: any) {
      setState({ kind: 'error', message: String(e?.message || e) });
    }
  }, [serverId, token]);

  const fetchPreview = useCallback(async () => {
    if (!serverId || !token) return;
    if (state.kind !== 'ready') return;
    try {
      const res = await fetch(
        `${BACKEND}/api/tower/strict/battle/preview?server_id=${encodeURIComponent(serverId)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({}),
        },
      );
      if (res.status !== 200) return;
      const data = await res.json().catch(() => ({}));
      const preview = (data?.preview || null) as Preview | null;
      setState({ kind: 'ready', progress: state.progress, preview });
    } catch {
      // network failure: ignora
    }
  }, [serverId, token, state]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus, serverId]);

  if (!serverId || !token) return null;

  return (
    <View style={styles.wrap}>
      <Text style={styles.h1}>Torre — server {serverId} (strict)</Text>
      <Text style={styles.warn}>Reward in quarantena: nessun premio concesso live.</Text>
      {state.kind === 'loading' && (
        <View style={styles.row}>
          <ActivityIndicator />
          <Text style={styles.muted}> Caricamento…</Text>
        </View>
      )}
      {state.kind === 'psp_missing' && (
        <Text style={styles.error}>Profilo server mancante. Crea un personaggio su questo server.</Text>
      )}
      {state.kind === 'error' && (
        <Text style={styles.error}>Errore: {state.message}</Text>
      )}
      {state.kind === 'ready' && (
        <>
          <View style={styles.row}>
            <Text style={styles.label}>Piano attuale</Text>
            <Text style={styles.val}>{state.progress.floor}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Piano massimo</Text>
            <Text style={styles.val}>{state.progress.highest_floor}</Text>
          </View>
          <Pressable
            onPress={fetchPreview}
            style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}
          >
            <Text style={styles.btnText}>Anteprima battaglia (no reward)</Text>
          </Pressable>
          {state.preview && (
            <View style={styles.previewBox}>
              <Text style={styles.previewTitle}>Anteprima piano {state.preview.floor}</Text>
              <Text style={styles.previewLine}>
                Team power: {state.preview.team_power} · Enemy power: {state.preview.enemy_power}
              </Text>
              <Text style={state.preview.victory_predicted ? styles.successInline : styles.warnInline}>
                {state.preview.victory_predicted ? 'Vittoria prevista' : 'Sconfitta prevista'}
              </Text>
              <Text style={styles.muted}>Deterministica · nessun reward concesso.</Text>
            </View>
          )}
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: { padding: 12, borderRadius: 8, backgroundColor: '#1c1c24', marginVertical: 8 },
  h1: { color: '#fff', fontSize: 14, fontWeight: '700', marginBottom: 4 },
  warn: { color: '#f0883e', fontSize: 11, marginBottom: 10, fontStyle: 'italic' },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 },
  label: { color: '#cdd9e5' },
  val: { color: '#fff', fontWeight: '700' },
  muted: { color: '#8b949e', fontSize: 11 },
  btn: { backgroundColor: '#1f6feb', paddingVertical: 10, paddingHorizontal: 16, borderRadius: 6, alignSelf: 'flex-start', marginTop: 8 },
  btnPressed: { opacity: 0.7 },
  btnText: { color: '#fff', fontWeight: '700' },
  previewBox: { marginTop: 12, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#2d333b' },
  previewTitle: { color: '#fff', fontWeight: '600', marginBottom: 4 },
  previewLine: { color: '#cdd9e5', fontSize: 12, marginBottom: 4 },
  successInline: { color: '#3fb950', fontWeight: '700' },
  warnInline: { color: '#f0883e', fontWeight: '700' },
  error: { color: '#f85149' },
});

export default TowerStrictConsumer;

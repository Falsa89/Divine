/**
 * Pack 97 — Daily Login Claim minimal gated consumer.
 *
 * IMPORTANTE — Gating rules:
 *   1. Component returns null se `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED !== 'true'`
 *      (default: hidden in production).
 *   2. Component returns null se `useServerScope()` non fornisce un server_id.
 *   3. Mai mostra successo senza una risposta 200 di /api/daily-login/claim.
 *   4. NESSUN consumer per mail/achievements/battlepass/event/AFK in Pack 97.
 *
 * Stati gestiti: idle | loading | claimed | already_claimed | kill_switch_off |
 *                psp_missing | error
 */
import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const UI_FLAG = (process.env.EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const UI_ENABLED = UI_FLAG === 'true';

type ClaimState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'claimed'; rewards: Record<string, number>; claim_key: string }
  | { kind: 'already_claimed'; rewards: Record<string, number>; claim_key: string }
  | { kind: 'kill_switch_off'; which: 'global' | 'daily' }
  | { kind: 'psp_missing' }
  | { kind: 'error'; message: string };

export type DailyLoginClaimButtonProps = {
  /** Override del flag UI per test/preview pages (default: false). */
  forceVisible?: boolean;
  /** Callback opzionale post-claim per refetch wallet/PSP. */
  onClaimed?: (rewards: Record<string, number>) => void;
};

export const DailyLoginClaimButton: React.FC<DailyLoginClaimButtonProps> = ({
  forceVisible = false,
  onClaimed,
}) => {
  const auth = useAuth();
  const scope = useServerScope();
  const [state, setState] = useState<ClaimState>({ kind: 'idle' });

  // Gate 1: UI feature flag (default OFF)
  if (!UI_ENABLED && !forceVisible) return null;
  // Gate 2: server scope required
  const serverId = scope?.serverId;
  if (!serverId) return null;
  // Gate 3: auth required
  const token = auth?.token;
  if (!token) return null;

  const claim = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const res = await fetch(`${BACKEND}/api/daily-login/claim?server_id=${encodeURIComponent(serverId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({}),
      });
      const data = await res.json().catch(() => ({}));
      if (res.status === 503) {
        const blocker = (data?.detail?.blocker || data?.blocker || '').toString();
        if (blocker === 'DAILY_LOGIN_CLAIM_DISABLED') {
          setState({ kind: 'kill_switch_off', which: 'daily' });
        } else {
          setState({ kind: 'kill_switch_off', which: 'global' });
        }
        return;
      }
      if (res.status === 409) {
        setState({ kind: 'psp_missing' });
        return;
      }
      if (res.status !== 200) {
        setState({ kind: 'error', message: data?.detail?.blocker || data?.blocker || `HTTP ${res.status}` });
        return;
      }
      const rewards = (data?.rewards?.server_scoped || {}) as Record<string, number>;
      const claim_key = (data?.claim_key || '').toString();
      if (data?.idempotent_replay) {
        setState({ kind: 'already_claimed', rewards, claim_key });
      } else {
        setState({ kind: 'claimed', rewards, claim_key });
        if (onClaimed) onClaimed(rewards);
      }
    } catch (e: any) {
      setState({ kind: 'error', message: String(e?.message || e) });
    }
  }, [serverId, token, onClaimed]);

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Ricompensa giornaliera</Text>
      {state.kind === 'idle' && (
        <Pressable onPress={claim} style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}>
          <Text style={styles.btnText}>Riscatta</Text>
        </Pressable>
      )}
      {state.kind === 'loading' && (
        <View style={styles.row}>
          <ActivityIndicator />
          <Text style={styles.status}> Richiesta in corso…</Text>
        </View>
      )}
      {state.kind === 'claimed' && (
        <Text style={styles.success}>
          ✓ Ricompensa riscattata: {Object.entries(state.rewards).map(([k, v]) => `${k} +${v}`).join(', ')}
        </Text>
      )}
      {state.kind === 'already_claimed' && (
        <Text style={styles.info}>Ricompensa di oggi già riscattata. Torna domani.</Text>
      )}
      {state.kind === 'kill_switch_off' && (
        <Text style={styles.warn}>
          Sistema temporaneamente non disponibile ({state.which === 'daily' ? 'daily_off' : 'global_off'}).
        </Text>
      )}
      {state.kind === 'psp_missing' && (
        <Text style={styles.warn}>Profilo server non trovato per questo server.</Text>
      )}
      {state.kind === 'error' && (
        <Text style={styles.error}>Errore: {state.message}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: { padding: 12, borderRadius: 8, backgroundColor: '#1f1f25', marginVertical: 8 },
  title: { color: '#fff', fontSize: 14, fontWeight: '600', marginBottom: 8 },
  btn: { backgroundColor: '#6f42c1', paddingVertical: 10, paddingHorizontal: 18, borderRadius: 6, alignSelf: 'flex-start' },
  btnPressed: { opacity: 0.7 },
  btnText: { color: '#fff', fontWeight: '700' },
  row: { flexDirection: 'row', alignItems: 'center' },
  status: { color: '#bbb', marginLeft: 8 },
  success: { color: '#7ee787' },
  info: { color: '#cdd9e5' },
  warn: { color: '#f0883e' },
  error: { color: '#f85149' },
});

export default DailyLoginClaimButton;

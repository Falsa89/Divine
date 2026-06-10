/**
 * Pack 98 — Daily Quest Claim minimal gated consumer.
 *
 * Stessa logica di gating del Pack 97 (`DailyLoginClaimButton`):
 *   1. UI flag `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` (Pack 97) deve essere true.
 *   2. Server scope presente (`useServerScope().serverId`).
 *   3. Auth token presente.
 *
 * Pack 98 SAFETY: Il backend rifiuta il claim con `DAILY_QUEST_COMPLETION_REQUIRED`
 * per utenti non marcati `pack_98_test_artifact`. Il componente espone questo stato
 * onestamente all'utente come "Quest non disponibile / in arrivo".
 */
import React, { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const UI_FLAG = (process.env.EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const UI_ENABLED = UI_FLAG === 'true';

const QUEST_IDS = ['daily_quest_1', 'daily_quest_2', 'daily_quest_3'] as const;
type QuestId = typeof QUEST_IDS[number];

type ClaimState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'claimed'; rewards: Record<string, number>; claim_key: string; quest_id: string }
  | { kind: 'already_claimed'; rewards: Record<string, number>; quest_id: string }
  | { kind: 'completion_required'; quest_id: string }
  | { kind: 'kill_switch_off'; which: 'global' | 'quest' }
  | { kind: 'whitelist_error'; quest_id: string }
  | { kind: 'psp_missing' }
  | { kind: 'error'; message: string };

export type DailyQuestClaimButtonProps = {
  forceVisible?: boolean;
  questId?: QuestId;
  onClaimed?: (rewards: Record<string, number>) => void;
};

export const DailyQuestClaimButton: React.FC<DailyQuestClaimButtonProps> = ({
  forceVisible = false,
  questId = 'daily_quest_1',
  onClaimed,
}) => {
  const auth = useAuth();
  const scope = useServerScope();
  const [state, setState] = useState<ClaimState>({ kind: 'idle' });

  if (!UI_ENABLED && !forceVisible) return null;
  const serverId = scope?.serverId;
  if (!serverId) return null;
  const token = auth?.token;
  if (!token) return null;

  const claim = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const res = await fetch(
        `${BACKEND}/api/daily-quest/claim?server_id=${encodeURIComponent(serverId)}&quest_id=${encodeURIComponent(questId)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({}),
        },
      );
      const data = await res.json().catch(() => ({}));
      const blocker = (data?.detail?.blocker || data?.blocker || '').toString();
      if (res.status === 503) {
        setState({ kind: 'kill_switch_off', which: blocker === 'DAILY_QUEST_CLAIM_DISABLED' ? 'quest' : 'global' });
        return;
      }
      if (res.status === 409) {
        if (blocker === 'DAILY_QUEST_COMPLETION_REQUIRED') {
          setState({ kind: 'completion_required', quest_id: questId });
        } else {
          setState({ kind: 'psp_missing' });
        }
        return;
      }
      if (res.status === 422 && blocker === 'QUEST_ID_NOT_WHITELISTED') {
        setState({ kind: 'whitelist_error', quest_id: questId });
        return;
      }
      if (res.status !== 200) {
        setState({ kind: 'error', message: blocker || `HTTP ${res.status}` });
        return;
      }
      const rewards = (data?.rewards?.server_scoped || {}) as Record<string, number>;
      if (data?.idempotent_replay) {
        setState({ kind: 'already_claimed', rewards, quest_id: questId });
      } else {
        setState({ kind: 'claimed', rewards, claim_key: data?.claim_key || '', quest_id: questId });
        if (onClaimed) onClaimed(rewards);
      }
    } catch (e: any) {
      setState({ kind: 'error', message: String(e?.message || e) });
    }
  }, [serverId, token, questId, onClaimed]);

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Quest giornaliera ({questId})</Text>
      {state.kind === 'idle' && (
        <Pressable onPress={claim} style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}>
          <Text style={styles.btnText}>Riscatta quest</Text>
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
          ✓ Quest completata: {Object.entries(state.rewards).map(([k, v]) => `${k} +${v}`).join(', ')}
        </Text>
      )}
      {state.kind === 'already_claimed' && (
        <Text style={styles.info}>Quest di oggi già riscattata.</Text>
      )}
      {state.kind === 'completion_required' && (
        <Text style={styles.warn}>
          Quest non ancora disponibile per il claim (sistema in arrivo).
        </Text>
      )}
      {state.kind === 'kill_switch_off' && (
        <Text style={styles.warn}>
          Sistema temporaneamente non disponibile ({state.which === 'quest' ? 'quest_off' : 'global_off'}).
        </Text>
      )}
      {state.kind === 'whitelist_error' && (
        <Text style={styles.error}>quest_id non valido</Text>
      )}
      {state.kind === 'psp_missing' && (
        <Text style={styles.warn}>Profilo server non trovato.</Text>
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

export default DailyQuestClaimButton;

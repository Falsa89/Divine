/**
 * Pack 100 — Daily Task Loop UI (overview server-side authoritative).
 *
 * Mostra in modo "glanceable" lo stato del primo loop reale:
 *  - Daily Login: pronto a riscattare oggi su S<server_id>.
 *  - Daily Quest 1: stato server-side dal tracker (`not_started` / `completed` / `claimed`).
 *  - Daily Quest 2/3: marcate come "in arrivo" (deferred) - NESSUN claim attivo.
 *
 * Triple gate di sicurezza:
 *  1. Flag UI `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` === 'true' (default OFF).
 *  2. Flag Home `EXPO_PUBLIC_DAILY_HOME_UNLOCK` === 'true' (default OFF).
 *  3. `useServerScope().serverId` presente (no fallback s1).
 *  4. `useAuth().token` presente.
 *
 * Lo stato del tracker è letto via `GET /api/daily-quest/progress?server_id=...`.
 * Lo switching di server (S1 -> S2) deve forzare un refresh tramite chiave
 * `serverId` su useEffect (no false positives da cache).
 *
 * NESSUNA scrittura. Solo lettura informativa + delegating ai claim button esistenti.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const UI_FLAG = (process.env.EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const HOME_FLAG = (process.env.EXPO_PUBLIC_DAILY_HOME_UNLOCK || 'false').toString().toLowerCase();
const UI_ENABLED = UI_FLAG === 'true';
const HOME_ENABLED = HOME_FLAG === 'true';

type TrackerState = 'not_started' | 'in_progress' | 'completed' | 'claimed';

type QuestRow = { quest_id: string; state: TrackerState };

export type DailyTaskLoopOverviewProps = {
  forceVisible?: boolean;
};

export const DailyTaskLoopOverview: React.FC<DailyTaskLoopOverviewProps> = ({ forceVisible = false }) => {
  if (!forceVisible && (!UI_ENABLED || !HOME_ENABLED)) return null;
  return <DailyTaskLoopOverviewInner forceVisible={forceVisible} />;
};

const DailyTaskLoopOverviewInner: React.FC<DailyTaskLoopOverviewProps> = ({ forceVisible = false }) => {
  const auth = useAuth();
  const scope = useServerScope();
  const serverId = scope?.serverId;
  const token = auth?.token;
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState<QuestRow[]>([]);

  const refresh = useCallback(async () => {
    if (!serverId || !token) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${BACKEND}/api/daily-quest/progress?server_id=${encodeURIComponent(serverId)}`,
        { method: 'GET', headers: { Authorization: `Bearer ${token}` } },
      );
      if (res.status === 200) {
        const data = await res.json().catch(() => ({}));
        setRows((data?.progress || []) as QuestRow[]);
      }
    } finally {
      setLoading(false);
    }
  }, [serverId, token]);

  // Server switching MUST refresh (S1 -> S2 deve invalidare lo stato in UI).
  useEffect(() => {
    refresh();
  }, [refresh, serverId]);

  if (!serverId || !token) return null;

  const findState = (qid: string): TrackerState => {
    const r = rows.find((x) => x.quest_id === qid);
    return (r?.state as TrackerState) || 'not_started';
  };

  const renderQuest = (qid: string, deferred: boolean) => {
    const s = findState(qid);
    let label = 'Non iniziata';
    let style = styles.chipNeutral;
    if (deferred) {
      label = 'In arrivo (deferred)';
      style = styles.chipDeferred;
    } else if (s === 'completed') {
      label = 'Pronta da riscattare';
      style = styles.chipReady;
    } else if (s === 'claimed') {
      label = 'Riscattata oggi';
      style = styles.chipClaimed;
    }
    return (
      <View key={qid} style={styles.row}>
        <Text style={styles.qid}>{qid}</Text>
        <View style={style}>
          <Text style={styles.chipText}>{label}</Text>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.wrap}>
      <Text style={styles.h1}>Daily Task Loop — server {serverId}</Text>
      {loading ? (
        <View style={styles.row}>
          <ActivityIndicator />
          <Text style={styles.muted}> Caricamento stato server…</Text>
        </View>
      ) : (
        <>
          {renderQuest('daily_quest_1', false)}
          {renderQuest('daily_quest_2', true)}
          {renderQuest('daily_quest_3', true)}
        </>
      )}
      <Text style={styles.footer}>
        Stato server-authoritative. Nessun completamento client-side.
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: { padding: 12, borderRadius: 8, backgroundColor: '#16161c', marginVertical: 8 },
  h1: { color: '#fff', fontSize: 14, fontWeight: '700', marginBottom: 10 },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 },
  qid: { color: '#cdd9e5', fontWeight: '600' },
  chipNeutral: { backgroundColor: '#2d333b', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  chipReady: { backgroundColor: '#3fb950', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  chipClaimed: { backgroundColor: '#8957e5', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  chipDeferred: { backgroundColor: '#6e7681', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  chipText: { color: '#fff', fontSize: 11, fontWeight: '700' },
  muted: { color: '#8b949e', marginLeft: 6 },
  footer: { color: '#6e7681', fontSize: 11, marginTop: 8, fontStyle: 'italic' },
});

export default DailyTaskLoopOverview;

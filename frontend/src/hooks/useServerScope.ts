// useServerScope.ts — v104 + PRE_QA_STABILIZATION_110 backward-compat alias.
//
// Espone `selected_server_id` (v104) e l'alias `serverId` (consumer attuali)
// affinche' i componenti Pack 98-106 (Daily*, *StrictConsumer, *RewardsConsumer,
// PlayableLoopConsumer) possano leggere uniformemente il server selezionato.
//
// SAFETY:
// - read-only di AsyncStorage
// - nessun token raw log
// - nessun secret in repo
// - nessuna mutazione DB
// - no silent s1 fallback: se non c'e' server selezionato, ritorniamo null
//   e NO_SERVER_SELECTED come token canonico.
import { useEffect, useRef, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type ServerScope = {
  // Canonical (Pack 91+):
  selected_server_id: string | null;
  selected_server_name: string | null;
  // Backward-compat alias (Pack 98-106 consumer):
  serverId: string | null;
  serverName: string | null;
  // Sentinel: indica al consumer che non e' stato fatto silent fallback.
  no_silent_s1_fallback: true;
  noServerSelectedToken: 'NO_SERVER_SELECTED';
  // Stato di runtime:
  is_isolation_pending: boolean;
  isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING';
  loading: boolean;
  // Pack 108 compat: refreshToken bump per re-fetch al cambio server.
  refreshToken: number;
  isReady: boolean;
};

export function useServerScope(): ServerScope {
  const [state, setState] = useState<ServerScope>({
    selected_server_id: null,
    selected_server_name: null,
    serverId: null,
    serverName: null,
    no_silent_s1_fallback: true,
    noServerSelectedToken: 'NO_SERVER_SELECTED',
    is_isolation_pending: true,
    isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING',
    loading: true,
    refreshToken: 0,
    isReady: false,
  });
  const lastIdRef = useRef<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const id = await AsyncStorage.getItem('v101_selected_server_id');
        const name = await AsyncStorage.getItem('v102_selected_server_name');
        if (!alive) return;
        const changed = id !== lastIdRef.current;
        lastIdRef.current = id;
        setState((prev) => ({
          selected_server_id: id,
          selected_server_name: name,
          // Alias canonici per i consumer Pack 98-106 / PlayableLoopConsumer.
          serverId: id,
          serverName: name,
          no_silent_s1_fallback: true,
          noServerSelectedToken: 'NO_SERVER_SELECTED',
          // Pre-QA Stabilization 110: il backend e' progressivamente
          // server-scoped via PSP/Pack 91+. Il flag isolation_pending resta
          // a true SOLO se davvero non e' implementato; ora l'isolamento
          // server-side esiste per tower/economy/controlled rewards/guild
          // strict/playable-loop, quindi marchiamo come false a riposo.
          is_isolation_pending: false,
          isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING',
          loading: false,
          refreshToken: changed ? prev.refreshToken + 1 : prev.refreshToken,
          isReady: true,
        }));
      } catch (_e) {
        if (alive) setState((s) => ({ ...s, loading: false, isReady: false }));
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return state;
}

export default useServerScope;

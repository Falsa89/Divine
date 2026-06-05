// useServerScope.ts — v104 — Hook frontend per esporre il selected_server_id ai loader.
//
// Scopo: fornire alle superfici di gioco (home/heroes/inventory/treasury/team/chat)
// un accesso uniforme a selected_server_id senza forzare nessun backend isolation.
// Finche' il backend non e' multi-shard, i loader continuano a leggere stato account
// condiviso ma la UI deve mostrare SERVER_DATA_ISOLATION_BACKEND_PENDING.
//
// SAFETY:
// - read-only di AsyncStorage
// - nessun token raw log
// - nessun secret in repo
// - nessuna mutazione DB
import { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type ServerScope = {
  selected_server_id: string | null;
  selected_server_name: string | null;
  is_isolation_pending: boolean;
  isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING';
  loading: boolean;
};

export function useServerScope(): ServerScope {
  const [state, setState] = useState<ServerScope>({
    selected_server_id: null,
    selected_server_name: null,
    is_isolation_pending: true,
    isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING',
    loading: true,
  });

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const id = await AsyncStorage.getItem('v101_selected_server_id');
        const name = await AsyncStorage.getItem('v102_selected_server_name');
        if (!alive) return;
        setState({
          selected_server_id: id,
          selected_server_name: name,
          // v104: backend per-server isolation NON ancora implementata.
          // Anche se selected_server_id e' presente, i dati runtime restano account-wide.
          is_isolation_pending: true,
          isolation_pending_token: 'SERVER_DATA_ISOLATION_BACKEND_PENDING',
          loading: false,
        });
      } catch (_e) {
        if (alive) setState((s) => ({ ...s, loading: false }));
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return state;
}

export default useServerScope;

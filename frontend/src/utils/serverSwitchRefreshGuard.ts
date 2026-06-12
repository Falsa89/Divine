// Pack 108 — Server Switch Refresh Guard.
//
// Quando l'utente cambia `selected_server_id`, ogni cache locale dei
// loader playable loop DEVE essere invalidata. Nessuna surface deve
// continuare a mostrare dati di un server precedente. Nessun fallback
// silenzioso a 's1'.
//
// Pattern uso:
//   const { serverId, refreshToken } = useServerSwitchRefreshGuard();
//   useEffect(() => { loadPlayableLoopMap(serverId); }, [refreshToken]);
import { useEffect, useRef, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import useServerScope from '../hooks/useServerScope';

export type ServerSwitchRefreshGuard = {
  serverId: string | null;
  refreshToken: number;
  isReady: boolean;
  /** Forza l'invalidazione manuale (ad es. logout). */
  bump: () => void;
  /** Stato canonico: se serverId === null, il loader deve NON usare 's1' come fallback. */
  serverScopeRequired: true;
};

export function useServerSwitchRefreshGuard(): ServerSwitchRefreshGuard {
  const scope = useServerScope();
  const [refreshToken, setRefreshToken] = useState<number>(0);
  const lastServerId = useRef<string | null>(null);

  useEffect(() => {
    if (scope.loading) return;
    if (scope.selected_server_id !== lastServerId.current) {
      lastServerId.current = scope.selected_server_id;
      // Server e' cambiato -> bump refresh token; i loader devono refetchare.
      setRefreshToken((t) => t + 1);
    }
  }, [scope.loading, scope.selected_server_id]);

  return {
    serverId: scope.selected_server_id,
    refreshToken,
    isReady: !scope.loading,
    bump: () => setRefreshToken((t) => t + 1),
    serverScopeRequired: true,
  };
}

// Helper deterministico (per smoke E2E / validator statici): assicura che
// la chiave di cache contenga sempre serverId esplicito e mai 's1' silente.
export function buildPlayableLoopCacheKey(serverId: string | null): string {
  if (!serverId || !String(serverId).trim()) {
    return 'playable_loop:NO_SERVER_SELECTED';
  }
  return `playable_loop:server=${serverId}`;
}

export async function clearPlayableLoopCacheKeys(): Promise<void> {
  // Best-effort: rimuove eventuali chiavi pl:server=* memorizzate (no-op se assenti).
  try {
    const keys = await AsyncStorage.getAllKeys();
    const targets = keys.filter((k) => k.startsWith('playable_loop:'));
    if (targets.length) await AsyncStorage.multiRemove(targets);
  } catch (_e) {
    // silent fail (safety net only).
  }
}

export default useServerSwitchRefreshGuard;

// Pack 108 — Playable Loop Consumer (componente di polish frontend).
//
// Mostra lo stato canonico per ogni surface (Home/Lobby/Daily/Tower/Shop/
// Forge/Rewards/Guild/Arena/PvP/Event). Default: il componente e' nascosto
// (`EXPO_PUBLIC_PLAYABLE_LOOP_MAP_UI_ENABLED=false`). Quando montato, usa
// `useServerSwitchRefreshGuard` per rifetchare al cambio server.
//
// SAFETY:
// - read-only;
// - nessun reward claim;
// - nessuna scrittura account-wide;
// - nessun fallback a 's1'.
import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, ScrollView } from 'react-native';
import useServerSwitchRefreshGuard, {
  buildPlayableLoopCacheKey,
} from '../utils/serverSwitchRefreshGuard';
import getPlayableLoopFlags, {
  statusCopy,
  PlayableLoopStatus,
} from '../utils/playableLoopFlags';

type SurfaceEntry = {
  status: PlayableLoopStatus | string;
  ui_flag: string;
  ui_flag_default_off: boolean;
  reward_live: boolean;
  server_scope_enforced: boolean;
  notes?: string;
  legacy_route_quarantined?: boolean;
};

type AlphaMap = {
  server_id: string;
  alpha_map_version: string;
  release_readiness_claimed: boolean;
  reward_live_general: boolean;
  no_silent_fallback_to_s1: boolean;
  surfaces: Record<string, SurfaceEntry>;
  copy_audit: Record<string, string | boolean>;
};

const API_BASE = (process.env.EXPO_PUBLIC_API_URL || '/api').replace(/\/$/, '');

export default function PlayableLoopConsumer() {
  const flags = getPlayableLoopFlags();
  const { serverId, refreshToken, isReady } = useServerSwitchRefreshGuard();
  const [map, setMap] = useState<AlphaMap | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!flags.playable_loop_map_ui_enabled) return;
    if (!isReady) return;
    if (!serverId || !String(serverId).trim()) {
      setError('NO_SERVER_SELECTED');
      setMap(null);
      return;
    }
    setLoading(true);
    setError(null);
    const cacheKey = buildPlayableLoopCacheKey(serverId);
    // (cacheKey non e' usato per memoize qui: lo serve solo come marker di
    // server-scope identity per i validator statici).
    void cacheKey;
    fetch(`${API_BASE}/playable-loop/map?server_id=${encodeURIComponent(serverId)}`)
      .then((r) => r.json())
      .then((j) => {
        setMap(j as AlphaMap);
      })
      .catch((e) => setError(String(e?.message || e)))
      .finally(() => setLoading(false));
  }, [flags.playable_loop_map_ui_enabled, isReady, serverId, refreshToken]);

  if (!flags.playable_loop_map_ui_enabled) {
    // Default OFF: componente non renderizzato.
    return null;
  }

  if (!serverId) {
    return (
      <View style={styles.container} testID="playable-loop-no-server">
        <Text style={styles.title}>Playable Loop (Alpha)</Text>
        <Text style={styles.error}>
          Nessun server selezionato. Seleziona un server (no silent fallback a s1).
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} testID="playable-loop-map">
      <Text style={styles.title}>Playable Loop (Alpha) — server: {serverId}</Text>
      {loading && <ActivityIndicator />}
      {error && <Text style={styles.error}>Errore: {error}</Text>}
      {map && (
        <View>
          <Text style={styles.sub}>
            release_readiness_claimed: {String(map.release_readiness_claimed)}
          </Text>
          <Text style={styles.sub}>
            reward_live_general: {String(map.reward_live_general)}
          </Text>
          {Object.entries(map.surfaces).map(([key, s]) => (
            <View key={key} style={styles.row} testID={`playable-loop-row-${key}`}>
              <Text style={styles.surfaceName}>{key}</Text>
              <Text style={styles.statusText}>{statusCopy(s.status)}</Text>
              <Text style={styles.flagText}>flag: {s.ui_flag} (default OFF)</Text>
              {s.legacy_route_quarantined && (
                <Text style={styles.quarantined}>Legacy quarantineata</Text>
              )}
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  sub: { fontSize: 12, color: '#666', marginBottom: 4 },
  row: {
    paddingVertical: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#ccc',
  },
  surfaceName: { fontSize: 14, fontWeight: '500' },
  statusText: { fontSize: 12, color: '#444' },
  flagText: { fontSize: 10, color: '#999' },
  quarantined: { fontSize: 10, color: '#a00' },
  error: { color: '#a00', marginVertical: 8 },
});

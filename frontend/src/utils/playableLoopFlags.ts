// Pack 108 — Playable Loop UI Flags (default OFF).
//
// Tutti i flag UI sensibili (Home/Lobby/Daily/Tower/Shop/Forge/Rewards/Guild/
// Arena/PvP/Event/PlayableLoopMap) sono default OFF. L'unico flag default ON
// e' `SERVER_SWITCH_REFRESH_GUARD_ENABLED` perche' garantisce che il cambio
// server invalidi lo stato locale (no silent fallback a s1).
//
// SAFETY:
// - nessun fetch live di reward;
// - nessuna scrittura account-wide;
// - nessun fallback a server_id='s1' silenzioso.

const TRUTHY = new Set(['true', '1', 'yes', 'on']);

function readEnvFlag(name: string, defaultValue: boolean = false): boolean {
  const raw = (process.env as Record<string, string | undefined>)[name];
  if (raw === undefined || raw === null || raw === '') return defaultValue;
  return TRUTHY.has(String(raw).trim().toLowerCase());
}

export type PlayableLoopFlags = {
  daily_claim_ui_enabled: boolean;
  daily_home_unlock: boolean;
  lobby_ui_enabled: boolean;
  tower_strict_ui_enabled: boolean;
  economy_strict_ui_enabled: boolean;
  forge_strict_ui_enabled: boolean;
  reward_center_ui_enabled: boolean;
  guild_ui_enabled: boolean;
  arena_ui_enabled: boolean;
  pvp_ui_enabled: boolean;
  event_ui_enabled: boolean;
  playable_loop_map_ui_enabled: boolean;
  server_switch_refresh_guard_enabled: boolean;
};

export function getPlayableLoopFlags(): PlayableLoopFlags {
  return {
    daily_claim_ui_enabled: readEnvFlag('EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED', false),
    daily_home_unlock: readEnvFlag('EXPO_PUBLIC_DAILY_HOME_UNLOCK', false),
    lobby_ui_enabled: readEnvFlag('EXPO_PUBLIC_LOBBY_UI_ENABLED', false),
    tower_strict_ui_enabled: readEnvFlag('EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED', false),
    economy_strict_ui_enabled: readEnvFlag('EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED', false),
    forge_strict_ui_enabled: readEnvFlag('EXPO_PUBLIC_FORGE_STRICT_UI_ENABLED', false),
    reward_center_ui_enabled: readEnvFlag('EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED', false),
    guild_ui_enabled: readEnvFlag('EXPO_PUBLIC_GUILD_UI_ENABLED', false),
    arena_ui_enabled: readEnvFlag('EXPO_PUBLIC_ARENA_UI_ENABLED', false),
    pvp_ui_enabled: readEnvFlag('EXPO_PUBLIC_PVP_UI_ENABLED', false),
    event_ui_enabled: readEnvFlag('EXPO_PUBLIC_EVENT_UI_ENABLED', false),
    playable_loop_map_ui_enabled: readEnvFlag('EXPO_PUBLIC_PLAYABLE_LOOP_MAP_UI_ENABLED', false),
    server_switch_refresh_guard_enabled: readEnvFlag('EXPO_PUBLIC_SERVER_SWITCH_REFRESH_GUARD_ENABLED', true),
  };
}

// Status canonici per UI copy audit (no false-ready labels).
export const PLAYABLE_LOOP_STATUS_COPY = {
  READY: 'Disponibile',
  READY_GATED: 'Disponibile in anteprima (server-scoped)',
  READY_GATED_DEFERRED: 'Anteprima (reward in preparazione)',
  DEFERRED: 'In preparazione (deferred)',
  LOCKED: 'Bloccato (Closed Alpha)',
  PREVIEW: 'Anteprima sola lettura',
  QUARANTINED: 'Route legacy in quarantena (server-scope retrofit in corso)',
};

export type PlayableLoopStatus = keyof typeof PLAYABLE_LOOP_STATUS_COPY;

export function statusCopy(status: PlayableLoopStatus | string): string {
  return (PLAYABLE_LOOP_STATUS_COPY as Record<string, string>)[status] || 'Stato sconosciuto';
}

// Sentinel: nessuna surface deve mai essere mostrata come READY se la sua
// `reward_live` lato server e' false. La logica helper aiuta a evitare
// false-ready label nei componenti.
export function isFalseReadyClaim(status: string, rewardLive: boolean | undefined): boolean {
  return status === 'READY' && rewardLive === false;
}

export default getPlayableLoopFlags;

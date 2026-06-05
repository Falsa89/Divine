// v107B — Pre-Battle Lobby Adapter.
// Bridges a generic mode-launch payload into a Battle Launch Contract v1 + POST /api/battle/launch.
// SAFETY: read-only against backend (preview echo), no DB writes, no reward grant.
import { buildLaunchContext, validateLaunchContext, BattleLaunchContractV1 } from '../buildLaunchContext';

export interface LobbyLaunchInput {
  server_id: string;
  mode: BattleLaunchContractV1['mode'];
  encounter_id: string;
  enemy_source_type: BattleLaunchContractV1['enemy_source_type'];
  enemy_source_id: string;
  player_team_id?: string | null;
  player_team_snapshot?: unknown[];
  client_trace_id?: string | null;
}

export interface LobbyLaunchResult {
  ok: boolean;
  contract: BattleLaunchContractV1 | null;
  response_status: number | null;
  preview_echo: unknown | null;
  errors: string[];
}

function backendBase(): string {
  const env = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
  return env.replace(/\/$/, '');
}

export async function launchFromLobby(input: LobbyLaunchInput): Promise<LobbyLaunchResult> {
  const contract = buildLaunchContext({
    server_id: input.server_id,
    mode: input.mode,
    encounter_id: input.encounter_id,
    enemy_source_type: input.enemy_source_type,
    enemy_source_id: input.enemy_source_id,
    player_team_id: input.player_team_id ?? null,
    player_team_snapshot: input.player_team_snapshot ?? [],
    reward_policy: 'preview',
    progress_policy: 'preview',
    battle_engine_mode: 'preview',
    idempotency_key: null,
    client_trace_id: input.client_trace_id ?? null,
  });
  const v = validateLaunchContext(contract);
  if (!v.ok) return { ok: false, contract, response_status: null, preview_echo: null, errors: v.errors };
  const base = backendBase();
  try {
    const res = await fetch(`${base}/api/battle/launch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contract),
    });
    const json = await res.json().catch(() => null);
    return { ok: res.ok, contract, response_status: res.status, preview_echo: json, errors: [] };
  } catch (e) {
    return { ok: false, contract, response_status: null, preview_echo: null, errors: [String(e)] };
  }
}

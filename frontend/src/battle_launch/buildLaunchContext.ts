// v107A — Battle Launch Contract v1 helper.
//
// Build & validate a launch_context payload to send to POST /api/battle/launch.
// Pure helper: no React state, no network calls, no DB.
//
// SAFETY:
// - reward_policy/progress_policy defaults to 'preview'
// - battle_engine_mode defaults to 'preview'
// - validateLaunchContext returns errors[] for shape violations

export type BattleMode =
  | 'story' | 'tower' | 'arena' | 'training' | 'boss' | 'raid'
  | 'event' | 'guild_war' | 'guild_raid' | 'world_boss';

export type EnemySourceType =
  | 'authored' | 'player_team' | 'bot_team' | 'boss' | 'training_preset' | 'event_preset';

export type RewardPolicy = 'none' | 'preview' | 'live_gated' | 'live';
export type ProgressPolicy = 'none' | 'preview' | 'live_gated' | 'live';
export type BattleEngineMode = 'preview' | 'authoritative';

export interface BattleLaunchContractV1 {
  server_id: string;
  mode: BattleMode;
  encounter_id: string;
  player_team_id: string | null;
  player_team_snapshot: unknown[];
  enemy_source_type: EnemySourceType;
  enemy_source_id: string;
  reward_policy: RewardPolicy;
  progress_policy: ProgressPolicy;
  battle_engine_mode: BattleEngineMode;
  idempotency_key: string | null;
  client_trace_id: string | null;
}

export interface BuildLaunchContextInput {
  server_id: string;
  mode: BattleMode;
  encounter_id: string;
  enemy_source_type: EnemySourceType;
  enemy_source_id: string;
  player_team_id?: string | null;
  player_team_snapshot?: unknown[];
  reward_policy?: RewardPolicy;
  progress_policy?: ProgressPolicy;
  battle_engine_mode?: BattleEngineMode;
  idempotency_key?: string | null;
  client_trace_id?: string | null;
}

const ALLOWED_MODES: BattleMode[] = [
  'story','tower','arena','training','boss','raid','event','guild_war','guild_raid','world_boss',
];
const ALLOWED_ENEMY_SOURCES: EnemySourceType[] = [
  'authored','player_team','bot_team','boss','training_preset','event_preset',
];

export function buildLaunchContext(input: BuildLaunchContextInput): BattleLaunchContractV1 {
  return {
    server_id: input.server_id,
    mode: input.mode,
    encounter_id: input.encounter_id,
    player_team_id: input.player_team_id ?? null,
    player_team_snapshot: input.player_team_snapshot ?? [],
    enemy_source_type: input.enemy_source_type,
    enemy_source_id: input.enemy_source_id,
    reward_policy: input.reward_policy ?? 'preview',
    progress_policy: input.progress_policy ?? 'preview',
    battle_engine_mode: input.battle_engine_mode ?? 'preview',
    idempotency_key: input.idempotency_key ?? null,
    client_trace_id: input.client_trace_id ?? null,
  };
}

export function validateLaunchContext(ctx: BattleLaunchContractV1): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  if (!ctx.server_id || ctx.server_id.length === 0) errors.push('server_id_required');
  if (!ALLOWED_MODES.includes(ctx.mode)) errors.push(`invalid_mode:${ctx.mode}`);
  if (!ctx.encounter_id || ctx.encounter_id.length === 0) errors.push('encounter_id_required');
  if (!ALLOWED_ENEMY_SOURCES.includes(ctx.enemy_source_type)) errors.push(`invalid_enemy_source_type:${ctx.enemy_source_type}`);
  if (!ctx.enemy_source_id || ctx.enemy_source_id.length === 0) errors.push('enemy_source_id_required');
  const needsIdem = ctx.reward_policy === 'live' || ctx.reward_policy === 'live_gated'
    || ctx.progress_policy === 'live' || ctx.progress_policy === 'live_gated';
  if (needsIdem && (!ctx.idempotency_key || ctx.idempotency_key.length === 0)) {
    errors.push('idempotency_key_required_for_live_gated_or_live');
  }
  return { ok: errors.length === 0, errors };
}

export function parseLaunchContextFromParams(params: Record<string, unknown>): BattleLaunchContractV1 | null {
  try {
    return buildLaunchContext({
      server_id: String(params.server_id ?? ''),
      mode: String(params.mode ?? 'training') as BattleMode,
      encounter_id: String(params.encounter_id ?? ''),
      enemy_source_type: String(params.enemy_source_type ?? 'training_preset') as EnemySourceType,
      enemy_source_id: String(params.enemy_source_id ?? ''),
      player_team_id: (params.player_team_id ?? null) as string | null,
      player_team_snapshot: (params.player_team_snapshot as unknown[]) ?? [],
      reward_policy: (params.reward_policy as RewardPolicy) ?? 'preview',
      progress_policy: (params.progress_policy as ProgressPolicy) ?? 'preview',
      battle_engine_mode: (params.battle_engine_mode as BattleEngineMode) ?? 'preview',
      idempotency_key: (params.idempotency_key as string | null) ?? null,
      client_trace_id: (params.client_trace_id as string | null) ?? null,
    });
  } catch {
    return null;
  }
}

export default buildLaunchContext;

/**
 * battleReplayTypes.ts — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PACK (v26)
 *
 * Tipi frontend-only per snapshot e timeline di replay.
 * NESSUNA mutazione. NESSUNA chiamata backend. NESSUN reward grant.
 */

import type { BattleReport } from './postBattleTypes';

export type BattleReplayOutcome = 'victory' | 'defeat';

export interface BattleReplayTimelineEntry {
  index: number;
  turn?: number;
  actor_name?: string;
  action_name?: string;
  target_names?: string[];
  damage?: number;
  healing?: number;
  is_critical?: boolean;
  raw_label: string;
}

export interface BattleReplaySafetyFlags {
  replay_mode: true;
  rewards_disabled: true;
  exp_disabled: true;
  grants_disabled: true;
  no_rng_rerun: true;
}

export interface BattleReplaySnapshotV1 {
  schema_version: 1;
  replay_id: string;
  created_at: string;
  local_only: true;
  server_synced: false;
  source: 'post_battle_summary';
  outcome: BattleReplayOutcome;
  headline?: string;
  turns: number;
  duration_sec: number;
  mvp_ally_name?: string;
  total_damage_dealt: number;
  total_damage_received: number;
  total_healing_done: number;
  battle_report: BattleReport;
  timeline: BattleReplayTimelineEntry[];
  safety: BattleReplaySafetyFlags;
}

export const BATTLE_REPLAY_SCHEMA_VERSION = 1 as const;
export const BATTLE_REPLAY_STORAGE_KEY = 'divinewaifus.saved_battle_replays.v1';
export const BATTLE_REPLAY_MAX_LOCAL = 20;

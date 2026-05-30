/**
 * battleReplayStorage.ts — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PACK
 *
 * Helper LOCAL-ONLY per salvare snapshot di replay su AsyncStorage.
 * NESSUNA chiamata backend. NESSUN reward grant. NESSUN token salvato.
 * Cap max 20 entries: evict oldest non-favorite first (favorite non implementato qui).
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { BattleReplaySnapshotV1 } from '../components/battle/battleReplayTypes';
import { BATTLE_REPLAY_STORAGE_KEY, BATTLE_REPLAY_MAX_LOCAL } from '../components/battle/battleReplayTypes';

export type SaveBattleReplayResult =
  | { status: 'saved'; replay_id: string; total: number }
  | { status: 'updated'; replay_id: string; total: number }
  | { status: 'failed'; error: string };

/**
 * Sanitize aggressivo: rimuove eventuali campi sensibili o claim state.
 * Manteniamo SOLO i campi già definiti nel tipo V1.
 */
function sanitize(snap: BattleReplaySnapshotV1): BattleReplaySnapshotV1 {
  return {
    schema_version: 1,
    replay_id: snap.replay_id,
    created_at: snap.created_at,
    local_only: true,
    server_synced: false,
    source: 'post_battle_summary',
    outcome: snap.outcome,
    headline: snap.headline,
    turns: snap.turns,
    duration_sec: snap.duration_sec,
    mvp_ally_name: snap.mvp_ally_name,
    total_damage_dealt: snap.total_damage_dealt,
    total_damage_received: snap.total_damage_received,
    total_healing_done: snap.total_healing_done,
    battle_report: snap.battle_report,
    timeline: snap.timeline,
    safety: {
      replay_mode: true,
      rewards_disabled: true,
      exp_disabled: true,
      grants_disabled: true,
      no_rng_rerun: true,
    },
  };
}

async function readAll(): Promise<BattleReplaySnapshotV1[]> {
  try {
    const raw = await AsyncStorage.getItem(BATTLE_REPLAY_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((x: unknown): x is BattleReplaySnapshotV1 =>
      !!x && typeof x === 'object' && (x as BattleReplaySnapshotV1).schema_version === 1
    );
  } catch {
    return [];
  }
}

export async function listSavedBattleReplays(): Promise<BattleReplaySnapshotV1[]> {
  return readAll();
}

export async function saveBattleReplay(snap: BattleReplaySnapshotV1): Promise<SaveBattleReplayResult> {
  try {
    const clean = sanitize(snap);
    const list = await readAll();
    const existingIdx = list.findIndex((s) => s.replay_id === clean.replay_id);
    if (existingIdx >= 0) {
      list[existingIdx] = clean;
      await AsyncStorage.setItem(BATTLE_REPLAY_STORAGE_KEY, JSON.stringify(list));
      return { status: 'updated', replay_id: clean.replay_id, total: list.length };
    }
    list.unshift(clean);
    // Cap: evict oldest (in fondo) prima
    while (list.length > BATTLE_REPLAY_MAX_LOCAL) {
      list.pop();
    }
    await AsyncStorage.setItem(BATTLE_REPLAY_STORAGE_KEY, JSON.stringify(list));
    return { status: 'saved', replay_id: clean.replay_id, total: list.length };
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'unknown_error';
    return { status: 'failed', error: msg };
  }
}

export async function clearSavedBattleReplays(): Promise<void> {
  try {
    await AsyncStorage.removeItem(BATTLE_REPLAY_STORAGE_KEY);
  } catch {
    /* graceful */
  }
}

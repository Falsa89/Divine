/**
 * buildBattleReplaySnapshot.ts — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PACK
 *
 * Builder PURO frontend-only: trasforma un PostBattleSummaryData in BattleReplaySnapshotV1.
 * NESSUNA chiamata backend, NESSUN RNG, NESSUN side effect.
 */
import type { PostBattleSummaryData, BattleReport, BattleStat } from '../components/battle/postBattleTypes';
import type {
  BattleReplaySnapshotV1,
  BattleReplayTimelineEntry,
} from '../components/battle/battleReplayTypes';
import { BATTLE_REPLAY_SCHEMA_VERSION } from '../components/battle/battleReplayTypes';

function sumDamageDealt(report: BattleReport): number {
  return (report.allies || []).reduce((acc: number, a: BattleStat) => acc + (a.damage_dealt || 0), 0);
}
function sumDamageReceived(report: BattleReport): number {
  return (report.allies || []).reduce((acc: number, a: BattleStat) => acc + (a.damage_received || 0), 0);
}
function sumHealing(report: BattleReport): number {
  return (report.allies || []).reduce((acc: number, a: BattleStat) => acc + (a.healing_done || 0), 0);
}
function findMvpName(report: BattleReport): string | undefined {
  if (!report.mvp_ally_id) return undefined;
  const m = (report.allies || []).find((a) => a.unit_id === report.mvp_ally_id);
  return m?.name;
}

/**
 * Costruisce una timeline best-effort dal battle_report. Se l'engine non passa
 * un battle_log nel summary, usiamo i battle stats per generare un timeline
 * informativo (no RNG, no recomputation).
 */
function buildTimelineFromReport(report: BattleReport): BattleReplayTimelineEntry[] {
  const entries: BattleReplayTimelineEntry[] = [];
  let idx = 0;
  for (const a of report.allies || []) {
    if ((a.damage_dealt || 0) > 0) {
      entries.push({
        index: idx++,
        actor_name: a.name,
        action_name: 'Danni complessivi',
        damage: a.damage_dealt,
        raw_label: `${a.name} ha inflitto ${a.damage_dealt} danni totali`,
      });
    }
    if ((a.healing_done || 0) > 0) {
      entries.push({
        index: idx++,
        actor_name: a.name,
        action_name: 'Cure complessive',
        healing: a.healing_done,
        raw_label: `${a.name} ha curato per ${a.healing_done} HP`,
      });
    }
    if (!a.survived) {
      entries.push({
        index: idx++,
        actor_name: a.name,
        action_name: 'KO',
        raw_label: `${a.name} è stato sconfitto`,
      });
    }
  }
  for (const e of report.enemies || []) {
    if ((e.damage_dealt || 0) > 0) {
      entries.push({
        index: idx++,
        actor_name: e.name,
        action_name: 'Danni nemici',
        damage: e.damage_dealt,
        raw_label: `${e.name} ha inflitto ${e.damage_dealt} danni`,
      });
    }
  }
  return entries;
}

function genReplayId(): string {
  const t = Date.now().toString(36);
  const r = Math.random().toString(36).slice(2, 8);
  return `replay_${t}_${r}`;
}

export function buildBattleReplaySnapshot(
  summary: PostBattleSummaryData,
  externalTimeline?: BattleReplayTimelineEntry[]
): BattleReplaySnapshotV1 {
  const report = summary.battle_report;
  const timeline = externalTimeline && externalTimeline.length > 0
    ? externalTimeline
    : buildTimelineFromReport(report);

  return {
    schema_version: BATTLE_REPLAY_SCHEMA_VERSION,
    replay_id: genReplayId(),
    created_at: new Date().toISOString(),
    local_only: true,
    server_synced: false,
    source: 'post_battle_summary',
    outcome: summary.outcome,
    headline: summary.headline,
    turns: summary.turns || 0,
    duration_sec: summary.duration_sec || 0,
    mvp_ally_name: findMvpName(report),
    total_damage_dealt: sumDamageDealt(report),
    total_damage_received: sumDamageReceived(report),
    total_healing_done: sumHealing(report),
    battle_report: report,
    timeline,
    safety: {
      replay_mode: true,
      rewards_disabled: true,
      exp_disabled: true,
      grants_disabled: true,
      no_rng_rerun: true,
    },
  };
}

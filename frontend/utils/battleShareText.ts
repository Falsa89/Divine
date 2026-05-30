/**
 * battleShareText.ts — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PACK
 *
 * Builder PURO frontend-only per share testuale del summary battaglia.
 * NESSUN URL. NESSUN share code. NESSUN user/account/token id.
 * NESSUNA chiamata backend.
 */
import type { PostBattleSummaryData, BattleReport, BattleStat } from '../components/battle/postBattleTypes';

function findMvpName(report: BattleReport): string {
  if (!report.mvp_ally_id) return 'sconosciuto';
  const m = (report.allies || []).find((a: BattleStat) => a.unit_id === report.mvp_ally_id);
  return m?.name || 'sconosciuto';
}
function sumDmg(report: BattleReport): number {
  return (report.allies || []).reduce((acc: number, a: BattleStat) => acc + (a.damage_dealt || 0), 0);
}
function sumHeal(report: BattleReport): number {
  return (report.allies || []).reduce((acc: number, a: BattleStat) => acc + (a.healing_done || 0), 0);
}

export function buildBattleShareText(summary: PostBattleSummaryData): string {
  const report = summary.battle_report;
  const mvp = findMvpName(report);
  const dmg = sumDmg(report);
  const heal = sumHeal(report);
  const turns = summary.turns || 0;
  const dur = Math.max(0, Math.round(summary.duration_sec || 0));
  const verb = summary.outcome === 'victory' ? 'Vittoria!' : 'Sconfitta.';
  return `Divine Waifus — ${verb} MVP: ${mvp}, Danni totali: ${dmg}, Cure: ${heal}, Turni: ${turns}, Durata: ${dur}s.`;
}

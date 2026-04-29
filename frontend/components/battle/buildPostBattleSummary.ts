/**
 * Post-Battle Summary — adapter/builder (v16.22 Foundation)
 * ─────────────────────────────────────────────────────────────────────
 * Converte il `result` object dell'API combat (formato esistente)
 * + lo state runtime di battaglia in un PostBattleSummaryData che la UI
 * sa come renderizzare.
 *
 * Le formule numeriche QUI sono SAMPLE/MOCK quando il backend non fornisce
 * dati reali (es. damage tracking per BattleStat). Il prompt del task
 * richiede architettura + UI foundation, NON balancing finale.
 *
 * Quando in futuro il backend esporrà damage_dealt / received / heal in
 * ogni char, basta sostituire i sample inside `buildBattleStats()`.
 */
import type {
  PostBattleSummaryData, RewardItem, HeroExpBreakdown, BattleStat, BattleReport,
} from './postBattleTypes';

// ─────────────────────────────────────────────────────────────────────
// REWARDS
// ─────────────────────────────────────────────────────────────────────
function buildRewards(result: any): PostBattleSummaryData['rewards'] {
  const r = result?.rewards || {};
  const auto: RewardItem[] = [];
  const manual: RewardItem[] = [];

  if (r.gold) auto.push({ type: 'gold', name: 'Oro', icon: '\uD83D\uDCB0', amount: r.gold });
  if (r.exp)  auto.push({ type: 'exp',  name: 'EXP Account', icon: '\u2728', amount: r.exp });
  if (r.gem)  auto.push({ type: 'gem',  name: 'Gemme', icon: '\uD83D\uDC8E', amount: r.gem, rarity: 'rare' });
  if (r.hero_exp && r.hero_exp > 0) {
    auto.push({ type: 'hero_exp', name: 'Hero EXP', icon: '\u2694\uFE0F', amount: r.hero_exp });
  }

  // drops are typically items / shards / equipment → important by rarity
  if (Array.isArray(r.drops)) {
    for (const d of r.drops) {
      const isImportant = ['legendary', 'epic', 'mythic'].includes(d.rarity);
      const item: RewardItem = {
        type: d.type || 'item',
        id: d.id,
        name: d.name || 'Oggetto',
        icon: d.icon || '\uD83C\uDF81',
        amount: d.quantity || 1,
        rarity: d.rarity,
        is_important: isImportant,
      };
      (isImportant ? manual : auto).push(item);
    }
  }

  return {
    auto_claim: auto,
    manual_claim: manual,
    expires_in_days: manual.length > 0 ? 7 : undefined,
    account_level_up: !!r.account_level_up,
    new_account_level: r.new_account_level,
  };
}

// ─────────────────────────────────────────────────────────────────────
// HERO EXP BREAKDOWN
// ─────────────────────────────────────────────────────────────────────
function buildHeroExp(result: any, teamA: any[]): HeroExpBreakdown[] {
  const totalHeroExp: number = result?.rewards?.hero_exp || 0;
  const levelups: any[] = result?.rewards?.hero_levelups || [];
  const lookup = new Map<string, any>(
    levelups.map(lu => [lu.user_hero_id || lu.hero_id, lu])
  );

  // Distribute hero_exp evenly across used (non-NPC, non-summon) team members.
  const usable = teamA.filter(c => !!c?.user_hero_id || !!c?.id);
  if (usable.length === 0) return [];

  const perHero = Math.max(1, Math.floor(totalHeroExp / usable.length));

  return usable.map(c => {
    const uid = c.user_hero_id || c.id;
    const lu = lookup.get(uid);
    const levelBefore = lu?.old_level ?? c.level ?? 1;
    const levelAfter  = lu?.new_level ?? c.level ?? levelBefore;
    const leveledUp = levelAfter > levelBefore;

    // SAMPLE: thresholds standard tipo (level * 100). Da sostituire quando
    // il backend esporrà exp/exp_to_next per user_hero.
    const expToNextBefore = Math.max(100, levelBefore * 100);
    const expToNextAfter  = Math.max(100, levelAfter  * 100);

    let expBefore: number;
    let expAfter: number;
    if (leveledUp) {
      // bar parte ~80% e crossa (sample). exp_after sul livello nuovo.
      expBefore = Math.floor(expToNextBefore * 0.8);
      expAfter  = Math.floor(expToNextAfter * 0.25);
    } else {
      expBefore = Math.floor(expToNextBefore * 0.45);
      expAfter  = Math.min(expToNextBefore, expBefore + perHero);
    }

    return {
      user_hero_id: uid,
      hero_id: c.hero_id || uid,
      name: c.name || c.hero_name || 'Hero',
      avatar: c.image || c.hero_image || undefined,
      rarity: c.rarity,
      element: c.element,
      level_before: levelBefore,
      level_after: levelAfter,
      exp_before: expBefore,
      exp_after: expAfter,
      exp_to_next_before: expToNextBefore,
      exp_to_next_after: expToNextAfter,
      exp_gained: perHero,
      leveled_up: leveledUp,
    };
  });
}

// ─────────────────────────────────────────────────────────────────────
// BATTLE STATS / REPORT
// ─────────────────────────────────────────────────────────────────────
/**
 * Builds BattleStat[] from teams. Backend non traccia ancora damage per unit
 * → SAMPLE values derivati in modo deterministico da rarity/level così che
 * unit più forti mostrino numeri più alti coerenti. Da sostituire quando
 * il backend esporrà damage tracking reale.
 */
function buildBattleStats(team: any[], side: 'ally' | 'enemy', mvpName?: string): {
  stats: BattleStat[];
  mvpId?: string;
} {
  const stats: BattleStat[] = team.map((c, idx) => {
    const rar = Math.max(1, Math.min(6, c.rarity || 3));
    const lvl = Math.max(1, c.level || 1);
    // SAMPLE deterministic numbers — multiplier base on rarity/level.
    const base = rar * 1500 + lvl * 60 + (idx * 73);
    const damage_dealt     = Math.round(base * (0.85 + (idx % 3) * 0.07));
    const damage_received  = Math.round(base * (0.55 + (idx % 4) * 0.06));
    const healing_done     = (c.role === 'support' || c.element === 'divine')
                              ? Math.round(base * 0.42)
                              : Math.round(base * 0.05);
    return {
      unit_id: c.user_hero_id || c.id || `${side}-${idx}`,
      name: c.name || c.hero_name || (side === 'enemy' ? 'Nemico' : 'Eroe'),
      avatar: c.image || c.hero_image || undefined,
      rarity: c.rarity,
      element: c.element,
      team: side,
      damage_dealt,
      damage_received,
      healing_done,
      survived: c.is_alive !== false,
    };
  });

  // MVP picker:
  //  - se backend ha già fornito un mvpName, prova match per name
  //  - altrimenti prendi il top damage_dealt
  let mvpId: string | undefined;
  if (mvpName) {
    const m = stats.find(s => s.name === mvpName);
    if (m) mvpId = m.unit_id;
  }
  if (!mvpId && stats.length > 0) {
    mvpId = stats.reduce((a, b) => (a.damage_dealt >= b.damage_dealt ? a : b)).unit_id;
  }
  return { stats, mvpId };
}

function buildBattleReport(result: any, teamA: any[], teamB: any[]): BattleReport {
  const allies  = buildBattleStats(teamA, 'ally',  result?.mvp);
  const enemies = buildBattleStats(teamB, 'enemy');
  return {
    allies: allies.stats,
    enemies: enemies.stats,
    mvp_ally_id: allies.mvpId,
    mvp_enemy_id: enemies.mvpId,
  };
}

// ─────────────────────────────────────────────────────────────────────
// PUBLIC ENTRY POINT
// ─────────────────────────────────────────────────────────────────────
export function buildPostBattleSummary(
  result: any,
  teamA: any[],
  teamB: any[],
  durationSec: number = 0,
): PostBattleSummaryData {
  return {
    outcome: result?.victory ? 'victory' : 'defeat',
    duration_sec: durationSec,
    turns: result?.turns ?? 0,
    headline: result?.stage_name || result?.headline || undefined,
    rewards: buildRewards(result),
    hero_exp: buildHeroExp(result, teamA),
    battle_report: buildBattleReport(result, teamA, teamB),
  };
}

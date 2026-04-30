/**
 * Post-Battle Summary — adapter/builder (v16.22 Foundation, v16.28 wired)
 * ─────────────────────────────────────────────────────────────────────
 * Converte il `result` object dell'API combat (formato esistente)
 * + lo state runtime di battaglia in un PostBattleSummaryData che la UI
 * sa come renderizzare.
 *
 * STATO DATI (v16.28 wiring):
 *  - REAL  → damage_dealt: viene da `team_a_final[i].damage_dealt` /
 *            `team_b_final[i].damage_dealt` (backend battle_engine.py
 *            traccia `total_damage_dealt` per char, increment a ogni hit
 *            in 455+462; esposto a riga 384-385). Combat.tsx popola
 *            teamA/teamB dai final → il valore arriva intatto qui.
 *  - REAL  → mvp ally:    backend `result.mvp` è il NAME dell'eroe top
 *            damage_dealt del team_a (battle_engine.py:386). Solo
 *            valorizzato in caso di victory; altrimenti null/None.
 *  - REAL  → mvp enemy:   backend non lo espone direttamente, ma
 *            calcolarlo dal `damage_dealt` reale degli enemy ora è
 *            altrettanto reale (top-damage del team_b).
 *  - MOCK  → damage_received: backend NON traccia ancora un counter
 *            `total_damage_received`. Placeholder deterministico finché
 *            non arriva.
 *  - MOCK  → healing_done: backend NON traccia ancora un counter
 *            `total_healing_done`. Placeholder deterministico finché
 *            non arriva.
 *  - MOCK  → exp_to_next per user_hero (curve formali). Backend
 *            persiste level/exp ma non espone exp/exp_to_next al
 *            payload di battle. Placeholder formula `level * 100`.
 *
 * TODO (TASK 4.4-C): Replace when backend exposes damage_received and
 * healing_done counters. Update this file ONLY then.
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
 * Mock fallback ONLY for fields the backend does not yet track.
 * Deterministic by rarity/level/idx so unit più forti mostrino numeri
 * più alti coerenti tra runs della stessa battaglia.
 *
 * TODO: Replace when backend exposes damage_received and healing_done counters.
 * (See battle_engine.py — `total_damage_dealt` already exists per char on
 * line 217/455/462; equivalent counters per damage_received/healing_done
 * are NOT implemented yet.)
 */
function getMockBattleStatsFallback(c: any, idx: number): {
  damage_dealt_fallback: number;
  damage_received_mock: number;
  healing_done_mock: number;
} {
  const rar = Math.max(1, Math.min(6, c.rarity || 3));
  const lvl = Math.max(1, c.level || 1);
  const base = rar * 1500 + lvl * 60 + (idx * 73);
  return {
    // Fallback only: used solo se il payload non ha damage_dealt numerico
    // (caso storico / backend che non passa team_*_final).
    damage_dealt_fallback: Math.round(base * (0.85 + (idx % 3) * 0.07)),
    // MOCK: backend non traccia damage_received per unit ancora.
    damage_received_mock:  Math.round(base * (0.55 + (idx % 4) * 0.06)),
    // MOCK: backend non traccia healing_done per unit ancora.
    healing_done_mock:    (c.role === 'support' || c.element === 'divine')
                            ? Math.round(base * 0.42)
                            : Math.round(base * 0.05),
  };
}

/**
 * Builds BattleStat[] from teams.
 *
 * v16.28 wiring:
 *  - REAL damage_dealt da `c.damage_dealt` (popolato da team_*_final).
 *  - MOCK damage_received / healing_done finché backend non espone counter.
 *  - MVP: prima prova match per `mvpName` (string nome) dal backend
 *    (esiste solo per ally team, e solo se victory). Fallback: top-damage
 *    della squadra — ora è un fallback REALE perché damage_dealt è reale.
 */
function buildBattleStats(team: any[], side: 'ally' | 'enemy', mvpName?: string): {
  stats: BattleStat[];
  mvpId?: string;
} {
  const stats: BattleStat[] = team.map((c, idx) => {
    const fallback = getMockBattleStatsFallback(c, idx);
    // REAL: consuma damage_dealt dal payload server (team_a_final/team_b_final).
    // 0 è un valore REALE valido (unit che non ha mai colpito) → check di tipo,
    // NON falsy check. Solo se il campo è proprio assente/non numerico,
    // si ricade sul deterministico fallback.
    const damage_dealt: number =
      typeof c.damage_dealt === 'number'
        ? c.damage_dealt
        : fallback.damage_dealt_fallback;

    return {
      unit_id: c.user_hero_id || c.id || `${side}-${idx}`,
      name: c.name || c.hero_name || (side === 'enemy' ? 'Nemico' : 'Eroe'),
      avatar: c.image || c.hero_image || undefined,
      rarity: c.rarity,
      element: c.element,
      team: side,
      damage_dealt,
      // MOCK fields (placeholder until backend tracking lands):
      damage_received: fallback.damage_received_mock,
      healing_done:    fallback.healing_done_mock,
      survived: c.is_alive !== false,
    };
  });

  // MVP picker:
  //  1) Se backend ha già fornito mvpName (stringa name dell'eroe top
  //     damage_dealt), prova match esatto per name.
  //  2) Match fallback per id/user_hero_id nel caso il backend in futuro
  //     passasse l'mvp come id invece che name (best-effort).
  //  3) Fallback finale: top damage_dealt della squadra. Ora è un fallback
  //     REALE perché damage_dealt è popolato dal payload server.
  let mvpId: string | undefined;
  if (mvpName) {
    const m = stats.find(s => s.name === mvpName);
    if (m) mvpId = m.unit_id;
    else {
      // Fallback only: backend MVP missing or could not be matched by name.
      // Try matching by raw unit id (in case backend evolves to send id).
      const byId = stats.find(s => s.unit_id === mvpName);
      if (byId) mvpId = byId.unit_id;
    }
  }
  if (!mvpId && stats.length > 0) {
    // Fallback only: nessun mvpName ricevuto (es. defeat → backend mvp=null,
    // oppure team enemy per cui backend non espone mvp). Ora il top-damage
    // riflette dati REALI di damage_dealt.
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

/**
 * Post-Battle Summary — adapter/builder (v16.22 Foundation, v16.28+v16.29 wired)
 * ─────────────────────────────────────────────────────────────────────
 * Converte il `result` object dell'API combat (formato esistente)
 * + lo state runtime di battaglia in un PostBattleSummaryData che la UI
 * sa come renderizzare.
 *
 * STATO DATI (v16.29 wiring):
 *  - REAL  → damage_dealt:    da `team_*_final[i].damage_dealt`
 *            (battle_engine.py 217 init total_damage_dealt, 455+462 increment).
 *  - REAL  → damage_received: da `team_*_final[i].damage_received`
 *            (v16.29 — battle_engine.py 218-225 init total_damage_received,
 *            increment per HP-actual delta nei punti damage application:
 *            AoE skill, single target, DoT). Capped a HP rimanenti per
 *            evitare overkill.
 *  - REAL  → healing_done:    da `team_*_final[i].healing_done`
 *            (v16.29 — battle_engine.py increment per HP-actual delta nei
 *            punti heal application: passive heal_per_turn). Capped a
 *            max_hp_battle per evitare overheal.
 *  - REAL  → mvp ally:        backend `result.mvp` = name dell'eroe top
 *            damage_dealt del team_a (battle_engine.py:386), valorizzato
 *            solo in caso di victory.
 *  - REAL  → mvp enemy:       calcolato sul damage_dealt reale del team_b
 *            (top-damage). Backend non lo espone direttamente.
 *  - MOCK  → exp_to_next:     curve formali per user_hero. Backend
 *            persiste level/exp ma non espone exp/exp_to_next nel battle
 *            payload. Placeholder formula `level * 100`.
 *
 * FALLBACK fields (kept solo per legacy payloads / variant senza counter):
 *  damage_dealt_fallback, damage_received_mock, healing_done_mock —
 *  usati esclusivamente quando il payload non contiene il campo numerico.
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
 * Mock fallback ONLY for legacy payloads where backend counters are missing.
 * Deterministic by rarity/level/idx so unit più forti mostrino numeri
 * più alti coerenti tra runs della stessa battaglia.
 *
 * v16.29: backend ora traccia total_damage_dealt + total_damage_received
 * + total_healing_done per char (battle_engine.py). I campi sotto sono
 * usati SOLO se il payload non contiene il valore numerico atteso (es.
 * vecchi payload pre-v16.29 in cache, o flussi che non passano
 * team_*_final).
 */
function getMockBattleStatsFallback(c: any, idx: number): {
  damage_dealt_fallback: number;
  damage_received_fallback: number;
  healing_done_fallback: number;
} {
  const rar = Math.max(1, Math.min(6, c.rarity || 3));
  const lvl = Math.max(1, c.level || 1);
  const base = rar * 1500 + lvl * 60 + (idx * 73);
  return {
    // Fallback only for legacy payloads where backend counters are missing.
    damage_dealt_fallback:    Math.round(base * (0.85 + (idx % 3) * 0.07)),
    damage_received_fallback: Math.round(base * (0.55 + (idx % 4) * 0.06)),
    healing_done_fallback:   (c.role === 'support' || c.element === 'divine')
                              ? Math.round(base * 0.42)
                              : Math.round(base * 0.05),
  };
}

/**
 * Builds BattleStat[] from teams.
 *
 * v16.29 wiring:
 *  - REAL damage_dealt    da `c.damage_dealt`    (team_*_final).
 *  - REAL damage_received da `c.damage_received` (team_*_final).
 *  - REAL healing_done    da `c.healing_done`    (team_*_final).
 *  - MVP: prima prova match per `mvpName` (string nome) dal backend
 *    (esiste solo per ally team, e solo se victory). Fallback: top-damage
 *    della squadra — ora è un fallback REALE perché damage_dealt è reale.
 *
 * Type-safe checks (typeof === 'number') per gestire correttamente il
 * caso 0 (real value valido per unit che non ha mai colpito/subito/curato).
 */
function buildBattleStats(team: any[], side: 'ally' | 'enemy', mvpName?: string): {
  stats: BattleStat[];
  mvpId?: string;
} {
  const stats: BattleStat[] = team.map((c, idx) => {
    const fallback = getMockBattleStatsFallback(c, idx);
    // REAL values — type-safe consumption (0 is valid).
    const damage_dealt: number =
      typeof c.damage_dealt === 'number'
        ? c.damage_dealt
        : fallback.damage_dealt_fallback;
    const damage_received: number =
      typeof c.damage_received === 'number'
        ? c.damage_received
        : fallback.damage_received_fallback;
    const healing_done: number =
      typeof c.healing_done === 'number'
        ? c.healing_done
        : fallback.healing_done_fallback;

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

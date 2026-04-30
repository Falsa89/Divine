/**
 * Divine Waifus — Reward Table static catalog (foundation)
 * ──────────────────────────────────────────────────────────────────
 * PLACEHOLDER ONLY — not final tuning.
 * Values are intentionally small/round to make their placeholder nature
 * obvious. Replace with real curves only when balance is approved.
 */
import type { RewardTable, RewardItem } from '../types/rewards';

// Helper inline factories to keep tables compact and self-documenting.
const gold = (n: number, source?: any): RewardItem => ({ id: `currency:gold:${n}`,            itemType: 'currency', itemId: 'gold',            amount: n, source });
const crystals = (n: number, source?: any): RewardItem => ({ id: `currency:dc:${n}`,          itemType: 'currency', itemId: 'divine_crystals', amount: n, source });
const seal = (n: number, source?: any): RewardItem => ({ id: `currency:seal:${n}`,            itemType: 'currency', itemId: 'summon_seal',     amount: n, source });
const honor = (n: number, source?: any): RewardItem => ({ id: `currency:honor:${n}`,          itemType: 'currency', itemId: 'honor_marks',     amount: n, source });
const banner = (n: number, source?: any): RewardItem => ({ id: `currency:banner:${n}`,        itemType: 'currency', itemId: 'war_banners',     amount: n, source });
const expHero = (n: number, source?: any): RewardItem => ({ id: `hero_exp:${n}`,              itemType: 'hero_exp', amount: n, source });
const expAcct = (n: number, source?: any): RewardItem => ({ id: `account_exp:${n}`,           itemType: 'account_exp', amount: n, source });
const mat = (matId: string, n: number): RewardItem  => ({ id: `material:${matId}:${n}`,      itemType: 'material', itemId: matId,             amount: n });

export const REWARD_TABLES: Record<string, RewardTable> = {
  // ─── STORY ────────────────────────────────────────────────────────
  story_stage_reward_placeholder: {
    id: 'story_stage_reward_placeholder',
    guaranteedRewards: [gold(500, 'battle_repeat'), expAcct(50, 'battle_repeat'), expHero(100, 'battle_repeat')],
    firstClearRewards:  [crystals(50, 'battle_first_clear')],
    repeatRewards:      [gold(250, 'battle_repeat')],
    accountExpReward: 50,
    heroExpReward: 100,
  },
  story_milestone_reward_placeholder: {
    id: 'story_milestone_reward_placeholder',
    milestoneRewards: [crystals(200, 'milestone'), seal(1, 'milestone'), expAcct(500, 'milestone')],
  },

  // ─── AFK / INSTANT ────────────────────────────────────────────────
  afk_autobattle_reward_placeholder: {
    id: 'afk_autobattle_reward_placeholder',
    afkRewards: [gold(120, 'afk_accumulation'), expHero(20, 'afk_accumulation'), expAcct(10, 'afk_accumulation')],
    accountExpReward: 10,
    heroExpReward: 20,
  },
  instant_autobattle_reward_placeholder: {
    id: 'instant_autobattle_reward_placeholder',
    guaranteedRewards: [gold(800, 'battle_repeat'), expHero(150, 'battle_repeat')],
    accountExpReward: 30,
    heroExpReward: 150,
  },

  // ─── TRIALS ───────────────────────────────────────────────────────
  trial_exp_reward_placeholder: {
    id: 'trial_exp_reward_placeholder',
    guaranteedRewards: [{ id: 'consumable:major_exp_tome:1', itemType: 'consumable', itemId: 'major_exp_tome', amount: 1 }, { id: 'consumable:medium_exp_tome:3', itemType: 'consumable', itemId: 'medium_exp_tome', amount: 3 }],
  },
  trial_ascension_reward_placeholder: {
    id: 'trial_ascension_reward_placeholder',
    guaranteedRewards: [mat('major_ascension_stone', 1), mat('medium_ascension_stone', 3)],
  },
  trial_elemental_reward_placeholder: {
    id: 'trial_elemental_reward_placeholder',
    guaranteedRewards: [mat('fire_essence', 5)], // rotation handled at runtime
    possibleDrops: [mat('water_essence', 5), mat('earth_essence', 5), mat('wind_essence', 5)],
  },
  trial_gold_reward_placeholder: {
    id: 'trial_gold_reward_placeholder',
    guaranteedRewards: [gold(5000, 'battle_repeat')],
  },

  // ─── PVP / GUILD ──────────────────────────────────────────────────
  arena_reward_placeholder: {
    id: 'arena_reward_placeholder',
    guaranteedRewards: [honor(50, 'battle_victory'), gold(300, 'battle_victory')],
    rankingRewards:    [honor(500, 'ranking'), crystals(100, 'ranking'), seal(1, 'ranking')],
  },
  guild_live_reward_placeholder: {
    id: 'guild_live_reward_placeholder',
    guaranteedRewards: [banner(50, 'guild'), gold(500, 'guild')],
    rankingRewards:    [banner(800, 'guild'), crystals(150, 'guild')],
  },

  // ─── EVENTS ───────────────────────────────────────────────────────
  event_minor_reward_placeholder: {
    id: 'event_minor_reward_placeholder',
    guaranteedRewards: [gold(200, 'event'), { id: 'currency:event:10', itemType: 'currency', itemId: 'event_currency_placeholder', amount: 10 }],
  },
  event_normal_reward_placeholder: {
    id: 'event_normal_reward_placeholder',
    guaranteedRewards: [gold(500, 'event'), { id: 'currency:event:25', itemType: 'currency', itemId: 'event_currency_placeholder', amount: 25 }, expHero(80, 'event')],
  },
  event_major_reward_placeholder: {
    id: 'event_major_reward_placeholder',
    guaranteedRewards: [gold(1500, 'event'), crystals(50, 'event'), { id: 'currency:event_seal:1', itemType: 'currency', itemId: 'event_summon_seal', amount: 1 }],
    milestoneRewards:  [crystals(300, 'event_milestone'), { id: 'currency:limited_seal:1', itemType: 'currency', itemId: 'limited_summon_seal', amount: 1 }],
  },

  // ─── ENDGAME ──────────────────────────────────────────────────────
  tower_reward_placeholder: {
    id: 'tower_reward_placeholder',
    guaranteedRewards: [gold(400, 'battle_first_clear'), expHero(200, 'battle_first_clear')],
    milestoneRewards:  [crystals(150, 'milestone'), mat('refined_forge_ore', 2)],
    rankingRewards:    [crystals(500, 'ranking')],
  },
  artifact_material_reward_placeholder: {
    id: 'artifact_material_reward_placeholder',
    guaranteedRewards: [mat('artifact_dust', 3)],
    possibleDrops:     [mat('artifact_core', 1)],
  },
  rune_gem_reward_placeholder: {
    id: 'rune_gem_reward_placeholder',
    guaranteedRewards: [mat('rune_fragment', 5)],
    possibleDrops:     [mat('rune_core', 1)],
  },
};

/** Lookup helper. */
export function getRewardTable(id: string): RewardTable | undefined {
  return REWARD_TABLES[id];
}

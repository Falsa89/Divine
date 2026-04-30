/**
 * Divine Waifus — Centralized Reward Type Contracts (foundation)
 * ───────────────────────────────────────────────────────────────
 * SCOPE: shared contract for any reward shown/awarded across the app:
 *   battle results, mailbox, shop bundles, daily login, ranking,
 *   afk accumulation, milestone clears, ranking podiums, chest grants.
 *
 * TODO (post-foundation): bridge or migrate `components/battle/postBattleTypes.ts`
 * (RewardItem, HeroExpBreakdown) into this shared contract. Today both
 * coexist intentionally — the post-battle types mirror the legacy
 * backend payload shape (snake_case fields) and are tightly coupled to
 * `PostBattleSummary.tsx`. We will not touch them in this task.
 */

import type { CurrencyId } from './economy';

export type RewardItemType =
  | 'currency'
  | 'material'
  | 'equipment'
  | 'artifact'
  | 'hero_exp'
  | 'account_exp'
  | 'chest'
  | 'consumable';

export type RewardSourceType =
  | 'battle_victory'
  | 'battle_first_clear'
  | 'battle_repeat'
  | 'mailbox'
  | 'daily_login'
  | 'shop_purchase'
  | 'gacha'
  | 'milestone'
  | 'ranking'
  | 'chest_open'
  | 'afk_accumulation'
  | 'event'
  | 'guild'
  | 'achievement'
  | 'sanctuary'
  | 'system';

/**
 * One single reward atom.
 * For currency rewards `itemId` MUST be a CurrencyId (e.g. 'gold').
 * For materials/equipment/artifacts/consumables, `itemId` is the catalog id.
 * For hero_exp/account_exp the `itemId` may be omitted; `amount` is the EXP.
 * For chest the `itemId` is the chest catalog id; opening yields nested rewards.
 */
export interface RewardItem {
  /** Unique id for animation keys / analytics. UUID or `${itemType}:${itemId}` */
  id: string;
  itemType: RewardItemType;
  /** Catalog id of the awarded thing. snake_case. May be undefined for *_exp. */
  itemId?: string | CurrencyId;
  /** Quantity awarded. For exp this is total EXP gained. */
  amount: number;
  /** Optional display name override (else look up in catalog). */
  name?: string;
  /** Optional rarity 1..6 for visual treatment. */
  rarity?: number;
  /** Optional icon glyph / asset / emoji override. */
  icon?: string;
  /** Sub-rewards for chest type or aggregated bundles. */
  contents?: RewardItem[];
  /** True if this item is granted automatically (no claim needed). */
  autoClaimed?: boolean;
  /** Where this reward came from (analytics/UI labelling). */
  source?: RewardSourceType;
  /** Optional hero_id to which a hero_exp reward applies. */
  heroId?: string;
  /** Optional user_hero_id (instance) to which a hero_exp reward applies. */
  userHeroId?: string;
  /** Optional notes for UI tooltip. */
  notes?: string;
}

/**
 * Reward Table for any mode/encounter/event.
 * All buckets are independent and optional — populate only what applies.
 */
export interface RewardTable {
  /** Stable id for the table; useful for cross-references. */
  id: string;
  /** Always granted upon completion. */
  guaranteedRewards?: RewardItem[];
  /** Drops with weighted probability (resolved server-side). */
  possibleDrops?: RewardItem[];
  /** First clear bonus (lifetime, per account/hero). */
  firstClearRewards?: RewardItem[];
  /** Granted on subsequent clears (after first). */
  repeatRewards?: RewardItem[];
  /** Score/progress milestones (e.g. tower floor 10/20/...). */
  milestoneRewards?: RewardItem[];
  /** PvP/Arena/Tower ranking podium rewards. */
  rankingRewards?: RewardItem[];
  /** Chest contents preview (for chest_open sources). */
  chestRewards?: RewardItem[];
  /** AFK pool accumulation per hour/per cycle. */
  afkRewards?: RewardItem[];
  /** Aggregated account EXP reward shortcut. */
  accountExpReward?: number;
  /** Aggregated hero EXP reward (split by backend across team). */
  heroExpReward?: number;
}

/**
 * UI-friendly aggregated preview (used in mode select / shop tooltip).
 * Renders a compact list without revealing probabilities.
 */
export interface RewardPreview {
  tableId: string;
  guaranteed: RewardItem[];
  /** Bullet items like 'Possibili: 3-5 frammenti raro' (display strings). */
  possibleSummaries: string[];
  /** Whether ranking rewards exist for this mode (UI hint). */
  hasRanking: boolean;
  /** Whether the user is locked out by daily/weekly entry limits. */
  isLocked?: boolean;
}

/**
 * Server response contract for claim endpoints (mailbox, milestone, etc.).
 * Mirrors the typical FastAPI shape: `{ success, rewards, errors }`.
 */
export interface RewardClaimResult {
  success: boolean;
  /** Final reward atoms granted to the player wallet. */
  rewards: RewardItem[];
  /** Optional updated balances snapshot for UI refresh hint. */
  newBalances?: Record<string, number>;
  /** Server-side claim id (idempotency key). */
  claimId?: string;
  /** Localized error message if success=false. */
  error?: string;
}

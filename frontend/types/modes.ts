/**
 * Divine Waifus — Centralized Game Mode Type Contracts (foundation)
 * ──────────────────────────────────────────────────────────────────
 * SCOPE: shared contract for any progression/PvE/PvP/social/event mode.
 *
 * IMPORTANT:
 *  - This file does NOT refactor existing screens (story.tsx, tower.tsx,
 *    pvp.tsx, gvg.tsx, raids.tsx, sanctuary.tsx, etc.).
 *  - Mode IDs MUST be snake_case (e.g. 'story', 'tower_of_infinity').
 *  - `prototype` modes can be hidden from UI via `isVisibleInUI=false`.
 */

import type { CurrencyId } from './economy';

export type ModeCategory =
  | 'pve'
  | 'pvp'
  | 'social'
  | 'event'
  | 'progression'
  | 'idle';

export type ModeFamily =
  | 'story'
  | 'tower'
  | 'arena'
  | 'gvg'
  | 'raid'
  | 'sanctuary'
  | 'afk'
  | 'training'
  | 'co_op'
  | 'world_boss'
  | 'void_region'
  | 'cross_server'
  | 'event_dungeon'
  | 'gacha'
  | 'forge_quest'
  | 'misc';

export type ResetType =
  | 'never'
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'season'
  | 'event_window';

/**
 * High-level static definition of a mode.
 * Store catalog separately (e.g. `frontend/data/modes.ts` later).
 */
export interface ModeDefinition {
  /** snake_case id, e.g. 'tower_of_infinity'. Stable. */
  id: string;
  /** Display name (i18n-ready). */
  name: string;
  category: ModeCategory;
  family: ModeFamily;
  /** Short description for mode-select tooltip. */
  description: string;
  /** Account level required to unlock the mode (UI gating). */
  unlockAccountLevel?: number;
  /** Story stage required to unlock the mode (alternate gating). */
  unlockStoryStage?: number;
  /** Whether the mode can be replayed multiple times. */
  isRepeatable: boolean;
  /** True if entries/day or entries/week apply. */
  hasEntryLimit: boolean;
  /** True if attempts/run apply (per-stage). */
  hasAttemptLimit: boolean;
  /** Base entry count per cycle (when `hasEntryLimit`). */
  baseEntries?: number;
  /** Base attempt count per stage/run (when `hasAttemptLimit`). */
  baseAttempts?: number;
  /** True if extra entries can be purchased. */
  allowsExtraEntries?: boolean;
  /** Currency used to buy extra entries (e.g. 'divine_crystals'). */
  extraEntryCurrency?: CurrencyId;
  /** Placeholder hook for future VIP rules. */
  vipExtraRulesPlaceholder?: boolean;
  /** Reward table id (resolves to a RewardTable definition). */
  rewardTableId?: string;
  /** Milestone table id (e.g. tower floor milestones). */
  milestoneTableId?: string;
  /** Optional shop attached to the mode (e.g. honor shop). */
  shopId?: string;
  /** Primary currency earned by the mode (display hint). */
  currencyId?: CurrencyId;
  /** Whether the mode contributes to a ranking. */
  hasRanking?: boolean;
  /** Whether the mode runs only inside a live window. */
  hasLiveWindow?: boolean;
  /** Live window definition id (resolves to LiveWindowDefinition). */
  liveWindowId?: string;
  /** True if implementation exists (foundation/prototype). */
  isPrototypeEnabled: boolean;
  /** True if the user can see/access the mode in the current build. */
  isVisibleInUI: boolean;
  /** True if the mode is just a placeholder (no real backend yet). */
  isPlaceholder?: boolean;
}

/**
 * Per-mode entry/attempt rules. Keeps refresh logic data-driven.
 */
export interface EntryRule {
  modeId: string;
  /** How many entries a user gets per day (overrides ModeDefinition.baseEntries). */
  dailyEntries?: number;
  /** How many entries a user gets per week. */
  weeklyEntries?: number;
  /** Number of attempts per entry (when hasAttemptLimit). */
  attempts?: number;
  /** Of those attempts, how many count toward ranking score. */
  rankingAttempts?: number;
  /** Of those attempts, how many give rewards (vs free practice). */
  rewardedAttempts?: number;
  /** Cap on extra entries purchasable per cycle. */
  extraPurchaseLimit?: number;
  /** Currency used for extra purchase. */
  extraPurchaseCurrency?: CurrencyId;
  /** Optional ticket item id used in lieu of currency. */
  extraTicketItem?: string;
  /** Reserved for future VIP overrides (no behavior here). */
  vipRulesPlaceholder?: boolean;
  /** UTC time-of-day for reset (HH:MM). */
  resetTime?: string;
  resetType: ResetType;
  /** True if attempts here affect a ranking leaderboard. */
  isRankingAffected?: boolean;
}

/**
 * Live window definition (e.g. event period, season).
 * Used for time-gated modes.
 */
export interface LiveWindowDefinition {
  id: string;
  name: string;
  /** ISO datetime, inclusive. */
  startsAt: string;
  /** ISO datetime, exclusive. */
  endsAt: string;
  /** Server timezone hint (default UTC). */
  timezone?: string;
  /** Optional notice/banner key. */
  bannerKey?: string;
  /** True if currently active (computed; populate at runtime). */
  isActive?: boolean;
}

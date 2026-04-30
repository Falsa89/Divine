/**
 * Divine Waifus — Battle Statistics Type Contracts (foundation)
 * ──────────────────────────────────────────────────────────────
 * SCOPE: shared contract for per-unit and per-team battle stats.
 *
 * IMPORTANT:
 *  - This file does NOT wire into the existing BattleReport / PostBattleSummary.
 *  - It does NOT change `components/battle/buildPostBattleSummary.ts`.
 *  - The existing `components/battle/postBattleTypes.ts` mirrors the backend
 *    payload (snake_case fields) and is tightly coupled to the rendered
 *    `<BattleReport>`. We will keep both in parallel until a future migration.
 *  - Recommended next step (separate task): wire real `damage_dealt` and
 *    `mvp` from `team_a_final[]`/`mvp` server fields into the existing
 *    `buildPostBattleSummary.ts`. This file does not perform that wiring.
 */

export type BattleSide = 'ally' | 'enemy';

/**
 * Per-unit battle metrics. All fields are optional except identity, so
 * partial data (e.g. only damage_dealt available today) is representable.
 *
 * Field names are camelCase here (TS-side contract). Adapters from the
 * snake_case backend payload should translate explicitly when bridging.
 */
export interface BattleUnitStats {
  /** Server-issued user_hero_id or temporary battle id. */
  unitId: string;
  /** Hero catalog id (e.g. 'greek_hoplite'). Useful for asset resolution. */
  heroId?: string;
  /** Localized display name. */
  displayName: string;
  /** Avatar source: remote URL OR local sentinel (`asset:greek_hoplite:*`). */
  avatar?: string;
  /** Side the unit fought on. */
  side: BattleSide;
  /** Star rating / rarity tier 1..6. */
  rarity?: number;
  /** Element tag (snake_case). */
  element?: string;
  /** Faction/clan tag (snake_case). */
  faction?: string;
  /** Total damage dealt by this unit. REAL from backend (battle_engine.py). */
  damageDealt?: number;
  /** Total damage taken by this unit. NOT yet tracked server-side. */
  damageTaken?: number;
  /** Total healing performed (own or allies). NOT yet tracked server-side. */
  healingDone?: number;
  /** Number of enemy KOs credited. */
  kills?: number;
  /** Whether the unit survived to the end of the battle. */
  survived?: boolean;
  /** Whether this unit was crowned MVP for its side. */
  isMvp?: boolean;
  /** Optional grid coordinates for tactical view. */
  gridX?: number;
  gridY?: number;
}

/**
 * Aggregated battle stats grouped by side, with optional MVP shortcuts.
 */
export interface BattleStats {
  ally: BattleUnitStats[];
  enemy: BattleUnitStats[];
  /** Direct shortcut to the ally MVP id (resolved against ally[]). */
  allyMvpId?: string;
  /** Direct shortcut to the enemy MVP id (resolved against enemy[]). */
  enemyMvpId?: string;
}

/**
 * Top-level summary used by the (future) shared Battle Report layer.
 * Existing `<BattleReport>` continues to consume the legacy contract
 * defined in `components/battle/postBattleTypes.ts` until migration.
 */
export interface BattleReportSummary {
  /** Whether the battle was won by the ally side. */
  victory: boolean;
  /** Total turns elapsed. */
  turns?: number;
  /** Battle duration in seconds (if backend exposes it; otherwise undefined). */
  durationSec?: number;
  /** Per-unit + per-side stats. */
  stats: BattleStats;
  /** Mode id for analytics/UI hints. */
  modeId?: string;
  /** Stage id for analytics/UI hints. */
  stageId?: string;
}

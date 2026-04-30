/**
 * Divine Waifus — Centralized Equipment & Forge Type Contracts (foundation)
 * ──────────────────────────────────────────────────────────────────────────
 * SCOPE: shared contract for equipment definitions + player instances
 *        + forge recipes (upgrade/fusion).
 *
 * IMPORTANT:
 *  - DOES NOT modify app/equipment.tsx, app/forge.tsx, backend routes,
 *    or any forge/upgrade behavior.
 *  - Mirrors backend `game_data.py:EQUIPMENT_TEMPLATES` slot/rarity model.
 */

import type { RewardItem } from './rewards';

/**
 * Equipment slots — must mirror backend `EQUIPMENT_SLOTS`:
 *   ['weapon', 'armor', 'accessory', 'rune']
 */
export type EquipmentSlot = 'weapon' | 'armor' | 'accessory' | 'rune';

/** Rarity tier 1..6 — same scale as RARITY in constants/theme.ts. */
export type EquipmentRarity = 1 | 2 | 3 | 4 | 5 | 6;

/**
 * Stat block on equipment. Keys are snake_case to mirror backend payload
 * (`stats: { attack, defense, hp, speed, crit_rate, crit_damage, ... }`).
 */
export interface EquipmentStats {
  attack?: number;
  defense?: number;
  hp?: number;
  speed?: number;
  crit_rate?: number;
  crit_damage?: number;
  /** Allow forward-compat extra stats without losing typing. */
  [extraStat: string]: number | undefined;
}

/**
 * Static catalog definition for an equipment template.
 * One entry per `EQUIPMENT_TEMPLATES[slot][i]` in backend.
 */
export interface EquipmentDefinition {
  /** Stable snake_case id (TBD by backend; today templates are nameless rows). */
  id: string;
  name: string;
  slot: EquipmentSlot;
  rarity: EquipmentRarity;
  /** Base stat block before upgrades. */
  baseStats: EquipmentStats;
  /** Optional set bonus id (future feature). */
  setId?: string;
  /** Max forge level (e.g. 15). */
  maxLevel?: number;
  /** Max forge grade (e.g. 5). */
  maxGrade?: number;
  icon?: string;
  description?: string;
  /** Where this equipment can drop (modeIds). Diagnostic. */
  sourceModeIds?: string[];
}

/**
 * Player-owned equipment instance.
 */
export interface PlayerEquipmentInstance {
  /** Server-issued instance uuid. */
  id: string;
  /** Reference to EquipmentDefinition.id. */
  defId: string;
  slot: EquipmentSlot;
  rarity: EquipmentRarity;
  level: number;
  grade: number;
  /** Currently equipped on this user_hero (optional). */
  equippedOnUserHeroId?: string;
  /** Computed effective stats (server-side, includes level+grade bonus). */
  effectiveStats?: EquipmentStats;
  /** Optional rune sockets etc. */
  socketedRuneIds?: string[];
  /** True if the instance is locked (cannot be salvaged/sold). */
  locked?: boolean;
}

export type ForgeRecipeType =
  | 'upgrade'   // level up: same instance, +level, consumes materials/gold
  | 'fusion'    // combine N instances into a higher-rarity instance
  | 'grade'     // grade up at level cap, may consume duplicates
  | 'salvage'   // break down instance into materials
  | 'reforge';  // reroll stats/sub-stats

/**
 * A forge recipe / step. Backend resolves the actual outcome; the frontend
 * uses this only to render preview/UI.
 */
export interface ForgeRecipe {
  /** Stable id, e.g. 'upgrade_armor_lvl5'. */
  id: string;
  type: ForgeRecipeType;
  /** Human-readable label (i18n-ready). */
  name: string;
  /** Slot this recipe applies to (or undefined = any). */
  slot?: EquipmentSlot;
  /** Required rarity input (or undefined = any). */
  rarityIn?: EquipmentRarity;
  /** Resulting rarity output (when applicable, e.g. fusion). */
  rarityOut?: EquipmentRarity;
  /** Required level (for grade/upgrade gating). */
  requiresLevel?: number;
  /**
   * Cost: any combination of currencies/materials/equipment instance
   * references. Reused RewardItem shape for ergonomic symmetry.
   */
  requirements: ForgeRequirement[];
  /** Preview of expected outcome rewards (e.g. salvage byproducts). */
  outcomePreview?: RewardItem[];
  /** True if recipe is currently visible in the forge UI. */
  isVisibleInUI?: boolean;
}

/**
 * One requirement entry of a forge recipe. Either a generic reward-style
 * cost (currency/material/consumable) OR a reference to an owned equipment
 * instance (used by fusion/grade/salvage).
 */
export type ForgeRequirement =
  | {
      kind: 'reward_cost';
      /** Reuses RewardItem shape — itemType MUST be currency/material/consumable */
      cost: RewardItem;
    }
  | {
      kind: 'equipment_ref';
      /** Need this many instances of equipment matching the criteria. */
      count: number;
      slot?: EquipmentSlot;
      rarity?: EquipmentRarity;
      /** Optional: must match a specific definition id. */
      defId?: string;
      /** Optional: minimum level the input instance must be at. */
      minLevel?: number;
    };

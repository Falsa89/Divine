/**
 * Divine Waifus — Centralized Inventory Type Contracts (foundation)
 * ──────────────────────────────────────────────────────────────────
 * SCOPE: shared contract for inventory sectioning + materials/consumables.
 * Does NOT modify app/inventory.tsx or backend.
 */

import type { RewardItemType } from './rewards';

export type InventorySection =
  | 'shards'         // hero shards / soulbound fragments
  | 'consumables'    // EXP potions, books, single-use items
  | 'materials'      // crafting / forge / skill stones
  | 'equipment'      // owned equipment instances
  | 'artifacts'      // owned artifact instances
  | 'runes_gems'     // runes + decorative gems
  | 'event_items';   // event-bound items (may expire)

/**
 * Player-side state of an owned inventory item slot.
 */
export interface InventoryItemState {
  /** snake_case catalog id. e.g. 'exp_potion_m'. */
  itemId: string;
  /** Section the item belongs to (UI tab). */
  section: InventorySection;
  /** Owned quantity. */
  count: number;
  /** Optional locked flag (cannot be sold/used). */
  locked?: boolean;
  /** Optional ISO datetime — item disappears at this time. */
  expiresAt?: string;
  /** Optional event id this item belongs to. */
  eventId?: string;
  /** Convenience type duplicate from catalog (UI rendering). */
  itemType?: RewardItemType;
}

/**
 * Static catalog definition for materials.
 * Mirrors backend `SKILL_MATERIALS` and similar (game_data.py / items.py).
 */
export interface MaterialDefinition {
  id: string;
  name: string;
  description: string;
  icon?: string;
  rarity: number; // 1..6
  /** Where it slots in the inventory tabs. */
  section: InventorySection;
  /** Modes/screens that drop or use this material. Diagnostic. */
  sourceModeIds?: string[];
  /** Hints for UI tooltip about how to obtain. */
  obtainHints?: string[];
  /** Hints for UI tooltip about how to spend. */
  spendHints?: string[];
}

/**
 * Static catalog definition for consumable (single-use) items.
 * Mirrors backend `EXP_ITEMS` and similar.
 */
export interface ConsumableDefinition {
  id: string;
  name: string;
  description: string;
  icon?: string;
  rarity: number; // 1..6
  /** Effect descriptor. e.g. { type:'hero_exp', amount: 5000 } */
  effect: ConsumableEffect;
  /** Optional cooldown in seconds. */
  cooldownSeconds?: number;
  /** True if can be used in battle. */
  usableInBattle?: boolean;
  /** True if can be used outside battle (menu/inventory). */
  usableInMenu?: boolean;
}

/**
 * Discriminated union for consumable effects.
 * Extend safely: each variant must include a `type`.
 */
export type ConsumableEffect =
  | { type: 'hero_exp'; amount: number }
  | { type: 'account_exp'; amount: number }
  | { type: 'currency'; currencyId: string; amount: number }
  | { type: 'heal'; percent: number }
  | { type: 'revive'; percent: number }
  | { type: 'open_chest'; chestId: string }
  | { type: 'custom'; key: string; payload?: unknown };

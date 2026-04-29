/**
 * Post-Battle Summary — data types (v16.22 Foundation)
 * ─────────────────────────────────────────────────────────
 * Definisce le forme dei dati post-battaglia. Le formule numeriche sono
 * intenzionalmente NON definite qui: questa pass è architettura + UI
 * foundation. Sample/mock values dove necessario.
 */

export type RewardKind =
  | 'gold' | 'gem' | 'exp' | 'hero_exp'
  | 'shard' | 'item' | 'equipment' | 'cosmetic' | 'special';

export interface RewardItem {
  /** Categoria di reward (drives icon + display) */
  type: RewardKind;
  /** Optional id (per item/equipment/shard with backend reference) */
  id?: string;
  /** Display name ("Oro", "Pozione EXP", "Hero Shard ..."). */
  name: string;
  /** Emoji or text-based icon for compact display. */
  icon: string;
  /** Reward count (es: 1500 oro, 25 gem, 1 item). */
  amount: number;
  /** Optional rarity for visual styling. */
  rarity?: 'common' | 'rare' | 'epic' | 'legendary' | 'mythic';
  /**
   * Importance flag:
   *  - false (default) → reward auto-claimed (oro/exp/gem comuni, etc.)
   *  - true            → reward important, manual claim required.
   *                       Le voci `important` finiscono in mailbox/inbox
   *                       e scadono dopo `expires_in_days`.
   */
  is_important?: boolean;
}

export interface HeroExpBreakdown {
  user_hero_id: string;
  hero_id: string;
  name: string;
  /** Avatar URL or base64 thumbnail (optional). */
  avatar?: string;
  /** Star rarity (1–6) for frame coloring. */
  rarity?: number;
  /** Element (fire/ice/...) for tinting. */
  element?: string;

  level_before: number;
  level_after: number;

  /** EXP value at the start of the bar (within current level). */
  exp_before: number;
  /** EXP value after gain (within final level if leveled up). */
  exp_after: number;

  /** EXP threshold to next level for the BEFORE level (used for animation). */
  exp_to_next_before: number;
  /** EXP threshold to next level for the AFTER level. */
  exp_to_next_after: number;

  exp_gained: number;
  leveled_up: boolean;
}

export interface BattleStat {
  /** user_hero_id for allies, monster_instance_id for enemies. */
  unit_id: string;
  name: string;
  avatar?: string;
  rarity?: number;
  element?: string;
  team: 'ally' | 'enemy';

  damage_dealt: number;
  damage_received: number;
  healing_done: number;

  /** Survived? false = KO during the battle. */
  survived: boolean;
}

export interface BattleReport {
  allies: BattleStat[];
  enemies: BattleStat[];
  /** unit_id of the ally MVP (highest contribution). */
  mvp_ally_id?: string;
  /** unit_id of the most dangerous enemy. */
  mvp_enemy_id?: string;
}

export interface PostBattleSummaryData {
  outcome: 'victory' | 'defeat';
  duration_sec: number;
  turns: number;
  /** Optional flavor headline (es: "Stage 5-3 Conquistato"). */
  headline?: string;

  rewards: {
    /** Auto-claimed rewards (gold/exp/gem comuni). */
    auto_claim: RewardItem[];
    /** Manual claim rewards (important, finiscono in mailbox). */
    manual_claim: RewardItem[];
    /** Days di scadenza per i manual_claim in mailbox. */
    expires_in_days?: number;
    /** Account-level-up flag (separato dai loot per evidenza). */
    account_level_up?: boolean;
    new_account_level?: number;
  };

  hero_exp: HeroExpBreakdown[];
  battle_report: BattleReport;
}

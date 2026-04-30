/**
 * Divine Waifus — Artifact Type Contracts (foundation)
 * ─────────────────────────────────────────────────────
 * NOTE: Artifacts are NOT equipment. They are collectible/evocable
 * progression objects with global and conditional roster bonuses
 * (e.g. "+8% attacco a tutti gli eroi Fuoco", "+5% velocità in PvP").
 * They have copies/duplicates → grade ups, separate from level ups.
 *
 * SCOPE: pure types only — does NOT modify artifact screens or routes.
 */

import type { RewardItem } from './rewards';
import type { CurrencyId } from './economy';

/**
 * Conditional bonus that applies only under specific roster/mode conditions.
 */
export interface ArtifactConditionalBonus {
  id: string;
  /** Human-readable label e.g. 'Bonus PvP'. */
  label: string;
  /**
   * Condition descriptor (data-driven, evaluated server-side).
   * Common shapes: { type:'mode', modeId:'arena' } / { type:'element', element:'fire' }
   * / { type:'faction', faction:'olympus' } / { type:'team_size', size:6 }.
   */
  condition:
    | { type: 'mode'; modeId: string }
    | { type: 'element'; element: string }
    | { type: 'faction'; faction: string }
    | { type: 'rarity'; rarity: number }
    | { type: 'team_size'; size: number }
    | { type: 'custom'; key: string; payload?: unknown };
  /** Stat key (matches EquipmentStats keys: snake_case). */
  stat: string;
  /** Numerical bonus (flat or percent — discriminate via `unit`). */
  amount: number;
  /** 'flat' = +N, 'percent' = +N% (interpreted server-side). */
  unit: 'flat' | 'percent';
}

/**
 * Global (always-on) bonus from an artifact.
 */
export interface ArtifactBonus {
  /** Stat key (snake_case). */
  stat: string;
  amount: number;
  unit: 'flat' | 'percent';
  /** Optional scope label (e.g. 'all heroes', 'home hero only'). */
  scopeLabel?: string;
}

/**
 * Static catalog definition for an artifact.
 * Stored separately from owned-state.
 */
export interface ArtifactDefinition {
  /** snake_case id, e.g. 'aegis_of_olympus'. */
  id: string;
  name: string;
  description: string;
  /** 1..6 rarity scale. */
  rarity: number;
  icon?: string;
  /** Splash/showcase image when revealed. */
  splashImage?: string;
  /** Always-on bonuses applied while artifact is unlocked. */
  globalBonuses: ArtifactBonus[];
  /** Conditional bonuses (apply only when condition met). */
  conditionalBonuses?: ArtifactConditionalBonus[];
  /** Max grade tier (e.g. 5). */
  maxGrade?: number;
  /** Max level per grade. */
  maxLevel?: number;
  /**
   * Materials required to grade up.
   * Reuses RewardItem shape for ergonomic symmetry (snake_case ids inside).
   */
  gradeUpRequirements?: RewardItem[];
  /** Materials required per level up step. */
  levelUpRequirements?: RewardItem[];
  /** Summon pool / gacha banner this artifact belongs to (if evocable). */
  summonPoolId?: string;
  /** True if cannot be obtained outside of a specific event window. */
  isLimitedTime?: boolean;
  /** Currency used to summon (if applicable). */
  summonCurrency?: CurrencyId;
  /** Optional faction tag for grouping in the artifact gallery. */
  factionTag?: string;
}

/**
 * Player-side state for one artifact catalog entry.
 */
export interface PlayerArtifactState {
  defId: string;
  /** True once any copy has been obtained. */
  unlocked: boolean;
  /** Total copies (duplicates) collected so far. */
  copiesOwned: number;
  /** Current grade tier. */
  grade: number;
  /** Current level within grade. */
  level: number;
  /** Date first obtained (ISO). */
  obtainedAt?: string;
  /** True if user has marked it as favorite. */
  favorite?: boolean;
}

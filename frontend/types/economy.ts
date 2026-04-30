/**
 * Divine Waifus — Centralized Economy Type Contracts (foundation)
 * ────────────────────────────────────────────────────────────────
 * SCOPE: pure type contracts shared by future economy/treasury/shop/UI.
 *
 * IMPORTANT NOTES:
 *  - This file does NOT modify AuthContext.User.
 *  - Stamina (`stamina`/`max_stamina`) currently still lives on AuthContext
 *    by design. Roadmap may remove global stamina later — for now we leave
 *    a placeholder Currency category 'legacy_stamina' so any migration is
 *    explicit and safe.
 *  - Currency IDs MUST be snake_case to match backend `game_data.py` style
 *    and existing user fields (`gold`, `gems`).
 *
 * Example IDs (NOT exhaustive — populate later when wiring real data):
 *   - gold              (standard, primary, isPremium=false)
 *   - divine_crystals   (premium gem-replacement candidate, isPremium=true)
 *   - summon_seal       (event/seasonal pull token)
 *   - honor_marks       (PvP/Arena reward currency)
 *   - war_banners       (Guild/GvG reward currency)
 *   - soul_essence      (sanctuary/affinity material currency)
 *   - tower_keys        (Tower of Infinity entry tickets)
 */

export type CurrencyCategory =
  | 'standard'        // gold, basic materials
  | 'premium'         // divine_crystals, real-money convertible
  | 'event'           // limited-time, may expire
  | 'faction'         // tied to a faction allegiance
  | 'guild'           // war_banners etc.
  | 'ranking'         // honor_marks etc.
  | 'soulbound'       // sanctuary/affinity-bound (not tradable)
  | 'legacy_stamina'  // PLACEHOLDER for current AuthContext stamina; do NOT migrate yet
  | 'special';        // anything that does not fit other buckets

export type CurrencyImportance = 'primary' | 'secondary' | 'tertiary';

/**
 * Static definition of a currency. UI/treasury reads from this.
 * NEVER stores the actual user balance here — see PlayerCurrencyState.
 */
export interface CurrencyDefinition {
  /** snake_case identifier; stable across versions. e.g. 'gold' */
  id: string;
  /** Human-readable name (i18n-ready). e.g. 'Oro' */
  name: string;
  /** Optional short label for compact UI. e.g. 'G' */
  shortName?: string;
  /** One-line description for tooltips/treasury. */
  description: string;
  /** Optional icon glyph or emoji or asset path. UI may override. */
  icon?: string;
  /** Bucket for treasury grouping. */
  category: CurrencyCategory;
  /** Visual emphasis hint for UI ordering. */
  importance?: CurrencyImportance;
  /** True if obtained primarily via real-money purchase. */
  isPremium?: boolean;
  /** Whether the Home top bar should display this currency. */
  isVisibleInHome: boolean;
  /** Whether the Treasury screen should list this currency. */
  isVisibleInTreasury: boolean;
  /** Hints for documentation/tooltip: where the user can earn it. */
  sourceHints: string[];
  /** Hints for documentation/tooltip: where the user can spend it. */
  spendHints: string[];
  /** Screens (route names) that interact with this currency. Diagnostic. */
  relatedScreens: string[];
  /** True if balance can decay/expire (e.g. event currencies). */
  expires?: boolean;
  /** If event currency, the event identifier this belongs to. */
  eventId?: string;
  /** Display order in treasury/home. Lower = first. */
  sortOrder: number;
}

/**
 * Player-side wallet state. Keys are CurrencyDefinition.id.
 * NOT wired to AuthContext yet — this is a forward-looking contract.
 */
export type PlayerCurrencyState = Record<string, number>;

/** Optional helper alias for code that may want a typed currency id. */
export type CurrencyId = string;

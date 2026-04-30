/**
 * Divine Waifus — Prototype / Feature Flag Type Contracts (foundation)
 * ─────────────────────────────────────────────────────────────────────
 * SCOPE: pure types describing release-phase metadata for any feature.
 * Used to decide whether a feature is wired-up, hidden, or mocked.
 *
 * NOTE:
 *  - This is NOT a runtime feature-flag system. It only defines the
 *    contract. Future runtime evaluation can live in a separate file.
 *  - Useful to mark unfinished modes/screens (`isPlaceholder=true`,
 *    `requiresDevMode=true`) without breaking working flows.
 */

export type ReleasePhase =
  | 'concept'      // idea-only, not started
  | 'foundation'   // type/contract or backend skeleton present
  | 'prototype'    // working demo (may be limited)
  | 'beta'         // playable end-to-end with known gaps
  | 'live';        // production-ready

/**
 * Static definition of a prototype/feature flag entry.
 */
export interface PrototypeFeatureFlag {
  /** snake_case id, e.g. 'afk_autobattle', 'tesoreria', 'addestramento_eroico'. */
  id: string;
  /** Human-readable name (i18n-ready). */
  name?: string;
  /** True if the underlying implementation is wired-up enough to test. */
  isPrototypeEnabled: boolean;
  /** True if exposed in the user-visible UI (independently of prototype state). */
  isVisibleInUI: boolean;
  /** True if the feature exists only as a placeholder/stub. */
  isPlaceholder: boolean;
  /** True if access requires a developer-mode toggle (dev-test/sprite-test/etc.). */
  requiresDevMode: boolean;
  releasePhase: ReleasePhase;
  /** Optional notes for engineers (kept short). */
  notes?: string;
}

/**
 * Runtime evaluation snapshot of a feature flag.
 * Future flag-evaluator may produce this from PrototypeFeatureFlag + context.
 */
export interface PrototypeFeatureState {
  flagId: string;
  /** Final UI visibility decision (may differ from flag.isVisibleInUI). */
  visible: boolean;
  /** Final reachability for the player (entry rules + flag combined). */
  reachable: boolean;
  /** True if the player has ever interacted with this feature. */
  seen?: boolean;
  /** Last update timestamp (ISO). */
  updatedAt?: string;
}

/**
 * Divine Waifus — Static Data Catalog (foundation barrel)
 * ───────────────────────────────────────────────────────────────
 * Re-exports the static config catalogs created in TASK 4.5-A.
 *
 * Usage (when consumers are ready, NOT today):
 *   import { CURRENCY_DEFINITIONS, MODE_DEFINITIONS } from '../data';
 *
 * IMPORTANT:
 *  - Pure static data + tiny getters. No runtime/UI wiring.
 *  - Existing screens are NOT consuming these catalogs yet.
 *  - VALUES ARE PLACEHOLDER — not final balance.
 */
export * from './currencies';
export * from './materials';
export * from './modes';
export * from './rewardTables';
export * from './shops';
export * from './prototypeFlags';

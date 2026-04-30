/**
 * Divine Waifus — Centralized Frontend Types (foundation barrel)
 * ──────────────────────────────────────────────────────────────
 * Re-exports all shared type contracts under a single import path.
 *
 * Usage (when consumers are ready, NOT today):
 *   import type { CurrencyDefinition, RewardItem, ModeDefinition } from '../types';
 *
 * IMPORTANT:
 *  - This is a TYPE-ONLY foundation. No runtime code, no side effects.
 *  - Existing screens are NOT consuming these types yet.
 *  - The legacy `components/battle/postBattleTypes.ts` still drives the
 *    PostBattleSummary/BattleReport rendering; do NOT replace until a
 *    dedicated migration task is scheduled.
 */

export * from './economy';
export * from './rewards';
export * from './modes';
export * from './inventory';
export * from './equipment';
export * from './artifacts';
export * from './battleStats';
export * from './prototypeFlags';

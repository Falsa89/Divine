/**
 * Hero Assets — public canonical API (RM1.17)
 * ────────────────────────────────────────────────────────────────
 * Punto d'ingresso preferito per nuovi consumer. Internamente delega al
 * registry esteso in ./hopliteAssets.ts (file storico mantenuto per
 * backward-compat con i 12+ consumer esistenti).
 *
 * Usage:
 *   import {
 *     resolveHeroImageByRole,
 *     heroPortraitSource,
 *     heroBattleImageSource,
 *     isHeroAssetSentinel,
 *     parseHeroAssetSentinel,
 *   } from '@/components/ui/heroAssets';
 *
 * Per registrare un nuovo eroe ufficiale con asset locali aggiungere
 * l'entry in HERO_ASSET_REGISTRY dentro hopliteAssets.ts.
 */
export {
  // Identity helpers
  isGreekHoplite,
  isNorseBerserker,
  isHopliteSentinel,
  isBerserkerSentinel,
  isHeroAssetSentinel,
  parseHeroAssetSentinel,
  // Role-based resolver (canonical)
  resolveHeroImageByRole,
  // UI-safe wrappers
  heroImageSource,
  heroPortraitSource,
  heroBattleImageSource,
  resolveHeroImageSource,
  resolveHeroDetailImageSource,
  resolveHeroPortraitSource,
  // Constants
  GREEK_HOPLITE_ID,
  GREEK_HOPLITE_NAME,
  GREEK_HOPLITE_IMAGE_SENTINEL,
  GREEK_HOPLITE_TRANSPARENT,
  GREEK_HOPLITE_PORTRAIT,
  GREEK_HOPLITE_DETAIL,
  GREEK_HOPLITE_COMBAT_BASE,
  NORSE_BERSERKER_ID,
  NORSE_BERSERKER_NAME,
  NORSE_BERSERKER_IMAGE_SENTINEL,
  NORSE_BERSERKER_PORTRAIT,
  NORSE_BERSERKER_DETAIL,
  NORSE_BERSERKER_TRANSPARENT,
  NORSE_BERSERKER_COMBAT_BASE,
} from './hopliteAssets';

export type { HeroImageRole } from './hopliteAssets';

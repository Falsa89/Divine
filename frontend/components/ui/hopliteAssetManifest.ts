/**
 * Greek Hoplite — Asset Manifest
 * ================================
 * Elenco CENTRALIZZATO e STATICO di tutti gli asset richiesti per renderizzare
 * correttamente Greek Hoplite in battle senza "ricaricamento visivo".
 *
 * Perché module-level const:
 *  - I `require(...)` vengono risolti una sola volta a build time dal bundler.
 *  - L'array è stabile per identità → può essere iterato in preload con
 *    `Asset.fromModule(...).downloadAsync()` che cachea in memoria ed evita
 *    decode lazy durante la battle.
 *  - Importato una volta, distribuito ovunque → niente duplicazioni.
 *
 * L'ordine NON è rilevante per il rendering: i componenti (HeroHopliteRig,
 * HeroHopliteAffondo, HeroHopliteGuardiaFerrea) hanno i loro `require`
 * locali. Questo manifest serve SOLO a guidare il preload ahead-of-time
 * in combat.tsx.
 */
import { ImageSourcePropType } from 'react-native';

// ── RIG (idle): 7 layer anatomici + 5 helper fill ────────────────────────
export const HOPLITE_RIG_ASSETS: ImageSourcePropType[] = [
  require('../../assets/heroes/greek_hoplite/rig/hair.png'),
  require('../../assets/heroes/greek_hoplite/rig/legs.png'),
  require('../../assets/heroes/greek_hoplite/rig/skirt.png'),
  require('../../assets/heroes/greek_hoplite/rig/torso.png'),
  require('../../assets/heroes/greek_hoplite/rig/shield_arm.png'),
  require('../../assets/heroes/greek_hoplite/rig/spear_arm.png'),
  require('../../assets/heroes/greek_hoplite/rig/head_helmet.png'),
  require('../../assets/heroes/greek_hoplite/rig_safe/hip_fill.png'),
  require('../../assets/heroes/greek_hoplite/rig_safe/under_arm_spear.png'),
  require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_shield_fill.png'),
  require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_spear_fill.png'),
  require('../../assets/heroes/greek_hoplite/rig_safe/neck_fill.png'),
];

// ── AFFONDO DI FALANGE (attack): 8 keyframe ──────────────────────────────
export const HOPLITE_AFFONDO_ASSETS: ImageSourcePropType[] = [
  require('../../assets/heroes/greek_hoplite/affondo/frame_1.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_2.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_3.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_4.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_5.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_6.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_7.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_8.png'),
];

// ── GUARDIA FERREA (skill): 6 keyframe ───────────────────────────────────
export const HOPLITE_GUARDIA_ASSETS: ImageSourcePropType[] = [
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_1.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_2.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_3.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_4.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_5.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_6.png'),
];

// ── COMBAT BASE (fallback / HUD splash base) ─────────────────────────────
export const HOPLITE_COMBAT_BASE: ImageSourcePropType =
  require('../../assets/heroes/greek_hoplite/combat_base.png');
export const HOPLITE_SPLASH: ImageSourcePropType =
  require('../../assets/heroes/greek_hoplite/splash.png');

// ── Aggregato: TUTTO ciò che serve per Hoplite in battle ─────────────────
export const HOPLITE_BATTLE_ASSET_MANIFEST: ImageSourcePropType[] = [
  ...HOPLITE_RIG_ASSETS,
  ...HOPLITE_AFFONDO_ASSETS,
  ...HOPLITE_GUARDIA_ASSETS,
  HOPLITE_COMBAT_BASE,
  HOPLITE_SPLASH,
];

/** Conteggio totale asset Hoplite (informativo per progress bar). */
export const HOPLITE_BATTLE_ASSET_COUNT = HOPLITE_BATTLE_ASSET_MANIFEST.length;

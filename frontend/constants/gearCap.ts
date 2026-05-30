/**
 * frontend/constants/gearCap.ts
 *
 * PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK
 * Sentinella: v23 PUBLIC_SYNC_TAG_RESYNC_v23_GEAR_CAP_PLUS_50_RUNTIME
 *
 * Stage canonici del Gear Cap (+50). Locked da Bible 202 (Track D).
 * Separato da: Hero Elevation, Hero Level, Star Up, Ascensione, Skill, Costellazioni,
 * Reincarnation, Gemme, Rune, Artifact, Divine Weapon, BP Delta, Combat, Battle Engine.
 *
 * Tutto read-only / preview-only in questo pack. NESSUNA mutation.
 */

export type GearStageId = 'early' | 'mid' | 'late' | 'endgame';
export type GearSlotId = 'weapon' | 'armor' | 'helm' | 'boots' | 'gloves' | 'accessory';

export type GearStagedCap = {
  stage_id: GearStageId;
  order: number;
  label_it: string;
  min: number;
  max: number;
  display_color_hint: string;
  unlock_via: string;
};

export type GearSlot = {
  slot_id: GearSlotId;
  label_it: string;
};

export const GEAR_CAP_CANONICAL: number = 50;
export const GEAR_CAP_LEGACY_TO_REPLACE: number = 20;
export const GEAR_CAP_MIN: number = 0;

export const GEAR_STAGED_CAPS: GearStagedCap[] = [
  { stage_id: 'early',   order: 0, label_it: 'Avvio',      min: 0,  max: 10, display_color_hint: '#9ea0c8', unlock_via: 'hero_level_or_ascension_low' },
  { stage_id: 'mid',     order: 1, label_it: 'Intermedio', min: 11, max: 20, display_color_hint: '#4a90e2', unlock_via: 'hero_level_mid + ascension_unlock' },
  { stage_id: 'late',    order: 2, label_it: 'Avanzato',   min: 21, max: 35, display_color_hint: '#a96bff', unlock_via: 'forge_enhance + materials_late' },
  { stage_id: 'endgame', order: 3, label_it: 'Endgame',    min: 36, max: 50, display_color_hint: '#ff5470', unlock_via: 'forge_reforge + endgame_materials + costellazione_gate_optional' },
];

export const GEAR_SLOTS: GearSlot[] = [
  { slot_id: 'weapon',    label_it: 'Arma' },
  { slot_id: 'armor',     label_it: 'Armatura' },
  { slot_id: 'helm',      label_it: 'Elmo' },
  { slot_id: 'boots',     label_it: 'Stivali' },
  { slot_id: 'gloves',    label_it: 'Guanti' },
  { slot_id: 'accessory', label_it: 'Accessorio' },
];

/** Risolve lo stage corrente dato un gear level (0..50). Ritorna null se fuori range. */
export function resolveGearStage(level: number): GearStagedCap | null {
  if (typeof level !== 'number' || isNaN(level)) return null;
  if (level < GEAR_CAP_MIN || level > GEAR_CAP_CANONICAL) return null;
  return GEAR_STAGED_CAPS.find((s) => level >= s.min && level <= s.max) ?? null;
}

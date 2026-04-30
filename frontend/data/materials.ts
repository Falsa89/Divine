/**
 * Divine Waifus — Material & Consumable static catalog (foundation)
 * ────────────────────────────────────────────────────────────────
 * PLACEHOLDER ONLY — not final tuning.
 * Pure static data + tiny getters. No screen wiring.
 */
import type { MaterialDefinition, ConsumableDefinition } from '../types/inventory';

// ──────────────────────────────────────────────────────────────────────
// MATERIALS (crafting/forge/skill/ascension/elemental/role/etc.)
// ──────────────────────────────────────────────────────────────────────
export const MATERIAL_DEFINITIONS: Record<string, MaterialDefinition> = {
  // ── Hero EXP tomes (consumable in spirit, kept here for catalog parity) ──
  // (Real ConsumableDefinitions for them are in CONSUMABLE_DEFINITIONS below;
  //  these MaterialDefinitions are the catalog metadata for inventory grouping.)

  // ── Ascension stones ───────────────────────────────────────────────
  minor_ascension_stone:    { id: 'minor_ascension_stone',    name: 'Pietra Ascensione Minore',    description: 'Materiale ascensione hero. Tier 1.', icon: '🪨', rarity: 1, section: 'materials', sourceModeIds: ['hero_training_ascension_trial', 'story_campaign'], obtainHints: ['ascension_trial', 'story_drop'] },
  medium_ascension_stone:   { id: 'medium_ascension_stone',   name: 'Pietra Ascensione Media',     description: 'Materiale ascensione hero. Tier 2.', icon: '🪨', rarity: 2, section: 'materials', sourceModeIds: ['hero_training_ascension_trial', 'tower_of_inferno'], obtainHints: ['ascension_trial', 'tower_drop'] },
  major_ascension_stone:    { id: 'major_ascension_stone',    name: 'Pietra Ascensione Maggiore',  description: 'Materiale ascensione hero. Tier 3.', icon: '⚒️', rarity: 3, section: 'materials', sourceModeIds: ['hero_training_ascension_trial', 'tower_of_inferno', 'event_hub'], obtainHints: ['ascension_trial_high', 'tower_drop', 'event'] },
  supreme_ascension_stone:  { id: 'supreme_ascension_stone',  name: 'Pietra Ascensione Suprema',   description: 'Materiale ascensione hero. Tier 4 endgame.', icon: '💠', rarity: 4, section: 'materials', sourceModeIds: ['scale_of_olympus', 'thrones_of_eclipse'], obtainHints: ['endgame_drops'] },

  // ── Elemental essences ────────────────────────────────────────────
  fire_essence:    { id: 'fire_essence',    name: 'Essenza di Fuoco',  description: 'Materiale elementale fuoco.',   icon: '🔥', rarity: 2, section: 'materials', sourceModeIds: ['hero_training_elemental_trial', 'event_hub'], obtainHints: ['elemental_trial_fire'], spendHints: ['hero_skill_upgrade_fire'] },
  water_essence:   { id: 'water_essence',   name: 'Essenza d\'Acqua',  description: 'Materiale elementale acqua.',  icon: '💧', rarity: 2, section: 'materials', sourceModeIds: ['hero_training_elemental_trial'], obtainHints: ['elemental_trial_water'], spendHints: ['hero_skill_upgrade_water'] },
  earth_essence:   { id: 'earth_essence',   name: 'Essenza di Terra',  description: 'Materiale elementale terra.',  icon: '⛰️', rarity: 2, section: 'materials', sourceModeIds: ['hero_training_elemental_trial'], obtainHints: ['elemental_trial_earth'], spendHints: ['hero_skill_upgrade_earth'] },
  wind_essence:    { id: 'wind_essence',    name: 'Essenza di Vento',  description: 'Materiale elementale vento.',  icon: '🌪️', rarity: 2, section: 'materials', sourceModeIds: ['hero_training_elemental_trial'], obtainHints: ['elemental_trial_wind'], spendHints: ['hero_skill_upgrade_wind'] },
  light_essence:   { id: 'light_essence',   name: 'Essenza di Luce',   description: 'Materiale elementale luce.',   icon: '☀️', rarity: 3, section: 'materials', sourceModeIds: ['hero_training_elemental_trial'], obtainHints: ['elemental_trial_light'], spendHints: ['hero_skill_upgrade_light'] },
  shadow_essence:  { id: 'shadow_essence',  name: 'Essenza d\'Ombra',  description: 'Materiale elementale ombra.',  icon: '🌑', rarity: 3, section: 'materials', sourceModeIds: ['hero_training_elemental_trial'], obtainHints: ['elemental_trial_shadow'], spendHints: ['hero_skill_upgrade_shadow'] },

  // ── Role emblems ──────────────────────────────────────────────────
  warrior_emblem:  { id: 'warrior_emblem',  name: 'Emblema Guerriero',  description: 'Token classe Guerriero.',   icon: '⚔️', rarity: 3, section: 'materials', sourceModeIds: ['arena_pvp', 'event_hub'], obtainHints: ['arena_drop'], spendHints: ['warrior_skill_unlock'] },
  guardian_emblem: { id: 'guardian_emblem', name: 'Emblema Guardiano',  description: 'Token classe Guardiano (Tank).', icon: '🛡️', rarity: 3, section: 'materials', sourceModeIds: ['arena_pvp', 'event_hub'], obtainHints: ['arena_drop'], spendHints: ['tank_skill_unlock'] },
  oracle_emblem:   { id: 'oracle_emblem',   name: 'Emblema Oracolo',    description: 'Token classe Oracolo (Mage).',  icon: '🔮', rarity: 3, section: 'materials', sourceModeIds: ['arena_pvp', 'event_hub'], obtainHints: ['arena_drop'], spendHints: ['mage_skill_unlock'] },
  assassin_emblem: { id: 'assassin_emblem', name: 'Emblema Assassino',  description: 'Token classe Assassino.',   icon: '🗡️', rarity: 3, section: 'materials', sourceModeIds: ['arena_pvp', 'event_hub'], obtainHints: ['arena_drop'], spendHints: ['assassin_skill_unlock'] },
  support_emblem:  { id: 'support_emblem',  name: 'Emblema Supporto',   description: 'Token classe Supporto.',    icon: '✨', rarity: 3, section: 'materials', sourceModeIds: ['arena_pvp', 'event_hub'], obtainHints: ['arena_drop'], spendHints: ['support_skill_unlock'] },

  // ── Forge ores ────────────────────────────────────────────────────
  basic_forge_ore:    { id: 'basic_forge_ore',    name: 'Minerale Base',    description: 'Minerale base per forge equipment tier 1-2.',   icon: '⛏️', rarity: 1, section: 'materials', sourceModeIds: ['hephaestus_forge', 'story_campaign'], obtainHints: ['forge_quest', 'story_drop'], spendHints: ['equipment_upgrade_1_2'] },
  refined_forge_ore:  { id: 'refined_forge_ore',  name: 'Minerale Raffinato', description: 'Minerale raffinato per forge equipment tier 3-4.', icon: '⚒️', rarity: 3, section: 'materials', sourceModeIds: ['hephaestus_forge'], obtainHints: ['forge_quest_advanced'], spendHints: ['equipment_upgrade_3_4'] },
  divine_forge_ore:   { id: 'divine_forge_ore',   name: 'Minerale Divino',  description: 'Minerale divino per forge equipment tier 5-6 endgame.', icon: '💎', rarity: 5, section: 'materials', sourceModeIds: ['scale_of_olympus', 'titanomachy'], obtainHints: ['endgame_drops'], spendHints: ['equipment_upgrade_5_6'] },

  // ── Artifact materials ───────────────────────────────────────────
  artifact_dust: { id: 'artifact_dust', name: 'Polvere Artefatti', description: 'Polvere magica per crafting artefatti base.', icon: '✨', rarity: 2, section: 'materials', sourceModeIds: ['artifacts_page', 'event_hub'], obtainHints: ['artifact_drop', 'event'], spendHints: ['artifact_levelup'] },
  artifact_core: { id: 'artifact_core', name: 'Nucleo Artefatto',  description: 'Nucleo per crafting/grading artefatti rari.', icon: '🌟', rarity: 5, section: 'materials', sourceModeIds: ['scale_of_olympus', 'event_hub'], obtainHints: ['endgame_drops', 'event_milestone'], spendHints: ['artifact_gradeup'] },

  // ── Rune/Gems ─────────────────────────────────────────────────────
  rune_fragment: { id: 'rune_fragment', name: 'Frammento Runa',   description: 'Frammento di runa per craft.',                      icon: '🔷', rarity: 2, section: 'runes_gems', sourceModeIds: ['rune_gem_trial'], obtainHints: ['rune_trial'], spendHints: ['rune_craft'] },
  rune_core:     { id: 'rune_core',     name: 'Nucleo Runico',    description: 'Nucleo per crafting/fusione rune endgame.',         icon: '💠', rarity: 5, section: 'runes_gems', sourceModeIds: ['rune_gem_trial', 'tower_of_inferno'], obtainHints: ['rune_trial_high', 'tower_high'], spendHints: ['rune_fuse'] },

  // ── Reincarnation / endgame placeholders ─────────────────────────
  reincarnation_core: { id: 'reincarnation_core', name: 'Nucleo Reincarnazione', description: 'PLACEHOLDER — risorsa reincarnazione endgame. Non finalizzato.', icon: '♾️', rarity: 6, section: 'materials', sourceModeIds: ['twilight_of_titans'], obtainHints: ['endgame_only'], spendHints: ['reincarnate'] },
  stellar_essence:    { id: 'stellar_essence',    name: 'Essenza Stellare',     description: 'PLACEHOLDER — risorsa per costellazioni cosmiche. Non finalizzato.',                  icon: '🌌', rarity: 6, section: 'materials', sourceModeIds: ['thrones_of_eclipse'], obtainHints: ['endgame_only'],  spendHints: ['constellation_endgame'] },
};

// ──────────────────────────────────────────────────────────────────────
// CONSUMABLES (single-use items: EXP tomes, etc.)
// ──────────────────────────────────────────────────────────────────────
export const CONSUMABLE_DEFINITIONS: Record<string, ConsumableDefinition> = {
  minor_exp_tome:   { id: 'minor_exp_tome',   name: 'Tomo EXP Minore',   description: 'Conferisce EXP minore a un eroe.',   icon: '📕', rarity: 1, effect: { type: 'hero_exp', amount: 500    }, usableInMenu: true },
  medium_exp_tome:  { id: 'medium_exp_tome',  name: 'Tomo EXP Medio',    description: 'Conferisce EXP medio a un eroe.',    icon: '📗', rarity: 2, effect: { type: 'hero_exp', amount: 2500   }, usableInMenu: true },
  major_exp_tome:   { id: 'major_exp_tome',   name: 'Tomo EXP Maggiore', description: 'Conferisce EXP maggiore a un eroe.', icon: '📘', rarity: 3, effect: { type: 'hero_exp', amount: 12500  }, usableInMenu: true },
  supreme_exp_tome: { id: 'supreme_exp_tome', name: 'Tomo EXP Supremo',  description: 'Conferisce EXP supremo a un eroe.',  icon: '📙', rarity: 4, effect: { type: 'hero_exp', amount: 60000  }, usableInMenu: true },
};

/** Lookup helpers. */
export function getMaterialDefinition(id: string): MaterialDefinition | undefined {
  return MATERIAL_DEFINITIONS[id];
}
export function getConsumableDefinition(id: string): ConsumableDefinition | undefined {
  return CONSUMABLE_DEFINITIONS[id];
}

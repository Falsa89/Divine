/**
 * Divine Waifus — Mode static catalog (foundation)
 * ───────────────────────────────────────────────────────────────
 * Pure static data — PLACEHOLDER ONLY, not final tuning.
 * Account-level unlock thresholds follow the approved roadmap.
 */
import type { ModeDefinition } from '../types/modes';

const placeholder = {
  isPrototypeEnabled: false,
  isVisibleInUI: false,
  isPlaceholder: true,
};

export const MODE_DEFINITIONS: Record<string, ModeDefinition> = {
  // ─── CORE ─────────────────────────────────────────────────────────
  story_campaign: {
    id: 'story_campaign', name: 'Campagna', category: 'pve', family: 'story',
    description: 'Campagna principale story-driven.',
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    rewardTableId: 'story_stage_reward_placeholder',
    milestoneTableId: 'story_milestone_reward_placeholder',
    isPrototypeEnabled: true, isVisibleInUI: true,
  },
  afk_autobattle: {
    id: 'afk_autobattle', name: 'AFK Autobattle', category: 'idle', family: 'afk',
    description: 'Accumulo automatico risorse mentre offline.',
    unlockAccountLevel: 5,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    rewardTableId: 'afk_autobattle_reward_placeholder',
    ...placeholder,
  },
  instant_autobattle: {
    id: 'instant_autobattle', name: 'Autobattle Istantaneo', category: 'pve', family: 'misc',
    description: 'Risolvi una battaglia ripetibile istantaneamente.',
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'instant_autobattle_reward_placeholder',
    ...placeholder,
  },
  daily_tasks: {
    id: 'daily_tasks', name: 'Missioni Giornaliere', category: 'progression', family: 'misc',
    description: 'Quest giornaliere con reward incrementale.',
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    isPrototypeEnabled: false, isVisibleInUI: true, isPlaceholder: true,
  },

  // ─── ADDESTRAMENTO EROICO ────────────────────────────────────────
  hero_training_exp_trial: {
    id: 'hero_training_exp_trial', name: 'Trial EXP', category: 'pve', family: 'training',
    description: 'Farm di tomi EXP per eroi.',
    unlockAccountLevel: 35,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'trial_exp_reward_placeholder',
    ...placeholder,
  },
  hero_training_ascension_trial: {
    id: 'hero_training_ascension_trial', name: 'Trial Ascensione', category: 'pve', family: 'training',
    description: 'Farm pietre di ascensione.',
    unlockAccountLevel: 35,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'trial_ascension_reward_placeholder',
    ...placeholder,
  },
  hero_training_elemental_trial: {
    id: 'hero_training_elemental_trial', name: 'Trial Elementale', category: 'pve', family: 'training',
    description: 'Farm essenze elementali (rotazione giornaliera per elemento).',
    unlockAccountLevel: 35,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'trial_elemental_reward_placeholder',
    ...placeholder,
  },
  hero_training_gold_trial: {
    id: 'hero_training_gold_trial', name: 'Trial Oro', category: 'pve', family: 'training',
    description: 'Farm intensivo di oro.',
    unlockAccountLevel: 35,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'trial_gold_reward_placeholder', currencyId: 'gold',
    ...placeholder,
  },

  // ─── BUILD / FUCINA ──────────────────────────────────────────────
  hephaestus_forge: {
    id: 'hephaestus_forge', name: 'Fucina di Efesto', category: 'progression', family: 'forge_quest',
    description: 'Crafting/upgrading equipment.',
    unlockAccountLevel: 55,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    rewardTableId: 'rune_gem_reward_placeholder',
    ...placeholder,
  },
  rune_gem_trial: {
    id: 'rune_gem_trial', name: 'Trial Rune & Gemme', category: 'pve', family: 'training',
    description: 'Farm frammenti runici e gemme.',
    unlockAccountLevel: 55,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 2, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'rune_gem_reward_placeholder',
    ...placeholder,
  },
  artifacts_page: {
    id: 'artifacts_page', name: 'Artefatti', category: 'progression', family: 'misc',
    description: 'Gestione artefatti (collezione/upgrade/grade).',
    unlockAccountLevel: 70,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    rewardTableId: 'artifact_material_reward_placeholder',
    ...placeholder,
  },

  // ─── PVP ─────────────────────────────────────────────────────────
  arena_pvp: {
    id: 'arena_pvp', name: 'Arena PvP', category: 'pvp', family: 'arena',
    description: 'Combattimento ranked contro altri giocatori.',
    unlockAccountLevel: 18,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    baseEntries: 5, baseAttempts: 5, allowsExtraEntries: true, extraEntryCurrency: 'divine_crystals',
    rewardTableId: 'arena_reward_placeholder', shopId: 'honor_marks_shop_placeholder',
    currencyId: 'honor_marks', hasRanking: true,
    ...placeholder,
  },

  // ─── GUILD / LIVE ────────────────────────────────────────────────
  guild_live: {
    id: 'guild_live', name: 'Gilda', category: 'social', family: 'gvg',
    description: 'Hub gilda (chat, attività, contributi).',
    unlockAccountLevel: 7,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners',
    ...placeholder,
  },
  fronts_of_valhalla: {
    id: 'fronts_of_valhalla', name: 'Fronti del Valhalla', category: 'social', family: 'gvg',
    description: 'Fronti GvG settimanali.',
    unlockAccountLevel: 45,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    baseEntries: 3, baseAttempts: 3,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners', hasRanking: true,
    ...placeholder,
  },
  war_of_three_thrones: {
    id: 'war_of_three_thrones', name: 'Guerra dei Tre Troni', category: 'social', family: 'gvg',
    description: 'Live event GvG a 3 fazioni.',
    unlockAccountLevel: 80,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners',
    hasRanking: true, hasLiveWindow: true,
    ...placeholder,
  },
  assault_of_ragnarok: {
    id: 'assault_of_ragnarok', name: 'Assalto di Ragnarok', category: 'social', family: 'world_boss',
    description: 'Boss mondiale gilda.',
    unlockAccountLevel: 80,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners',
    hasLiveWindow: true,
    ...placeholder,
  },
  titanomachy: {
    id: 'titanomachy', name: 'Titanomachia', category: 'social', family: 'world_boss',
    description: 'Boss mondiale endgame.',
    unlockAccountLevel: 90,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners',
    hasRanking: true, hasLiveWindow: true,
    ...placeholder,
  },
  twilight_of_titans: {
    id: 'twilight_of_titans', name: 'Crepuscolo dei Titani', category: 'social', family: 'world_boss',
    description: 'Endgame finale apocalittico.',
    unlockAccountLevel: 100,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    rewardTableId: 'guild_live_reward_placeholder', currencyId: 'war_banners',
    hasRanking: true, hasLiveWindow: true,
    ...placeholder,
  },

  // ─── EVENTS ──────────────────────────────────────────────────────
  event_hub: {
    id: 'event_hub', name: 'Eventi', category: 'event', family: 'event_dungeon',
    description: 'Hub centrale eventi attivi.',
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: false,
    ...placeholder,
  },
  minor_event_placeholder: {
    id: 'minor_event_placeholder', name: 'Evento Minore (PLACEHOLDER)', category: 'event', family: 'event_dungeon',
    description: 'Slot evento minore.',
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 5, hasLiveWindow: true,
    rewardTableId: 'event_minor_reward_placeholder',
    ...placeholder,
  },
  normal_event_placeholder: {
    id: 'normal_event_placeholder', name: 'Evento Normale (PLACEHOLDER)', category: 'event', family: 'event_dungeon',
    description: 'Slot evento normale.',
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 3, hasLiveWindow: true,
    rewardTableId: 'event_normal_reward_placeholder',
    ...placeholder,
  },
  major_seasonal_event_placeholder: {
    id: 'major_seasonal_event_placeholder', name: 'Evento Stagionale Maggiore (PLACEHOLDER)', category: 'event', family: 'event_dungeon',
    description: 'Slot evento maggiore stagionale.',
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: false,
    baseEntries: 1, hasLiveWindow: true, hasRanking: true,
    rewardTableId: 'event_major_reward_placeholder',
    ...placeholder,
  },

  // ─── ENDGAME ─────────────────────────────────────────────────────
  tower_of_inferno: {
    id: 'tower_of_inferno', name: "Torre dell'Inferno", category: 'pve', family: 'tower',
    description: 'Torre infinita per progressione e milestone.',
    unlockAccountLevel: 60,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: true, baseAttempts: 1,
    rewardTableId: 'tower_reward_placeholder', milestoneTableId: 'tower_reward_placeholder',
    hasRanking: true,
    ...placeholder,
  },
  scale_of_olympus: {
    id: 'scale_of_olympus', name: "Scala dell'Olimpo", category: 'pve', family: 'tower',
    description: 'Endgame avanzato a livelli multipli.',
    unlockAccountLevel: 70,
    isRepeatable: true, hasEntryLimit: false, hasAttemptLimit: true, baseAttempts: 1,
    rewardTableId: 'tower_reward_placeholder', hasRanking: true,
    ...placeholder,
  },
  trials_of_pantheon: {
    id: 'trials_of_pantheon', name: 'Prove del Pantheon', category: 'pve', family: 'training',
    description: 'Trial endgame del Pantheon.',
    unlockAccountLevel: 80,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    baseEntries: 1, baseAttempts: 1, hasLiveWindow: true,
    ...placeholder,
  },
  thrones_of_eclipse: {
    id: 'thrones_of_eclipse', name: "Troni dell'Eclissi", category: 'pve', family: 'tower',
    description: 'Endgame supremo — cap mode.',
    unlockAccountLevel: 100,
    isRepeatable: true, hasEntryLimit: true, hasAttemptLimit: true,
    baseAttempts: 1, hasLiveWindow: true, hasRanking: true,
    ...placeholder,
  },
};

/** Lookup helper. */
export function getModeDefinition(id: string): ModeDefinition | undefined {
  return MODE_DEFINITIONS[id];
}

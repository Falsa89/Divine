/**
 * frontend/constants/materialRaid.ts
 *
 * PROJECT_MATERIAL_RAID_RUNTIME_PACK
 * Sentinella: v25 PUBLIC_SYNC_TAG_RESYNC_v25_MATERIAL_RAID_RUNTIME
 *
 * Tracks e stages canonici del Material Raid. Locked da Bible 202.
 * Tutto read-only / preview-only in questo pack. NESSUNA mutation.
 */

export type MaterialRaidTrackId =
  | 'gear_material_raid'
  | 'hero_growth_raid'
  | 'gem_material_raid'
  | 'rune_material_raid'
  | 'artifact_divine_material_raid';

export type MaterialRaidRuntimeState = 'open_preview' | 'locked_deferred';
export type MaterialRaidStageId = 'I' | 'II' | 'III' | 'IV' | 'V';

export type MaterialRaidTrack = {
  track_id: MaterialRaidTrackId;
  label_it: string;
  description_it: string;
  runtime_state: MaterialRaidRuntimeState;
};

export const MATERIAL_RAID_TRACKS: MaterialRaidTrack[] = [
  { track_id: 'gear_material_raid',            label_it: 'Raid Materiali Gear',           description_it: 'Fonte primaria per gear dust/shard/core/essence/orb.',          runtime_state: 'open_preview' },
  { track_id: 'hero_growth_raid',              label_it: 'Raid Crescita Eroe',             description_it: 'Materiali per hero level/star/ascension.',                       runtime_state: 'open_preview' },
  { track_id: 'gem_material_raid',             label_it: 'Raid Materiali Gemme',           description_it: 'Materiali per gem socket/upgrade. Sbloccato con Gem Socket pack.',runtime_state: 'locked_deferred' },
  { track_id: 'rune_material_raid',            label_it: 'Raid Materiali Rune',             description_it: 'Materiali per rune/scroll/talisman. Sbloccato con Rune pack.',  runtime_state: 'locked_deferred' },
  { track_id: 'artifact_divine_material_raid', label_it: 'Raid Materiali Artefatto/Divino', description_it: 'Frammenti per artifact e divine weapon 6★. Locked.',           runtime_state: 'locked_deferred' },
];

export const MATERIAL_RAID_STAGE_IDS: MaterialRaidStageId[] = ['I', 'II', 'III', 'IV', 'V'];

export const MATERIAL_RAID_RECOMMENDED_POWER: Record<MaterialRaidStageId, number> = {
  I:   5000,
  II:  15000,
  III: 45000,
  IV:  120000,
  V:   320000,
};

export const MATERIAL_RAID_REWARD_FAMILIES = {
  gear:                    ['gear_dust_common', 'gear_shard_uncommon', 'gear_core_rare', 'gear_essence_epic', 'gear_orb_legendary'],
  hero_growth:             ['hero_growth_dust', 'hero_growth_crystal', 'hero_growth_essence'],
  gem_locked:              ['gem_dust_common', 'gem_shard_rare'],
  rune_locked:             ['rune_paper_common', 'rune_paper_rare'],
  artifact_divine_locked:  ['artifact_fragment_locked', 'divine_fragment_locked'],
} as const;

export function describeRuntimeState(state: MaterialRaidRuntimeState): string {
  return state === 'open_preview' ? 'APERTO (preview)' : 'BLOCCATO (futuro)';
}

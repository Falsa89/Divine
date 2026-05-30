/**
 * frontend/constants/gearForge.ts
 *
 * PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PACK
 * Sentinella: v24 PUBLIC_SYNC_TAG_RESYNC_v24_GEAR_FORGE_FUSION_REFORGE_RUNTIME
 *
 * Subsystems Forge canonici. Locked da Bible 202 + Gear Cap +50 pack.
 * Tutto read-only / preview-only in questo pack. NESSUNA mutation.
 */

export type ForgeSubsystemId = 'enhance' | 'fusion' | 'reforge' | 'enchant';
export type ForgeSubsystemRuntimeState =
  | 'preview_only_aware_of_cap_plus_50'
  | 'preview_only_commit_disabled_safety_audit'
  | 'preview_only_schema_only'
  | 'design_only_schema_only';

export type ForgeSubsystem = {
  id: ForgeSubsystemId;
  label_it: string;
  description_it: string;
  runtime_state: ForgeSubsystemRuntimeState;
};

export const FORGE_SUBSYSTEMS: ForgeSubsystem[] = [
  { id: 'enhance', label_it: 'Potenzia', description_it: 'Alza il +level del gear fino al cap canonico (+50, staged 10/20/35/50).', runtime_state: 'preview_only_aware_of_cap_plus_50' },
  { id: 'fusion',  label_it: 'Fondi',    description_it: 'Combina pezzi same-slot in eccesso per salire di grado/quality.',         runtime_state: 'preview_only_commit_disabled_safety_audit' },
  { id: 'reforge', label_it: 'Riforgia', description_it: 'Reroll dei sub-stat secondari mantenendo +level e quality.',              runtime_state: 'preview_only_schema_only' },
  { id: 'enchant', label_it: 'Incanta',  description_it: 'Aggiunge proprieta magiche temporanee/permanenti (design-only, futuro).', runtime_state: 'design_only_schema_only' },
];

export type FusionQuality = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' | 'mythic';
export const FUSION_QUALITIES: FusionQuality[] = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'];
export const FUSION_MIN_FODDER: number = 3;

export function describeSubsystemState(state: ForgeSubsystemRuntimeState): string {
  switch (state) {
    case 'preview_only_aware_of_cap_plus_50':           return 'PREVIEW (cap +50 aware)';
    case 'preview_only_commit_disabled_safety_audit':   return 'PREVIEW (commit disabled — safety audit)';
    case 'preview_only_schema_only':                    return 'PREVIEW (schema-only)';
    case 'design_only_schema_only':                     return 'DESIGN-ONLY (runtime disabled)';
  }
}

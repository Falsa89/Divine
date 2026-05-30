/**
 * frontend/constants/heroElevation.ts
 *
 * PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PACK
 * Sentinella: v22 PUBLIC_SYNC_TAG_RESYNC_v22_HERO_ELEVATION_RUNTIME
 *
 * Tier canonici dell'Hero Elevation / Quality Frame (Bianco/E0 \u2192 Rosso +3 / E14).
 * Separato da: Hero Level, Star Up, Ascensione, Skill Upgrade, Costellazioni,
 * Reincarnation, Gear, Gemme, Rune, Artifact, Divine Weapon.
 *
 * Tutto read-only / preview-only in questo pack. NESSUNA mutation.
 */

export type HeroElevationColorId = 'white' | 'green' | 'blue' | 'purple' | 'gold' | 'red';

export type HeroElevationTier = {
  tier_id: string;
  order: number;
  color_id: HeroElevationColorId;
  label_it: string;
  quality: 0 | 1 | 2 | 3;
  frame_color_hint: string;
};

export const HERO_ELEVATION_DEFAULT_TIER_ID = 'E0';

export const HERO_ELEVATION_TIERS: HeroElevationTier[] = [
  { tier_id: 'E0',  order: 0,  color_id: 'white',  label_it: 'Bianco',      quality: 0, frame_color_hint: '#e0e0ea' },
  { tier_id: 'E1',  order: 1,  color_id: 'green',  label_it: 'Verde',       quality: 0, frame_color_hint: '#3ddc84' },
  { tier_id: 'E2',  order: 2,  color_id: 'green',  label_it: 'Verde +1',    quality: 1, frame_color_hint: '#3ddc84' },
  { tier_id: 'E3',  order: 3,  color_id: 'blue',   label_it: 'Blu',         quality: 0, frame_color_hint: '#4a90e2' },
  { tier_id: 'E4',  order: 4,  color_id: 'blue',   label_it: 'Blu +1',      quality: 1, frame_color_hint: '#4a90e2' },
  { tier_id: 'E5',  order: 5,  color_id: 'blue',   label_it: 'Blu +2',      quality: 2, frame_color_hint: '#4a90e2' },
  { tier_id: 'E6',  order: 6,  color_id: 'purple', label_it: 'Viola +1',    quality: 1, frame_color_hint: '#a96bff' },
  { tier_id: 'E7',  order: 7,  color_id: 'purple', label_it: 'Viola +2',    quality: 2, frame_color_hint: '#a96bff' },
  { tier_id: 'E8',  order: 8,  color_id: 'purple', label_it: 'Viola +3',    quality: 3, frame_color_hint: '#a96bff' },
  { tier_id: 'E9',  order: 9,  color_id: 'gold',   label_it: 'Oro +1',      quality: 1, frame_color_hint: '#ffb84a' },
  { tier_id: 'E10', order: 10, color_id: 'gold',   label_it: 'Oro +2',      quality: 2, frame_color_hint: '#ffb84a' },
  { tier_id: 'E11', order: 11, color_id: 'gold',   label_it: 'Oro +3',      quality: 3, frame_color_hint: '#ffb84a' },
  { tier_id: 'E12', order: 12, color_id: 'red',    label_it: 'Rosso +1',    quality: 1, frame_color_hint: '#ff5470' },
  { tier_id: 'E13', order: 13, color_id: 'red',    label_it: 'Rosso +2',    quality: 2, frame_color_hint: '#ff5470' },
  { tier_id: 'E14', order: 14, color_id: 'red',    label_it: 'Rosso +3',    quality: 3, frame_color_hint: '#ff5470' },
];

/** Resolve a tier by id, with fallback to E0 if missing/unknown. */
export function resolveHeroElevationTier(tierId?: string | null): HeroElevationTier {
  if (!tierId) return HERO_ELEVATION_TIERS[0];
  const found = HERO_ELEVATION_TIERS.find((t) => t.tier_id === tierId);
  return found || HERO_ELEVATION_TIERS[0];
}

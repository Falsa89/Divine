/**
 * PROJECT_TOWER_OF_THE_HELLS_RUNTIME — Floor catalog (TEST MVP)
 *
 * 20 floors design-only client-side. Boss markers ogni 5 floors.
 * TUTTO PLACEHOLDER. asset_status=test_placeholder. replace_before_release=true.
 *
 * Vincoli:
 *  - NO stamina cost (no_stamina canonical pack 183)
 *  - NO monetized attempts
 *  - NO backend write
 *  - NO economy mutation
 *  - first_clear_reward = solo UI badge design-only
 */

export interface TowerFloorTestPlaceholder {
  readonly id: number;
  readonly name: string;
  readonly is_boss: boolean;
  readonly recommended_team_power_test: number;
  readonly first_clear_reward_design_label: string;
  readonly asset_status: 'test_placeholder';
  readonly replace_before_release: true;
}

const BOSS_EVERY = 5;

function makeFloor(i: number): TowerFloorTestPlaceholder {
  const isBoss = i % BOSS_EVERY === 0;
  const baseName = isBoss ? `Boss Floor ${i} (TEST)` : `Floor ${i} (TEST)`;
  return {
    id: i,
    name: baseName,
    is_boss: isBoss,
    recommended_team_power_test: 1000 + i * 250,
    first_clear_reward_design_label: isBoss
      ? `First Clear Badge \u2728 + Boss Mark (TEST, no economy)`
      : `First Clear Badge \u2728 (TEST, no economy)`,
    asset_status: 'test_placeholder',
    replace_before_release: true,
  };
}

export const TOWER_OF_THE_HELLS_FLOORS: readonly TowerFloorTestPlaceholder[] = Array.from(
  { length: 20 },
  (_v, idx) => makeFloor(idx + 1),
);

export const TOWER_OF_THE_HELLS_FLOOR_COUNT = TOWER_OF_THE_HELLS_FLOORS.length;
export const TOWER_OF_THE_HELLS_BOSS_EVERY = BOSS_EVERY;
export const TOWER_OF_THE_HELLS_MODE_ID = 'tower_of_the_hells' as const;
export const TOWER_OF_THE_HELLS_LOCAL_PROGRESS_KEY = 'tower_of_the_hells_local_progress_v1';

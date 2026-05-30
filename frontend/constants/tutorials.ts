/**
 * frontend/constants/tutorials.ts
 *
 * PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK
 * Sentinella: v19 PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL
 *
 * Registry runtime dei tutorial. Completion locale via AsyncStorage (vedi tutorialStorage.ts).
 * Wiring nelle schermate target (Tower/Home) e\u2019 DEFERRED a pack futuri.
 */

export type TutorialTrigger =
  | 'app_first_launch'
  | 'mode_first_unlock'
  | 'feature_first_touch'
  | 'manual';

export type TutorialStep = {
  step: number;
  title_it: string;
  body_it: string;
};

export type TutorialEntry = {
  id: string;
  trigger: TutorialTrigger;
  category: string;
  target_mode_id?: string;
  target_feature?: string;
  steps: TutorialStep[];
  runtime_wired: boolean;
  runtime_wiring_status: string;
};

export const TUTORIAL_CONTENT_STATUS = 'test_content';
export const TUTORIAL_REPLACE_BEFORE_RELEASE = true;

export const TUTORIAL_ENTRIES: TutorialEntry[] = [
  {
    id: 'tutorial_initial_onboarding_v1',
    trigger: 'app_first_launch',
    category: 'getting_started',
    steps: [
      { step: 1, title_it: 'Benvenuto',                          body_it: 'PLACEHOLDER: messaggio di benvenuto.' },
      { step: 2, title_it: 'Esplora la Guida',                   body_it: 'PLACEHOLDER: punta alla schermata Guida.' },
      { step: 3, title_it: 'Combatti la tua prima battaglia',    body_it: 'PLACEHOLDER.' },
    ],
    runtime_wired: false,
    runtime_wiring_status: 'DEFERRED_FUTURE_PACK',
  },
  {
    id: 'tutorial_tower_of_the_hells_first_unlock_v1',
    trigger: 'mode_first_unlock',
    category: 'modes',
    target_mode_id: 'tower_of_the_hells',
    steps: [
      { step: 1, title_it: 'Torre degli Inferi', body_it: '20 piani da scalare, boss ogni 5 piani.' },
      { step: 2, title_it: 'Niente Stamina',     body_it: 'Nessun costo stamina/ticket. Sali a tuo ritmo.' },
      { step: 3, title_it: 'Progresso locale',   body_it: 'In questa fase TEST, il progresso e\u2019 salvato sul dispositivo.' },
    ],
    runtime_wired: false,
    runtime_wiring_status: 'DEFERRED_FORBIDDEN_BY_PACK_NO_TOWER_GAMEPLAY_TOUCH',
  },
  {
    id: 'tutorial_team_columns_positioning_v1',
    trigger: 'feature_first_touch',
    category: 'team_columns_and_positioning',
    target_feature: 'team_columns_positioning',
    steps: [
      { step: 1, title_it: 'Tre colonne',  body_it: 'Avanguardia / DPS / Support.' },
      { step: 2, title_it: 'Avanguardia',  body_it: 'Eroi tank/duellanti davanti.' },
      { step: 3, title_it: 'DPS',          body_it: 'Eroi che fanno danno principale.' },
      { step: 4, title_it: 'Support',      body_it: 'Healer / buffer / debuffer.' },
    ],
    runtime_wired: false,
    runtime_wiring_status: 'DEFERRED_FUTURE_PACK',
  },
  {
    id: 'tutorial_active_battle_power_delta_v1',
    trigger: 'feature_first_touch',
    category: 'battle_power_and_power_delta',
    target_feature: 'active_battle_power_delta_overlay',
    steps: [
      { step: 1, title_it: 'Active Battle Power', body_it: 'POWER riassume la forza attuale del team.' },
      { step: 2, title_it: 'Variazioni +BP/-BP',  body_it: 'FUTURE_FEATURE: vedrai overlay +BP/-BP quando cambia il team.' },
    ],
    runtime_wired: false,
    runtime_wiring_status: 'DEFERRED_FUTURE_PACK',
  },
];

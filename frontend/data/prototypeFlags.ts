/**
 * Divine Waifus — Prototype Feature Flags (foundation data)
 * ──────────────────────────────────────────────────────────────
 * Pure data — NOT wired into runtime gating logic.
 * Provides a single source-of-truth for which roadmap features are
 * actually implemented vs placeholder vs concept-only.
 */
import type { PrototypeFeatureFlag } from '../types/prototypeFlags';

export const PROTOTYPE_FLAGS: Record<string, PrototypeFeatureFlag> = {
  treasury: {
    id: 'treasury',
    name: 'Tesoreria',
    isPrototypeEnabled: false,
    isVisibleInUI: false,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'foundation',
    notes: 'Frontend type/data foundation pronta. UI non implementata. Dipende da CURRENCY_DEFINITIONS + AuthContext wallet read.',
  },
  afk_autobattle: {
    id: 'afk_autobattle',
    name: 'AFK Autobattle',
    isPrototypeEnabled: false,
    isVisibleInUI: false,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'concept',
    notes: 'Pendente engine + UI + claim flow. ModeDefinition placeholder presente.',
  },
  hero_training: {
    id: 'hero_training',
    name: 'Addestramento Eroico (Trial)',
    isPrototypeEnabled: false,
    isVisibleInUI: false,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'foundation',
    notes: 'Placeholder ModeDefinitions + RewardTables presenti. UI/route mancano.',
  },
  hephaestus_forge: {
    id: 'hephaestus_forge',
    name: 'Fucina di Efesto',
    isPrototypeEnabled: true,           // backend forge route esiste
    isVisibleInUI: true,                // frontend forge.tsx esiste
    isPlaceholder: false,
    requiresDevMode: false,
    releasePhase: 'prototype',
    notes: 'Backend /api/forge upgrade/fuse + frontend equipment/forge screens già attivi. Data foundation aggiunta in 4.5-A.',
  },
  artifacts: {
    id: 'artifacts',
    name: 'Artefatti',
    isPrototypeEnabled: true,
    isVisibleInUI: false,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'prototype',
    notes: 'Backend artifacts route presente. Frontend UI dedicata non confermata. Type/data foundation pronta.',
  },
  arena: {
    id: 'arena',
    name: 'Arena PvP',
    isPrototypeEnabled: true,
    isVisibleInUI: true,
    isPlaceholder: false,
    requiresDevMode: false,
    releasePhase: 'prototype',
    notes: 'Frontend pvp.tsx + backend rankings esistono. Honor marks shop foundation aggiunta.',
  },
  event_hub: {
    id: 'event_hub',
    name: 'Event Hub',
    isPrototypeEnabled: false,
    isVisibleInUI: false,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'concept',
    notes: 'Backend DAILY_EVENTS list presente. UI hub aggregato mancante. Reward tables placeholder pronte.',
  },
  tower_placeholder: {
    id: 'tower_placeholder',
    name: 'Tower (Inferno/Olimpo/Eclissi)',
    isPrototypeEnabled: true,
    isVisibleInUI: true,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'prototype',
    notes: 'Frontend tower.tsx esistente con mock-data. Versioni endgame avanzate placeholder.',
  },
  battle_report_real_stats: {
    id: 'battle_report_real_stats',
    name: 'Battle Report Real Stats',
    isPrototypeEnabled: true,
    isVisibleInUI: true,
    isPlaceholder: false,
    requiresDevMode: false,
    releasePhase: 'beta',
    notes: 'damage_dealt + damage_received + healing_done + MVP REAL via backend (TASK 4.4-B/4.4-C). exp_to_next per hero ancora MOCK.',
  },
  legacy_stamina: {
    id: 'legacy_stamina',
    name: 'Legacy Stamina (runtime)',
    isPrototypeEnabled: true,
    isVisibleInUI: true,
    isPlaceholder: true,
    requiresDevMode: false,
    releasePhase: 'live',
    notes: 'Stamina/max_stamina ancora presenti su AuthContext.User. Final roadmap NON include global stamina. Migration deferred. Vedi CURRENCY_DEFINITIONS.legacy_stamina.',
  },
};

/** Lookup helper. */
export function getPrototypeFlag(id: string): PrototypeFeatureFlag | undefined {
  return PROTOTYPE_FLAGS[id];
}

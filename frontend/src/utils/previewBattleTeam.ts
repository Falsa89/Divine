/**
 * Pack 123 — Preview Battle Team utility (no-write, no-DB, no-grant).
 *
 * VINCOLI ASSOLUTI (rispettati al 100% — fail-closed):
 *   - Solo per preview mode (`is_preview === true`).
 *   - NON salva team, NON chiama endpoint backend mutanti, NON assegna eroi
 *     all'account, NON scrive AsyncStorage come team reale.
 *   - NON concede reward/EXP/progress/affinity/drop.
 *   - NON muta roster, gacha, shop, VIP, BP, IAP.
 *   - Snapshot deterministico e LOCAL-ONLY.
 *
 * EROI CANONICI:
 *   I 6 hero_id qui sotto sono REALI e presenti in `data/design/heroes_master.json`
 *   (release_group=launch_base, rarity 3*, no premium, no hidden, no placeholder).
 *   Coprono il 6v6: Tank / DPS Melee / DPS Ranged / Mage AoE / Support / Healer.
 *   Vietati esplicitamente: Borea, 6* premium, hidden, pending/placeholder.
 *
 * USO:
 *   Il consumer (`pre-battle-lobby.tsx`, `combat.tsx`, `tower-of-the-hells.tsx`,
 *   `hero-training.tsx`, `arena-preview.tsx`, `boss-raid-preview.tsx`) DEVE
 *   sempre passare attraverso `canUsePreviewTeamFallback()` e `buildPreviewLocalTeamSnapshot()`
 *   per generare il team. Mai costruire team fake in-place.
 */

export const PREVIEW_TEAM_BANNER_IT =
  "TEAM PREVIEW LOCALE — nessun eroe aggiunto all'account, nessun salvataggio, nessuna ricompensa";

export const PREVIEW_ALLOWED_MODES = [
  'story', 'tower', 'training', 'arena', 'boss', 'raid',
] as const;

export type PreviewMode = typeof PREVIEW_ALLOWED_MODES[number];

export type PreviewContext = {
  is_preview: boolean;
  reward_policy: string;
  progress_policy: string;
  battle_engine_mode: string;
  mode: string;
};

/**
 * 6 eroi canonici per il fallback locale 6v6.
 * Tutti 3* launch_base presenti in heroes_master.json.
 * Composizione: 1 Tank, 1 DPS Melee, 1 DPS Ranged, 1 Mage AoE, 1 Support, 1 Healer.
 */
export type PreviewHeroSlot = {
  hero_id: string;
  name_it: string;
  role: 'tank' | 'dps' | 'support' | 'healer';
  role_display: string;
  rarity: number;
  element: string;
  level: number;
  stars: number;
  power: number;
};

export const CANONICAL_PREVIEW_HERO_SLOTS: ReadonlyArray<PreviewHeroSlot> = [
  // Tank
  {
    hero_id: 'greek_hoplite',
    name_it: 'Hoplite',
    role: 'tank',
    role_display: 'Tank',
    rarity: 3,
    element: 'Terra',
    level: 10,
    stars: 3,
    power: 2400,
  },
  // DPS Melee
  {
    hero_id: 'norse_berserker',
    name_it: 'Berserker',
    role: 'dps',
    role_display: 'DPS Melee',
    rarity: 3,
    element: 'Fuoco',
    level: 10,
    stars: 3,
    power: 2600,
  },
  // DPS Ranged
  {
    hero_id: 'celtic_archer',
    name_it: 'Arciera',
    role: 'dps',
    role_display: 'DPS Ranged',
    rarity: 3,
    element: 'Vento',
    level: 10,
    stars: 3,
    power: 2550,
  },
  // Mage AoE
  {
    hero_id: 'arcane_lightning_enchantress',
    name_it: 'Incantatrice della Folgore',
    role: 'dps',
    role_display: 'Mage AoE',
    rarity: 3,
    element: 'Fulmine',
    level: 10,
    stars: 3,
    power: 2650,
  },
  // Support / Buffer
  {
    hero_id: 'greek_sanctuary_muse',
    name_it: 'Musa del Santuario',
    role: 'support',
    role_display: 'Support / Buffer',
    rarity: 3,
    element: 'Luce',
    level: 10,
    stars: 3,
    power: 2200,
  },
  // Healer
  {
    hero_id: 'angelic_priestess',
    name_it: 'Sacerdotessa',
    role: 'healer',
    role_display: 'Healer',
    rarity: 3,
    element: 'Luce',
    level: 10,
    stars: 3,
    power: 2150,
  },
] as const;

export const CANONICAL_PREVIEW_HERO_IDS: ReadonlyArray<string> =
  CANONICAL_PREVIEW_HERO_SLOTS.map((s) => s.hero_id);

/**
 * Verifica fail-closed: ritorna true SOLO se TUTTE le condizioni di preview
 * sono soddisfatte. In ogni dubbio: false (no fallback → blocker onesto).
 */
export function canUsePreviewTeamFallback(ctx: PreviewContext): boolean {
  if (ctx.is_preview !== true) return false;
  if (ctx.reward_policy !== 'preview') return false;
  if (ctx.progress_policy !== 'preview') return false;
  if (ctx.battle_engine_mode !== 'preview') return false;
  if (!(PREVIEW_ALLOWED_MODES as readonly string[]).includes(ctx.mode)) return false;
  return true;
}

export type PreviewTeamSnapshot = {
  is_preview_local_team: true;
  persistent: false;
  db_write: false;
  reward_allowed: false;
  progress_allowed: false;
  account_roster_mutation: false;
  gacha_mutation: false;
  shop_mutation: false;
  vip_mutation: false;
  bp_mutation: false;
  iap_mutation: false;
  hero_ids: string[];
  slots: PreviewHeroSlot[];
  banner: string;
  source: 'pack_123_preview_team_fallback';
  total_power: number;
};

/**
 * Costruisce uno snapshot deterministico LOCALE del team preview.
 * Restituisce `null` se il contesto non passa il fail-closed.
 */
export function buildPreviewLocalTeamSnapshot(
  ctx: PreviewContext,
): PreviewTeamSnapshot | null {
  if (!canUsePreviewTeamFallback(ctx)) {
    return null;
  }
  const slots = CANONICAL_PREVIEW_HERO_SLOTS.map((s) => ({ ...s }));
  const totalPower = slots.reduce((sum, s) => sum + s.power, 0);
  return {
    is_preview_local_team: true,
    persistent: false,
    db_write: false,
    reward_allowed: false,
    progress_allowed: false,
    account_roster_mutation: false,
    gacha_mutation: false,
    shop_mutation: false,
    vip_mutation: false,
    bp_mutation: false,
    iap_mutation: false,
    hero_ids: slots.map((s) => s.hero_id),
    slots,
    banner: PREVIEW_TEAM_BANNER_IT,
    source: 'pack_123_preview_team_fallback',
    total_power: totalPower,
  };
}

/**
 * Costruisce la query URL canonica per `/combat` in modalita' preview.
 * Tutti i campi richiesti dal Battle Launch Contract v1 sono passati
 * come query params separati cosicche' il parser combat.tsx (v107B)
 * possa validare l'envelope con `is_valid=true` e attivare
 * PREVIEW_REWARD_LOCK_ACTIVE (no simulate, no reward, no progress).
 *
 * IMPORTANTE: server_id='preview_local' e' una sentinella non-DB.
 */
export type BuildPreviewCombatUrlInput = {
  mode: PreviewMode;
  encounter_id: string;
  enemy_source_id: string;
  // Opzionali: enemy_source_type default 'authored', server_id default 'preview_local'.
  enemy_source_type?: string;
  server_id?: string;
  floor_id?: string | number;
  opponent_id?: string;
  boss_id?: string;
  trial_id?: string;
};

export function buildPreviewCombatUrl(input: BuildPreviewCombatUrlInput): string {
  const serverId = (input.server_id || 'preview_local').toString();
  const enemySourceType = (input.enemy_source_type || 'authored').toString();
  const launchContext = {
    server_id: serverId,
    mode: input.mode,
    encounter_id: input.encounter_id,
    player_team_id: null as string | null,
    player_team_snapshot: [],
    enemy_source_type: enemySourceType,
    enemy_source_id: input.enemy_source_id,
    reward_policy: 'preview',
    progress_policy: 'preview',
    battle_engine_mode: 'preview',
    idempotency_key: null as string | null,
    client_trace_id: `pack_123_${Date.now()}`,
  };
  const battleLaunchId = `pack_123_preview_${Date.now()}`;
  const qp: Record<string, string> = {
    mode: input.mode,
    encounter_id: input.encounter_id,
    enemy_source_type: enemySourceType,
    enemy_source_id: input.enemy_source_id,
    server_id: serverId,
    reward_policy: 'preview',
    progress_policy: 'preview',
    battle_engine_mode: 'preview',
    is_preview: 'true',
    launch_context: JSON.stringify(launchContext),
    battle_launch_id: battleLaunchId,
    source_id: input.enemy_source_id,
  };
  if (input.floor_id != null) qp.floor_id = String(input.floor_id);
  if (input.opponent_id) qp.opponent_id = input.opponent_id;
  if (input.boss_id) qp.boss_id = input.boss_id;
  if (input.trial_id) qp.trial_id = input.trial_id;
  const qs = Object.keys(qp)
    .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(qp[k])}`)
    .join('&');
  return `/combat?${qs}`;
}

/**
 * Costruisce la query URL canonica per `/pre-battle-lobby` in modalita' preview.
 * I parametri sono propagabili al combat downstream via la lobby stessa.
 */
export function buildPreviewLobbyUrl(input: BuildPreviewCombatUrlInput): string {
  const qp: Record<string, string> = {
    mode: input.mode,
    encounter_id: input.encounter_id,
    enemy_source_type: (input.enemy_source_type || 'authored').toString(),
    enemy_source_id: input.enemy_source_id,
    server_id: (input.server_id || 'preview_local').toString(),
    reward_policy: 'preview',
    progress_policy: 'preview',
    battle_engine_mode: 'preview',
    is_preview: 'true',
    source_id: input.enemy_source_id,
  };
  if (input.floor_id != null) qp.floor_id = String(input.floor_id);
  if (input.opponent_id) qp.opponent_id = input.opponent_id;
  if (input.boss_id) qp.boss_id = input.boss_id;
  if (input.trial_id) qp.trial_id = input.trial_id;
  const qs = Object.keys(qp)
    .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(qp[k])}`)
    .join('&');
  return `/pre-battle-lobby?${qs}`;
}

/**
 * Helper: deriva un PreviewContext leggibile da router params arbitrari.
 * Stringhe normalizzate; default conservativi (NON preview se mancano flag).
 */
export function previewContextFromParams(
  params: Record<string, unknown>,
): PreviewContext {
  const get = (k: string) => {
    const v = params[k];
    return v == null ? '' : String(v);
  };
  const isPreviewFlag = get('is_preview').toLowerCase() === 'true';
  const rewardPolicy = get('reward_policy');
  const progressPolicy = get('progress_policy');
  const battleEngineMode = get('battle_engine_mode');
  const mode = get('mode');
  // Fail-closed: tutti i flag preview devono essere presenti coerentemente.
  const coherentPreview =
    isPreviewFlag &&
    rewardPolicy === 'preview' &&
    progressPolicy === 'preview' &&
    battleEngineMode === 'preview';
  return {
    is_preview: coherentPreview,
    reward_policy: coherentPreview ? 'preview' : rewardPolicy,
    progress_policy: coherentPreview ? 'preview' : progressPolicy,
    battle_engine_mode: coherentPreview ? 'preview' : battleEngineMode,
    mode,
  };
}

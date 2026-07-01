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
 * Legacy builder neutralizzato da Pack 5D-3C.
 * Non deve piu' produrre direct `/combat` player-facing: chi lo richiama
 * viene mandato alla lobby, dove Pack 5D-3B blocca preview_local fail-closed.
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
    source_id: input.enemy_source_id,
    blocked: 'PREVIEW_LOCAL_LOBBY_DISABLED_PRE_QA',
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

// =========================================================================
// Pack 124 — Real Combat Preview Snapshot Builder.
// Genera teamA + teamB completi per il renderer combat (sprite/HUD reali)
// in modalita' PREVIEW. NESSUNA chiamata a `/api/battle/simulate`,
// NESSUN reward/EXP/progress.
//
// Caratteri compatibili con il rendering esistente di `combat.tsx`:
//   id, hero_id, hero_name, name, hero_image, rarity, element, level,
//   stars, role, max_hp, current_hp, max_hp_battle, is_alive, atk, def,
//   spd, grid_x, grid_y.
// =========================================================================

export type PreviewCombatUnit = {
  id: string;
  hero_id: string;
  hero_name: string;
  name: string;
  hero_image: null;
  image: null;
  rarity: number;
  element: string;
  level: number;
  stars: number;
  role: 'tank' | 'dps' | 'support' | 'healer';
  /** Pack 126 — faction derivata dal hero_id prefix (greek/norse/celtic/...). */
  faction: string;
  max_hp: number;
  current_hp: number;
  max_hp_battle: number;
  is_alive: true;
  atk: number;
  def: number;
  spd: number;
  rage: number;
  max_rage: number;
  grid_x: number;
  grid_y: number;
};

// Mappa hero_id canonico → archetipo enemy preview deterministico.
// Tutti gli ID elencati esistono in `heroes_master.json` (launch_base, 3*).
export const CANONICAL_PREVIEW_ENEMY_IDS: ReadonlyArray<{
  hero_id: string;
  name_it: string;
  role: 'tank' | 'dps' | 'support' | 'healer';
  rarity: number;
  element: string;
}> = [
  { hero_id: 'creature_coral_guardian', name_it: 'Guardiana di Corallo', role: 'tank', rarity: 3, element: 'Acqua' },
  { hero_id: 'norse_thunder_spear', name_it: 'Lancia del Tuono', role: 'dps', rarity: 3, element: 'Fulmine' },
  { hero_id: 'tides_corsair', name_it: 'Corsara delle Maree', role: 'dps', rarity: 3, element: 'Acqua' },
  { hero_id: 'egyptian_tide_sibyl', name_it: 'Sibilla delle Maree', role: 'dps', rarity: 3, element: 'Acqua' },
  { hero_id: 'celtic_moor_druidess', name_it: 'Druida della Brughiera', role: 'support', rarity: 3, element: 'Terra' },
  { hero_id: 'tides_healer', name_it: 'Guaritrice delle Maree', role: 'healer', rarity: 3, element: 'Acqua' },
] as const;

function slotToCombatUnit(
  slot: PreviewHeroSlot,
  idx: number,
  side: 'A' | 'B',
): PreviewCombatUnit {
  // Stat baseline deterministica per consentire al renderer di funzionare.
  // Tutti i valori sono LOCAL-ONLY e non impattano alcuna logica live.
  const baseHp = slot.role === 'tank' ? 16000 : slot.role === 'healer' ? 11000 : 12000;
  const baseAtk = slot.role === 'dps' ? 1600 : slot.role === 'healer' ? 900 : 1100;
  const baseDef = slot.role === 'tank' ? 1100 : slot.role === 'support' ? 800 : 700;
  // Pack 126 — Formation 6v6 nel layout battaglia approvato (vecchia
  // convenzione backend con X_MAP_A {1,4,7} → front/mid/back e Y_MAP
  // {1,4,7} → row 0/1/2). Mappiamo i 6 ruoli su 3 colonne × 2 righe:
  //   col 1 (front): tank (idx 0), dps melee (idx 1)
  //   col 4 (mid)  : dps ranged (idx 2), mage AoE (idx 3)
  //   col 7 (back) : support (idx 4), healer (idx 5)
  // In questo modo TUTTI i 6 eroi sono visibili nel layout 3-line approvato.
  const POS_BACKEND = [
    { grid_x: 1, grid_y: 1 }, // 0 tank   - front, top
    { grid_x: 1, grid_y: 4 }, // 1 dps M  - front, mid
    { grid_x: 4, grid_y: 1 }, // 2 dps R  - mid, top
    { grid_x: 4, grid_y: 4 }, // 3 mage   - mid, mid
    { grid_x: 7, grid_y: 1 }, // 4 supp   - back, top
    { grid_x: 7, grid_y: 4 }, // 5 heal   - back, mid
  ];
  const pos = POS_BACKEND[idx] || POS_BACKEND[POS_BACKEND.length - 1];
  // Faction derivata dal hero_id prefix (greek/norse/celtic/etc.).
  // Garantisce che battleBackgrounds.extractFaction risolva correttamente.
  const faction = (slot.hero_id.split('_')[0] || '').toLowerCase();
  return {
    id: `pack124_${side}_${slot.hero_id}_${idx}`,
    hero_id: slot.hero_id,
    hero_name: slot.name_it,
    name: slot.name_it,
    hero_image: null,
    image: null,
    rarity: slot.rarity,
    element: slot.element,
    level: slot.level,
    stars: slot.stars,
    role: slot.role,
    faction,
    max_hp: baseHp,
    current_hp: baseHp,
    max_hp_battle: baseHp,
    is_alive: true,
    atk: baseAtk,
    def: baseDef,
    spd: 100 + idx,
    rage: 0,
    max_rage: 100,
    grid_x: pos.grid_x,
    grid_y: pos.grid_y,
  };
}

export type PreviewCombatSnapshot = {
  is_preview_combat: true;
  reward_allowed: false;
  progress_allowed: false;
  db_write: false;
  simulate_endpoint_called: false;
  teamA: PreviewCombatUnit[];
  teamB: PreviewCombatUnit[];
  source: 'pack_124_preview_combat_snapshot';
  mode: string;
};

/**
 * Costruisce uno snapshot COMPLETO di combat preview con teamA (eroi canonici
 * preview) e teamB (avversari canonici preview). Fail-closed: ritorna null se
 * il contesto non e' preview-coerente.
 *
 * Output utilizzato in `combat.tsx` per popolare teamA/teamB e procedere al
 * renderer reale (`phase='preparing'` → `phase='fighting'`) SENZA chiamare
 * il backend `/api/battle/simulate`.
 */
export function buildPreviewCombatSnapshot(
  ctx: PreviewContext,
): PreviewCombatSnapshot | null {
  const teamSnapshot = buildPreviewLocalTeamSnapshot(ctx);
  if (!teamSnapshot) return null;
  const teamA = teamSnapshot.slots.map((s, i) => slotToCombatUnit(s, i, 'A'));
  // teamB: usa CANONICAL_PREVIEW_ENEMY_IDS — sono hero_id stub per visualizzare
  // il battlefield. NOTA: questi ID sono indicativi; se non esistono nel roster
  // canonico il renderer cade su placeholder iniziali (vedi renderHudCard).
  const teamB = CANONICAL_PREVIEW_ENEMY_IDS.map((e, i) =>
    slotToCombatUnit(
      {
        hero_id: e.hero_id,
        name_it: e.name_it,
        role: e.role,
        role_display: e.role,
        rarity: e.rarity,
        element: e.element,
        level: 10,
        stars: 3,
        power: 2500,
      },
      i,
      'B',
    ),
  );
  return {
    is_preview_combat: true,
    reward_allowed: false,
    progress_allowed: false,
    db_write: false,
    simulate_endpoint_called: false,
    teamA,
    teamB,
    source: 'pack_124_preview_combat_snapshot',
    mode: ctx.mode,
  };
}

// =========================================================================
// Pack 125 — Preview Battle Log Builder (deterministico, frontend-only).
// Genera un battle_log compatibile con `playLog(res, ti, ai)` di combat.tsx
// con almeno 3 turni e azioni reali (attack base / skill / heal) cosi' che
// gli sprite NON restino in idle. NESSUNA chiamata `/api/battle/simulate`,
// NESSUN reward/progress/DB write.
// =========================================================================

export type PreviewBattleAction = {
  type: 'attack' | 'heal' | 'dot' | 'dodge' | 'skip';
  skill_type?: 'nad' | 'sad' | 'sp';
  actor_id: string;
  actor: string;
  team: 'A' | 'B';
  element?: string;
  skill?: { name: string };
  total_damage?: number;
  crit?: boolean;
  amount?: number;
  target_id?: string;
  target?: string;
  damage?: number;
  targets?: Array<{
    id: string;
    name: string;
    killed: boolean;
    hp_before: number;
    hp_after: number;
  }>;
};

export type PreviewBattleTurn = {
  turn: number;
  actions: PreviewBattleAction[];
};

/**
 * Costruisce un battle_log deterministico minimo che fa scattare:
 *   - 3 turni
 *   - attacchi base 'nad' (Normal Attack Damage)
 *   - una skill 'sad' (Strong Active Damage)
 *   - un heal
 *   - reazioni hit/killed compatibili con renderer
 *
 * IMPORTANTE: i target referenziano `teamA[i].id` e `teamB[i].id` reali,
 * cosi' `updateHP(a)` aggiorna lo state corretto e gli sprite reagiscono.
 * Tutti i damage/heal sono finti ma proporzionati ai max_hp dei membri.
 */
export function buildPreviewBattleLog(
  teamA: PreviewCombatUnit[],
  teamB: PreviewCombatUnit[],
): PreviewBattleTurn[] {
  if (!teamA?.length || !teamB?.length) return [];
  // Slot references (deterministic indexing).
  const aTank = teamA[0];
  const aMelee = teamA[1];
  const aRanged = teamA[2];
  const aMage = teamA[3];
  const aSupport = teamA[4];
  const aHealer = teamA[5];
  const bTank = teamB[0];
  const bMelee = teamB[1];
  const bRanged = teamB[2];
  const bMage = teamB[3];
  const bSupport = teamB[4];
  const bHealer = teamB[5];
  // Helper: damage proporzionato al max_hp del target (no crit, no kill).
  const dmg = (target: PreviewCombatUnit, ratio: number) =>
    Math.round((target.max_hp || 10000) * ratio);
  const heal = (target: PreviewCombatUnit, ratio: number) =>
    Math.round((target.max_hp || 10000) * ratio);
  const target = (u: PreviewCombatUnit, dealt: number, prevHp: number) => ({
    id: u.id,
    name: u.hero_name || u.name,
    killed: false,
    hp_before: prevHp,
    hp_after: Math.max(1, prevHp - dealt),
  });

  // Turn 1: attacchi base reciproci (tank/melee/ranged).
  const t1: PreviewBattleAction[] = [
    {
      type: 'attack', skill_type: 'nad',
      actor_id: aTank.id, actor: aTank.hero_name, team: 'A', element: aTank.element,
      skill: { name: 'Affondo di Falange' },
      total_damage: dmg(bTank, 0.10), crit: false,
      targets: [target(bTank, dmg(bTank, 0.10), bTank.max_hp)],
    },
    {
      type: 'attack', skill_type: 'nad',
      actor_id: aMelee.id, actor: aMelee.hero_name, team: 'A', element: aMelee.element,
      skill: { name: 'Furia del Nord' },
      total_damage: dmg(bMelee, 0.12), crit: false,
      targets: [target(bMelee, dmg(bMelee, 0.12), bMelee.max_hp)],
    },
    {
      type: 'attack', skill_type: 'nad',
      actor_id: bTank.id, actor: bTank.hero_name, team: 'B', element: bTank.element,
      skill: { name: 'Carapace di Corallo' },
      total_damage: dmg(aTank, 0.08), crit: false,
      targets: [target(aTank, dmg(aTank, 0.08), aTank.max_hp)],
    },
  ];
  // Turn 2: skill + heal.
  const t2: PreviewBattleAction[] = [
    {
      type: 'attack', skill_type: 'sad',
      actor_id: aMage.id, actor: aMage.hero_name, team: 'A', element: aMage.element,
      skill: { name: 'Tempesta di Folgore' },
      total_damage: dmg(bMage, 0.18), crit: true,
      targets: [target(bMage, dmg(bMage, 0.18), bMage.max_hp)],
    },
    {
      type: 'heal',
      actor_id: aHealer.id, actor: aHealer.hero_name, team: 'A', element: aHealer.element,
      skill: { name: 'Benedizione Divina' },
      amount: heal(aTank, 0.15),
      target_id: aTank.id, target: aTank.hero_name,
    },
    {
      type: 'attack', skill_type: 'nad',
      actor_id: aRanged.id, actor: aRanged.hero_name, team: 'A', element: aRanged.element,
      skill: { name: 'Tiro Preciso' },
      total_damage: dmg(bRanged, 0.11), crit: false,
      targets: [target(bRanged, dmg(bRanged, 0.11), bRanged.max_hp)],
    },
  ];
  // Turn 3: enemy skill + chiusura.
  const t3: PreviewBattleAction[] = [
    {
      type: 'attack', skill_type: 'sad',
      actor_id: bMelee.id, actor: bMelee.hero_name, team: 'B', element: bMelee.element,
      skill: { name: 'Lancia del Tuono' },
      total_damage: dmg(aMelee, 0.16), crit: false,
      targets: [target(aMelee, dmg(aMelee, 0.16), aMelee.max_hp)],
    },
    {
      type: 'heal',
      actor_id: bHealer.id, actor: bHealer.hero_name, team: 'B', element: bHealer.element,
      skill: { name: 'Marea Curativa' },
      amount: heal(bTank, 0.12),
      target_id: bTank.id, target: bTank.hero_name,
    },
    {
      type: 'attack', skill_type: 'nad',
      actor_id: aSupport.id, actor: aSupport.hero_name, team: 'A', element: aSupport.element,
      skill: { name: 'Canto del Santuario' },
      total_damage: dmg(bSupport, 0.10), crit: false,
      targets: [target(bSupport, dmg(bSupport, 0.10), bSupport.max_hp)],
    },
  ];
  return [
    { turn: 1, actions: t1 },
    { turn: 2, actions: t2 },
    { turn: 3, actions: t3 },
  ];
}

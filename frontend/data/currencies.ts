/**
 * Divine Waifus — Currency static catalog (foundation)
 * ──────────────────────────────────────────────────────────────────
 * Pure static data — no side effects, no runtime wiring.
 *
 * Currency IDs are snake_case (stable across versions, mirrors backend
 * conventions). Final-design notes are inline; legacy runtime fields
 * (e.g. `gems`, `stamina`) are NOT removed in this task — they remain in
 * AuthContext.User and are referenced via the `legacy_stamina` /
 * `divine_crystals` placeholders below.
 *
 * VALUES ARE PLACEHOLDER — not final balance.
 */
import type { CurrencyDefinition } from '../types/economy';

export const CURRENCY_DEFINITIONS: Record<string, CurrencyDefinition> = {
  // ─── MAIN / VISIBLE IN HOME ───────────────────────────────────────
  gold: {
    id: 'gold',
    name: 'Oro',
    shortName: 'G',
    description: 'Valuta principale per upgrade, forge e shop di base.',
    icon: '🪙',
    category: 'standard',
    importance: 'primary',
    isPremium: false,
    isVisibleInHome: true,
    isVisibleInTreasury: true,
    sourceHints: ['battle_victory', 'daily_login', 'shop_purchase', 'mailbox'],
    spendHints: ['hero_levelup', 'forge_upgrade', 'shop_purchase'],
    relatedScreens: ['home', 'shop', 'forge', 'hero-detail', 'inventory'],
    sortOrder: 10,
  },
  divine_crystals: {
    id: 'divine_crystals',
    name: 'Cristalli Divini',
    shortName: 'CD',
    description: 'Valuta premium. Conceptually maps to current runtime `gems` (NOT wired yet — runtime still uses `gems` field on AuthContext.User).',
    icon: '💎',
    category: 'premium',
    importance: 'primary',
    isPremium: true,
    isVisibleInHome: true,
    isVisibleInTreasury: true,
    sourceHints: ['real_money_purchase', 'event_milestone', 'achievement'],
    spendHints: ['summon', 'extra_entries', 'shop_premium'],
    relatedScreens: ['home', 'gacha', 'shop'],
    sortOrder: 20,
  },
  account_exp: {
    id: 'account_exp',
    name: 'EXP Account',
    shortName: 'EXP',
    description: 'Esperienza account utilizzata per livello giocatore (sblocchi modi/feature). Risorsa di progressione, non spendibile direttamente.',
    icon: '⭐',
    category: 'standard',
    importance: 'primary',
    isPremium: false,
    isVisibleInHome: true,            // bar account level conceptually
    isVisibleInTreasury: false,        // non spendibile → fuori dal treasury
    sourceHints: ['battle_victory', 'first_clear', 'milestone'],
    spendHints: [],
    relatedScreens: ['home'],
    sortOrder: 30,
  },

  // ─── SUMMON SEALS ─────────────────────────────────────────────────
  summon_seal: {
    id: 'summon_seal',
    name: 'Sigillo di Evocazione',
    shortName: 'SE',
    description: 'Token di evocazione standard usato per banner permanenti.',
    icon: '🔯',
    category: 'standard',
    importance: 'secondary',
    isPremium: false,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['daily_login', 'event', 'milestone', 'mailbox'],
    spendHints: ['summon'],
    relatedScreens: ['gacha'],
    sortOrder: 40,
  },
  limited_summon_seal: {
    id: 'limited_summon_seal',
    name: 'Sigillo di Evocazione Limitata',
    shortName: 'SEL',
    description: 'Token di evocazione per banner limitati/event.',
    icon: '✨',
    category: 'event',
    importance: 'secondary',
    isPremium: false,
    expires: true,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['event', 'event_milestone', 'event_shop'],
    spendHints: ['summon_limited'],
    relatedScreens: ['gacha'],
    sortOrder: 41,
  },
  event_summon_seal: {
    id: 'event_summon_seal',
    name: 'Sigillo di Evocazione Evento',
    shortName: 'SEE',
    description: 'Token specifico di un evento. Scade a fine evento.',
    icon: '🎟️',
    category: 'event',
    importance: 'tertiary',
    isPremium: false,
    expires: true,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['event', 'event_shop'],
    spendHints: ['event_summon'],
    relatedScreens: ['gacha', 'event_hub'],
    sortOrder: 42,
  },

  // ─── SOCIAL / BOND ────────────────────────────────────────────────
  bond_points: {
    id: 'bond_points',
    name: 'Punti Legame',
    shortName: 'PL',
    description: 'Punti accumulati interagendo con altri giocatori (friendship summon, scambi sociali).',
    icon: '💞',
    category: 'soulbound',
    importance: 'tertiary',
    isPremium: false,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['friend_help', 'guild_activity', 'social'],
    spendHints: ['friendship_summon'],
    relatedScreens: ['gacha', 'guild'],
    sortOrder: 50,
  },

  // ─── PVP / RANKING ────────────────────────────────────────────────
  honor_marks: {
    id: 'honor_marks',
    name: "Marchi d'Onore",
    shortName: 'MO',
    description: 'Valuta PvP/Arena. Spendibile nel shop d’onore per equip/skill cosmetiche.',
    icon: '🏵️',
    category: 'ranking',
    importance: 'secondary',
    isPremium: false,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['arena_victory', 'arena_milestone', 'arena_ranking'],
    spendHints: ['honor_shop'],
    relatedScreens: ['pvp', 'shop'],
    sortOrder: 60,
  },

  // ─── GUILD / LIVE ─────────────────────────────────────────────────
  war_banners: {
    id: 'war_banners',
    name: 'Stendardi di Guerra',
    shortName: 'SG',
    description: 'Valuta gilda/live event (GvG, raid, conquest). Spendibile nel guild shop.',
    icon: '🚩',
    category: 'guild',
    importance: 'secondary',
    isPremium: false,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['guild_battle', 'live_event', 'gvg', 'raid_boss'],
    spendHints: ['guild_shop', 'war_banners_shop'],
    relatedScreens: ['guild', 'gvg', 'raids'],
    sortOrder: 70,
  },

  // ─── SEASON / PRESTIGE ────────────────────────────────────────────
  season_prestige_token: {
    id: 'season_prestige_token',
    name: 'Token Prestigio Stagione',
    shortName: 'TPS',
    description: 'Risorsa prestigio season (battle pass / season pass). Resetta a fine season.',
    icon: '🏆',
    category: 'event',
    importance: 'tertiary',
    isPremium: false,
    expires: true,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['season_pass', 'season_milestone'],
    spendHints: ['season_shop', 'prestige_unlock'],
    relatedScreens: ['shop'],
    sortOrder: 80,
  },

  // ─── EVENT / MODE PLACEHOLDERS ────────────────────────────────────
  event_currency_placeholder: {
    id: 'event_currency_placeholder',
    name: 'Valuta Evento (PLACEHOLDER)',
    description: 'Slot generico per valute event-specific. Eventi reali avranno il loro id dedicato.',
    icon: '🎉',
    category: 'event',
    importance: 'tertiary',
    isPremium: false,
    expires: true,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['event'],
    spendHints: ['event_shop'],
    relatedScreens: ['event_hub'],
    sortOrder: 90,
  },
  mode_currency_placeholder: {
    id: 'mode_currency_placeholder',
    name: 'Valuta Modalità (PLACEHOLDER)',
    description: 'Slot generico per valute mode-specific (es. tower_keys, trial_marks).',
    icon: '🗝️',
    category: 'special',
    importance: 'tertiary',
    isPremium: false,
    isVisibleInHome: false,
    isVisibleInTreasury: true,
    sourceHints: ['mode_progression'],
    spendHints: ['mode_shop'],
    relatedScreens: [],
    sortOrder: 95,
  },

  // ─── LEGACY (DO NOT REMOVE YET) ───────────────────────────────────
  legacy_stamina: {
    id: 'legacy_stamina',
    name: 'Stamina (LEGACY)',
    shortName: 'ST',
    description: 'Legacy runtime field still present in current code (AuthContext.User.stamina/max_stamina). Final roadmap has NO global stamina. This entry exists ONLY to formalize migration intent. Do NOT remove runtime stamina yet.',
    icon: '⚡',
    category: 'legacy_stamina',
    importance: 'tertiary',
    isPremium: false,
    isVisibleInHome: false,        // off in config — UI may still read runtime
    isVisibleInTreasury: false,
    sourceHints: ['legacy_regen'],
    spendHints: ['legacy_battle_entry'],
    relatedScreens: ['legacy'],
    sortOrder: 999,
  },
};

/** Lookup helper. Returns undefined if id is not registered. */
export function getCurrencyDefinition(id: string): CurrencyDefinition | undefined {
  return CURRENCY_DEFINITIONS[id];
}

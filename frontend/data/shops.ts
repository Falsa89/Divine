/**
 * Divine Waifus — Shop static catalog (foundation, PLACEHOLDER ONLY)
 * ─────────────────────────────────────────────────────────────────
 * No frontend/types/shops.ts exists yet — small LOCAL types defined here.
 * When shops graduate to a formal type contract, lift these into
 * `frontend/types/shops.ts` and import via barrel.
 *
 * NOT WIRED into existing shop UI. Pure data + tiny getter.
 */
import type { CurrencyId } from '../types/economy';
import type { RewardItem } from '../types/rewards';

// ─────────────────────────── Local types ────────────────────────────
export type ShopLimitType = 'daily' | 'weekly' | 'monthly' | 'season' | 'event' | 'lifetime' | 'unlimited';

export interface ShopItemDefinition {
  /** Stable snake_case id e.g. 'gold_pack_small'. */
  id: string;
  /** Display name (i18n-ready). */
  name: string;
  /** What the player gets when buying. */
  contents: RewardItem[];
  /** Cost (one of: currency cost, or material cost). */
  cost: { currencyId?: CurrencyId; materialId?: string; amount: number };
  /** Optional purchase cap per cycle. */
  limit?: number;
  /** Limit cycle. */
  limitType?: ShopLimitType;
  /** Optional UI flag for highlighted bundles. */
  isFeatured?: boolean;
}

export interface ShopSection {
  id: string;
  name: string;
  /** Hint for grouping/sorting in UI. */
  sortOrder?: number;
  items: ShopItemDefinition[];
}

export interface ShopDefinition {
  /** snake_case id. */
  id: string;
  name: string;
  /** Currency this shop primarily spends. */
  currencyId: CurrencyId;
  /** Optional secondary currencies accepted in this shop. */
  acceptedCurrencies?: CurrencyId[];
  description?: string;
  /** Default limit cycle for the entire shop (overridable per item). */
  limitType?: ShopLimitType;
  sections: ShopSection[];
  /** True if implementation is wired-up. */
  isPrototypeEnabled?: boolean;
  /** True if exposed in user-visible UI. */
  isVisibleInUI?: boolean;
}

// ─────────────────────────── Static data ────────────────────────────
export const SHOP_DEFINITIONS: Record<string, ShopDefinition> = {
  base_shop_placeholder: {
    id: 'base_shop_placeholder',
    name: 'Negozio Base',
    currencyId: 'gold',
    acceptedCurrencies: ['gold', 'divine_crystals'],
    description: 'Negozio base con materiali comuni.',
    limitType: 'daily',
    isPrototypeEnabled: false,
    isVisibleInUI: false,
    sections: [
      {
        id: 'common_materials', name: 'Materiali Comuni', sortOrder: 10,
        items: [
          { id: 'pack_minor_exp_tome',  name: '5x Tomo EXP Minore',  contents: [{ id: 'consumable:minor_exp_tome:5',  itemType: 'consumable', itemId: 'minor_exp_tome',  amount: 5 }], cost: { currencyId: 'gold', amount: 1500 }, limit: 5, limitType: 'daily' },
          { id: 'pack_basic_forge_ore', name: '10x Minerale Base',   contents: [{ id: 'material:basic_forge_ore:10',  itemType: 'material',   itemId: 'basic_forge_ore', amount: 10 }], cost: { currencyId: 'gold', amount: 2500 }, limit: 3, limitType: 'daily' },
        ],
      },
    ],
  },
  honor_marks_shop_placeholder: {
    id: 'honor_marks_shop_placeholder',
    name: "Negozio d'Onore",
    currencyId: 'honor_marks',
    description: "Spendi Marchi d'Onore in equipaggiamento PvP ed emblemi.",
    limitType: 'weekly',
    isPrototypeEnabled: false, isVisibleInUI: false,
    sections: [
      {
        id: 'role_emblems', name: 'Emblemi Ruolo', sortOrder: 10,
        items: [
          { id: 'pack_warrior_emblem', name: 'Emblema Guerriero', contents: [{ id: 'material:warrior_emblem:1', itemType: 'material', itemId: 'warrior_emblem', amount: 1 }], cost: { currencyId: 'honor_marks', amount: 200 }, limit: 5, limitType: 'weekly' },
          { id: 'pack_oracle_emblem',  name: 'Emblema Oracolo',   contents: [{ id: 'material:oracle_emblem:1',  itemType: 'material', itemId: 'oracle_emblem',  amount: 1 }], cost: { currencyId: 'honor_marks', amount: 200 }, limit: 5, limitType: 'weekly' },
        ],
      },
    ],
  },
  war_banners_shop_placeholder: {
    id: 'war_banners_shop_placeholder',
    name: 'Negozio della Gilda',
    currencyId: 'war_banners',
    description: 'Spendi Stendardi di Guerra in materiali endgame.',
    limitType: 'weekly',
    isPrototypeEnabled: false, isVisibleInUI: false,
    sections: [
      {
        id: 'endgame_materials', name: 'Materiali Endgame', sortOrder: 10,
        items: [
          { id: 'pack_refined_forge_ore', name: '5x Minerale Raffinato', contents: [{ id: 'material:refined_forge_ore:5', itemType: 'material', itemId: 'refined_forge_ore', amount: 5 }], cost: { currencyId: 'war_banners', amount: 300 }, limit: 4, limitType: 'weekly' },
          { id: 'pack_artifact_dust',     name: '10x Polvere Artefatti', contents: [{ id: 'material:artifact_dust:10',    itemType: 'material', itemId: 'artifact_dust',    amount: 10 }], cost: { currencyId: 'war_banners', amount: 250 }, limit: 4, limitType: 'weekly' },
        ],
      },
    ],
  },
  event_shop_placeholder: {
    id: 'event_shop_placeholder',
    name: 'Negozio Eventi',
    currencyId: 'event_currency_placeholder',
    description: 'Negozio temporaneo legato a un evento attivo.',
    limitType: 'event',
    isPrototypeEnabled: false, isVisibleInUI: false,
    sections: [
      {
        id: 'event_pulls', name: 'Sigilli', sortOrder: 10,
        items: [
          { id: 'pack_event_seal_1',     name: '1x Sigillo Evento', contents: [{ id: 'currency:event_summon_seal:1', itemType: 'currency', itemId: 'event_summon_seal',   amount: 1 }], cost: { currencyId: 'event_currency_placeholder', amount: 100 }, limit: 5, limitType: 'event' },
          { id: 'pack_limited_seal_1',   name: '1x Sigillo Limitato', contents: [{ id: 'currency:limited_seal:1',     itemType: 'currency', itemId: 'limited_summon_seal', amount: 1 }], cost: { currencyId: 'event_currency_placeholder', amount: 250 }, limit: 1, limitType: 'event', isFeatured: true },
        ],
      },
    ],
  },
  endgame_shop_placeholder: {
    id: 'endgame_shop_placeholder',
    name: 'Negozio Endgame',
    currencyId: 'season_prestige_token',
    description: 'Negozio cap-mode (Troni Eclissi / Crepuscolo Titani). Materiali finali.',
    limitType: 'season',
    isPrototypeEnabled: false, isVisibleInUI: false,
    sections: [
      {
        id: 'capstone_materials', name: 'Materiali Cap', sortOrder: 10,
        items: [
          { id: 'pack_reincarnation_core', name: '1x Nucleo Reincarnazione', contents: [{ id: 'material:reincarnation_core:1', itemType: 'material', itemId: 'reincarnation_core', amount: 1 }], cost: { currencyId: 'season_prestige_token', amount: 1500 }, limit: 1, limitType: 'season' },
          { id: 'pack_stellar_essence',    name: '3x Essenza Stellare',     contents: [{ id: 'material:stellar_essence:3',    itemType: 'material', itemId: 'stellar_essence',   amount: 3 }], cost: { currencyId: 'season_prestige_token', amount: 1800 }, limit: 1, limitType: 'season' },
        ],
      },
    ],
  },
};

/** Lookup helper. */
export function getShopDefinition(id: string): ShopDefinition | undefined {
  return SHOP_DEFINITIONS[id];
}

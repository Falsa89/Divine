/**
 * gemSocket.ts — PROJECT_GEM_SOCKET_RUNTIME_PACK (v27)
 *
 * Constants frontend per il sandbox Gem Socket. Tutto preview-only / read-only.
 * NESSUNA mutation, NESSUN premium gems spend, NESSUN material spend.
 *
 * Importante: Gemme = socket nei gear. Diverse da Rune (scroll/talisman su eroe) e
 * dalla valuta premium `gems`.
 */

export type GemFamilyId = 'ruby' | 'sapphire' | 'emerald' | 'topaz' | 'amethyst' | 'diamond';
export type GemTier = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' | 'divine';
export type GearSlotId = 'weapon' | 'armor' | 'helm' | 'boots' | 'gloves' | 'accessory';

export type GemFamily = {
  family_id: GemFamilyId;
  label_it: string;
  color: string;
  stat_family: string;
  preferred_slots: GearSlotId[];
  max_per_item_preview?: number;
};

export const GEM_FAMILIES: GemFamily[] = [
  { family_id: 'ruby',     label_it: 'Rubino',   color: '#ff5470', stat_family: 'attack',      preferred_slots: ['weapon','gloves','accessory'] },
  { family_id: 'sapphire', label_it: 'Zaffiro',  color: '#4a90e2', stat_family: 'defense',     preferred_slots: ['armor','helm'] },
  { family_id: 'emerald',  label_it: 'Smeraldo', color: '#44cc88', stat_family: 'hp',          preferred_slots: ['armor','helm','accessory'] },
  { family_id: 'topaz',    label_it: 'Topazio',  color: '#e8c44a', stat_family: 'speed',       preferred_slots: ['boots','accessory'] },
  { family_id: 'amethyst', label_it: 'Ametista', color: '#a96bff', stat_family: 'crit_chance', preferred_slots: ['weapon','gloves','accessory'] },
  { family_id: 'diamond',  label_it: 'Diamante', color: '#e8e8f0', stat_family: 'all_stat',    preferred_slots: ['weapon','armor','helm','boots','gloves','accessory'], max_per_item_preview: 1 },
];

export const GEM_TIERS: GemTier[] = ['common','uncommon','rare','epic','legendary','divine'];

export const MAX_SOCKETS_BY_RARITY: Record<number, number> = { 1:0, 2:0, 3:1, 4:1, 5:2, 6:3 };
export const SOCKET_LEVEL_UNLOCKS: Record<number, number> = { 1:10, 2:20, 3:35 };

export const GEAR_SLOTS_CANONICAL: GearSlotId[] = ['weapon','armor','helm','boots','gloves','accessory'];

export const SAFETY_BADGE_LABELS = {
  preview_only: 'PREVIEW-ONLY',
  no_db: 'DB WRITES = 0',
  no_premium: 'NO PREMIUM GEMS',
  no_live_commit: 'NO LIVE SOCKET COMMIT',
  no_rune_overlap: 'NON È RUNA',
} as const;

export function maxSocketsForRarity(rarity: number): number {
  return MAX_SOCKETS_BY_RARITY[rarity] ?? 0;
}
export function levelRequiredForSocket(socketIndex: number): number | null {
  return SOCKET_LEVEL_UNLOCKS[socketIndex] ?? null;
}

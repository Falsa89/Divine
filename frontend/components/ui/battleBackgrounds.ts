/**
 * Battle Background Resolver
 * ==========================
 * Fornisce lo sfondo della schermata battle in base a:
 *
 *  PRIORITÀ 1 (ASSOLUTA):
 *    Se la battaglia appartiene a una campagna/storyline, usa SEMPRE
 *    lo sfondo della fazione della campagna (anche se gli eroi sono
 *    di fazione diversa).
 *
 *  PRIORITÀ 2:
 *    Altrimenti (PvP, eventi, test, arena, raid, ecc.) usa la fazione
 *    dominante contando tutti gli eroi di entrambi i team.
 *    - tie-breaker: fazione dominante del solo Team A (player).
 *    - se ancora pareggio → nessuno sfondo (gradient neutro).
 *
 * Scelta deterministica per battaglia:
 *   pickBattleBackground() restituisce lo stesso bg se chiamato due
 *   volte con le stesse condizioni, MA introduce una variante random
 *   (1 o 2) al momento della scelta iniziale. Chi lo chiama deve
 *   memorizzare il risultato in state per mantenerlo stabile durante
 *   la fight (e rigenerarlo al retry/nuova battaglia).
 *
 * Asset mapping alias (DB → asset):
 *   greek     → greek_bg_*.png
 *   norse     → nordic_bg_*.png
 *   egyptian  → egypt_bg_*.png
 *   japanese  → japanese_bg_*.png
 *   celtic    → celtic_bg_*.png
 */
import { ImageSourcePropType } from 'react-native';
import { Asset } from 'expo-asset';

export type FactionKey = 'greek' | 'norse' | 'egyptian' | 'japanese' | 'celtic';

// ---- Asset registry ----------------------------------------------------------
// Mantenuto come array di 2 varianti per fazione.
// Nuovi asset futuri: aggiungere varianti a questi array.
const BG_REGISTRY: Record<FactionKey, ImageSourcePropType[]> = {
  greek: [
    require('../../assets/backgrounds/greek_bg_01.png'),
    require('../../assets/backgrounds/greek_bg_02.png'),
  ],
  norse: [
    require('../../assets/backgrounds/nordic_bg_01.png'),
    require('../../assets/backgrounds/nordic_bg_02.png'),
  ],
  egyptian: [
    require('../../assets/backgrounds/egypt_bg_01.png'),
    require('../../assets/backgrounds/egypt_bg_02.png'),
  ],
  japanese: [
    require('../../assets/backgrounds/japanese_bg_01.png'),
    require('../../assets/backgrounds/japanese_bg_02.png'),
  ],
  celtic: [
    require('../../assets/backgrounds/celtic_bg_01.png'),
    require('../../assets/backgrounds/celtic_bg_02.png'),
  ],
};

// Alias tolleranti: tradurre stringhe dal DB / param in chiavi registry.
// Nota: teniamo SOLO quelli confermati dal designer (no fantasiosi extra).
const FACTION_ALIASES: Record<string, FactionKey> = {
  greek: 'greek',
  greeks: 'greek',
  hellenic: 'greek',
  norse: 'norse',
  nordic: 'norse',
  viking: 'norse',
  egyptian: 'egyptian',
  egypt: 'egyptian',
  japanese: 'japanese',
  japan: 'japanese',
  celtic: 'celtic',
  celt: 'celtic',
  celts: 'celtic',
};

export function normalizeFaction(raw?: string | null): FactionKey | null {
  if (!raw) return null;
  const k = String(raw).trim().toLowerCase();
  return FACTION_ALIASES[k] || null;
}

// ---- Counting helpers --------------------------------------------------------
function extractFaction(hero: any): FactionKey | null {
  if (!hero) return null;
  // Il backend può chiamarlo in vari modi — accetta le forme più comuni
  const raw =
    hero.faction ||
    hero.hero_faction ||
    hero.factionKey ||
    hero.faction_id ||
    null;
  return normalizeFaction(raw);
}

/**
 * Calcola la fazione con il conteggio più alto tra gli eroi passati.
 * Ritorna null se l'input è vuoto o se non ci sono fazioni riconoscibili.
 * In caso di pareggio al top ritorna null (→ tie non risolto qui).
 */
function dominantFaction(heroes: any[] | null | undefined): FactionKey | null {
  if (!heroes || !heroes.length) return null;
  const counts: Partial<Record<FactionKey, number>> = {};
  heroes.forEach(h => {
    const f = extractFaction(h);
    if (f) counts[f] = (counts[f] || 0) + 1;
  });
  const entries = Object.entries(counts) as [FactionKey, number][];
  if (!entries.length) return null;
  entries.sort((a, b) => b[1] - a[1]);
  if (entries.length === 1) return entries[0][0];
  // Tie al top → ritorna null (non risolto)
  if (entries[0][1] === entries[1][1]) return null;
  return entries[0][0];
}

// ---- Public API --------------------------------------------------------------

export interface BattleBgContext {
  /** Se la battaglia è parte di una campagna/storyline. */
  campaignFaction?: string | null;
  /** Team A (player). */
  teamA?: any[] | null;
  /** Team B (enemy). */
  teamB?: any[] | null;
  /**
   * Indice della variante da usare (0 o 1). Se omesso viene generato random.
   * Passare un valore fisso per determinismo (es. memorizzato in useState).
   */
  variantIndex?: number;
}

export interface BattleBgResult {
  /** Source dell'Image da usare come sfondo. null = usa gradient di fallback. */
  source: ImageSourcePropType | null;
  /** Fazione risolta (debug/telemetria). */
  faction: FactionKey | null;
  /** Motivo della scelta (debug). */
  reason: 'campaign' | 'dominant_both' | 'dominant_player' | 'fallback_gradient';
  /** Indice variante scelto (0/1), utile per memorizzare in state. */
  variantIndex: number;
}

/**
 * Risolve lo sfondo della battle screen seguendo le regole di priorità.
 * NON è puro se variantIndex è omesso (genera random): il chiamante è
 * responsabile di "congelare" il risultato in state per mantenerlo
 * deterministico durante la fight.
 */
export function pickBattleBackground(ctx: BattleBgContext): BattleBgResult {
  const variantIndex =
    typeof ctx.variantIndex === 'number'
      ? Math.max(0, Math.min(1, Math.floor(ctx.variantIndex)))
      : Math.random() < 0.5 ? 0 : 1;

  // PRIORITÀ 1 — Campaign
  const campaignKey = normalizeFaction(ctx.campaignFaction);
  if (campaignKey && BG_REGISTRY[campaignKey]) {
    const arr = BG_REGISTRY[campaignKey];
    return {
      source: arr[variantIndex % arr.length],
      faction: campaignKey,
      reason: 'campaign',
      variantIndex,
    };
  }

  // PRIORITÀ 2 — Dominant across both teams
  const allHeroes = [
    ...((ctx.teamA as any[]) || []),
    ...((ctx.teamB as any[]) || []),
  ];
  const dominantBoth = dominantFaction(allHeroes);
  if (dominantBoth && BG_REGISTRY[dominantBoth]) {
    const arr = BG_REGISTRY[dominantBoth];
    return {
      source: arr[variantIndex % arr.length],
      faction: dominantBoth,
      reason: 'dominant_both',
      variantIndex,
    };
  }

  // Tie-breaker — Dominant Team A only
  const dominantA = dominantFaction(ctx.teamA as any[] | null | undefined);
  if (dominantA && BG_REGISTRY[dominantA]) {
    const arr = BG_REGISTRY[dominantA];
    return {
      source: arr[variantIndex % arr.length],
      faction: dominantA,
      reason: 'dominant_player',
      variantIndex,
    };
  }

  // Fallback — gradient neutro (source = null)
  return {
    source: null,
    faction: null,
    reason: 'fallback_gradient',
    variantIndex,
  };
}

/**
 * Preload (decode + cache) di un asset locale richiesto con require().
 * Cross-platform: su native scarica/decodifica in memoria, su web pre-carica
 * l'URL fetched. Se l'asset è null o l'operazione fallisce, ritorna comunque
 * (non blocca la battle — la pipeline riprende col fallback gradient).
 */
export async function preloadBattleAsset(source: ImageSourcePropType | null | undefined): Promise<boolean> {
  if (!source) return true;
  try {
    const asset = Asset.fromModule(source as any);
    if (!asset.downloaded) {
      await asset.downloadAsync();
    }
    return true;
  } catch (e) {
    // Non blocchiamo la battle se il preload fallisce: il rendering sarà
    // comunque eseguito, con un possibile pop-in visivo invece di crash.
    return false;
  }
}

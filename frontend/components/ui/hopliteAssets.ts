/**
 * Greek Hoplite asset helpers
 * ----------------------------
 * Centralizza il riferimento al personaggio Greek Hoplite in tutto il frontend.
 * - SPLASH: splash art ufficiale (usata in lista eroi, dettaglio, fullscreen)
 * - COMBAT_BASE: pose combattimento (usata SOLO per il rig animato / preview tecnico)
 * - RIG_BASE_SIZE: dimensione del canvas del rig (1024)
 *
 * ID ufficiale: 'greek_hoplite'
 * NAME ufficiale: 'Greek Hoplite'
 *
 * NON mappare su altri eroi (Athena, ecc.): Greek Hoplite è un eroe standalone.
 */
import { ImageSourcePropType } from 'react-native';

export const GREEK_HOPLITE_ID = 'greek_hoplite';
export const GREEK_HOPLITE_NAME = 'Hoplite';
/** Nomi alternativi che rimandano allo stesso asset (backward compat + match tollerante). */
const HOPLITE_NAME_ALIASES = ['hoplite', 'greek hoplite', 'spartana'];

// Marker per il campo hero_image sul backend quando vogliamo segnalare
// "usa la splash locale" invece di un URL remoto.
export const GREEK_HOPLITE_IMAGE_SENTINEL = 'asset:greek_hoplite:splash';

// ──────────────────────────────────────────────────────────────────────
// ECCEZIONE STORICA ASSET (Msg 424):
// I file di greek_hoplite NON seguono la convenzione standard.
//  - base.png   → è il VERO splash/card (UI piccolo, homepage, collection)
//  - splash.png → è in realtà il DETAIL/fullscreen art
// I file non vengono rinominati per non rompere storia git/cache.
// Il mapping qui rispetta il loro vero utilizzo UX.
// Vedi /app/frontend/components/ui/heroAssetManifest.ts per la convenzione
// pulita che seguiranno TUTTI i prossimi eroi (card.png / detail.png / combat_base.png).
// ──────────────────────────────────────────────────────────────────────

// Card art = splash piccolo per UI (list / homepage / collection grid)
export const GREEK_HOPLITE_CARD: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/base.png');

// Detail art = fullscreen grande (santuario, hero-detail, encyclopedia)
export const GREEK_HOPLITE_DETAIL: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/splash.png');

// Alias legacy: molti consumer esistenti usano GREEK_HOPLITE_SPLASH.
// Lo manteniamo PUNTANDO AL CARD (quello corretto per UI piccolo).
// Se serve il fullscreen, usare esplicitamente GREEK_HOPLITE_DETAIL.
export const GREEK_HOPLITE_SPLASH: ImageSourcePropType = GREEK_HOPLITE_CARD;

// Combat base = usata solo dal rig / preview, NON come immagine principale
export const GREEK_HOPLITE_COMBAT_BASE: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/combat_base.png');

export function isGreekHoplite(heroId?: string | null, heroName?: string | null): boolean {
  if (!heroId && !heroName) return false;
  if (heroId && String(heroId).toLowerCase() === GREEK_HOPLITE_ID) return true;
  if (heroName) {
    const n = String(heroName).toLowerCase().trim();
    if (HOPLITE_NAME_ALIASES.includes(n)) return true;
  }
  return false;
}

/** True se l'URL è il sentinel asset (non un vero URL remoto). */
export function isHopliteSentinel(imageUrl?: string | null): boolean {
  return !!imageUrl && String(imageUrl).startsWith('asset:greek_hoplite');
}

/**
 * Risolve il source per contesti UI PICCOLI (list / card / homepage splash / collection).
 * Per Hoplite → base.png (vero splash)
 * Per altri eroi → {uri: remoteUrl}
 * Ritorna null se non c'è nulla da mostrare.
 */
export function resolveHeroImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  if (isGreekHoplite(heroId, heroName)) return GREEK_HOPLITE_CARD;
  if (imageUrl && imageUrl.startsWith('asset:greek_hoplite')) return GREEK_HOPLITE_CARD;
  if (imageUrl) return { uri: imageUrl };
  return null;
}

/**
 * Risolve il source per FULLSCREEN / DETAIL grande (santuario, hero-detail, encyclopedia).
 * Per Hoplite → splash.png (il vero fullscreen art)
 * Per altri eroi → {uri: remoteUrl} (non abbiamo ancora detail separati per gli altri)
 */
export function resolveHeroDetailImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  if (isGreekHoplite(heroId, heroName)) return GREEK_HOPLITE_DETAIL;
  if (imageUrl && imageUrl.startsWith('asset:greek_hoplite')) return GREEK_HOPLITE_DETAIL;
  if (imageUrl) return { uri: imageUrl };
  return null;
}

/**
 * Versione UI-safe senza null (ritorna {uri:''} se mancante).
 * Usa questa SOLO per UI (list/detail/fullscreen viewer), mai in battle.
 */
export function heroImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType {
  const src = resolveHeroImageSource(imageUrl, heroId, heroName);
  if (src) return src;
  return { uri: '' };
}

/**
 * Risolve il source di un'Image eroe per il contesto BATTLE.
 *  - Per Hoplite → COMBAT_BASE (pose laterale da combattimento)
 *  - Per il sentinel backend (es. asset:greek_hoplite:splash) → COMBAT_BASE
 *  - Per altri eroi → {uri: remoteUrl}
 *
 * Non ritorna mai la splash per Hoplite: la splash è solo UI.
 */
export function heroBattleImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType {
  if (isGreekHoplite(heroId, heroName)) return GREEK_HOPLITE_COMBAT_BASE;
  if (imageUrl && imageUrl.startsWith('asset:greek_hoplite')) return GREEK_HOPLITE_COMBAT_BASE;
  if (imageUrl) return { uri: imageUrl };
  return { uri: '' };
}

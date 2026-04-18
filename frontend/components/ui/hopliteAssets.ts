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

// Splash art = immagine PRINCIPALE (lista / dettaglio / fullscreen)
export const GREEK_HOPLITE_SPLASH: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/splash.png');

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
 * Risolve il source di un'Image eroe per contesti UI (list / detail / fullscreen viewer).
 * Per Hoplite → splash.png
 * Per il sentinel backend → splash.png
 * Per altri eroi → {uri: remoteUrl}
 * Ritorna null se non c'è nulla da mostrare.
 */
export function resolveHeroImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  if (isGreekHoplite(heroId, heroName)) return GREEK_HOPLITE_SPLASH;
  if (imageUrl && imageUrl.startsWith('asset:greek_hoplite')) return GREEK_HOPLITE_SPLASH;
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

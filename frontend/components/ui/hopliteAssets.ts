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
export const GREEK_HOPLITE_NAME = 'Greek Hoplite';

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
  if (heroName && String(heroName).toLowerCase().trim() === GREEK_HOPLITE_NAME.toLowerCase()) return true;
  return false;
}

/**
 * Risolve il source di un'Image eroe.
 * Se è Greek Hoplite o se image è il sentinel, ritorna la splash locale.
 * Altrimenti ritorna {uri: imageUrl} per le immagini remote.
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

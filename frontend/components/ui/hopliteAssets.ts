/**
 * Greek Hoplite asset helpers + role-based hero image resolver
 * ─────────────────────────────────────────────────────────────
 * Centralizza il riferimento al personaggio Greek Hoplite e definisce un
 * resolver generico ROLE-BASED per immagini hero in tutto il frontend.
 *
 * ┌───────────────────────────────────────────────────────────────────┐
 * │ ASSET REALI HOPLITE (verificato via PIL su file fisici Apr 2025): │
 * │  - base.png         → 682×1024 RGBA, ALPHA=0 ai corner            │
 * │                       = cutout TRASPARENTE (no background)        │
 * │  - splash.png       → 1024×1536 RGB (no alpha)                    │
 * │                       = portrait CON SFONDO (full art)            │
 * │  - combat_base.png  → 1024×1024 RGBA, sprite battle (rig)         │
 * └───────────────────────────────────────────────────────────────────┘
 *
 * RUOLI (HeroImageRole) — usare questi al posto dei nomi di file:
 *   - 'transparent' → cutout senza sfondo. Es: Home splash che si fonde
 *                     col gradient della scena, overlay decorativi.
 *   - 'card'        → portrait CON SFONDO. Default per qualsiasi card UI:
 *                     team-select, post-battle summary, hero list grid,
 *                     hero-detail header, encyclopedia, top HUD battle.
 *   - 'detail'      → fullscreen detail art (sanctuary, hero-viewer).
 *                     Stesso file di 'card' per Hoplite oggi.
 *
 * Per gli ALTRI eroi: oggi abbiamo un solo URL remoto per hero → tutti i
 * ruoli ritornano {uri: imageUrl}. Quando in futuro avremo varianti
 * trasparent/card/detail per altri eroi, basterà estendere il resolver.
 *
 * ID ufficiale: 'greek_hoplite' · NAME ufficiale: 'Greek Hoplite'
 * NON mappare su altri eroi (Athena, ecc.): Greek Hoplite è standalone.
 */
import { ImageSourcePropType } from 'react-native';

export const GREEK_HOPLITE_ID = 'greek_hoplite';
export const GREEK_HOPLITE_NAME = 'Hoplite';
/** Nomi alternativi che rimandano allo stesso asset (backward compat + match tollerante). */
const HOPLITE_NAME_ALIASES = ['hoplite', 'greek hoplite', 'spartana'];

// Marker per il campo hero_image sul backend quando vogliamo segnalare
// "usa l'asset locale" invece di un URL remoto. Il resolver lo rileva e
// torna l'asset Hoplite corretto in base al ruolo richiesto.
export const GREEK_HOPLITE_IMAGE_SENTINEL = 'asset:greek_hoplite:splash';

// ──────────────────────────────────────────────────────────────────────
// ASSET LOCALI HOPLITE
// ──────────────────────────────────────────────────────────────────────

/** TRASPARENTE — cutout su sfondo alpha=0. Per Home overlay, decoratori. */
export const GREEK_HOPLITE_TRANSPARENT: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/base.png');

/** CARD/PORTRAIT — splash art CON SFONDO. Default per UI card/list/team-select/post-battle. */
export const GREEK_HOPLITE_PORTRAIT: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/splash.png');

/** DETAIL — fullscreen art (santuario, hero-viewer). Stesso file di PORTRAIT. */
export const GREEK_HOPLITE_DETAIL: ImageSourcePropType = GREEK_HOPLITE_PORTRAIT;

/** Combat base — sprite per battle/rig. NON usare come immagine card UI. */
export const GREEK_HOPLITE_COMBAT_BASE: ImageSourcePropType = require('../../assets/heroes/greek_hoplite/combat_base.png');

// ── LEGACY ALIASES — preservati per i call-site che li importano ──────
// Tutti i consumer storici di `GREEK_HOPLITE_CARD` si aspettano la
// versione TRASPARENTE (base.png) — la lasciamo invariata per non
// rompere Home / overlay decorativi che dipendono da questo nome.
/** @deprecated Usa GREEK_HOPLITE_TRANSPARENT (semantica più chiara). */
export const GREEK_HOPLITE_CARD: ImageSourcePropType = GREEK_HOPLITE_TRANSPARENT;
/** @deprecated Usa GREEK_HOPLITE_TRANSPARENT (era alias di CARD). */
export const GREEK_HOPLITE_SPLASH: ImageSourcePropType = GREEK_HOPLITE_TRANSPARENT;

// ──────────────────────────────────────────────────────────────────────
// HERO IDENTITY HELPERS
// ──────────────────────────────────────────────────────────────────────
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

// ──────────────────────────────────────────────────────────────────────
// ROLE-BASED RESOLVER (canonical API — preferire questo)
// ──────────────────────────────────────────────────────────────────────

export type HeroImageRole = 'transparent' | 'card' | 'detail';

function hopliteAssetForRole(role: HeroImageRole): ImageSourcePropType {
  switch (role) {
    case 'transparent': return GREEK_HOPLITE_TRANSPARENT;
    case 'detail':      return GREEK_HOPLITE_DETAIL;
    case 'card':
    default:            return GREEK_HOPLITE_PORTRAIT;
  }
}

/**
 * Canonical resolver basato su RUOLO.
 * Preferire questa API: la semantica è esplicita e estendibile a future
 * varianti per-hero (oggi solo Hoplite ha varianti, gli altri hanno 1 URL).
 *
 * - role='transparent' → cutout senza sfondo (Home overlay)
 * - role='card'        → portrait con sfondo (DEFAULT, list/team/post-battle)
 * - role='detail'      → fullscreen detail (sanctuary/hero-viewer)
 *
 * Se imageUrl è un sentinel `asset:*` lo riconosciamo e torniamo
 * l'asset Hoplite corretto per il ruolo. Se è un URL valido remoto,
 * torniamo {uri: imageUrl} (gli altri eroi non hanno varianti separate).
 * Se non c'è nulla → null (caller mostri fallback).
 */
export function resolveHeroImageByRole(
  role: HeroImageRole,
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null,
): ImageSourcePropType | null {
  if (isGreekHoplite(heroId, heroName)) return hopliteAssetForRole(role);
  if (imageUrl && isHopliteSentinel(imageUrl)) return hopliteAssetForRole(role);
  if (imageUrl) return { uri: imageUrl };
  return null;
}

// ──────────────────────────────────────────────────────────────────────
// LEGACY API (preservata per backward compat — proxy al role resolver)
// ──────────────────────────────────────────────────────────────────────

/**
 * @deprecated Usa `resolveHeroImageByRole('transparent', ...)`.
 *
 * Storicamente tornava il "card art piccolo" che però oggi è il cutout
 * TRASPARENTE (base.png). Il significato semantico è "transparent": la
 * usano consumer come HomeHeroSplash che vogliono un overlay senza sfondo.
 *
 * NOTA: i call-site che vogliono un portrait CON SFONDO devono migrare a
 * `resolveHeroPortraitSource` o a `resolveHeroImageByRole('card', ...)`.
 */
export function resolveHeroImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  return resolveHeroImageByRole('transparent', imageUrl, heroId, heroName);
}

/**
 * @deprecated Usa `resolveHeroImageByRole('detail', ...)`.
 * Resolver per FULLSCREEN / DETAIL grande (santuario, hero-viewer).
 */
export function resolveHeroDetailImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  return resolveHeroImageByRole('detail', imageUrl, heroId, heroName);
}

/**
 * Resolver per PORTRAIT CARD CON SFONDO (team-select, post-battle,
 * hero list grid, top HUD, qualsiasi card non-Home). Ritorna splash art
 * con background per Hoplite, URL remoto per altri eroi, null fallback.
 */
export function resolveHeroPortraitSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType | null {
  return resolveHeroImageByRole('card', imageUrl, heroId, heroName);
}

// ──────────────────────────────────────────────────────────────────────
// UI-SAFE WRAPPERS (mai null — ritornano {uri:''} se mancante)
// ──────────────────────────────────────────────────────────────────────

/**
 * @deprecated Per nuovi consumer preferire `heroPortraitSource` se serve
 * uno sfondo, oppure `resolveHeroImageByRole('transparent', ...)` esplicito.
 *
 * UI-safe wrapper TRASPARENTE: ritorna `{uri:''}` come fallback null-safe
 * per Image. Mantiene comportamento legacy (base.png) per non rompere
 * call-site come Home overlay che dipendono dalla trasparenza.
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
 * UI-safe wrapper PORTRAIT (con sfondo): per qualsiasi card UI non-Home.
 * Ritorna splash art per Hoplite, URL remoto per altri, {uri:''} fallback.
 */
export function heroPortraitSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType {
  const src = resolveHeroPortraitSource(imageUrl, heroId, heroName);
  if (src) return src;
  return { uri: '' };
}

/**
 * Risolve il source di un'Image eroe per il contesto BATTLE (rig sprite).
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

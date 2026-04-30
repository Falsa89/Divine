/**
 * Hero asset helpers + role-based hero image resolver (multi-hero)
 * ─────────────────────────────────────────────────────────────
 * RM1.17 — Generalizzato da hoplite-only a multi-hero asset registry.
 * Path FILE invariato (`hopliteAssets.ts`) per backward-compat: tutti i
 * consumer storici importano già da qui. Aggiunto supporto Berserker
 * + scaffolding generico per futuri eroi con asset locali.
 *
 * SENTINEL PATTERN BACKEND:
 *   `asset:<hero_id>:<variant>`
 *   - `asset:greek_hoplite:splash`     (Hoplite — record DB esistente)
 *   - `asset:norse_berserker:splash`   (Berserker — record DB RM1.16)
 *
 * SUPPORTED VARIANTS (ad oggi): splash, combat_base, transparent.
 * Nuovi eroi seguono lo stesso pattern: registrare gli asset locali e
 * dichiarare l'identità in HERO_ASSET_REGISTRY.
 *
 * Centralizza il riferimento ai personaggi con asset locali e definisce
 * un resolver generico ROLE-BASED per immagini hero in tutto il frontend.
 *
 * ┌───────────────────────────────────────────────────────────────────┐
 * │ ASSET REALI HOPLITE (verificato via PIL su file fisici Apr 2025): │
 * │  - base.png         → 682×1024 RGBA, ALPHA=0 ai corner            │
 * │                       = cutout TRASPARENTE (no background)        │
 * │  - splash.png       → 1024×1536 RGB (no alpha)                    │
 * │                       = portrait CON SFONDO (full art)            │
 * │  - combat_base.png  → 1024×1024 RGBA, sprite battle (rig)         │
 * └───────────────────────────────────────────────────────────────────┘
 * ┌───────────────────────────────────────────────────────────────────┐
 * │ ASSET REALI BERSERKER (RM1.17):                                   │
 * │  - norse_berserker.jpg     → splash/portrait con sfondo full art  │
 * │  - berserker_sprites/idle.png → combat_base / pose laterale       │
 * │  - berserker_sprites/{attack,skill,hit,death}.png → battle anims  │
 * │  Note: nessuna variante 'transparent' dedicata → fallback a       │
 * │  splash (per Home overlay sembra accettabile, ma il record DB     │
 * │  Berserker NON è promosso ad hero della Home).                    │
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
 * Per gli ALTRI eroi non in HERO_ASSET_REGISTRY: oggi abbiamo un solo URL
 * remoto per hero → tutti i ruoli ritornano {uri: imageUrl}.
 */
import { ImageSourcePropType } from 'react-native';

// ════════════════════════════════════════════════════════════════════
// HOPLITE — record canonico Bible (preservato 100%)
// ════════════════════════════════════════════════════════════════════
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

// ════════════════════════════════════════════════════════════════════
// BERSERKER — record canonico Bible (RM1.16 seed, RM1.17 asset wire)
// ════════════════════════════════════════════════════════════════════
export const NORSE_BERSERKER_ID = 'norse_berserker';
export const NORSE_BERSERKER_NAME = 'Berserker';
/** Match tollerante per name lookup. */
const BERSERKER_NAME_ALIASES = ['berserker', 'norse berserker'];

/** Sentinel pattern: `asset:norse_berserker:*`. */
export const NORSE_BERSERKER_IMAGE_SENTINEL = 'asset:norse_berserker:splash';

/** SPLASH/PORTRAIT/DETAIL — full art con sfondo. */
export const NORSE_BERSERKER_PORTRAIT: ImageSourcePropType = require('../../assets/heroes/norse_berserker.jpg');
export const NORSE_BERSERKER_DETAIL: ImageSourcePropType = NORSE_BERSERKER_PORTRAIT;
/** Berserker non ha cutout transparent dedicato → fallback al portrait con sfondo. */
export const NORSE_BERSERKER_TRANSPARENT: ImageSourcePropType = NORSE_BERSERKER_PORTRAIT;
/** Combat base — pose idle laterale dal sprite sheet folder. */
export const NORSE_BERSERKER_COMBAT_BASE: ImageSourcePropType = require('../../assets/heroes/berserker_sprites/idle.png');

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

export function isNorseBerserker(heroId?: string | null, heroName?: string | null): boolean {
  if (!heroId && !heroName) return false;
  if (heroId && String(heroId).toLowerCase() === NORSE_BERSERKER_ID) return true;
  if (heroName) {
    const n = String(heroName).toLowerCase().trim();
    if (BERSERKER_NAME_ALIASES.includes(n)) return true;
  }
  return false;
}

/** True se l'URL è un sentinel asset per Hoplite (legacy specific). */
export function isHopliteSentinel(imageUrl?: string | null): boolean {
  return !!imageUrl && String(imageUrl).startsWith('asset:greek_hoplite');
}

/** True se l'URL è un sentinel asset per Berserker. */
export function isBerserkerSentinel(imageUrl?: string | null): boolean {
  return !!imageUrl && String(imageUrl).startsWith('asset:norse_berserker');
}

/** True se l'URL è un sentinel `asset:*` (qualsiasi hero). */
export function isHeroAssetSentinel(imageUrl?: string | null): boolean {
  return !!imageUrl && String(imageUrl).startsWith('asset:');
}

/**
 * Parse `asset:<hero_id>:<variant>`. Ritorna null su input non valido.
 * Variant default → 'splash' se mancante.
 */
export function parseHeroAssetSentinel(
  imageUrl?: string | null,
): { heroId: string; variant: string } | null {
  if (!imageUrl) return null;
  const s = String(imageUrl);
  if (!s.startsWith('asset:')) return null;
  const parts = s.split(':');
  // 'asset:<hero_id>' o 'asset:<hero_id>:<variant>'
  if (parts.length < 2 || !parts[1]) return null;
  return { heroId: parts[1], variant: parts[2] || 'splash' };
}

// ──────────────────────────────────────────────────────────────────────
// HERO ASSET REGISTRY
// ──────────────────────────────────────────────────────────────────────
type HeroAssetMap = {
  transparent: ImageSourcePropType;
  card: ImageSourcePropType;
  detail: ImageSourcePropType;
  combat_base: ImageSourcePropType;
};

/**
 * Registry centrale degli eroi con asset locali. Estendere QUESTO map per
 * aggiungere nuovi eroi ufficiali futuri (es. norse_eir, greek_athena, ...).
 * Chiave = canonical hero_id (Character Bible).
 */
const HERO_ASSET_REGISTRY: Record<string, HeroAssetMap> = {
  [GREEK_HOPLITE_ID]: {
    transparent: GREEK_HOPLITE_TRANSPARENT,
    card: GREEK_HOPLITE_PORTRAIT,
    detail: GREEK_HOPLITE_DETAIL,
    combat_base: GREEK_HOPLITE_COMBAT_BASE,
  },
  [NORSE_BERSERKER_ID]: {
    transparent: NORSE_BERSERKER_TRANSPARENT,
    card: NORSE_BERSERKER_PORTRAIT,
    detail: NORSE_BERSERKER_DETAIL,
    combat_base: NORSE_BERSERKER_COMBAT_BASE,
  },
};

/** Lookup hero ID dalla coppia (id, name). Risolve alias name. */
function resolveLocalHeroId(
  heroId?: string | null,
  heroName?: string | null,
): string | null {
  if (heroId) {
    const k = String(heroId).toLowerCase();
    if (HERO_ASSET_REGISTRY[k]) return k;
  }
  if (isGreekHoplite(heroId, heroName)) return GREEK_HOPLITE_ID;
  if (isNorseBerserker(heroId, heroName)) return NORSE_BERSERKER_ID;
  return null;
}

// ──────────────────────────────────────────────────────────────────────
// ROLE-BASED RESOLVER (canonical API — preferire questo)
// ──────────────────────────────────────────────────────────────────────

export type HeroImageRole = 'transparent' | 'card' | 'detail';

function localAssetForRole(
  localId: string,
  role: HeroImageRole,
): ImageSourcePropType | null {
  const m = HERO_ASSET_REGISTRY[localId];
  if (!m) return null;
  switch (role) {
    case 'transparent': return m.transparent;
    case 'detail':      return m.detail;
    case 'card':
    default:            return m.card;
  }
}

/**
 * Canonical resolver basato su RUOLO.
 * Preferire questa API: la semantica è esplicita e estendibile a future
 * varianti per-hero. Riconosce sia identità diretta (heroId/heroName) sia
 * sentinel `asset:<hero_id>:<variant>`.
 *
 * - role='transparent' → cutout senza sfondo (Home overlay)
 * - role='card'        → portrait con sfondo (DEFAULT, list/team/post-battle)
 * - role='detail'      → fullscreen detail (sanctuary/hero-viewer)
 */
export function resolveHeroImageByRole(
  role: HeroImageRole,
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null,
): ImageSourcePropType | null {
  // 1) Identity-based (heroId/heroName match registry)
  const localId = resolveLocalHeroId(heroId, heroName);
  if (localId) {
    const a = localAssetForRole(localId, role);
    if (a) return a;
  }
  // 2) Sentinel-based (asset:<hero_id>:<variant>)
  const parsed = parseHeroAssetSentinel(imageUrl);
  if (parsed && HERO_ASSET_REGISTRY[parsed.heroId]) {
    const a = localAssetForRole(parsed.heroId, role);
    if (a) return a;
  }
  // 3) Sentinel sconosciuto → graceful fallback (skip, treat as null URL)
  if (parsed) return null;
  // 4) URL remoto valido
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
 *  - Per heroes registrati (Hoplite, Berserker, ...) → COMBAT_BASE locale
 *  - Per sentinel `asset:<hero_id>:*` con asset locale → COMBAT_BASE locale
 *  - Per altri eroi → {uri: remoteUrl}
 *
 * Non ritorna mai la splash per eroi locali: la splash è solo UI.
 */
export function heroBattleImageSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null
): ImageSourcePropType {
  // 1) Identity-based registry lookup
  const localId = resolveLocalHeroId(heroId, heroName);
  if (localId && HERO_ASSET_REGISTRY[localId]) {
    return HERO_ASSET_REGISTRY[localId].combat_base;
  }
  // 2) Sentinel-based lookup
  const parsed = parseHeroAssetSentinel(imageUrl);
  if (parsed && HERO_ASSET_REGISTRY[parsed.heroId]) {
    return HERO_ASSET_REGISTRY[parsed.heroId].combat_base;
  }
  // 3) Sentinel sconosciuto → fallback safe
  if (parsed) return { uri: '' };
  // 4) URL remoto
  if (imageUrl) return { uri: imageUrl };
  return { uri: '' };
}

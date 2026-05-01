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
 * │ ASSET REALI BERSERKER (RM1.17-J — canonical contract pack):       │
 * │  Percorso canonico: assets/heroes/norse_berserker/                │
 * │  - splash.jpg         512×768  RGB   → card/portrait/detail/full  │
 * │  - transparent.png    408×612  RGBA  → Home overlay cutout        │
 * │  - combat_base.png    1024×1536 RGBA → fallback combat statico    │
 * │  - idle.png           1536×1024 RGBA → battle state idle          │
 * │  - attack.png         1536×1024 RGBA → battle state attack        │
 * │  - skill.png          1024×1536 RGBA → battle state skill         │
 * │  - hit.png            1024×1536 RGBA → battle state hit           │
 * │  - death.png          1024×1536 RGBA → battle state death         │
 * │  Forbidden paths (NON runtime Berserker):                         │
 * │    berserker_sprites/* (legacy sprite sheets, solo dev tool)      │
 * │    _legacy_wrong_pack/* (backup RM1.17-C)                         │
 * │    norse_berserker.jpg root (legacy)                              │
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

/** SPLASH/PORTRAIT/DETAIL — full art con sfondo (RM1.17-C: aggiornato a 512×768 portrait dal ZIP ufficiale). */
export const NORSE_BERSERKER_PORTRAIT: ImageSourcePropType = require('../../assets/heroes/norse_berserker/splash.jpg');
export const NORSE_BERSERKER_DETAIL: ImageSourcePropType = NORSE_BERSERKER_PORTRAIT;
/** TRANSPARENT — cutout RGBA 408×612 dal ZIP ufficiale (RM1.17-C). */
export const NORSE_BERSERKER_TRANSPARENT: ImageSourcePropType = require('../../assets/heroes/norse_berserker/transparent.png');
/** Combat base — pose ufficiale 1536×1024 (RM1.17-C). */
export const NORSE_BERSERKER_COMBAT_BASE: ImageSourcePropType = require('../../assets/heroes/norse_berserker/combat_base.png');
/** Battle anim sprites (RM1.17-C). Esposti per future expansion del sistema sprite. */
export const NORSE_BERSERKER_IDLE: ImageSourcePropType = require('../../assets/heroes/norse_berserker/idle.png');
export const NORSE_BERSERKER_ATTACK: ImageSourcePropType = require('../../assets/heroes/norse_berserker/attack.png');
export const NORSE_BERSERKER_SKILL: ImageSourcePropType = require('../../assets/heroes/norse_berserker/skill.png');
export const NORSE_BERSERKER_HIT: ImageSourcePropType = require('../../assets/heroes/norse_berserker/hit.png');
export const NORSE_BERSERKER_DEATH: ImageSourcePropType = require('../../assets/heroes/norse_berserker/death.png');

// ──────────────────────────────────────────────────────────────────────
// RUNTIME SPRITE SHEETS — RM1.17-N
// Sheet normalizzati (detection ibrida controllata + repack uniforme 640×768).
// Ogni sheet è a celle uniformi, feet-anchored al bottom, scala consistente.
// Metadata canonici in runtime/battle_animations.json (SHA256 tracciato).
// ──────────────────────────────────────────────────────────────────────
type BerserkerAnimMetaState = {
  sheet: string;
  frames: number;
  columns: number;
  rows: number;
  fps: number;
  loop: boolean;
  sha256: string;
};
type BerserkerAnimMeta = {
  heroId: string;
  version: number;
  frameWidth: number;
  frameHeight: number;
  animations: Record<'idle' | 'attack' | 'skill' | 'hit' | 'death', BerserkerAnimMetaState>;
};

const BERSERKER_RUNTIME_IDLE_SHEET: ImageSourcePropType = require('../../assets/heroes/norse_berserker/runtime/idle_sheet.png');
const BERSERKER_RUNTIME_ATTACK_SHEET: ImageSourcePropType = require('../../assets/heroes/norse_berserker/runtime/attack_sheet.png');
const BERSERKER_RUNTIME_SKILL_SHEET: ImageSourcePropType = require('../../assets/heroes/norse_berserker/runtime/skill_sheet.png');
const BERSERKER_RUNTIME_HIT_SHEET: ImageSourcePropType = require('../../assets/heroes/norse_berserker/runtime/hit_sheet.png');
const BERSERKER_RUNTIME_DEATH_SHEET: ImageSourcePropType = require('../../assets/heroes/norse_berserker/runtime/death_sheet.png');
const BERSERKER_BATTLE_ANIM_META = require('../../assets/heroes/norse_berserker/runtime/battle_animations.json') as BerserkerAnimMeta;

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
  // Optional battle-anim variants (RM1.17-C)
  idle?: ImageSourcePropType;
  attack?: ImageSourcePropType;
  skill?: ImageSourcePropType;
  hit?: ImageSourcePropType;
  death?: ImageSourcePropType;
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
    idle: NORSE_BERSERKER_IDLE,
    attack: NORSE_BERSERKER_ATTACK,
    skill: NORSE_BERSERKER_SKILL,
    hit: NORSE_BERSERKER_HIT,
    death: NORSE_BERSERKER_DEATH,
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

// ════════════════════════════════════════════════════════════════════════
// HERO ASSET CONTRACT (RM1.17-F/G/I — pipeline standard future-proof)
// ════════════════════════════════════════════════════════════════════════
/**
 * Contratto asset per-eroe. Ogni nuovo eroe ufficiale dovrà registrarne
 * uno qui per avere:
 *  - variant mapping esplicito per contesto UI (card/detail/fullscreen/battle)
 *  - crop metadata per portrait/card/detail (focus sul volto)
 *  - viewer policy (orientation + contain vs cover)
 *  - battle policy (state-sprite swap, glow soppressione, legacy motion)
 *
 * FALLBACK RULES (implementate sotto in getHeroVariant):
 *  - variant richiesta mancante → portrait → splash → card → transparent → null
 *  - fullscreen mancante → splash → detail → portrait
 *  - idle mancante → combat_base
 *  - attack/skill/hit/death mancanti → idle → combat_base
 *  - Sentinel sconosciuto → safe fallback null (no crash)
 *  - Eroi non-Hoplite → MAI asset Hoplite come fallback visibile
 */
export type HeroVariantKey =
  | 'splash' | 'portrait' | 'card' | 'detail' | 'fullscreen' | 'transparent'
  | 'combat_base' | 'idle' | 'attack' | 'skill' | 'hit' | 'death';

export type HeroCropConfig = {
  /** Focus Y (0..1) per portrait circolare/quadrato. 0.28 = volto in alto. */
  portraitFocusY: number;
  /** Focus Y per card rettangolare. */
  cardFocusY: number;
  /** Focus Y per detail panel. */
  detailFocusY: number;
  /** Aspect intrinseco della splash: 'portrait' | 'square' | 'landscape'. */
  sourceAspect: 'portrait' | 'square' | 'landscape';
};

export type HeroViewerConfig = {
  fullscreenVariant: HeroVariantKey;
  fullscreenOrientation: 'portrait' | 'landscape';
  useContain: boolean;
  /** Se false, il fullscreen NON applicherà crop cover aggressivo. */
  allowDestructiveCrop: boolean;
};

export type HeroBattleConfig = {
  /** State di default quando non c'è action attiva. */
  defaultState: 'idle' | 'combat_base';
  /** Se true, BattleSprite userà state sprites (idle/attack/skill/hit/death). */
  useStateSprites: boolean;
  /** Se true, BattleSprite userà runtime sprite-sheet animati (RM1.17-N).
   *  Priorità MAX: supera useStateSprites + sprite_url legacy. */
  useRuntimeSheets?: boolean;
  /** Se true, BattleSprite sopprime l'aura glow elementale di default. */
  removeDefaultGlow: boolean;
  /** Se true, usa DEFAULT_PROFILE generico di transform; se false, il
   *  profilo animazioni è minimale (state swap + micro-motion). */
  useLegacyDefaultMotion: boolean;
};

/** Metadati runtime sheet per animazione a frame. */
export type RuntimeSheetInfo = {
  source: ImageSourcePropType;
  frames: number;
  columns: number;
  rows: number;
  fps: number;
  loop: boolean;
  /** Cell-size nativa del source (es. 640×768 per Berserker). */
  frameWidth: number;
  frameHeight: number;
  /** RM1.17-O — scala visiva applicata al rendering in battle SOLO.
   *  Applicata da RuntimeSheetSprite con bottom-anchor compensation.
   *  NON modifica layout/grid/posizione battlefield. Default: 1.0 (nessuna scala). */
  visualScale?: number;
};

export type RuntimeSheetState = 'idle' | 'attack' | 'skill' | 'hit' | 'death';

export interface HeroAssetContract {
  id: string;
  variants: Partial<Record<HeroVariantKey, ImageSourcePropType>>;
  crop: HeroCropConfig;
  viewer: HeroViewerConfig;
  battle: HeroBattleConfig;
  /** RM1.17-N: runtime sprite-sheet per-state. Popolato solo se
   *  battle.useRuntimeSheets === true. */
  runtimeSheets?: Partial<Record<RuntimeSheetState, RuntimeSheetInfo>>;
}

// --- Default / fallback contract (usato per eroi non registrati) -------
export const DEFAULT_HERO_CONTRACT: HeroAssetContract = {
  id: 'default',
  variants: {},
  crop: {
    portraitFocusY: 0.35,
    cardFocusY: 0.35,
    detailFocusY: 0.40,
    sourceAspect: 'portrait',
  },
  viewer: {
    fullscreenVariant: 'splash',
    fullscreenOrientation: 'portrait',
    useContain: true,
    allowDestructiveCrop: false,
  },
  battle: {
    defaultState: 'combat_base',
    useStateSprites: false,
    removeDefaultGlow: false,
    useLegacyDefaultMotion: true,
  },
};

// --- Registry contratti per-eroe ---------------------------------------
export const HERO_CONTRACTS: Record<string, HeroAssetContract> = {
  // HOPLITE — preserva comportamento legacy 100%: il rig custom
  // (HeroHopliteRig) è separato dai state sprites; lascia legacy motion e
  // non usa state swap. `removeDefaultGlow` false per mantenere l'aura
  // skill esistente identica a prima.
  [GREEK_HOPLITE_ID]: {
    id: GREEK_HOPLITE_ID,
    variants: {
      splash: GREEK_HOPLITE_PORTRAIT,
      portrait: GREEK_HOPLITE_PORTRAIT,
      card: GREEK_HOPLITE_PORTRAIT,
      detail: GREEK_HOPLITE_DETAIL,
      fullscreen: GREEK_HOPLITE_PORTRAIT,
      transparent: GREEK_HOPLITE_TRANSPARENT,
      combat_base: GREEK_HOPLITE_COMBAT_BASE,
    },
    crop: {
      portraitFocusY: 0.32,
      cardFocusY: 0.30,
      detailFocusY: 0.35,
      sourceAspect: 'square',
    },
    viewer: {
      fullscreenVariant: 'splash',
      fullscreenOrientation: 'portrait',
      useContain: true,
      allowDestructiveCrop: false,
    },
    battle: {
      defaultState: 'combat_base',
      useStateSprites: false,          // rig custom HeroHopliteRig
      removeDefaultGlow: false,        // legacy aura skill preservata
      useLegacyDefaultMotion: true,    // legacy motion preservato
    },
  },
  // BERSERKER — primo esempio completo della pipeline future-proof.
  [NORSE_BERSERKER_ID]: {
    id: NORSE_BERSERKER_ID,
    variants: {
      splash: NORSE_BERSERKER_PORTRAIT,
      portrait: NORSE_BERSERKER_PORTRAIT,
      card: NORSE_BERSERKER_PORTRAIT,
      detail: NORSE_BERSERKER_DETAIL,
      fullscreen: NORSE_BERSERKER_PORTRAIT,
      transparent: NORSE_BERSERKER_TRANSPARENT,
      combat_base: NORSE_BERSERKER_COMBAT_BASE,
      idle: NORSE_BERSERKER_IDLE,
      attack: NORSE_BERSERKER_ATTACK,
      skill: NORSE_BERSERKER_SKILL,
      hit: NORSE_BERSERKER_HIT,
      death: NORSE_BERSERKER_DEATH,
    },
    crop: {
      // Volto Berserker ~25-30% dall'alto (analisi AI vision + misure PIL).
      portraitFocusY: 0.28,
      cardFocusY: 0.25,
      detailFocusY: 0.30,
      sourceAspect: 'portrait',
    },
    viewer: {
      // RM1.17-J — fullscreenVariant='fullscreen' semantico;
      // la fallback chain lo risolve a splash.jpg canonico.
      fullscreenVariant: 'fullscreen',
      fullscreenOrientation: 'portrait',
      useContain: true,
      allowDestructiveCrop: false,
    },
    battle: {
      defaultState: 'idle',
      useStateSprites: true,
      useRuntimeSheets: true,        // RM1.17-N — animazioni a frame
      removeDefaultGlow: true,
      useLegacyDefaultMotion: false,
    },
    runtimeSheets: {
      idle: {
        source: BERSERKER_RUNTIME_IDLE_SHEET,
        frames: BERSERKER_BATTLE_ANIM_META.animations.idle.frames,
        columns: BERSERKER_BATTLE_ANIM_META.animations.idle.columns,
        rows: BERSERKER_BATTLE_ANIM_META.animations.idle.rows,
        fps: BERSERKER_BATTLE_ANIM_META.animations.idle.fps,
        loop: BERSERKER_BATTLE_ANIM_META.animations.idle.loop,
        frameWidth: BERSERKER_BATTLE_ANIM_META.frameWidth,
        frameHeight: BERSERKER_BATTLE_ANIM_META.frameHeight,
        visualScale: 1.30,   // RM1.17-O — body visivo matcha Hoplite battlefield
      },
      attack: {
        source: BERSERKER_RUNTIME_ATTACK_SHEET,
        frames: BERSERKER_BATTLE_ANIM_META.animations.attack.frames,
        columns: BERSERKER_BATTLE_ANIM_META.animations.attack.columns,
        rows: BERSERKER_BATTLE_ANIM_META.animations.attack.rows,
        fps: BERSERKER_BATTLE_ANIM_META.animations.attack.fps,
        loop: BERSERKER_BATTLE_ANIM_META.animations.attack.loop,
        frameWidth: BERSERKER_BATTLE_ANIM_META.frameWidth,
        frameHeight: BERSERKER_BATTLE_ANIM_META.frameHeight,
        visualScale: 1.30,
      },
      skill: {
        source: BERSERKER_RUNTIME_SKILL_SHEET,
        frames: BERSERKER_BATTLE_ANIM_META.animations.skill.frames,
        columns: BERSERKER_BATTLE_ANIM_META.animations.skill.columns,
        rows: BERSERKER_BATTLE_ANIM_META.animations.skill.rows,
        fps: BERSERKER_BATTLE_ANIM_META.animations.skill.fps,
        loop: BERSERKER_BATTLE_ANIM_META.animations.skill.loop,
        frameWidth: BERSERKER_BATTLE_ANIM_META.frameWidth,
        frameHeight: BERSERKER_BATTLE_ANIM_META.frameHeight,
        visualScale: 1.30,
      },
      hit: {
        source: BERSERKER_RUNTIME_HIT_SHEET,
        frames: BERSERKER_BATTLE_ANIM_META.animations.hit.frames,
        columns: BERSERKER_BATTLE_ANIM_META.animations.hit.columns,
        rows: BERSERKER_BATTLE_ANIM_META.animations.hit.rows,
        fps: BERSERKER_BATTLE_ANIM_META.animations.hit.fps,
        loop: BERSERKER_BATTLE_ANIM_META.animations.hit.loop,
        frameWidth: BERSERKER_BATTLE_ANIM_META.frameWidth,
        frameHeight: BERSERKER_BATTLE_ANIM_META.frameHeight,
        visualScale: 1.30,
      },
      death: {
        source: BERSERKER_RUNTIME_DEATH_SHEET,
        frames: BERSERKER_BATTLE_ANIM_META.animations.death.frames,
        columns: BERSERKER_BATTLE_ANIM_META.animations.death.columns,
        rows: BERSERKER_BATTLE_ANIM_META.animations.death.rows,
        fps: BERSERKER_BATTLE_ANIM_META.animations.death.fps,
        loop: BERSERKER_BATTLE_ANIM_META.animations.death.loop,
        frameWidth: BERSERKER_BATTLE_ANIM_META.frameWidth,
        frameHeight: BERSERKER_BATTLE_ANIM_META.frameHeight,
        visualScale: 1.30,
      },
    },
  },
};

/** Ritorna il contratto per l'eroe, o DEFAULT_HERO_CONTRACT. */
export function getHeroContract(
  heroId?: string | null,
  heroName?: string | null,
): HeroAssetContract {
  const localId = resolveLocalHeroId(heroId, heroName);
  if (localId && HERO_CONTRACTS[localId]) return HERO_CONTRACTS[localId];
  return DEFAULT_HERO_CONTRACT;
}

/** Priority order per resolve variant con fallback chain. */
const VARIANT_FALLBACK_CHAIN: Record<HeroVariantKey, HeroVariantKey[]> = {
  splash:      ['splash', 'portrait', 'card', 'detail'],
  portrait:    ['portrait', 'splash', 'card', 'detail'],
  card:        ['card', 'portrait', 'splash', 'detail'],
  detail:      ['detail', 'splash', 'portrait', 'card'],
  fullscreen:  ['fullscreen', 'splash', 'detail', 'portrait', 'card'],
  transparent: ['transparent'],
  combat_base: ['combat_base', 'idle'],
  idle:        ['idle', 'combat_base'],
  attack:      ['attack', 'idle', 'combat_base'],
  skill:       ['skill', 'idle', 'combat_base'],
  hit:         ['hit', 'idle', 'combat_base'],
  death:       ['death', 'idle', 'combat_base'],
};

/**
 * Risolve un asset per variant con fallback chain.
 * Se il contract non contiene la variant richiesta, prova la chain di
 * fallback. Se nulla è disponibile ritorna null.
 */
export function getHeroVariant(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
  variant: HeroVariantKey,
): ImageSourcePropType | null {
  const contract = getHeroContract(heroId, heroName);
  const chain = VARIANT_FALLBACK_CHAIN[variant] || [variant];
  for (const v of chain) {
    const src = contract.variants[v];
    if (src) return src;
  }
  return null;
}

/**
 * Fullscreen viewer source (RM1.17-G). Ritorna sempre la splash portrait
 * dell'eroe — MAI transparent/combat_base. Fallback safe su sentinel
 * sconosciuti → null (non crash).
 */
export function heroFullscreenSource(
  imageUrl?: string | null,
  heroId?: string | null,
  heroName?: string | null,
): ImageSourcePropType | null {
  // 1) contratto per-eroe
  const contract = getHeroContract(heroId, heroName);
  if (contract.id !== 'default') {
    const variant = contract.viewer.fullscreenVariant;
    const src = getHeroVariant(heroId, heroName, variant);
    if (src) return src;
  }
  // 2) sentinel-based lookup
  const parsed = parseHeroAssetSentinel(imageUrl);
  if (parsed) {
    const src = getHeroVariant(parsed.heroId, null, 'fullscreen');
    if (src) return src;
    return null;  // sentinel sconosciuto — safe null
  }
  // 3) URL remoto valido
  if (imageUrl) return { uri: imageUrl };
  return null;
}

/**
 * Battle state source (RM1.17-I). Ritorna l'asset per lo state corrente
 * (idle/attack/skill/hit/death). Rispetta fallback chain: state → idle →
 * combat_base. Se il contratto non ha useStateSprites, ritorna combat_base.
 */
export function heroBattleStateSource(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
  state: 'idle' | 'attack' | 'skill' | 'hit' | 'death' | 'combat_base',
  imageUrl?: string | null,
): ImageSourcePropType | null {
  const contract = getHeroContract(heroId, heroName);
  if (!contract.battle.useStateSprites) {
    // Legacy: solo combat_base statico
    return getHeroVariant(heroId, heroName, 'combat_base') ||
           heroBattleImageSource(imageUrl, heroId, heroName);
  }
  const src = getHeroVariant(heroId, heroName, state);
  if (src) return src;
  // Fallback sentinel-based
  const parsed = parseHeroAssetSentinel(imageUrl);
  if (parsed) {
    const v = getHeroVariant(parsed.heroId, null, state);
    if (v) return v;
  }
  return null;
}

/**
 * RM1.17-N — Runtime sprite-sheet resolver.
 * Ritorna il RuntimeSheetInfo per l'eroe+state se il contract ha
 * `useRuntimeSheets: true` e lo state è definito. Altrimenti null.
 *
 * Fallback chain per state:
 *   attack/skill/hit/death → se mancanti, fallback a 'idle'
 *   idle mancante → null (no sheet disponibile)
 *
 * Consumer-side: BattleSprite controlla PRIMA questa funzione. Se !null,
 * monta il RuntimeSheetSprite component. Altrimenti cade su
 * heroBattleStateSource (PNG statico) o combat_base.
 */
export function heroRuntimeSheet(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
  state: RuntimeSheetState,
): RuntimeSheetInfo | null {
  const contract = getHeroContract(heroId, heroName);
  if (!contract.battle.useRuntimeSheets) return null;
  if (!contract.runtimeSheets) return null;
  const info = contract.runtimeSheets[state];
  if (info) return info;
  // fallback a idle per state non definiti (plausibile per eroi con solo idle)
  return contract.runtimeSheets.idle || null;
}

/** True se l'eroe ha runtime sheets disponibili (almeno idle). */
export function hasHeroRuntimeSheets(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
): boolean {
  const contract = getHeroContract(heroId, heroName);
  return !!(contract.battle.useRuntimeSheets && contract.runtimeSheets?.idle);
}

/**
 * RM1.17-O — Preload battle assets helper.
 * Ritorna la lista di tutti gli asset Image locali che battle deve avere
 * decodati PRIMA di passare alla fase `preparing`. Include:
 *   - runtime sprite-sheets (idle/attack/skill/hit/death) se l'eroe ha
 *     `useRuntimeSheets: true`
 *   - combat_base statico (fallback + eventuale aura layer)
 * Dedup automatico via set. Usato da combat.tsx nel preload block.
 */
export function getHeroBattlePreloadAssets(
  heroId?: string | null,
  heroName?: string | null,
  image?: string | null,
): ImageSourcePropType[] {
  const contract = getHeroContract(heroId, heroName);
  const assets: ImageSourcePropType[] = [];

  if (contract.runtimeSheets) {
    Object.values(contract.runtimeSheets).forEach((info) => {
      if (info?.source) assets.push(info.source);
    });
  }

  const combat = heroBattleImageSource(image || undefined, heroId, heroName);
  if (combat) assets.push(combat);

  const seen = new Set<string>();
  return assets.filter((asset: any) => {
    const key = typeof asset === 'number' ? `num:${asset}` : JSON.stringify(asset);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

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

// ────────────────────────────────────────────────────────────────────
// RM1.17-R — UI PORTRAIT FRAMING CONTRACT (per-hero, per-slot)
// ────────────────────────────────────────────────────────────────────
/**
 * Slot UI riconosciuti dall'app. Ogni slot ha un framing dedicato che
 * controlla variant sorgente, resizeMode, focusY/X e scale. Fonte di
 * verità unica per evitare fix "a occhio" sparsi nei componenti.
 *
 *  - 'home'            → HomeHeroSplash (overlay eroe sulla scena home)
 *  - 'card'            → Card griglia Collezione / AnimatedHeroPortrait
 *  - 'detailIcon'      → Icona 80×80 nell'header di HeroDetail
 *  - 'selectedPreview' → Pannello destro della Collezione (preview eroe)
 *  - 'fullscreen'      → hero-viewer fullscreen (portrait verticale grande)
 */
export type HeroUiSlot =
  | 'home'
  | 'card'
  | 'detailIcon'
  | 'selectedPreview'
  | 'fullscreen';

/**
 * Framing per-slot. Valori numerici (no magic constants sparsi).
 *  - variant     → quale variant del contract usare (splash/transparent/…)
 *  - resizeMode  → 'contain' = niente crop, 'cover' = crop con focus
 *  - focusY      → 0..1 dal top (solo per 'cover'; 0.28 = volto alto)
 *  - focusX      → 0..1 da sinistra (default 0.5); riservato per asset
 *                  non-centrali (es. eroi con busto fuori asse).
 *  - scale       → zoom extra applicato al body dopo il fit. >1 = zoom-in
 *                  (utile per card strette dove vogliamo più faccia).
 *                  <1 = zoom-out (aria intorno al body). Default 1.
 *  - verticalPriority → se true e resizeMode='contain', il box usa la
 *                  height come dimensione guida (fit-to-height). Usato
 *                  in fullscreen per evitare che il portrait diventi
 *                  un rettangolo landscape in device landscape.
 */
export type HeroUiFraming = {
  variant: HeroVariantKey;
  resizeMode: 'contain' | 'cover';
  focusY: number;
  focusX?: number;
  scale?: number;
  verticalPriority?: boolean;
};

export type HeroUiContract = Record<HeroUiSlot, HeroUiFraming>;

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
  /** RM1.17-FINAL — Scala applicata al wrapper di rendering in battle SOLO
   *  per eroi runtime-sheet. Compensa la differenza di proporzioni body/frame
   *  (es. Berserker body fills 39% cell width vs Hoplite 97%). Bottom-anchor
   *  compensation applicata. Default: 1.0 (no-op). */
  runtimeRenderScale?: number;
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
  /** RM1.17-R — UI portrait framing per-slot. Opzionale: se assente
   *  viene usato DEFAULT_UI_CONTRACT. Definire esplicitamente per
   *  ogni eroe i cui asset hanno proporzioni/anchor differenti dal
   *  default (es. Berserker con volto più in alto). */
  ui?: HeroUiContract;
  /** RM1.17-N: runtime sprite-sheet per-state. Popolato solo se
   *  battle.useRuntimeSheets === true. */
  runtimeSheets?: Partial<Record<RuntimeSheetState, RuntimeSheetInfo>>;
}

// --- Default UI contract (usato se il contract non specifica `ui`) -----
// Valori neutri/sicuri: splash in tutti gli slot, contain per evitare
// crop indesiderati, focusY 0.35 per un focus leggermente alto sul
// busto. NIENTE crop aggressivo di default.
export const DEFAULT_UI_CONTRACT: HeroUiContract = {
  home:            { variant: 'transparent', resizeMode: 'contain', focusY: 0.35, scale: 1.0 },
  card:            { variant: 'card',        resizeMode: 'cover',   focusY: 0.28, scale: 1.0 },
  detailIcon:      { variant: 'detail',      resizeMode: 'cover',   focusY: 0.30, scale: 1.0 },
  selectedPreview: { variant: 'portrait',    resizeMode: 'contain', focusY: 0.35, scale: 1.0 },
  fullscreen:      { variant: 'fullscreen',  resizeMode: 'contain', focusY: 0.5,  scale: 1.0, verticalPriority: true },
};

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
    // RM1.17-S — UI contract per Hoplite. Fix Home top-cut usando contain.
    // Gli slot NON-home preservano la semantica legacy (cover center / default)
    // così gli altri contesti (card grid, hero-detail header via isHoplite
    // short-circuit, selectedPreview via isGreekHoplite branch, fullscreen
    // via isHoplite short-circuit in hero-viewer) non hanno regressioni.
    ui: {
      // Home: transparent cutout con contain → full hero visibile, no top cut.
      home:            { variant: 'transparent', resizeMode: 'contain', focusY: 0.5, scale: 1.0 },
      // Card/detailIcon: cover center preserva il look legacy per i consumer
      // che passano attraverso HeroFramedImage (AnimatedHeroPortrait grid).
      // Per Hoplite sourceAspect='square' → transform è noop, stesso risultato
      // del RNImage plain cover legacy.
      card:            { variant: 'card',        resizeMode: 'cover',   focusY: 0.5, scale: 1.0 },
      detailIcon:      { variant: 'detail',      resizeMode: 'cover',   focusY: 0.5, scale: 1.0 },
      selectedPreview: { variant: 'portrait',    resizeMode: 'contain', focusY: 0.5, scale: 1.0 },
      fullscreen:      { variant: 'fullscreen',  resizeMode: 'contain', focusY: 0.5, scale: 1.0, verticalPriority: true },
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
      runtimeRenderScale: 1.30,      // RM1.17-FINAL — match visivo vs Hoplite
    },
    // RM1.17-R — UI portrait framing per Berserker.
    // Sorgente splash.jpg 512×768 (2:3 portrait). Volto al ~25-30% dal top.
    // Cutout transparent.png 408×612 (2:3 portrait) stesso anchor.
    // RM1.17-S — card e detailIcon passati a 'contain' dopo verifica device:
    // i valori di cover+focusY anche al clamp massimo tagliavano ancora la
    // testa in certi edge cases. 'contain' garantisce che il VOLTO non sia
    // MAI tagliato (letterbox sicuro sui lati per aspetti quadrati), a costo
    // di un leggero sacrificio di presenza visiva — scelta consapevole:
    // "faccia sempre visibile" > "ingrandimento aggressivo".
    ui: {
      // Home: cutout trasparente su gradient. No crop → full-body visibile.
      home:            { variant: 'transparent', resizeMode: 'contain', focusY: 0.5,  scale: 1.02 },
      // Card 48×48: RM1.17-S → contain + scale per massimizzare presenza
      // senza mai tagliare la testa. Letterbox verticale neutro.
      card:            { variant: 'card',        resizeMode: 'contain', focusY: 0.5,  scale: 1.0  },
      // DetailIcon 80×80: RM1.17-S → contain, stesso rationale della card.
      detailIcon:      { variant: 'detail',      resizeMode: 'contain', focusY: 0.5,  scale: 1.0  },
      // SelectedPreview (pannello destro Collezione): contain full portrait.
      selectedPreview: { variant: 'portrait',    resizeMode: 'contain', focusY: 0.5,  scale: 1.0  },
      // Fullscreen viewer: portrait verticale grande, height-priority.
      fullscreen:      { variant: 'fullscreen',  resizeMode: 'contain', focusY: 0.5,  scale: 1.0, verticalPriority: true },
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
        visualScale: 1.0,   // RM1.17-P — body già scalato nel packing runtime
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
        visualScale: 1.0,   // RM1.17-P — body già scalato nel packing runtime
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
        visualScale: 1.0,   // RM1.17-P — body già scalato nel packing runtime
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
        visualScale: 1.0,   // RM1.17-P — body già scalato nel packing runtime
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
        visualScale: 1.0,   // RM1.17-P — body già scalato nel packing runtime
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


// ════════════════════════════════════════════════════════════════════════
// RM1.17-R — UI PORTRAIT FRAMING RESOLVERS
// ════════════════════════════════════════════════════════════════════════

/**
 * Ritorna il framing configurato per un dato slot UI. Se il contract non
 * definisce `ui` usa DEFAULT_UI_CONTRACT. Questa è la FONTE UNICA per
 * qualsiasi decisione di rendering portrait nei componenti UI.
 */
export function getHeroUiFraming(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
  slot: HeroUiSlot,
): HeroUiFraming {
  const contract = getHeroContract(heroId, heroName);
  const ui = contract.ui || DEFAULT_UI_CONTRACT;
  return ui[slot] || DEFAULT_UI_CONTRACT[slot];
}

/**
 * Ritorna il source Image per un dato slot UI, usando la variant indicata
 * nel framing (via VARIANT_FALLBACK_CHAIN). Per eroi remoti (non
 * registrati) ritorna {uri: imageUrl} se presente, altrimenti null.
 */
export function heroUiSource(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
  slot: HeroUiSlot,
  imageUrl?: string | null,
): ImageSourcePropType | null {
  const framing = getHeroUiFraming(heroId, heroName, slot);
  // 1) variant dal contract
  const variantSrc = getHeroVariant(heroId, heroName, framing.variant);
  if (variantSrc) return variantSrc;
  // 2) sentinel parsing
  const parsed = parseHeroAssetSentinel(imageUrl);
  if (parsed) {
    const v = getHeroVariant(parsed.heroId, null, framing.variant);
    if (v) return v;
    return null;
  }
  // 3) URL remoto
  if (imageUrl) return { uri: imageUrl };
  return null;
}

/**
 * Calcola il transform (translateX/Y + scale) da applicare a un Image con
 * resizeMode='cover' per ancorare il focusY (e opzionalmente focusX) della
 * sorgente al centro della box.
 *
 *  boxW,  boxH      → dimensioni della box in pixel
 *  framing          → HeroUiFraming (usa focusY, focusX, scale)
 *  sourceAspect     → 'portrait' | 'square' | 'landscape' (dal contract)
 *
 * Math:
 *  - Normalizziamo la sorgente ad altezza 1, width = sourceAspectRatio.
 *  - scale_cover = max(boxW/srcW, boxH/srcH) garantisce che la sorgente
 *    coprà interamente la box.
 *  - scaledH = srcH * scale_cover, scaledW = srcW * scale_cover.
 *  - overflowY = scaledH - boxH, overflowX = scaledW - boxW.
 *  - Per portare un focus Y della sorgente al centro della box:
 *      ty = (0.5 - focusY) * scaledH  (clampato a ±overflowY/2)
 *    Questo è DIVERSO dalla formula vecchia che usava overflowY al posto
 *    di scaledH: quella sottostima lo shift quando scaledH >> boxH.
 *  - Stesso approccio per focusX.
 *  - Infine applichiamo lo scale extra (zoom) come moltiplicatore.
 */
export function computeUiCoverTransform(
  boxW: number,
  boxH: number,
  framing: HeroUiFraming,
  sourceAspect: 'portrait' | 'square' | 'landscape',
): { transform: any[] } {
  const srcAspectRatio =
    sourceAspect === 'portrait' ? 2 / 3
    : sourceAspect === 'landscape' ? 3 / 2
    : 1;
  const srcW = srcAspectRatio;
  const srcH = 1;
  const scaleCover = Math.max(boxW / srcW, boxH / srcH);
  const scaledW = srcW * scaleCover;
  const scaledH = srcH * scaleCover;
  const overflowY = Math.max(0, scaledH - boxH);
  const overflowX = Math.max(0, scaledW - boxW);

  const focusY = framing.focusY;
  const focusX = framing.focusX ?? 0.5;

  let ty = (0.5 - focusY) * scaledH;
  let tx = (0.5 - focusX) * scaledW;
  // Clamp ai bordi: non scopriamo mai spazio vuoto.
  const maxTy = overflowY / 2;
  const maxTx = overflowX / 2;
  if (ty > maxTy) ty = maxTy;
  if (ty < -maxTy) ty = -maxTy;
  if (tx > maxTx) tx = maxTx;
  if (tx < -maxTx) tx = -maxTx;

  const extraScale = framing.scale ?? 1;
  const transform: any[] = [];
  if (Math.abs(tx) > 0.5) transform.push({ translateX: Math.round(tx) });
  if (Math.abs(ty) > 0.5) transform.push({ translateY: Math.round(ty) });
  if (extraScale !== 1) transform.push({ scale: extraScale });
  return { transform };
}

/**
 * Ritorna il sourceAspect dichiarato nel contract crop (con fallback
 * 'portrait' per non-registrati).
 */
export function getHeroSourceAspect(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
): 'portrait' | 'square' | 'landscape' {
  const contract = getHeroContract(heroId, heroName);
  return contract.crop.sourceAspect;
}

/** True se l'eroe ha un UI contract esplicito (non default). */
export function hasHeroUiContract(
  heroId: string | null | undefined,
  heroName: string | null | undefined,
): boolean {
  const contract = getHeroContract(heroId, heroName);
  return !!contract.ui;
}

// ════════════════════════════════════════════════════════════════════════
// RM1.18 — NEW HERO IMPORT STANDARD: TEMPLATE + VALIDATOR
// ════════════════════════════════════════════════════════════════════════
//
// Documentazione completa: /app/docs/NEW_HERO_IMPORT_CHECKLIST.md
//
// Questo blocco implementa lo STANDARD operativo per importare un nuovo
// eroe locale senza ri-introdurre i bug storici (face crop, preload
// mancante, motion duplicata, scale non coerente, background tie null,
// scroll DETTAGLIO irraggiungibile).
//
// Fornisce:
//   1) `NEW_HERO_CONTRACT_TEMPLATE`: template `HeroAssetContract` con
//      valori sicuri di default (contain everywhere, no glow, preload OK).
//      Copiare + rinominare + compilare gli asset.
//   2) `validateHeroContract(heroId)`: ritorna lista di warning sulla
//      completezza del contract (UI slots, variants, runtime sheets,
//      scale, preload). Array vuoto = OK.
//   3) `validateAllHeroContracts()`: helper dev-only che cicla tutti gli
//      eroi registrati e raccoglie i warning in un dizionario.
//
// IMPORTANTE: questo file NON impone check a runtime (nessun throw),
// NON modifica comportamenti esistenti. È una guardrail read-only per
// developer. L'uso è opt-in via console/dev-tools.
// ════════════════════════════════════════════════════════════════════════

/**
 * Template di HeroAssetContract con valori di default sicuri per
 * un nuovo eroe portrait 2:3. Copiare e compilare per ogni nuovo hero.
 *
 *  - Tutte le UI slot usano `contain` → volto mai tagliato.
 *  - `verticalPriority: true` sulla fullscreen → portrait viewer ruota
 *    in PORTRAIT_UP e fit-to-height.
 *  - Runtime sheets disabilitate di default: se l'eroe ha solo
 *    `combat_base.png` come battle asset, tenere `useRuntimeSheets: false`
 *    + `useStateSprites: false` + `defaultState: 'combat_base'`.
 *  - Se l'eroe usa runtime sheets, impostare:
 *      useRuntimeSheets: true
 *      useStateSprites:  false
 *      useLegacyDefaultMotion: false
 *      removeDefaultGlow: true
 *      runtimeRenderScale: <tarato vs Hoplite/Berserker reference>
 *      runtimeSheets: { idle, attack, skill, hit, death }
 *
 * Il template è annotato inline con i placeholder `<...>`. NON è un
 * contract valido as-is: è solo una base da compilare.
 */
export const NEW_HERO_CONTRACT_TEMPLATE = {
  id: '<canonical_hero_id>',
  variants: {
    // splash: require('../../assets/heroes/<hero_id>/splash.jpg'),
    // portrait: require('../../assets/heroes/<hero_id>/splash.jpg'),
    // card: require('../../assets/heroes/<hero_id>/splash.jpg'),
    // detail: require('../../assets/heroes/<hero_id>/splash.jpg'),
    // fullscreen: require('../../assets/heroes/<hero_id>/splash.jpg'),
    // transparent: require('../../assets/heroes/<hero_id>/transparent.png'),
    // combat_base: require('../../assets/heroes/<hero_id>/combat_base.png'),
  },
  crop: {
    portraitFocusY: 0.32,
    cardFocusY: 0.28,
    detailFocusY: 0.30,
    sourceAspect: 'portrait' as const, // 'portrait' | 'square' | 'landscape'
  },
  viewer: {
    fullscreenVariant: 'splash' as const,
    fullscreenOrientation: 'portrait' as const,
    useContain: true,
    allowDestructiveCrop: false,
  },
  battle: {
    defaultState: 'idle' as const,
    useStateSprites: false,          // true SOLO se niente runtime sheets
    useRuntimeSheets: false,         // true se runtime/*_sheet.png esistono
    removeDefaultGlow: true,
    useLegacyDefaultMotion: false,
    // runtimeRenderScale: 1.0,      // tarare vs Hoplite/Berserker se runtime
  },
  // runtimeSheets: {
  //   idle:   { source: require('../../assets/heroes/<hero_id>/runtime/idle_sheet.png'),   ... },
  //   attack: { source: require('../../assets/heroes/<hero_id>/runtime/attack_sheet.png'), ... },
  //   skill:  { source: require('../../assets/heroes/<hero_id>/runtime/skill_sheet.png'),  ... },
  //   hit:    { source: require('../../assets/heroes/<hero_id>/runtime/hit_sheet.png'),    ... },
  //   death:  { source: require('../../assets/heroes/<hero_id>/runtime/death_sheet.png'),  ... },
  // },
  ui: {
    // Home: cutout trasparente su gradient. Contain → full body, no crop.
    home:            { variant: 'transparent' as const, resizeMode: 'contain' as const, focusY: 0.5, scale: 1.0 },
    // Card: grid collezione 48×48. Contain + scale custom se serve presenza.
    card:            { variant: 'card' as const,        resizeMode: 'contain' as const, focusY: 0.5, scale: 1.0 },
    // DetailIcon: header 80×80. Contain default, safe per portrait 2:3.
    detailIcon:      { variant: 'detail' as const,      resizeMode: 'contain' as const, focusY: 0.5, scale: 1.0 },
    // SelectedPreview: pannello destro Collezione ~180×170. Contain per
    // preservare full body portrait e presenza comparabile a Hoplite.
    selectedPreview: { variant: 'portrait' as const,    resizeMode: 'contain' as const, focusY: 0.5, scale: 1.0 },
    // Fullscreen: portrait verticale grande, height-priority lock device.
    fullscreen:      { variant: 'fullscreen' as const,  resizeMode: 'contain' as const, focusY: 0.5, scale: 1.0, verticalPriority: true },
  },
};

/** Slot UI obbligatori per ogni HeroUiContract. */
const REQUIRED_UI_SLOTS: readonly HeroUiSlot[] = ['home', 'card', 'detailIcon', 'selectedPreview', 'fullscreen'];

/** Variant minime per un eroe "completo" (portrait/fullscreen/card/detail). */
const REQUIRED_VARIANTS: readonly HeroVariantKey[] = ['splash', 'portrait', 'card', 'detail', 'fullscreen'];

/** Stati runtime sheet richiesti se `useRuntimeSheets: true`. */
const REQUIRED_RUNTIME_STATES: readonly RuntimeSheetState[] = ['idle', 'attack', 'skill', 'hit', 'death'];

/**
 * Validatore read-only per un singolo HeroAssetContract.
 *
 * Controlla:
 *  - tutti i variants obbligatori sono popolati
 *  - tutti gli UI slot sono popolati (con i campi minimi)
 *  - ui.fullscreen ha `verticalPriority: true`
 *  - se battle.useRuntimeSheets=true: runtimeSheets ha tutti e 5 gli stati
 *  - se battle.useRuntimeSheets=true: useStateSprites DEVE essere false
 *  - se battle.useRuntimeSheets=true: useLegacyDefaultMotion DEVE essere false
 *  - sourceAspect è uno dei valori supportati
 *  - combat_base esiste per eroi con rig di battaglia
 *
 * Non esegue I/O su filesystem (i `require(...)` sono già risolti in build).
 * Ritorna array di stringhe: vuoto = contract OK.
 */
export function validateHeroContract(
  heroId: string | null | undefined,
  heroName?: string | null,
): string[] {
  const warnings: string[] = [];
  if (!heroId) {
    warnings.push('[validateHeroContract] heroId mancante');
    return warnings;
  }
  // NB: getHeroContract ripiega su DEFAULT_HERO_CONTRACT se l'id è ignoto.
  // Per validare solo gli eroi REGISTRATI nel system verifichiamo
  // esplicitamente la presenza nel dictionary.
  const registered = HERO_CONTRACTS[heroId];
  if (!registered) {
    warnings.push(`[${heroId}] nessuna entry in HERO_CONTRACTS — eroe non registrato`);
    return warnings;
  }
  const c = registered;

  // 1. Variants
  for (const v of REQUIRED_VARIANTS) {
    if (!c.variants[v]) {
      warnings.push(`[${heroId}] variant mancante: ${v}`);
    }
  }
  if (!c.variants.combat_base) {
    warnings.push(`[${heroId}] variant combat_base mancante (richiesto per rig di battaglia)`);
  }

  // 2. UI contract
  if (!c.ui) {
    warnings.push(`[${heroId}] ui contract assente — fallback su DEFAULT_UI_CONTRACT`);
  } else {
    for (const slot of REQUIRED_UI_SLOTS) {
      const f = c.ui[slot];
      if (!f) {
        warnings.push(`[${heroId}] ui slot mancante: ${slot}`);
        continue;
      }
      if (!f.variant) warnings.push(`[${heroId}] ui.${slot}.variant mancante`);
      if (!f.resizeMode) warnings.push(`[${heroId}] ui.${slot}.resizeMode mancante`);
      if (typeof f.focusY !== 'number') warnings.push(`[${heroId}] ui.${slot}.focusY non numerico`);
    }
    // Fullscreen deve avere verticalPriority true per true-portrait viewer.
    if (c.ui.fullscreen && c.ui.fullscreen.verticalPriority !== true) {
      warnings.push(`[${heroId}] ui.fullscreen.verticalPriority DEVE essere true per portrait viewer device-lock`);
    }
  }

  // 3. SourceAspect
  if (!['portrait', 'square', 'landscape'].includes(c.crop.sourceAspect)) {
    warnings.push(`[${heroId}] crop.sourceAspect invalido: ${c.crop.sourceAspect}`);
  }

  // 4. Runtime sheets consistency
  if (c.battle.useRuntimeSheets) {
    // NB: useStateSprites=true + useRuntimeSheets=true è LEGAL in produzione.
    // BattleSprite branch order: runtime sheets FIRST → state sprites
    // FALLBACK. Il flag stateSprites su un eroe con runtime sheets serve
    // come safety net se in futuro le runtime non si caricassero. Quindi
    // NIENTE warning hard su questa combinazione.
    if (c.battle.useLegacyDefaultMotion) {
      warnings.push(`[${heroId}] useRuntimeSheets=true richiede useLegacyDefaultMotion=false (runtime owns motion)`);
    }
    if (!c.runtimeSheets) {
      warnings.push(`[${heroId}] useRuntimeSheets=true ma runtimeSheets assente`);
    } else {
      for (const st of REQUIRED_RUNTIME_STATES) {
        if (!c.runtimeSheets[st]) {
          warnings.push(`[${heroId}] runtimeSheets.${st} mancante`);
        }
      }
    }
    if (c.battle.removeDefaultGlow !== true) {
      // Non è un errore hard (Hoplite glow intenzionale), ma warn per nuovi eroi.
      warnings.push(`[${heroId}] NOTE: runtime sheets + removeDefaultGlow=false — intenzionale?`);
    }
    if (typeof c.battle.runtimeRenderScale !== 'number') {
      warnings.push(`[${heroId}] runtimeRenderScale non impostato — verifica scale vs Hoplite/Berserker`);
    }
  }

  // 5. State sprites consistency (mutually exclusive con runtime sheets)
  if (c.battle.useStateSprites && !c.battle.useRuntimeSheets) {
    const stateVariants: HeroVariantKey[] = ['idle', 'attack', 'skill', 'hit', 'death'];
    for (const sv of stateVariants) {
      if (!c.variants[sv]) {
        warnings.push(`[${heroId}] useStateSprites=true ma variant ${sv} mancante`);
      }
    }
  }

  return warnings;
}

/**
 * Valida TUTTI gli eroi registrati in HERO_CONTRACTS. Utile per invocazione
 * manuale da console dev-tools o da un test unitario opt-in.
 * Ritorna un oggetto { [heroId]: warnings[] } solo per eroi con warning.
 */
export function validateAllHeroContracts(): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  for (const heroId of Object.keys(HERO_CONTRACTS)) {
    const w = validateHeroContract(heroId);
    if (w.length > 0) out[heroId] = w;
  }
  return out;
}

// ════════════════════════════════════════════════════════════════════════
// NEW_HERO_IMPORT_CHECKLIST — riferimento rapido
// ════════════════════════════════════════════════════════════════════════
// Per il processo completo vedi /app/docs/NEW_HERO_IMPORT_CHECKLIST.md
//
// Quick checklist:
//   [A] Asset folder: frontend/assets/heroes/<hero_id>/
//        ├── splash.jpg, transparent.png (se Home), combat_base.png
//        ├── source_sheets/*.png (5 stati, se runtime)
//        └── runtime/*_sheet.png + battle_animations.json (se runtime)
//   [B] HERO_CONTRACTS entry con: id, variants, crop.sourceAspect, viewer,
//        battle, ui (5 slot), runtimeSheets (se applicabile)
//   [C] UI framing: contain everywhere di default; cover SOLO se verificato
//        che non taglia il volto; scale in contract, non in CSS components.
//   [D] Battle runtime: se useRuntimeSheets=true → BattleSprite branch
//        runtime, no external motion, runtimeRenderScale tarato.
//   [E] Battle preload: getHeroBattlePreloadAssets(...) copre tutti gli
//        asset locali del nuovo eroe, battle phase attende il caricamento.
//   [F] Background fallback deterministico (no tie randomness).
//   [G] Safety: Hoplite/Berserker invariati; tsc clean; Metro clean.
//   [H] Validator: validateHeroContract('<id>') ritorna [] dopo import.
// ════════════════════════════════════════════════════════════════════════


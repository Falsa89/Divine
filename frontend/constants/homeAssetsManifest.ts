/**
 * HOME ASSETS MANIFEST
 * =====================================================================
 *
 * UNICA fonte di verità per TUTTI gli asset della homepage.
 * Quando arriveranno gli asset definitivi dell'art team, si aggiunge SOLO
 * il `require(...)` nel campo corrispondente — nessun tocco ai componenti.
 *
 * Struttura:
 *   - HOME_BACKGROUNDS  → per scena × fase temporale (dawn/day/sunset/night)
 *   - HOME_PANELS       → frame bg / decor per ciascun pannello UI
 *   - HOME_BUTTONS      → icone + stati (default/pressed/selected/disabled)
 *   - HOME_NAV_ICONS    → icone bottom nav custom (10 slot)
 *   - HOME_BANNERS      → frame per il main banner (summon rate-up)
 *   - HOME_PLAY_SHIELD  → asset del pulsante centrale PLAY
 *
 * Tutti i campi sono opzionali (`?`): se assenti, il componente mostra
 * un fallback tecnico NEUTRO (placeholder non artistico). Nessuno
 * stile creativo improvvisato.
 */
import type { TimePhase } from '../utils/serverTimePhase';

export type HomeScene =
  | 'default'   // hub principale
  | 'celtic'
  | 'nordic'
  | 'greek'
  | 'egypt'
  | 'japanese';

/* ────────────────────────────── BACKGROUNDS ────────────────────────────── */
export type BackgroundVariants = { [K in TimePhase]?: any };
export type BackgroundManifest = { [K in HomeScene]: BackgroundVariants };

/**
 * Un entry per scena; 4 chiavi per fase temporale.
 * Quando un asset non è ancora disponibile, lasciare `undefined`:
 * il sistema cadrà automaticamente sulla variante più vicina.
 */
export const HOME_BACKGROUNDS: BackgroundManifest = {
  default: {
    dawn:   require('../assets/home_bg/home_bg_default_dawn.png'),
    day:    require('../assets/home_bg/home_bg_default_day.png'),
    sunset: require('../assets/home_bg/home_bg_default_sunset.png'),
    night:  require('../assets/home_bg/home_bg_default_night.png'),
  },
  celtic:   { dawn: undefined, day: undefined, sunset: undefined, night: undefined },
  nordic:   { dawn: undefined, day: undefined, sunset: undefined, night: undefined },
  greek:    { dawn: undefined, day: undefined, sunset: undefined, night: undefined },
  egypt:    { dawn: undefined, day: undefined, sunset: undefined, night: undefined },
  japanese: { dawn: undefined, day: undefined, sunset: undefined, night: undefined },
};

/**
 * Risolve il background per (scena, fase) con fallback ordinato:
 *   phase richiesta → night → day → sunset → dawn → default.night
 */
export function resolveHomeBackground(scene: HomeScene, phase: TimePhase): any {
  const s = HOME_BACKGROUNDS[scene] || HOME_BACKGROUNDS.default;
  const order: TimePhase[] = [phase, 'night', 'day', 'sunset', 'dawn'];
  for (const p of order) {
    if (s[p]) return s[p];
  }
  // Ultimo fallback cross-scene
  return HOME_BACKGROUNDS.default.night;
}

/* ────────────────────────────── PANELS ────────────────────────────── */
/**
 * Frame panel: immagine di sfondo (può essere un 9-slice / nineSlice).
 * In futuro potremo aggiungere `decor` (overlay decorativo dorato etc.).
 */
export type PanelAsset = {
  frame?: any;
  decor?: any;
  /** se vero, frame è 9-slice (lo useremo con ImageBackground + capInsets) */
  nineSlice?: boolean;
  /** margini interni del 9-slice in pixel dell'asset sorgente */
  capInsets?: { top: number; left: number; bottom: number; right: number };
};

export type PanelKey =
  | 'profile'      // top-left profile panel
  | 'currency'     // top-right gold/gems
  | 'chatNotif'    // bottom-left chat/notifiche
  | 'mainBanner'   // summon rate-up banner
  | 'overflow'     // modal menu overflow
  | 'spOffer'      // SP offer button
  | 'crystalPack'  // crystal packs
  | 'serverTime';  // server time box

export const HOME_PANELS: Record<PanelKey, PanelAsset> = {
  profile:     {},
  currency:    {},
  chatNotif:   {},
  mainBanner:  {},
  overflow:    {},
  spOffer:     {},
  crystalPack: {},
  serverTime:  {},
};

/* ══════════════════════════════════════════════════════════════════════
 *   SLOT MANIFEST — GRANULARE PER BLOCCO (drop-in ready per Pack A/B/…)
 * ══════════════════════════════════════════════════════════════════════
 *
 * Ogni blocco homepage ha un oggetto-manifest con TUTTI gli slot possibili
 * in formato `slot?: any`. Quando arriva un Pack:
 *   1) si aggiungono i `require(...)` nel manifest corretto
 *   2) nessun refactor del componente richiesto → drop-in immediato
 *
 * Fintanto che i slot sono `undefined`, i componenti cadono sul fallback
 * visivo attuale (gradient/placeholder) SENZA cambi visibili.
 *
 * Per 9-slice usare `capInsets` in px dell'asset sorgente.
 */

/* ───── Pack A — Profile Panel (TOP-LEFT) ───── */
export type ProfilePanelAssets = {
  /** Frame principale del panel (9-slice o full-bleed) */
  frame?: any;
  /** Overlay decorativo (filigrane/cornici oro); opzionale */
  decor?: any;
  nineSlice?: boolean;
  capInsets?: { top: number; left: number; bottom: number; right: number };

  /** Cornice dorata intorno all'avatar (ring+glow) */
  avatarRing?: any;
  /** Sfondo avatar quando non c'è immagine user (portrait generico) */
  avatarPlaceholder?: any;
  /** Badge numero livello (cerchio sotto avatar) */
  lvBadge?: any;

  /** Traccia barra EXP (sfondo) */
  expBarBg?: any;
  /** Fill barra EXP (può essere tileable) */
  expBarFill?: any;

  /** Riga power: frame/cornice full-width */
  powerRow?: any;
  /** Icona lightning power (overrides emoji ⚡) */
  powerIcon?: any;

  /** Pill VIP */
  vipBadge?: any;
  /** Pill Spirito */
  spiritoBadge?: any;
  /** Pill Titolo attivo */
  titleBadge?: any;
};
export const HOME_PROFILE_PANEL: ProfilePanelAssets = {
  // Tutti i slot undefined → fallback visivo identico all'attuale.
  // Quando arriva il Pack A: aggiungere qui frame / avatarRing / lvBadge / …
};

/* ───── Pack B — Currency Bar (TOP-RIGHT) ───── */
export type CurrencyPillAssets = {
  /** Frame pill (9-slice consigliato) */
  frame?: any;
  nineSlice?: boolean;
  capInsets?: { top: number; left: number; bottom: number; right: number };
  /** Icona moneta (gold bag / gem) */
  icon?: any;
  /** Pulsante "+" (singolo asset con stati opzionali) */
  plusBtn?: ButtonAsset;
};
export type CurrencyBarAssets = {
  gold?: CurrencyPillAssets;
  gems?: CurrencyPillAssets;
};
export const HOME_CURRENCY_BAR: CurrencyBarAssets = {
  gold: {},
  gems: {},
};

/* ───── Pack C — Top Actions (Wheel/Quest/Event, TOP-RIGHT sotto valute) ───── */
export type TopActionsAssets = {
  /** Frame comune a tutti i 3 bottoni (opzionale; se mancante si usa HOME_BUTTONS per-button) */
  commonFrame?: ButtonAsset;
  /** Override icone singole (se HOME_BUTTONS[key].default non basta) */
  iconWheel?: any;
  iconQuest?: any;
  iconEvent?: any;
};
export const HOME_TOP_ACTIONS: TopActionsAssets = {};

/* ───── Pack D — Left Utility Stack (server time, SP offer, crystal packs) ───── */
export type LeftStackAssets = {
  /** Frame box Server Time */
  serverTimeFrame?: any;
  /** Badge piccolo icona clock (override 🕐) */
  serverTimeIcon?: any;

  /** Frame SP Offer (bundle esclusivo) */
  spOfferFrame?: any;
  spOfferBadge?: any;        // badge "SP" a sinistra
  spOfferArrow?: any;        // freccia ›

  /** Frame comune crystal pack (se shared) */
  crystalPackFrame?: any;
  /** Frame specifico per tier (2, 3, 4, 5…) — sovrascrive crystalPackFrame */
  crystalPackFrameByTier?: Record<number, any>;
  /** Icona gem pack (override 💎) */
  crystalPackIcon?: any;
};
export const HOME_LEFT_STACK: LeftStackAssets = {};

/* ───── Pack E — Right Mode Panel (Arena/Blessing/Trial/Battle/Research) ───── */
export type ModePanelAssets = {
  /** Frame comune a tutti i 5 mode button (se i singoli HOME_BUTTONS non bastano) */
  commonFrame?: ButtonAsset;
  /** Icone singole (override); usate se HOME_BUTTONS[key].default è undefined */
  iconArena?: any;
  iconBlessing?: any;
  iconTrial?: any;
  iconBattle?: any;
  iconResearch?: any;
};
export const HOME_MODE_PANEL_ASSETS: ModePanelAssets = {};

/* ───── Pack F — Main Banner (Summon rate-up) ───── */
export type MainBannerAssets = {
  /** Frame principale del banner (9-slice consigliato) */
  frame?: any;
  nineSlice?: boolean;
  capInsets?: { top: number; left: number; bottom: number; right: number };
  /** Ribbon "RATE-UP" decorativo */
  ribbon?: any;
  /** Badge "RATE-UP" alternativo (piccolo tag) */
  rateUpBadge?: any;
  /** Bottone SUMMON CTA */
  summonCta?: ButtonAsset;
  /** Cornice intorno all'artwork hero featured */
  characterFrame?: any;
  /** Sparkle/FX decorativo (override ✨) */
  sparkle?: any;
};
export const HOME_MAIN_BANNER_ASSETS: MainBannerAssets = {};

/* ────────────────────────────── BUTTONS ────────────────────────────── */
/**
 * Button asset con stati. In assenza di asset, il componente renderizza
 * un icon fallback da emoji/testo — neutro, non art-directed.
 */
export type ButtonAsset = {
  default?: any;
  pressed?: any;
  selected?: any;
  disabled?: any;
  /** se true: il bottone è quadrato/rotondo con solo icona (no label sovrapposta) */
  iconOnly?: boolean;
};

export type ButtonKey =
  | 'wheel' | 'quest' | 'event'
  | 'arena' | 'blessing' | 'trial' | 'battle' | 'research'
  | 'goldPlus' | 'gemsPlus';

export const HOME_BUTTONS: Record<ButtonKey, ButtonAsset> = {
  wheel:    {},
  quest:    {},
  event:    {},
  arena:    {},
  blessing: {},
  trial:    {},
  battle:   {},
  research: {},
  goldPlus: {},
  gemsPlus: {},
};

/* ─────────────────────────── BOTTOM NAV ICONS ─────────────────────────── */
export type NavKey =
  | 'chat' | 'bag' | 'artifact' | 'skill' | 'team'
  | 'guild' | 'shop' | 'forge' | 'menu';

export const HOME_NAV_ICONS: Record<NavKey, ButtonAsset> = {
  chat:     {},
  bag:      {},
  artifact: {},
  skill:    {},
  team:     {},
  guild:    {},
  shop:     {},
  forge:    {},
  menu:     {},
};

/* ─────────────────────────── PLAY SHIELD (central) ─────────────────────────── */
/**
 * Il pulsante centrale PLAY ha 3 stati visivi + 1 overlay FX separato (glow).
 * Il testo "PLAY" è BAKED negli asset: NON sovrapporre testo PLAY da codice.
 */
export type PlayShieldAsset = {
  idle?: any;
  pressed?: any;
  selected?: any;
  disabled?: any;
  /** overlay decorativo separato; la UI lo attiva via `usePlayGlow` flag */
  glow?: any;
};

export const HOME_PLAY_SHIELD: PlayShieldAsset = {
  idle:     require('../assets/home_nav/nav_btn_play_idle.png'),
  pressed:  require('../assets/home_nav/nav_btn_play_pressed.png'),
  selected: require('../assets/home_nav/nav_btn_play_selected.png'),
  glow:     require('../assets/home_nav/nav_btn_play_glow.png'),
};

/* ─────────────────────────── BOTTOM NAV BAR BASE ─────────────────────────── */
/**
 * Frame/sfondo della bottom nav custom (decorazione dorata con cornice + slot
 * centrale vuoto per lo scudo PLAY). Se `undefined` → fallback gradient in UI.
 */
export const HOME_NAV_BAR_BASE: any = require('../assets/home_nav/nav_bar_base.png');

/* ─────────────────────────── SIDE BUTTON FRAME ─────────────────────────── */
/**
 * Frame COMUNE per i 9 side buttons della bottom nav (chat/bag/artifact/skill/
 * team/guild/shop/forge/menu).
 *
 * Stati:
 *  - idle     → nav_btn_side_idle.png     (REALE)
 *  - selected → nav_btn_side_selected.png (REALE)
 *  - pressed  → idle (TODO: asset pressed futuro)
 *  - disabled → idle (TODO: asset disabled futuro)
 */
export const HOME_SIDE_FRAME: ButtonAsset = {
  default:  require('../assets/home_nav/nav_btn_side_idle.png'),
  selected: require('../assets/home_nav/nav_btn_side_selected.png'),
  pressed:  require('../assets/home_nav/nav_btn_side_idle.png'),      // TODO pressed reale
  disabled: require('../assets/home_nav/nav_btn_side_idle.png'),      // TODO disabled reale
};

/* ─────────────────────────── SIDE BUTTON ICON IMAGES ─────────────────────────── */
/**
 * Icone PNG singole per ciascuno dei 9 side buttons. Vanno SOPRA il frame
 * comune (HOME_SIDE_FRAME). Se un'icona manca (`undefined`), il NavBtn
 * mostra l'emoji fallback.
 *
 * Mapping 1:1 con i file canonici forniti dall'art team:
 */
export const HOME_NAV_ICON_IMAGES: Record<NavKey, any> = {
  chat:     require('../assets/home_nav/icons/icon_nav_chat.png'),
  bag:      require('../assets/home_nav/icons/icon_nav_bag.png'),
  artifact: require('../assets/home_nav/icons/icon_nav_artifact.png'),
  skill:    require('../assets/home_nav/icons/icon_nav_skill.png'),
  team:     require('../assets/home_nav/icons/icon_nav_team.png'),
  guild:    require('../assets/home_nav/icons/icon_nav_guild.png'),
  shop:     require('../assets/home_nav/icons/icon_nav_shop.png'),
  forge:    require('../assets/home_nav/icons/icon_nav_forge.png'),
  menu:     require('../assets/home_nav/icons/icon_nav_menu.png'),
};

/* ─────────────────────────── BANNERS ─────────────────────────── */
export type BannerAsset = {
  /** sfondo frame (può contenere decoro dorato) */
  frame?: any;
  /** eventuale overlay di ribbon "RATE-UP" etc. */
  ribbon?: any;
};

export type BannerKey = 'summonMain' | 'event1' | 'event2';

export const HOME_BANNERS: Record<BannerKey, BannerAsset> = {
  summonMain: {},
  event1:     {},
  event2:     {},
};

/* ─────────────────────────── NAVIGATION ROUTES ─────────────────────────── */
/**
 * Mapping centralizzato bottone → route. Evita hardcode sparsi in home.tsx.
 * Modificare QUI quando una feature cambia destinazione.
 */
export const HOME_ROUTES: Partial<Record<ButtonKey | NavKey | 'heroTap' | 'mainBanner' | 'play' | 'profileTap' | 'vipTap' | 'spiritoTap' | 'titleTap' | 'spOffer', string>> = {
  wheel:    '/(tabs)/gacha',
  quest:    '/quests',
  event:    '/events',
  arena:    '/arena',
  blessing: '/blessings',
  trial:    '/tower',
  battle:   '/story',
  research: '',            // vuoto = apre overflow (no destinazione inventata)
  goldPlus: '/shop',
  gemsPlus: '/shop',

  chat:     '',            // '' = apre pannello chat in-home
  bag:      '/equipment',
  artifact: '/artifacts',
  skill:    '',            // overflow
  team:     '/(tabs)/heroes',
  guild:    '/guild',
  shop:     '/shop',
  forge:    '/soul-forge',
  menu:     '',            // apre overflow

  heroTap:    '/sanctuary',
  mainBanner: '/(tabs)/gacha',
  play:       '/combat',

  profileTap: '/profile',
  vipTap:     '/vip',
  spiritoTap: '/profile',
  titleTap:   '/achievements',
  spOffer:    '/shop',
};

// Pre-QA Stabilization 112 — Shared Pre-QA Navigation Guard.
//
// Unico set canonico di route bloccate / categorie QA nascoste durante la
// closed alpha pre-QA. Usato da Home, Menu, Tabs, HomeOverflow.
//
// SAFETY:
// - default OFF: blocca finche' EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE non e' true.
// - no false-ready labels.
// - no silent s1 fallback.
// - dev/QA route richiedono EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true.

const TRUTHY = new Set(['true', '1', 'yes', 'on']);

function _truthy(name: string, fallback = false): boolean {
  const v = (process.env as Record<string, string | undefined>)[name];
  if (v === undefined || v === null || v === '') return fallback;
  return TRUTHY.has(String(v).trim().toLowerCase());
}

// Set canonico di route PLAYER-FACING UNSAFE / DEFERRED / LEGACY bloccate di default.
export const PRE_QA_BLOCKED_PLAYER_ROUTES: ReadonlySet<string> = new Set<string>([
  '/pvp',
  '/battlepass',
  '/item-shop',
  '/shop',
  '/vip',
  '/guild',
  '/gvg',
  '/raid',
  '/territory',
  '/plaza',
  '/dm',
  '/events',
  '/gacha',
  '/sanctuary',
  '/friends',
  '/level-sharing',
  '/cosmetics',
  '/exclusive-items',
  '/unique-items',
  '/artifacts',
  '/constellations',
  '/fragments',
  '/runes',
  '/affinity',
  '/mail',
  '/wallet',
  '/materials',
]);

// Set canonico di categorie QA/dev nascoste di default.
export const PRE_QA_BLOCKED_CATEGORIES: ReadonlySet<string> = new Set<string>([
  'Playability & Announcements QA (v93)',
  'Modalit\u00e0 Live & Guild QA (v92)',
]);

export function preQaUnsafeVisible(): boolean {
  return _truthy('EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE', false);
}

export function preQaDevQaVisible(): boolean {
  return _truthy('EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE', false);
}

export function preQaGachaUiVisible(): boolean {
  return _truthy('EXPO_PUBLIC_GACHA_UI_ENABLED', false);
}

// Helper: decide se una route player-facing deve essere visibile in Home/Menu.
export function isRouteAllowedInPreQa(route: string): boolean {
  if (preQaUnsafeVisible()) return true;
  // Normalizza in modo che '/pvp/some-sub' venga bloccato come '/pvp'.
  for (const blocked of PRE_QA_BLOCKED_PLAYER_ROUTES) {
    if (route === blocked || route.startsWith(blocked + '/')) return false;
  }
  return true;
}

// Helper: decide se una categoria menu/home deve essere visibile.
export function isCategoryAllowedInPreQa(title: string): boolean {
  if (preQaDevQaVisible()) return true;
  return !PRE_QA_BLOCKED_CATEGORIES.has(title);
}

// Sentinel canonico per loaders che richiedono server selezionato.
export const SELECTED_SERVER_REQUIRED_BLOCKER = 'SELECTED_SERVER_REQUIRED';

// Honest blocker name per la pre-QA cleanup.
export const PRE_QA_ROUTE_BLOCKED_TOKEN = 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED';

const _api = {
  PRE_QA_BLOCKED_PLAYER_ROUTES,
  PRE_QA_BLOCKED_CATEGORIES,
  isRouteAllowedInPreQa,
  isCategoryAllowedInPreQa,
  preQaUnsafeVisible,
  preQaDevQaVisible,
  preQaGachaUiVisible,
  SELECTED_SERVER_REQUIRED_BLOCKER,
  PRE_QA_ROUTE_BLOCKED_TOKEN,
};

export default _api;

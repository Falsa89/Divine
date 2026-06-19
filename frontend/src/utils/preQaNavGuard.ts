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

// Normalizza route alias: /(tabs)/x -> /x, /(stack)/x -> /x, etc.
// Pre-QA Stabilization 114: garantisce che /(tabs)/gacha venga riconosciuto come /gacha.
export function normalizeRoute(route: string): string {
  if (!route) return route;
  // Strip parametri/query.
  const base = String(route).split('?')[0].split('#')[0];
  // Pattern /(group)/x -> /x.
  const m = base.match(/^\/\([^)]+\)(\/.*)?$/);
  if (m) return m[1] || '/';
  return base;
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
  // Pre-QA Stabilization 114 — missing/dead-link routes da bloccare onestamente.
  '/quests',
  '/arena',
  '/blessings',
  '/profile',
  // Pre-QA Stabilization 115E — Tower legacy route fail-closed.
  '/tower',
  // Pre-QA Stabilization 115A — HomeOverflow dead-link `/research` (no research.tsx).
  '/research',
  // Pre-QA Pack 119B — Catalog/internal/dev-only routes nascoste dal menu pubblico.
  // Le pagine restano accessibili via deep link interno per QA, ma non
  // appaiono in /(tabs)/menu come voci player-facing.
  '/skill-status-vfx-catalogs',
  '/hero-skill-kits-catalog',
  '/safe-previews',
  '/playable-mode-battle-preview',
]);

// Set canonico di categorie QA/dev nascoste di default.
export const PRE_QA_BLOCKED_CATEGORIES: ReadonlySet<string> = new Set<string>([
  'Playability & Announcements QA (v93)',
  'Modalit\u00e0 Live & Guild QA (v92)',
  // Pre-QA Pack 119B — sezione deprecated Battle Preview wireframe (v88/v90).
  // Le voci collegate (`/playable-mode-battle-preview?mode=...`) restano
  // disponibili in dev/QA gated; nascoste dal menu pubblico.
  'Battle Preview QA (v88) \u2014 Wireframe Deprecato v90',
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
  // Pre-QA Stabilization 114: normalizza alias /(tabs)/x -> /x prima del lookup.
  const normalized = normalizeRoute(route);
  for (const blocked of PRE_QA_BLOCKED_PLAYER_ROUTES) {
    if (normalized === blocked || normalized.startsWith(blocked + '/')) return false;
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

// =============================================================================
// PACK 128 \u2014 Route allowlist registry (additivo, append-only).
// =============================================================================
// Lista esplicita POSITIVA delle route player-facing consentite in pre-QA.
// Coerente con la blocklist `PRE_QA_BLOCKED_PLAYER_ROUTES` ma orientata
// allow-first: ogni route non in questa lista \u00e8 considerata non-allowlisted
// e va trattata come deeplink/route fail-closed.
// Non altera il comportamento del guard esistente (`isRouteAllowedInPreQa`),
// che resta blocklist-based per backward compatibility.
export const PRE_QA_ROUTE_ALLOWLIST: ReadonlySet<string> = new Set<string>([
  // Auth / onboarding
  '/login',
  '/register',
  '/servers',
  '/select-home-hero',
  '/',
  '/index',
  // Tab core (home/menu/heroes/battle/gacha tab UI, gate logico altrove)
  '/(tabs)/home',
  '/(tabs)/menu',
  '/(tabs)/heroes',
  '/(tabs)/battle',
  // Hero read-only / collection / encyclopedia
  '/hero-collection',
  '/hero-detail',
  '/hero-encyclopedia',
  '/hero-viewer',
  // Team editor + pre-battle lobby preview (gated via QA team save env)
  '/pre-battle-lobby',
  '/combat',
  // Safe previews hub + design-only catalogs
  // NB: `/safe-previews`, `/skill-status-vfx-catalogs`, `/hero-skill-kits-catalog`
  // sono intenzionalmente NON in allowlist Pack 128: la blocklist Pack 119B
  // li classifica come "hidden dal menu pubblico ma accessibili via deeplink
  // dev/QA gated da EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE". `classifyDeeplink`
  // li tratta come BLOCKED_DEFERRED via precedenza blocklist, che \u00e8 il
  // comportamento corretto pre-QA.
  '/alpha-preview-hub',
  '/alpha-codex',
  '/alpha-guide',
  '/status-codex',
  '/synergy-codex',
  '/guide',
  '/divine-weapons-catalog',
]);

/** Restituisce true se `route` (eventualmente con alias `/(group)/x`) \u00e8
 *  esplicitamente nell'allowlist Pack 128. */
export function isRouteInPreQaAllowlist(route: string): boolean {
  if (!route) return false;
  const normalized = normalizeRoute(route);
  if (PRE_QA_ROUTE_ALLOWLIST.has(normalized)) return true;
  // Tollera path con suffissi (es. `/hero-detail/123` se entry e' `/hero-detail`).
  for (const allowed of PRE_QA_ROUTE_ALLOWLIST) {
    if (normalized === allowed) return true;
    if (normalized.startsWith(allowed + '/')) return true;
  }
  return false;
}

/** Decide la disposizione di un deeplink in pre-QA:
 *  - 'ALLOW'                 \u2192 route \u00e8 in allowlist e non in blocklist.
 *  - 'BLOCKED_DEFERRED'      \u2192 route \u00e8 in blocklist legacy/deferred.
 *  - 'BLOCKED_NOT_ALLOWLISTED'\u2192 route non in allowlist (deny-default).
 *  - 'BLOCKED_NOT_FOUND'     \u2192 route vuota/non valida.
 */
export type DeeplinkDisposition =
  | 'ALLOW'
  | 'BLOCKED_DEFERRED'
  | 'BLOCKED_NOT_ALLOWLISTED'
  | 'BLOCKED_NOT_FOUND';

export function classifyDeeplink(route: string): DeeplinkDisposition {
  if (!route || typeof route !== 'string') return 'BLOCKED_NOT_FOUND';
  const normalized = normalizeRoute(route);
  // 1) Blocklist Pack 112+ ha precedenza (legacy/deferred player-dangerous).
  for (const blocked of PRE_QA_BLOCKED_PLAYER_ROUTES) {
    if (normalized === blocked || normalized.startsWith(blocked + '/')) {
      return 'BLOCKED_DEFERRED';
    }
  }
  // 2) Override env: se EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=true, considera tutto allowed.
  if (preQaUnsafeVisible()) return 'ALLOW';
  // 3) Allowlist Pack 128 (deny-default).
  if (isRouteInPreQaAllowlist(normalized)) return 'ALLOW';
  return 'BLOCKED_NOT_ALLOWLISTED';
}

const _api = {
  PRE_QA_BLOCKED_PLAYER_ROUTES,
  PRE_QA_BLOCKED_CATEGORIES,
  PRE_QA_ROUTE_ALLOWLIST,
  isRouteAllowedInPreQa,
  isRouteInPreQaAllowlist,
  classifyDeeplink,
  isCategoryAllowedInPreQa,
  preQaUnsafeVisible,
  preQaDevQaVisible,
  preQaGachaUiVisible,
  normalizeRoute,
  SELECTED_SERVER_REQUIRED_BLOCKER,
  PRE_QA_ROUTE_BLOCKED_TOKEN,
};

export default _api;

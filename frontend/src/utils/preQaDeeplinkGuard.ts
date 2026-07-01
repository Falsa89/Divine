// Pack 128 — Pre-QA Deeplink Guard (helper puro, non ancora mountato a runtime).
//
// Scopo:
//   Fornire una funzione pura `interceptDeeplink(url, opts)` che data una URL
//   esterna (deeplink/scheme) decide se aprire la route, mostrare un blocker
//   safe, o redirectare a una schermata sicura. Non chiama alcun endpoint
//   mutativo e non emette navigazione di per se' (rinvia all'host expo-router).
//
// SAFETY:
//   - default fail-closed se la route non e' in allowlist Pack 128.
//   - non bypassa la blocklist Pack 112+ (PRE_QA_BLOCKED_PLAYER_ROUTES).
//   - rispetta EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE come override
//     coerente con il guard esistente.
//   - NON e' mountato in _layout.tsx in Pack 128 per minimizzare touch UI.
//     Vedi marker `pack_128_route_deeplink_lockdown_marker.json` per stato
//     di enforcement (VALIDATED_ONLY_HELPER_NOT_MOUNTED).
//
// Categorie di errore strutturato (allineate alla §9 del prompt Pack 128):
//   - 'locked'             : route nota ma in blocklist legacy/deferred
//   - 'blocked'            : route attualmente bloccata da policy pre-QA
//   - 'pre_qa_blocked'     : alias semantico per blocco pre-QA generico
//   - 'not_found'          : route non riconosciuta
//   - 'legacy_disabled'    : route legacy disabilitata
//
// NB: questo file e' importato/letto solo da chi mountera' l'intercept guard
// (Pack 128.x o Pack 129). In Pack 128 ne validiamo la presenza statica.

import {
  classifyDeeplink,
  normalizeRoute,
  PRE_QA_ROUTE_BLOCKED_TOKEN,
  type DeeplinkDisposition,
} from './preQaNavGuard';

export type StructuredErrorCode =
  | 'locked'
  | 'blocked'
  | 'pre_qa_blocked'
  | 'auth_missing'
  | 'not_found'
  | 'legacy_disabled';

export interface DeeplinkInterceptResult {
  decision: 'ALLOW' | 'REDIRECT_SAFE' | 'SHOW_LOCKED';
  normalizedRoute: string;
  errorCode?: StructuredErrorCode;
  errorToken?: string;
  safeRedirect?: string;
}

const SAFE_HOME_ROUTE = '/(tabs)/home';
const PREVIEW_LOCAL_COMBAT_BLOCKER = 'PREVIEW_LOCAL_COMBAT_DEEPLINK_BLOCKED_PRE_QA';

/** Parse minimo di una URL deeplink → path. Tollerante a scheme custom. */
export function extractPath(url: string): string {
  if (!url) return '';
  try {
    // expo-linking style: "divinewaifus://route/path" o "/route/path"
    const stripped = url.replace(/^[a-z][a-z0-9+\-.]*:\/\//i, '');
    const after = stripped.indexOf('/') === -1 ? '/' + stripped : stripped.substring(stripped.indexOf('/'));
    return after.split('?')[0].split('#')[0];
  } catch (_e) {
    return '';
  }
}

function hasPreviewLocalCombatQuery(url: string, path: string): boolean {
  const normalized = normalizeRoute(path);
  if (normalized !== '/combat') return false;
  let decoded = '';
  try {
    decoded = decodeURIComponent(url || '').toLowerCase();
  } catch (_e) {
    decoded = String(url || '').toLowerCase();
  }
  return (
    decoded.includes('preview_local')
    || decoded.includes('server_id=preview')
    || decoded.includes('is_preview=true')
  );
}

/** Decide come trattare un deeplink in pre-QA. */
export function interceptDeeplink(
  url: string,
  opts?: { authMissing?: boolean }
): DeeplinkInterceptResult {
  const path = extractPath(url);
  if (!path) {
    return {
      decision: 'SHOW_LOCKED',
      normalizedRoute: '',
      errorCode: 'not_found',
      errorToken: PRE_QA_ROUTE_BLOCKED_TOKEN,
    };
  }
  if (opts?.authMissing) {
    return {
      decision: 'REDIRECT_SAFE',
      normalizedRoute: normalizeRoute(path),
      errorCode: 'auth_missing',
      safeRedirect: '/login',
    };
  }
  if (hasPreviewLocalCombatQuery(url, path)) {
    return {
      decision: 'SHOW_LOCKED',
      normalizedRoute: normalizeRoute(path),
      errorCode: 'pre_qa_blocked',
      errorToken: PREVIEW_LOCAL_COMBAT_BLOCKER,
    };
  }
  const disposition: DeeplinkDisposition = classifyDeeplink(path);
  const normalized = normalizeRoute(path);
  switch (disposition) {
    case 'ALLOW':
      return { decision: 'ALLOW', normalizedRoute: normalized };
    case 'BLOCKED_DEFERRED':
      return {
        decision: 'SHOW_LOCKED',
        normalizedRoute: normalized,
        errorCode: 'legacy_disabled',
        errorToken: PRE_QA_ROUTE_BLOCKED_TOKEN,
      };
    case 'BLOCKED_NOT_ALLOWLISTED':
      return {
        decision: 'REDIRECT_SAFE',
        normalizedRoute: normalized,
        errorCode: 'pre_qa_blocked',
        safeRedirect: SAFE_HOME_ROUTE,
        errorToken: PRE_QA_ROUTE_BLOCKED_TOKEN,
      };
    case 'BLOCKED_NOT_FOUND':
    default:
      return {
        decision: 'SHOW_LOCKED',
        normalizedRoute: normalized,
        errorCode: 'not_found',
        errorToken: PRE_QA_ROUTE_BLOCKED_TOKEN,
      };
  }
}

export default {
  extractPath,
  interceptDeeplink,
  SAFE_HOME_ROUTE,
};

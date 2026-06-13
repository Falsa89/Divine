// Pre-QA Stabilization 115C — canonical backend URL helper.
//
// Risolve la URL base del backend in modo coerente fra `frontend/utils/api.ts`
// e `frontend/app/servers.tsx`, eliminando la divergenza tra Server Select e
// resto della UI.
//
// Strategia:
//  - WEB (Platform.OS === 'web') → ritorna stringa vuota (relative URL, nginx
//    proxy `/api/*` -> backend). Compatibile con il comportamento storico.
//  - Mobile / Expo Go → preferisce le var d'ambiente esplicite, nell'ordine:
//      1. EXPO_BACKEND_URL (canonical, gia' usato da servers.tsx)
//      2. Constants.expoConfig.extra.backendUrl
//      3. Constants.expoConfig.extra.EXPO_PACKAGER_HOSTNAME / proxy
//      4. process.env.EXPO_PACKAGER_HOSTNAME / proxy
//  - Non introduce segreti, non logga URL.
//
// SAFETY:
//  - read-only, nessun side-effect
//  - non normalizza/append `/api` (lo fa il caller)
//  - nessun import di authTokenCompat (evita coupling circolare con api.ts)

import { Platform } from 'react-native';
import Constants from 'expo-constants';

/**
 * Ritorna la URL base del backend (senza trailing slash).
 * Stringa vuota = usa URL relativa (web/nginx proxy).
 */
export function getCanonicalBackendUrl(): string {
  if (Platform.OS === 'web') {
    return '';
  }
  // 1) Var esplicita EXPO_BACKEND_URL (preferita).
  const fromEnv = (process.env.EXPO_BACKEND_URL as string | undefined)
    || (Constants?.expoConfig?.extra as any)?.EXPO_BACKEND_URL;
  if (fromEnv && String(fromEnv).trim().length > 0) {
    return String(fromEnv).replace(/\/$/, '');
  }
  // 2) Constants.expoConfig.extra.backendUrl (compat servers.tsx).
  const fromExtra = (Constants?.expoConfig?.extra as any)?.backendUrl;
  if (fromExtra && String(fromExtra).trim().length > 0) {
    return String(fromExtra).replace(/\/$/, '');
  }
  // 3) Hostname Expo Packager (compat storica api.ts).
  const hostname = (Constants?.expoConfig?.extra as any)?.EXPO_PACKAGER_HOSTNAME
    || (process.env.EXPO_PACKAGER_HOSTNAME as string | undefined)
    || (Constants?.expoConfig?.extra as any)?.EXPO_PACKAGER_PROXY_URL
    || (process.env.EXPO_PACKAGER_PROXY_URL as string | undefined)
    || '';
  return String(hostname).replace(/\/$/, '');
}

export default getCanonicalBackendUrl;

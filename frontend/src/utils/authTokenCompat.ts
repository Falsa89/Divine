// Pre-QA Stabilization 110 — Auth Token Compatibility Bridge.
//
// Esistono due path di login player-facing:
//  - login default -> AsyncStorage key 'token' (../context/AuthContext)
//  - login v96    -> SecureStore  key 'v96_auth_token' (../auth/AuthContext)
//
// Questo helper centralizza la lettura del token, controllando entrambe le
// locations. NESSUN downgrade di sicurezza: SecureStore resta canonico, ma
// se assente (utente entrato dal login default) cadiamo su AsyncStorage
// SOLO per la lettura. NIENTE plaintext log, niente persistenza di token in
// posti nuovi.
//
// Uso:
//   const tok = await getAuthTokenCompat();
//   if (!tok) { ...gestire NO_TOKEN... }
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

export const AUTH_TOKEN_SECURE_KEY = 'v96_auth_token';
export const AUTH_TOKEN_ASYNC_KEY = 'token';

export type AuthTokenSource =
  | 'secure_store_v96'
  | 'async_storage_default'
  | 'none';

export type AuthTokenLookup = {
  token: string | null;
  source: AuthTokenSource;
  no_silent_fallback: true;
};

export async function getAuthTokenCompat(): Promise<AuthTokenLookup> {
  // 1) SecureStore canonical key.
  try {
    const sec = await SecureStore.getItemAsync(AUTH_TOKEN_SECURE_KEY);
    if (sec && String(sec).trim().length > 0) {
      return { token: sec, source: 'secure_store_v96', no_silent_fallback: true };
    }
  } catch (_e) { /* silent: SecureStore unavailable on web */ }
  // 2) AsyncStorage default login fallback.
  try {
    const asy = await AsyncStorage.getItem(AUTH_TOKEN_ASYNC_KEY);
    if (asy && String(asy).trim().length > 0) {
      return { token: asy, source: 'async_storage_default', no_silent_fallback: true };
    }
  } catch (_e) { /* silent */ }
  return { token: null, source: 'none', no_silent_fallback: true };
}

// Helper opzionale: costruisce un Authorization header se token disponibile.
export async function authHeaderCompat(): Promise<Record<string, string>> {
  const lookup = await getAuthTokenCompat();
  if (!lookup.token) return {};
  return { Authorization: `Bearer ${lookup.token}` };
}

export default getAuthTokenCompat;

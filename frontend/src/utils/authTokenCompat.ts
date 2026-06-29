import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

export const AUTH_TOKEN_SECURE_KEY = 'v96_auth_token';
export const AUTH_ACCOUNT_SECURE_KEY = 'v96_auth_account';
export const AUTH_TOKEN_ASYNC_KEY = 'token';
export const SELECTED_SERVER_ID_KEY = 'v101_selected_server_id';
export const SELECTED_SERVER_NAME_KEY = 'v102_selected_server_name';

export type AuthTokenSource =
  | 'secure_store_v96'
  | 'migrated_legacy_async_storage'
  | 'async_storage_default'
  | 'conflict'
  | 'none';

export type AuthTokenLookup = {
  token: string | null;
  source: AuthTokenSource;
  no_silent_fallback: true;
  conflict?: boolean;
};

function normalizeToken(value: string | null | undefined): string | null {
  const token = typeof value === 'string' ? value.trim() : '';
  return token.length > 0 ? token : null;
}

async function readSecureToken(): Promise<string | null> {
  try {
    return normalizeToken(await SecureStore.getItemAsync(AUTH_TOKEN_SECURE_KEY));
  } catch (_e) {
    return null;
  }
}

async function readLegacyToken(): Promise<string | null> {
  try {
    return normalizeToken(await AsyncStorage.getItem(AUTH_TOKEN_ASYNC_KEY));
  } catch (_e) {
    return null;
  }
}

async function removeLegacyToken(): Promise<void> {
  try {
    await AsyncStorage.removeItem(AUTH_TOKEN_ASYNC_KEY);
  } catch (_e) {}
}

export async function persistCanonicalAuthToken(token: string | null): Promise<void> {
  const canonicalToken = normalizeToken(token);
  try {
    if (canonicalToken) {
      await SecureStore.setItemAsync(AUTH_TOKEN_SECURE_KEY, canonicalToken);
    } else {
      await SecureStore.deleteItemAsync(AUTH_TOKEN_SECURE_KEY);
    }
  } catch (_e) {
    if (canonicalToken) {
      await AsyncStorage.setItem(AUTH_TOKEN_ASYNC_KEY, canonicalToken);
      return;
    }
  }
  await removeLegacyToken();
}

export async function persistV96AuthAccount(account: unknown | null): Promise<void> {
  try {
    if (account) {
      await SecureStore.setItemAsync(AUTH_ACCOUNT_SECURE_KEY, JSON.stringify(account));
    } else {
      await SecureStore.deleteItemAsync(AUTH_ACCOUNT_SECURE_KEY);
    }
  } catch (_e) {}
}

export async function clearAuthStorage(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(AUTH_TOKEN_SECURE_KEY).catch(() => {}),
    SecureStore.deleteItemAsync(AUTH_ACCOUNT_SECURE_KEY).catch(() => {}),
    AsyncStorage.removeItem(AUTH_TOKEN_ASYNC_KEY).catch(() => {}),
    AsyncStorage.removeItem(SELECTED_SERVER_ID_KEY).catch(() => {}),
    AsyncStorage.removeItem(SELECTED_SERVER_NAME_KEY).catch(() => {}),
  ]);
}

export async function getAuthTokenCompat(): Promise<AuthTokenLookup> {
  const [secureToken, legacyToken] = await Promise.all([
    readSecureToken(),
    readLegacyToken(),
  ]);

  if (secureToken && legacyToken && secureToken !== legacyToken) {
    await clearAuthStorage();
    return {
      token: null,
      source: 'conflict',
      no_silent_fallback: true,
      conflict: true,
    };
  }

  if (secureToken) {
    if (legacyToken) await removeLegacyToken();
    return { token: secureToken, source: 'secure_store_v96', no_silent_fallback: true };
  }

  if (legacyToken) {
    await persistCanonicalAuthToken(legacyToken);
    return {
      token: legacyToken,
      source: 'migrated_legacy_async_storage',
      no_silent_fallback: true,
    };
  }

  return { token: null, source: 'none', no_silent_fallback: true };
}

export async function authHeaderCompat(): Promise<Record<string, string>> {
  const lookup = await getAuthTokenCompat();
  if (!lookup.token) return {};
  return { Authorization: `Bearer ${lookup.token}` };
}

export default getAuthTokenCompat;

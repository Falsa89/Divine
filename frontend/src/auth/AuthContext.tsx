/**
 * v96 — Auth context.
 *
 * Pack: MEGA_RELEASE_ACCELERATION_45_v96.
 *
 * Funzionalità:
 *  - Session restore da expo-secure-store all'avvio.
 *  - login(provider): Google / Apple / Guest (con fallback sandbox se credentials mancanti).
 *  - logout().
 *  - account info (alias-safe, no PII raw).
 *
 * Safety:
 *  - Token in expo-secure-store (NON plain AsyncStorage).
 *  - NO raw OAuth token loggato in console.
 *  - Marker provider_sandbox visibile in UI.
 *  - Fallback dichiarato.
 */
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'v96_auth_token';
const ACCOUNT_KEY = 'v96_auth_account';
const BACKEND = (process.env.EXPO_BACKEND_URL || '').toString();

export type AuthProvider = 'google' | 'apple' | 'guest';

export type AuthAccount = {
  user_id: string;
  account_id: string;
  alias: string;
  username?: string;
  provider: string;
  provider_sandbox: boolean;
  level: number;
  created_at?: string | null;
  last_login?: string | null;
};

export type AuthState = {
  loading: boolean;
  authenticated: boolean;
  token: string | null;
  account: AuthAccount | null;
  error: string | null;
  providerStatus: any | null;
  login: (provider: AuthProvider, opts?: { alias_hint?: string; sandbox_subject?: string; email?: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshMe: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export const useAuth = (): AuthState => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside <AuthProvider>');
  }
  return ctx;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [account, setAccount] = useState<AuthAccount | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [providerStatus, setProviderStatus] = useState<any | null>(null);

  const persist = useCallback(async (t: string | null, a: AuthAccount | null) => {
    try {
      if (t) await SecureStore.setItemAsync(TOKEN_KEY, t);
      else await SecureStore.deleteItemAsync(TOKEN_KEY);
      if (a) await SecureStore.setItemAsync(ACCOUNT_KEY, JSON.stringify(a));
      else await SecureStore.deleteItemAsync(ACCOUNT_KEY);
    } catch (e) {
      // SecureStore può non essere supportato su web → degrade silently
    }
  }, []);

  const refreshMe = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${BACKEND}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!r.ok) {
        // token invalido/scaduto → logout silenzioso
        await persist(null, null);
        setToken(null);
        setAccount(null);
        return;
      }
      const d = await r.json();
      if (d?.authenticated && d?.account) {
        setAccount(d.account as AuthAccount);
        await persist(token, d.account);
      }
    } catch (e: any) {
      // network error: mantieni stato locale
    }
  }, [token, persist]);

  // Session restore + provider status
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [storedToken, storedAccount] = await Promise.all([
          SecureStore.getItemAsync(TOKEN_KEY).catch(() => null),
          SecureStore.getItemAsync(ACCOUNT_KEY).catch(() => null),
        ]);
        if (!cancelled && storedToken) {
          setToken(storedToken);
          if (storedAccount) {
            try { setAccount(JSON.parse(storedAccount)); } catch {}
          }
        }
        // Provider status (non auth-required)
        const r = await fetch(`${BACKEND}/api/auth/provider-status`);
        if (r.ok && !cancelled) {
          const d = await r.json();
          setProviderStatus(d);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // Quando il token cambia, esegui refreshMe per validare
  useEffect(() => {
    if (token && !account) {
      refreshMe();
    }
  }, [token, account, refreshMe]);

  const login = useCallback(async (provider: AuthProvider, opts?: { alias_hint?: string; sandbox_subject?: string; email?: string }) => {
    setError(null);
    setLoading(true);
    try {
      const body: any = {};
      if (provider === 'google') {
        body.sandbox_subject = opts?.sandbox_subject || `sandbox_g_${Date.now()}`;
        if (opts?.email) body.email = opts.email;
      } else if (provider === 'apple') {
        body.sandbox_subject = opts?.sandbox_subject || `sandbox_a_${Date.now()}`;
        if (opts?.email) body.email = opts.email;
      } else if (provider === 'guest') {
        body.alias_hint = opts?.alias_hint;
      }
      const r = await fetch(`${BACKEND}/api/auth/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const txt = await r.text().catch(() => '');
        throw new Error(`login_${provider}_failed_${r.status}_${txt.slice(0, 80)}`);
      }
      const d = await r.json();
      // NESSUN log del token (no raw OAuth)
      const newToken = d.token as string;
      const newAccount = d.account as AuthAccount;
      setToken(newToken);
      setAccount(newAccount);
      await persist(newToken, newAccount);
    } catch (e: any) {
      setError(e.message || 'login_error');
    } finally {
      setLoading(false);
    }
  }, [persist]);

  const logout = useCallback(async () => {
    setError(null);
    try {
      if (token) {
        await fetch(`${BACKEND}/api/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => {});
      }
    } finally {
      setToken(null);
      setAccount(null);
      await persist(null, null);
    }
  }, [token, persist]);

  const value: AuthState = {
    loading,
    authenticated: !!token && !!account,
    token,
    account,
    error,
    providerStatus,
    login,
    logout,
    refreshMe,
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

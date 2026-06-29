import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import {
  AUTH_ACCOUNT_SECURE_KEY,
  clearAuthStorage,
  getAuthTokenCompat,
  persistCanonicalAuthToken,
  persistV96AuthAccount,
} from '../utils/authTokenCompat';

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
    await persistCanonicalAuthToken(t);
    await persistV96AuthAccount(a);
  }, []);

  const refreshMe = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${BACKEND}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!r.ok) {
        await clearAuthStorage();
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
      // Network errors keep the local auth state until an explicit logout.
    }
  }, [token, persist]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [storedAuth, storedAccount] = await Promise.all([
          getAuthTokenCompat(),
          SecureStore.getItemAsync(AUTH_ACCOUNT_SECURE_KEY).catch(() => null),
        ]);
        if (!cancelled && storedAuth.conflict) {
          setError('auth_token_conflict');
        }
        if (!cancelled && storedAuth.token) {
          setToken(storedAuth.token);
          if (storedAccount) {
            try { setAccount(JSON.parse(storedAccount)); } catch {}
          }
        }
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
      await clearAuthStorage();
    }
  }, [token]);

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

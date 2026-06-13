// Pre-QA Stabilization 115C — apiCall() usa authTokenCompat + canonical backendUrl.
//
// PRIMA: apiCall leggeva solo il token diretto e aveva il proprio
//        getBaseUrl divergente da servers.tsx.
// DOPO:  apiCall usa authTokenCompat (SecureStore canonico, fallback Async) e
//        getCanonicalBackendUrl (helper condiviso).
//
// SAFETY: no token logs, no secret persistence, backward-compat preservata.

import { authHeaderCompat } from '../src/utils/authTokenCompat';
import { getCanonicalBackendUrl } from '../src/utils/backendUrl';

export async function apiCall(endpoint: string, options: RequestInit = {}) {
  // Pre-QA Stabilization 115C: bearer via authTokenCompat (SecureStore canonico
  // con fallback AsyncStorage). No token raw log.
  const authHdr = await authHeaderCompat();
  const headers: any = {
    'Content-Type': 'application/json',
    ...authHdr,
    ...options.headers,
  };

  const base = getCanonicalBackendUrl();
  const path = endpoint.startsWith('/api') ? endpoint : `/api${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const url = `${base}${path}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

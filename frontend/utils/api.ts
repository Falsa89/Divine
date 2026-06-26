// HOTFIX B — API ERROR CONTRACT + BLOCKER VISIBILITY
//
// PRIMA (Pre-QA Stabilization 115C):
//   apiCall lanciava `new Error(detail || HTTP X)` perdendo:
//     - HTTP status (4xx/5xx mascherato come stringa);
//     - body strutturato (detail come oggetto, code, blocker);
//     - response headers diagnostici emessi dal backend
//       (X-Blocker, X-Roster-Count, X-PSP-Lookup-Mode, X-Server-Scope).
//   Conseguenza: schermate trasformavano errori in "roster vuoto" generico,
//   senza modo di leggere il blocker o lo scope server lato UI.
//
// DOPO (HOTFIX B):
//   - Introduce la classe `ApiError` che preserva
//       status, data, detail, code, headers, diagnostics.
//   - `apiCall` su risposta non-ok lancia `ApiError` invece di `Error`.
//   - Nuovo `apiCallWithMeta` ritorna { data, status, headers, diagnostics }
//     anche su 200 OK, così la UI può leggere gli header diagnostici
//     (es. X-Roster-Count: 0 ⇒ roster realmente vuoto, vs blocker server).
//
// SAFETY:
//   - Zero DB writes, zero endpoint mutativi.
//   - Nessun cambio di header outbound (Authorization + Content-Type invariati).
//   - Backward-compat: `apiCall` ritorna ancora `data` su 2xx.
//   - Nessun log di token, secret o body sensibile.
//   - In assenza di header diagnostici (BE non li emette), i campi
//     `diagnostics.*` sono `null` — la UI deve gestirli come opzionali.

import { authHeaderCompat } from '../src/utils/authTokenCompat';
import { getCanonicalBackendUrl } from '../src/utils/backendUrl';

// Contract degli header diagnostici (case-insensitive lookup).
// Backend li può emettere su 200 OK (es. roster vuoto server-scoped) o su
// risposte di blocco (4xx con blocker code).
const DIAG_HEADER_KEYS = [
  'x-blocker',
  'x-roster-count',
  'x-psp-lookup-mode',
  'x-server-scope',
] as const;

export type ApiDiagnostics = {
  blocker: string | null;
  roster_count: number | null;
  psp_lookup_mode: string | null;
  server_scope: string | null;
  raw: Record<string, string>;
};

function extractDiagnostics(headers: Record<string, string>): ApiDiagnostics {
  const lower: Record<string, string> = {};
  Object.keys(headers || {}).forEach((k) => {
    lower[k.toLowerCase()] = headers[k];
  });
  const raw: Record<string, string> = {};
  DIAG_HEADER_KEYS.forEach((k) => {
    if (typeof lower[k] === 'string') raw[k] = lower[k];
  });
  const rosterRaw = lower['x-roster-count'];
  const rosterParsed =
    typeof rosterRaw === 'string' && rosterRaw.trim() !== ''
      ? Number(rosterRaw)
      : null;
  return {
    blocker: lower['x-blocker'] || null,
    roster_count:
      rosterParsed !== null && !Number.isNaN(rosterParsed) ? rosterParsed : null,
    psp_lookup_mode: lower['x-psp-lookup-mode'] || null,
    server_scope: lower['x-server-scope'] || null,
    raw,
  };
}

export class ApiError extends Error {
  status: number;
  data: any;
  detail: string | null;
  code: string | null;
  headers: Record<string, string>;
  diagnostics: ApiDiagnostics;

  constructor(args: {
    status: number;
    data: any;
    headers: Record<string, string>;
    message?: string;
  }) {
    const { status, data, headers } = args;
    let detail: string | null = null;
    let code: string | null = null;
    if (data && typeof data === 'object') {
      if (typeof data.detail === 'string') {
        detail = data.detail;
      } else if (data.detail && typeof data.detail === 'object') {
        // FastAPI emette spesso `detail` come oggetto strutturato con
        // `blocker` / `code` / `message`. Estraiamo entrambi.
        const d = data.detail;
        detail =
          (typeof d.message === 'string' && d.message) ||
          (typeof d.blocker === 'string' && d.blocker) ||
          (typeof d.code === 'string' && d.code) ||
          null;
        if (typeof d.code === 'string') code = d.code;
        if (!code && typeof d.blocker === 'string') code = d.blocker;
      }
      if (!code && typeof (data as any).code === 'string') {
        code = (data as any).code;
      }
      if (!code && typeof (data as any).blocker === 'string') {
        code = (data as any).blocker;
      }
    } else if (typeof data === 'string' && data) {
      detail = data;
    }
    const message = args.message || detail || `HTTP ${status}`;
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.detail = detail;
    this.code = code;
    this.headers = headers || {};
    this.diagnostics = extractDiagnostics(this.headers);
  }
}

function collectHeaders(response: Response): Record<string, string> {
  const headers: Record<string, string> = {};
  try {
    response.headers.forEach((value: string, key: string) => {
      headers[key.toLowerCase()] = value;
    });
  } catch (_e) {
    // Fallback: nessuna iterazione disponibile (edge case RN/web). No throw.
  }
  return headers;
}

async function parseBody(response: Response): Promise<any> {
  // Parsing best-effort: tentiamo JSON, fallback a stringa, fallback a null.
  // Non logghiamo il body (può contenere PII / dettagli QA).
  let text = '';
  try {
    text = await response.text();
  } catch (_e) {
    return null;
  }
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch (_e) {
    return text;
  }
}

export type ApiCallMeta<T = any> = {
  data: T;
  status: number;
  headers: Record<string, string>;
  diagnostics: ApiDiagnostics;
};

async function performRequest(endpoint: string, options: RequestInit) {
  // HOTFIX B: bearer via authTokenCompat (SecureStore canonico con fallback
  // AsyncStorage). No token raw log. Comportamento outbound invariato.
  const authHdr = await authHeaderCompat();
  const headers: any = {
    'Content-Type': 'application/json',
    ...authHdr,
    ...options.headers,
  };
  const base = getCanonicalBackendUrl();
  const path = endpoint.startsWith('/api')
    ? endpoint
    : `/api${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const url = `${base}${path}`;
  const response = await fetch(url, { ...options, headers });
  const responseHeaders = collectHeaders(response);
  const data = await parseBody(response);
  return { response, responseHeaders, data };
}

export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const { response, responseHeaders, data } = await performRequest(
    endpoint,
    options,
  );
  if (!response.ok) {
    throw new ApiError({
      status: response.status,
      data,
      headers: responseHeaders,
    });
  }
  return data;
}

export async function apiCallWithMeta<T = any>(
  endpoint: string,
  options: RequestInit = {},
): Promise<ApiCallMeta<T>> {
  const { response, responseHeaders, data } = await performRequest(
    endpoint,
    options,
  );
  if (!response.ok) {
    throw new ApiError({
      status: response.status,
      data,
      headers: responseHeaders,
    });
  }
  return {
    data: data as T,
    status: response.status,
    headers: responseHeaders,
    diagnostics: extractDiagnostics(responseHeaders),
  };
}

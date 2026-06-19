// Pack 129 — Structured Error Mapping (helper puro, additivo).
//
// Mappa i codici errore strutturati Pack 129 + i legacy blocker Pack 125 a
// messaggi italiani UI-friendly + categorie navigabili dall'app.
//
// Questo helper è opt-in: NON è ancora mountato nelle screen esistenti
// (es. battle.tsx ha già un suo handler basato su `blocker`). Future schermate
// possono adottarlo per coerenza UI.
//
// Categorie supportate (allineate con backend `category` field):
//   - 'auth'        : utente non autenticato / token scaduto
//   - 'server'      : server context mancante/invalido/PSP mancante
//   - 'team'        : team save / ownership / disponibilità eroe
//   - 'pre_qa'      : mutazione bloccata da Pack 128 middleware
//   - 'validation'  : payload/size/slot/duplicate
//   - 'locked'      : feature/flag locked
//   - 'not_found'   : risorsa non trovata

// =============================================================================
// Codici structured Pack 129 (specchio del backend `helpers/structured_errors.py`)
// =============================================================================
export const STRUCTURED_CODES = {
  // Auth
  AUTH_REQUIRED: 'AUTH_REQUIRED',
  // Server context
  SERVER_CONTEXT_REQUIRED: 'SERVER_CONTEXT_REQUIRED',
  SERVER_CONTEXT_INVALID: 'SERVER_CONTEXT_INVALID',
  SERVER_NOT_READY: 'SERVER_NOT_READY',
  SERVER_PROFILE_MISSING: 'SERVER_PROFILE_MISSING',
  SERVER_SCOPE_UNAVAILABLE: 'SERVER_SCOPE_UNAVAILABLE',
  SERVER_MISMATCH: 'SERVER_MISMATCH',
  // Team
  TEAM_SAVE_DISABLED_PRE_QA: 'TEAM_SAVE_DISABLED_PRE_QA',
  TEAM_INVALID_PAYLOAD: 'TEAM_INVALID_PAYLOAD',
  TEAM_INVALID_SIZE: 'TEAM_INVALID_SIZE',
  TEAM_INVALID_SLOT: 'TEAM_INVALID_SLOT',
  TEAM_DUPLICATE_HERO: 'TEAM_DUPLICATE_HERO',
  TEAM_HERO_NOT_OWNED: 'TEAM_HERO_NOT_OWNED',
  TEAM_HERO_NOT_AVAILABLE: 'TEAM_HERO_NOT_AVAILABLE',
  TEAM_FORMATION_BLOCKED_PRE_QA: 'TEAM_FORMATION_BLOCKED_PRE_QA',
  // Pre-QA
  PRE_QA_MUTATION_BLOCKED: 'PRE_QA_MUTATION_BLOCKED',
  FEATURE_LOCKED_PRE_QA: 'FEATURE_LOCKED_PRE_QA',
} as const;

export type StructuredCode = (typeof STRUCTURED_CODES)[keyof typeof STRUCTURED_CODES];
export type StructuredCategory =
  | 'auth' | 'server' | 'team' | 'pre_qa' | 'validation' | 'locked' | 'not_found';

// =============================================================================
// Legacy Pack 125 blocker → Pack 129 code aliases.
// =============================================================================
export const LEGACY_BLOCKER_TO_CODE: Record<string, StructuredCode> = {
  AUTHENTICATION_REQUIRED: STRUCTURED_CODES.AUTH_REQUIRED,
  AUTHENTICATION_INVALID: STRUCTURED_CODES.AUTH_REQUIRED,
  QA_TEAM_SAVE_DISABLED: STRUCTURED_CODES.TEAM_SAVE_DISABLED_PRE_QA,
  QA_TEAM_SAVE_ALLOWLIST_EMPTY: STRUCTURED_CODES.FEATURE_LOCKED_PRE_QA,
  QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED: STRUCTURED_CODES.FEATURE_LOCKED_PRE_QA,
  PLAYER_SERVER_PROFILE_REQUIRED: STRUCTURED_CODES.SERVER_PROFILE_MISSING,
  TEAM_TOO_LARGE: STRUCTURED_CODES.TEAM_INVALID_SIZE,
  DUPLICATE_POSITIONS: STRUCTURED_CODES.TEAM_INVALID_SLOT,
  DUPLICATE_HEROES: STRUCTURED_CODES.TEAM_DUPLICATE_HERO,
  OWNERSHIP_VALIDATION_FAILED: STRUCTURED_CODES.TEAM_HERO_NOT_OWNED,
};

// =============================================================================
// Code → categoria default.
// =============================================================================
export const CODE_TO_CATEGORY: Record<StructuredCode, StructuredCategory> = {
  AUTH_REQUIRED: 'auth',
  SERVER_CONTEXT_REQUIRED: 'server',
  SERVER_CONTEXT_INVALID: 'server',
  SERVER_NOT_READY: 'server',
  SERVER_PROFILE_MISSING: 'server',
  SERVER_SCOPE_UNAVAILABLE: 'server',
  SERVER_MISMATCH: 'server',
  TEAM_SAVE_DISABLED_PRE_QA: 'team',
  TEAM_INVALID_PAYLOAD: 'validation',
  TEAM_INVALID_SIZE: 'validation',
  TEAM_INVALID_SLOT: 'validation',
  TEAM_DUPLICATE_HERO: 'validation',
  TEAM_HERO_NOT_OWNED: 'team',
  TEAM_HERO_NOT_AVAILABLE: 'team',
  TEAM_FORMATION_BLOCKED_PRE_QA: 'pre_qa',
  PRE_QA_MUTATION_BLOCKED: 'pre_qa',
  FEATURE_LOCKED_PRE_QA: 'locked',
};

// =============================================================================
// Code → messaggio UI italiano user-friendly.
// =============================================================================
const CODE_TO_MESSAGE_IT: Record<StructuredCode, string> = {
  AUTH_REQUIRED: 'Accedi per continuare.',
  SERVER_CONTEXT_REQUIRED: 'Seleziona un server prima di procedere.',
  SERVER_CONTEXT_INVALID: 'Server non valido. Torna alla selezione server.',
  SERVER_NOT_READY: 'Server non pronto. Riprova fra qualche secondo.',
  SERVER_PROFILE_MISSING: 'Profilo server mancante. Crea il profilo per questo server.',
  SERVER_SCOPE_UNAVAILABLE: 'Impossibile verificare lo scope server. Riprova più tardi.',
  SERVER_MISMATCH: 'Il server richiesto non corrisponde al server attivo.',
  TEAM_SAVE_DISABLED_PRE_QA: 'Salvataggio formazione disabilitato in pre-QA.',
  TEAM_INVALID_PAYLOAD: 'Formazione non valida.',
  TEAM_INVALID_SIZE: 'La formazione deve avere al massimo 6 eroi.',
  TEAM_INVALID_SLOT: 'Posizioni duplicate nella formazione.',
  TEAM_DUPLICATE_HERO: 'Lo stesso eroe è stato inserito più volte.',
  TEAM_HERO_NOT_OWNED: 'Uno o più eroi non sono posseduti su questo server.',
  TEAM_HERO_NOT_AVAILABLE: 'Uno o più eroi non sono disponibili.',
  TEAM_FORMATION_BLOCKED_PRE_QA: 'Modifica formazione bloccata in pre-QA.',
  PRE_QA_MUTATION_BLOCKED: 'Operazione bloccata in modalità pre-QA.',
  FEATURE_LOCKED_PRE_QA: 'Funzionalità non disponibile in pre-QA.',
};

// =============================================================================
// Public API
// =============================================================================

export interface StructuredErrorEnvelope {
  code: StructuredCode;
  category: StructuredCategory;
  message: string;
  recoverable: boolean;
}

/** Mappa un codice strutturato o un blocker legacy in un envelope UI-ready. */
export function mapStructuredError(input: {
  code?: string | null;
  blocker?: string | null;
  detail?: string | null;
  category?: string | null;
  recoverable?: boolean;
}): StructuredErrorEnvelope {
  let code: StructuredCode | null = null;
  if (input.code && (STRUCTURED_CODES as Record<string, string>)[input.code] === input.code) {
    code = input.code as StructuredCode;
  } else if (input.blocker && LEGACY_BLOCKER_TO_CODE[input.blocker]) {
    code = LEGACY_BLOCKER_TO_CODE[input.blocker];
  }
  if (!code) {
    return {
      code: STRUCTURED_CODES.FEATURE_LOCKED_PRE_QA,
      category: 'locked',
      message: input.detail || 'Errore non classificato.',
      recoverable: input.recoverable ?? true,
    };
  }
  return {
    code,
    category: (input.category as StructuredCategory) || CODE_TO_CATEGORY[code],
    message: input.detail || CODE_TO_MESSAGE_IT[code],
    recoverable: input.recoverable ?? (CODE_TO_CATEGORY[code] !== 'auth' && code !== STRUCTURED_CODES.FEATURE_LOCKED_PRE_QA),
  };
}

/** Estrae un envelope da un errore lanciato da apiCall (struttura tipica:
 *  e.status, e.data.detail = string | { detail, code, category, ... } | { blocker, message }).
 */
export function envelopeFromApiError(err: any): StructuredErrorEnvelope {
  const status = err?.status || err?.response?.status;
  const raw = err?.data?.detail ?? err?.response?.data?.detail ?? err?.detail ?? null;
  if (raw && typeof raw === 'object') {
    return mapStructuredError({
      code: raw.code,
      blocker: raw.blocker,
      detail: raw.detail || raw.message,
      category: raw.category,
      recoverable: raw.recoverable,
    });
  }
  if (typeof raw === 'string') {
    return mapStructuredError({
      detail: raw,
      recoverable: status !== 401 && status !== 403,
    });
  }
  return mapStructuredError({
    detail: `Errore (${status || 'unknown'}).`,
    recoverable: true,
  });
}

export default {
  STRUCTURED_CODES,
  LEGACY_BLOCKER_TO_CODE,
  CODE_TO_CATEGORY,
  mapStructuredError,
  envelopeFromApiError,
};

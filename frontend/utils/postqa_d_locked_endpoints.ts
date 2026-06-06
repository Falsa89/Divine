/**
 * v108_POSTQA_D - Frontend reachability blocker (player-facing)
 *
 * PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS
 *
 * Lista statica degli endpoint legacy mutanti bloccati dal pack v108_POSTQA_D
 * lato backend (HTTP 423 LEGACY_MUTATION_LOCKED_BY_POSTQA_D).
 *
 * Questo helper NON apre i gate. Serve solo a:
 *   - evitare round-trip HTTP inutili su azioni che il backend rifiutera';
 *   - mostrare all'utente un messaggio coerente ("Funzione bloccata");
 *   - segnalare al validator frontend l'avvenuto inserimento del blocker.
 *
 * Regole rispettate:
 *   - nessuna abilitazione di default;
 *   - nessuna scrittura DB / reward / progress dal frontend;
 *   - nessuna ridisegnazione UI: si limita a bloccare l'azione.
 */

export const POSTQA_D_PUBLIC_SYNC_TAG =
  'PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS';

export const POSTQA_D_LOCK_CODE = 'LEGACY_MUTATION_LOCKED_BY_POSTQA_D';

export const POSTQA_D_LOCKED_ENDPOINTS: ReadonlyArray<string> = [
  '/api/hero/gain-exp',
  '/api/hero/levelup',
  '/api/fusion/star-up',
  '/api/soul/forge',
  '/api/vip/add-spend',
  '/api/battlepass/buy-premium',
  '/api/friends/gift',
  '/api/gvg/end-war',
  '/api/equipment/equip',
] as const;

export function isLegacyMutationLocked(endpoint: string): boolean {
  if (!endpoint) return false;
  // Match esatto oppure prefix per gli endpoint con path param (es. /api/friends/gift/{id}).
  return POSTQA_D_LOCKED_ENDPOINTS.some(
    (e) => endpoint === e || endpoint.startsWith(e + '/'),
  );
}

export const POSTQA_D_LOCK_MESSAGE_TITLE = 'Funzione bloccata (v108_POSTQA_D)';
export const POSTQA_D_LOCK_MESSAGE_BODY =
  'Questo endpoint legacy e\u0301 bloccato di default dal pack v108_POSTQA_D ' +
  'in attesa dell\u0027attivazione authoritative. Nessuna scrittura DB, ' +
  'nessuna ricompensa, nessuna progressione live. (' +
  POSTQA_D_LOCK_CODE +
  ')';

# 154A — Dual-Read Preview Scope Audit

**Verdict:** `TRACK_A_DUAL_READ_PREVIEW_SCOPE_AUDIT_READY` · audit-only

## Cosa può essere letto in sicurezza oggi
- `users.server` legacy via `GET /api/user/profile` (già player-visible, read-only)
- `/api/servers` list (read-only) — ma la UI NON deve fetch-arlo (audit `audit_server_selection_runtime_safety_v1`)
- `/api/server-profiles/select GET` — 503 envelope, no data leak

## Posso mostrare users.server nella locked preview?
**Sì** — riusando `/api/user/profile` esistente. Nessun nuovo endpoint richiesto per il display.

## server_profiles count=0 blocca?
- Live preview: **Sì**
- Dual-read preview (questo pack): **No** — il dual-read è design + UI copy + gap matrix

## Endpoint helper futuro
- Nome: `GET /api/account/server-profiles/preview`
- Semantica: ritorna current legacy server + future profile readiness
- 503 se flag off
- Mai mutazioni
- Introdotto da `PROJECT_SERVER_PROFILES_AUTH_AND_CONTRACT_HARDENING_PACK`

## Perché la mutation rimane bloccata
- nuovo POST senza auth
- nessun capacity/maintenance enforcement
- nessun seed `server_profiles`
- nessuna strategia dual-write
- rischio orphan-user se flag flip prima del seed

## Smallest safe next step
Design draft + UI copy polish SENZA nuovo endpoint o fetch.

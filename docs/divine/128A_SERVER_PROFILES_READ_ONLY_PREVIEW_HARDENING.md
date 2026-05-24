# 128A — Server Profiles Read-Only Preview Hardening (Track A)

**Verdict:** `TRACK_A_SERVER_PROFILES_READ_ONLY_PREVIEW_HARDENED_INERT`

## Scope
Irrobustire la copertura del comportamento di anteprima read-only senza
attivarlo runtime. Default rimane 503 su GET/POST `/api/server-profiles/select`
con flag spenti.

## Cose verificate
- Doppio gate `SERVER_PROFILES_RUNTIME_ENABLED` AND `SERVER_PROFILES_PREVIEW_ENABLED`.
- Helper `_preview_dry_run_envelope` NON chiamato dai default handler.
- `mutation_executed`, `active_server_switched`, `dual_write_executed`,
  `second_server_opened` sempre `False` nell'envelope.
- Nessuna keyword di DB write nei default handler (`insert_one`, `update_one`,
  `replace_one`, `delete_one`, `find_one_and_update`).
- Runtime probe (best-effort): `GET` e `POST /api/server-profiles/select` ⇒ 503
  con flag OFF.

## Vincoli rispettati
- NO live enable, NO active switch, NO DB writes, NO second server, NO frontend.

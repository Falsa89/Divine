# 131_A — Server Profiles Preview Canary Flag Flip (Track A)

**Verdict:** `TRACK_A_SERVER_PROFILES_PREVIEW_CANARY_ENABLED_SAFE`

## Approval markers rilevati
- `TRACK_A_SERVER_PROFILES_PREVIEW_CANARY_APPROVAL=true` ✅
- `SERVER_PROFILES_PREVIEW_CANARY_OK=true` ✅

## Scope del flip
- Canary env only (NON local dev backend, NON production).
- Local backend rimane 503 sia su GET sia su POST.
- Application reale al canary env = PENDING_OPS_OPERATOR_NETWORK_LEVEL.

## Verifica del code-path
Il validator importa `routes/server_profiles.py` in-process, imposta
temporaneamente `SERVER_PROFILES_RUNTIME_ENABLED=true` +
`SERVER_PROFILES_PREVIEW_ENABLED=true` in `os.environ`, invoca
`_runtime_enabled()`, `_preview_runtime_enabled()`, `_preview_dry_run_envelope()`,
verifica che `mutation_executed`, `active_server_switched`,
`dual_write_executed`, `second_server_opened` siano TUTTI `False`, e ripristina
l'environment.

## Rollback
Unsetting `SERVER_PROFILES_RUNTIME_ENABLED` in canary riporta a 503 default.

## Vincoli rispettati
- NO active switch, NO DB writes, NO second server, NO dual-write, NO frontend.

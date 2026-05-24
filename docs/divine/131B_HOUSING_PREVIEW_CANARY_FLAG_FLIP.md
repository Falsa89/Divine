# 131B — Housing Preview Canary Flag Flip (Track B)

**Verdict:** `TRACK_B_HOUSING_PREVIEW_CANARY_ENABLED_SAFE`

## Approval markers rilevati
- `TRACK_B_HOUSING_PREVIEW_CANARY_APPROVAL=true` ✅
- `HOUSING_PREVIEW_CANARY_OK=true` ✅

## Scope del flip
- Canary env only; local backend rimane 503.
- Application reale al canary env = PENDING_OPS_OPERATOR.

## Verifica del code-path
Il validator importa `routes/housing_preview.py` in-process, imposta
`HOUSING_PREVIEW_ENABLED=true`, invoca `_flag_enabled()` +
`_read_only_envelope(None)` e verifica:
- `preview=True`, `dry_run=True`
- `live_bonus_applied=False`, `db_writes=False`, `combat_mutation=False`
- `rooms=[]`, envelope bonus tutti `0.0` (zero-bonus inert).

## Rollback
Unsetting `HOUSING_PREVIEW_ENABLED` in canary riporta a 503 default.

## Vincoli rispettati
- NO Housing live bonus, NO DB writes, NO battle/account stat mutation,
  NO frontend.

# 132F — Status Rollback & Kill-Switch Plan

**Verdict:** `TRACK_F_STATUS_ROLLBACK_KILL_SWITCH_PLAN_READY`

## Kill-switch flag
`STATUS_RUNTIME_BUFF_SLICE_ENABLED` — unset/false = disarmed.

## Rollback steps (target < 60s)
R1. set `STATUS_RUNTIME_BUFF_SLICE_ENABLED=false` (o unset) in canary env.
R2. graceful restart backend in canary.
R3. verifica `resolver.is_runtime_active() == False`.
R4. verifica payload battle non contiene `status_envelope_preview`.
R5. esegui QA safe smoke extension (Track G) per confermare zero leakage.
R6. archivia incident report con timestamp.

## Verifica in-process
Il validator F effettua toggle os.environ true→false→unset e asserisce
`is_runtime_active()` flippa coerentemente.

## Vincoli rispettati
- NO DB writes, NO runtime activation.

# 439 — Menu Public Exposure Approval Handshake (v73)

Pack: `MEGA_RELEASE_ACCELERATION_22_v73`
Tag: `PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA`

## Obiettivo

Definire l'handshake esplicito (approval phrase + checksum + dry-run pass) necessario prima di qualsiasi futura abilitazione del menu pubblico per le preview alpha.

## Stato v73

- `manual_approval_required = true`
- `manual_approval_received = false`
- `approval_phrase_required = true`
- `checksum_required = true`
- `public_menu_exposure_apply_default = false`
- `public_menu_exposure_enabled = false`
- `production_navigation_changed = false`
- `db_writes = 0`

## Step handshake

1. qa_exit_pass (da `alpha_internal_qa_exit_criteria_v1`)
2. scope_lock_present (da `menu_public_exposure_scope_lock_v1`)
3. approval_phrase_received (da user prompt o env)
4. checksum_verified (sha256 dello scope lock)
5. dry_run_pass (da `menu_public_exposure_dry_run_result_v1`)
6. explicit_apply_instruction (da user prompt)

Se anche solo uno step fallisce -> `BLOCKED_NOT_APPLIED_SAFE`.

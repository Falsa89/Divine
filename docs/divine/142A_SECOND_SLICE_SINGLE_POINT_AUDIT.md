# 142A — PROJECT_T Track A: Second-Slice Single-Point Audit

## Verdict
`TRACK_A_SECOND_SLICE_SINGLE_POINT_AUDIT_READY`

## Classification
**`SECOND_SLICE_SINGLE_POINT_SAFE_NOW_FLAGGED`**

## Marker JSON
`/app/data/design/status_effects/project_t_second_slice_single_point_audit_v1.json`

## Validator
`/app/backend/scripts/validate_project_t_second_slice_single_point_audit_v1.py` → **[PASS]**

## Insertion point identificato
- File: `/app/backend/battle_engine.py`
- Import block: righe 25-31 (adiacente all'import del seam Project M).
- Call site: dentro `simulate_battle()`, riga 407-408 (subito dopo il chiamato Project M).
- Pattern: due call adiacenti identiche al pattern Project M (`team_a = _project_t_second_slice_seam(team_a)`, idem per `team_b`).

## Rationale
Il seam first-slice (Project M) già fornisce un single-point inserimento safe via identità; il seam second-slice viene cablato accanto come due chiamate identità aggiuntive e un singolo blocco `try/except` per l'import. Con flag OFF, entrambi i seam sono identità stretta, quindi la battle behavior è invariata.

## Hard safety invariants (10)
- flag OFF default
- identity / no-op fallback su fallimento import
- no DoT / tick loop
- no hard CC
- no Borea Marchio live
- no damage/heal formula change
- no battle round loop change
- no `battle_core.py` mutation
- no `combat.tsx` mutation
- no `.env` flag enable

## Side effects
Nessuno. Track A è read-only.

# 142C — PROJECT_T Track C: Flag-OFF Runtime-Byte-Identical Guard

## Verdict
`TRACK_C_SECOND_SLICE_FLAG_OFF_BYTE_IDENTICAL_GUARD_READY`

## Marker JSON
`/app/data/design/status_effects/project_t_second_slice_flag_off_regression_v1.json`

## Validator
`/app/backend/scripts/validate_project_t_second_slice_flag_off_regression_v1.py` → **[PASS]**

## Comparison mode
**Deterministic-input identity comparison on the seam call site.**

Il file md5 di `battle_engine.py` necessariamente cambia (file ha +24 righe). Tuttavia il **runtime behavior** con flag OFF rimane byte-identico al pre-pack, perché:
- `is_seam_active()` ritorna `False` con flag unset.
- `apply_prefight_second_slice_preview(team_payload)` esegue `return team_payload` (strict identity).
- Le 2 call site in `simulate_battle()` sono quindi due NO-OP identità stretta.

## Validator subprocess test
Subprocess isolato, env var rimossa esplicitamente, esegue il pattern esatto delle 2 chiamate seam (first-slice + second-slice) su `team_a` e `team_b`:
- `team_a is orig_a` → **True** ✅
- `team_b is orig_b` → **True** ✅
- Output: `IDENTITY_OK`

## Backup verification
- Backup file MD5: `d04feb03e1388db8557d17bd42d5b4d1` (byte-identico al pre-pack dichiarato).

## Normalization
Non usata. Verifica diretta tramite `id()`.

## Side effects
Nessuno. DB writes: 0.

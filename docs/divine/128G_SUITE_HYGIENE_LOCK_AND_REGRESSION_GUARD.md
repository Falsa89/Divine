# 128G — Suite Hygiene Lock & Regression Guard (Track G)

**Verdict:** `TRACK_G_SUITE_HYGIENE_LOCK_READY`

## Garantito
- Baseline post-Project_E: `406 PASS / 0 FAIL / 0 MISS`.
- Il cluster v1 SLC resta segregato dietro `SUPERSEDED_AFTER_PROJECT_E_V2`.
- I REQUIRED restano invariati.
- 8 entry `PROJECT-E-TRACK-*` e 8 entry `PROJECT-F-TRACK-*` registrate in OPTIONAL.
- Nessun fake PASS, nessun hiding di fallimenti.

## Validator
`validate_project_f_suite_hygiene_lock_v1.py` esegue check strutturali (no
ri-esecuzione ricorsiva) sulla suite runner e sul marker hygiene.

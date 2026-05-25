# 157D — Feature/Mode Crosswalk & Duplication Audit (Track D)

Verdetto: `TRACK_D_FEATURE_MODE_CROSSWALK_AND_DUPLICATION_AUDIT_READY`
File: `data/design/audit/full_repo/feature_mode_crosswalk_v1.json`

## Coverage
- 49 feature mappate con cross-link FE routes / FE callsites / BE endpoints
- Duplicazioni rilevate: ~4 (es. `shop` + `item-shop` + `economy`, `artifact` + `artifacts-preview`, `hero` + `heroes` + `hero-collection`)

## Uso
La crosswalk è la fonte di verità per individuare:
- backend orfani (endpoint senza FE caller)
- frontend orfani (route senza BE endpoint)
- duplicazioni di sistema

# 207H — SMOKE AND QA

**Track**: H | **Verdict**: `TRACK_H_SMOKE_AND_QA_READY`

## Smoke tests

| Test | Method | Path | Atteso |
|---|---|---|---|
| flag-off default | GET | `/api/gear-forge/config` | HTTP 503 `disabled` |
| flag-on config | GET | `/api/gear-forge/config` | HTTP 200, `subsystems[4]`, `staged_caps[4]` |
| fusion preview ok | POST | `/api/gear-forge/fusion/preview` | HTTP 200, `preview_ok` |
| fusion insufficient fodder | POST | `/api/gear-forge/fusion/preview` | HTTP 200, `insufficient_fodder` |
| enhance preview ok | POST | `/api/gear-forge/enhance/preview` | HTTP 200, `preview_ok` |
| enhance target above cap | POST | `/api/gear-forge/enhance/preview` | HTTP 200, `target_above_cap` |
| reforge preview | POST | `/api/gear-forge/reforge/preview` | HTTP 200, `preview_design_only` |
| enchant preview | POST | `/api/gear-forge/enchant/preview` | HTTP 200, `preview_design_only` |

## Osservazioni QA

- Tutti gli endpoint read-only/preview-only. Zero scrittura DB possibile.
- Enhance/preview rispetta cap canonico +50 e blocca target > 50.
- Fusion/preview valida solo schema: min 3 fodder, base != fodder. **ZERO** ownership lookup.
- Reforge ed Enchant ritornano envelope deterministicamente design-only.

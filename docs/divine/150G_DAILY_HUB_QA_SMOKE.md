# 150G — DAILY HUB FRONTEND QA SMOKE

## Track G — `PROJECT_FRONTEND_C_TRACK_G`

**Verdict:** `TRACK_G_DAILY_HUB_FRONTEND_QA_SMOKE_READY`

## Static smoke

| Check | Risultato |
|---|---|
| Route compile (Metro bundle 2589 modules clean) | PASS |
| `router.push` target esistenti | 5/5 ✅ (`/mail`, `/events`, `/achievements`, `/battlepass`, `/shop`) |
| Forbidden labels scan (Riscatta tutto / Claim all / Reclama / Apri tutto) | PASS (0 match) |
| Mutating API calls scan | PASS (0 match) |
| `fetch(` presence | 0 |
| Only navigation actions | ✅ |

## Manual QA checklist (8 step)

1. Apri Menu → Altro → Guida Giornaliera
2. Verifica hub si apre senza crash
3. Tap Posta → navigazione a /mail
4. Back → hub
5. Tap Eventi Giornalieri → navigazione a /events
6. Tap Achievement, Battle Pass, Negozio → navigazione corretta
7. Conferma assenza pulsanti claim/riscatta diretti nell'hub
8. Verifica safe area corretta su 390x844 e 360x800

## `fake_screenshot_verification = false`

## Validator

`validate_project_frontend_c_daily_hub_frontend_qa_smoke_v1.py` → **PASS**.

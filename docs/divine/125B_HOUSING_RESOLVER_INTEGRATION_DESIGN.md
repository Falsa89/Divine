# 125B — PROJECT_C Track B — HOUSING_MVP_RESOLVER_STUB_INTEGRATION_DESIGN

**Verdict**: 🟢 `TRACK_B_HOUSING_RESOLVER_INTEGRATION_DESIGN_READY`  
**Mode**: design doc only, no runtime import

## 5-Phase integration plan

| # | Phase | Status |
|---|---|---|
| 1 | INTEGRATION_POINT_DESIGN | ✅ DONE V_C |
| 2 | NON_RUNTIME_UNIT_TEST_PACK | PLANNED |
| 3 | INERT_RUNTIME_IMPORT_AUDIT_PACK | PLANNED |
| 4 | FEATURE_FLAG_GATED_LIVE_IMPORT_PACK | PLANNED |
| 5 | LIVE_BONUS_APPLICATION_PACK | 🚫 FORBIDDEN OUT_OF_SCOPE PROJECT_C |

## Canonical call site (design only)
`GET /api/user/me` extended (additive optional) with key `housing_bonus: {hp_pct:0, atk_pct:0, def_pct:0, healing_pct:0, source:resolver_stub_inert}`. **Non-runtime until Phase 4**.

## Forbidden scope rispettato
resolver imported by runtime ❌, live bonus application ❌, frontend ❌, DB writes ❌.

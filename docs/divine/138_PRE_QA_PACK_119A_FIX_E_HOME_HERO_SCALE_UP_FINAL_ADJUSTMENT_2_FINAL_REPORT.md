# 138 — Pre-QA Pack 119A-FIX-E — Home Hero Scale-Up Final Adjustment 2 — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_FIX_E_HOME_HERO_SCALE_UP_FINAL_ADJUSTMENT_2`
**Data:** 2026-06-15 (UTC)

## Verdict
# ✅ `PRE_QA_PACK_119A_FIX_E_HOME_HERO_SCALE_UP_FINAL_ADJUSTMENT_2_READY_FOR_DEVICE_RETEST`

## Files Modified
- `frontend/app/(tabs)/home.tsx` (2 valori in 2 punti)
- `docs/divine/138_*_FINAL_REPORT.md` (NEW)

## Valori prima/dopo

| Parametro | 119A-FIX-D | **119A-FIX-E** | Δ |
|-----------|------------|-----------------|---|
| Hero width | `min(W*0.61, 470)` | **`min(W*0.67, 520)`** | **+9.8%** |
| Hero height | `min(H*0.88, 660)` | **`min(H*0.96, 720)`** | **+9.1%** |
| translateY | `76` | **`88`** | **+12px** |

## Background top -56 INVARIATO ✅
```
$ grep -n "top: -56" frontend/app/(tabs)/home.tsx
627: top: -56,        // pack 119A-FIX-A: floor lift cross-background
```

## Fix funzionali 119A intatti
Avatar tap Alert · BAG → `/inventory` · FORGE → `/equipment` · SKILL Alert · TEAM `/(tabs)/battle` · Nickname tap Alert · Title tap Alert · heroLayer anchor flex-end + paddingBottom 0 · HomeBackground top -56 → **tutti invariati**.

## Validator suite
**24/24 PASS** · 0 FAIL · 0 SKIPPED · backend_up=True
File: `backend/reports/pre_qa_safety_validator_suite_20260615T212432Z.json`

## Repo hygiene
`sweep_repo_hygiene.py` → clean=true · 0 bytecode tracciato

## Commit SHAs
- Baseline: `d9b96516b` (119A-FIX-D)
- Pack commit: `e3c3297d4a4786f75fc5f8c2903cb976e028a71e` — 2 file (1 MOD home.tsx + 1 NEW report).

🛑 Stop. Pack 119A-FIX-E applicato. Attendo device retest.

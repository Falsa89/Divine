# 137 — Pre-QA Pack 119A-FIX-D — Home Hero Scale-Up Final Adjustment — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_FIX_D_HOME_HERO_SCALE_UP_FINAL_ADJUSTMENT`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_PACK_119A_FIX_D_HOME_HERO_SCALE_UP_FINAL_ADJUSTMENT_READY_FOR_DEVICE_RETEST`

---

## 2. Files Modified

| File | Tipo |
|------|------|
| `frontend/app/(tabs)/home.tsx` | **MODIFIED** (2 micro-modifiche: hero size + translateY) |
| `docs/divine/137_*_FINAL_REPORT.md` | **NEW** |

---

## 3. Valori prima/dopo

| Parametro | 119A-FIX-C | **119A-FIX-D** | Δ |
|-----------|------------|-----------------|---|
| Hero width | `min(W*0.55, 420)` | **`min(W*0.61, 470)`** | **+10.9%** (fattore W +0.06) |
| Hero height | `min(H*0.88, 600)` * | **`min(H*0.88, 660)`** | **+10.0%** (fattore H +0.08) |
| translateY | `64` | **`76`** | **+12px** |

\* Nota: 119A-FIX-C era `min(H*0.80, 600)`.

### Conferma background top -56 INVARIATO ✅
```
$ grep -n "top: -56" frontend/app/(tabs)/home.tsx
627: top: -56,        // pack 119A-FIX-A: floor lift cross-background
```
Linea inalterata dal Pack 119A-FIX-A.

---

## 4. Acceptance criteria

| # | Criterio | Esito |
|---|----------|-------|
| 1 | Hero visibilmente più grande del FIX-C | ✅ +10.9% width, +10.0% height |
| 2 | Hero ancora grounded, non fluttuante | ✅ `translateY: 76` + `flex-end` + background lift -56 |
| 3 | Lower legs/feet restano parzialmente occlusi | ✅ translateY +12px compensa altezza aggiuntiva |
| 4 | Pavimento/prospettiva corretti | ✅ background top -56 invariato |
| 5 | Zero regressioni fix funzionali 119A | ✅ verificato statico (solo 2 valori in 2 punti del file) |
| 6 | Validator suite invariata PASS | ✅ 24/24 PASS |
| 7 | Repo hygiene pulita | ✅ clean=true, 0 bytecode tracciato |

---

## 5. Conferma fix funzionali 119A intatti

| Fix 119A | Stato 119A-FIX-D |
|----------|------------------|
| Avatar tap (Alert locked, no crash) | **invariato** |
| BAG → `/inventory` | **invariato** |
| FORGE → `/equipment` | **invariato** |
| SKILL → Alert locked | **invariato** |
| TEAM → `/(tabs)/battle` | **invariato** |
| Nickname tap → Alert locked | **invariato** |
| Title tap → Alert locked (no `/achievements`) | **invariato** |
| HomeBackground `top: -56` floor lift | **invariato** |
| heroLayer anchor `flex-end` + `paddingBottom: 0` | **invariato** |

---

## 6. Smoke / validator

### Validator suite pre-QA safety
```
totali:  24
PASS:    24
FAIL:    0
SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260615T205157Z.json`

### Repo hygiene
```
sweep_repo_hygiene.py → clean=true
git ls-files | grep -E '\.pyc$|\.pyo$|__pycache__' → vuoto
```

---

## 7. Cosa NON è stato toccato

Background top -56 · floor lift · grounding logic (flex-end / paddingBottom 0) · BAG/FORGE/SKILL/TEAM routing · avatar fix · Player/title behavior · BP formula · tutorial · onboarding · starter claim · DB · gacha · shop · reward · battle · Character Bible · overlay redesign · pulsanti destra · header redesign.

---

## 8. Commit SHAs

- **Baseline pre-119A-FIX-D:** `304eada75` (Pack 119A-FIX-C)
- **Pack commit 119A-FIX-D:** `d9b96516bcd908ec6033e3469b2780abc87ad26b` — 2 file (1 MOD home.tsx + 1 NEW report).

---

## 9. Stop Condition

🛑 **Stop. Pack 119A-FIX-D applicato. Attendo device retest del Game Master.**

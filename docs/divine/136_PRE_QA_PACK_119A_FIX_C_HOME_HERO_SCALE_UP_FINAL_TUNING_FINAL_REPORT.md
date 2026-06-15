# 136 — Pre-QA Pack 119A-FIX-C — Home Hero Scale-Up Final Tuning — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_FIX_C_HOME_HERO_SCALE_UP_FINAL_TUNING`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_PACK_119A_FIX_C_HOME_HERO_SCALE_UP_FINAL_TUNING_READY_FOR_DEVICE_RETEST`

---

## 2. Scope

Pack 119A-FIX-C esegue lo scale-up finale dell'eroe Home, tornando vicino
alla scala originale (119A) ora che floor lift + grounding anchor esistono.
**NON** modifica nient'altro: background top -56 e grounding logic restano
invariati. Nessun fix funzionale 119A regredisce.

Applicato il **target forte** suggerito (non il fallback minimo).

---

## 3. Files Modified

| File | Tipo |
|------|------|
| `frontend/app/(tabs)/home.tsx` | **MODIFIED** (2 micro-modifiche: hero size + translateY) |
| `docs/divine/136_*_FINAL_REPORT.md` | **NEW** |

---

## 4. Valori prima/dopo

### 4.1 Hero size — scale-up finale (target forte)

| Parametro | 119A originale | 119A-FIX-A | 119A-FIX-B | **119A-FIX-C** |
|-----------|----------------|------------|------------|-----------------|
| Width | `min(W*0.55, 420)` | `min(W*0.42, 320)` | `min(W*0.49, 370)` | **`min(W*0.55, 420)`** |
| Height | `min(H*0.80, 600)` | `min(H*0.62, 460)` | `min(H*0.72, 540)` | **`min(H*0.80, 600)`** |

Δ rispetto a FIX-B:
- Width +0.06 fattore W (+50px max cap, **+12.2%**)
- Height +0.08 fattore H (+60px max cap, **+11.1%**)

Δ rispetto a 119A originale:
- **Identico** in width/height → torniamo alla presenza originale piena.

### 4.2 translateY scale-up compensation

| Parametro `s.heroLayer.transform` | 119A-FIX-A | 119A-FIX-B | **119A-FIX-C** |
|-----------------------------------|------------|------------|-----------------|
| `translateY` | `48` | `52` | **`64`** |

`+12px` rispetto a FIX-B per compensare il pieno ritorno alla scala 119A
(altezza +60px max) e mantenere l'occlusione lower-body sotto la
HomeBottomNav. La logica resta: splash box spinta sotto la baseline visibile
→ ginocchia/sotto-ginocchia/feet occlusi dall'overlay nav.

### 4.3 Conferma background top -56 INVARIATO

Verificato via `grep "top: -56"` su `home.tsx`:
```
627: top: -56,        // pack 119A-FIX-A: floor lift cross-background
```
Linea inalterata dal Pack 119A-FIX-A. Floor lift cross-background preservato
in tutte le scene risolte (faction/time-phase/fallback).

---

## 5. Acceptance criteria — Mapping ai fix

| # | Criterio | Verifica |
|---|----------|----------|
| 1 | Hero molto più grande del FIX-B | ✅ width +12.2%, height +11.1% rispetto a FIX-B |
| 2 | Hero con presenza centrale forte | ✅ scala identica all'originale 119A (W*0.55 / H*0.80) |
| 3 | Hero non torna fluttuante | ✅ `translateY: 64` (vs 119A originale che non aveva translateY) → splash box sotto baseline, anchor flex-end + paddingBottom 0 |
| 4 | Gambe basse/feet restano occlusi | ✅ translateY +64 spinge la fascia inferiore sotto HomeBottomNav (zIndex superiore, ~120px alto) |
| 5 | Pavimento resta alto e coerente | ✅ background top `-56` invariato (floor lift preservato) |
| 6 | Background top -56 invariato | ✅ verificato statico (riga 627 di home.tsx) |
| 7 | Zero regressione fix funzionali 119A | ✅ tutte le altre modifiche del file non toccate |

---

## 6. Screenshot evidence

URL preview pubblica: `https://game-portal-327.preview.emergentagent.com/(tabs)/home`

File: `/tmp/119a_fix_c_home.png` (430×932 mobile portrait).

Stato visivo:
- ✅ Background floor lift preservato (castello/piazza posizionati in alto, pavimento ampio fino al bottom).
- ✅ UI completa intatta: HomeProfilePanel (P avatar · "Player" · POWER "Server richiesto" · "❖ Apprendista"), sidebar destra (WHEEL/QUEST/EVENT + ARENA/BLESSING/TRIAL/BATTLE/RESEARCH), HomeBottomNav (CHAT · BAG · ARTIFACT · SKILL · TEAM · GUILD · SHOP · FORGE · MENU), Hoplite SUMMON ›, SP OFFER, CHAT GLOBALE panel.
- ✅ Server time 20:42:54 UTC NIGHT background visibile.

Hero non visibile sul preview pubblico anonimo (`homeHero=null` → splash transparent). **Verifica visiva dell'hero alla nuova scala richiede device retest con account loggato.**

---

## 7. Conferma fix funzionali 119A intatti

| Fix 119A | Stato 119A-FIX-C |
|----------|------------------|
| Avatar tap (Alert locked, no crash) | **invariato** |
| BAG → `/inventory` | **invariato** |
| FORGE → `/equipment` | **invariato** |
| SKILL → Alert locked | **invariato** |
| TEAM → `/(tabs)/battle` | **invariato** |
| Nickname tap → Alert locked | **invariato** |
| Title tap → Alert locked (no `/achievements`) | **invariato** |

Diff effettivo Pack 119A-FIX-C su `home.tsx`:
- Linee 478-479 (HomeHeroSplash props width/height)
- Linea ~2193 (`s.heroLayer.transform.translateY`)

Nessun'altra modifica.

---

## 8. Smoke / validator

### 8.1 Validator suite pre-QA safety
```
totali:  24
PASS:    24
FAIL:    0
SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260615T204235Z.json`

### 8.2 Repo hygiene
```
sweep_repo_hygiene.py → clean=true
git ls-files | grep -E '\.pyc$|\.pyo$|__pycache__' → vuoto
```

---

## 9. Cosa NON è stato toccato

Background top -56 · floor lift · BAG/FORGE/SKILL/TEAM · avatar fix · Player/title behavior · BP formula · tutorial · onboarding · starter claim · DB · gacha · shop · reward · battle · Character Bible · overlay redesign · pulsanti destra · header redesign.

---

## 10. Commit SHAs

- **Baseline pre-119A-FIX-C:** `2411b6642` (Pack 119A-FIX-B)
- **Pack commit 119A-FIX-C:** (riempire dopo commit)

---

## 11. Stop Condition

🛑 **Stop. Pack 119A-FIX-C applicato (target forte). Attendo device retest del Game Master.**

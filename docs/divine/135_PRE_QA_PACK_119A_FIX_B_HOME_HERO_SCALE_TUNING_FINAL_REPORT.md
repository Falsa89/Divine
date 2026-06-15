# 135 — Pre-QA Pack 119A-FIX-B — Home Hero Scale Tuning — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_FIX_B_HOME_HERO_SCALE_TUNING`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_PACK_119A_FIX_B_HOME_HERO_SCALE_TUNING_READY_FOR_DEVICE_RETEST`

---

## 2. Scope

Pack 119A-FIX-B interviene **esclusivamente** sulla scala dell'eroe Home (dopo
device retest 119A-FIX-A = PARTIAL_PASS con feedback "hero troppo piccolo").
**NON** modifica nient'altro: background floor lift, grounding anchor logic,
routing, avatar fix, BP formula, ecc. restano invariati.

---

## 3. Files Modified

| File | Tipo |
|------|------|
| `frontend/app/(tabs)/home.tsx` | **MODIFIED** (2 micro-modifiche: hero size + micro translateY) |
| `docs/divine/135_*_FINAL_REPORT.md` | **NEW** (questo report) |

---

## 4. Valori prima/dopo

### 4.1 Hero size (scala intermedia tra 119A e 119A-FIX-A)

| Parametro | 119A (troppo grande) | 119A-FIX-A (troppo piccolo) | **119A-FIX-B (target)** |
|-----------|----------------------|-----------------------------|-------------------------|
| Width | `min(W * 0.55, 420)` | `min(W * 0.42, 320)` | **`min(W * 0.49, 370)`** |
| Height | `min(H * 0.80, 600)` | `min(H * 0.62, 460)` | **`min(H * 0.72, 540)`** |

Valore intermedio scelto dal suggerimento del Game Master. Δ rispetto a FIX-A:
- Width +0.07 fattore W (+50px max cap, +16.7%)
- Height +0.10 fattore H (+80px max cap, +17.4%)

Δ rispetto a 119A originale:
- Width -0.06 fattore W (-50px max cap, -11%)
- Height -0.08 fattore H (-60px max cap, -10%)

### 4.2 translateY micro-bump (mantenere occlusione)

| Parametro `s.heroLayer.transform` | 119A-FIX-A | **119A-FIX-B** |
|-----------------------------------|------------|----------------|
| `translateY` | `48` | **`52`** |

Bump di +4px per compensare l'aumento di altezza del personaggio
(+80px max) e mantenere la stessa occlusione lower-body sotto la
HomeBottomNav.

### 4.3 Conferma background top -56 INVARIATO

Verificato via `grep "top: -56"` su `home.tsx`:
```
627: top: -56,        // pack 119A-FIX-A: floor lift cross-background
```
Linea inalterata da Pack 119A-FIX-A. Il background floor lift continua a
sollevare la piazza/pavimento di 56px in tutte le scene risolte
(faction/time-phase/fallback).

---

## 5. Acceptance criteria — Mapping ai fix

| # | Criterio | Verifica |
|---|----------|----------|
| 1 | Eroe visibilmente più grande del FIX-A | ✅ width +16.7%, height +17.4% |
| 2 | Eroe non torna gigante come prima | ✅ width -11%, height -10% rispetto a 119A |
| 3 | Eroe resta ancorato al pavimento | ✅ `translateY: 52` (mantiene anchor a flex-end con leggero overshoot) |
| 4 | Lower legs/feet restano parzialmente occlusi | ✅ translateY +4px compensa l'aumento di +80px height (occlusione preserved) |
| 5 | Piazza/pavimento resta percepita alta | ✅ background top `-56` invariato |
| 6 | Nessuna regressione fix funzionali 119A | ✅ tutti gli altri elementi del file non toccati |

---

## 6. Screenshot evidence

URL preview pubblica: `https://game-portal-327.preview.emergentagent.com/(tabs)/home`

Mobile portrait 430×932 → file `/tmp/119a_fix_b_home.png`.

Stato visivo (utente non loggato → `homeHero=null` → splash transparent):
- ✅ Background floor lift preservato (castello + piazza posizionati in alto,
  pavimento visibile fino al bottom dello schermo).
- ✅ HomeBottomNav intatta: CHAT · BAG · ARTIFACT · SKILL · TEAM · GUILD · SHOP · FORGE · MENU.
- ✅ HomeProfilePanel intatta: P avatar circle · "Player" · POWER "Server richiesto" · "❖ Apprendista".
- ✅ Sidebar destra intatta: WHEEL/QUEST/EVENT + ARENA/BLESSING/TRIAL/BATTLE/RESEARCH.

Verifica visiva DIRETTA dell'hero con la nuova scala richiede device retest
con account loggato (idem 119A e 119A-FIX-A — la preview anonima non popola
`homeHero` quindi la splash resta vuota).

---

## 7. Conferma: fix funzionali 119A intatti

Verificati statico via diff:

| Fix 119A | Stato 119A-FIX-B |
|----------|------------------|
| Avatar tap (Alert locked, no crash) | **invariato** |
| BAG → `/inventory` | **invariato** |
| FORGE → `/equipment` | **invariato** |
| SKILL → Alert locked | **invariato** |
| TEAM → `/(tabs)/battle` | **invariato** |
| Nickname tap → Alert locked | **invariato** |
| Title tap → Alert locked (no `/achievements`) | **invariato** |

E fix 119A-FIX-A (grounding):
- Background floor lift `top: -56` → **invariato**
- HeroLayer anchor `flex-end` + `paddingBottom: 0` → **invariato**

L'unica differenza fra 119A-FIX-A e 119A-FIX-B sono i 3 valori:
- `width: 0.42→0.49 / 320→370`
- `height: 0.62→0.72 / 460→540`
- `translateY: 48→52`

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
File: `backend/reports/pre_qa_safety_validator_suite_20260615T203308Z.json`

### 8.2 Repo hygiene
```
sweep_repo_hygiene.py → clean=true
git ls-files | grep -E '\.pyc$|\.pyo$|__pycache__' → vuoto
```

---

## 9. Cosa NON è stato toccato

Background top -56 · BAG/FORGE/SKILL/TEAM · avatar fix · Player/title behavior · BP formula (`battle_power_v1_preqa_derived`) · tutorial · onboarding · starter claim · DB · gacha · shop · reward · battle · Character Bible · overlay redesign · pulsanti destra · header redesign.

---

## 10. Commit SHAs

- **Baseline pre-119A-FIX-B:** `487cb2d14` (Pack 119A-FIX-A)
- **Pack commit 119A-FIX-B:** `2411b66422db8e9297c1603c8c8eeb8eb83c0164` — 2 file (1 MOD home.tsx + 1 NEW report).

---

## 11. Stop Condition

🛑 **Stop. Pack 119A-FIX-B applicato. Attendo device retest del Game Master.**

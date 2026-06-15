# 134 — Pre-QA Pack 119A-FIX-A — Home Hero Grounding Perspective Repair — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_FIX_A_HOME_HERO_GROUNDING_PERSPECTIVE_REPAIR`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_PACK_119A_FIX_A_HOME_HERO_GROUNDING_PERSPECTIVE_REPAIR_READY_FOR_DEVICE_RETEST`

---

## 2. Scope

Pack 119A-FIX-A interviene **esclusivamente** sul grounding visivo dell'eroe Home
e sul framing del background per migliorare l'integrazione personaggio↔piazza.
**NON** riapre i fix funzionali 119A (avatar/BAG/FORGE/SKILL/TEAM/Player/title)
che il Game Master ha confermato DEVICE_PASS.

---

## 3. Files Modified

| File | Tipo | Note |
|------|------|------|
| `frontend/app/(tabs)/home.tsx` | **MODIFIED** | 3 micro-modifiche mirate (size hero · heroLayer anchor · HomeBackground floor lift) |
| `docs/divine/134_*_FINAL_REPORT.md` | **NEW** | questo report |

Nessun altro file toccato. Nessun asset rigenerato.

---

## 4. Fix dettagli — Valori prima/dopo

### 4.1 Hero scale (riduzione "fuori scala")

| Parametro | PRIMA (119A) | DOPO (119A-FIX-A) |
|-----------|--------------|-------------------|
| Larghezza splash | `Math.min(W * 0.55, 420)` | **`Math.min(W * 0.42, 320)`** |
| Altezza splash | `Math.min(H * 0.80, 600)` | **`Math.min(H * 0.62, 460)`** |

Riduzione effettiva ~24% larghezza e ~23% altezza → hero meno gigante,
percepito come presente nella piazza piuttosto che dominante sopra il background.

### 4.2 Real anchor con occlusione lower-body

| Parametro `s.heroLayer` | PRIMA (119A) | DOPO (119A-FIX-A) |
|-------------------------|--------------|-------------------|
| `top / bottom` | `0 / 0` | `0 / 0` (invariato) |
| `justifyContent` | `flex-end` | `flex-end` (invariato) |
| `paddingBottom` | `28` | **`0`** |
| `transform` | — | **`[{ translateY: 48 }]`** |

`translateY: +48` spinge la splash box **sotto la baseline visibile** dello
schermo. La `HomeBottomNav` (zIndex superiore, altezza `BAR_H_VISIBLE` ~120px)
**occlude realmente** la fascia ginocchia/sotto-ginocchia/piedi dell'hero.
L'effetto è "hero entra nella piazza" invece di "hero appiccicato sopra
l'overlay".

Logica `translateY` resta screen-relative (non background-relative) →
identico effetto cross-faction/time-phase/fallback.

### 4.3 Background floor lift cross-background

| Componente `HomeBackground` | PRIMA (119A) | DOPO (119A-FIX-A) |
|-----------------------------|--------------|-------------------|
| Container wrapper | `<View style={absoluteFill}>` | `<View style={[absoluteFill, { overflow: 'hidden' }]}>` |
| Inner background offset | — | inner View con **`top: -56`**, full bleed |
| `ImageBackground` resizeMode | `cover` | `cover` (invariato) |

L'intera immagine background ora è spostata **-56px in alto** rispetto al
viewport — il pavimento/piazza viene così percepito **più alto** nel campo
visivo, coerente col personaggio ora grounded. `overflow: 'hidden'` sul
wrapper esterno garantisce che lo shift non sbordi sui top safe-area.

Il fix vale **uniformemente** per:
- night background (corrente test)
- day background (time-phase variant)
- faction backgrounds (resolveHomeBackground via manifest)
- fallback `LinearGradient` (uniche scene senza asset — invariato perché non c'è asset da spostare; il gradient resta full-bleed)

Nessun asset rigenerato.

---

## 5. Screenshot evidence

URL preview pubblica: `https://game-portal-327.preview.emergentagent.com/(tabs)/home`

| Viewport | File | Stato |
|----------|------|-------|
| Mobile portrait (430×932 — iPhone 14 Pro Max) | `/tmp/119a_fix_a_home_mobile.png` | Background floor lift VISIBILE (castello/piazza spostati verso il centro). Hero non visibile (utente non loggato → `homeHero=null` → splash vuota). |
| Desktop landscape (1280×720) | `/tmp/119a_fix_a_home_landscape.png` | Idem: background ribilanciato in alto, restante UI intatta (CHAT/BAG/ARTIFACT/SKILL/TEAM/GUILD/SHOP/FORGE/MENU presenti). |

> **Nota onesta:** preview pubblica testata senza login → `homeHero` non
> popolato → la `HomeHeroSplash` ritorna `<View width height bg=transparent />`
> e l'hero non è visibile sul preview. Le **configurazioni di grounding sono
> tuttavia applicate** (verificabili nel codice + suite validator).
> **Verifica visuale completa richiede device retest con account loggato**
> (atteso `DEVICE_PASS`).

---

## 6. Acceptance criteria — Mapping ai fix

| # | Criterio | Fix applicato | Atteso device |
|---|----------|---------------|---------------|
| 1 | Eroe non sembra più fluttuante | `translateY: +48` + occlusione nav | ✅ feet/lower-legs sotto overlay |
| 2 | Eroe non troppo alto/gigante | Width 0.55→0.42 · Height 0.80→0.62 | ✅ ridotto ~23% |
| 3 | Lower legs/feet realmente occlusi dal bottom overlay | `translateY: +48` spinge box sotto baseline; HomeBottomNav zIndex superiore | ✅ |
| 4 | Piazza/pavimento più coerente con punto di vista hero | Background floor lift `top: -56` | ✅ pavimento più alto |
| 5 | Funziona su night + day/fallback/faction | Logica screen-relative su `HomeBackground` (vale per tutti gli asset risolti) | ✅ |
| 6 | Fix funzionali 119A non regrediti | Modifiche limitate a `heroLayer` style + size props + `HomeBackground` wrapper | ✅ avatar/BAG/FORGE/SKILL/TEAM/Player/title intatti |

---

## 7. Conferma: fix funzionali 119A NON modificati

Verifica statica tramite `git diff` su `home.tsx` e `homeAssetsManifest.ts`:

| Fix 119A | Stato Pack 119A-FIX-A |
|----------|------------------------|
| Avatar tap → Alert locked (no crash) | **invariato** |
| BAG → `/inventory` | **invariato** in `homeAssetsManifest.ts` |
| FORGE → `/equipment` | **invariato** in `homeAssetsManifest.ts` |
| SKILL → Alert locked (HomeBottomNav onPress override) | **invariato** |
| TEAM → `/(tabs)/battle` | **invariato** |
| Nickname tap → Alert locked | **invariato** |
| Title tap → Alert locked (no `/achievements`) | **invariato** |

Pack 119A-FIX-A ha toccato esclusivamente:
- `HomeBackground()` function (wrapper interno + offset `top: -56`)
- `HomeHeroSplash` props `width`/`height` (riduzione scala)
- `s.heroLayer` style (transform translateY)

Nessun'altra modifica al file. Diff disponibile su request.

---

## 8. Smoke / validator eseguiti

### 8.1 Validator suite pre-QA safety
```
totali:  24
PASS:    24
FAIL:    0
SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260615T201931Z.json`

Conferma: BP formula invariata · RD invariata · HU readiness invariata · 116B chat/bot preservato · 118B QA harness preservato · 119A fix funzionali preservati.

### 8.2 Repo hygiene
```
sweep_repo_hygiene.py → clean=true
git ls-files | grep -E '\.pyc$|\.pyo$|__pycache__' → vuoto
```

---

## 9. Cosa NON è stato toccato (fuori scope rispettato)

Avatar fix · BAG routing · FORGE routing · SKILL routing · TEAM · Player/title behavior · BP formula · tutorial · onboarding · starter claim · DB · gacha · shop · reward · battle · Character Bible · overlay redesign · pulsanti destra redesign · header profile redesign.

---

## 10. Commit SHAs

- **Baseline pre-119A-FIX-A:** `02e2cd5d7` (Pack 119A)
- **Pack commit 119A-FIX-A:** (riempire dopo commit)

---

## 11. Stop Condition

🛑 **Stop. Pack 119A-FIX-A applicato. Attendo device retest del Game Master.**

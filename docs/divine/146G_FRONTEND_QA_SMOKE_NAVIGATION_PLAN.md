# 146G — FRONTEND QA SMOKE NAVIGATION PLAN

## Track G — `PROJECT_X_TRACK_G`

**Verdict:** `TRACK_G_FRONTEND_QA_SMOKE_NAVIGATION_PLAN_READY`

## 1. Obiettivo

Definire un piano QA navigation smoke per la futura UI Project Y, **mobile-first**, **senza credenziali**, **dev-only**.

## 2. Aree coperte (8 sezioni, 34 check)

| Sezione | # Check |
|---|---|
| Mobile-first checks (viewport, safe area, touch target...) | 7 |
| Expo Go checks | 4 |
| Route existence checks | 3 |
| Dead button checks | 3 |
| Accidental live action checks | 3 |
| Blocked endpoint crash checks | 3 |
| Empty / error states | 4 |
| Smoke navigation paths | 7 |

## 3. Mobile-first highlights

- iPhone 12/13/14 (390x844)
- Samsung Galaxy S21 (360x800)
- Safe area insets corretti
- Keyboard avoiding view su form
- Min touch target 44x44 iOS / 48x48 Android
- Nessun overflow orizzontale

## 4. Smoke paths critici

```
home → heroes → hero-detail → back
home → battle → combat → back
home → gacha → banner pull → back
menu → storia → capitolo → battle
menu → catalogo skill & status → voce → back
menu → artefatti (read-only locked) → back
menu → servers → lista → back
```

## 5. Blocked endpoint resilience

- `/api/server-profiles/select` (503) → gestito senza crash
- `/api/housing/preview` (503) → gestito senza crash
- Network errors / timeout → stato grazioso

## 6. Future automation

- Tool: `expo_frontend_testing_agent` (Playwright)
- Trigger: **solo dopo Project Y**
- Credenziali richieste: **no**
- Esecuzione: **dev only**

## 7. Validator

`validate_project_x_frontend_qa_smoke_navigation_plan_v1.py` → **PASS**.

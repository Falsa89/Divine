# 148G — EXPO GO MOBILE QA SMOKE

## Track G — `PROJECT_Z_TRACK_G`

**Verdict:** `TRACK_G_MOBILE_SCREENSHOT_MANUAL_PENDING`

## 1. Stato automation

| Voce | Stato |
|---|---|
| Playwright disponibile | ✅ |
| Expo Web render in automazione consistente | ❌ (white screen iniziale, hydration lenta) |
| Bundle Metro compila clean | ✅ (2672 modules, 0 errori) |
| HTTP route check (200) | ✅ (`GET /safe-previews` → 200) |

**Causa render bianco in automazione:** App configurata in `OrientationLock.LANDSCAPE` + wrapper `AuthProvider` + `NotificationProvider` + `GestureHandlerRootView`. L'idratazione iniziale di Expo Web richiede più tempo del timeout di automazione headless.

## 2. Static smoke run (PASS empirico)

| Check | Risultato |
|---|---|
| Route compile | PASS |
| `SafeFeatureCard` importato in tutte le 4 route | PASS |
| Forbidden labels scan | PASS (0 match) |
| Mutating API calls scan | PASS (0 match) |
| GET-only check | PASS |
| 503 handling presente | PASS |

## 3. Manual QA checklist per Expo Go (device reale)

1. Apri Expo Go su iPhone reale (viewport 390x844) e Samsung S21 (360x800)
2. Scansiona QR del dev server
3. Naviga: Home → Menu → sezione **Altro** → **“Sistemi in preparazione”**
4. Verifica hub si apre senza crash
5. Tap su **“Codex Status Effects”** → verifica scrolling + legenda colorata
6. Tap back → hub
7. Tap su **“Anteprima Artefatti”** → verifica 4 raretà + 4 categorie
8. Tap back → hub
9. Tap su **“Dimora Divina”** → verifica stato 503 con copy IT
10. Verifica nessun overflow orizzontale su entrambi i viewport
11. Verifica safe area corretta (notch / status bar)
12. Verifica min touch target 44pt sui pulsanti back
13. Conferma assenza di pulsanti live (Evoca/Importa/Attiva/Spendi/Cambia)

## 4. No fake screenshot verification

**`fake_screenshot_verification = false`**. La verifica visiva su device reale resta marcata `MANUAL_DEVICE_SCREENSHOT_PENDING` per onestà. Può essere riaperta in `PROJECT_Z2_FRONTEND_SAFE_PREVIEW_MOBILE_QA_SCREENSHOT_FIX_PACK` se necessario.

## 5. Validator

`validate_project_z_expo_go_mobile_qa_smoke_v1.py` → **PASS**.

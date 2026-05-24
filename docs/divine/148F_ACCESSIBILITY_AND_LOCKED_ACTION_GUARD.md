# 148F — ACCESSIBILITY & LOCKED ACTION GUARD

## Track F — `PROJECT_Z_TRACK_F`

**Verdict:** `TRACK_F_ACCESSIBILITY_AND_LOCKED_ACTION_GUARD_READY`

## 1. Component audited

`/app/frontend/components/SafeFeatureCard.tsx` — verificato:

- Usa `accessibilityLabel` su ogni card
- Usa `accessibilityState.disabled = true` quando locked
- Locked render → wrap in `View` (non `TouchableOpacity`)
- `onPress` viene **ignorato** quando locked

## 2. Route audited (4)

- `/app/frontend/app/safe-previews.tsx` — entry hub con `accessibilityRole="link"`, `accessibilityHint` e label parlanti
- `/app/frontend/app/artifacts-preview.tsx` — back button con `accessibilityLabel="Indietro"`
- `/app/frontend/app/housing-preview.tsx` — idem
- `/app/frontend/app/status-codex.tsx` — idem

## 3. Forbidden labels enabled scan

| Label | Presente come bottone enabled? |
|---|---|
| “Evoca ora” | ❌ |
| “Importa ora” | ❌ |
| “Attiva bonus” | ❌ |
| “Cambia server” | ❌ |
| “Lancia rollout” | ❌ |

## 4. Screen reader safety

- I locked card annunciano lo stato `disabled` ai lettori di schermo
- Nessuna label suggerisce disponibilità live di feature in attesa

## 5. Validator

`validate_project_z_accessibility_locked_action_guard_v1.py` → **PASS**.

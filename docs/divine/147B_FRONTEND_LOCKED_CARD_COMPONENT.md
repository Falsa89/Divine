# 147B — FRONTEND LOCKED CARD COMPONENT

## Track B — `PROJECT_Y_TRACK_B`

**Verdict:** `TRACK_B_FRONTEND_LOCKED_CARD_COMPONENT_READY`

## 1. Componente creato

```
/app/frontend/components/SafeFeatureCard.tsx
```

## 2. Props supportate (9)

`title`, `subtitle`, `statusBadge`, `visibility`, `lockReason`, `endpointStatus`, `icon`, `onPress`, `testID`.

## 3. Visibility classes supportate

- `player_visible_locked`
- `player_visible_active_read_only`
- `dev_admin_only`
- `hidden_until_approved`

## 4. Comportamento default locked (CRITICO)

- Wrap in `View` (NON `TouchableOpacity`) quando `visibility ∈ {locked, hidden}`
- `onPress` **ignorato** quando locked
- `accessibilityState.disabled = true`
- Stile differenziato: bordo tratteggiato, opacità ridotta, badge giallo warning
- Mostra `lockReason` con icona lucchetto

## 5. Endpoint status supportati

`live` / `preview_503` / `dry_run` / `none` — quando `preview_503`, mostra hint giallo dedicato.

## 6. Live action handler default

❌ **assente di default**. Nessuna funzione mutativa cablata.

## 7. Validator

`validate_project_y_locked_card_component_v1.py` → **PASS**.

# 183A — Stamina Surface Audit

**Track:** A — Stamina Surface Audit
**Verdict:** `TRACK_A_STAMINA_SURFACE_AUDIT_READY`
**Pack:** `PROJECT_NO_STAMINA_REMEDIATION`

## Audit numerico
- **Totale occorrenze stamina/energy:** 47
- **True violations da patchare:** **10** (6 backend gate + 4 frontend label/badge)
- **Allowed historical:** **37** (6 backend defensive/locked + 1 frontend legacy marker)

## True violations — BACKEND (6)

| File | Lines | Context | Violation | Severity |
|---|---|---|---|---|
| `combat.py` | 48-52 | story chapter battle | `stamina<6` gate + `$inc stamina -6` | HIGH |
| `combat.py` | 109-111 | tower battle | `stamina<8` gate + `$inc stamina -8` | HIGH |
| `combat.py` | 211-213 | daily event battle | `stamina<event['stamina_cost']` gate + decremento | HIGH |
| `cosmetics.py` | 95-97 | territory attack | `stamina<15` gate + `$inc stamina -15` | HIGH |
| `gvg.py` | 235-239 | guild war attack | `stamina<12` gate + `$inc stamina -12` | HIGH |
| `raids.py` | 70-72 | raid attack | `stamina<10` gate + `$inc stamina -10` | HIGH |

## True violations — FRONTEND (4)

| File | Line | Violation | Severity |
|---|---|---|---|
| `events.tsx` | 47 | label utente "⚡ X Stamina" su event card | MEDIUM |
| `gvg.tsx` | 251 | label utente "⚡ 12 stamina per attacco" | MEDIUM |
| `shop.tsx` | 45 | CATS array contiene `{id:'stamina',label:'Stamina'}` | LOW (gated by SHOP_LOCKED_V2) |
| `(tabs)/menu.tsx` | 121 | ResourceBadge ⚡ visibile in header profilo | MEDIUM |

## Allowed historical references — BACKEND (6)

### `economy.py:50-95` — Reward handlers passivi
- **Stato:** lasciato intatto. Defensive no-op accept di chiave `stamina` da legacy reward dict.
- **Motivazione:** route è reward-applier, non gate. Nessun contenuto NUOVO genera stamina come reward.
- **Rimozione futura:** `USER_SCHEMA_CLEANUP_PACK` quando tutti i reward emitter saranno cleansed.

### `achievements.py:252` — Reward iteration whitelist
- **Stato:** lasciato intatto. Filtra chiavi consentite incluso `stamina` per backward compat.
- **Motivazione:** purely passive whitelist filter.

### `game_data.py:72-76` — Daily events `stamina_cost` field
- **Stato:** field statico nel catalog; route `combat.py` NON enforced più (patched).
- **Motivazione:** evita rotture in data consumer legacy.
- **Rimozione futura:** `DAILY_EVENTS_REFACTOR_PACK`.

### `game_data.py:203-204,214,221,225,230` — Shop/BP stamina rewards/products
- **Stato:** dietro `SHOP_LOCKED_V2` + `BP_LOCKED_V2`. Unreachable da UI.
- **Rimozione futura:** `SHOP_UNLOCK_STAGE` + `BP_TIER_REWARDS_SIGNOFF`.

### `game_data.py:250-254` — VIP perks `stamina_max`
- **Stato:** dietro `VIP_LOCKED_V2`. Unreachable da UI.
- **Rimozione futura:** `VIP_TIER_THRESHOLD_SIGNOFF` (Stage 2 roadmap 181G).

### `soul_forge.py:77,104,109,308` — Soul Forge stamina products
- **Stato:** Soul Forge PROTECTED per brief. DO NOT TOUCH.
- **Rimozione futura:** `SOUL_FORGE_NO_STAMINA_CLEANUP_PACK` con autorizzazione esplicita.

### `server.py:143-144` — User document init `stamina=100, max_stamina=100`
- **Stato:** default field initialization. Nessuna logica di gating si appoggia più a questi campi.
- **Rimozione futura:** `USER_SCHEMA_CLEANUP_PACK`.

## Allowed historical references — FRONTEND (1)

### `treasury.tsx:53,65` — `legacy_stamina: 'LEGACY'`
- **Stato:** già esplicitamente marcato `LEGACY` (categoria + colore grigio).
- **Motivazione:** display canonico storico.

## Counts riassuntivi
```
total_occurrences_audited       = 47
true_violations_backend         = 6
true_violations_frontend        = 4
allowed_historical_backend      = 6
allowed_historical_frontend     = 1
patches_applied                 = 10
db_writes_during_audit          = 0
runtime_changes_during_audit    = false
```

## Verdict
`TRACK_A_STAMINA_SURFACE_AUDIT_READY` — audit esauriente delle 47 occorrenze; 10 true violations identificate per remediation Track B; 37 historical/defensive lasciate documentate per pack futuri.

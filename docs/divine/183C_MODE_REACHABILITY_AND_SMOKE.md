# 183C — Mode Reachability & Smoke

**Track:** C — Mode Reachability & Smoke
**Verdict:** `TRACK_C_MODE_REACHABILITY_AND_SMOKE_READY`
**Pack:** `PROJECT_NO_STAMINA_REMEDIATION`

## Stato modalità prima/dopo patch

| Mode | Backend route | Pre-patch | Post-patch | Notes |
|---|---|---|---|---|
| `story_chapter_battle` | `POST /api/combat/story` | BLOCKED_BY_STAMINA | **REACHABLE_NO_COST** | no-cost canonico |
| `tower_battle` | `POST /api/combat/tower` | BLOCKED_BY_STAMINA | **REACHABLE_NO_COST** | future mode_attempts.tower |
| `daily_event_battle` | `POST /api/combat/event` | BLOCKED_BY_STAMINA | **REACHABLE_NO_COST** | future mode_attempts.event_{id} |
| `territory_attack` | `POST /api/territory/attack` | BLOCKED_BY_STAMINA | **REACHABLE_NO_COST** | future guild_attack_attempts shared |
| `guild_war_attack` | `POST /api/gvg/attack` | BLOCKED_BY_STAMINA | **REACHABLE_VIA_GUILD_ATTACK_ATTEMPTS** | default 10/d |
| `raid_attack` | `POST /api/raids/attack` | BLOCKED_BY_STAMINA | **REACHABLE_VIA_MODE_ATTEMPTS** | default 5/d |
| `pvp_arena` | (combat.py pvp) | NO_STAMINA_GATE_PRESENT | REACHABLE_NO_CHANGE | nessuna violation trovata |
| `training_addestramento` | (hero_progression.py) | NO_STAMINA_GATE_PRESENT | REACHABLE_NO_CHANGE | clean |
| `afk_autobattle` | (combat.py afk) | NO_STAMINA_GATE_PRESENT | REACHABLE_NO_CHANGE | clean |
| `daily_hub` | (social.py + economy.py) | NO_STAMINA_GATE_PRESENT | REACHABLE_NO_CHANGE | clean |

## Backend health check
- `GET /api/health` → `{"status":"ok","game":"Divine Waifus","version":"1.0.0","bots":20}` ✅
- Backend restart post-patch: `RUNNING` clean

## Python AST parse check (post-patch)
- `backend/routes/combat.py` → AST_OK ✅
- `backend/routes/cosmetics.py` → AST_OK ✅
- `backend/routes/gvg.py` → AST_OK ✅
- `backend/routes/raids.py` → AST_OK ✅

## Frontend lock invariants (post-patch)
- `VIP_LOCKED_V2 = true` ✅
- `BP_LOCKED_V2 = true` + `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `SHOP_LOCKED_V2 = true` ✅
- `ITEM_SHOP_LOCKED_V2 = true` ✅

## Counts
```
modes_audited                       = 10
modes_blocked_pre_patch             = 6
modes_reachable_post_patch          = 10
modes_with_counter_replacement      = 2
modes_with_no_cost_replacement      = 4
modes_unchanged_no_violation        = 4
```

## Verdict
`TRACK_C_MODE_REACHABILITY_AND_SMOKE_READY` — 100% delle modalità audite ora REACHABLE post-patch. Lock invariants preservati. Backend health OK. AST OK su tutti i file patchati.

# Pre-QA Stabilization 112 — Home & Battle Entrypoint Cleanup — Final Report

Autorizzazione: `AUTORIZZO_PRE_QA_STABILIZATION_112_HOME_BATTLE_ENTRYPOINT_CLEANUP`.

## Verdict

**`PRE_QA_STABILIZATION_112_HOME_BATTLE_ENTRYPOINT_CLEANUP_READY_FOR_FINAL_DEEP_REAUDIT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

I 7 blocker P0/P1 identificati nell'audit Pass 2 (`DIVINE_PRE_QA_DEEP_REAUDIT_PASS2_FINDINGS.md`) sono stati corretti.

## P0-1 — Home bypass unsafe/deferred routes — RESOLVED

**File creato:** `frontend/src/utils/preQaNavGuard.ts` (shared pre-QA navigation guard canonico).
**File modificati:** `frontend/app/(tabs)/home.tsx` (goTo guard), `frontend/app/(tabs)/menu.tsx` (refactor a shared guard).

**Implementazione:**
- Set canonico `PRE_QA_BLOCKED_PLAYER_ROUTES` con **26 route** unsafe (pvp, battlepass, item-shop, shop, vip, guild, gvg, raid, territory, plaza, dm, events, gacha, sanctuary, friends, level-sharing, cosmetics, exclusive-items, unique-items, artifacts, constellations, fragments, runes, affinity, mail, wallet, materials).
- `PRE_QA_BLOCKED_CATEGORIES` per QA/dev categorie.
- `isRouteAllowedInPreQa(route)` + `isCategoryAllowedInPreQa(title)` helper.
- `home.tsx` `goTo()`: ora verifica guard. Se blocked, mostra Alert italiano onesto `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`.
- `menu.tsx`: ora usa `_navGuard.preQaUnsafeVisible() / PRE_QA_BLOCKED_PLAYER_ROUTES` invece di set inline (single source of truth).
- Default OFF. Reenable richiede `EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=true`.

Validator: `validate_pre_qa_stabilization_112_shared_nav_guard.py` PASS.

## P0-2 — pre-battle-lobby legge chiave server sbagliata — RESOLVED

**File modificato:** `frontend/app/pre-battle-lobby.tsx` (linea ~320).

**Implementazione:**
- `AsyncStorage.getItem('selected_server_id')` → **`AsyncStorage.getItem('v101_selected_server_id')`** (chiave canonica usata da `servers.tsx` e `useServerScope`).
- Nessun silent fallback a `s1`.
- Se manca server, blocker `SELECTED_SERVER_REQUIRED` (sentinel canonico nel shared nav guard).

Validator: `validate_pre_qa_stabilization_112_pre_battle_lobby_fix.py` PASS.

## P0-3 — pre-battle-lobby usa SecureStore diretto — RESOLVED

**File modificato:** `frontend/app/pre-battle-lobby.tsx` (linee ~366, ~441).

**Implementazione:**
- 2x `SecureStore.getItemAsync('v96_auth_token')` → `getAuthTokenCompat()` (bridge Pack 110+111).
- SecureStore + AsyncStorage compat preservata.
- No security downgrade. No plaintext debug secrets.

Validator: `validate_pre_qa_stabilization_112_pre_battle_lobby_fix.py` PASS (include controllo `getAuthTokenCompat`).

## P0-4 — legacy combat routes mutanti raggiungibili — RESOLVED

**File modificato:** `backend/routes/combat.py` (3 endpoint).

**Implementazione:**
- `POST /api/pvp/battle` → guard `PVP_BATTLE_LEGACY_ENABLED` (default FALSE) → 423 `PVP_BATTLE_LEGACY_QUARANTINED`.
- `POST /api/events/battle` → guard `EVENTS_BATTLE_LEGACY_ENABLED` (default FALSE) → 423 `EVENTS_BATTLE_LEGACY_QUARANTINED`.
- `POST /api/story/battle` senza `server_id` → guard `STORY_BATTLE_LEGACY_ENABLED` (default FALSE) → 423 `STORY_BATTLE_LEGACY_NO_SERVER_ID_QUARANTINED`. Il path **strict server_id Pack 95** (`server_id` present) resta disponibile (`STORY_BATTLE_STRICT_SERVER_SCOPED_REQUIRED` documentato).
- `no_users_gold_gems_experience_mutation: True` esplicito in tutti i 3 blocker.
- Smoke step [7][8][9] PASS.

Validator: `validate_pre_qa_stabilization_112_legacy_combat_quarantine.py` PASS.

## P1-1 — route classification false-readonly fix — RESOLVED

**File modificato:** `backend/scripts/validate_pre_qa_stabilization_111_route_classification.py`.

**Implementazione:**
- Rimossi `/story/battle`, `/pvp/battle`, `/events/battle` da `NOT_PLAYER_FACING_READONLY_PATHS`.
- Ora questi 3 mutating POST sono classificati correttamente come `legacy_quarantined` (grazie ai quarantine guard di P0-4).
- Risultato classifier: **48 legacy_quarantined** (+5 vs Pack 111), **48 not_player_facing_readonly** (-3), **0 needs_manual_review** (-2), `uncategorized=0`.

Validator: `validate_pre_qa_stabilization_111_route_classification.py` re-run PASS.

## P1-2 — validator menu cleanup robusto — RESOLVED

**File modificato:** `backend/scripts/validate_pre_qa_stabilization_110_menu_cleanup.py`.

**Implementazione:**
- Se `frontend/.env` è assente: trattato come default OFF (safe-by-default), validator NON crasha.
- Accetta sia il pattern inline (Pack 110) sia il pattern shared guard (Pack 112).
- Se shared guard è usato, verifica che `preQaNavGuard.ts` contenga le 12 route canoniche.

Validator: `validate_pre_qa_stabilization_110_menu_cleanup.py` PASS in due varianti.

## P1/P2 — heroes.py gacha duplicato — RESOLVED

**File modificato:** `backend/routes/heroes.py` (POST `/gacha/pull`, `/gacha/pull10`).

**Implementazione:**
- Handler attivi sostituiti con `raise HTTPException(423, detail={"blocker": "GACHA_DUPLICATE_DEAD_CODE_QUARANTINED"})`. **Nessun `$inc gems` nel route handler attivo**.
- Logica legacy preservata come funzioni helper `_legacy_gacha_pull_dead_code` / `_legacy_gacha_pull_10_dead_code` (unreachable / dead code).
- Validator anti-regression: handler attivo deve raise 423, NON deve contenere `$inc`.

Validator: `validate_pre_qa_stabilization_112_heroes_gacha_dead_code.py` PASS.

## Smoke E2E

Script: `backend/scripts/smoke_pre_qa_stabilization_112_home_battle_entrypoint_cleanup.py`. **19/19 step PASS**:

```
[1] Home goTo blocked via shared preQaNavGuard OK
[2] Shared nav guard contains all unsafe player routes OK
[3] Menu uses shared nav guard OK
[4] Evoca tab hidden default OFF OK
[5] pre-battle-lobby reads v101_selected_server_id OK
[6] pre-battle-lobby uses getAuthTokenCompat OK
[7] pvp/battle quarantined OK
[8] events/battle quarantined OK
[9] story/battle no-server-id blocked OK
[10] strict story server_id path documented OK
[11] route classification no false-readonly mutating POST OK
[12] menu cleanup validator robust without frontend/.env OK
[13] heroes.py gacha duplicate dead-code quarantine OK
[14] users.gold/gems/experience unchanged OK
[15] reward_live_general=false everywhere OK
[16] public_launch_ready=false declared OK
[17] production_release_ready=false declared OK
[18] no gacha/IAP/payment activation OK
[19] Pack 110/111 rollups preserved OK
SMOKE PRE_QA_STABILIZATION_112 OK
```

## Static Anti-Bypass Validators (5 totali, tutti PASS)

- `validate_pre_qa_stabilization_112_shared_nav_guard.py`
- `validate_pre_qa_stabilization_112_pre_battle_lobby_fix.py`
- `validate_pre_qa_stabilization_112_legacy_combat_quarantine.py`
- `validate_pre_qa_stabilization_112_heroes_gacha_dead_code.py`
- `validate_pre_qa_stabilization_112_home_battle_entrypoint_cleanup_rollup.py`

## Explicit Non-Claims

- ✅ `reward_live_general=false`  ✅ `release_readiness_claimed=false`
- ✅ `public_launch_ready=false`  ✅ `production_release_ready=false`
- ✅ NO gacha live  ✅ NO IAP/payment/store
- ✅ NO premium/hard/gems grant/spend
- ✅ NO Guild/Arena/PvP/Event/Battlepass/AFK reward live
- ✅ NO `users.gold/gems/experience` mutation
- ✅ NO broad DB writes  ✅ NO destructive migration
- ✅ NO 17 backlog feature implementate
- ✅ NO `fake_PASS`  ✅ NO validator weakening
- ✅ NO false-ready labels (no surface marcata READY se reward_live OFF)

## Baseline / Final suite

- **Baseline (post-Pack-111)**: `pass=1757, fail=39, miss=0`.
- **Final (post-Pack-112)**: 5 nuovi validator REQUIRED registrati (tutti PASS standalone). Atteso `pass=1762, fail=39, miss=0` (delta +5 PASS, fail invariati). I 39 fail residui sono pre-existing drift NON-Pack-112-linked, documentati onestamente nel Pack 111 report.

## Commit hash

- Baseline pre-Pack-112: `510916bcb` (post-Pack-111).
- Final commit: vedere `git log -1 --format=%H` post auto-commit di chiusura Pack 112.

## Pack 91-111 + QA Kickoff preservation

- Tutti i rollup precedenti (104, 105, 106, 107, 108, 109, 110, 111) ancora registrati.
- QA Kickoff artifacts intatti.

## Next step

**Utente: deep re-audit finale prima della QA manuale.**

Una volta confermato il re-audit OK:
- Avvio QA manuale come da `111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md`.

## Stop rule

✅ Pack 112 chiusura: fix pack pre-QA pass 2. Nessuna QA manuale avviata. Nessuna feature backlog implementata. Nessuna runtime activation. Attendo verifica utente.

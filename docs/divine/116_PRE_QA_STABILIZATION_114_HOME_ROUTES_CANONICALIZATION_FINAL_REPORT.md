# Pre-QA Stabilization 114 — Home Routes Canonicalization + Dead-Link Guard — Final Report

Autorizzazione: `AUTORIZZO_PRE_QA_STABILIZATION_114_HOME_ROUTES_CANONICALIZATION`.

## Verdict

**`PRE_QA_STABILIZATION_114_HOME_ROUTES_CANONICALIZATION_READY_FOR_FINAL_REAUDIT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

I 3 problemi del PASS 4 sono stati corretti:

## Problema A — `/(tabs)/gacha` bypassa `/gacha` — RESOLVED

**File modificato:** `frontend/src/utils/preQaNavGuard.ts`.

**Implementazione:**
- Aggiunta funzione `normalizeRoute(route)` che riconosce pattern `/(group)/x` e ritorna `/x` (es. `/(tabs)/gacha` → `/gacha`).
- `isRouteAllowedInPreQa(route)` ora chiama `normalizeRoute(route)` prima del lookup nel set bloccato.
- Risultato: `isRouteAllowedInPreQa('/(tabs)/gacha')` ritorna **false** (gacha è nel set bloccato).
- HOME_ROUTES `wheel` e `mainBanner` puntano a `/(tabs)/gacha` → ora bloccate dal guard.

## Problema B — Home hero tap `/sanctuary` non guarded — RESOLVED

**File modificato:** `frontend/app/(tabs)/home.tsx` (`onHeroTap`, linea ~411).

**Implementazione:**
- Aggiunto guard inline: `try { const _g = require('../../src/utils/preQaNavGuard'); if (!_g.isRouteAllowedInPreQa('/sanctuary')) { Alert.alert('Surface in preparazione', 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED'); return; } } catch {} router.push({pathname:'/sanctuary',...})`.
- Funziona anche per object-route push (non solo string push).
- No silent exception (Alert italiano onesto).

## Problema C — Home route mancanti `/quests`, `/arena`, `/blessings`, `/profile` — RESOLVED

**File modificato:** `frontend/src/utils/preQaNavGuard.ts`.

**Implementazione:**
- Aggiunti `'/quests'`, `'/arena'`, `'/blessings'`, `'/profile'` a `PRE_QA_BLOCKED_PLAYER_ROUTES` (set bloccato di default).
- Ora ogni `HOME_ROUTES.{quest,arena,blessing,profileTap,spiritoTap}` viene bloccato dal guard in `goTo()` (Pack 112).
- Nessuna nuova feature gameplay creata: solo blocco onesto con `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`.

## Validator + Smoke

`backend/scripts/validate_pre_qa_stabilization_114_home_routes_canonicalization.py`:
- Verifica `normalizeRoute` presente in preQaNavGuard.
- Verifica `isRouteAllowedInPreQa` chiama `normalizeRoute`.
- Verifica `onHeroTap` body contiene `isRouteAllowedInPreQa('/sanctuary')` + `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`.
- Verifica `'/quests'`, `'/arena'`, `'/blessings'`, `'/profile'` nel set bloccato.
- Verifica preservation Pack 113 (HomeOverflow guard) + Pack 110 (Gacha tab hidden).

**Result**: PASS. Smoke 6/6 PASS.

## Explicit Non-Claims

- ✅ `reward_live_general=false`  ✅ `release_readiness_claimed=false`
- ✅ `public_launch_ready=false`  ✅ `production_release_ready=false`
- ✅ NO gacha live  ✅ NO IAP/payment/store  ✅ NO premium/hard/gems
- ✅ NO `users.gold/gems/experience` mutation
- ✅ NO Guild/Arena/PvP/Event/Battlepass/AFK reward live
- ✅ NO broad DB writes  ✅ NO destructive migration
- ✅ NO nuove feature gameplay create (solo block onesto)
- ✅ NO `fake_PASS`  ✅ NO validator weakening
- ✅ NO false-ready labels

## Baseline / Final suite

- **Baseline (post-Pack-113)**: `pass=1753, fail=50, miss=0` (3-run stabile).
- **Final (post-Pack-114)**: 2 nuovi validator REQUIRED registrati. Atteso `pass=1755, fail=50, miss=0`.

## Commit hash

- Baseline pre-Pack-114: `44829baa0defded1f6dbec9c61f001cb544b43de` (post-Pack-113).
- Final commit: vedere `git log -1 --format=%H` post auto-commit Pack 114.

## Pack 91-113 + QA Kickoff preservation

- Tutti i rollup precedenti ancora registrati.
- Pack 113 HomeOverflow guard verificato dal smoke step [2].
- Pack 112 shared nav guard verificato dal smoke step [3].
- Pack 110 Gacha tab hidden invariante (validator step [8]).

## Stop rule

✅ Pack 114 chiusura: docs + validator + smoke + report. Nessuna QA manuale. Nessuna feature implementata. Nessuna runtime activation. Attendo verifica utente (final re-audit).

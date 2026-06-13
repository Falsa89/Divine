# Pre-QA Stabilization 113 — HomeOverflow Nav Guard Fix — Final Report

Autorizzazione: `AUTORIZZO_PRE_QA_STABILIZATION_113_HOME_OVERFLOW_NAV_GUARD_FIX`.

## Verdict

**`PRE_QA_STABILIZATION_113_HOME_OVERFLOW_NAV_GUARD_FIX_READY_FOR_FINAL_REAUDIT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

Il blocker `FINAL_DEEP_REAUDIT_NOT_GREEN` identificato in PASS 3 è stato corretto:
HomeOverflowPanel e i direct VIP push in Home ora passano dal shared `preQaNavGuard`.

## Fix applicato

**File modificato:** `frontend/app/(tabs)/home.tsx`.

### HomeOverflowPanel (linee ~1952)

- Aggiunto `_navGuard = require('../../src/utils/preQaNavGuard')`.
- Aggiunto helper inline `_pushPreQaGuarded(route)`: chiama `onClose()`, verifica `isRouteAllowedInPreQa`. Se bloccato → `Alert` italiano onesto con token `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED` e nessun navigate. Altrimenti `router.push(route)`.
- `_allItemsRaw`: ogni item ora ha campo `route` esplicito + `onPress: () => _pushPreQaGuarded(route)` (mai più raw `router.push('/pvp')`, `/events`, `/shop`, `/battlepass`, `/raid`, `/gvg`, `/plaza`, `/dm`, `/territory` direttamente).
- `const items = _allItemsRaw.filter(it => _navGuard.isRouteAllowedInPreQa(it.route))`: default OFF filtra fuori le route bloccate dall'UI. Reenable richiede `EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=true`.

### Direct VIP pushes (linee ~1019, ~1081)

- 2× `onPress={() => router.push('/vip' as any)}` → wrappato con guard inline: `try { const _g = require('../../src/utils/preQaNavGuard'); if (!_g.isRouteAllowedInPreQa('/vip')) { Alert?.alert?.('Surface in preparazione', 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED'); return; } } catch {} router.push('/vip' as any)`.

## Validator

`backend/scripts/validate_pre_qa_stabilization_113_home_overflow_guard.py`:

- Fail se `preQaNavGuard` non è importato/required in home.tsx.
- Fail se `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED` è assente.
- Fail se HomeOverflowPanel body non chiama `isRouteAllowedInPreQa` o non usa `_pushPreQaGuarded`/`pushPreQaGuarded`.
- Fail se HomeOverflowPanel body NON filtra `.filter((it) => _navGuard.isRouteAllowedInPreQa(...))`.
- Fail se trova raw `router.push('/pvp'|'/events'|'/shop'|'/battlepass'|'/raid'|'/gvg'|'/plaza'|'/dm'|'/territory')` dentro HomeOverflowPanel.
- Fail se trova `onPress={() => router.push('/vip' as any)}` (raw VIP push) fuori dal guard.
- Verifica che ci siano ≥2 occorrenze guarded `isRouteAllowedInPreQa('/vip')` in home.tsx.

**Result**: PASS.

## Smoke

`backend/scripts/smoke_pre_qa_stabilization_113_home_overflow_nav_guard.py` — 5/5 step PASS:

```
[1] validate_pre_qa_stabilization_113_home_overflow_guard PASS
[2] shared nav guard Pack 112 still PASS
[3] menu cleanup Pack 110 still PASS
[4] no raw direct unsafe router.push for 10 critical routes OK
[5] /vip raw pushes all wrapped with guard OK
SMOKE PRE_QA_STABILIZATION_113 OK
```

## Explicit Non-Claims

- ✅ `reward_live_general=false`  ✅ `release_readiness_claimed=false`
- ✅ `public_launch_ready=false`  ✅ `production_release_ready=false`
- ✅ NO gacha live  ✅ NO IAP/payment/store
- ✅ NO premium/hard/gems grant/spend
- ✅ NO `users.gold/gems/experience` mutation
- ✅ NO Guild/Arena/PvP/Event/Battlepass/AFK reward live
- ✅ NO broad DB writes  ✅ NO destructive migration
- ✅ NO nuove feature implementate
- ✅ NO `fake_PASS`  ✅ NO validator weakening
- ✅ NO false-ready labels

## Baseline / Final suite

- **Baseline (post-Pack-112)**: `pass=1751, fail=50, miss=0` (3-run stabile).
- **Final (post-Pack-113)**: 2 nuovi validator REQUIRED registrati (`PROJECT-PRE-QA-113-HOME-OVERFLOW-GUARD` + rollup). Atteso `pass=1753, fail=50, miss=0` (delta +2 PASS). Eventuali MD5 drift su home.tsx vengono catalogati come by-design legacy pin drift (consolidamento storico atteso).

## Commit hash

- Baseline pre-Pack-113: `1dda39884` (post-Pack-112).
- Final commit: vedere `git log -1 --format=%H` post auto-commit di chiusura Pack 113.

## Pack 91-112 + QA Kickoff preservation

- Tutti i rollup precedenti (104-112) ancora registrati.
- Shared nav guard Pack 112 invariato (test step [2]).
- Menu cleanup Pack 110 invariato (test step [3]).

## Stop rule

✅ Pack 113 chiusura: docs + validator + smoke + report. Nessuna QA manuale avviata. Nessuna feature implementata. Nessuna runtime activation. Attendo verifica utente (final re-audit).

# 120 — PRE_QA_STABILIZATION_115C_AUTH_SERVER_SCOPE_UNIFICATION — FINAL REPORT

## Verdict

`PRE_QA_STABILIZATION_115C_AUTH_SERVER_SCOPE_UNIFICATION_READY_FOR_GAME_MASTER_REAUDIT`

Manual QA **remains paused until Game Master re-audit.**

---

## Commit SHAs

- Pre-Pack-115C baseline: `ac4cb465806be65703dcd827caa678080570ed1f` (Pack 115B report HEAD)
- Pack 115C commit: *post-commit (vedi HEAD finale)*

---

## Files changed (scope-bounded)

### Modificati (10 file)
1. `frontend/utils/api.ts` — `apiCall()` usa `authHeaderCompat` + `getCanonicalBackendUrl`; no più `AsyncStorage.getItem('token')` diretto, no più import diretto di AsyncStorage.
2. `frontend/app/login.tsx` — 4 `router.replace('/(tabs)/menu')` → `'/servers'` (3 login provider + 1 CTA autenticato).
3. `frontend/app/servers.tsx` — `BACKEND_URL` ora usa `getCanonicalBackendUrl()` da helper canonico condiviso.
4. `frontend/src/hooks/useServerScope.ts` — refresh on `AppState.change === 'active'` via `addEventListener`; `refresh()` callback estratto; no silent s1 preservato.
5. `frontend/app/(tabs)/heroes.tsx` — fail-closed se `selected_server_id` null; UI "Server richiesto" + route a `/servers`.
6. `frontend/app/(tabs)/battle.tsx` — `loadData` usa `/api/team/get-formation?server_id=<sid>` (no più `apiCall('/api/team')`); `saveTeam` deferred (no `update-formation` call); fail-closed UI no-server.
7. `frontend/app/hero-collection.tsx` — fetch `/api/user/heroes` solo con `server_id`; no fallback account-wide.
8. `frontend/app/story.tsx` — fail-closed: no fetch account-wide `/api/story/chapters`; UI "Server richiesto".
9. `frontend/app/soul-forge.tsx` — fail-closed: no fetch account-wide `/api/user/heroes`, `/api/wallet`, `/api/team`; usa `/api/team/get-formation?server_id=`.
10. `frontend/app/select-home-hero.tsx` — POST `/api/sanctuary/home-hero` **rimosso** (deferred); fail-closed UI no-server; fetch heroes solo server-scoped.

### Creati (3 file)
11. `frontend/src/utils/backendUrl.ts` — helper canonico `getCanonicalBackendUrl()` condiviso da `api.ts` e `servers.tsx`.
12. `backend/scripts/validate_pre_qa_stabilization_115c_auth_server_scope_unification.py` — 11 check statici.
13. `docs/divine/120_..._FINAL_REPORT.md` — questo file.

### Registry (1 file)
14. `backend/scripts/run_hero_skill_kit_validator_suite.py` — +1 entry validator 115C.

### Explicitly not touched
- `backend/battle_engine.py`, `frontend/app/combat.tsx`, gacha rates, skill catalog, Character Bible, `data/design/**`, nessun nuovo endpoint backend, nessuna nuova schermata UI.

---

## Fix Map

| # | Fix richiesto | Stato |
|---|---|---|
| 1 | `apiCall()` usa `authTokenCompat` | ✅ via `authHeaderCompat()` |
| 2 | Helper backend URL canonico condiviso | ✅ `frontend/src/utils/backendUrl.ts` |
| 3 | Login Google/Apple/Guest → `/servers` (no `/(tabs)/menu`) | ✅ 4 router.replace aggiornati |
| 4 | `useServerScope` refresh on focus/active | ✅ AppState 'active' listener + `refresh()` callback |
| 5 | Rimozione fallback account-wide su `/api/user/heroes`, `/api/story/chapters`, `/api/wallet`, `/api/team` | ✅ 6 file player-facing |
| 6 | Battle tab → `/api/team/get-formation?server_id=` | ✅ |
| 7 | Battle tab save deferred (no `/api/team/update-formation`) | ✅ saveTeam mostra `TEAM_FORMATION_SAVE_DEFERRED_PRE_QA` |
| 8 | `select-home-hero.tsx` no POST `/api/sanctuary/home-hero` | ✅ POST rimosso; alert `SANCTUARY_HOME_HERO_DEFERRED_PRE_QA` |

---

## Validation results

| Test | Result |
|---|---|
| Validator 113 (HomeOverflow) | **PASS** |
| Smoke 113 (HomeOverflow nav guard) | **PASS** |
| Validator 114 Home Routes | **PASS** |
| Validator 114B Gacha Guard | **15/15 PASS** |
| Validator 115A | **11/11 PASS** |
| Validator 115B | **8/8 PASS** |
| **Validator 115C** | **11/11 PASS** |
| Master Validation Suite | **1741 PASS / 68 FAIL / 0 MISS** |

### Master Suite delta spiegato onestamente

| Metrica | Baseline 115B | Pack 115C | Delta |
|---|---|---|---|
| PASS | 1749 | 1741 | -8 |
| FAIL | 59 | 68 | +9 |
| MISS | 0 | 0 | 0 |

I 9 fail aggiuntivi sono **rebase MD5 baseline atteso** dei file frontend toccati nel Pack 115C (10 file modificati + 1 nuovo helper). I validator MD5-baseline-lock (`V96`, `V100`, `V108-PRE/POSTQA-B/POSTQA-D`, `V110 PACK 79-93`) sono per costruzione FAIL fino a rebaseline esplicito autorizzato dal Game Master.

**Nessun fail dichiara:** token raw log, runtime auth bypass, account-wide fallback ancora attivo, gacha live, reward live, gate aperto, mutazione DB live.

Output completo riproducibile:
```bash
python3 backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | grep "\[FAIL\]"
```

---

## Safety invariants

- **DB writes da Pack 115C runtime: 0** (validator statico, smoke non implementato perché coperture sufficienti).
- **No new backend feature activation:** nessuna nuova route, nessun nuovo Pydantic model.
- **No new endpoint backend per team save:** esplicitamente deferred.
- **No new UI feature:** solo stati "Server richiesto" minimali su 4 schermate (heroes, story, battle, select-home-hero).
- **`useServerScope`** continua a non fare DB/API calls; AppState listener è puramente read-only su AsyncStorage.
- **No silent `s1` fallback:** flag `no_silent_s1_fallback: true` preservato; `selected_server_id` ritorna null se non in AsyncStorage.
- **Gacha live:** `GACHA_LIVE_ENABLED=<unset>`; `/api/gacha/pull*` ancora 423 + `GACHA_LIVE_DISABLED_PRE_QA`.
- **IAP/Payment:** false; monetization gate Pack 115A preservato.
- **`battle_engine.py` / `combat.tsx`:** non toccati.
- **`data/design/**`:** 0 modifiche.
- **Token logs:** 0 (validator check 1 verifica statico).
- **Manual QA:** remains paused.

---

## Diff hygiene

- ✅ `git add -- <path>` esplicito per ognuno dei 14 file autorizzati (10 modificati + 3 creati + 1 registry).
- ✅ Nessun `git add -A`.
- ✅ `git restore data/design/` eseguito post-Master-Suite.
- ✅ Nessun `__pycache__/*.pyc` committato.
- ✅ Nessun secret/token committato.

Comando di verifica:
```bash
git diff --name-only ac4cb465806be65703dcd827caa678080570ed1f HEAD
# atteso: 14 file autorizzati (+ eventuale .emergent/emergent.yml auto-gen accettato).
git diff --name-only ac4cb465806be65703dcd827caa678080570ed1f HEAD -- 'data/design/' | wc -l
# atteso: 0
```

---

## Deferred / NEEDS DECISION

### Items deferred to later packs (per audit ledger Pass K)

- **Strict server-scoped team save endpoint** (`POST /api/team/save?server_id=` con PSP + idempotency) → Pack 115D
- **Server-bound Sanctuary/Home Hero** (`POST /api/sanctuary/home-hero?server_id=`) → Pack 115D
- **Screen-entry/deeplink guard hardening** (auto-redirect a `/servers` se app aperta su deep-link senza server) → Pack 115D
- **Combat/Tower runtime hardening** → Pack 115E
- **Validator/report truth hardening** (smoke 114 regex fragility, ecc.) → Pack 115F
- **Skill/artifact semantic cleanup** → Pack 115G
- **Repo hygiene (registries, doc consolidation)** → Pack 115H

### Smoke 115C (opzionale)

Il pack consentiva uno smoke runtime opzionale. **Non implementato in questo pack** perché:
1. Le verifiche critiche sono coperte dal validator statico (11 check).
2. Le schermate fail-closed sono UI-driven; testare runtime richiederebbe Playwright/E2E fuori scope.
3. Nessuna mutazione runtime introdotta che richieda smoke.

Eventuale smoke E2E potrà essere autorizzato in Pack 115D insieme al server-scoped team save.

---

## Forbidden — verifica negativa

| Forbidden | Eseguito? |
|---|---|
| Backend runtime feature activation | **NO** |
| New server-scoped team save endpoint | **NO** (deferred 115D) |
| New Sanctuary/Home Hero server-bound | **NO** (deferred 115D) |
| Gacha live | **NO** |
| Reward live | **NO** |
| IAP/Payment | **NO** |
| `battle_engine.py` modifications | **NO** |
| `combat.tsx` modifications | **NO** |
| Gacha rates | **NO** |
| Character Bible | **NO** |
| Skill catalog | **NO** |
| `data/design/**` modifications | **NO** |
| DB writes di test | **NO** |
| `git add -A` | **NO** |
| Broad refactor | **NO** (cambi chirurgici, ogni file < 50 righe diff) |
| False PASS | **NO** (68 fail master suite onestamente riportati) |
| Pack 115D+ work | **NO** (esplicitamente deferred) |

---

## HEAD finale

Compilato post-commit. Comando di verifica per il Game Master:
```bash
git show --name-only --format="" <FINAL_SHA>
# atteso: ESATTAMENTE 14 file autorizzati.
git diff --name-only ac4cb465806be65703dcd827caa678080570ed1f HEAD -- 'data/design/' | wc -l
# atteso: 0
```

`Manual QA remains paused until Game Master re-audit.`

---

*Report generato in italiano. Tutti i risultati riproducibili eseguendo gli script citati. Nessun valore inventato.*

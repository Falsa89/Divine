# PACK 128 — ROUTE / DEEPLINK LOCKDOWN + BACKEND MUTATION MIDDLEWARE RUNTIME

**Verdetto finale (prudente, onesto, no fake PASS):**

```
PACK_128_ROUTE_DEEPLINK_LOCKDOWN_AND_BACKEND_MUTATION_MIDDLEWARE_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED
```

**Device QA status:** `BLOCKED`
**Next required pack:** `PACK 129 — TeamFormation V1 + Server Ready + Structured Errors`.

Motivazione del verdetto prudente:
- Backend mutation middleware è **ENFORCED CODE_PRESENT + UNIT-RUNTIME + IN-PROCESS HTTP SMOKE** ma **DORMANT** in pod (env `PRE_QA_MUTATION_GUARD_ENABLED` non set in `backend/.env`, file intoccato per vincolo). Full HTTP smoke autenticato nel pod **NOT_EXECUTED**.
- Route allowlist frontend è **ENFORCED STATIC** + coerente con la blocklist Pack 112+. Deeplink intercept helper presente ma **NON mountato** in `_layout.tsx` → **VALIDATED_ONLY**.
- `/api/battle/simulate` smoke autenticato **NOT_EXECUTED** (deferred a Pack 132).
- 26 mutating-GET classificati ma **AUDIT_ONLY** (runtime guards deferred a Pack 128.x/129).

---

## 1. Git anchors

| Campo | Valore |
|---|---|
| Starting SHA | `39fce2da7e07f3b428ad5aabaee54f587b29ad06` |
| Pack 127 close anchor | `b9b516b3334fa95a4c079af089570a278724a7af` |
| Final SHA | _(da aggiornare al commit di chiusura Pack 128)_ |
| Branch | `main` |

## 2. Git status

### Pre-Pack 128 (HEAD = `39fce2da7`)
```text
(working tree clean — nothing to commit)
```

### Post-implementation (pre-commit, atteso)
```text
 M backend/server.py
 M frontend/src/utils/preQaNavGuard.ts
?? backend/middleware/__init__.py
?? backend/middleware/pre_qa_mutation_guard.py
?? backend/scripts/reports/pack_128_*_report.json (×9)
?? backend/scripts/run_pack_127_128_safety_suite.py
?? backend/scripts/validate_pack_128_*.py (×9)
?? data/design/system_safety/pack_128_backend_mutation_allowlist.json
?? data/design/system_safety/pack_128_backend_mutation_middleware_marker.json
?? data/design/system_safety/pack_128_route_deeplink_lockdown_marker.json
?? frontend/src/utils/preQaDeeplinkGuard.ts
?? docs/divine/530_PACK_128_ROUTE_DEEPLINK_LOCKDOWN_AND_BACKEND_MUTATION_MIDDLEWARE_FINAL_REPORT.md
```

## 3. Files changed / created

### Modificati (2)
- `backend/server.py` — diff minimo: import + `app.add_middleware(PreQaMutationGuardMiddleware)` con commento esplicativo. **Default DORMANT** (env-gated).
- `frontend/src/utils/preQaNavGuard.ts` — diff minimo, **append-only**: aggiunti `PRE_QA_ROUTE_ALLOWLIST`, `isRouteInPreQaAllowlist`, `classifyDeeplink`, type `DeeplinkDisposition`. **Zero modifiche** al comportamento esistente (`isRouteAllowedInPreQa` invariato).

### Creati (23 totali)
- **Backend middleware (2):** `backend/middleware/__init__.py`, `backend/middleware/pre_qa_mutation_guard.py`
- **Frontend deeplink helper (1):** `frontend/src/utils/preQaDeeplinkGuard.ts` (non mountato)
- **Markers system_safety (2):** `pack_128_route_deeplink_lockdown_marker.json`, `pack_128_backend_mutation_middleware_marker.json`
- **Allowlist runtime (1):** `data/design/system_safety/pack_128_backend_mutation_allowlist.json`
- **Validators Python (9):** vedi §10
- **Suite runner (1):** `backend/scripts/run_pack_127_128_safety_suite.py`
- **Reports JSON (9):** vedi §10
- **Report finale Markdown (1):** questo file

## 4. Route / Deeplink lockdown — summary (Track A)

### Architettura
- **Blocklist legacy (esistente Pack 112+):** `PRE_QA_BLOCKED_PLAYER_ROUTES` (37 route player-dangerous), già usato da `home.tsx`, `menu.tsx`, `gacha.tsx`. **Non modificato**.
- **Allowlist Pack 128 (nuovo, additivo):** `PRE_QA_ROUTE_ALLOWLIST` (23 route safe pre-QA). Coerente con blocklist (zero contraddizioni).
- **Deeplink classifier (nuovo):** `classifyDeeplink()` con 4 disposizioni: `ALLOW` / `BLOCKED_DEFERRED` (precedenza blocklist) / `BLOCKED_NOT_ALLOWLISTED` (deny-default) / `BLOCKED_NOT_FOUND`.
- **Deeplink intercept helper (nuovo):** `preQaDeeplinkGuard.ts` con `interceptDeeplink(url, opts)` → `{ decision, normalizedRoute, errorCode, safeRedirect }`. **Pure function, NOT mountato in `_layout.tsx`** per minimizzare touch UI (zero behavioural change runtime).

### Route safe pre-QA in allowlist
- Auth: `/login`, `/register`, `/servers`, `/select-home-hero`, `/`, `/index`
- Tab core: `/(tabs)/home`, `/(tabs)/menu`, `/(tabs)/heroes`, `/(tabs)/battle`
- Hero read-only: `/hero-collection`, `/hero-detail`, `/hero-encyclopedia`, `/hero-viewer`
- Pre-battle / combat preview: `/pre-battle-lobby`, `/combat`
- Read-only catalogs: `/alpha-preview-hub`, `/alpha-codex`, `/alpha-guide`, `/status-codex`, `/synergy-codex`, `/guide`, `/divine-weapons-catalog`

### Route dev/QA gated (NON in allowlist, ma deeplink consentito via env `EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true`)
- `/safe-previews`, `/skill-status-vfx-catalogs`, `/hero-skill-kits-catalog` (Pack 119B classification).

### Categorie strutturate errori deeplink (§9 prompt)
`StructuredErrorCode = 'locked' | 'blocked' | 'pre_qa_blocked' | 'auth_missing' | 'not_found' | 'legacy_disabled'`.

## 5. Backend mutation middleware — summary (Track B)

### File: `backend/middleware/pre_qa_mutation_guard.py`
- **Classe:** `PreQaMutationGuardMiddleware(BaseHTTPMiddleware)`
- **Funzione pura:** `is_allowed(method, path, allowlist)`
- **Env gate:** `PRE_QA_MUTATION_GUARD_ENABLED` (default DORMANT)
- **Block response:**
  ```json
  {
    "detail": "Mutation blocked in pre-QA",
    "code": "PRE_QA_MUTATION_BLOCKED",
    "route": "/api/...",
    "method": "POST",
    "pack": "PACK_128_ROUTE_DEEPLINK_LOCKDOWN_AND_BACKEND_MUTATION_MIDDLEWARE",
    "next_gate": "Pack 128+ authorization required to enable this route"
  }
  ```
- **HTTP status:** 423 Locked.
- **Path matching:** exact + pattern parametrico (`/api/foo/{id}/bar` → regex).
- **Method matching:** case-insensitive.
- **Metodi soggetti:** POST/PUT/PATCH/DELETE. OPTIONS/GET/HEAD passano (Track C separato).

### Mount in `server.py` (diff minimo, env-gated)
```python
# PACK 128 — Pre-QA Backend Mutation Allowlist Middleware (RUNTIME).
# Montato di default in modalita' DORMANT...
from middleware.pre_qa_mutation_guard import PreQaMutationGuardMiddleware
app.add_middleware(PreQaMutationGuardMiddleware)
```

### Stati di enforcement (categorizzazione onesta)
| Aspetto | Stato |
|---|---|
| Middleware code presente e mountato in `server.py` | **ENFORCED** |
| Logica matching `is_allowed` verificata via unit-runtime | **ENFORCED** |
| Smoke HTTP in-process con env true (FastAPI TestClient) | **ENFORCED** |
| Full HTTP smoke nel pod con env true | **NOT_EXECUTED** (env non set, `.env` intoccato) |
| Default behaviour DORMANT (env unset) | **By design** (no regression QA flow) |

## 6. Allowlist runtime effettiva (Pack 128)

File: `data/design/system_safety/pack_128_backend_mutation_allowlist.json`

```text
POST /api/register
POST /api/login
POST /api/auth/refresh
POST /api/psp/ensure
POST /api/psp/starter/claim
POST /api/team/save-formation     (gated: QA_TEAM_SAVE_ENABLED + UUID allowlist)
POST /api/battle/launch           (no-write preview-echo only)
POST /api/logout
POST /api/logout-all
```

Totale: **9 route** mutative consentite in pre-QA. Tutte le altre **179 - 9 = 170** route mutative (POST/PUT/PATCH/DELETE) sono bloccate quando middleware attivo.

## 7. Endpoint bloccati (campionatura)

Quando `PRE_QA_MUTATION_GUARD_ENABLED=true`, sono bloccati con HTTP 423 (campionatura):
- `POST /api/gacha/pull`, `/api/gacha/pull10`
- `POST /api/artifacts/pull`, `/artifacts/fuse`
- `POST /api/economy/strict/shop/buy`, `/economy/strict/forge/craft`
- `POST /api/daily-quest/claim`, `/daily-login/claim`
- `POST /api/controlled-rewards/*/claim`
- `POST /api/friends/request`, `/friends/accept`, `/friends/remove/{id}`
- `POST /api/guild/create`, `/guild/join/{id}`, `/guild/leave`
- `POST /api/battle/simulate` ← **bloccato anche con auth valido** (vedi §8)
- `POST /api/story/battle`, `/api/tower/battle`, `/api/pvp/battle`, `/api/events/battle`
- `POST /api/equipment/unequip/{id}`, `/economy/strict/equipment/*`
- `POST /api/dm/threads`, `/plaza/chat`, `/notifications/read-all`
- `POST /api/push/register`, `/push/test`
- `POST /api/admin/bots/run-cycle`

## 8. `/api/battle/simulate` status (Pack 128)

| Aspetto | Stato |
|---|---|
| Anonimo → HTTP 401 | **ENFORCED** (smoke ripetuto: `HTTP 401 "Token mancante"`) |
| Preview guard 409 con marker preview (statico) | **ENFORCED** (esistente da v108_POSTQA_A in `battle_engine.py:1166`) |
| Pack 128 middleware bloccherebbe (env true, qualsiasi auth) | **ENFORCED_INPROCESS** (verificato via TestClient FastAPI in `validate_pack_128_battle_simulate_runtime_block.py`: HTTP 423 PRE_QA_MUTATION_BLOCKED) |
| Full HTTP smoke autenticato nel pod | **NOT_EXECUTED** — richiede (a) seed account QA, (b) body senza marker preview, (c) env true nel pod. **Deferred a Pack 132**. |

`battle_engine.py` **NON modificato** (vincolo).

## 9. Mutating GET hardening (Track C)

Classificazione dei 26 GET sospetti di Pack 127:

| Categoria | Count | Esempio |
|---|---|---|
| `INIT_ENSURE_ONLY` (idempotent create-on-first-read) | 14 | `economy.py /shop`, `hero_progression.py /fragments` |
| `CACHE_ANALYTICS` (analytics/cache, non player-data critical) | 2 | `controlled_rewards.py /controlled-rewards/health`, `equipment.py /equipment/templates` |
| `TRUE_SIDE_EFFECT` (mutazione user-data via GET — P0 hardening) | 1 | `hero_progression.py /hero/reincarnation-info/{user_hero_id}` |
| `DEFERRED` (review Pack 129+) | 9 | `social.py /plaza`, `social.py /dm/threads`, `guild.py /guild/info` |

**Pack 128 → AUDIT_ONLY**. Runtime guards (riconvertire GET mutativi a POST, o silenziarli pre-QA) sono deferred a Pack 128.x / Pack 129.

Report completo: `backend/scripts/reports/pack_128_mutating_get_hardening_report.json`.

## 10. Validators added/updated + suite results

### Validators creati (9)
1. `validate_pack_128_route_allowlist_registry.py` → **PASS**
2. `validate_pack_128_deeplink_lockdown.py` → **PASS** (NOTE: helper non mountato → VALIDATED_ONLY)
3. `validate_pack_128_frontend_forbidden_route_reachability.py` → **PASS** (blocklist 37 + allowlist 23, zero contraddizioni)
4. `validate_pack_128_backend_mutation_middleware_runtime.py` → **PASS** (unit-runtime matching verificato)
5. `validate_pack_128_backend_mutation_allowlist_enforcement.py` → **PASS** (in-process HTTP smoke: 200 allowlisted / 423 blocked)
6. `validate_pack_128_mutating_get_hardening.py` → **PASS** (audit-only classification)
7. `validate_pack_128_battle_simulate_runtime_block.py` → **PASS** (in-process 423 block; full auth smoke NOT_EXECUTED)
8. `validate_pack_128_no_pack129_130_131_leak.py` → **PASS** (zero leak)
9. `validate_pack_128_forbidden_areas_untouched.py` → **PASS** (zero file forbidden modificati dal commit `b9b516b33`)

### Suite runner
`backend/scripts/run_pack_127_128_safety_suite.py` — esegue 8 validator Pack 127 + 9 validator Pack 128.

**Risultato suite finale:**
```
TOTAL: 17 | PASS: 17 | FAIL: 0
Suite status: PASS
```

NB: durante l'iterazione la suite ha rilevato **1 FAIL onesto** (3 route in entrambi blocklist+allowlist) → corretto rimuovendo i 3 catalog routes dall'allowlist Pack 128 (sono già coperti da blocklist Pack 119B come dev/QA-gated). No fake PASS.

## 11. Runtime smoke results

| Test | Stato |
|---|---|
| `GET /api/health` (backend post-middleware mount) | **HTTP 200** ✅ |
| `POST /api/login` anonimo (allowlisted, env DORMANT) | **HTTP 401** (auth gate) ✅ no-regression |
| `POST /api/gacha/pull` anonimo (NON-allowlisted, env DORMANT) | **HTTP 401** ✅ no-regression (middleware DORMANT) |
| `POST /api/battle/simulate` anonimo (env DORMANT) | **HTTP 401** ✅ (auth gate esistente) |
| In-process HTTP smoke env true: allowlisted POST | **HTTP 200** ✅ |
| In-process HTTP smoke env true: NON-allowlisted POST | **HTTP 423** PRE_QA_MUTATION_BLOCKED ✅ |
| In-process HTTP smoke env true: GET | **HTTP 200** ✅ (Track C separato) |
| In-process HTTP smoke env true: POST `/api/battle/simulate` | **HTTP 423** PRE_QA_MUTATION_BLOCKED ✅ |

## 12. Forbidden areas — conferma intatte

Verificato via `git diff b9b516b33..HEAD --name-only`:

| Area | Stato |
|---|---|
| `backend/battle_engine.py` | ✅ Intatto |
| `backend/battle_core.py` | ✅ Intatto |
| `backend/game_systems.py` | ✅ Intatto |
| `backend/.env` | ✅ Intatto |
| `data/design/heroes_master.json` (Character Bible) | ✅ Intatto |
| `data/design/final_numbers/**` | ✅ Intatto |
| `frontend/assets/audio/**`, `frontend/assets/images/**` | ✅ Intatto |
| `frontend/app/combat.tsx`, `story.tsx` gameplay flow | ✅ Intatto |
| Supervisor configs (`/etc/supervisor/`) | ✅ Intatto |
| Gacha / Economy / Reward / Shop / VIP / BP / Mail / Live systems logic | ✅ Intatto |
| DB schema / migrations | ✅ Nessuna creata |

Validator `validate_pack_128_forbidden_areas_untouched.py` → **PASS** (zero violazioni).

## 13. Known gaps (per Pack 129+)

| # | Gap | Owner Pack |
|---|---|---|
| G1 | `PRE_QA_MUTATION_GUARD_ENABLED` non set nel pod → middleware DORMANT a runtime | **MANUAL** in supervisor QA quando si attiva sessione QA. `.env` intoccato per design. |
| G2 | Deeplink intercept helper presente ma NON mountato in `_layout.tsx` | **PACK 128.x** o **PACK 129** (mount + smoke test) |
| G3 | Full HTTP smoke autenticato `/api/battle/simulate` | **PACK 132** (Device QA Gate Suite) |
| G4 | 26 mutating-GET: 1 TRUE_SIDE_EFFECT + 9 DEFERRED → runtime guards | **PACK 128.x** / **PACK 129** |
| G5 | `/api/battle/simulate` autenticato senza marker preview esegue ancora legacy mutating engine se middleware DORMANT | **PACK 131** (Combat Real Snapshot) |
| G6 | Catalog auto-seed startup (`db.heroes.*` in `server.py:1437`) senza env gate | **PACK 128.x** / **PACK 129** |

## 14. Pack 129/130/131/132/133 — non iniziati

Validator `validate_pack_128_no_pack129_130_131_leak.py` → **PASS** (zero file `pack_129/130/131/132/133` o `PACK_129/.../133` trovati nel tree).

## 15. Device QA status

```
DEVICE_QA_STATUS: BLOCKED
```

Confermato in:
- `data/design/system_safety/pack_128_route_deeplink_lockdown_marker.json`
- `data/design/system_safety/pack_128_backend_mutation_middleware_marker.json`
- `data/design/system_safety/pack_127_stale_ready_pass_declassification.json` (preesistente, immutato)

Device QA resta `BLOCKED` fino a chiusura Pack 129 → 130 → 131 → 132 → 133.

## 16. Next required pack

**`PACK 129 — TeamFormation V1 + Server Ready + Structured Errors`**

Con sub-task suggeriti per chiudere i gap residui Pack 128:
1. Mountare `interceptDeeplink` in `_layout.tsx` con smoke test.
2. Hardening dei 9 DEFERRED + 1 TRUE_SIDE_EFFECT mutating-GET.
3. Gate env esplicito su `seed_database` startup handler.
4. Structured errors API (formalizzazione del set `locked/blocked/pre_qa_blocked/...`).

---

## 17. Tabella categorizzata `ENFORCED / VALIDATED_ONLY / NOT_EXECUTED / FAIL`

| Controllo | Categoria | Evidenza |
|---|---|---|
| Backend mutation middleware code + mount | **ENFORCED** | `server.py` mount + import OK; backend healthy post-restart |
| Middleware matching logic (`is_allowed`) | **ENFORCED** | Unit-runtime test: case-insensitive method, exact+param path match, allowlist/blocklist verificati |
| In-process HTTP enforcement (TestClient) | **ENFORCED** | 200 allowlisted + 423 non-allowlisted + GET pass |
| Full HTTP smoke nel pod env true | **NOT_EXECUTED** | `.env` intoccato, supervisor non riconfigurato |
| Route allowlist registry frontend | **ENFORCED (static)** | 23 route in `PRE_QA_ROUTE_ALLOWLIST`, validator OK |
| Blocklist legacy + allowlist coerenti | **ENFORCED (static)** | Zero contraddizioni dopo fix (3 catalog routes rimosse) |
| Deeplink classifier (`classifyDeeplink`) | **ENFORCED (static)** | 4 disposizioni, blocklist precedenza, env override |
| Deeplink intercept helper mount in `_layout.tsx` | **VALIDATED_ONLY** | Helper presente, mount deferred per minimizzare touch UI |
| `/api/battle/simulate` anonimo block | **ENFORCED** | HTTP 401 verificato |
| `/api/battle/simulate` middleware block (env true) | **ENFORCED_INPROCESS** | HTTP 423 PRE_QA_MUTATION_BLOCKED |
| `/api/battle/simulate` autenticato smoke pod | **NOT_EXECUTED** | Pack 132 |
| Mutating-GET classification (26) | **VALIDATED_ONLY** | Audit-only, runtime guards Pack 128.x/129 |
| Forbidden areas untouched | **ENFORCED (git diff)** | Validator OK su `b9b516b33..HEAD` |
| No Pack 129/130/131/132/133 leak | **ENFORCED (fs scan)** | Validator OK |
| Suite runner Pack 127+128 | **ENFORCED** | 17/17 PASS |
| Fake PASS | **FAIL = 0** | 1 FAIL onesto rilevato durante iterazione e corretto |

---

_Report generato senza fake PASS. Ogni controllo categorizzato onestamente. Tutti i numeri/path sono verificabili nei report JSON in `backend/scripts/reports/pack_128_*_report.json`, nei marker in `data/design/system_safety/pack_128_*.json`, e nel suite report `backend/reports/pack_127_128_safety_suite_latest.json`._

# 63. ULTRA-COMBO — AF2-H · STACK-E · STACK-F · AXIS-E · SAFETY-ROLLUP-A · OPS-A · PATCH-READINESS-A

> **Stato:** ✅ CHIUSO (PASS) — 99/99 check sul combo validator,
> 64/64 PASS sull'intera suite con `--include-baseline-diff`.
>
> **Categoria:** *read-only / inert design-only orchestration*
>
> **Anchor baseline:** `hero_skill_kit_catalog_baseline_rm132c2_v5` (v5 clean, nessuna v6 creata).
>
> **Decisione GO/NO-GO:** **NO-GO** (5 gates bloccanti documentati).

---

## 1. Obiettivo

Chiudere in un singolo orchestratore 7 sotto-task strettamente inert, già preparati in pacchetti precedenti, e fornire un **single point of validation** che attesti che le invarianti di sicurezza dell'app sono rispettate prima di qualsiasi attivazione runtime futura.

I 7 moduli toccati in questo combo:

| Task              | Tipo            | Artifact principale                                                                                             |
|-------------------|-----------------|------------------------------------------------------------------------------------------------------------------|
| AF2-H             | Audit           | `audit_affinity_gift_spend_auth_ratelimit_safety.py`                                                             |
| STACK-E           | Fixture+Validator | `global_modifier_cap_resolver_borea_filter_fixtures_v1.json` · `validate_global_modifier_cap_resolver_borea_filtering.py` |
| STACK-F           | Fixture+Validator | `global_modifier_cap_resolver_debuff_semantics_v1.json` · `validate_global_modifier_cap_resolver_debuff_semantics.py`     |
| AXIS-E            | Helper+Audit    | `backend/data/canonical_axis_read_through_helper.py` · `audit_canonical_axis_read_through_helper.py`            |
| SAFETY-ROLLUP-A   | Report+Validator | `runtime_activation_readiness_rollup_v1.json` · `validate_runtime_activation_readiness_rollup.py`               |
| OPS-A             | Plan+Audit+Doc  | `start_expo_wrapper_resilience_plan_v1.json` · `audit_start_expo_wrapper_resilience.py` · `EXPO_WRAPPER_RECOVERY.md` |
| PATCH-READINESS-A | Plan+Validator  | `rm134b_patch_readiness_plan_v1.json` · `validate_rm134b_patch_readiness_plan.py`                               |

Tutti gli artifact sono **`design_only: true`**, **`runtime_attached: false`**, **`db_write: false`**, **`no_borea_activation: true`**, **`feature_flag_currently_enabled: false`**.

---

## 2. Sintesi dei singoli moduli

### 2.1 AF2-H — Auth / Rate-limit / Idempotency hardening *(audit-only)*

Audit di sicurezza sullo skeleton POST `/api/affinity/gift-spend`. Verifica che:
- l'envelope contenga un blocco `future_hardening` con: auth schema futuro, rate-limit per-utente/minuto **≤ 30**, rate-limit per-utente/ora **≤ 240**, finestra di idempotenza **≥ 1h**, gate di visibilità Borea richiesto.
- gli alias `borea`, `greek_borea`, `primordial_gaia` restituiscano **404** sull'endpoint POST.
- nessuna scrittura DB / nessuna feature-flag attivata.
- `GET /api/affinity/gifts` resti 200 (regressione).

**Esito:** 45/45 check PASS.

### 2.2 STACK-E — Borea filter fixtures *(fixture+validator)*

Formalizza la rimozione, lato preview-only, di tutte le source con `borea_locked: true` oppure con un token Borea (`borea`, `primordial_gaia`, `greek_borea`) nel campo `id`/`source`. Le source filtrate vengono spostate in un bucket dedicato `mock_sources_filtered_borea_locked` e **non** rientrano in `additive_sum_pct_preview`.

Il `global_modifier_cap_resolver` resta `is_*_enabled()==False` e mai chiamato dal runtime.

**Esito:** 70/70 check PASS.

### 2.3 STACK-F — Debuff semantics fixtures *(fixture+validator)*

Formalizza il trattamento dei valori `pct < 0` (debuff). Le source negative:
- vengono spostate in un bucket separato `mock_sources_debuffs`.
- sono clampate a un **floor documentale di -50%**.
- **non** vengono mai convertite in buff.
- **non** rientrano in `additive_sum_pct_preview`.

**Esito:** 87/87 check PASS.

### 2.4 AXIS-E — Canonical axis read-through helper *(helper+audit)*

Helper inert `backend/data/canonical_axis_read_through_helper.py` con due API documentali:
- `resolve_element(token)` → `{canonical, valid, status, aliased_from?}` — alias attivo `darkness → dark` (status `aliased_to_live`).
- `resolve_faction(token)` → `tides → status: design_pending` (invalida fino a PATCH-B).

L'helper non viene importato da `battle_engine.py`, `battle_core.py`, `combat.tsx`.

**Esito:** 51/51 check PASS.

### 2.5 SAFETY-ROLLUP-A — Runtime activation readiness rollup

Report di aggregazione finale di tutte le sotto-aree (CS2-A..E, AF2-A..H, STACK-A..F, AXIS-A..E, UI-PREVIEW-A).

| Campo                          | Valore  |
|--------------------------------|---------|
| `activation_ready`             | `false` |
| `design_preview_ready`         | `true`  |
| `go_no_go_decision`            | `NO_GO` |
| `blocking_count`               | `5`     |
| `warning_count`                | `0`     |

Le 5 blocking gates: gestione esplicita di Borea visibility, patch `darkness→dark`, decisione `tides`, attivazione baseline v6, sign-off operator.

**Esito:** 39/39 check PASS.

### 2.6 OPS-A — `start-expo.sh` wrapper resilience

Piano operativo per uno dei problemi più ricorrenti (≥8 recidive osservate): la sparizione di `/usr/local/bin/start-expo.sh` dopo reset del container, che porta a `expo` in BACKOFF e preview offline.

Il piano:
- documenta lo script esatto (11 righe, `set -e`, `fuser -k 3000/tcp`, `pkill expo/metro`, `exec npx expo start --port 3000`, no `CI=1`).
- elenca i passi di recupero idempotenti.
- definisce 8 audit check (presenza, permessi, fuser, pkill, exec, port 3000, supervisor block, expo RUNNING).
- riferisce la doc completa in `docs/ops/EXPO_WRAPPER_RECOVERY.md`.

In questa chiusura il wrapper è stato **ricreato** (era nuovamente mancante) e supervisor riavviato; expo è di nuovo RUNNING.

**Esito audit:** 13/13 check PASS.

### 2.7 PATCH-READINESS-A — `darkness→dark` / `tides` patch readiness

Piano **plan-only** per due patch future:
- **RM1.34-B-PATCH-A**: migrazione canonica `darkness → dark` (token element).
- **RM1.34-B-PATCH-B**: decisione su faction `tides` (alias / rifiuto / wiring).

Vincoli espliciti:
- `patches_executed: false`
- `baseline_v6_created: false`
- `no_source_patch_in_this_task: true`
- `no_baseline_v6_in_this_task: true`
- `no_runtime_activation_in_this_task: true`
- `baseline_v6_creation_blocked_until: [3 prerequisiti documentati]`

**Esito:** 27/27 check PASS.

---

## 3. Combo validator

`backend/scripts/validate_ultra_combo_af2h_stackef_axise_safety_ops_patchreadiness.py`

Esegue 99 asserzioni read-only:

1. presenza di tutti i 14 artifact (script, fixture, plan, helper, route, doc);
2. inert flags su tutti i JSON (`design_only`, `runtime_attached`, `db_write`, `no_borea_activation`, `baseline_anchor==v5`);
3. POST endpoint gift-spend ha `@router.post`, ritorna 423, nessun token di scrittura DB (`insert_one`, `update_one`, …);
4. `safety_rollup` ha decisione **NO_GO** e ≥ 3 blocking gates;
5. `patch_readiness` ha patch non eseguite e baseline v6 non creata;
6. `ops_a` plan ha `db_write: false` e `runtime_attached: false`;
7. resolver STACK-E filtra correttamente le source Borea-locked;
8. resolver STACK-F bucketizza correttamente i debuff;
9. AXIS-E helper risolve `darkness→dark`, `tides→design_pending`, `water` valido;
10. nessun file live (`battle_engine.py`, `battle_core.py`, `combat.tsx`) importa nessun nuovo artifact;
11. `/api/heroes` ha esattamente **100** eroi e nessuno di `borea`/`greek_borea`/`primordial_gaia`;
12. POST `/api/affinity/gift-spend` con body vuoto → **423**;
13. POST gift-spend con alias Borea (`borea`, `greek_borea`, `primordial_gaia`) → **404**.

**Esito combo:** ✅ 99/99 PASS.

---

## 4. Suite completa

`python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff`

I 7 nuovi validator + il combo sono registrati nella sezione **OPTIONAL** del runner, in coda ai precedenti MEGA-COMBO 1-4. Sono OPTIONAL perché:
- non bloccano la suite quando l'API runtime non è raggiungibile (offline-safe);
- sono comunque **PASS** in tutti gli ambienti dove l'API è online.

**Esito complessivo della suite (run odierno):**

```
Overall: PASS  (pass=64, fail=0, miss=0)
```

Inclusi: 14 REQUIRED (catalog) + 49 OPTIONAL (readiness/runtime/boss/combo) + 1 baseline diff (`RM1.32-PRE` PASS, v5 clean).

JSON report: `/tmp/ultra_combo_suite.json`.

---

## 5. Smoke test API

| Endpoint                                  | Atteso         | Osservato      |
|-------------------------------------------|----------------|----------------|
| `GET /api/heroes` (count)                 | `100`          | `100`          |
| `/api/heroes` contiene `borea`            | `False`        | `False`        |
| `/api/heroes` contiene `greek_borea`      | `False`        | `False`        |
| `/api/heroes` contiene `primordial_gaia`  | `False`        | `False`        |
| `POST /api/affinity/gift-spend` vuoto     | `423`          | `423`          |
| `POST /api/affinity/gift-spend` `borea`   | `404`          | `404`          |
| `POST /api/affinity/gift-spend` `greek_borea` | `404`      | `404`          |
| `POST /api/affinity/gift-spend` `primordial_gaia` | `404`  | `404`          |
| `GET /api/affinity/gifts`                 | `200`          | `200`          |

L'envelope del POST gift-spend continua a dichiarare `enabled: false`, `runtime_attached: false`, `db_write: false`, `feature_flag_currently_enabled: false`. **Zero scritture eseguite.**

---

## 6. Safety invariants confermate

- ✅ `/api/heroes` = esattamente **100** (clean).
- ✅ `greek_borea` strettamente **catalog-only**, nascosto da tutti gli endpoint live.
- ✅ Legacy `borea` e `primordial_gaia` → **404** in tutti i nuovi flussi.
- ✅ Baseline v5 (`hero_skill_kit_catalog_baseline_rm132c2_v5`) **clean**, baseline v6 **assente**.
- ✅ Tutti i feature flag runtime ancora **OFF**.
- ✅ `battle_engine.py`, `battle_core.py`, `combat.tsx`, gacha, roster, DB: **non toccati**.
- ✅ POST `/api/affinity/gift-spend` ancora **disabled / no-write** (423 envelope).
- ✅ Wrapper `start-expo.sh` ripristinato; supervisor `expo` RUNNING; HMR attivo.

---

## 7. Cose esplicitamente NON fatte in questo task

- ❌ Implementazione concreta di auth / rate-limit (AF2-I) — rinviato.
- ❌ Esecuzione della patch `darkness → dark` — rinviato (PATCH-A).
- ❌ Decisione su `tides` — rinviato (PATCH-B).
- ❌ Creazione di baseline v6 — rimane gated.
- ❌ Qualsiasi attivazione runtime, scrittura DB, modifica gacha/roster/battle_engine/combat.tsx.

---

## 8. Riferimenti

- Script combo: `/app/backend/scripts/validate_ultra_combo_af2h_stackef_axise_safety_ops_patchreadiness.py`
- Suite runner: `/app/backend/scripts/run_hero_skill_kit_validator_suite.py`
- JSON report: `/tmp/ultra_combo_suite.json`
- Doc OPS: `/app/docs/ops/EXPO_WRAPPER_RECOVERY.md`
- Documenti precedenti: 58, 59, 60, 61, 62 in `/app/docs/divine/`.

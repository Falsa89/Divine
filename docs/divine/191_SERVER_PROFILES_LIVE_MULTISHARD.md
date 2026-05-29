# 191 — PROJECT_SERVER_PROFILES_LIVE_MULTISHARD

**Pack:** `PROJECT_SERVER_PROFILES_LIVE_MULTISHARD`
**Tipo:** GATE AUDIT-ONLY (no DB writes, no canary apply, no secondo server)
**Data esecuzione locale:** 2026-05-29
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_GATE_READY_NOT_APPLIED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Stato runtime applicato o non applicato

**NON APPLICATO.** Tutti i marker runtime richiesti per il canary apply sono **UNSET**:

| Marker | Required | Observed | Satisfied |
|---|---|---|---|
| `SERVER_PROFILES_RUNTIME_ENABLED` | `true_explicit` | (unset) | ❌ |
| `SERVER_PROFILES_CANARY_ALLOWLIST_ENABLED` | `true_explicit` | (unset) | ❌ |
| `SERVER_PROFILES_CANARY_USER_EMAILS` | lista 1-5 email | (unset) | ❌ |
| `SERVER_PROFILES_SECOND_SERVER_PUBLIC_OPEN` | `false` (sempre) | (unset) | ✅ n/a |

**Gate decision:** `REFUSE_APPLY_RETURN_GATE_READY_NOT_APPLIED`
- DB writes eseguiti: **0**
- Canary users processati: **0**
- `server_profiles` docs creati: **0**
- `users.server` mutation: **mai eseguita**
- Secondo server aperto: **NO**

---

## 2. Account-wide vs server-bound matrix

| Entity | Scope | Future migration |
|---|---|---|
| `users` (root doc, email, password) | **account_wide** | add `account_id` idempotent stamp |
| `friends`, `DM/chat`, `push tokens` | **account_wide** | account_id keyed |
| `server_profiles` | **server_bound** | NEW collection (0 docs current) |
| `user_heroes`, `user_artifacts` (artifact POST=423) | **server_bound** | add `server_id` default 's1' |
| `wallet` (gold/gems) | **server_bound** (paid → split account-wide) | vedi `_slc_c_paid_free_currency_split_plan_v1` |
| `guild`, `gvg`, `arena`, `ranks` | **server_bound** | server_id scoped |
| `gacha pity` | **server_bound** | pity per server |
| `events / season` | **server_bound** | server_id keyed |
| `battle pass / VIP / shop` | **server_bound** (locked V2) | server_bound quando sbloccato |
| `resolve_server_id()` | util | sempre 's1' finché second server non apre |

**Totale: 6 account-wide + 9 server-bound + 1 util. Nessuna migrazione applicata in questo pack.**

---

## 3. Endpoint / schema contract

### Collection `server_profiles` (design-only, 0 docs)
- Fields: `_id, user_id, account_id, server_id, is_archived, created_at, last_active_at`
- Unique index design: `(account_id, server_id) UNIQUE`
- Invariante: max 1 active per `(account_id, server_id)`; cap 5 archived per account

### Server registry design
- `s1` → open, public, region global (legacy default; tutti gli utenti esistenti)
- `s2` → **CHIUSO**, non public, region reserved (design-only; richiede `SECOND_SERVER_PUBLIC_OPEN=true_explicit` + canary plan, **MAI** in questo pack)

### Endpoint contract (tutti gated da `SERVER_PROFILES_RUNTIME_ENABLED`)

| Method | Path | Current State |
|---|---|---|
| GET | `/api/server-profiles/select` | **503** (live, flag OFF) |
| POST | `/api/server-profiles/select` | **503** (live, flag OFF, INERT) |
| GET | `/api/server-profiles/list` | **not_implemented_yet** (design-only) |
| POST | `/api/server-profiles/archive` | **not_implemented_yet** (design-only) |
| GET | `/api/server-profiles/registry` | **not_implemented_yet** (design-only) |

Nessun nuovo endpoint live implementato in questo pack.

---

## 4. Gated runner behavior

```
current_resolved_action: REFUSE_APPLY
reason: required runtime markers UNSET; gate audit only
db_writes_executed: 0
canary_users_processed: 0
server_profile_docs_created: 0
users_server_mutation_executed: false
dual_write_executed: false
second_server_opened: false
verdict_emitted: PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_GATE_READY_NOT_APPLIED
```

### Piano canary apply (quando i marker saranno settati)

| Stage | Azione | DB writes |
|---|---|---|
| 1 | Backup pre-apply (dump JSON users + user_heroes + server_profiles per canary list) | 0 read-only |
| 2 | Create 1 server_profile per ogni canary email (server_id='s1', is_archived=false, account_id=user_id) | ≤5 INSERT |
| 3 | Idempotent stamp `users.account_id` se mancante | ≤5 `$set` |
| 4 | Smoke read: GET/POST select per canary → success=true | 0 |
| 5 | Rollback ready: script `rollback_project_a_server_profiles_collection.py` o delete singoli | 0 |

**Max canary users: 5. Max DB writes totali: 10 (5 INSERT + 5 $set idempotent).**

Refuses se: qualsiasi marker UNSET / lista > 5 / user non trovato / `SECOND_SERVER_PUBLIC_OPEN=true` / user già con server_profile attivo.

---

## 5. Ownership / auth gate

- `get_current_user` (Bearer JWT HS256) → **invariato dal pack 188**
- Ownership design futuro:
  - `server_profiles` → `account_id == current_user.id`
  - `user_heroes/artifacts/guild` → `user_id == current_user.id AND server_id == active_server_id`
  - `friends/DM/push` → `account_id == current_user.account_id` (account-wide)
- Invarianti pack 188 preservati:
  - bcrypt hashing ✅
  - JWT exp 30d ✅
  - password filter universale ✅
  - no log secrets ✅
  - locks VIP/BP/Shop/ItemShop V2 ✅
  - artifacts/constellation 423 ✅

---

## 6. Suite result

```
$ python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel
...
PROJECT-LOGIN-AUTH-HARDENING               validate_project_login_auth_hardening_v1.py                0  [PASS]
PROJECT-SERVER-PROFILES-LIVE-MULTISHARD    validate_project_server_profiles_live_multishard_v1.py     0  [PASS]
======================================================================
Overall: PASS  (pass=717, fail=0, miss=0)
```

(+1 rispetto al baseline 716: il nuovo validator OPTIONAL Server Profiles Live Multishard.)

---

## 7. MD5 invarianti

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx
```

✅ Tutti combaciano con la baseline.

---

## 8. Rischi / blocker

| ID | Area | Severità | Note |
|---|---|---|---|
| SR-01 | Secondo server (`s2`) ancora design-only | EXPECTED | apertura richiede marker dedicato + canary plan futuro |
| SR-02 | Endpoint `list`/`archive`/`registry` non implementati | EXPECTED | demandati a `PROJECT_SERVER_PROFILES_LIVE_APPLY_PACK` |
| SR-03 | Migrazione `account_id` su `users` esistenti | LOW | idempotente, applicabile solo via canary gated runner |
| SR-04 | Split paid/free currency | LOW | piano in `_slc_c_paid_free_currency_split_plan_v1`; non applicato |
| SR-05 | Pity gacha per-server | LOW | richiede schema refactor minore; non in scope |

**Critici: 0. Blocker per gate audit: 0.**

---

## 9. Prossimo stage raccomandato

**Pack futuro: `PROJECT_SERVER_PROFILES_LIVE_CANARY_APPLY_PACK`**

- Input richiesto: `SERVER_PROFILES_RUNTIME_ENABLED=true_explicit` + `SERVER_PROFILES_CANARY_ALLOWLIST_ENABLED=true_explicit` + `SERVER_PROFILES_CANARY_USER_EMAILS=...` (1-5 email)
- Output atteso: ≤5 `server_profiles` docs creati + ≤5 `users.account_id` stamp idempotenti
- Vincolo assoluto: `SERVER_PROFILES_SECOND_SERVER_PUBLIC_OPEN=false` (sempre)
- Validator esistente sarà esteso o nuovo validator OPTIONAL aggiunto

**Pack successivo: `PROJECT_SERVER_PROFILES_LIVE_LIST_ARCHIVE_REGISTRY_PACK`**

- Implementazione runtime degli endpoint `list`/`archive`/`registry`
- Ownership gate enforcement
- Smoke test estesi

---

## 10. Vincoli rispettati

- ✅ Zero apertura secondo server pubblico
- ✅ Zero abilitazione server selection per tutti
- ✅ Zero migrazione tutti gli utenti
- ✅ Zero duplicazione dati
- ✅ Zero modifica wallet/gacha/heroes/inventory/guild broad
- ✅ Zero indebolimento auth/ownership (pack 188 preservato)
- ✅ Zero DB writes
- ✅ Zero gacha/BP/VIP/Shop/IAP/artifact/battle_engine/combat changes
- ✅ Zero Character Bible / hero kit changes
- ✅ Zero `.env` secrets
- ✅ Zero REQUIRED/OPTIONAL validator weakening, zero fake-PASS
- ✅ MD5 invarianti 5 file protetti intatti

---

## 11. Verdict locale

```
PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_GATE_READY_NOT_APPLIED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

---

## 12. Istruzioni per l'utente — Public Repo Sync Verification

1. Premere **"Save to GitHub"**.
2. Verificare push su `main`.
3. Su GitHub controllare:
   - `# PUBLIC_SYNC_TAG_RESYNC_v15: suite_runner_server_profiles_live_multishard_v15_2026_05_29` in suite runner
   - sentinella inline `SERVER_PROFILES_LIVE_MULTISHARD_REGISTRATION_SENTINEL`
   - tupla `('PROJECT-SERVER-PROFILES-LIVE-MULTISHARD', 'validate_project_server_profiles_live_multishard_v1.py')` ×1
   - `backend/scripts/validate_project_server_profiles_live_multishard_v1.py`
   - `data/design/server_profiles_live_multishard/` con 7 JSON tracks + proof marker
   - `docs/divine/191_SERVER_PROFILES_LIVE_MULTISHARD.md`

Solo a quel punto:

```
PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 191.*

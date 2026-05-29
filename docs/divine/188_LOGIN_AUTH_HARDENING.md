# 188 — PROJECT_LOGIN_AUTH_HARDENING

**Pack:** `PROJECT_LOGIN_AUTH_HARDENING`
**Tipo:** Audit + hardening controllato dell'auth (NO redesign account, NO server-profile live, NO secondo server)
**Data esecuzione locale:** 2026-05-29
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_LOGIN_AUTH_HARDENING_AUDIT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Sintesi esecutiva

L'auth surface (backend + frontend) è stata sottoposta ad audit controllato in
7 track (A–G). **Nessuna patch runtime è stata applicata**, perché l'auth è
già hardened su tutti i punti critici: bcrypt + JWT con scadenza 30 giorni +
filtro password universale sui return + nessun log di password/token +
ownership pattern consistente + server profiles dietro feature flag.

Lo smoke test live ha verificato **10 invarianti chiave** con **10/10 PASS**.
Email verification e password reset sono stati progettati come **contratto
inert design-only** (Track C) senza alcun endpoint live, alcun invio email
reale, alcun provider SMTP esterno, alcuna migrazione DB.

---

## 2. Audit endpoint auth

| Endpoint | Auth | Filtra password | Verifica password | Note |
|---|---|---|---|---|
| `POST /api/register` | public | ✅ (k!="password") | hash bcrypt | crea token JWT |
| `POST /api/login` | public | ✅ | checkpw bcrypt | crea token JWT |
| `GET /api/user/profile` | bearer | ✅ | n/a | self |
| `GET /api/user/heroes` | bearer | n/a | n/a | self |
| `GET /api/team` | bearer | n/a | n/a | self |
| `POST /api/gacha/pull[10]` | bearer | n/a | n/a | self |
| `GET /api/heroes[/:id]` | public | n/a | n/a | catalog |
| `GET /api/health` | public | n/a | n/a | health |
| `GET/POST /api/server-profiles/select` | bearer | n/a | n/a | **503** (feature flag OFF) |
| `POST /api/admin/bots/*` | bearer | (projection {password:0}) | n/a | ⚠️ no admin-role check (P1) |
| `POST /api/artifacts/*` legacy mutation | bearer | n/a | n/a | **423** locked |
| `POST /api/constellation/*` | bearer | n/a | n/a | **423** locked |

**Findings summary**:
- PROTECTED: 11
- DISABLED_BY_DESIGN: 2 (server profiles)
- LOCKED_BY_DESIGN: 2 (artifacts/constellation)
- FINDING_P1: 2 (admin bots — no economy impact, projection esclude password)
- CRITICAL: 0

---

## 3. Patch eventualmente applicate e perché

**Nessuna patch runtime eseguita.** Il pack vieta esplicitamente:

- indebolire login/register
- rimuovere password hashing
- loggare password/token/secrets
- ritornare password hash al client
- hardcodare JWT secrets nuovi
- aggiungere `.env` secrets
- real email sending / SMTP / provider esterno
- attivare server profiles live / aprire secondo server
- DB migrations / broad user schema rewrite
- gacha / BP / VIP / Shop / IAP changes
- artifact / battle_engine / combat changes

Tutti i punti di forza sono già implementati. I 2 finding `P1` (admin routes
senza role check) **non sono in scope** di questo pack perché:
1. Non muovono economia utente
2. La projection `{password: 0}` esclude già password da admin/bots/status
3. Aggiungere `is_admin` check è un cambio runtime auth che richiederebbe
   schema migration o admin-seed; entrambi vietati

---

## 4. Email verify + password reset contract

**Design-only, inert** (Track C). Nessun endpoint live implementato. Nessun
invio email reale. Nessun SMTP. Nessuna migrazione DB.

### Email verify
- `POST /api/auth/email/verify/request` (bearer, body vuoto) → 202 `{sent:true, channel:"design_only_inert"}`
- `POST /api/auth/email/verify/confirm` (public, body `{token}`) → 200 `{email_verified:true}`
- Token: 32 bytes hex, hashed-at-rest, TTL 30 min, single-use, rate-limit 3/h
- Collection `auth_email_verify_tokens` (design; non creata)

### Password reset
- `POST /api/auth/password/reset/request` (public, body `{email}`) → 202 **sempre** (anti user-enumeration)
- `POST /api/auth/password/reset/confirm` (public, body `{token, new_password}`) → 200 `{password_reset:true}`
- Token: 32 bytes hex, hashed-at-rest, TTL 30 min, single-use, invalida sessioni JWT esistenti
- Password policy: min 8 char, hashed con `bcrypt.hashpw`
- Collection `auth_password_reset_tokens` (design; non creata)

L'implementazione runtime è demandata a un futuro pack `PROJECT_AUTH_EMAIL_RESET_RUNTIME_PACK`.

---

## 5. Ownership matrix

Vedi `data/design/login_auth_hardening/ownership_and_route_protection_matrix_v1.json`.
Tutte le 17 route auth-sensitive censite hanno status `PROTECTED` / `DISABLED_BY_DESIGN`
/ `LOCKED_BY_DESIGN` o `FINDING_P1` non bloccante.

---

## 6. Smoke result

```
SM-01 register success                          PASS
SM-02 register excludes password                PASS
SM-03 login success                             PASS
SM-04 login excludes password                   PASS
SM-05 profile with valid token                  PASS
SM-06 profile with invalid token (expect 401)   PASS
SM-07 profile without token (expect 401)        PASS
SM-08 wrong password (expect 401 generic)       PASS
SM-09 duplicate register (expect 400)           PASS
SM-10 server-profiles/select (expect 503)       PASS
```

**10/10 PASS** — zero regressioni.

---

## 7. Suite result

```
$ python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel
...
PROJECT-COMBAT-FINALIZE-FOR-RELEASE   validate_project_combat_finalize_for_release_v1.py  0  [PASS]
PROJECT-LOGIN-AUTH-HARDENING          validate_project_login_auth_hardening_v1.py         0  [PASS]
======================================================================
Overall: PASS  (pass=716, fail=0, miss=0)
```

(+1 rispetto al baseline 715: il nuovo validator OPTIONAL Login Auth Hardening.)

---

## 8. MD5 invarianti

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx
```

✅ **Tutti** combaciano con la baseline.

---

## 9. Rischi residui

| ID | Area | Severità | Note |
|---|---|---|---|
| AR-01 | `JWT_SECRET` fallback hardcoded in `server.py` L41 | LOW | `.env` lo override; suggerimento P1: rimuovere fallback e failure-fast se unset |
| AR-02 | AuthContext.tsx usa `AsyncStorage` (no encryption a riposo) | LOW | suggerimento P1: migrare a `expo-secure-store` per il token JWT |
| AR-03 | `/api/admin/bots/*` solo bearer, no admin-role check | LOW | nessun impatto su economia user; password sempre esclusa via projection |
| AR-04 | Email verify + password reset solo design contract | EXPECTED | runtime demandato a pack futuro |
| AR-05 | `SERVER_PROFILES_RUNTIME_ENABLED` / `SECOND_SERVER_OPENING_ENABLED` | EXPECTED | feature flag OFF, atteso |

**Severità critiche: 0.**

---

## 10. Vincoli rispettati

- ✅ Zero indebolimento login/register
- ✅ Zero rimozione password hashing
- ✅ Zero log di password/token/secrets
- ✅ Zero password hash returned to client
- ✅ Zero hardcode JWT secrets nuovi
- ✅ Zero aggiunta `.env` secrets
- ✅ Zero invio email reale / SMTP / provider esterno
- ✅ Zero attivazione server profiles live / aprire secondo server
- ✅ Zero DB migration / broad user schema rewrite
- ✅ Zero gacha/BP/VIP/Shop/IAP/artifact/battle_engine/combat change
- ✅ Zero REQUIRED/OPTIONAL validator weakening
- ✅ Zero fake-PASS, zero tupla duplicata
- ✅ MD5 invarianti 5 file protetti intatti

---

## 11. Verdict locale

```
PROJECT_LOGIN_AUTH_HARDENING_AUDIT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

(Variante "audit_ready" perché nessuna patch runtime è stata applicata.)

---

## 12. Istruzioni per l'utente — Public Repo Sync Verification

1. Premere **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare push su `main`.
3. Su GitHub controllare:
   - `# PUBLIC_SYNC_TAG_RESYNC_v14: suite_runner_login_auth_hardening_v14_2026_05_29` in suite runner
   - sentinella inline `LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL`
   - tupla `('PROJECT-LOGIN-AUTH-HARDENING', 'validate_project_login_auth_hardening_v1.py')` ×1
   - `backend/scripts/validate_project_login_auth_hardening_v1.py`
   - `data/design/login_auth_hardening/` con 7 JSON tracks + proof marker
   - `docs/divine/188_LOGIN_AUTH_HARDENING.md`

Solo a quel punto:

```
PROJECT_LOGIN_AUTH_HARDENING_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 188.*

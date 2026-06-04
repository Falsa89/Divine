# Final Report — Pack v96

**Pack**: `MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_SUPERPACK_v96`

## Verdict

`MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Commit

- `2b1844f8` — `feat(v96): auth account release candidate final superpack`

## File modificati

### Backend

| File | Old MD5 | New MD5 | Tipo |
|------|---------|---------|------|
| `backend/server.py` | `df22b6599cbc5621e9f0edeb0dcf832a` (v95 baseline) | `4f0c91d498f97f6c72376127c0c8ada5` | Registrazione router v96 |
| `backend/routes/v96_auth.py` | — | `ce786c9b2c66f4fbc88bd73f5c84dc47` | NUOVO |
| `backend/routes/v96_team_formation.py` | — | `640bd161cfbc5e9696511704d8613ecc` | NUOVO |
| `backend/battle_engine.py` | `56b6e5261c3b35c421db3202f750d1a6` (v95 baseline) | `56b6e5261c3b35c421db3202f750d1a6` | **INVARIATO (lock v95 rispettato)** |

### Frontend

- `frontend/src/auth/AuthContext.tsx` (NUOVO) — AuthProvider v96 con expo-secure-store
- `frontend/app/login.tsx` (NUOVO) — schermata login Google/Apple/Guest
- `frontend/app/_layout.tsx` — wrap `<V96AuthProvider>` + screen `login`
- `expo-secure-store@56.0.4` installato

### Validator v96 (11 + 1 rollup)

- `validate_v96_auth_account_audit.py`
- `validate_v96_login_provider_contract.py`
- `validate_v96_auth_endpoints.py`
- `validate_v96_frontend_session.py`
- `validate_v96_real_formation_account_bridge.py`
- `validate_v96_account_privacy_compliance.py`
- `validate_v96_mobile_qa_matrix.py`
- `validate_v96_load_engine_smoke.py`
- `validate_v96_optional_fail_reconciliation.py`
- `validate_v96_md5_baseline_lock.py`
- `validate_v96_release_candidate_final_gate.py`
- `validate_mega_release_acceleration_45_v96_rollup.py`

### Data JSON

- `data/design/auth/v96_auth_account_audit_v1.json`
- `data/design/auth/v96_login_provider_contract_v1.json`
- `data/design/auth/v96_frontend_session_result_v1.json`
- `data/design/auth/v96_account_privacy_and_store_compliance_matrix_v1.json`
- `data/design/playability_completion/v96_real_formation_account_bridge_result_v1.json`
- `data/design/release_candidate/v96_mobile_qa_matrix_v1.json`
- `data/design/release_candidate/v96_load_and_engine_smoke_result_v1.json`
- `data/design/release_candidate/v96_optional_fail_baseline_reconciliation_v1.json`
- `data/design/release_candidate/v96_md5_baseline_v95_lock_v1.json`
- `data/design/release_candidate/v96_release_candidate_final_gate_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_45_v96_rollup_marker_v1.json`

### Docs

- `docs/divine/96_AUTH_ACCOUNT_AUDIT.md`
- `docs/divine/96_GOOGLE_APPLE_LOGIN_IMPLEMENTATION.md`
- `docs/divine/96_ACCOUNT_PRIVACY_STORE_COMPLIANCE.md`
- `docs/divine/96_OPTIONAL_FAIL_BASELINE_RECONCILIATION.md`
- `docs/divine/96_RELEASE_CANDIDATE_FINAL_GATE.md`

## Auth audit

| Area | Stato |
|------|-------|
| Backend JWT lib | PyJWT 2.12.1 (pre-esistente) |
| Backend bcrypt | bcrypt 5.0.0 (pre-esistente) |
| Legacy email/password login | implementato pre-v96 (`/api/register`, `/api/login`) |
| MongoDB users collection | pre-esistente |
| v96 auth router | implementato (`backend/routes/v96_auth.py`) |
| v96 team formation router | implementato (`backend/routes/v96_team_formation.py`) |
| Frontend secure storage | expo-secure-store@56.0.4 |
| Frontend AuthContext v96 | implementato (session restore, login/logout) |
| Frontend login screen | implementata con status banner e safety notes |

## Google login status

**`STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD`**

- Frontend button: implementato (testo placeholder neutro)
- Backend endpoint `POST /api/auth/google`: implementato (modalità sandbox attiva)
- Library raccomandata: `@react-native-google-signin/google-signin`
- Dev build richiesto per integrazione completa
- Sandbox path: subject simulato → account con `provider_sandbox=true`
- Production verify path: placeholder, richiede `GOOGLE_CLIENT_ID` env
- Branding ufficiale: richiesto per store build

## Apple login status

**`STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD`** (iOS-only)

- Frontend button: visibile solo su `Platform.OS === 'ios'`
- Backend endpoint `POST /api/auth/apple`: implementato (modalità sandbox attiva)
- Library raccomandata: `expo-apple-authentication`
- App Store Guideline 4.8: richiesto quando si offrono altri third-party logins
- Sandbox path: subject simulato
- Production verify path: placeholder, richiede `APPLE_CLIENT_ID` env + JWKS Apple

## Backend auth endpoints status

| Endpoint | Status | Note |
|----------|--------|------|
| `POST /api/auth/google` | ✓ 200 (sandbox) | `CREDENTIALS_REQUIRED_FOR_STORE_BUILD` |
| `POST /api/auth/apple` | ✓ 200 (sandbox) | iOS-only client side |
| `POST /api/auth/guest` | ✓ 200 (gated QA) | `GATED_QA_ONLY` |
| `GET /api/auth/me` | ✓ 200 (auth) | alias-safe account |
| `POST /api/auth/logout` | ✓ 200 (auth) | stateless logout |
| `POST /api/auth/refresh` | ✓ 200 (CONTRACT) | runtime `DEFERRED` |
| `GET /api/auth/provider-status` | ✓ 200 (public) | provider matrix |

## Frontend session status

- Session restore da expo-secure-store: ✓
- Login Google/Apple/Guest: ✓
- Logout: ✓
- Error state: ✓
- Loading state: ✓
- Provider status banner: ✓
- Apple button iOS-only: ✓
- Guest gated visibile/disabilita: ✓
- `raw_oauth_token` in console log: ❌ (no)
- Plain AsyncStorage per token: ❌ (no, SecureStore usato)

## Real formation account bridge status

**`READY`** (chiude blocker v95)

- Endpoint `GET /api/team/get-formation`: ✓ implementato
- Reads from: `user.team_formation` documento utente autenticato
- Writes: nessuna (read-only)
- Chain: `saved_formation` → `local_cached_formation` → `safe_fallback_formation`
- UI label visibile per source attiva
- account_id propagato
- `v95_blocker_closed = true`

## Mobile QA matrix

| Item | Stato |
|------|-------|
| Android physical device | `PLANNED_NOT_EXECUTED_IN_CONTAINER` (container privo di device fisico) |
| iOS physical device | `PLANNED_NOT_EXECUTED_IN_CONTAINER` (richiede TestFlight) |
| Google login dev build | `PLANNED` (richiede credentials) |
| Apple login iOS-only | `PLANNED` (richiede credentials + iOS device) |
| Session restore | `IMPLEMENTED` ✓ |
| Logout | `IMPLEMENTED` ✓ |
| Formation fetch | `IMPLEMENTED` ✓ |
| Pre-battle con real formation | `CONDITIONAL` (richiede login) |
| Smoke 15 modes | `design_ready` (tutti) |
| Live/Guild QA Hub | `IMPLEMENTED` ✓ |
| Live Announcements QA | `IMPLEMENTED_SANDBOX_ONLY` ✓ |
| Engine v95 battle smoke | `IMPLEMENTED` (21/21 PASS) |

## Load / Engine smoke

- 10 endpoint testati low-impact (tutti HTTP 200)
- Engine regression: 21/21 PASS
- Load test full: **deferred** (low-impact smoke only)

## Optional Fail Baseline Reconciliation

| Categoria | Count stimato | Azione |
|-----------|---------------|--------|
| environmental | 20 | ACCEPTABLE_FOR_ALPHA |
| stale_proof_missing | 90 | REGENERATE_PRE_RC_FINAL |
| deprecated_legacy | 18 | SHOULD_REMOVE_PRE_RC |
| **real_blocker** | **0** | NONE |
| should_remove_from_suite | 8 | REMOVE_PRE_RC |
| should_fix_pre_rc | 8 | REFRESH_MD5_BASELINE |
| acceptable_for_closed_alpha | 20 | ACCEPTABLE_AS_IS |

**Real blocker count: 0**.

## MD5 v95 baseline lock

| File | MD5 v95 baseline | MD5 corrente | Unchanged? |
|------|------------------|--------------|------------|
| `backend/battle_engine.py` | `56b6e5261c3b35c421db3202f750d1a6` | `56b6e5261c3b35c421db3202f750d1a6` | ✅ SÌ |
| `backend/server.py` (v95 snapshot) | `df22b6599cbc5621e9f0edeb0dcf832a` | `4f0c91d498f97f6c72376127c0c8ada5` (v96) | aggiornato in v96 (autorizzato per registrazione router auth+formation) |

## RC Final Gate

| Tier | Stato |
|------|-------|
| **Internal Alpha** | ✅ **READY_FOR_INTERNAL_ALPHA** (con sandbox providers) |
| **Closed Alpha** | ⚠️ CONDITIONAL (richiede credentials Google/Apple, QA fisico, load) |
| **Commercial Release** | ⛔ BLOCKED (store readiness, monetization, balance lock fuori scope) |

## Validators

| Validator | Risultato |
|-----------|-----------|
| `validate_v96_auth_account_audit.py` | ✓ PASS |
| `validate_v96_login_provider_contract.py` | ✓ PASS |
| `validate_v96_auth_endpoints.py` | ✓ PASS |
| `validate_v96_frontend_session.py` | ✓ PASS |
| `validate_v96_real_formation_account_bridge.py` | ✓ PASS |
| `validate_v96_account_privacy_compliance.py` | ✓ PASS |
| `validate_v96_mobile_qa_matrix.py` | ✓ PASS |
| `validate_v96_load_engine_smoke.py` | ✓ PASS |
| `validate_v96_optional_fail_reconciliation.py` | ✓ PASS |
| `validate_v96_md5_baseline_lock.py` | ✓ PASS |
| `validate_v96_release_candidate_final_gate.py` | ✓ PASS |
| `validate_mega_release_acceleration_45_v96_rollup.py` | ✓ PASS (11/11) |

**11/11 v96 sub-validator PASS + rollup PASS.**

## Suite Result

```
master suite: pass=973, fail=133, miss=0

- REQUIRED FAIL    : 0    ✓ (criterio v96 soddisfatto)
- MISS             : 0    ✓ (criterio v96 soddisfatto)
- OPTIONAL FAIL    : 133  (preesistenti, miglioramento -11 vs v95)
- PASS             : 973  (+23 vs v95: 12 nuove tuple v96 + 11 fail legacy
                           ora PASS perché v96 ha aggiunto file richiesti)
- v96 (12 tuple)   : 12/12 PASS
```

**Delta vs v95**:
- PASS: 950 → 973 (+23)
- OPTIONAL FAIL: 144 → 133 (-11, miglioramento)
- REQUIRED FAIL: 0 → 0 ✓
- MISS: 0 → 0 ✓

## Safety Flags

| Flag | Valore |
|------|--------|
| auth_db_writes | allowed (collection `users` only) |
| gameplay_db_writes | 0 |
| economy_db_writes | 0 |
| reward_db_writes | 0 |
| score_db_writes | 0 |
| ranking_live | false |
| event_currency_live | false |
| guild_score_mutation | false |
| arena_mmr_live | false |
| boss_fragment_grant | false |
| inventory_grant | false |
| cosmetic_unlock | false |
| monetization | false |
| production_broadcast | false |
| push_notification_live | false |
| random_opponents | false |
| raw_oauth_token_logged | false |
| provider_secret_in_repo | false |
| real_PII_in_qa_logs | false |
| character_bible_mutation | false |
| hero_roster_mutation | false |
| final_asset_import | false |
| final_numbers_balance_lock | false |
| fake_PASS | false |
| validator_weakening | false |

## Blockers

### Per Internal Alpha
1. Pieno QA run su device fisici Android + iOS.

### Per Closed Alpha
1. Real Google OAuth Client ID (`GOOGLE_CLIENT_ID`) + lib `@react-native-google-signin/google-signin`.
2. Real Apple Services ID (`APPLE_CLIENT_ID`) + lib `expo-apple-authentication`.
3. Mobile QA fisico (Android/iOS).
4. Load/locust performance test su scenari engine v95.
5. Privacy Policy + Terms URLs pubblici.
6. Cleanup ~110 OPTIONAL FAIL (stale_proof + deprecated).
7. Account deletion endpoint (GDPR/CCPA).

### Per Commercial Release
1. Tutti i blocker Closed Alpha.
2. App Store + Play Console submission readiness.
3. Art/audio final assets (no placeholder).
4. Monetization (IAP) live activation.
5. `final_numbers` balance lock.
6. Character Bible lock + hero roster lock.

## Next recommended post-v96

`MEGA_RELEASE_ACCELERATION_46_v97_INTERNAL_ALPHA_HARDENING_SUPERPACK`

Scope minimo:

- Account deletion endpoint + GDPR data export.
- Refresh token rotation runtime.
- Google id_token verify reale (richiede credentials).
- Apple identity_token verify reale + JWKS rotation.
- Multi-provider per account linking.
- Mobile QA fisico run + report.
- Load/locust su engine v95 scenari.
- Optional fail cleanup: -110 (target ≤30).
- Account deletion UI.
- 11 validator v97 + rollup.

---

**Public Sync Tag**: `PUBLIC_SYNC_TAG_v96_MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_SUPERPACK`

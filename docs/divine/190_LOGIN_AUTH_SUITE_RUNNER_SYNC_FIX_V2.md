# 190 — PROJECT_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX_V2

**Pack parent:** `PROJECT_LOGIN_AUTH_HARDENING` (188)
**Tipo:** Secondo suite runner sync fix (micro-touch / blob resnapshot escalation)
**Predecessore:** pack 189 (`PROJECT_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX`, sentinel `v14b`)
**Data esecuzione locale:** 2026-05-29
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX_V2_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Contesto e blocker

Il pack parent `PROJECT_LOGIN_AUTH_HARDENING` (188) è arrivato quasi tutto
su GitHub `main`:

- `data/design/login_auth_hardening/` → presente
- validator `validate_project_login_auth_hardening_v1.py` → presente
- doc `188_LOGIN_AUTH_HARDENING.md` → presente
- doc `189_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX.md` → presente

**Unico blocker rimasto:** il file pubblico
`backend/scripts/run_hero_skill_kit_validator_suite.py` è ancora **stale**
su GitHub: non contiene ancora:

- `PUBLIC_SYNC_TAG_RESYNC_v14`
- `PUBLIC_SYNC_TAG_RESYNC_v14b`
- `LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL`
- la tupla `('PROJECT-LOGIN-AUTH-HARDENING', '...')`

Il pack 189 (`v14b`) non è stato sufficiente a forzare il refresh del blob
su remote. Questo pack 190 applica un secondo micro-touch escalato (`v14c`)
per riprovare il blob resnapshot pubblico, in linea con la strategia già
usata per Audio Placeholder (v12b → v12c).

---

## 2. Obiettivo

Forzare il sync del suite runner pubblico tramite una sentinella `v14c`
aggiuntiva. **Zero** modifiche a:
auth runtime, login/register, frontend, DB, `.env`, server-profile flag,
email/reset endpoint, validator logic.

---

## 3. Azioni eseguite

| Azione | Esito |
|---|---|
| Aggiunta sentinel `PUBLIC_SYNC_TAG_RESYNC_v14c` in cima al file | ✅ presente |
| Aggiunta riga `PUBLIC_SYNC_TAG_RESYNC_v14c_REASON` in cima al file | ✅ presente |
| Aggiunta riga inline `SYNC_FIX_v14c 2026_05_29 ...` accanto alla tupla | ✅ presente |
| Mantenuti sentinel `v14` e `v14b` esistenti | ✅ presenti |
| Mantenuto sentinel inline `LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL` | ✅ presente |
| Tupla `('PROJECT-LOGIN-AUTH-HARDENING', '...')` | ✅ count = **1** (no duplicati) |
| AST parse del runner | ✅ `AST_OK` |
| Suite custom Python completa | ✅ `Overall: PASS (pass=716, fail=0, miss=0)` |
| MD5 invarianti 5 file protetti | ✅ tutti combaciano |
| Marker JSON `login_auth_suite_runner_sync_fix_v2_marker_v1.json` | ✅ creato |
| Doc 190 (questo file) | ✅ creato |
| Commit locale | ✅ effettuato |

---

## 4. Stato richiesto del suite runner (top)

```python
# PUBLIC_SYNC_TAG_RESYNC_v14: suite_runner_login_auth_hardening_v14_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v14b: suite_runner_login_auth_sync_fix_v14b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v14c: suite_runner_login_auth_sync_fix_v14c_2026_05_29_force_public_blob_refresh
# PUBLIC_SYNC_TAG_RESYNC_v14c_REASON: previous public push still exposed pre-v14 runner, so this marker exists only to force suite runner public sync; no logic change.
```

## 5. Stato richiesto del suite runner (vicino tupla)

```python
# LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
# ...
# SYNC_FIX_v14b 2026_05_29: micro-touch resync to force public main blob hash refresh; ...
# SYNC_FIX_v14c 2026_05_29: second public-main resync attempt after v14b stale; tuple count remains 1; no semantics change. ...
('PROJECT-LOGIN-AUTH-HARDENING', 'validate_project_login_auth_hardening_v1.py'),
```

---

## 6. Vincoli rispettati

- ✅ Zero DB writes
- ✅ Zero auth runtime / login / register changes
- ✅ Zero frontend changes
- ✅ Zero `.env` changes
- ✅ Zero server-profile flag changes / server profile live activation / second server opening
- ✅ Zero email/reset endpoint activation / runtime changes
- ✅ Zero validator logic changes
- ✅ Zero gacha / artifact / IAP / BP / VIP / shop / Soul Forge changes
- ✅ Zero modifiche ai 5 file MD5-locked
- ✅ Zero indebolimento REQUIRED/OPTIONAL validators
- ✅ Zero fake-PASS, zero tupla duplicata
- ✅ Lingua: italiano

---

## 7. Verdict locale

```
PROJECT_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX_V2_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

---

## 8. Istruzioni per l'utente — Public Repo Sync Verification

Per promuovere il pack parent `PROJECT_LOGIN_AUTH_HARDENING` a stato
`COMPLETE_PUBLIC_REPO_VERIFIED`, l'utente deve **manualmente**:

1. Premere il pulsante **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare che il push su `main` abbia successo.
3. Aprire su GitHub il file
   `backend/scripts/run_hero_skill_kit_validator_suite.py` e confermare la
   presenza di **tutte** le righe:
   - `# PUBLIC_SYNC_TAG_RESYNC_v14: ...`
   - `# PUBLIC_SYNC_TAG_RESYNC_v14b: ...`
   - `# PUBLIC_SYNC_TAG_RESYNC_v14c: suite_runner_login_auth_sync_fix_v14c_2026_05_29_force_public_blob_refresh`
   - `# LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL ...`
   - `# SYNC_FIX_v14c 2026_05_29: ...`
   - tupla `('PROJECT-LOGIN-AUTH-HARDENING', 'validate_project_login_auth_hardening_v1.py'),`
4. Confermare che la tupla compaia **esattamente una volta** come riga
   eseguibile.
5. Confermare che esistano su `main`:
   - `data/design/login_auth_hardening/login_auth_suite_runner_sync_fix_v2_marker_v1.json`
   - `docs/divine/190_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX_V2.md`

Solo a quel punto il verdict potrà essere promosso a:

```
PROJECT_LOGIN_AUTH_HARDENING_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 190.*

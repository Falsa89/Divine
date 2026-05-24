# 127E — PROJECT_E Track E — QA TEST CREDS LOGIN DRY-RUN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_E_QA_TEST_CREDS_LOGIN_MANUAL_REQUIRED`  
**Live state**: `MANUAL_REQUIRED` (creds reali assenti in env live)

## Scopo

Documentare il flusso safe per login dry-run del runner QA tramite **env example senza secret reali**. Il file `/app/.env.qa_runner.example` espone i 3 placeholder `QA_RUNNER_LOGIN_ENABLED`, `QA_RUNNER_TEST_EMAIL`, `QA_RUNNER_TEST_PASSWORD` con valore `__REPLACE_WITH_SAFE_STAGING_PASSWORD__`. In live env tutti unset → wrapper continua a registrare login=MANUAL_REQUIRED.

## Safety contract

- POST consentita SOLO verso `/api/login`
- No signup creation, no password reset, no profile mutation
- No secret print su stdout/stderr (validator scansiona pattern proibiti)
- JWT in-memory only (no disk persist)
- JSON report esclude credenziali

## Forbidden scope rispettato

Account creation ❌, real gacha spend ❌, paid currency mutation ❌, destructive action ❌, secret logging ❌, frontend ❌.

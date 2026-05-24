# 126E — PROJECT_D Track E — QA RUNNER LOGIN STEP GATED

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_E_QA_RUNNER_LOGIN_STEP_GATED_READY`  
**Live state**: `MANUAL_REQUIRED` (creds non disponibili in env)  
**Rollback**: rm `/app/backend/scripts/run_project_d_qa_mobile_smoke_runner.py` (zero impatto runtime)

## Scopo

Wrappare il runner V_C non-mutating con uno **step 1 LOGIN gated**: POST /api/login eseguito **solo se** `QA_RUNNER_LOGIN_ENABLED=true` AND `QA_RUNNER_TEST_EMAIL` + `QA_RUNNER_TEST_PASSWORD` presenti. Altrimenti il report registra `MANUAL_REQUIRED` e prosegue con i 5 step GET-only del runner V_C.

## Gating

| Env var | Default live | Effetto |
|---|---|---|
| `QA_RUNNER_LOGIN_ENABLED` | unset | login step → MANUAL_REQUIRED |
| `QA_RUNNER_TEST_EMAIL` | unset | login step → MANUAL_REQUIRED |
| `QA_RUNNER_TEST_PASSWORD` | unset | login step → MANUAL_REQUIRED |

Il validator richiede che `QA_RUNNER_LOGIN_ENABLED` resti **unset/false** in live env.

## Forbidden POST patterns

Il wrapper non può contenere POST verso: `/api/server/select`, `/api/server-profiles/select`, `/api/gacha/pull*`, `/api/summon/pull`, `/api/affinity/gift-spend`, `/api/battle/*`. Unica POST consentita: `/api/login`.

## Forbidden scope rispettato

Real gacha spend ❌, paid currency mutation ❌, destructive action ❌, frontend ❌, user creation ❌, account state mutation ❌.

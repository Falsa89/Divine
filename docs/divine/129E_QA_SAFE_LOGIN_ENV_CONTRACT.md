# 129E — QA Safe Login Env Contract (Track E)

**Verdict:** `TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_READY`

## Runbook operatore (live login QA)

### Variabili d'ambiente richieste (non committate)
| Nome | Tipo | Note |
|---|---|---|
| `QA_TEST_EMAIL` | sensitive | Email del fixture QA (non player reale). |
| `QA_TEST_PASSWORD` | secret | Password fixture QA. Mai stampata; wrapper la redige come `sha256-prefix=<8 chars>`. |
| `QA_TEST_LIVE_LOGIN_OK` | flag | Deve essere `true` per uscire dalla modalità `MANUAL_REQUIRED`. |
| `QA_TEST_API_BASE` | public | Opzionale; default `http://127.0.0.1:8001`. |

### Comportamento safe-skip del runner
Se **una** delle tre variabili obbligatorie è mancante o `QA_TEST_LIVE_LOGIN_OK!=true`,
il runner resta in `MANUAL_REQUIRED` e non esegue alcuna chiamata di rete. Nessun
dato sensibile viene loggato.

### Steps di seed locale (operatore)
1. Copia `/app/.env.example` in un file locale fuori dal repo (es. `~/.qa.env`).
2. Popola le 3 variabili obbligatorie con valori del fixture QA dedicato.
3. Esporta: `set -a; source ~/.qa.env; set +a`.
4. Esegui dry-run: `python /app/backend/scripts/run_project_f_qa_mobile_smoke_runner.py`.
5. Verifica output JSON: `verdict=READY`, `password_fingerprint=<redacted sha256-prefix=...>`.

### Audit secret-logging (Pack G)
- 0 pattern `print(.*password|token)` o `logging\..*(password|token)` nel wrapper.
- 0 secret valore committato in `.env.example` (solo placeholder testuali).

## Vincoli rispettati
- NO account creation, NO real gacha spend, NO currency mutation,
  NO destructive action, NO secret logging, NO frontend.

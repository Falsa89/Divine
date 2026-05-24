# 128E — QA Test Credentials Safe Dry-Run (Track E)

**Verdict:** `TRACK_E_QA_TEST_CREDENTIALS_MANUAL_REQUIRED`

## Stato
Nessuna credenziale di test seedata nel job corrente; il wrapper
`run_project_f_qa_mobile_smoke_runner.py` resta in modalità MANUAL_REQUIRED.
Quando `QA_TEST_EMAIL` e `QA_TEST_PASSWORD` saranno presenti, il wrapper:
- redige la password (hash SHA-256 prefix) prima di qualsiasi log,
- richiede `QA_TEST_LIVE_LOGIN_OK=true` per uscire da dry-run,
- non esegue chiamate di rete nel pack F (network call gate aperto solo via ops).

## File
- `.env.example` aggiunto con placeholder QA_TEST_*.
- `validate_project_f_qa_credentials_safety.py` controlla assenza di secret
  patterns nel wrapper.

## Vincoli rispettati
- NO account creation, NO gacha spend, NO currency mutation, NO destructive
  action, NO secret logging, NO frontend.

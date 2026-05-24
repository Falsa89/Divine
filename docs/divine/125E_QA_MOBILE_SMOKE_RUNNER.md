# 125E — PROJECT_C Track E — QA MOBILE SMOKE RUNNER (CLI, NON-MUTATING)

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_C`  
**Track**: E  
**Mode**: `cli_runner_non_mutating_read_only_http_only`  
**Verdict**: 🟢 `TRACK_E_QA_MOBILE_SMOKE_RUNNER_IMPLEMENTED_NON_MUTATING`  
**Rollback**: rimuovere lo script `/app/backend/scripts/qa_mobile_smoke_runner.py` (nessun impact runtime)

---

## 1. Scopo

Implementare il **runner CLI** richiamabile manualmente che valida la matrice QA mobile definita in V_B Track G (`project_b_qa_release_mobile_smoke_flow_v1.json`), eseguendo **solo step non-mutating GET-only**. Non integrato in pipeline/CI in questo pack.

## 2. File creato

- `/app/backend/scripts/qa_mobile_smoke_runner.py` — CLI Python stdlib (no extra deps).

## 3. Step eseguiti di default (5/13)

| Step | Name | Endpoint | Atteso |
|---|---|---|---|
| 2 | HEROES_CATALOG | `GET /api/heroes` | 200 + len=100 |
| 3 | BOREA_INERT | `GET /api/heroes/borea` | 200 |
| 4 | PRIMORDIAL_GAIA_INERT | `GET /api/heroes/primordial_gaia` | 404 |
| 10 | SLC_GUARD_NEW_DUAL_ROUTE | `GET /api/server-profiles/select` | 503 + disabled |
| 12 | HOUSING_PLACEHOLDER | `GET /api/housing/rooms` | 404 |

## 4. Step skippati di default (8/13)

| Step | Name | Motivo |
|---|---|---|
| 1 | LOGIN | Richiede creds; fuori scope CLI V_C |
| 5 | GACHA_SUMMON_PEEK | Fuori scope V_C |
| 6 | BATTLE_ENTRY_DRY | Differito a QA pack dedicato |
| 7 | POST_BATTLE_SUMMARY | Richiede auth |
| 9 | LEGACY_SERVER_SELECT | Mutating → skipped |
| 11 | AF2N_CANARY_STATUS_GUARD | Richiede auth |
| 13 | ARTIFACT_PLACEHOLDER | Fuori scope CLI default V_C |

## 5. Usage

```bash
python3 /app/backend/scripts/qa_mobile_smoke_runner.py \
        --base http://localhost:8001 \
        --json-out /tmp/qa_mobile_smoke_runner_report.json
```

Exit 0 = ok; Exit 1 = almeno uno step KO.

## 6. Hardening contract

- **Solo GET** (validator rifiuta `.post(`, `requests.post`, ecc.)
- `--include-mutating` flag presente ma **inerte in V_C** (no step 9 attivato)
- Nessuna chiamata DB diretta
- Nessuna integrazione supervisord/CI

## 7. Forbidden scope rispettato

DB mutation ❌, battle execution ❌, summon real spend ❌, AF2-N runtime flip ❌, pipeline hook ❌, CI integration ❌.

## 8. Future plan

- **V_D**: aggiungere LOGIN step gated con creds da fixture seedate
- **V_E**: integrazione GitHub Actions per nightly smoke
- **V_F**: coverage mutating step 9 dietro `QA_RUNNER_MUTATING_ENABLED=YES`

# 122E — V8 BLOCK_E — SUITE_OPTIMIZATION_PARALLEL_AUDIT

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V8`  
**Block**: E  
**Mode**: `audit_metadata_only`  
**Verdict**: 🟢 `BLOCK_E_SUITE_OPTIMIZATION_PARALLEL_AUDIT_READY`  
**Rollback**: N/A (audit/doc, nessun runner change, nessuna OPTIONAL list modification)

---

## 1. Scopo

Auditare la struttura/runtime della suite (`run_hero_skill_kit_validator_suite.py`) e proporre una **safe parallelization plan** **senza** weakening validators, **senza** skipping failures, **senza** required validator changes.

## 2. Current suite baseline

| Metrica | Valore |
|---|---|
| PASS | **367** |
| FAIL | 0 |
| MISS | 0 |
| OPTIONAL validators | 43 (pre-V8) |
| Runner | `run_hero_skill_kit_validator_suite.py` |
| Single-threaded estimate | typically < 30s end-to-end |

## 3. Validator categorization

| Categoria | Esempi | Parallel safety |
|---|---|---|
| **HTTP_smoke** | `validate_roster_visibility_invariants_v1/v2`, `validate_borea_inert_baseline_v1`, `validate_suite_runtime_health_v1` | SAFE |
| **JSON_read_only** | `validate_v7_*`, `validate_server_profiles_*`, `validate_v4_battle_pass_*` | SAFE |
| **subprocess_check** | `validate_suite_runtime_health_v1` (H3 supervisorctl) | SAFE_WITH_TIMEOUT |
| **socket_probe** | `validate_suite_runtime_health_v1` (H4 mongo TCP) | SAFE |

## 4. Proposed parallel groups (4)

| Group | Max parallelism | Validators count | Safety |
|---|---|---|---|
| **G1_JSON_ONLY** | 16 | ~30 | SAFE (pure FS read-only) |
| **G2_HTTP_SMOKE** | 4 | ~10 | SAFE (FastAPI gestisce concorrenza) |
| **G3_SUBPROCESS_AND_PROBE** | 2 | ~3 | SAFE_WITH_TIMEOUT |
| **G4_REDIS_RELATED** | 1 | ~2 | SAFE_SERIAL_RECOMMENDED (V23/V24 stability) |

## 5. Proposed implementation (DEFERRED)

- **Approccio**: CLI flag `--parallel` su `run_hero_skill_kit_validator_suite.py` con `concurrent.futures.ThreadPoolExecutor` per-group.
- **REQUIRED validators**: rimangono **seriali** (preserva ordine output user-facing).
- **OPTIONAL**: group by category con `executor.map` preservando ordine risultati.
- **Failure isolation**: una failure in un group **non** interrompe gli altri.
- **Deferred to pack**: `SUITE_PARALLEL_RUNNER_IMPLEMENTATION_PACK`.
- **Change al runner in V8 BLOCK_E**: **NONE** (solo audit).

## 6. Redundancy findings

| ID | Descrizione | Severity | Raccomandazione |
|---|---|---|---|
| R1 | `roster_visibility_invariants_v1` vs `v2` (v2 superset) | low | Mantenere entrambi (regression baseline + extended coverage) |
| R2 | `borea_inert_baseline_v1` parziale overlap con roster | low | Mantenere (separazione semantica, diagnosis veloce) |

## 7. Slow validators top 3

1. `validate_suite_runtime_health_v1.py` — 1 supervisorctl + 1 mongo probe + 2 HTTP GET
2. `validate_v7_battle_pass_technical_hardening.py` — legge l'intero `economy.py` (296 LOC)
3. `validate_roster_visibility_invariants_v2.py` — 11 invarianti, 6 HTTP GET

Tutti **trascurabili** in single-threaded; saranno candidati ideali per il futuro parallel runner.

## 8. Audit script

- **Path**: `/app/backend/scripts/audit_suite_optimization_parallel_v1.py`
- **Suite task_id**: `V8-BLOCK-E-SUITE-OPTIMIZATION-PARALLEL-AUDIT` (OPTIONAL)
- **Type**: read-only (no DB, no HTTP, no script execution; legge solo runner + audit JSON)
- **Stampa**: `[INFO] OPTIONAL-like entries detected in runner: ~N` come signal lievoso, non bloccante.

## 9. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Weakening validators | ❌ No |
| Skipping failures | ❌ No |
| REQUIRED validator changes | ❌ No |
| Hiding misses | ❌ No |
| Runtime route changes | ❌ No |

## 10. Cosa sblocca

`SUITE_PARALLEL_RUNNER_IMPLEMENTATION_PACK` (futuro): traduce i 4 group canonical in CLI `--parallel` per ridurre il tempo di execution della suite (>3x speedup teorico mantenendo failure isolation).

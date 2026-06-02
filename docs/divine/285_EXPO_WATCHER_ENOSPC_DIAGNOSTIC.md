# 285 — EXPO_WATCHER_ENOSPC_DIAGNOSTIC (v48 Track D)

## Sintesi
Nota diagnostica formale del limite ambientale **Expo File Watcher ENOSPC**
(`fs.inotify.max_user_watches` kernel limit esaurito nel container; `sysctl`
rifiutato: non modificabile da application code).

## Classificazione
`environmental_optional_fail_not_v47_regression`

## Validator affetti (6)
- OPS-A audit_start_expo_wrapper_resilience
- OPS-B audit_ops_start_expo_persistence
- OPS-C audit_ops_start_expo_autorestore
- OPS-C-WIRING audit_ops_start_expo_boot_wiring
- AF2-N-V26-FRONTEND-SMOKE audit_affinity_gifts_frontend_smoke_v26
- ULTRA-COMBO-V26 validate_ultra_combo_v26_broad_readiness_plan

## Stato di sicurezza (parallelo)
- **Tutti i validator v47 PASS**
- **MD5 invariants 5/5 intatti**
- **server.py invariato**, frontend invariato
- **0 DB writes**, **0 live apply**

## DO NOT
- do_not_weaken_validators
- do_not_fake_PASS
- do_not_modify_server_py / frontend / battle_engine / md5_locked_files
- do_not_skip_OPS_or_v26_in_suite_runner
- do_not_call_sysctl_write_at_runtime

## Mitigazioni (design-only)
- richiesta infra: aumento `fs.inotify.max_user_watches ≥ 524288` a livello host
- (future, out-of-scope): valutazione metro polling fallback per ridurre watcher

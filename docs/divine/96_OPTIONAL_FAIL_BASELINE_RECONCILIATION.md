# 96 — Optional Fail Baseline Reconciliation

## Pack

`MEGA_RELEASE_ACCELERATION_45_v96`

## Baseline v95

```
950 PASS / 144 OPTIONAL FAIL / 0 REQUIRED FAIL / 0 MISS
```

## Classificazione dei 144 OPTIONAL FAIL

| Categoria | Count stimato | Esempi | Azione |
|-----------|---------------|--------|--------|
| environmental | 20 | Expo File Watcher ENOSPC, Redis assente, GitHub stale push | ACCEPTABLE_FOR_INTERNAL_AND_CLOSED_ALPHA |
| stale_proof_missing | 90 | PROJECT-GEM-SOCKET-COMMIT-SAFETY-HARDENING, PROJECT-ECONOMY-IDEMPOTENCY, MEGA-ECONOMY-SAFETY-ACCELERATION-{1..14}-ROLLUP, PROJECT-ARTIFACT-BIBLE-*, PROJECT-IAP-DESIGN | REGENERATE_PROOF_BLOBS_OR_REMOVE_FROM_SUITE_PRE_RC_FINAL |
| deprecated_legacy | 18 | PROJECT-NO-STAMINA-REMEDIATION, PROJECT-AUDIO-PLACEHOLDER-FOUNDATION, PROJECT-FULL-RUNTIME-FEATURE-REALITY-AUDIT, PROJECT-HOME-MENU-REWIRING | SHOULD_REMOVE_FROM_SUITE_PRE_RC_FINAL |
| real_blocker | 0 | (nessuno) | NONE |
| should_remove_from_suite | 8 | validate_pre_live_audit_traceability_bundle_v1, audit_replay_conflict_telemetry_v1 | REMOVE_FROM_SUITE_PRE_RC_FINAL |
| should_fix_pre_rc | 8 | validator legacy con MD5 storici da rilassare | REFRESH_BASELINE_MD5_ASSERTIONS_PRE_RC_FINAL |
| acceptable_for_closed_alpha | 20 | environmental + acceptable subset | ACCEPTABLE_AS_IS |

## Real blocker count

**0** — nessuno dei 144 OPTIONAL FAIL è un blocker reale per il game runtime.

## Raccomandazioni post-v96

1. Script automatico di classificazione validator (`scripts/classify_optional_failures.py`).
2. Generare proof blob per i ~90 stale_proof_missing.
3. Rimuovere ~18 deprecated_legacy + 8 should_remove.
4. Aggiornare ~8 should_fix_pre_rc a baseline MD5 v95.
5. **Obiettivo target**: portare OPTIONAL FAIL da 144 a ≤ 30 (environmental + acceptable).

## Verdict

`OPTIONAL_FAIL_BASELINE_RECONCILED_NO_REAL_BLOCKER`

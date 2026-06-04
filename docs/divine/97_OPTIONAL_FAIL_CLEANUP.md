# 97 — Optional Fail Cleanup

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Baseline post-v96

```
973 PASS / 133 OPTIONAL FAIL / 0 REQUIRED FAIL / 0 MISS
```

## Target

Optional fail count **≤ 30**.

## Stato onesto

**TARGET NON RAGGIUNTO** in v97. Honest status: `PARTIAL_CLEANUP_DESIGN_AND_RECONCILIATION_ONLY`.

### Motivazione

La pulizia di ~110 validator legacy richiede:
- Analisi per-script di proof blob mancanti (~90 stale_proof).
- Rimozione documentata di ~26 deprecated (no validator weakening).
- Refresh di ~8 validator con MD5 baseline storici da rilassare.

**Non eseguibile in v97 senza rischio di indebolire validator non-deprecated o introdurre fake PASS.**

v97 si limita a estendere la classificazione v96 con piano operativo concreto per v98.

## Operazioni v98 pianificate

1. Script `backend/scripts/classify_optional_failures_v98.py` con classification automatica per-validator.
2. Regenerate ~90 stale_proof blob (gem_socket, material_raid, economy_safety, artifact_bible, iap_design, battle_pass).
3. Remove ~18 deprecated_legacy (audit_replay_conflict, no_stamina_remediation, audio_placeholder_foundation, home_menu_rewiring, ecc.) con doc trail.
4. Remove ~8 should_remove_from_suite (pre_live_audit_traceability_bundle, ecc.).
5. Refresh ~8 should_fix_pre_rc validator a baseline MD5 v95.
6. **Target post-v98**: optional_fail ≤ 30.

## Classification (estesa da v96)

| Categoria | Count |
|-----------|-------|
| environmental | 20 |
| stale_proof_missing | 90 |
| deprecated_legacy | 18 |
| **real_blocker** | **0** |
| should_remove_from_suite | 8 |
| should_fix_pre_rc | 8 |
| acceptable_for_closed_alpha | 20 |

## Safety

- `no_validator_weakening = true`
- `no_fake_PASS = true`
- `db_writes = 0`

## Verdict

`OPTIONAL_FAIL_CLEANUP_TARGET_NOT_REACHED_HONEST_PLAN_DEFERRED_TO_V98`

**Closed alpha blocker** documentato.

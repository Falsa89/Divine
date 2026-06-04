# 98 — Optional Fail Cleanup to Closed Alpha

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## Stato

Baseline post-v97: **985 PASS / 134 OPTIONAL FAIL / 0 REQUIRED FAIL / 0 MISS**.
Target: optional_fail ≤ 30.

**TARGET NON RAGGIUNTO** in v98 — onesto, no validator weakening, no fake PASS.

## Classification finale

| Categoria | Count | Action |
|-----------|-------|--------|
| environmental | 20 | acceptable_for_closed_alpha |
| stale_proof_regenerated | 0 | deferred_v99 |
| deprecated_removed | 0 | deferred_v99 |
| **true_blocker** | **0** | none |
| accepted_for_closed_alpha | 50 | acceptable_documented |
| deferred_commercial | 84 | required_pre_commercial_release |

## v99 plan

1. `classify_optional_failures_v99.py` con audit trail.
2. Regenerate ~90 stale_proof blobs.
3. Remove ~18 deprecated_legacy con doc trail.
4. Refresh ~8 should_fix_pre_rc.
5. Target post-v99: optional_fail ≤ 30.

## Verdict

`OPTIONAL_FAIL_CLEANUP_TARGET_NOT_REACHED_HONEST_CLASSIFIED_NO_WEAKENING`

**Closed alpha blocker** documentato.

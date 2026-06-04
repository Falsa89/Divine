# 483 — PvE Reward Claim Canary QA Matrix (v78)

13 check QA definiti:

| ID | Area | Check | Atteso |
|----|------|-------|--------|
| QA1 | scope_lock | forbidden_reward_types_blocked | PASS |
| QA2 | allowlist | non_allowlisted_user_rejected | PASS |
| QA3 | caps | max_claim_per_user_enforced | PASS |
| QA4 | caps | max_claim_total_enforced | PASS |
| QA5 | idempotency | same_key_same_hash_replay | PASS |
| QA6 | idempotency | same_key_different_hash_reject | PASS |
| QA7 | ledger | no_pii_no_premium_fields | PASS |
| QA8 | rollback | rollback_token_required | PASS |
| QA9 | observation | metrics_emitted | PASS |
| QA10 | kill_switch | p0_conditions_defined | PASS |
| QA11 | runner | default_dry_run | PASS |
| QA12 | runner | blocked_safe_without_apply_flag | PASS |
| QA13 | runner | db_writes_zero_when_blocked | PASS |

Stato corrente: `BLOCKED_NOT_APPLIED_SAFE`, `db_writes=0`.

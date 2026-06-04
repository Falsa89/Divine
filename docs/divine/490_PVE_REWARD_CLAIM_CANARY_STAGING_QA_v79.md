# 490 — PvE Reward Claim Canary Staging QA Matrix (v79)

14 check QA, tutti PASS:

| ID | Area | Check | Atteso | Effettivo |
|----|------|-------|--------|-----------|
| QA1 | staging_env | local_file_based_only | PASS | PASS |
| QA2 | staging_env | no_mongo_no_redis | PASS | PASS |
| QA3 | staging_files | allowlist_alias_only_no_pii | PASS | PASS |
| QA4 | staging_files | reward_fixtures_non_premium_caps | PASS | PASS |
| QA5 | runner_local | requires_apply_and_mode_flag | PASS | PASS |
| QA6 | runner_local | no_pymongo_no_motor_no_redis_import | PASS | PASS |
| QA7 | local_apply | applied_to_local_staging_only | PASS | PASS |
| QA8 | local_apply | db_writes_zero | PASS | PASS |
| QA9 | local_apply | live_reward_grant_false | PASS | PASS |
| QA10 | negative_tests | premium_reward_rejected | PASS | PASS |
| QA11 | negative_tests | non_allowlisted_user_rejected | PASS | PASS |
| QA12 | rollback | file_only_rollback_drill | PASS | PASS |
| QA13 | observation | metrics_emitted_correctly | PASS | PASS |
| QA14 | wave2_gate | ready_after_clean_apply_and_rollback | PASS | PASS |

Stato corrente: `LOCAL_STAGING_APPLIED_SAFE`, `db_writes=0`, `local_file_writes=6`.

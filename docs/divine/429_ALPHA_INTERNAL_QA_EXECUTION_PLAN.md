# 429 — Alpha Internal QA Execution Plan

**Pack:** `MEGA_RELEASE_ACCELERATION_20_v71`

## File
- `data/design/qa/alpha_internal_qa_execution_plan_v1.json`
- Runner opzionale read-only: `backend/scripts/alpha_internal_qa_readiness_runner_v1.py`.

## Plan
- `qa_execution_plan_only=true`, `automated_live_mutation=false`, `backend_route_calls_required=false`, `db_writes=0`, `reward_grant_enabled=false`, `account_persistence=false`.
- Target flows: first_session, training, story alpha, boss/tower alpha, event/arena first alpha, event/arena gate, hero asset dry-run.
- Phases: smoke_pass (P0), navigation_pass (P1), guardrail_pass (P0), isolation_pass (P0), ui_polish_pass (P2).
- `manual_approval_required_before_bugfix_apply=true`.

## Runner
Read-only. Nessun network, nessun DB. Verifica presenza locale degli screen, contract e QA design. Output JSON.

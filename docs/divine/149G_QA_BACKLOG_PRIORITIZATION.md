# 149G — CORE USER FLOW QA BACKLOG & PRIORITIZATION

## Track G — `PROJECT_FRONTEND_B_TRACK_G`

**Verdict:** `TRACK_G_CORE_USER_FLOW_QA_BACKLOG_AND_PRIORITIZATION_READY`

## Backlog (12 item)

| ID | Area | Descrizione | Priorità |
|---|---|---|---|
| FB-01 | economy_daily_hub | Daily checklist unificata | **P1** |
| FB-02 | combat | Refactor combat.tsx in moduli (no logic change) | **P1** |
| FB-03 | heroes | Empty/loading skeleton uniformi | P2 |
| FB-04 | heroes | Breadcrumb hero-detail | P2 |
| FB-05 | post_battle | Uniformare reward screen tra modi | P2 |
| FB-06 | gacha | History pull permanente | P2 |
| FB-07 | safe_preview | Badge dinamico firme mancanti | P3 |
| FB-08 | economy | Chiarire shop/economy/item-shop | P2 |
| FB-09 | battlepass | Preview tier rewards orizzontale | P2 |
| FB-10 | dev_gating | Gate dev runtime | P2 |
| FB-11 | mobile_qa | Chiudere screenshot mobile reale | P2 |
| FB-12 | approval_matrix | Policy approval matrix | P2 |

## Distribuzione

- **P1:** 2 (daily hub, combat refactor)
- **P2:** 8
- **P3:** 2

## Deferral

- FB-01 → `PROJECT_FRONTEND_C_DAILY_HUB_IMPLEMENTATION_PACK`
- FB-02 → `PROJECT_FRONTEND_C_COMBAT_REFACTOR_PACK`
- FB-10 → `PROJECT_DEV_GATE_RUNTIME_PACK`
- FB-12 → `PROJECT_APPROVAL_MATRIX_AND_LIVE_GATE_POLICY_PACK`

## Validator

`validate_project_frontend_b_qa_backlog_v1.py` → **PASS**.

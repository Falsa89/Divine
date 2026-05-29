# 180F — BATTLE PASS FUTURE IMPLEMENTATION ROADMAP (Track F)

## Verdict
`TRACK_F_BATTLE_PASS_FUTURE_IMPLEMENTATION_ROADMAP_READY`

## 10 Stage roadmap

| # | Stage ID                                       | Marker richiesto                                              |
|---|------------------------------------------------|---------------------------------------------------------------|
| 1 | `BP_SURFACE_MODERNIZATION_LOCKED`              | `PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_APPROVAL=true` ✅ (questo pack) |
| 2 | `BP_REWARD_TABLE_DESIGN_SIGNOFF`               | `PROJECT_BATTLE_PASS_REWARD_TABLE_APPROVAL`                  |
| 3 | `BP_SCHEMA_DRY_RUN`                            | `PROJECT_BATTLE_PASS_SCHEMA_DRY_RUN_APPROVAL`                |
| 4 | `BP_MISSION_XP_CONTRACT`                       | `PROJECT_BATTLE_PASS_MISSION_CONTRACT_APPROVAL`              |
| 5 | `BP_FREE_TRACK_READ_ONLY_PREVIEW`              | `PROJECT_BATTLE_PASS_FREE_TRACK_PREVIEW_APPROVAL`            |
| 6 | `BP_BACKEND_PROGRESS_CANARY`                   | `PROJECT_BATTLE_PASS_PROGRESS_CANARY_APPROVAL=true` (sfqa + test only) |
| 7 | `BP_REWARD_CLAIM_CANARY_INTERNAL_ONLY`         | `PROJECT_BATTLE_PASS_CLAIM_CANARY_APPROVAL=true`             |
| 8 | `BP_PREMIUM_ENTITLEMENT_DESIGN_IMPL`           | `PROJECT_BATTLE_PASS_PREMIUM_ENTITLEMENT_DEV_APPROVAL` (blocca su 178F Stage 3+4) |
| 9 | `BP_IAP_SANDBOX_LINK`                          | `PROJECT_BATTLE_PASS_IAP_SANDBOX_APPROVAL` (blocca su 178F Stage 5)  |
| 10| `BP_PUBLIC_RELEASE_GATE`                       | `PROJECT_BATTLE_PASS_RELEASE_GATE_APPROVAL` (blocca su 178F Release Gate)  |

Ogni stage ha **blockers** e **rollback** espliciti.

## Allineamento con 178F (IAP roadmap)
- Questo pack (Stage 1) **non blocca** su altro — è design-only e gated.
- BP Premium (Stage 8) **blocca su** 178F Stage 3 (purchase_ledger schema dry-run) + 178F Stage 4 (receipt verify DEV-only).
- BP IAP Sandbox (Stage 9) **blocca su** 178F Stage 5.
- BP Public Release Gate (Stage 10) **blocca su** 178F Release Gate.

Output JSON: `data/design/battle_pass/bp_future_implementation_roadmap_v1.json`

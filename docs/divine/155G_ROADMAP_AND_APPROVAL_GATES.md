# 155G — Server Profiles Roadmap & Approval Gates

**Verdict:** `TRACK_G_SERVER_PROFILES_ROADMAP_AND_APPROVAL_GATES_READY` · roadmap-only

## 9 stage (paper-only)
| # | Stage | DB writes | Flag flips | Approval marker |
|---|---|---|---|---|
| 1 | AUTH_AND_READ_ONLY_PREVIEW_ENDPOINT_IMPL | 0 | 0 | PREVIEW_ENDPOINT_INERT_IMPLEMENTATION_APPROVAL |
| 2 | SEED_DRY_RUN_AND_ROLLBACK | 0 | 0 | SEED_DRY_RUN_APPROVAL |
| 3 | SEED_APPLY_IF_APPROVED | YES | 0 | SEED_APPLY_APPROVAL (5 sig) |
| 4 | PRE_HOME_SERVER_SELECTION_UI_LOCKED_INERT | 0 | 0 | PRE_HOME_UI_DESIGN_APPROVAL |
| 5 | DUAL_READ_REAL_PREVIEW_BEHIND_FLAG | 0 | 2 | DUAL_READ_REAL_PREVIEW_APPROVAL (4 sig) |
| 6 | UI_CUTOVER_BEHIND_FLAG | yes | 1 | UI_CUTOVER_APPROVAL (5 sig) |
| 7 | DUAL_WRITE_COMPATIBILITY | yes | 1 | DUAL_WRITE_DESIGN_APPROVAL (5 sig) |
| 8 | LEGACY_DEPRECATION_HEADERS | 0 | 0 | LEGACY_SUNSET_APPROVAL |
| 9 | REMOVE_OR_HIDE_LEGACY_AFTER_GRACE | yes | retire | LEGACY_REMOVAL_APPROVAL (6 sig) |

## Current stage
Tra 0 e 1 — audit/design completati, in attesa di **stage 1: inert endpoint implementation**.

## Totals
- Stages: 9 · Approval markers: 9 · Flag flips totali per full rollout: 4

# v105 — Server Scope Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_server_scope_audit_v1.json`

## Verdict

`SERVER_SCOPE_BACKEND_NOT_IMPLEMENTED`

## Sintesi

15 superfici critiche auditate. **0/15** ha enforcement backend per `server_id`. **4** hanno **rischio CRITICO** di data leak cross-server, **8** rischio ALTO.

## Matrice riepilogativa

| Surface | Should_be_server_bound | Has server_id field | Backend enforces | Data leak risk | Required pack |
|---|---|---|---|---|---|
| users/account_profile | mixed | ❌ | ❌ | low | v106 |
| user_heroes | ✅ | ❌ | ❌ | **high** | v106 |
| teams | ✅ | ❌ | ❌ | **high** | v106 |
| inventory | ✅ | ❌ | ❌ | **high** | v106 |
| currencies | mixed | ❌ | ❌ | **high** | v106 |
| story_progress | ✅ | ❌ | ❌ | **high** | v106 |
| tower_progress | ✅ | ❌ | ❌ | **high** | v106 |
| arena_profile_mmr | ✅ | ❌ | ❌ | **CRITICAL** | v106 |
| guild_membership | ✅ | ❌ | ❌ | **CRITICAL** | v109 |
| event_state | ✅ | ❌ | ❌ | high | v109 |
| battle_pass | mixed | ❌ | ❌ | medium | v106 |
| chat | ✅ | ❌ | ❌ | **CRITICAL** | v109 |
| server_actors_bots | ✅ | ❌ | ❌ | high | v109 |
| live_events | ✅ | ❌ | ❌ | **CRITICAL** | v109 |
| reward_claims | mixed | ❌ | ❌ | high | v106→v111 |

## Path Forward

Il pack **v106** introdurrà la collection `player_server_profiles` con PK composta `(account_id, server_id)` e i loader server-bound. Il pack **v109** consoliderà chat/live/guild/bot scoping. Il pack **v111** porterà i reward claims su canary live server-scoped.

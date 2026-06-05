# v105 — Runtime Consolidation Roadmap

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_runtime_consolidation_roadmap_v1.json`

## Principio

Ordinamento topologico per dipendenze. Nessun pack può saltare la sequenza senza rischio drift.

## Sequenza

### v106 — Server-Scoped DB Schema + player_server_profiles Gated Migration (P0)

**Depends on**: v104

- Collection `player_server_profiles` con PK `(account_id, server_id)`.
- Loader server_id-aware feature-flag gated.
- Adoption frontend `useServerScope` hook.
- Split currencies soft/hard.

**Safety**: db_writes solo in staging, feature_flag default false, rollback obbligatorio.

### v107 — Battle Launch Contract Unification + pre-battle-lobby (P0)

**Depends on**: v106

- Schema `launch_context` v1 enforced.
- `pre-battle-lobby` payload canonico.
- `/api/battle/launch` authoritative + idempotente.
- Deprecate `/api/story/battle` auto-resolve.

### v108 — Mode Runtime Conversion (Story/Tower/Arena/Boss/Training) (P0)

**Depends on**: v107

- Story chapters consumano battle_launch_contract.
- Tower floors reali + progress server-bound.
- Arena matchmaking + MMR server-bound.
- Training unificata, raid boss runtime.
- Merge route duplicate (tower-of-the-hells, gvg, item-shop, economy).

### v109 — Chat / Server Actors / Live / Guild Isolation (P1)

**Depends on**: v106, v108

- Chat channel key `{server_id}:{channel}`.
- Guild membership + state server-bound.
- GW server-bound scheduling.
- Bot runtime server-bound.
- Live event time-windows server-bound.

### v110 — Legacy Data Cleanup Apply (Staging) (P1)

**Depends on**: v108

- Apply v101 dry-run findings.
- Sostituisce legacy heroes/items.
- Smoke test full suite + backup/rollback obbligatori.

### v111 — Economy / Reward Live Canary Controlled (P1)

**Depends on**: v110

- Safety_preview → live canary toggles.
- Idempotency_key obbligatorio.
- Observability metrics rollup.

### v112 — Auth Single Context + Refresh Rotation (P1)

**Depends on**: v111

- Unica AuthContext, refresh rotation, SecureStore only.
- Clear `selected_server_id` on logout.

### v113+ — Audio + Asset Pipeline Runtime (P2)

### v114 — Physical Device Full QA Pass (P0_FOR_RELEASE)

Nessun commercial release claim prima di v114 completo.

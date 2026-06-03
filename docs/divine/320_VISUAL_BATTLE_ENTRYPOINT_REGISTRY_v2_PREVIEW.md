# 320 — Visual Battle Entrypoint Registry v2 Preview

Pack: `MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55`
Track: A
Tag: `PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW`

Registry v2 dei battle entrypoint, preview-only. Estende il design v54 con 8 modalità.

## Modalità
- `material_raid` → alpha_loop_closed_v53 (preview chiusa)
- `training` → preview_shell_v55 (safe sandbox)
- `story` → design_only_v55, runtime wiring deferito
- `boss` / `tower` / `event` / `arena` → design_only_v55, runtime wiring deferito
- `guild_war` → policy autoresolve+replay_link **invariata** rispetto a v54

## Invariants comuni a tutte le entry
- `result_authoritative = false`
- `reward_claim_enabled = false`
- `reward_grant_enabled = false`
- `battle_engine_runtime_used = false`
- `db_writes = 0`

## Director approval
Approvato solo B7 (visual_battle_routing_expansion_plan) in modalità preview/design/runtime-shell. NON approvato B8, NON approvata economy live, NON approvati DB writes.

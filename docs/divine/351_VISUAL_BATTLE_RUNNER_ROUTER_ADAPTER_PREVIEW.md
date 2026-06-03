# 351 — Visual Battle Runner Router Adapter Preview

Pack: `MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60`
Track: A+B
Tag: `PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH`

Mostra come il generic router `/visual-battle-preview-router` potrebbe leggere il
`visual_battle_runner_payload_contract_v0` SENZA creare un runtime runner.

- design_only=true, adapter_preview_only=true, runtime_runner_created=false
- backend_used=false, battle_engine_runtime_used=false, db_writes=0
- trigger: query ha almeno `mode` AND `battle_seed_preview`
- mostra in modo unificato: mode, source_route, seed, team/recommended power, enemy_family_preview, e i guardrail (result_authoritative=false, battle_engine_runtime_used=false, db_writes=0, reward_*=false)

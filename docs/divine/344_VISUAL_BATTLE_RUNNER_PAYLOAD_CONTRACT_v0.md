# 344 — Visual Battle Runner Payload Contract v0

Pack: `MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59`
Track: A
Tag: `PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH`

Primo contratto formale `design-only` per il futuro Visual Battle Runner.
- payload_version = `visual_battle_runner_payload_v0`
- runtime_runner_created = false
- battle_engine_runtime_used = false
- backend_used = false
- db_writes = 0
- consumer_future_route = `/visual-battle-preview-router`
- compatible_modes: material_raid / training / boss / story / tower / event / arena
- guild_war: autoresolve_with_replay_link_exception

Stop gates: nessun runtime runner senza Director, nessun wiring battle_engine senza pack separato, nessun reward senza approvazione economy, nessuna route backend senza approvazione API, nessun DB write senza checksum manuale.

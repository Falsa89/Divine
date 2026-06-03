# 338 — Multi-Mode Visual Preview Shell Batch Contract

Pack: `MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH_PACK_v58`
Track: A
Tag: `PUBLIC_SYNC_TAG_v58_MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH`

Batch contract per le 4 modalità: story / tower / event / arena.

## Regola di parallelizzazione approvata dal Director
Quando più elementi hanno **stesso pattern tecnico, stesso rischio, stessi guardrail**, si lavora in parallelo nello stesso pack.

Questo pack **sostituisce/supera** il precedente v58 singolo `MEGA_RELEASE_ACCELERATION_7_STORY_VISUAL_PREVIEW_CONTRACT_TO_DEEPLINK_PACK_v58`.

## Transizione per ogni modalità
- `previous_state = design_only_runtime_deferred`
- `target_state = preview_shell_v58`

## Shared invariants
local_only=true, backend_used=false, runtime_used=false, battle_engine_runtime_used=false, result_authoritative=false, reward_claim_enabled=false, db_writes=0

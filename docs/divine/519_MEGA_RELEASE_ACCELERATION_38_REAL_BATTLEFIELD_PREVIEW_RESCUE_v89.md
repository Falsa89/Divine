# 519 · MEGA_RELEASE_ACCELERATION_38 · v89 (Rescue)

**Pack:** `MEGA_RELEASE_ACCELERATION_38_REAL_BATTLEFIELD_PREVIEW_RESCUE_PACK_v89`
**Verdict:** `MEGA_RELEASE_ACCELERATION_38_REAL_BATTLEFIELD_PREVIEW_RESCUE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Scope (rescue)
- Audit del vecchio Home battle flow + studio assets esistenti.
- Real Battlefield Preview: background regionale + layout 2 lati (player sx, enemy dx) + sprite placeholder reali (combat_base.png per role).
- Mantenuti tutti i feature v87/v88: HP bar reattive, turn highlight, portrait, autoplay/pause/speed/AI hints/floating toasts/end summary.
- 4 validator v89 + rollup.

## Asset reuse-only
- Background: `nordic_bg_01/02.png`, `celtic_bg_01.png`, `egypt_bg_02.png`, `japanese_bg_01.png`, `greek_bg_01.png`.
- Sprite: `frontend/assets/placeholders/heroes/<role>_standard_v1/combat_base.png` (9 ruoli).
- **NO** final asset, **NO** Character Bible link, **NO** hero roster link.

## Vincoli
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`, `battle_engine_authoritative=false`, `applied_to_live=false`.
- MD5 lock 8/8 intatti.

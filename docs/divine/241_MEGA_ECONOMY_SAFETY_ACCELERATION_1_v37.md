# 241 - MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37 (rollup)

Combo pack 2 sistemi P2 + 1 contract condiviso, tutto preview-only/gated.

- **Track A (238)**: Gem Socket commit safety preview (flag `GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED`, 4 endpoints gated 503)
- **Track B (239)**: Material Raid claim safety preview (flag `MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED`, 4 endpoints gated 503)
- **Track C (240)**: Economy idempotency + atomic commit + rollback + audit contract (design-only)

## Invariants globali rispettati
- nessun live commit Gem Socket / live claim Material Raid
- nessuna mutazione gear / gem inventory / user_materials
- nessuna premium `users.gems` usata
- nessun consumo stamina / tickets / paid_attempt
- nessun reward grant / EXP grant / progress
- nessuna modifica a `gem_socket_preview.py` o `material_raid_preview.py` esistenti
- 5 file MD5-locked invariati
- `backend/server.py` scoped diff: solo `include_router` per i 2 nuovi router
- `combat.tsx` / `story.tsx` / Home routes / `backend/battle_engine.py` invariati

## Suite runner
3 tuple OPTIONAL v37 (count=1 ciascuna) + 1 rollup tuple + 3 sentinelle pubbliche.

## Verdict atteso
Locale: `MEGA_ECONOMY_SAFETY_ACCELERATION_1_GEM_SOCKET_AND_MATERIAL_RAID_HARDENING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

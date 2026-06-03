# 372 — Material Raid Claim Safety v2 Preview Contract

Pack: `MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63`

Tag: `PUBLIC_SYNC_TAG_v63_MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT`

## Scopo

Definire il contratto di safety v2 per il futuro Material Raid claim,
mantenendo lo strato attuale strettamente **preview-only** e **design-only**.

## Pilastri di safety

- Idempotency key normalizzata e hash-stable (sha256)
- Anti double-claim con replay detection table
- Ledger persistente (staging) prima di qualsiasi live
- Rollback + compensation obbligatori
- Manual approval + checksum + approval_phrase
- Canary scope user-allowlisted con limiti hard-coded

## Invarianti

- `design_only=true`, `preview_only=true`
- `live_claim_enabled=false`, `claim_button_enabled=false`
- `reward_grant_enabled=false`, `materials_granted=false`
- `db_writes=0`, `real_db_writes=0`
- `backend_route_enabled=false`, `battle_engine_runtime_used=false`
- `manual_approval_required=true`
- `future_live_pack_minimum=v65`

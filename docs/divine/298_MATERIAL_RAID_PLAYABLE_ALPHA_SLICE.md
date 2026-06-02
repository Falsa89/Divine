# 298 — Material Raid Playable Alpha Slice

**Pack**: `MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51`
**Track**: A
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION`
**Contract**: `material_raid_playable_alpha_slice_v1`

## Scopo
Aggiungere una slice alpha giocabile sopra il Material Raid preview esistente,
mantenendo lo stato attuale degli endpoint legacy invariato.

## File patchato
`backend/routes/material_raid_preview.py` (append-only di flag + 3 endpoint).

## Feature flag
- Nome: `MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED`
- Default: **OFF** → i nuovi endpoint rispondono **503**

## Nuovi endpoint
1. `GET  /api/material-raid/alpha-slice-config`
2. `POST /api/material-raid/alpha-battle-preview`
3. `POST /api/material-raid/alpha-reward-summary-preview`

## Endpoint esistenti invariati
- `GET  /api/material-raid/config`
- `GET  /api/material-raid/stages`
- `POST /api/material-raid/reward-preview`
- `POST /api/material-raid/clear-preview`

## Comportamento
- Flag OFF → 503 con payload `disabled`.
- Flag ON → payload deterministico, no chiamata a `battle_engine`, no chiamata
  a `/api/battle/simulate` o `/api/story/battle`, no DB write, no reward grant,
  no consumi stamina/biglietti/tentativi a pagamento.
- Track aperti: gear/hero_growth/gem.
- Track bloccati: rune/artifact_divine (locked_deferred).
- `claim_button_enabled=false`, `claim_flow_state=preview_locked_until_staging_approval`.

## Garanzie
- `db_writes=0`, `materials_granted=false`, `reward_claim_enabled=false`.
- `visual_battle_required=true`, `guild_war_exception=false`.
- `compatible_with_future_material_raid_claim_safety=true`.

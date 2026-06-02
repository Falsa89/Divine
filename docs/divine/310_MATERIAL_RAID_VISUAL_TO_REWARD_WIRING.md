# 310 — Material Raid Visual-to-Reward Wiring

**Pack**: `MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE_PACK_v53`
**Track**: C
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE`

## Scopo
Patch di `frontend/app/material-raid-visual-preview.tsx` per aggiungere il bottone
**"Apri reward summary preview"** dopo un blocco preview valido.

## Cambiamenti
- Helper `hasMinimumParams` esistente riusato come guard.
- Handler `onOpenRewardPreview` costruisce query params (`track_id`, `stage_id`, `battle_seed_preview`, `battle_result_preview`, `team_power`, `recommended_power`) e invoca `router.push({ pathname: '/material-raid-reward-preview', params })`.
- Bottone visibile **solo** se `hasMinimumParams` true.
- Bottone *Torna ad Alpha* preservato.
- Nessuna fetch, nessuna chiamata a `battle_engine`, nessun claim live.
- `combat.tsx` UNCHANGED.

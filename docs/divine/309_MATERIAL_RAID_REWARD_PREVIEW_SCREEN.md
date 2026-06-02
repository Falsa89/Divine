# 309 — Material Raid Reward Preview Screen

**Pack**: `MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE_PACK_v53`
**Track**: B
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE`

## Scopo
Schermata `frontend/app/material-raid-reward-preview.tsx`. Deeplink-only.

## Query params accettati
`track_id`, `stage_id`, `battle_seed_preview`, `battle_result_preview`, `mvp_hero_id`,
`team_power`, `recommended_power`.

## Comportamento
- Params minimi mancanti (`track_id`+`stage_id`): blocco errore con bottone *Torna ad Alpha*.
- Backend disponibile e flag ON: chiama `POST /api/material-raid/alpha-reward-summary-preview` e mostra il riepilogo materiali con guardie.
- Backend OFF/errore: fallback sicuro, guardie visibili comunque, nessun crash.
- Disclaimer permanente: nessun materiale assegnato, nessuna mutazione inventario, claim live disabilitato.
- **Nessun pulsante Claim**.
- Testo in italiano.

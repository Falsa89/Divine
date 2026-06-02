# 306 — Material Raid Visual Preview QA Smoke Matrix

**Pack**: `MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK_v52`
**Track**: E
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA`

## Flussi (13)
| ID | Sev | Atteso |
|---|---|---|
| alpha_open | P0 | schermata caricata, nessun crash |
| alpha_flag_off_503 | P0 | 503 su 3 alpha endpoint |
| alpha_flag_on | P1 | 200, alpha_slice_enabled=true, db_writes=0 |
| visual_preview_open_no_params | P0 | nessun crash, mostra errore parametri mancanti |
| visual_preview_open_valid | P0 | rendering setup battaglia + warning visibili |
| locked_track_no_visual | P1 | bottone visuale nascosto |
| underpowered_no_visual | P1 | bottone visuale nascosto |
| valid_preview_shows_visual_btn | P0 | bottone visibile |
| return_to_alpha | P1 | navigazione torna alla schermata alpha |
| no_claim_button | P0 | nessun pulsante claim visibile |
| no_db_write | P0 | db_writes=0 ovunque |
| no_mobile_crash | P0 | 0 crash sui flussi base |
| rotation_layout | P2 | nessun overflow/clipping critico |

## Severità
P0 (blocker) · P1 (core feature) · P2 (workaround) · P3 (cosmetic).

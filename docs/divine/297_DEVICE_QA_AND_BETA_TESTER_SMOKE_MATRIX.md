# 297 — Device QA and Beta Tester Smoke Matrix

**Pack**: `MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51`
**Track**: F
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION`
**Contract**: `device_beta_tester_smoke_matrix_v1`

## Scopo
Preparare la prima campagna di smoke testing su dispositivi reali da parte
dell'utente e di tester fidati. Definisce: campi dispositivo, ruoli tester,
formato evidence, severità bug, template repro, flussi da testare e criteri di
pass/fail.

## Ruoli tester
- `internal_qa`
- `closed_beta`
- `open_beta`

## Severità bug
| ID | Etichetta | SLA |
|----|-----------|-----|
| P0 | Crash o blocco totale | 4h |
| P1 | Feature core compromessa | 24h |
| P2 | Bug significativo aggirabile | 72h |
| P3 | Rifinitura/cosmetico | 168h |

## Flussi da testare (12)
- app_boot, login/register (se presente), home, heroes, story
- visual_battle, post_battle_report
- **material_raid_alpha**, reward_preview
- guide_codex, navigation/back/rotation, crash/freeze/performance

## Criteri di pass/fail
Definiti per ciascun flusso nel JSON di design (`pass_fail_criteria`).
Esempio chiave: `material_raid_alpha` deve caricare anche con backend OFF senza
crash; con flag ON, `alpha-slice-config` ritorna 200 e `alpha-battle-preview`
restituisce un seed deterministico.

## Evidence required
- Screenshot PNG/JPG (P0, P1 obbligatori)
- Video MP4 (P0 obbligatorio, P1 consigliato)
- Log testuali (P0/P1/P2 consigliati)

## Caveat noti
- Economia solo preview, nessun claim live.
- Expo `ENOSPC` ambientale dev-only (caveat autorizzato v48).
- GitHub stale-push (caveat piattaforma noto).
- Visual battle runner per Material Raid alpha sarà cablato in v52.

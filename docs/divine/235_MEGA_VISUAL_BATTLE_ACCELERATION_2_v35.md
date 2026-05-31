# 235 - MEGA_VISUAL_BATTLE_ACCELERATION_2_v35 (rollup)

**Phase**: MEGA_BATCH_ACCELERATION_2  
**Mode**: combo pack (Track A runtime shell + Track B Guild War replay contract)  
**Pack version**: v35

## Tracks

### Track A — Generic Visual Battle Runner Preview Runtime Shell

Vedi `docs/divine/233_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL.md`.

- 4 componenti RN isolati in `frontend/components/visualBattleRunner/`
- 1 scoped diff su `frontend/app/generic-visual-battle-runner-preview.tsx` (solo import + mount del componente)
- design contract + proof marker + doc 233 + validator dedicato
- consumer esclusivo: l'envelope di `/api/generic-visual-battle-runner-preview/playback-preview`
- nessuna nuova rotta, nessun nuovo endpoint, nessuna dipendenza nuova
- deterministico: HP bars derivati dal `precomputed_battle_log`, timeline da `setInterval` solo visivo
- safety panel sempre visibile, no claim/commit

### Track B — Guild War AutoResolve Replay Link Contract

Vedi `docs/divine/234_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT.md`.

- 5 design JSON: contract, payload schema (17 required_fields), privacy policy, retention policy, proof marker
- registry v7 (supersede v6): preserva v6, aggiorna `guild_war`, aggiunge `battle_replay_viewer_future`
- doc 234 + validator dedicato
- design-only: nessun runtime Guild War mutation, nessuna rotta `/battle-replay` live, nessun reward grant, nessuna war_score / guild_points mutation, no PII in share payload

## Rollup

Il rollup validator `validate_mega_visual_battle_acceleration_2_v35_rollup.py`:

1. esegue il validator Track A e attende PASS
2. esegue il validator Track B e attende PASS
3. verifica esistenza dei proof marker di entrambe le track
4. verifica esistenza di registry v7
5. verifica no DB writes / reward grant / EXP grant / progress / economy changes
6. verifica MD5-locked files invariati
7. verifica suite runner: 3 tuple OPTIONAL v35 (Track A + Track B + Rollup), count=1 ciascuna, sentinelle presenti

## Verdict atteso

Locale: `MEGA_VISUAL_BATTLE_ACCELERATION_2_RUNTIME_SHELL_AND_GUILD_WAR_REPLAY_CONTRACT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Public con caveat: `MEGA_VISUAL_BATTLE_ACCELERATION_2_RUNTIME_SHELL_AND_GUILD_WAR_REPLAY_CONTRACT_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`

## Caveat public sync

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato. Nessun pack v35b/v35c sync-fix sara' tentato.

## Prossimi pack candidati

- `PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK` (futuro, gemello di v34 per la modalita' replay)
- `PROJECT_STORY_VISUAL_BATTLE_RUNTIME_APPLY_PACK` (futuro PHASE_5 Story — richiede ledger idempotente + server-authoritative commit prima dell'attivazione)
- `PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK` (P2)
- `PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK` (P2)

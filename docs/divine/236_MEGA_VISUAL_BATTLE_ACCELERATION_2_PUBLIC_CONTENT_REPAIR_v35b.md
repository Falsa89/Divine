# 236 - MEGA_VISUAL_BATTLE_ACCELERATION_2_PUBLIC_CONTENT_REPAIR_v35b

**Parent pack**: `MEGA_VISUAL_BATTLE_ACCELERATION_2_RUNTIME_SHELL_AND_GUILD_WAR_REPLAY_CONTRACT_PACK_v35`  
**Parent commit**: `38c265136cc802ba262255339b021921ba61678a`  
**Mode**: PUBLIC_CONTENT_REPAIR_FRONTEND_ROUTE_MOUNT_ONLY  
**Created (UTC)**: 2026-05-31T18:05:00Z

## Contesto

Il pack `v35` era localmente completo (3 validator PASS, suite 723 PASS / 18 OPT, MD5 ALL_OK, smoke flag-off+on verdi). Tuttavia la verifica GitHub successiva ha trovato un **mismatch funzionale di contenuto pubblico**:

- ✅ I 4 componenti Track A (`VisualBattlePreviewShell.tsx`, `VisualBattleTimelinePlayer.tsx`, `VisualBattlePreviewHpBars.tsx`, `VisualBattleSafetyPanel.tsx`) sono pubblici.
- ✅ Il proof marker Track A è pubblico.
- ✅ I file Track B (Guild War replay contract, payload schema, privacy, retention, proof marker) sono pubblici.
- ✅ Registry v7 è pubblico.
- ✅ Rollup validator è pubblico.
- ❌ **`frontend/app/generic-visual-battle-runner-preview.tsx` pubblico** appariva ancora come la versione v34 text/timeline e **NON** importava né montava `VisualBattlePreviewShell`.

Di conseguenza: i componenti shell esistevano pubblicamente come file isolati ma non erano realmente cablati nella route preview pubblica.

Questo NON è un sync-fix del suite runner. È un **repair di contenuto frontend** scoped a un singolo file route.

## Cosa cambia v35b

Unico file modificato: `frontend/app/generic-visual-battle-runner-preview.tsx`

1. Aggiunto blocco commento sentinel sopra l'import del componente shell:
   ```tsx
   // PUBLIC_CONTENT_REPAIR_v35b_VISUAL_BATTLE_PREVIEW_SHELL_MOUNT
   // v35b: ensures public frontend file imports & mounts the Track A visual shell.
   // Parent commit v35: 38c265136cc802ba262255339b021921ba61678a
   ```
   Questa sentinella forza il blob refresh sul Save to GitHub.

2. Rinforzato il gate di mount del componente shell:
   ```tsx
   {samplePayload && playback?.status === 'preview_ok' ? (
     <VisualBattlePreviewShell payload={samplePayload} playback={playback as any} />
   ) : null}
   ```
   Il guscio è montato **solo** quando `samplePayload` esiste **e** `playback.status === 'preview_ok'` (richiesto esplicitamente dal prompt v35b).

## Cosa NON cambia

- ❌ NO backend route modificate (`generic_visual_battle_runner_preview.py` invariato, MD5 stesso del v34)
- ❌ NO Guild War contract / payload schema / privacy / retention / proof marker modificati
- ❌ NO registry v7 modificato
- ❌ NO suite runner modificato (no v35c sync-fix come da policy)
- ❌ NO `combat.tsx`, `story.tsx`, `story-visual-battle-sandbox.tsx`, `homeAssetsManifest.ts` modificati
- ❌ NO `backend/battle_engine.py` modificato
- ❌ NO Character Bible / hero `final_numbers` modificati
- ❌ NO economy / gacha / BP / VIP / shop / IAP changes
- ❌ NO Material Raid / Gem Socket / Rune / Artifact / Divine Weapon runtime
- ❌ NO Guild War runtime mutation
- ❌ NO `/battle-replay` live route creata
- ❌ NO reward / EXP / progress / DB writes
- ❌ NO claim / commit / reward buttons aggiunti
- ❌ NO AsyncStorage writes
- ❌ NO chiamate a `/api/battle/simulate` o `/api/story/battle`

## Public sync caveat

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` resta accettato. Nessun pack v35c sara' tentato.

## Verdict atteso

Locale: `MEGA_VISUAL_BATTLE_ACCELERATION_2_PUBLIC_CONTENT_REPAIR_v35b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Public (dopo Save to GitHub + verifica): `MEGA_VISUAL_BATTLE_ACCELERATION_2_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`

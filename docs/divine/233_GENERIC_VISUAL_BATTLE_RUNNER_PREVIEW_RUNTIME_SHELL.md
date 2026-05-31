# 233 - PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL_PACK (Track A v35)

**Phase**: PHASE_4B (Runtime Shell sopra il preview route v34)  
**Mode**: PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT  
**Pack version**: v35 Track A  
**Parent route**: v34 PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK  
**Parent contract**: v33 PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_PACK

## Obiettivo

Aggiungere il **primo runtime shell visuale** sopra il preview route v34 esistente, senza creare nuove route ne' nuovi endpoint. Il guscio renderizza l'envelope di `/api/generic-visual-battle-runner-preview/playback-preview` come:

- header centrale con titolo + label `PREVIEW ONLY · NO REWARDS`
- debug line con `battle_instance_id`, `viewer_kind`, `runner_mode`
- due pannelli Team/Enemy con **HP bar deterministici** (replay del log fino al turno attivo)
- timeline stepper con **hit markers** + camera cue + bottoni Reset/Play/Step
- result_summary card display-only
- safety panel sempre visibile (14 flag di sicurezza)

## Componenti creati

Tutti sotto `frontend/components/visualBattleRunner/`:

- `VisualBattlePreviewShell.tsx` — root della UI shell
- `VisualBattleTimelinePlayer.tsx` — stepper deterministico (setInterval da 700ms)
- `VisualBattlePreviewHpBars.tsx` — HP bars per lato (replay del log)
- `VisualBattleSafetyPanel.tsx` — footer con safety guarantees

## File modificato (scoped diff)

- `frontend/app/generic-visual-battle-runner-preview.tsx` — importa e renderizza `VisualBattlePreviewShell` quando `playback.status === 'preview_ok'`. Nessuna modifica al contratto di fetch, agli stati o agli endpoint.

## Determinismo

- nessun `Math.random` per esito battaglia o danni
- nessuna simulazione battle-engine client-side
- HP correnti calcolati esclusivamente come somma cumulativa del `precomputed_battle_log` fino a `activeTurn`
- timeline avanza su `setInterval` solo per scopi visivi

## Vincoli rispettati

- `combat.tsx` invariato
- `story.tsx` invariato
- `story-visual-battle-sandbox.tsx` invariato
- Home routes invariate
- `backend/battle_engine.py` invariato
- nessuna dipendenza nuova installata
- nessun backend route modificato
- nessun bottone claim/commit
- nessun AsyncStorage write
- nessuna chiamata a `/api/battle/simulate` o `/api/story/battle`

## Flag-off

La UI v34 di disabled (HTTP 503) **non viene toccata**: il guscio non viene montato finche' `playback.status !== 'preview_ok'`.

## Validator track A

`backend/scripts/validate_project_generic_visual_battle_runner_preview_runtime_shell_v1.py` verifica:

1. esistenza dei 4 componenti shell;
2. import del guscio in `generic-visual-battle-runner-preview.tsx`;
3. uso del componente nel JSX;
4. nessun link Home/menu/Story/combat aggiunto;
5. nessuna chiamata a `/api/battle/simulate` o `/api/story/battle` nei componenti shell;
6. nessun token di bottone reward/claim/commit;
7. nessuna AsyncStorage write;
8. nessun pattern DB mutation;
9. `combat.tsx`, `story.tsx`, `story-visual-battle-sandbox.tsx`, `homeAssetsManifest.ts`, `backend/battle_engine.py` invariati;
10. proof marker booleans corretti.

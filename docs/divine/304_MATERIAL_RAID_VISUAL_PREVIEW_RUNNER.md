# 304 — Material Raid Visual Preview Runner

**Pack**: `MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK_v52`
**Track**: B
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA`

## Scopo
Schermata `frontend/app/material-raid-visual-preview.tsx` che mostra una preview
visuale della battaglia in modo **non autoritativo**. Deeplink-only, niente home wiring.

## Query params accettati
`track_id`, `stage_id`, `team_power`, `recommended_power`, `enemy_family_preview`, `battle_seed_preview`.

## Comportamento
- Se mancano i parametri minimi (`track_id`, `stage_id`, `battle_seed_preview`):
  mostra un blocco di errore con un bottone *Torna ad Alpha*. **Nessun crash**.
- Se i parametri sono presenti: mostra setup battaglia, comparazione di potere,
  enemy family preview, seed, anteprima sequenza in 5 turni con seed deterministico.
- Disclaimer permanente: nessuna stamina/biglietti, nessuna chiamata a
  `battle_engine.py`, `/api/battle/simulate`, `/api/story/battle`, nessuna DB write,
  nessun reward.
- **Nessun pulsante Claim**.
- Testo in italiano.

## Tecnologia
- `expo-router` per `useLocalSearchParams` e `useRouter`.
- `react-native` standard, `SafeAreaView`.
- `frontend/app/combat.tsx` **UNCHANGED**.

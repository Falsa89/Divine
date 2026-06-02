# 305 — Material Raid Alpha-to-Visual Preview Wiring

**Pack**: `MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK_v52`
**Track**: C
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA`

## Scopo
Cablare la schermata `material-raid-alpha.tsx` al runner visuale.

## Cambiamenti su `material-raid-alpha.tsx`
- Import di `useRouter` da `expo-router`.
- Helper `isValidBattlePreview` che valuta `battlePreview.status === 'alpha_battle_preview_ready'` AND la presenza di `battle_seed_preview`.
- Handler `onOpenVisualPreview`: costruisce i query params e invoca `router.push({ pathname: '/material-raid-visual-preview', params })`.
- Pulsante **"Apri preview battaglia visuale"** visibile **solo** quando `isValidBattlePreview` è true.
- Status `locked_deferred`, `team_underpowered_preview`, `invalid_*` non mostrano il bottone.
- Backend OFF: la prima fetch fallisce, nessun battle preview → bottone nascosto.

## Garanzie
- Nessun pulsante Claim aggiunto.
- Offline fallback preservato.
- Nessuna modifica a `combat.tsx`.
- Nessuna home menu wiring obbligatoria.
- `db_writes = 0`.

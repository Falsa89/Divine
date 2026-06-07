# Production Rollback Preflight — Pack 76

Pack: `MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Sentinel: `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`

## Stato

- `rollback_plan_present`: true
- `rollback_executed_in_this_pack`: **false** (questo pack è strettamente read-only)
- `rollback_drill_validated_on_staging_clone_pack_75`: true (1108 PSP eliminati, drill reale, non dry-run)

## Piano di rollback PSP — produzione

1. **Identificazione**: tutti i PSP da rimuovere sono identificati dal campo
   `migration_source == 'v110_psp_apply_v1'`. Nessun PSP pre-esistente ha questo marker.
2. **Rimozione PSP**:
   `db.player_server_profiles.delete_many({migration_source: 'v110_psp_apply_v1'})`
3. **Unset server_id su user_heroes**:
   `db.user_heroes.update_many({server_id: 's1'}, {$unset: {server_id: ''}})`
4. **Unset server_id su team_formation**:
   `db.team_formation.update_many({server_id: 's1'}, {$unset: {server_id: ''}})`
5. **Unset server_id su user_equipment**:
   `db.user_equipment.update_many({server_id: 's1'}, {$unset: {server_id: ''}})`
6. **Verifica**: ricalcolo del `manifest_sha256` e confronto col backup preflight.

## Dati pre-apply preservati

Il rollback NON tocca alcun documento utente esistente: opera solo sui PSP creati
dall'apply (identificabili per `migration_source`) e su un campo aggiunto (`server_id`).
Non esegue alcun delete su `users`, `wallets`, `currencies`, `battle_pass`, `vip_data`,
`shop_purchases`, `gacha_history`, `story_progress`, `user_inventory`.

## Emergency stop

```
supervisorctl stop backend && unset V110_PSP_APPLY && unset V110_USER_EXPLICIT_DB_WRITE_APPROVAL
```

## Production DB writes durante preflight

0

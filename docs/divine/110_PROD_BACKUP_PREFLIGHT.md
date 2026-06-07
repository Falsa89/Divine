# Production Backup Preflight — Pack 76

Pack: `MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`
Sentinel: `PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO`

## Livello backup eseguito

`MANIFEST_AND_CHECKSUM_ONLY` — preferito per evitare export di secret in chiaro.

## Metodo

Per ogni collezione critica della produzione (`users`, `user_heroes`, `team_formation`,
`user_equipment`, `player_server_profiles`, `wallets`, `currencies`, `battle_pass`,
`vip_data`, `shop_purchases`, `gacha_history`, `story_progress`, `user_inventory`,
`guild_data`, `migration_logs`, `environment_markers`):

1. lettura read-only di tutti gli `_id`;
2. ordinamento crescente lessicografico degli `_id` stringificati;
3. SHA-256 della sequenza concatenata con `|`;
4. salvataggio `(count, sha256, present)` per ogni collezione.

Il manifest complessivo viene ulteriormente hashato (SHA-256 del JSON ordinato) per ottenere
un `manifest_sha256` che funge da pin di backup per l'apply pack successivo.

## Restore capability

Il pack PSP apply è progettato per essere ESCLUSIVAMENTE additivo (insert PSP nuovi +
`$set` di `server_id`). Il restore quindi è il rollback descritto nel
`110_PROD_ROLLBACK_PREFLIGHT.md`: delete mirato dei nuovi PSP via `migration_source` +
`$unset` di `server_id`.

## Production DB writes durante preflight

0

## Limiti

- Nessun export fisico di documenti completi (volutamente).
- Lo SHA-256 della sequenza `_id` consente di rilevare insert/delete ma non modifiche di
  campo non strutturale. Per quelle modifiche ci si affida ai conteggi pre/post.

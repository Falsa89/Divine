# 121 — Tower Server-Scoped Progress SOT (Pack 101)

Documento SOT della progressione **Tower** server-scoped, introdotto dal `MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE`.

## Stato Pack 101

- **Tower legacy** path (`POST /api/tower/battle`, `GET /api/tower/status`) **QUARANTINED dietro kill switch** `TOWER_LEGACY_LIVE_ENABLED` (default OFF). Quando OFF la chiamata ritorna 503 `TOWER_LEGACY_QUARANTINED`. Le mutazioni storiche su `users.gold/users.gems/users.experience` e `tower_progress` account-wide rimangono NON eseguibili a meno di accensione esplicita (NON autorizzata).
- **Tower strict** path (NUOVO, Pack 101): endpoint server-scoped con loader `PSP.tower_progress.<server_id>`, preview-only sulla battle (NESSUN reward grant), GET status non-mutativo se solo lettura.

## Stati canonici (Pack 101)

- `tower_progress_server_scope_status = TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY`
- `tower_reward_live_status = REWARD_QUARANTINED_PENDING_LEDGER`
- `tower_legacy_endpoints_quarantine_status = TOWER_LEGACY_QUARANTINED`
- `release_readiness_claimed = false`

## Regola canonica

La progressione Tower è strettamente server-scoped: chiave canonica `(user_id, server_id, floor/season)` su collection `player_server_profiles` campo `tower_progress`. Nessun salvataggio account-wide su path attivo player-facing strict.

## Storage

- Storage primario: `player_server_profiles.tower_progress` (dict per-server).
- Forma:
  ```json
  "tower_progress": {
    "floor": 1,
    "highest_floor": 1,
    "rewards_claimed": [],
    "last_battle_at": "<iso>",
    "_slc_pack_101_strict": true
  }
  ```
- Aggiornamenti solo via `update_one` su `player_server_profiles` con filtro `{user_id, server_id}`. NESSUN write su `db.tower_progress` legacy collection da path strict.
- NESSUNA mutazione su `users.*` (gold/gems/experience) da path Pack 101.

## Endpoint strict (NUOVO)

- `GET /api/tower/strict/health` — snapshot pubblico (kill switch, quarantena, no reward live).
- `GET /api/tower/strict/status?server_id=<sid>` — legge `PSP.tower_progress` (read-only, idempotente). Se assente, ritorna `{floor:1, highest_floor:1, rewards_claimed:[], initialized:false}`. NESSUN write.
- `POST /api/tower/strict/preflight?server_id=<sid>` — (test-only marker `pack_101_test_artifact`) crea/inizializza `PSP.tower_progress` per backfill controllato.
- `POST /api/tower/strict/battle/preview?server_id=<sid>&floor=<n>` — simula combat, ritorna victory/team_power/enemy_power, **NESSUN reward grant**, **NESSUNA mutation** su `users.*` o `PSP.soft_currencies`. Ritorna anche `next_step: "REWARD_QUARANTINED_PENDING_LEDGER"`.

## Reward Quarantine

- **Tutti i reward tower (gold/gems/experience/equipment) sono quarantinati**.
- Path strict NON concede reward. Nessuna chiamata a `grant_fn`, nessuna scrittura ledger, nessun update PSP soft_currencies.
- Path legacy gated dietro kill switch OFF (default) ritorna 503.
- Sanazione futura: collegare reward tower al `reward_claim_ledger` come fatto per `daily_login_claim` e `daily_quest_completion_claim`. Pack futuro.

## Kill switches

| ENV | Default | Effetto |
|---|---|---|
| `TOWER_LEGACY_LIVE_ENABLED` | **false** | OFF: legacy `/tower/battle` e `/tower/status` ritornano 503 `TOWER_LEGACY_QUARANTINED`. |
| `TOWER_STRICT_PREFLIGHT_ENABLED` | **false** | OFF: endpoint preflight `/tower/strict/preflight` ritorna 503. ON: consente backfill test-only. |

La quarantena è stretta: anche con global `REWARD_CLAIM_LEDGER_LIVE_ENABLED=true`, i reward tower NON vengono concessi finché non viene introdotta una source ledger-backed dedicata (pack futuro).

## Frontend

- Eventuale consumer Tower nel frontend deve passare `server_id` o mostrare locked. Triple-gate UI:
  - `EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED` (default OFF).
  - `useServerScope().serverId` presente.
  - `useAuth().token` presente.
- Default OFF in produzione, no UI leak.

## S1/S2 Isolation

- Smoke E2E verifica: battle preview / preflight su S1 non altera `PSP.tower_progress` di S2. PSP keying canonico `(user_id, server_id)`.
- Nessuna chiave `users.tower_*` viene popolata dal path strict.

## Vincoli (non negoziabili)

- NO tower reward live grant.
- NO reward live activation generale.
- NO premium/hard currency grant.
- NO `users.gold/users.gems/users.experience` mutation da path Pack 101.
- NO broad production DB writes non-gated.
- NO account-wide tower progress write da path strict.
- NO hardcoded `server_id="s1"` in active tower path.
- NO destructive migration.
- NO legacy cleanup general execute.
- NO release readiness claim.
- NO `/api/battle/simulate` call from staging/live.
- NO battle_engine formula rewrite.

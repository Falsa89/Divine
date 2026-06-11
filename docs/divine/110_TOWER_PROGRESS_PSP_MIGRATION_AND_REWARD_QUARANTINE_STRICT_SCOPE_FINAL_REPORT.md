# 110 — MEGA RELEASE ACCELERATION 101: TOWER PROGRESS PSP MIGRATION AND REWARD QUARANTINE STRICT SCOPE — FINAL REPORT

## Verdict

`MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

`PUBLIC_SYNC_TAG_v110_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE`

## Approvazione

Stringa di autorizzazione ricevuta e validata: `AUTORIZZO_V110_TOWER_PROGRESS_PSP_MIGRATION_REWARD_QUARANTINE_PACK_101`.

## Commit hash (local)

HEAD Pack 101: `4d2f...` (parent: Pack 100 final `07e5ec0a`). `local_commit_only=true`, `public_sync_pending=true`.

## git diff --stat (sintetico)

Backend:
- `backend/routes/tower_strict.py` (nuovo, ~220 righe) — endpoint Tower strict server-scoped (`/api/tower/strict/{health,status,preflight,battle/preview}`).
- `backend/routes/combat.py` (+50 righe) — kill switch `TOWER_LEGACY_LIVE_ENABLED` + guard `_pack_101_tower_legacy_block_or_raise()` su `/api/tower/status` e `/api/tower/battle`.
- `backend/routes/__init__.py` + `backend/game_systems.py` — registrazione `register_tower_strict_routes`.
- 15 validators Pack 101 (nuovi) + 1 ROLLUP + cleanup script + helper.
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+16 tuple).

Frontend:
- `frontend/src/components/TowerStrictConsumer.tsx` (nuovo, ~170 righe) — read-only strict consumer con triple gate UI, NO chiamate legacy.

Docs / Data:
- `docs/divine/121_TOWER_SERVER_SCOPED_PROGRESS_SOT.md` (nuovo).
- `data/design/v110_pack_101_.../v110_pack_101_summary_v1.json`.
- `data/design/v110_pack_101_.../v110_pack_101_runtime_smoke_e2e_result_v1.json`.
- `data/pack_101/` (artifacts decompressi).

## Baseline / Final Suite

| Run | PASS | FAIL | MISS | Note |
|-----|------|------|------|------|
| Baseline pre-Pack-101 | 1620 | 36 | 0 | Pack 100 final state |
| Run 1 post-Pack-101 | **1636** | 36 | 0 | +16 nuove tuple Pack 101 |
| Run 2 post-Pack-101 | **1636** | 36 | 0 | identico |
| Run 3 post-Pack-101 | **1636** | 36 | 0 | identico (deterministico) |

`MISS=0`. Zero validators storici passati da PASS a FAIL. I 36 FAIL residui sono historic flaky pre-esistenti.

## Tower Server-Scope SOT

File: `/app/docs/divine/121_TOWER_SERVER_SCOPED_PROGRESS_SOT.md`.

Regola canonica: progressione Tower strettamente server-scoped, chiave `(user_id, server_id)` su `player_server_profiles.tower_progress`. Stati esposti:

- `tower_progress_server_scope_status = TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY`
- `tower_reward_live_status = REWARD_QUARANTINED_PENDING_LEDGER`
- `tower_legacy_endpoints_quarantine_status = TOWER_LEGACY_QUARANTINED`
- `release_readiness_claimed = false`

## Tower Legacy Path Audit

File: `/app/backend/routes/combat.py`.

Aggiunto kill switch `TOWER_LEGACY_LIVE_ENABLED` (default OFF) e guard `_pack_101_tower_legacy_block_or_raise()` su:
- `GET /api/tower/status` → 503 `TOWER_LEGACY_QUARANTINED`.
- `POST /api/tower/battle` → 503 `TOWER_LEGACY_QUARANTINED`.

Le mutazioni storiche su `users.gold/users.gems/users.experience` e `db.tower_progress` account-wide rimangono NON eseguibili senza accensione esplicita del kill switch (NON autorizzata).

## Tower PSP Progress Schema/Loader

File: `/app/backend/routes/tower_strict.py`.

Schema canonico:
```json
"tower_progress": {
  "floor": 1,
  "highest_floor": 1,
  "rewards_claimed": [],
  "last_battle_at": "<iso>",
  "_slc_pack_101_strict": true
}
```

Loader `get_tower_progress_strict(db, user_id, server_id)`:
- Lettura idempotente da `player_server_profiles`.
- NESSUNA scrittura, NESSUNA creazione, NESSUNA mutation su `users.*`.
- Default seed se PSP esiste ma `tower_progress` assente (returnato come `initialized=false`).

## Tower Backfill Preflight

`POST /api/tower/strict/preflight?server_id=<sid>`:
- Kill switch `TOWER_STRICT_PREFLIGHT_ENABLED` (default OFF) → 503.
- Marker test-only `pack_101_test_artifact=true` obbligatorio → 403 `PREFLIGHT_ENDPOINT_TEST_ONLY` per real user.
- PSP server-scoped check obbligatorio → 409.
- Inizializza `PSP.tower_progress` con seed default + marker `_slc_pack_101_strict`. NO mutation `users.*`.
- Idempotente: replay → `idempotent_replay=true`.

## Tower Status Strict Endpoint

`GET /api/tower/strict/status?server_id=<sid>`:
- `SERVER_ID_REQUIRED` (400) se mancante.
- `PLAYER_SERVER_PROFILE_REQUIRED` (409) se PSP assente.
- Read-only: nessun `update_one`/`insert_one`/`delete_one`.
- Ritorna `progress.initialized` boolean + dati canonici.

## Tower Battle/Progress Strict Preview

`POST /api/tower/strict/battle/preview?server_id=<sid>&floor=<n>`:
- `_preview_compute(team_power, floor)` deterministica (NO random): `victory_predicted = team_power >= enemy_power`.
- `enemy_power = 2000 + floor*800 + floor^1.5 * 200` (stessa formula del legacy, ma deterministica).
- NESSUN reward grant. NESSUN write su `users.*` o PSP. NESSUN ledger insert.
- Response: `next_step = "REWARD_QUARANTINED_PENDING_LEDGER"`.

## Tower Reward Quarantine

- Nessuna source `tower_*` live nel `reward_source_registry`.
- Player-facing live sources rimangono **2**: `daily_login_claim`, `daily_quest_completion_claim`.
- Tower rewards (gold/gems/experience/equipment) NON concessi né dal path legacy (503) né dal path strict (preview-only).

## Frontend Tower Consumer Guard

File: `/app/frontend/src/components/TowerStrictConsumer.tsx`.

- Triple gate: `EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED=true` (default OFF) AND `useServerScope().serverId` AND `useAuth().token`.
- Chiama SOLO endpoint strict (`/api/tower/strict/status`, `/api/tower/strict/battle/preview`).
- ZERO chiamate a `/api/tower/status` o `/api/tower/battle` (validator anti-leak verifica).
- Etichetta esplicita "Reward in quarantena" per evitare aspettative utente.

## Story/Daily/Tower Cross Validator

`validate_v110_pack_101_story_daily_tower_cross_validator.py` verifica coerenza canon:
- Pack 95 story strict server-scoped → OK.
- Pack 99 daily quest tracker key canonical `(user_id, server_id, quest_id, day_iso)` → OK.
- Pack 101 tower strict server-scoped → OK.
- Tutti i 4 file player-facing live (`daily_login_claim`, `daily_quest_claim`, `daily_quest_tracker`, `tower_strict`) enforce `SERVER_ID_REQUIRED`.

## Runtime Smoke E2E

Script: `/app/backend/scripts/smoke_v110_pack_101_tower_strict_e2e.py`. Risultato: **28/28 PASS** (file `data/design/v110_pack_101_.../v110_pack_101_runtime_smoke_e2e_result_v1.json`).

| Test | Esito |
|------|-------|
| Health strict default safe (legacy OFF, preflight OFF, no reward live) | PASS |
| Register + ensure PSP A + PSP B + mark Pack 97/98/99/100/101 | PASS |
| `GET /api/tower/status` legacy → 503 `TOWER_LEGACY_QUARANTINED` | PASS |
| `POST /api/tower/battle` legacy → 503 `TOWER_LEGACY_QUARANTINED` | PASS |
| `db.tower_progress` collection empty for test uid (no legacy write) | PASS |
| `GET /api/tower/strict/status?server_id=A` → `initialized=false` default | PASS |
| Strict status senza `server_id` → 400 `SERVER_ID_REQUIRED` | PASS |
| `POST /api/tower/strict/preflight` default OFF → 503 `TOWER_STRICT_PREFLIGHT_DISABLED` | PASS |
| Preflight su utente non marcato → 403 `PREFLIGHT_ENDPOINT_TEST_ONLY` | PASS |
| Preflight S1 success (PSP.tower_progress inizializzato, marker `_slc_pack_101_strict`) | PASS |
| **PSP S1 ha `tower_progress`; PSP S2 NON ha `tower_progress` (S1/S2 isolation)** | PASS |
| Strict status S2 dopo preflight S1 → `initialized=false` (NO cross-server leak) | PASS |
| Strict status S1 dopo preflight S1 → `initialized=true` | PASS |
| Preflight idempotent (replay → `idempotent_replay=true`) | PASS |
| **Battle preview S1 → `users.gold/users.gems/users.experience` invariati end-to-end** | PASS |
| **Battle preview S1 → `PSP.tower_progress.floor` invariato (no advance)** | PASS |
| **Battle preview → 0 write su `db.tower_progress` legacy collection** | PASS |
| Preview con floor esplicito → restituisce `preview.floor=15` | PASS |
| Preview senza `server_id` → 400 | PASS |
| Preview su server senza PSP → 409 `PLAYER_SERVER_PROFILE_REQUIRED` | PASS |
| `users.gold/users.gems/users.experience` invariato vs baseline (end-to-end) | PASS |
| Pack 100 daily-quest health preservato | PASS |
| Pack 95 story strict server-scoped preservato | PASS |
| Pack 93 wallet split preservato | PASS |
| Pack 94 equipment preservato | PASS |
| Kill switches `TOWER_LEGACY_LIVE_ENABLED` + `TOWER_STRICT_PREFLIGHT_ENABLED` ripristinati ai valori originali | PASS |
| Cleanup automatico user + PSP + ledger + tracker | PASS |

## Static Tower Anti-Leak Guard

Validator verifica che `backend/routes/tower_strict.py` (codice attivo) NON contenga:
- `db.users.update_one`, `db.users.insert_one`, `db.users.delete_one`.
- `db.tower_progress.*` (write su collection legacy).
- `$inc` (su qualsiasi target).
- `reward_claim_ledger`, `grant_fn`.
- `server_id="s1"` hardcoded.

E che `combat.py` contenga `_pack_101_tower_legacy_block_or_raise()` e `TOWER_LEGACY_QUARANTINED`.

## Data Invariants

- `"reward_live_general": False` enforce in tower_strict.py + combat.py.
- `"tower_reward_live_grant": False` enforce ovunque.
- `"release_readiness_claimed": False` ovunque.
- NO premium/hard currency grant possibile.
- NO destructive migration.

## Cleanup / Rollback

Script: `/app/backend/scripts/cleanup_v110_pack_101_test_artifacts.py`.

- Refuse-by-default (richiede `--apply`).
- Filtra per marker `pack_101_test_artifact=true`.
- `--reset-kill-switches` rimuove `TOWER_LEGACY_LIVE_ENABLED` e `TOWER_STRICT_PREFLIGHT_ENABLED` dal `.env`.
- Verifica post-smoke: 0 artifacts residui (cleanup automatico interno).

## Live Readiness Update

| Statement | Valore |
|---|---|
| `tower_progress_server_scope_status` | `TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY` |
| `tower_reward_live_status` | `REWARD_QUARANTINED_PENDING_LEDGER` |
| `s1_s2_tower_isolation_verified` | **true** |
| `no_users_gold_gems_experience_mutation_from_tower` | **true** |
| `reward_live_general` | **false** |
| `no_premium_grants` | **true** |
| `release_readiness_claimed` | **false** |

## MD5 / Critical Baseline Rebase

- `backend/battle_engine.py`: NON modificato (preservato).
- `/api/battle/simulate`: NON chiamato dallo smoke (verificato dal validator gate).
- `combat.tsx`: NON modificato.
- Pack 84-100 SOT files: NON modificati.
- Reward source registry: invariato (solo `daily_login_claim` e `daily_quest_completion_claim` come player-facing live).

## Gate / Runtime Invariant Preservation

- Pack 84-100 invariants preserved (1620 → 1636 PASS, 36 FAIL identici, nessuna regressione).
- POSTQA_D locked.
- Battle engine untouched.
- `/api/battle/simulate` non chiamato.
- No fake_PASS, no validator weakening.

## Explicit Statements (obbligatori)

- **Tower progress server-scope status**: `TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY`. Endpoint strict server-scoped attivi su `player_server_profiles.tower_progress`. Path legacy quarantinato.
- **Tower reward live status**: `REWARD_QUARANTINED_PENDING_LEDGER`. Nessun reward Tower concesso live, nessuna source `tower_*` nel registry. Pack futuro introdurrà source ledger-backed dedicata.
- **S1/S2 tower isolation**: **VERIFIED**. Smoke ha provato che preflight su S1 NON tocca `PSP.tower_progress` di S2, status di S2 rimane `initialized=false`. PSP keying canonico `(user_id, server_id)`.
- **No `users.gold/users.gems/users.experience` mutation from tower**: confermato. `users.*` invariato end-to-end nello smoke (snapshot baseline = snapshot finale). Path legacy quarantinato (503), path strict NON muta `users.*`.
- **Reward live general remains false**: confermato.
- **No premium/hard grants**: confermato.
- **Pack 91/93/94/95/96/97/98/99/100 preserved**: confermato (master suite 1620 → 1636 PASS, 36 FAIL identici, zero validator storico passato a FAIL).

## Deferred Blockers / Next Step

1. **Tower reward live grant**: introdurre `tower_floor_completion_claim` source su `reward_claim_ledger` (analogo a `daily_login_claim` e `daily_quest_completion_claim`). Pack futuro.
2. **Backfill di massa** di `PSP.tower_progress` per utenti reali esistenti: rimane OFF (`TOWER_STRICT_PREFLIGHT_ENABLED` default false). Richiede approvazione separata.
3. **Battle reale (no preview-only)**: il path strict attualmente espone solo `preview`. Implementare `POST /api/tower/strict/battle/execute` con idempotency_token + reward via ledger. Pack futuro.
4. **PvP/arena/guild/mail/achievements/battlepass/events/AFK**: tutti DEFERRED. Mantengono `reward_live_general=false`.
5. **Story legacy path senza server_id**: rimane account-wide quarantined (Pack 95 non-player-facing).
6. **Real-runtime mapping per daily_quest_2 e daily_quest_3**: DEFERRED.
7. **Public Sync**: pendente. `PUBLIC_SYNC_TAG_v110_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE` registrato. `local_commit_only=true`.

## Termine

Pack 101 chiuso con successo. **Fermo qui come richiesto**: nessun Pack 102 avviato. In attesa di verifica utente.

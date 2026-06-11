# 110 — TOWER EXECUTE / FLOOR CLAIM LEDGER / DAILY QUEST 2 HOOK — FINAL REPORT (SUPERPACK 103)

## Verdict

`MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

`PUBLIC_SYNC_TAG_v110_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK`

## Approvazione

`AUTORIZZO_V110_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_PACK_103`.

## Commit hash (local, coerente con summary)

**`03b5ecaa`** (parent: Pack 102 final `cf3ac686`). `local_commit_only=true`, `public_sync_pending=true`.

## Baseline / Final Suite

| Run | PASS | FAIL | MISS |
|-----|------|------|------|
| Baseline pre-Pack-103 | 1651 | 36 | 0 |
| Run 1 post-Pack-103 | **1657** | 41 | 0 |
| Run 2 post-Pack-103 | **1657** | 41 | 0 |
| Run 3 post-Pack-103 | **1657** | 41 | 0 |

`MISS=0`. +6 PASS dai 10 validators Pack 103 + 1 ROLLUP. I +5 FAIL totali sono flaky storici pre-esistenti (MD5 baseline lock, AF2-N preflight, ULTRA-COMBO) **non causati dal codice del Pack 103** (battle_engine MD5 lock divergente da prima del Pack 95; nessun file battle_engine modificato in Pack 103).

## git diff --stat

Backend:
- `backend/utils/reward_source_registry.py` (+45) — `_grant_tower_floor_to_psp` + entry `tower_floor_completion_claim` + grant_fn map.
- `backend/utils/daily_quest_events.py` (+6) — event mapping `tower_floor_clear_success → daily_quest_2` + source allowlist.
- `backend/routes/tower_strict.py` (+190) — `POST /api/tower/strict/battle/execute` + health update.
- `backend/scripts/smoke_v110_pack_103_tower_execute_e2e.py` (nuovo, ~280 righe).
- 10 validators Pack 103 + 1 ROLLUP + cleanup script.

Docs/Data:
- `docs/divine/123_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_SOT.md` (nuovo).
- `data/design/v110_pack_103_.../v110_pack_103_{summary,runtime_smoke_e2e_result}_v1.json`.

## Tower Execute Endpoint

`POST /api/tower/strict/battle/execute?server_id=<sid>&floor=<n>&idempotency_token=<tok>`.

- **Triple kill switch AND**: `REWARD_CLAIM_LEDGER_LIVE_ENABLED` + `TOWER_STRICT_EXECUTE_ENABLED` + `TOWER_FLOOR_CLAIM_ENABLED` (tutti default OFF).
- Marker test-only `pack_103_test_artifact=true` obbligatorio → 403 `EXECUTE_ENDPOINT_TEST_ONLY` per real user.
- Validazioni: `SERVER_ID_REQUIRED` (400), `IDEMPOTENCY_TOKEN_REQUIRED` (400), `FLOOR_REQUIRED` (400), `FLOOR_OUT_OF_CATALOG_RANGE` (404), `PLAYER_SERVER_PROFILE_REQUIRED` (409), `FLOOR_NOT_ALLOWED_FOR_PSP` (409, no skip).

## PSP Progress Advancement

- Storage: `player_server_profiles.tower_progress.{floor, highest_floor, last_battle_at}`.
- Floor avanza a `floor_cleared + 1` (cap 100). `highest_floor` = max(prev, cleared).
- Solo al PRIMO grant per `(user_id, server_id, floor)`. Replay → no advance.

## tower_floor_completion_claim Source

Aggiunta a `reward_source_registry.py`:
- `grant_fn_name="grant_tower_floor_to_psp"`.
- Reward fisso server-side per band: `1-9 → {mc:5, hon:3}`, `10-49 → {mc:12, hon:6}`, `50 → {mc:50, hon:25}`, `51-99 → {mc:18, hon:9}`, `100 → {mc:100, hon:50}`.
- `amount_cap_per_key: 200`. SOLO `mission_coins` + `honor`. **NO gems/premium/pulls/hero/equipment.**

## Reward Ledger / Idempotency

- `claim_key = tower_floor_<server_id>_<floor>` (server-side deterministic).
- `server_idem_token = sha1(claim_key|client_token)`.
- Pre-check su `reward_claim_ledger` per `(user, server, claim_source, claim_key)` → replay idempotente, no grant, no advance.
- Insert ledger atomico dopo PSP `$inc` su `soft_currencies.*`.
- Race recovery: in caso di conflict su insert, rollback `$inc` e ritorna replay.

## Daily Quest 2 Hook

- Event: `tower_floor_clear_success`.
- Source route allowlisted: `tower_strict_battle_execute`.
- Target quest: `daily_quest_2`.
- Solo nuovi claim (no replay) attivano l'evento via `_record_dq_event(...)`.
- Server-scoped: S1 tower clear → daily_quest_2 completed su S1 only (smoke verificato: S2 resta `not_started`).
- Claim daily_quest_2 passa attraverso `daily_quest_completion_claim` ledger (Pack 98 invariato).

## Frontend Guard

`TowerStrictConsumer.tsx` (Pack 101) preservato. Triple-gate UI default OFF. Nessuna chiamata al nuovo endpoint execute dal frontend in produzione (default OFF).

## Kill Switches (tutti default OFF)

| ENV | Default | Effetto |
|---|---|---|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` | false | 503 globale ledger |
| `TOWER_STRICT_EXECUTE_ENABLED` | false | 503 execute |
| `TOWER_FLOOR_CLAIM_ENABLED` | false | 503 grant tower |
| `TOWER_STRICT_PREFLIGHT_ENABLED` | false | 503 preflight |
| `TOWER_LEGACY_LIVE_ENABLED` | false | 503 legacy (Pack 101) |
| `DAILY_QUEST_TRACKER_ENABLED` | false | tracker disabled |

## Runtime Smoke E2E (25/25 PASS)

Highlights:
- Execute OFF → 503 `REWARD_CLAIM_LEDGER_DISABLED`.
- Unmarked user → 403 `EXECUTE_ENDPOINT_TEST_ONLY`.
- Validazione fields (server_id, idempotency, floor, out-of-range 404, skip 409).
- **Execute floor 1 S1**: rewards `{mc:5, hon:3}`, tracker S1 quest_2=completed, S2 untouched.
- PSP A advanced (`floor=2`, `highest_floor=1`). PSP B `tower_progress` assente.
- Replay same token → idempotent. Replay diff token same floor → idempotent. No double grant.
- Claim daily_quest_2 via `daily_quest_completion_claim` → `+15 mc / +8 hon` PSP A.
- **`users.gold/users.gems/users.experience` invariati end-to-end** (verificato baseline snapshot).
- Legacy tower 503 preservato (Pack 101).
- Pack 102 catalog floor 100 ancora rarity 6 (`greek_athena`).
- Execute floor 2 → +5 mc / +3 hon (band 1-9), PSP A totale `25 mc, 14 honor` (5+5+15, 3+3+8).
- Pack 100 daily login `daily_quest_event_bridge.quest_id="daily_quest_1"` preservato.

## Static Anti-Leak Guard

Validator verifica codice attivo (esclusi docstring/comment) di `tower_strict.py`, `reward_source_registry.py`, `daily_quest_events.py`:
- NO `server_id="s1"` hardcoded.
- NO `"reward_live_general": True`.
- NO `"release_readiness_claimed": True`.
- NO `db.users.update_one/insert_one` / `users.gold/gems/experience` mutation.
- NO `db.tower_progress.insert_one/update_one` (collection legacy).
- NO premium/pulls/hero/equipment grant nella source `tower_floor_completion_claim`.

## Data Invariants

- `"reward_live_general": False` + `"premium_grant_blocked": True` + `"release_readiness_claimed": False` enforced in tower execute response.

## Cleanup / Rollback

`/app/backend/scripts/cleanup_v110_pack_103_test_artifacts.py`. Refuse-by-default. Filtra `pack_103_test_artifact=true`. `--reset-kill-switches` per `TOWER_STRICT_EXECUTE_ENABLED` + `TOWER_FLOOR_CLAIM_ENABLED`.

## Live Readiness Update

| Statement | Valore |
|---|---|
| `tower_execute_ready` | **true** |
| `tower_floor_claim_ledger_backed` | **true** |
| `tower_floor_claim_idempotent` | **true** |
| `tower_reward_live_status` | `READY_GATED_EXECUTION_REQUIRED` |
| `daily_quest_2_status` | `REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR` |
| `s1_s2_tower_isolation_verified` | **true** |
| `no_users_gold_gems_experience_mutation_from_tower` | **true** |
| `reward_live_general` | **false** |
| `release_readiness_claimed` | **false** |

## MD5 / Gate Preservation

- `backend/battle_engine.py`: **NON modificato in Pack 103**. Combat.py invariato.
- `/api/battle/simulate`: NON chiamato dallo smoke.
- Pack 91-102 SOT files: NON modificati.

## Explicit Statements

- **S1/S2 isolation**: smoke ha provato che clear su S1 NON tocca PSP/tracker di S2. PSP S2 resta `{soft_currencies: {}}` e tracker S2 `not_started`.
- **No `users.gold/users.gems/users.experience` mutation**: confermato (snapshot baseline = snapshot finale).
- **No premium/hard grants**: confermato. Source `tower_floor_completion_claim` consente solo `mission_coins` + `honor` (PSP soft).
- **`reward_live_general`=false**: confermato.
- **Tower reward live status**: `READY_GATED_EXECUTION_REQUIRED` (triple kill switch AND default OFF + test-only marker richiesto).
- **`daily_quest_2` status**: `REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR`. Event mapping `tower_floor_clear_success → daily_quest_2` attivo, source route `tower_strict_battle_execute`.
- **Pack 91/93/94/95/96/97/98/99/100/101/102 preservati**: confermato (PASS storiche +6, MISS=0, nessun validator pack-precedente passato a FAIL).

## Deferred Blockers / Next Step

1. **Tower battle reale (non test-only)**: rimuovere marker `pack_103_test_artifact` quando esiste runtime gameplay authoritative.
2. **Daily quest 3**: ancora `COMPLETION_RUNTIME_DEFERRED`.
3. **Catalog expansion v2** (+20/+30 piani): documentato, non applicato.
4. **PvP/arena/guild/mail/achievements/battlepass/events/AFK rewards live**: tutti DEFERRED.
5. **Flaky historic FAILs** (MD5 baseline lock, AF2-N preflight, ULTRA-COMBO): preesistenti, non legati al Pack 103. Da investigare separatamente.
6. **Public Sync**: pendente. Tag registrato.

## Termine

Pack 103 SUPERPACK chiuso. **Fermo qui come richiesto**: nessun Superpack 104 avviato. In attesa di verifica utente.

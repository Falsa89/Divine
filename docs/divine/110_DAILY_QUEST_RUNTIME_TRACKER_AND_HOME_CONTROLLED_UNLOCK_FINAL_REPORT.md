# 110 — MEGA RELEASE ACCELERATION 99: DAILY QUEST RUNTIME TRACKER AND HOME CONTROLLED UNLOCK — FINAL REPORT

## Approvazione

Stringa di autorizzazione ricevuta: `AUTORIZZO_V110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_UNLOCK_PACK_99`.

## Stato finale

- Master Validation Suite (3 run consecutivi post-commit): **PASS=1605, FAIL=36, MISS=0** — deterministico.
- Smoke E2E Pack 99 (`smoke_v110_pack_99_daily_quest_runtime_tracker_e2e.py`): **31/31 PASS**, zero blocker.
- Rollup Pack 99 (`validate_mega_release_acceleration_99_daily_quest_runtime_tracker_and_home_unlock_rollup.py`): **13/13 PASS**.
- Cleanup test artifacts: REFUSED BY DEFAULT, smoke ha auto-cleanato i suoi documenti.
- Kill switches `.env` post-test: TUTTI rimossi (default OFF).

I 14 nuovi validators del Pack 99 (13 statici + 1 ROLLUP) sono integrati nella suite master, portando il baseline storico da `1591/36/0` a `1605/36/0`, senza alcun nuovo FAIL o regressione storica.

## Implementazione

### Backend — Runtime Tracker server-side (NUOVO)

File: `/app/backend/routes/daily_quest_tracker.py`.

- Collection MongoDB dedicata `daily_quest_progress` con marker `_slc_pack_99_tracker=true`.
- Chiave canonica `(user_id, server_id, quest_id, day_iso)` con indice unico parziale `ux_user_server_quest_day_pack99`.
- Stati: `not_started` / `in_progress` / `completed` / `claimed`.
- Quest ID whitelist: `daily_quest_1`, `daily_quest_2`, `daily_quest_3`.
- Endpoint registrati:
  - `GET  /api/daily-quest/tracker/health` — health snapshot pubblico.
  - `POST /api/daily-quest/tracker/preflight` — crea l'indice unico parziale.
  - `GET  /api/daily-quest/progress` — restituisce lo stato dei quest del giorno UTC per l'utente nello scope `server_id`.
  - `POST /api/daily-quest/progress/complete` — segna lo stato a `completed` (test-only).
- Kill switch dedicato `DAILY_QUEST_TRACKER_ENABLED` (default OFF).
- Completion endpoint **test-only** finché non esiste gameplay authoritative: richiede marker `pack_99_test_artifact=true` sull'utente. I real player ricevono 403 `COMPLETION_ENDPOINT_TEST_ONLY`.
- Server scoping rigoroso: PSP obbligatoria (no fallback `s1`), cross-server B senza PSP → 409 `PLAYER_SERVER_PROFILE_REQUIRED`.
- Idempotency: `update_one` con `$setOnInsert` + `$set state=completed` su upsert; replay completion stesso giorno → `idempotent_replay=true`, nessuna sovrascrittura di `created_at`.
- **Nessun reward grant lato tracker.** Il tracker non importa nemmeno il `reward_source_registry` (anti-leak garantito).
- Day override (`_test_day_override=YYYY-MM-DD`) consentito SOLO se l'utente è marcato `pack_99_test_artifact`.

### Backend — Refactor Daily Quest Claim (PACK 98 → PACK 99)

File: `/app/backend/routes/daily_quest_claim.py`.

- Importa `is_quest_completed` e `mark_quest_claimed` dal nuovo tracker.
- Logica claim aggiornata:
  - Path A (legacy Pack 98 fallback): `test_completion_proof=true` + marker `pack_98_test_artifact` → bypass diretto (preservato per le smoke pre-Pack-99).
  - Path B (Pack 99): consulta `daily_quest_progress` via `_tracker_is_completed(...)`. Se `state != completed/claimed` → 409 `DAILY_QUEST_COMPLETION_REQUIRED` (no client spoofing possibile).
- Dopo grant: transizione tracker `completed → claimed` con `claimed_at` via `_tracker_mark_claimed(...)` (non-blocking se il tracker fallisce, il claim è già registrato a ledger).
- `ready_status` cambiato da `READY_GATED_COMPLETION_REQUIRED` a `READY_TRACKER_GATED`.
- Reward payload invariato: `mission_coins=15`, `honor=8` (PSP soft_currencies, nessun premium).
- Idempotency `reward_claim_ledger` invariata: replay stesso giorno → `idempotent_replay=true`, balance PSP NON modificata.

### Backend — Wiring

- `/app/backend/routes/__init__.py`: import + export `register_daily_quest_tracker_routes`.
- `/app/backend/game_systems.py`: registrazione delle nuove route in `create_game_router(...)`.

### Frontend — DailyQuestClaimButton refactor

File: `/app/frontend/src/components/DailyQuestClaimButton.tsx` (overwrite).

- Consulta `GET /api/daily-quest/progress` PRIMA del claim per leggere lo stato server-side.
- UI gates: invisibile di default in produzione finché `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` non è `true` (default OFF) o `forceVisible=true`.
- Stati renderizzabili: `idle (tracker=...)`, `loading`, `claimed`, `already_claimed`, `completion_required`, `kill_switch_off`, `whitelist_error`, `psp_missing`, `error`.
- Quando lo stato del tracker è `completed` mostra "Riscatta quest"; altrimenti mostra il messaggio di completion richiesta (no chiamata POST inutile).
- Nessun nuovo flag di produzione attivato. Il backend ricontrolla sempre lo stato (no client trust).

### Daily Home Embed (preservato Pack 98)

File: `/app/frontend/src/components/DailyHomeRewardSection.tsx` + `/app/frontend/app/(tabs)/home.tsx` invariati.

- Doppio flag UI mantenuto `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` + `EXPO_PUBLIC_DAILY_HOME_UNLOCK`, entrambi default OFF.
- Nessun leak in produzione (validator `validate_v110_pack_99_daily_home_controlled_unlock_static.py` verifica `.env` frontend).

### Documentazione

- `/app/docs/divine/119_DAILY_QUEST_RUNTIME_TRACKER_SOT.md` — SOT del tracker.
- `/app/data/design/v110_pack_99_daily_quest_runtime_tracker_home_unlock/v110_pack_99_daily_quest_tracker_sot_v1.json` — SOT JSON.
- `/app/data/design/v110_pack_99_daily_quest_runtime_tracker_home_unlock/v110_pack_99_runtime_smoke_e2e_result_v1.json` — risultato smoke E2E.
- `/app/data/design/v110_pack_99_daily_quest_runtime_tracker_home_unlock/v110_pack_99_summary_v1.json` — summary safety flags.

## Validators creati (14)

| # | Nome | Esito |
|---|------|-------|
| 1 | `validate_v110_pack_99_daily_quest_runtime_tracker_sot.py` | PASS |
| 2 | `validate_v110_pack_99_daily_quest_tracker_endpoint.py` | PASS |
| 3 | `validate_v110_pack_99_claim_tracker_enforcement.py` | PASS |
| 4 | `validate_v110_pack_99_reward_payload_preservation.py` | PASS |
| 5 | `validate_v110_pack_99_daily_home_controlled_unlock_static.py` | PASS |
| 6 | `validate_v110_pack_99_frontend_daily_quest_tracker_guard.py` | PASS |
| 7 | `validate_v110_pack_99_runtime_smoke_e2e.py` | PASS |
| 8 | `validate_v110_pack_99_static_anti_leak_guard.py` | PASS |
| 9 | `validate_v110_pack_99_legacy_claim_non_regression.py` | PASS |
| 10 | `validate_v110_pack_99_data_invariants.py` | PASS |
| 11 | `validate_v110_pack_99_cleanup_rollback.py` | PASS |
| 12 | `validate_v110_pack_99_live_readiness_update.py` | PASS |
| 13 | `validate_v110_pack_99_gate_invariant_preservation.py` | PASS |
| 14 | `validate_mega_release_acceleration_99_daily_quest_runtime_tracker_and_home_unlock_rollup.py` | PASS |

## Invarianti certificate (proofs smoke E2E)

| Test | Esito |
|------|-------|
| Default OFF su tracker + claim health endpoint | PASS |
| Register + ensure PSP A + mark Pack 98+99 | PASS |
| Tracker complete con kill switch OFF → 503 | PASS |
| GET progress iniziale → all `not_started` | PASS |
| Claim PRIMA di tracker completion → 409 `DAILY_QUEST_COMPLETION_REQUIRED` (ready_status=`READY_TRACKER_GATED`) | PASS |
| Preflight tracker indices → indice unico parziale creato | PASS |
| Tracker complete con quest invalida → 422 `QUEST_ID_NOT_WHITELISTED` | PASS |
| Tracker complete senza `server_id` → 400 | PASS |
| Tracker complete `daily_quest_1` → state=`completed`, no reward concesso | PASS |
| PSP soft_currencies post-completion: `mission_coins=0`, `honor=0` (zero reward grant on completion) | PASS |
| Replay tracker complete → `idempotent_replay=true` | PASS |
| Claim DOPO completion → grant `+15 mc / +8 honor`, `pack_99_tracker_state_after_claim=claimed`, `completion_proof_used=runtime_tracker` | PASS |
| GET progress post-claim → `state=claimed`, `claimed_at` valorizzato | PASS |
| Replay claim stesso giorno → `idempotent_replay=true`, no double grant (balance PSP invariata) | PASS |
| Quest 2 senza completion → 409 | PASS |
| Quest 2 completion + claim → secondo grant `+15 mc / +8 honor` | PASS |
| Next-day simulation (`_test_day_override=tomorrow`) full loop → `idempotent_replay=false`, grant nuovo | PASS |
| Cross-server B senza PSP → 409 `PLAYER_SERVER_PROFILE_REQUIRED` | PASS |
| Utente unmarked invoca tracker complete → 403 `COMPLETION_ENDPOINT_TEST_ONLY` | PASS |
| Pack 97 daily_login claim ancora funzionante | PASS |
| Pack 96 premium block preservato | PASS |
| Pack 95 story strict preservato | PASS |
| Pack 94 equipment loader preservato | PASS |
| Pack 93 wallet split preservato | PASS |
| Disattivare tracker (kill switch) → tracker complete blocca (503) | PASS |
| Pack 98 legacy bypass `test_completion_proof=true` con marker `pack_98_test_artifact` ancora funziona (compatibilità) | PASS |
| Ripristino kill switches ai valori originali (rimossi dal `.env`) | PASS |
| Cleanup automatic del test user e degli artefatti | PASS |

## Safety vincoli (tutti rispettati)

```
NO reward live activation generale ........... ✓
NO mail rewards live ......................... ✓
NO achievements rewards live ................. ✓
NO battlepass rewards live ................... ✓
NO event rewards live ........................ ✓
NO AFK rewards live .......................... ✓
NO premium/hard currency grant ............... ✓
NO IAP/store/payment change .................. ✓
NO gacha change .............................. ✓
NO broad production grants ................... ✓
NO unmarked test writes ...................... ✓
NO legacy cleanup general execute ............ ✓
NO destructive migration ..................... ✓
NO account-wide server-bound reward/currency . ✓
NO hardcoded server_id="s1" in active path ... ✓
NO reward source outside allowlist ........... ✓
NO double daily reward grant ................. ✓
NO release readiness claim ................... ✓
NO fake_PASS ................................. ✓
NO validator weakening ....................... ✓
NO battle_engine formula rewrite ............. ✓
NO call to /api/battle/simulate from staging . ✓
NO client can fake completion ................ ✓
NO tracker grants reward on completion ....... ✓
```

## Stato consolidato release

- Reward sources player-facing reali: **2** (`daily_login_claim`, `daily_quest_completion_claim`).
- Completion proof per daily quest: **tracker server-side** (`daily_quest_progress` collection con indice unico parziale).
- Completion endpoint: ancora test-only (gameplay authoritative non disponibile → real player non possono completare via API → comportamento safety-by-design invariato).
- Idempotency: doppia (ledger + tracker).
- Cross-server isolation: stretta.
- Frontend default OFF in produzione.
- `release_readiness_claimed=false` (esplicito sia in tracker che in summary JSON).

## Public Sync

`local_commit_only=true`. Nessun push remoto eseguito (no git remote sync). Commit locale registrato in `/app`.

## Termine

Pack 99 chiuso con successo. **Fermo qui come richiesto**: nessun Pack 100 avviato.

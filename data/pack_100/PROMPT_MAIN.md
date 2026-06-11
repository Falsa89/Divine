# MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP

Ciao Emergent, esegui questo mega-pack dopo Pack 99.

## Stato precedente accettato

Pack 99 approvato con caveat corretto:
- Daily quest tracker server-side READY.
- `daily_quest_completion_claim` è `READY_TRACKER_GATED`.
- Tracker storage `daily_quest_progress` usa chiave canonica `user_id + server_id + quest_id + day_iso`.
- Claim daily quest consulta tracker e richiede `state=completed/claimed`.
- Completion endpoint attuale è test-only finché non esiste gameplay authoritative.
- Completion spoofing client-side bloccato.
- Reward daily quest resta `{mission_coins: 15, honor: 8}`, solo PSP soft currencies.
- No double grant via ledger/claim_key.
- Home UI daily resta gated/default OFF.
- Reward live generale OFF.
- Premium/hard grants NO.
- Mail/achievements/battlepass/events/AFK rewards NON attivati.
- Release readiness NON dichiarata.

## Chiarimento canonico server-scope

Tutte le progressioni di gioco sono `account + server`, non account-wide.

Regola canonica:
`user_id + server_id + feature_scope`

Quindi:
- daily quest su S1 non sono completate su S2;
- storia su S1 non sblocca storia su S2;
- Torre su S1 piano 20 non significa Torre piano 20 su S2;
- modalità/eventi/raid/arena/guild/shop/forge devono essere server-scoped;
- nuovo server = progressione fresca.

Ogni route legacy che salva progress account-wide deve essere bloccata, migrata o quarantined prima di diventare player-facing.

## Obiettivo Pack 100

Questo è un MEGAPACK accorpato ma controllato.

Obiettivi:
1. Collegare il tracker daily quest a primi eventi gameplay server-authoritative.
2. Eliminare la dipendenza dal test-only completion per almeno 1-2 daily quest safe.
3. Creare il primo Daily Task Loop reale server-scoped: login daily -> completion event safe -> daily quest completion tracker -> claim via reward ledger -> no double grant -> isolamento S1/S2.
4. Rafforzare il principio `user_id + server_id` su Story/Tower/Daily progress invariants.
5. Preparare, ma NON sbloccare in massa, Torre/story rewards live.
6. Non attivare mail/achievements/battlepass/events/AFK rewards.
7. Non attivare reward live generale.
8. Non concedere premium/hard currency.
9. Non dichiarare release readiness.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- daily quest gameplay completion event bus/server-authoritative tracker bridge;
- completamento daily quest da azioni safe già server-scoped;
- aggiornamento tracker daily quest per eventi reali allowlisted;
- smoke E2E Pack 100;
- test writes su utenti/server marcati Pack 100;
- validator server-scope per Daily/Story/Tower progress.

Stringa richiesta:
`AUTORIZZO_V110_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_PACK_100`

NON autorizzo:
- reward live activation generale;
- mail rewards live;
- achievements rewards live;
- battlepass rewards live;
- event rewards live;
- AFK rewards live;
- premium/hard currency grant;
- IAP/store/payment changes;
- gacha changes;
- broad production grants;
- legacy cleanup generale;
- release readiness claim.

Se approval string manca:
`MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Definizione fondamentale

In Pack 100:
- daily quest completion può avvenire solo da eventi server-authoritative allowlisted.
- Il client non può inviare “completed=true” libero.
- Se un endpoint completion rimane test-only, deve restare marker-gated.
- Le prime daily quest reali devono essere semplici e sicure.
- Consigliato mapping:
  - `daily_quest_1`: claim daily login completed;
  - `daily_quest_2`: story strict progress/battle preview safe completed, se route già server-scoped;
  - `daily_quest_3`: safe action solo se completamente server-scoped, altrimenti deferred.
- Se una daily quest non ha evento safe, resta `COMPLETION_RUNTIME_DEFERRED`.
- Reward live generale resta false.
- Source reali restano solo `daily_login_claim` e `daily_quest_completion_claim`.
- Progress story/tower/daily deve essere server-scoped: S1 non può contaminare S2.

## Regola anti-pack falso

Questo pack NON può chiudere READY se:
- daily quest viene completata da client free proof;
- tracker non verifica user_id + server_id + quest_id + day;
- daily quest completata su S1 risulta completata su S2;
- story/tower progress validator non verifica server-scope;
- si attivano reward live generali;
- mail/achievement/battlepass/event/AFK rewards vengono attivati;
- premium/hard currency può essere grantata;
- smoke E2E non prova S1/S2 isolation;
- fake_PASS o validator weakening.

## Track obbligatorie

A. Baseline verification: Master Suite 3 volte, atteso circa `1605/36/0`.

B. Server-Scoped Progress Canon SOT: creare `docs/divine/120_SERVER_SCOPED_PROGRESS_CANON_SOT.md`; daily/story/tower progress devono essere user_id+server_id+scope; route senza server_id devono bloccare/defer.

C. Daily Quest Gameplay Event Bus / Bridge: creare helper interno `backend/utils/daily_quest_events.py` con `record_daily_quest_event(user_id, server_id, event_type, payload, source_route, day_iso=None)`. Deve validare PSP/server_id, mappare eventi a quest_id allowlist, scrivere solo tracker, non dare reward.

D. First Real Daily Quest Event Mapping: daily_login_claim_success -> daily_quest_1. Optional story_strict_progress_success -> daily_quest_2 solo se sicuro/server-scoped. daily_quest_3 deferred se non c’è evento sicuro.

E. Daily Login -> Daily Quest Completion Hook: dopo successful `daily_login_claim`, registra evento `daily_login_claim_success`; completa daily_quest_1 solo per lo stesso user/server/day; idempotente; nessun secondo reward.

F. Story/Tower Server-Scope Audit and Guards: audit route story/tower; progress player-facing deve essere server-scoped o blocked/deferred; se tower non pronto usare `TOWER_PROGRESS_SERVER_SCOPE_DEFERRED`; nessun reward story/tower live.

G. Daily Quest Claim Real-Player Status Update: health/readiness deve indicare tracker ready, daily_quest_1 real completion event ready, daily_quest_2/3 honest status. Claim reale solo se tracker completed da server event.

H. Frontend Daily Task Loop UI Guard: UI mostra daily login, daily quest progress, claim quando completed, locked/deferred; dietro flag default OFF; selected server required; S1/S2 switching refresh; no false success.

I. Kill Switches and Flags: REWARD_CLAIM_LEDGER_LIVE_ENABLED, DAILY_LOGIN_CLAIM_ENABLED, DAILY_QUEST_CLAIM_ENABLED, DAILY_QUEST_TRACKER_ENABLED e frontend flags default OFF; smoke abilita e ripristina.

J. Runtime Smoke E2E: creare `backend/scripts/smoke_v110_pack_100_daily_task_loop_e2e.py`; prova S1/S2 empty, daily login su S1 completa daily_quest_1 solo S1, claim S1 OK, replay no double grant, claim S2 blocked, invalid quest 422, spoof blocked, premium blocked/ignored, story/tower audit, flags OFF default, Pack 91-99 preserved, cleanup.

K. Static Server-Scope Anti-Leak Guard: fail se daily/story/tower progress active path manca server_id, client può completare freely, hardcoded s1, progress solo user_id, users.gold/gems, mail/achievement/battlepass/event/AFK live, reward_live_general true, premium/hard allowed.

L. Legacy Claim/Progress Non-Regression: solo daily_login + daily_quest real player-facing claim sources; story/tower rewards non broadly enabled; altri sistemi blocked/deferred unless QA/test.

M. Data Invariants: no production broad grants, no unmarked test writes, no premium/hard grants, no reward live general, no gacha/IAP/payment, no legacy cleanup, no destructive migration, Pack 84-99 preserved.

N. Cleanup/Rollback: `backend/scripts/cleanup_v110_pack_100_test_artifacts.py`, refuse-by-default, dry-run default, `--apply`, reset kill switches, no production users.

O. Live Readiness Update: `daily_task_loop_ready=true` only if daily login -> daily quest -> claim smoke green; `daily_quest_1_real_completion_ready=true`; daily_quest_2/3 only if truly server-authoritative; reward_live_general=false; release_readiness_claimed=false.

P. MD5 / Critical Baseline Rebase: historical refs, replacement invariants, no validator weakening, reason daily task loop gameplay event completion.

Q. Gate/Runtime Invariant Preservation: Pack 84-99 preserved, POSTQA_D locked, no battle_engine rewrite, no `/api/battle/simulate` regression, no fake_PASS.

R. Final 3-run suite.

S. Validators + Runner Integration: rollup `validate_mega_release_acceleration_100_daily_quest_gameplay_completion_events_first_real_task_loop_rollup.py`; sentinel `PUBLIC_SYNC_TAG_v110_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP`.

## Forbidden Scope

NO reward live activation generale
NO mail rewards live
NO achievements rewards live
NO battlepass rewards live
NO event rewards live
NO AFK rewards live
NO premium/hard currency grant
NO IAP/store/payment change
NO gacha change
NO broad production grants
NO unmarked test writes
NO legacy cleanup general execute
NO destructive migration
NO account-wide server-bound reward/currency grant
NO hardcoded server_id="s1" in active daily/story/tower/reward path
NO reward source outside daily_login/daily_quest allowlist
NO double daily reward grant
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

## Expected verdicts

If daily login -> daily quest -> claim loop green:
`MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If tracker/event bridge unsafe or client spoof possible:
`MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_CONDITIONAL_BLOCKERS_CLIENT_COMPLETION_OR_SERVER_SCOPE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If story/tower server-scope audit finds player-facing leak:
`MEGA_RELEASE_ACCELERATION_100_SERVER_SCOPE_PROGRESS_CONDITIONAL_BLOCKERS_STORY_TOWER_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final Report Required

Create:
`docs/divine/110_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP_FINAL_REPORT.md`

Must include verdict, commit hash, git diff --stat, baseline/final suite, server-scoped progress canon SOT, daily quest event bridge, first daily quest event mapping, daily login completion hook, story/tower server-scope audit, daily quest claim real-player status update, frontend daily task loop UI guard, kill switches/flags, runtime smoke E2E, static server-scope anti-leak guard, legacy claim/progress non-regression, data invariants, cleanup/rollback, live readiness update, MD5 rebase, gate preservation, daily task loop ready status, daily_quest_1 real completion event status, S1/S2 progress isolation, story/tower server-scope status, reward live general remains false, no premium/hard grants, no double daily quest reward, only daily_login + daily_quest sources, Pack 91-99 preserved, deferred blockers and next step.

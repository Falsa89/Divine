# MEGA_RELEASE_ACCELERATION_99_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_CONTROLLED_UNLOCK

Ciao Emergent, esegui questo mega-pack dopo Pack 98.

## Stato precedente accettato

Pack 98 approvato:
- Daily login Home unlock READY ma default OFF.
- `daily_quest_completion_claim` aggiunto come seconda source reale, ma in stato `READY_GATED_COMPLETION_REQUIRED`.
- Daily quest endpoint richiede completion proof; per utenti reali ritorna `DAILY_QUEST_COMPLETION_REQUIRED`.
- Bypass test-only consentito solo con marker `pack_98_test_artifact=true`.
- Reward daily quest fisso `{mission_coins: 15, honor: 8}`, solo PSP soft currencies.
- Home embed gated tramite `DailyHomeRewardSection`, con doppio flag: `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` + `EXPO_PUBLIC_DAILY_HOME_UNLOCK`, entrambi default OFF.
- Reward live generale OFF. Premium/hard grants NO.
- Mail/achievements/battlepass/events/AFK rewards NON attivati.
- Pack 91/93/94/95/96/97 preservati.
- Release readiness NON dichiarata.
- Caveat Pack 98: suite finale `1591/36/0`, +2 optional fail non-Pack-98/pre-esistenti, accettati come caveat non regressivo.

## Obiettivo Pack 99

Questo è un MEGAPACK accorpato ma controllato.

Obiettivi:
1. Implementare il runtime tracker server-side per il completamento delle daily quest.
2. Sbloccare `daily_quest_completion_claim` da `READY_GATED_COMPLETION_REQUIRED` a claim reale sicuro SOLO se il tracker conferma il completamento.
3. Mantenere daily quest claim ledger/idempotency/no double claim.
4. Preparare Daily Login Home controlled unlock con flag ancora default OFF, ma smoke/preview completa.
5. Non aggiungere nuove source reali oltre `daily_login_claim` e `daily_quest_completion_claim`.
6. Non attivare mail/achievements/battlepass/events/AFK rewards.
7. Non attivare reward live generale.
8. Non concedere premium/hard currency.
9. Non dichiarare release readiness.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- daily quest completion runtime tracker;
- endpoint/progress state server-scoped per completamento daily quest;
- collegamento sicuro tra completion tracker e `daily_quest_completion_claim`;
- preview/smoke del daily login Home unlock;
- test writes su utenti/server marcati Pack 99;
- smoke E2E Pack 99;
- feature flags/kill switches daily claim e daily quest.

Stringa richiesta:
`AUTORIZZO_V110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_UNLOCK_PACK_99`

NON autorizzo:
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

## Definizione fondamentale

In Pack 99:
- `daily_quest_completion_claim` può diventare realmente claimable per player solo se server_id, PSP, quest_id whitelisted, daily quest completion tracker completed, reward ledger/idempotency e kill switches passano.
- Nessun claim daily quest può basarsi solo su quest_id whitelisted.
- Nessun client proof libero deve sbloccare reward reale.
- `_test_day_override` o test completion bypass devono restare test-only marcati.
- Reward live generale resta false.
- Source reali totali restano solo `daily_login_claim` e `daily_quest_completion_claim`.

## Track obbligatorie

A. Baseline verification: Master Suite 3 volte prima delle modifiche. Atteso circa `1591/36/0`.

B. Daily Quest Runtime Tracker SOT: creare `docs/divine/119_DAILY_QUEST_RUNTIME_TRACKER_SOT.md` e JSON SOT. Definire storage PSP subdocument o collection server-scoped, key `(user_id, server_id, quest_id, day_key)`, quest whitelist `daily_quest_1/2/3`, status not_started/in_progress/completed/claimed, completion source server-side only.

C. Daily Quest Progress Runtime Endpoint: `GET /api/daily-quest/progress?server_id=<sid>` e/o `POST /api/daily-quest/progress/complete?server_id=<sid>`. Auth, server_id, PSP, quest_id whitelist, server-scoped, idempotent, no reward grant on completion. If no real gameplay condition exists, completion endpoint must be test-only and refuse real users.

D. Claim Endpoint Completion Enforcement: update `POST /api/daily-quest/claim`; check tracker completed state; if not completed return `DAILY_QUEST_COMPLETION_REQUIRED`; after claim mark claimed; replay no second grant; no users.gold/gems.

E. Daily Quest Reward Payload Preservation: keep `{mission_coins: 15, honor: 8}`, server-side fixed, client payload ignored, PSP.soft_currencies only, no gold/gems/pulls/inventory/equipment/hero.

F. Daily Login Home Controlled Unlock Smoke/Preview: Home integration stays gated; both frontend flags default false; smoke/preview can render with flags; no production leak.

G. Frontend Daily Quest Progress/Claim UI Guard: UI not production-visible by default; use selected server_id; show completion_required if tracker incomplete; claim only when completed; no false success.

H. Kill Switches and Flags: all defaults OFF; smoke can enable and restore; health reports tracker ready, claim_executable false by default, ready_status after Pack 99.

I. Runtime Smoke E2E: `backend/scripts/smoke_v110_pack_99_daily_quest_runtime_tracker_e2e.py`; test claim before completion blocked, completion marks completed, claim succeeds, replay no double grant, cross-server no leak, invalid quest 422, payload ignored, next-day simulation test-controlled, cleanup verified.

J. Static Tracker/Claim Anti-Leak Guard: fail if claim can grant without tracker, client can set completed freely, users.gold/gems writes, hardcoded s1, progress lacks server_id, Home visible without flags, unrelated claims live, premium reward allowed.

K. Legacy Claim Source Non-Regression: only daily_login + daily_quest are real player-facing sources; mail/achievements/battlepass/AFK/events/shops/soul/earn remain blocked/deferred.

L. Data Invariants / Forbidden Mutation Proof: no production broad grants, unmarked writes, premium grants, reward_live_general, gacha/IAP/payment, legacy cleanup, destructive migration; Pack 84-98 preserved.

M. Cleanup / Rollback: `backend/scripts/cleanup_v110_pack_99_test_artifacts.py`, refuse-by-default, dry-run default, `--apply`, only Pack 99 marked artifacts, reset kill switches.

N. Live Readiness Update: tracker ready only if tracker+claim+smoke green; daily_login_home_unlock remains gated/default off; reward_live_general=false; release_readiness_claimed=false.

O. MD5 / Critical Baseline Rebase: historical refs, replacement invariants, no validator weakening.

P. Gate/Runtime Invariant Preservation: Pack 84-98 preserved; POSTQA_D locked; no battle_engine rewrite; no `/api/battle/simulate` regression.

Q. Final 3-run suite.

R. Validators + runner integration: rollup `validate_mega_release_acceleration_99_daily_quest_runtime_tracker_and_home_unlock_rollup.py`; sentinel `PUBLIC_SYNC_TAG_v110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_CONTROLLED_UNLOCK`.

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
NO hardcoded server_id="s1" in active daily/reward path
NO reward source outside daily_login/daily_quest allowlist
NO double daily reward grant
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

## Expected verdicts

If tracker + claim enforcement + smoke green:
`MEGA_RELEASE_ACCELERATION_99_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_CONTROLLED_UNLOCK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If tracker unsafe or client can fake completion:
`MEGA_RELEASE_ACCELERATION_99_DAILY_QUEST_RUNTIME_TRACKER_CONDITIONAL_BLOCKERS_CLIENT_COMPLETION_OR_UNSAFE_CLAIM_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If Home unlock leaks UI:
`MEGA_RELEASE_ACCELERATION_99_HOME_CONTROLLED_UNLOCK_CONDITIONAL_BLOCKERS_PRODUCTION_UI_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final Report Required

Create:
`docs/divine/110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_CONTROLLED_UNLOCK_FINAL_REPORT.md`

Must include verdict, commit hash, git diff stat, baseline/final suite, tracker SOT, progress endpoint, claim completion enforcement, reward payload preservation, Home controlled unlock, frontend guard, kill switches, smoke, anti-leak guard, non-regression, data invariants, cleanup, live readiness, MD5, gate preservation, explicit statements for tracker status, real-player claim status, reward live general false, no premium grants, no double reward, only daily_login + daily_quest sources, Pack 91/93/94/95/96/97/98 preserved, deferred blockers and next step.

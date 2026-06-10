# MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE_MEGAPACK

Ciao Emergent, esegui questo mega-pack dopo Pack 97.

## Stato precedente accettato

Pack 97 approvato:
- `daily_login_claim` è la prima e unica source reale player-facing aggiunta.
- Reward fisso `{mission_coins: 10, honor: 5}`, server-scoped, non-premium.
- Endpoint `POST /api/daily-login/claim` con doppio kill switch: `REWARD_CLAIM_LEDGER_LIVE_ENABLED` + `DAILY_LOGIN_CLAIM_ENABLED`.
- Entrambi i kill switch default OFF.
- Daily claim usa claim_key server-side `daily_login_<server_id>_<YYYY-MM-DD UTC>`.
- Unique partial index `(user_id, server_id, claim_key)` per `daily_login_claim`.
- `_test_day_override` consentito solo per `pack_97_test_artifact=true`.
- Frontend minimale `DailyLoginClaimButton.tsx` + preview route, ma default hidden.
- Reward live generale OFF.
- Premium/hard grants NO.
- Mail/achievements/battlepass/events/AFK rewards NON attivati.
- Pack 91/93/94/95/96 preservati.
- Release readiness NON dichiarata.

## Obiettivo Pack 98

Questo è un MEGAPACK accorpato ma ancora controllato.

Obiettivi:
1. Preparare lo sblocco controllato di `daily_login_claim` sulla Home, ma dietro flag esplicito.
2. Aggiungere una sola seconda source reale low-risk: `daily_quest_completion_claim`.
3. Collegare `daily_quest_completion_claim` al reward ledger/idempotency/claim registry.
4. Garantire no double claim per quest giornaliera/utente/server/giorno.
5. Mantenere rewards piccole, non-premium e server-scoped.
6. Non attivare mail/achievements/battlepass/events/AFK.
7. Non attivare reward live generale.
8. Non concedere premium/hard currency.
9. Non dichiarare release readiness.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- home unlock controllato/gated di `daily_login_claim`;
- aggiunta source `daily_quest_completion_claim`;
- endpoint/registry/validator changes necessari;
- frontend consumer minimale/gated per daily login + daily quest;
- test writes su utenti/server marcati Pack 98;
- smoke E2E Pack 98;
- feature flag/kill switch per daily quest claim.

Stringa richiesta:
`AUTORIZZO_V110_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_PACK_98`

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

Se approval string manca:
`MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Definizione fondamentale

In Pack 98:
- `daily_login_claim` può essere esposto sulla Home solo dietro flag frontend + backend kill switches.
- `daily_quest_completion_claim` è l'unica nuova source reale aggiunta.
- Quest daily claim deve essere ledger/idempotency mandatory.
- Una daily quest non può dare doppio reward nello stesso giorno per user/server/quest_id.
- Reward deve essere server-scoped e non-premium.
- Qualunque source non allowlisted resta bloccata.
- Reward live generale resta false.
- Non sbloccare sistemi claim multipli.

## Regola anti-pack falso

Questo pack NON può chiudere READY se:
- Home mostra claim senza flag e senza server scope;
- daily_quest_completion_claim non usa ledger;
- daily quest può fare double claim;
- claim cross-server può vedere o consumare claim di altro server;
- frontend mostra successo senza backend claim;
- premium/hard currency può essere grantata;
- mail/achievements/battlepass/events/AFK vengono attivati insieme;
- kill switch default diventa unsafe;
- smoke E2E non prova Home gated state, first quest claim, replay, same-day different token, cross-server no leak;
- fake_PASS o validator weakening.

## Track obbligatorie

A. Baseline verification: Master Suite 3 volte prima delle modifiche. Atteso circa `1574/34/0`.

B. Daily Home Unlock Policy / SOT: creare `docs/divine/118_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOT.md`; Home claim visibile solo con selected server + frontend flag + backend state; no silent s1; locked/deferred state quando kill switch OFF.

C. Daily login Home integration: usare `DailyLoginClaimButton`, `useServerScope`, `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=false` default; no mail/achievement/battlepass/event/AFK claim UI; refetch wallet/PSP dopo successo.

D. Daily quest claim source SOT: source `daily_quest_completion_claim`; daily quest id `daily_quest:<quest_id>:<YYYY-MM-DD UTC>`; server-side claim_key `daily_quest_<server_id>_<quest_id>_<YYYY-MM-DD UTC>`; completamento quest richiesto o blocker onesto `DAILY_QUEST_COMPLETION_REQUIRED`.

E. Reward registry daily quest source addition: `server_scoped=true`, `idempotency=mandatory`, `DAILY_QUEST_CLAIM_ENABLED` default OFF, no premium, soft currencies only, small cap.

F. Daily quest claim endpoint/integration: eventuale `POST /api/daily-quest/claim?server_id=<sid>`; auth, PSP, quest_id allowlisted/test-controlled, completion proof o blocker, claim_key server-side, ledger required, no users.gold/gems, kill switches block.

G. Daily quest reward payload guard: recommended `mission_coins: 15` oppure `honor: 5`; no gold/gems, no pulls, no hero/equipment/inventory grants.

H. Frontend daily quest consumer guard: preview/test UI only unless completion runtime exists; pass server_id + quest_id; no false success; not production-visible by default.

I. Kill switches and flags: `REWARD_CLAIM_LEDGER_LIVE_ENABLED=false`, `DAILY_LOGIN_CLAIM_ENABLED=false`, `DAILY_QUEST_CLAIM_ENABLED=false`, `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=false`, optional `EXPO_PUBLIC_DAILY_QUEST_CLAIM_UI_ENABLED=false`; smoke enables/restores.

J. Runtime smoke E2E: create `backend/scripts/smoke_v110_pack_98_daily_home_quest_claim_e2e.py`; marker `pack_98_test_artifact=true`; prove Home gated state, daily login preserved, daily quest first claim or honest blocker, replay no double grant, same quest/day different token no double grant, next-day simulation test-only, server B isolation, unknown source block, premium block, kill switches OFF block, Pack 91/93/94/95/96/97 preserved, cleanup.

K. Static anti-double-claim / anti-ui-leak guard: fail if daily home visible without flag, daily quest grants without ledger, same daily quest grants multiple times, users.gold/gems write, hardcoded s1, frontend lacks server_id, kill switch unsafe, mail/achievement/battlepass/event/AFK accidentally live, premium allowed.

L. Legacy claim source non-regression: only daily_login_claim + daily_quest_completion_claim are real player-facing sources; all others remain blocked/deferred unless QA/test source.

M. Data invariants: no production broad grants, no unmarked test writes, no premium/hard grants, reward_live_general=false, no gacha/IAP, no legacy cleanup, Pack 84-97 preserved.

N. Cleanup/rollback: refuse-by-default `cleanup_v110_pack_98_test_artifacts.py`, dry-run, `--apply` required, reset kill switches.

O. Live readiness update: `daily_login_home_unlock_ready`, `daily_quest_completion_claim_ready`, `reward_live_general=false`, `premium_grants=false`, `release_readiness_claimed=false`.

P. MD5 / critical baseline rebase: historical refs, replacement invariants, no validator weakening.

Q. Gate/runtime invariant preservation: Pack 84-97 preserved, POSTQA_D locked, no battle_engine rewrite, no `/api/battle/simulate` regression.

R. Final 3-run suite: REQUIRED=0, MISS=0, OPTIONAL<=baseline or explained honestly, deterministic.

S. Validators + runner integration: rollup `validate_mega_release_acceleration_98_daily_home_unlock_and_daily_quest_claim_source_rollup.py`; sentinel `PUBLIC_SYNC_TAG_v110_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE`.

## Forbidden scope

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
NO reward source outside allowlist
NO double daily reward grant
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

## Expected verdicts

If Home gated unlock + daily quest source + smoke green:
`MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If daily quest source unsafe or double claim possible:
`MEGA_RELEASE_ACCELERATION_98_DAILY_QUEST_CLAIM_SOURCE_CONDITIONAL_BLOCKERS_DOUBLE_CLAIM_OR_UNSAFE_GRANT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If Home unlock leaks production UI:
`MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_CONDITIONAL_BLOCKERS_PRODUCTION_UI_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final report required

Create:
`docs/divine/110_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE_FINAL_REPORT.md`

Must include: verdict, commit hash, git diff --stat, baseline/final suite, daily home unlock SOT, daily login Home integration, daily quest claim SOT, reward registry daily quest source, daily quest endpoint/integration, reward payload guard, frontend daily quest guard, kill switch/flags, runtime smoke E2E, static anti-double-claim/UI leak guard, legacy claim non-regression, data invariants, cleanup/rollback, live readiness update, MD5 rebase, gate preservation, explicit daily login Home unlock status, daily_quest_completion_claim status, reward live general remains false, no premium/hard grants, no double daily quest reward, only daily_login + daily_quest are real player-facing claim sources, Pack 91/93/94/95/96/97 preserved, deferred blockers and next step.

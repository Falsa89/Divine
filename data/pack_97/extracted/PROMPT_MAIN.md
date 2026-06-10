# MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_MEGAPACK

Ciao Emergent, esegui questo mega-pack dopo Pack 96.

## Stato precedente accettato

Pack 96 approvato:
- Reward ledger live-gated infrastructure READY.
- `POST /api/rewards/claim` esiste, ma kill switch default OFF.
- Allowlist Pack 96 limitata a:
  - `qa_controlled_soft_currency_claim`;
  - `story_progress_marker_claim`.
- Idempotency ledger attivo e replay-safe.
- Unique index su `reward_claim_ledger` verificato.
- No double grant verificato via smoke.
- Unknown source blocked.
- Premium/hard currency grants blocked.
- Pack 91 inventory, Pack 93 wallet spend, Pack 94 equipment, Pack 95 story strict preservati.
- Reward live generale OFF.
- Release readiness NON dichiarata.

## Obiettivo Pack 97

Questo è un MEGAPACK accorpato ma molto controllato.

Obiettivi:
1. Introdurre la prima source reale player-facing: `daily_login_claim`.
2. Collegarla al reward claim ledger live-gated di Pack 96.
3. Attivare una UI/frontend reward claim consumer minima e gated.
4. Garantire idempotency giornaliera, no double grant, server isolation e kill switch.
5. Limitare le rewards a server-bound soft currencies piccole e non-premium.
6. Non attivare mail/achievements/battlepass/events in massa.
7. Non attivare reward live generale.
8. Non concedere premium/hard currency.
9. Non dichiarare release readiness.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- aggiunta source `daily_login_claim`;
- endpoint/registry/validator changes necessari;
- frontend consumer minimale/gated per daily login claim;
- test writes su utenti/server marcati Pack 97;
- smoke E2E Pack 97;
- eventuale feature flag/kill switch per daily claim.

Stringa richiesta:
`AUTORIZZO_V110_DAILY_LOGIN_CLAIM_AND_FRONTEND_UNLOCK_PACK_97`

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
`MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Definizione fondamentale

In Pack 97:
- `daily_login_claim` è la sola nuova real player-facing source.
- Daily claim deve usare ledger/idempotency obbligatoria.
- Una giornata/server/utente non può ricevere doppio claim.
- Reward deve essere server-scoped e non-premium.
- Se kill switch OFF, claim deve bloccare.
- Reward live generale resta false.
- Non sbloccare sistemi claim multipli.

## Regola anti-pack falso

Questo pack NON può chiudere READY se:
- daily_login_claim non usa ledger;
- daily claim può essere doppio nello stesso giorno;
- claim cross-server può vedere o consumare claim di altro server;
- frontend mostra successo senza backend claim;
- premium/hard currency può essere grantata;
- mail/achievements/battlepass/events vengono attivati insieme;
- kill switch default diventa unsafe;
- smoke E2E non prova first claim + replay + next-day simulation/key + cross-server block/no leak;
- fake_PASS o validator weakening.

## Track obbligatorie

A. Baseline verification: Master Suite 3 volte prima delle modifiche. Atteso circa `1557/34/0`.

B. Daily login claim design/SOT:
creare `docs/divine/117_DAILY_LOGIN_CLAIM_SOT.md` e JSON SOT. Definire daily key `YYYY-MM-DD` UTC o server day, idempotency, no double claim per user/server/day, small non-premium server-scoped reward, flag separato da reward_live_general.

C. Reward registry source addition:
aggiungere `daily_login_claim`, `server_scoped=true`, `idempotency=mandatory`, live controlled by `DAILY_LOGIN_CLAIM_ENABLED`, no premium, soft currencies only, small cap.

D. Daily claim endpoint/integration:
usare `/api/rewards/claim` o thin endpoint `/api/daily-login/claim?server_id=<sid>`. Requirements: auth, server_id, PSP, daily source, daily instance server-side/validated, idempotency token, ledger, duplicate same day no second grant, no users.gold/gems.

E. Daily claim reward payload guard:
initial reward payload low-risk server soft currency only, e.g. `mission_coins: 10` or `honor: 5`; no gold/gems, no pulls, no hero/equipment/inventory grant.

F. Frontend daily claim consumer unlock:
minimal UI entrypoint; use `useServerScope`; pass server_id and idempotency_token; handle already claimed/replay/kill switch/deferred; refetch wallet; no mail/achievement/battlepass/event claims.

G. Kill switch and flags:
global `REWARD_CLAIM_LEDGER_LIVE_ENABLED` default remains OFF unless explicit local/test override; daily source has own flag `DAILY_LOGIN_CLAIM_ENABLED`; smoke enables/restores; health state documented.

H. Runtime smoke E2E:
script `backend/scripts/smoke_v110_pack_97_daily_login_claim_e2e.py`. Test user `pack97_test_user_*@test.com`, marker `pack_97_test_artifact=true`. Prove first claim, balance PSP only, replay no second grant, same day/different token no double claim, server B no leak, next-day test simulation if controlled, unknown source blocked, premium blocked, kill switch OFF blocks, Pack 91/93/94/95/96 preserved, cleanup.

I. Static daily anti-double-claim guard:
fail if daily can grant without ledger, same daily can grant multiple times, users.gold/gems writes, hardcoded s1, frontend lacks server_id, kill switch unsafe, other claim sources accidentally live, premium reward allowed.

J. Legacy claim source non-regression:
only daily_login_claim new source live/allowlisted; mail/achievements/battlepass/AFK/events/shops/soul/earn remain blocked/deferred unless pre-existing QA.

K. Data invariants:
no production broad grants; no unmarked test writes; no premium/hard grants; reward_live_general=false; no gacha/IAP; no legacy cleanup; Pack 84-96 preserved.

L. Cleanup/rollback:
script refuse-by-default `cleanup_v110_pack_97_test_artifacts.py`, dry-run, --apply required, reset kill switches.

M. Live readiness update:
daily_login_claim_ready only if endpoint+frontend+smoke green; reward_live_general=false; premium_grants=false; release_readiness_claimed=false.

N. MD5 / critical baseline rebase:
historical refs, replacement invariants, no validator weakening, reason first real daily login claim and frontend unlock.

O. Gate/runtime invariant preservation:
Pack 84-96 preserved, POSTQA_D locked unless explicitly intended, no battle_engine rewrite, no /api/battle/simulate regression.

P. Final 3-run suite.

Q. Validators + runner integration:
rollup `validate_mega_release_acceleration_97_first_real_claim_source_and_frontend_reward_unlock_rollup.py`.
Sentinel: `PUBLIC_SYNC_TAG_v110_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK`

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

If daily source + frontend + smoke green:
`MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If daily source unsafe or double claim possible:
`MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_CONDITIONAL_BLOCKERS_DAILY_DOUBLE_CLAIM_OR_UNSAFE_GRANT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If frontend unlock incomplete:
`MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_CONDITIONAL_BLOCKERS_FRONTEND_CLAIM_UNLOCK_INCOMPLETE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final report required

Create:
`docs/divine/110_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_FINAL_REPORT.md`

Must include:
- verdict;
- commit hash;
- git diff --stat;
- baseline/final suite;
- daily login claim SOT;
- reward registry daily source;
- daily claim endpoint;
- reward payload guard;
- frontend consumer unlock;
- kill switch/flags;
- runtime smoke E2E;
- static daily anti-double-claim guard;
- legacy claim non-regression;
- data invariants;
- cleanup/rollback;
- live readiness update;
- MD5 rebase;
- gate preservation;
- explicit statement: daily_login_claim live/ready status;
- explicit statement: reward live general remains false;
- explicit statement: no premium/hard grants;
- explicit statement: no double daily reward;
- explicit statement: only daily source added as real player-facing source;
- explicit statement: Pack 91/93/94/95/96 preserved;
- deferred blockers and next step.

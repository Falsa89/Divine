# MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK

Ciao Emergent, esegui questo mega-pack dopo Pack 94.

## Stato precedente accettato

Pack 94 approvato:
- Equipment backfill `user_equipment.server_id` eseguito con autorizzazione.
- Equipment loader `/api/user/equipment?server_id=...` promosso a strict server-scoped reale.
- Equipment equip/unequip promosso a strict server-scoped reale.
- Legacy `earn-pvp` e `earn-guild` con `server_id` quarantined con `LEGACY_CURRENCY_QUARANTINE_DEFERRED`.
- Reward/progress live OFF.
- Legacy cleanup generale NON eseguito.
- Release readiness NON dichiarata.

Deferred blocker ancora attivi:
- reward claim ledger live execute;
- story progress write strict scope execute;
- legacy `earn-mission`, `earn-dimension`, `/shops/buy`, `soul-forge/retire`;
- forge upgrade/fuse endpoints non implementati;
- frontend equipment POSTQA_D unlock;
- legacy cleanup pre-Pack-86 `user_heroes`.

## Obiettivo Pack 95

Questo è un MEGAPACK accorpato.

Obiettivi:
1. Implementare reward claim ledger runtime-safe, idempotente e live-gated.
2. Promuovere story progress write strict scope in modalità sicura/testata, senza reward grant live.
3. Quarantinare o promuovere in modo server-safe i legacy reward/currency paths:
   - `earn-mission`;
   - `earn-dimension`;
   - `/shops/buy`;
   - `soul-forge/retire`.
4. Preparare claim/reward guards comuni per futuri mail/achievements/daily/battlepass/story/battle/afk/events.
5. Eseguire smoke E2E test-only con idempotency/replay/no double grant.
6. Preservare Pack 91 inventory, Pack 93 wallet spend, Pack 94 equipment strict.
7. NO reward live activation generale.
8. NO premium/hard currency grants.
9. NO release readiness claim.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- runtime code per reward ledger pre-live/live-gated;
- runtime code per story progress write strict guard;
- runtime code per legacy reward/currency quarantine o server-safe conversion;
- test writes su utenti/server marcati Pack 95;
- smoke E2E su test artifacts;
- ledger/index creation solo se safe/idempotent e documentata.

Stringa richiesta:
`AUTORIZZO_V110_REWARD_LEDGER_STORY_WRITE_LEGACY_GUARDS_TEST_ONLY_PACK_95`

NON autorizzo:
- reward live activation generale;
- grants su utenti reali;
- premium/hard currency grant;
- broad production DB writes;
- legacy cleanup generale;
- IAP/store/payment changes;
- gacha changes;
- release readiness claim.

Se approval string manca:
`MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Regola anti-pack falso

Questo pack NON può chiudere READY se:
- crea solo docs/JSON senza runtime guards;
- chiama ledger live ma non testa idempotency/replay;
- reward path può fare double grant;
- story progress write muta account-wide progress;
- legacy earn/shop/soul paths restano attivi player-facing senza server_id guard/quarantine;
- muta premium/hard currency;
- abilita reward live generale;
- fake_PASS o validator weakening.

## Decisioni canoniche

- Reward claim richiede idempotency ledger prima di qualunque live activation.
- Story progress operativo è server-scoped.
- Story progress write può avanzare solo su PSP/story server-scoped, non su users.story_progress account-wide.
- Reward/currency grants server-bound devono essere server-scoped e idempotenti.
- Hard/premium currency non si concede in questo pack.
- Legacy reward/currency paths non sicuri devono essere quarantined/guarded, non lasciati player-facing.
- Nessun nuovo server eredita reward/story/currency progress da S1.

## Track obbligatorie

A. Baseline verification: Master Suite 3 volte, atteso circa `1527/29/0/0`.

B. Reward/legacy write path audit:
auditare `earn-mission`, `earn-dimension`, `earn-pvp`, `earn-guild`, `/shops/buy`, `soul-forge/retire`, story/battle progress write, mail/achievements/daily/battlepass/afk/event claim endpoints se presenti, e ogni grant/write a users.gold, users.gems, PSP.soft_currencies, inventory, user_heroes, story progress, reward ledgers.

C. Reward claim ledger runtime foundation:
collection `reward_claim_ledger` o nome canonico; idempotency key `(user_id, server_id, reward_source, reward_instance_id, idempotency_token)`; unique index safe/idempotent; replay senza secondo grant; audit fields completi; no reward live by default.

D. Story progress write strict scope:
`POST /api/story/battle?server_id=<sid>` o route equivalente; server_id required; PSP check; write solo PSP.story_progress o storage server-bound; idempotency token required; no reward/currency/inventory grant; no users.story_progress; replay idempotente.

E. Legacy currency earn quarantine/server-safe conversion:
gestire earn-mission, earn-dimension, earn-pvp, earn-guild. Se `server_id` presente: conversione PSP.soft_currencies con ledger oppure blocker `LEGACY_CURRENCY_QUARANTINE_DEFERRED`. Se legacy no-server resta, marcarlo deprecated/non-player-facing o flag dev. No users.gold/gems per server-bound rewards; no hardcoded s1.

F. Shops buy quarantine/server-safe guard:
server-bound shop purchase richiede server_id, usa Pack 93 wallet spend ledger o defer; no account-wide spend per server-bound goods; no inventory write senza server_id; blocker onesto se unsafe.

G. Soul forge retire quarantine/server-safe guard:
retire richiede server_id; hero selector user_id+server_id+hero_id; reward output via ledger o defer; no cross-server hero destruction; blocker se unsafe.

H. Frontend reward/story/legacy consumer guard:
frontend passa server_id e idempotency_token dove necessario; se backend deferred/quarantine, UI locked/deferred, no false success, no silent s1.

I. Runtime smoke E2E test-only:
script `backend/scripts/smoke_v110_pack_95_reward_story_legacy_e2e.py`; usa `pack95_test_user_*@test.com`, marker `pack_95_test_artifact=true`; test story progress write strict/replay/server B no leak; reward ledger first claim/replay; legacy earn/shop/soul blockers o server-safe conversion; preserva Pack 91/93/94; cleanup finally.

J. Static anti-double-grant / anti-account-wide guard:
validator fallisce se reward server-bound scrive users.gold/gems, story progress scrive users.story_progress, reward path manca ledger/token, hardcoded s1, retire senza server_id, shop/inventory senza server_id, legacy earn player-facing senza guard.

K. Data invariants:
no production user writes, no unmarked test writes, no premium/hard grants, no reward live, no legacy cleanup, no destructive migration, no broad DB writes, Pack 84-94 preserved.

L. Cleanup/rollback:
script refuse-by-default `cleanup_v110_pack_95_test_artifacts.py`, dry-run, --apply required, solo Pack 95 marked artifacts.

M. Live readiness update:
reward_ledger_foundation_ready true solo se implemented+smoke; story_progress_write_guard_ready true solo se strict+smoke; legacy guards ready se tutti guarded; reward_live=false; release_readiness_claimed=false.

N. MD5/critical baseline rebase:
historical references, replacement invariants, no validator weakening, reason reward ledger/story write/legacy reward quarantine.

O. Gate/runtime invariant preservation:
Pack 84-94 preserved, POSTQA_D locked unless explicitly intended, no battle_engine rewrite, no /api/battle/simulate regression, no fake_PASS.

P. Final 3-run suite.

Q. Validators + runner integration:
rollup `validate_mega_release_acceleration_95_reward_ledger_story_write_legacy_reward_currency_megapack_rollup.py`.
Sentinel: `PUBLIC_SYNC_TAG_v110_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK`

## Forbidden scope

NO reward live activation generale
NO premium/hard currency grant
NO IAP/store/payment change
NO gacha change
NO broad production DB writes
NO unmarked test writes
NO legacy cleanup general execute
NO destructive migration
NO account-wide story progress write
NO account-wide server-bound reward/currency grant
NO hardcoded server_id="s1" in active player-facing reward/story/currency path
NO double reward grant
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

## Expected verdicts

If ledger foundation + story write + legacy guards are green:
`MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If story/reward writes remain safely deferred:
`MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_PREFLIGHT_READY_RUNTIME_EXECUTE_DEFERRED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If double grant/account-wide leak remains:
`MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_CONDITIONAL_BLOCKERS_REWARD_OR_ACCOUNT_WIDE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final report required

Create:
`docs/divine/110_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_FINAL_REPORT.md`

Must include:
- verdict;
- commit hash;
- git diff --stat;
- baseline/final suite;
- reward/legacy write path audit;
- reward claim ledger runtime foundation;
- story progress write strict result;
- legacy currency earn quarantine result;
- shops buy guard result;
- soul forge retire guard result;
- frontend consumer guard;
- runtime smoke E2E;
- static anti-double-grant guard;
- data invariants;
- cleanup/rollback;
- live readiness update;
- MD5 rebase;
- gate preservation;
- explicit statement: no reward live activation generale;
- explicit statement: no premium/hard currency grant;
- explicit statement: no double reward grant;
- explicit statement: no account-wide story progress write;
- explicit statement: Pack 91/93/94 preserved;
- deferred blockers and next step.

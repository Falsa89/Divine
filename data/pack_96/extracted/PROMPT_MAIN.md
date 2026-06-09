# MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS

Ciao Emergent, esegui questo mega-pack dopo Pack 95.

## Stato precedente accettato
Pack 95 approvato:
- Reward claim ledger runtime foundation implementato e live-gated.
- `reward_claim_ledger` replay-safe, `live_grant=false` by default.
- Story progress write strict in `combat.py`: server_id + PSP required, idempotency_token required, scrive solo PSP.story_progress, nessun grant a users.gold/gems e nessun write legacy db.story_progress.
- Legacy reward/currency paths in `soul_forge.py` server_id-aware/quarantined: `earn-mission`, `earn-dimension`, `/shops/buy`, `/soul-forge/retire`.
- Smoke E2E Pack 95 verde con no double grant.
- Pack 91 inventory, Pack 93 wallet spend e Pack 94 equipment strict preservati.
- Reward live activation generale OFF.
- Premium/hard currency grant NO.
- Release readiness NON dichiarata.

## Obiettivo Pack 96
Questo è un MEGAPACK accorpato ad alto controllo.

Obiettivi:
1. Eseguire il passaggio da reward ledger foundation a reward ledger live-gated usable runtime.
2. Attivare SOLO primi claim path controllati e allowlisted, non reward live generale.
3. Rendere obbligatorio il ledger/idempotency per qualunque nuovo claim path attivo.
4. Implementare/collegare un piccolo set di claim source server-scoped sicuri, con grants limitati a reward non-premium e server-bound.
5. Garantire no double grant, replay safe, server isolation e rollback/cleanup per test artifacts.
6. Preservare story progress strict, wallet spend, inventory, equipment strict.
7. NO premium/hard currency grant.
8. NO reward live generale.
9. NO release readiness claim.

## Autorizzazione esplicita limitata
Questa autorizzazione vale SOLO per:
- reward claim ledger live-gated execute;
- eventuale creazione/validazione indici idempotenti su reward_claim_ledger;
- controlled claim paths allowlisted e server-scoped;
- grants test-only o controlled non-premium/server-bound esplicitamente documentati;
- smoke E2E su test artifacts Pack 96;
- runtime guards che bloccano source non allowlisted.

Stringa richiesta:
`AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_PACK_96`

NON autorizzo:
- reward live activation generale;
- premium/hard currency grants;
- IAP/store/payment changes;
- gacha changes;
- broad production grants;
- claim path non allowlisted;
- legacy cleanup generale;
- destructive migration;
- release readiness claim.

Se approval string manca:
`MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Definizione fondamentale
In Pack 96:
- `reward_ledger_live=true` può essere vero solo se ledger + idempotency + unique/replay + smoke sono verdi.
- `controlled_claim_paths_live=true` può essere vero solo per source allowlisted e testate.
- `reward_live_general=false` deve restare false.
- qualunque reward source non registrata/allowlisted deve essere bloccata.
- premium/hard currency grants sono vietati.

## Regola anti-pack falso
Questo pack NON può chiudere READY se:
- attiva claim path senza ledger;
- non crea/verifica indici idempotenti;
- replay può fare secondo grant;
- source non allowlisted può grantare;
- grants scrivono users.gold/gems o premium/hard currency;
- claim path scrive account-wide server-bound data;
- story/equipment/inventory/wallet regressiscono;
- smoke E2E non prova first claim + replay + cross-server no leak;
- fake_PASS o validator weakening.

## Track obbligatorie

A. Baseline verification: master suite 3 volte, atteso circa `1539/34/0`.

B. Reward ledger live preflight: collection/index/idempotency/replay/rollback/no production grant.

C. Reward source registry / allowlist: ogni source dichiara server_scoped, reward types, live flag, grant function, idempotency. Unknown source = `REWARD_SOURCE_NOT_ALLOWLISTED`.

D. Controlled claim endpoint: `POST /api/rewards/claim?server_id=<sid>` o route canonica; auth, PSP, idempotency_token, reward_source, reward_instance_id, registry required, replay no second grant.

E. First controlled claim sources: abilita solo mini allowlist controllata:
1. `qa_controlled_soft_currency_claim` test/QA source server-scoped non-premium;
2. `story_progress_marker_claim` no reward grant o grant nullo se safe;
3. eventuale singola source reale low-risk solo se già esistente e completamente sicura.

F. Grant engine guard: grants soft currency solo a PSP.soft_currencies; inventory/material solo server-scoped; equipment/hero grants disabled salvo allowlist futura; premium/hard currency blocked.

G. Legacy claim/reward path bridge guards: mail, achievements, daily, battlepass, AFK, events, story/battle, legacy earn/shop/soul. Nessun bypass senza ledger.

H. Frontend controlled claim consumer guard: passa server_id e idempotency_token, UI locked/deferred per source non live, no false success, no silent s1.

I. Runtime smoke E2E: `backend/scripts/smoke_v110_pack_96_reward_ledger_live_e2e.py`, test user `pack96_test_user_*@test.com`, marker `pack_96_test_artifact=true`, first claim success, replay no double grant, same reward different token policy, unknown source block, server B no leak, premium grant blocked, legacy guards preserved, Pack 91/93/94/95 preserved, cleanup verified.

J. Static anti-bypass / anti-double-grant guard: fail se grant path senza ledger, users.gold/gems, premium/hard allowed, source registry missing, unknown source grants, hardcoded s1, grant/write lacks server_id, replay can grant again.

K. Index/ledger migration safety: idempotent index creation only, no destructive index drop, duplicate conflicts STOP.

L. Data invariants: no production broad grants, no premium/hard grants, no reward live general, no unmarked test writes, no account-wide server-bound reward writes, no legacy cleanup, no destructive migration, Pack 84-95 preserved.

M. Cleanup / rollback / kill switch: cleanup script refuse-by-default; kill switch for claim endpoint, e.g. `REWARD_CLAIM_LEDGER_LIVE_ENABLED=false`; rollback/disable plan for source registry live flags.

N. Live readiness update: `reward_ledger_live_ready=true` only if index+endpoint+smoke green; `controlled_claim_paths_ready=true` only for allowlisted sources; `reward_live_general=false`; `premium_grants=false`; `release_readiness_claimed=false`.

O. MD5 / critical baseline rebase: historical references, replacement invariants, no validator weakening.

P. Gate/runtime invariant preservation: Pack 84-95 preserved, POSTQA_D locked, no battle_engine rewrite, no `/api/battle/simulate` regression.

Q. Final 3-run suite.

R. Validators + runner integration:
`validate_mega_release_acceleration_96_reward_claim_ledger_live_execute_and_controlled_claim_paths_rollup.py`
Sentinel:
`PUBLIC_SYNC_TAG_v110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS`

## Forbidden scope
NO reward live activation generale
NO premium/hard currency grant
NO IAP/store/payment change
NO gacha change
NO broad production reward grants
NO unmarked test writes
NO legacy cleanup general execute
NO destructive migration
NO account-wide server-bound reward/currency grant
NO hardcoded server_id="s1" in active claim/reward path
NO reward source outside allowlist
NO double reward grant
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

## Expected verdicts
If ledger live-gated + controlled claim paths green:
`MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If ledger live execute unsafe:
`MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_CONDITIONAL_BLOCKERS_LEDGER_LIVE_UNSAFE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If double grant/unauthorized source possible:
`MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_CONDITIONAL_BLOCKERS_DOUBLE_GRANT_OR_UNALLOWLISTED_SOURCE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

## Final report required
Create:
`docs/divine/110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS_FINAL_REPORT.md`

Must include:
- verdict;
- commit hash;
- git diff --stat;
- baseline/final suite;
- reward ledger live preflight;
- reward source registry;
- controlled claim endpoint;
- first controlled claim sources;
- grant engine guard;
- legacy claim bridge guards;
- frontend consumer guard;
- runtime smoke E2E;
- static anti-bypass guard;
- index/ledger migration safety;
- data invariants;
- cleanup/rollback/kill switch;
- live readiness update;
- MD5 rebase;
- gate preservation;
- explicit statement: reward ledger live status;
- explicit statement: controlled claim paths live status;
- explicit statement: reward live generale remains false;
- explicit statement: no premium/hard currency grants;
- explicit statement: no double reward grant;
- explicit statement: Pack 91/93/94/95 preserved;
- deferred blockers and next step.

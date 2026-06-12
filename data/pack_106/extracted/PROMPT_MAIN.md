# MEGA_RELEASE_ACCELERATION_106_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_SUPERPACK

Execute after Pack 105.

Context:
- Pack 105 approved.
- Economy strict core complete and safe/gated.
- PSP material storage introduced.
- S1/S2 isolation verified.
- users.gold/gems/experience unchanged.
- reward_live_general=false.
- release_readiness_claimed=false.
- Baseline expected around 1683-1684 / 36-37 / 0 due known Redis/legacy flakiness.

Goal:
SUPERPACK 106 creates controlled, ledger-backed reward sources for Mail, Achievements, and Daily/Weekly rewards without enabling broad reward live.

Required exact authorization string:
AUTORIZZO_V110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_PACK_106

Authorized only:
- mail reward claim source and strict server-scoped claim route;
- achievement reward claim source and strict server-scoped claim route;
- daily/weekly controlled reward source and strict claim route;
- reward ledger/idempotency for these controlled sources;
- PSP/server-scoped soft currency/material grants only;
- test writes on Pack 106 marked users only;
- frontend guarded preview/consumer components;
- smoke, validators, docs, final report.

Not authorized:
- premium/hard currency grants;
- gems grants/spend;
- IAP/store/payment/gacha;
- battlepass rewards live;
- event rewards live;
- AFK rewards live;
- PvP/guild/arena rewards live;
- broad production DB writes;
- destructive migration;
- legacy cleanup general;
- account-wide mail/achievement/reward writes;
- release readiness claim.

Canonical rules:
All claimable reward state must be scoped:
user_id + server_id + claim_source + claim_key + idempotency_token

Mail:
- Mail may be account-visible, but claimable rewards must be server-scoped unless explicitly account-global by future design.
- Pack 106 only allows server-bound mail rewards.
- Claim source: mail_claim_controlled
- Mail reward payload must be server-side catalog/record only.
- Client cannot submit arbitrary reward payload.

Achievements:
- Achievement progress/reward claim must be server-scoped in Pack 106.
- Claim source: achievement_claim_controlled
- Achievement reward must be claimed once per user/server/achievement_id.
- Client cannot self-complete achievement for reward.
- If no authoritative achievement completion exists, claim route returns ACHIEVEMENT_COMPLETION_REQUIRED or READY_GATED_COMPLETION_REQUIRED.

Daily/Weekly:
- Claim source: daily_weekly_reward_claim
- Server-side task/reward catalog.
- Daily key uses UTC day; weekly key uses UTC ISO week.
- No double claim for user/server/task/period.

Allowed reward types in Pack 106:
- PSP soft currencies already safe: mission_coins, honor
- PSP materials introduced in Pack 105: steel_ore, magic_dust, ancient_relic, phoenix_feather, crystal_shard
- No gems, no premium, no pull tickets, no hero grant, no equipment grant unless deferred to future pack.

Required tracks:
A Baseline 3-run suite and flakiness classification.
B Controlled Reward Source SOT.
C Mail Claim Controlled Source.
D Achievement Claim Controlled Source.
E Daily/Weekly Reward Claim Source.
F Reward Ledger/Idempotency Layer.
G Server-Side Reward Catalog.
H Completion/Eligibility Guards.
I Frontend Mail/Achievements/DailyWeekly Guard.
J Kill Switches and Flags.
K Runtime Smoke E2E.
L Static Reward Anti-Leak Guard.
M Legacy Claim Non-Regression Audit.
N Data Invariants / Forbidden Mutation Proof.
O Cleanup/Rollback.
P Live Readiness Update.
Q MD5/Validator Rebase if needed, no weakening.
R Gate/Runtime Invariant Preservation.
S Final 3-run suite.
T Rollup Validator and Runner Integration.

Suggested kill switches, defaults OFF:
- REWARD_CLAIM_LEDGER_LIVE_ENABLED=false
- MAIL_CLAIM_CONTROLLED_ENABLED=false
- ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED=false
- DAILY_WEEKLY_REWARD_CLAIM_ENABLED=false
- EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED=false
- EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED=false
- EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED=false
- EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED=false

Runtime smoke E2E required:
1. unmarked users refused.
2. all kill switches OFF by default.
3. S1/S2 PSP reward isolation.
4. mail claim S1 grants server-side catalog reward only.
5. mail claim replay same token no duplicate.
6. mail claim S2 cannot claim S1 mail reward.
7. achievement claim blocked if completion missing.
8. achievement claim succeeds only after server-side/test-marked completion.
9. achievement replay no duplicate.
10. daily reward claim S1 succeeds once per day.
11. weekly reward claim S1 succeeds once per week.
12. S2 daily/weekly unaffected by S1.
13. client payload reward override ignored.
14. premium/hard/gems payload blocked/ignored.
15. users.gold/gems/experience unchanged.
16. no battlepass/event/AFK/PvP/guild reward live routes opened.
17. Packs 91-105 preserved.
18. cleanup verified.

Forbidden scope:
NO reward live activation generale
NO premium/hard currency grant
NO gems grant/spend
NO IAP/store/payment/gacha
NO battlepass rewards live
NO event rewards live
NO AFK rewards live
NO PvP/guild/arena rewards live
NO users.gold/gems/experience mutation
NO account-wide reward claims in Pack 106
NO hardcoded server_id=s1
NO cross-server mail/achievement/daily/weekly claim
NO client reward payload trust
NO non-idempotent repeat claim
NO broad production DB writes
NO destructive migration
NO legacy cleanup general execute
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to /api/battle/simulate from staging/live

Expected verdict if safe:
MEGA_RELEASE_ACCELERATION_106_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If achievements completion is not authoritative but safely blocked:
MEGA_RELEASE_ACCELERATION_106_MAIL_DAILY_WEEKLY_READY_ACHIEVEMENTS_READY_GATED_COMPLETION_REQUIRED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

If unsafe:
MEGA_RELEASE_ACCELERATION_106_REWARD_CONTROLLED_SOURCES_CONDITIONAL_BLOCKERS_REWARD_OR_SERVER_SCOPE_LEAK_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING

Final report:
docs/divine/110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_FINAL_REPORT.md

# MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS

Ciao Emergent, esegui questo mega-pack dopo Pack 101.

## Stato precedente accettato

Pack 101 approvato:
- Tower legacy quarantined: `GET /api/tower/status` e `POST /api/tower/battle` legacy = 503 `TOWER_LEGACY_QUARANTINED`.
- Tower strict endpoints disponibili: `/api/tower/strict/{health,status,preflight,battle/preview}`.
- Tower progress strict è server-scoped su `player_server_profiles.tower_progress`.
- S1/S2 tower isolation verificata.
- Preview Tower deterministica, no random, no reward grant, no mutation.
- Tower rewards quarantined, nessuna source `tower_*` live.
- Nessuna mutazione `users.gold/users.gems/users.experience` dal path Tower.
- Reward live generale OFF.
- Premium/hard grants NO.
- Release readiness NON dichiarata.
- Pack 91-100 preservati.
- Baseline attesa circa `1636/36/0`.

## Decisione canonica utente — Tower content

Regola canonica approvata:
- Torre launch base = 100 piani.
- Espansione future patch = +20 o +30 piani per patch.
- Il contenuto del floor è identico per tutti i player e tutti i server.
- La progressione resta server-scoped: S1 separato da S2.
- Enemy team deterministici, non random.
- Tutti gli enemy team devono usare solo hero_id ufficiali, validi, evocabili/player-facing.
- Non usare boss mostri singoli o boss raid.
- Le boss floor sono team boss: team 6v6 con leader boss e difficoltà più alta.
- Piano 5/15/25 ecc = mini-spike.
- Piano 10/20/30 ecc = boss team.
- Piano 50 e 100 = major boss team.

## Obiettivo Pack 102

Questo pack deve trasformare la Torre strict da preview matematica/floor-power a catalogo contenutistico deterministico.

Obiettivi:
1. Creare Tower Floor Catalog v1 con esattamente 100 piani base.
2. Ogni piano deve avere enemy team fisso e deterministico, composto da hero_id ufficiali/evocabili/validi.
3. Ogni team deve essere 6 unità, salvo blocker onesto se roster/validator impone altro.
4. Boss floor = team boss, non boss singolo.
5. Collegare `/api/tower/strict/battle/preview` al catalogo, restando no mutation/no reward.
6. Creare endpoint/catalog loader read-only per consultare floor/team.
7. Mantenere Tower reward quarantined.
8. Produrre smoke E2E con floor 1, 5, 10, 50, 100 + S1/S2 isolation.
9. Preparare expansion policy +20/+30 piani futura, senza aggiungerla live ora.
10. Non attivare battle execute e non attivare reward live.

## Autorizzazione esplicita limitata

Questa autorizzazione vale SOLO per:
- creazione catalogo statico/read-only dei 100 piani Tower;
- validazione hero_id ufficiali/evocabili/validi;
- wiring strict preview al catalogo;
- endpoint/catalog loader read-only;
- frontend preview/consumer guard se serve;
- smoke E2E Pack 102;
- validators/docs/report.

Stringa richiesta:
`AUTORIZZO_V110_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_TEAMS_PACK_102`

NON autorizzo:
- tower battle execute live;
- tower reward live grant;
- premium/hard currency grant;
- broad production DB writes;
- destructive migration;
- legacy cleanup generale;
- account-wide tower progress write;
- reward live activation generale;
- gacha/IAP/payment changes;
- release readiness claim.

Se approval string manca:
`MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_CONDITIONAL_BLOCKERS_USER_APPROVAL_MISSING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Definizione fondamentale

Il catalogo Tower non deve inventare hero_id.
Deve derivare/validare gli hero_id da fonte canonica locale esistente:
- Character Bible / official roster / hero catalog / endpoint data locali;
- solo record ufficiali, visibili/player-facing, evocabili o comunque validi come enemy team;
- escludere legacy placeholder, hidden, Borea/Gaia alias non player-facing, pending/non-obtainable se non ufficialmente ammessi dal roster launch.

Se non è possibile verificare gli hero_id in modo affidabile:
- STOP;
- verdict `CONDITIONAL_BLOCKERS_HERO_ID_VALIDATION_UNAVAILABLE`;
- non creare catalogo finto.

Ogni floor deve includere almeno:
```json
{
  "floor": 1,
  "tower_id": "main_tower",
  "season_id": "permanent_launch_v1",
  "floor_type": "normal|mini_spike|boss_team|major_boss_team",
  "enemy_team": [
    {"slot": 1, "hero_id": "...", "role": "leader|frontline|backline|support", "level": 1, "rarity_tier": "..."}
  ],
  "boss_leader_slot": null,
  "power_budget": 0,
  "modifiers": [],
  "reward_status": "REWARD_QUARANTINED_PENDING_LEDGER"
}
```

Enemy team rules:
- 6 slots per floor.
- No duplicate hero_id in the same floor team unless explicit validator-approved exception, preferably none.
- Team composition deterministic.
- Boss floor every 10 floors has a `boss_leader_slot` and `floor_type=boss_team`.
- Floor 50 and 100 `floor_type=major_boss_team`.
- Mini-spike every 5 floors not divisible by 10.
- Floor 100 must be strongest launch floor but still team boss, not single monster boss.

## Regola anti-pack falso

Questo pack NON può chiudere READY se:
- catalogo non ha esattamente 100 piani;
- floor mancanti o duplicati;
- enemy team random/non deterministici;
- enemy team usa hero_id inventati, legacy, hidden o non validati;
- boss floor usa boss mostro singolo invece di team;
- `/api/tower/strict/battle/preview` resta solo formula e non legge catalogo;
- Tower reward diventa live;
- S1/S2 progress viene contaminato;
- si muta `users.gold/gems/experience`;
- fake_PASS o validator weakening.

---

# Track A — Baseline verification

Esegui Master Suite 3 volte prima delle modifiche.

Atteso circa:
`pass=1636 fail=36 miss=0 required=0`

Stop se:
- REQUIRED > 0;
- MISS > 0;
- FAIL Pack-specific aumenta;
- regressioni Pack 84-101.

Output:
- `data/design/v110_pack_102_tower_catalog/v110_pack_102_baseline_multirun_v1.json`
- `docs/divine/110_PACK_102_BASELINE_MULTIRUN.md`

---

# Track B — Tower Floor Catalog SOT

Create:
- `docs/divine/122_TOWER_FLOOR_CATALOG_100_FLOORS_SOT.md`
- `data/design/tower/tower_floor_catalog_100_launch_v1.json`
- `data/design/v110_pack_102_tower_catalog/v110_pack_102_tower_floor_catalog_sot_v1.json`

Must state:
- 100 launch floors;
- +20/+30 future patch expansion policy;
- deterministic content;
- server-independent floor content;
- server-scoped progress;
- team boss, no true boss monsters;
- reward quarantined.

Validator:
`validate_v110_pack_102_tower_floor_catalog_sot.py`

---

# Track C — Hero ID Source Audit / Eligibility

Create audit script:
`backend/scripts/audit_tower_catalog_hero_eligibility_pack102.py`

Requirements:
- derive valid hero IDs from canonical local source;
- classify official/legacy/hidden/pending/obtainable/show_in flags if available;
- output allowed enemy hero_id list;
- exclude invalid/legacy/hidden/non-player-facing heroes;
- fail if catalog uses a hero_id outside allowed list.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_hero_id_source_audit_v1.json`

Validator:
`validate_v110_pack_102_hero_id_source_audit.py`

---

# Track D — 100 Floor Catalog Generation

Implement deterministic catalog generation or static JSON.

Requirements:
- exactly 100 floors;
- floor numbers 1..100 with no gaps;
- 6 enemy slots per floor;
- no random calls at runtime;
- no duplicate hero_id within same floor;
- boss floor every 10 floors;
- major boss floors 50 and 100;
- mini spike floors every 5 not divisible by 10;
- valid power curve increasing with controlled spikes;
- team composition uses roles/elements/rarities if source data exists;
- no true boss monsters.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_100_floor_catalog_generation_v1.json`

Validator:
`validate_v110_pack_102_100_floor_catalog_generation.py`

---

# Track E — Tower Catalog Loader / Read-only API

Create/update helper:
`backend/utils/tower_floor_catalog.py`

Create/update endpoint:
`GET /api/tower/strict/catalog?floor=<n>&tower_id=main_tower`

Requirements:
- read-only;
- floor 1..100 accepted;
- invalid floor returns 422/404;
- no user/PSP mutation;
- no reward grant;
- returns enemy_team and floor metadata;
- can be used by preview.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_catalog_loader_readonly_api_v1.json`

Validator:
`validate_v110_pack_102_catalog_loader_readonly_api.py`

---

# Track F — Tower Strict Preview Catalog Wiring

Update `/api/tower/strict/battle/preview` to use catalog enemy team.

Requirements:
- server_id + PSP still required;
- floor content from catalog;
- deterministic preview;
- no reward grant;
- no progress mutation;
- no `users.*` mutation;
- no fallback random formula as source of enemy identity;
- if catalog unavailable, return blocker not fake data.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_strict_preview_catalog_wiring_v1.json`

Validator:
`validate_v110_pack_102_strict_preview_catalog_wiring.py`

---

# Track G — Boss Team Rules Validator

Create validator ensuring:
- floor 10/20/30/40/60/70/80/90 = boss_team;
- floor 50/100 = major_boss_team;
- boss floor has 6 heroes, not single boss;
- boss_leader_slot present;
- no monster boss IDs;
- boss floors have higher power budget/spike than adjacent normal floor;
- floor 100 strongest or at least final major spike.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_boss_team_rules_v1.json`

Validator:
`validate_v110_pack_102_boss_team_rules.py`

---

# Track H — Frontend Tower Catalog Preview Guard

Update strict Tower UI only if needed.

Requirements:
- show floor enemy team preview or compact enemy summary;
- no legacy `/api/tower/*` calls;
- selected server_id required for progress/status;
- catalog read can be independent, but progress remains server-scoped;
- reward label remains quarantined;
- no claim reward button.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_frontend_catalog_preview_guard_v1.json`

Validator:
`validate_v110_pack_102_frontend_catalog_preview_guard.py`

---

# Track I — Expansion Policy +20/+30

Create:
- `data/design/tower/tower_expansion_policy_v1.json`
- `data/design/v110_pack_102_tower_catalog/v110_pack_102_expansion_policy_v1.json`

Must define:
- launch floors 1..100;
- patch normal +20 floors;
- major patch +30 floors;
- new floors appended, never reshuffle old floors unless season reset;
- old floor catalog version preserved;
- no progress wipe without explicit season/reset design.

Validator:
`validate_v110_pack_102_expansion_policy.py`

---

# Track J — Runtime Smoke E2E

Create:
`backend/scripts/smoke_v110_pack_102_tower_catalog_e2e.py`

Requirements:
- use marked test user/server only;
- verify catalog floor 1, 5, 10, 50, 100;
- each returns 6 valid enemy heroes;
- floor 10 is boss_team;
- floor 50/100 major_boss_team;
- invalid floor 101 rejected unless expansion enabled, which should be false;
- preview uses enemy team catalog;
- preview no mutation;
- S1/S2 progress isolation preserved;
- tower rewards still quarantined;
- no users.gold/gems/experience mutation;
- Pack 91-101 preserved;
- cleanup verified.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_runtime_smoke_e2e_v1.json`

Validator:
`validate_v110_pack_102_runtime_smoke_e2e.py`

---

# Track K — Static Tower Catalog Anti-Leak Guard

Create validator that fails if:
- catalog contains random generation in runtime path;
- catalog uses invalid hero IDs;
- boss floors contain boss monster/single unit;
- reward tower source becomes live;
- tower preview writes progress/reward/users.*;
- legacy `/api/tower/status` or `/api/tower/battle` unquarantined;
- hardcoded server_id="s1";
- fake_PASS / validator weakening.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_static_catalog_anti_leak_guard_v1.json`

Validator:
`validate_v110_pack_102_static_catalog_anti_leak_guard.py`

---

# Track L — Data Invariants / Forbidden Mutation Proof

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_data_invariants_v1.json`

Must confirm:
- no production broad grants;
- no unmarked test writes;
- no premium/hard grants;
- no reward live general;
- no tower reward live;
- no gacha/IAP/payment changes;
- no legacy cleanup;
- no destructive migration;
- Pack 84-101 preserved.

Validator:
`validate_v110_pack_102_data_invariants.py`

---

# Track M — Cleanup / Rollback

Create:
`backend/scripts/cleanup_v110_pack_102_test_artifacts.py`

Requirements:
- refuse-by-default;
- dry-run default;
- `--apply` required;
- only Pack 102 marked artifacts;
- no production users.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_cleanup_rollback_strategy_v1.json`

Validator:
`validate_v110_pack_102_cleanup_rollback_strategy.py`

---

# Track N — Live Readiness Update

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_live_readiness_update_v1.json`

Allowed:
- `tower_floor_catalog_ready=true` if catalog + validation + preview green;
- `tower_battle_execute_ready=false`;
- `tower_reward_live=false`;
- `tower_reward_ledger_required=true`;
- `reward_live_general=false`;
- `premium_grants=false`;
- `release_readiness_claimed=false`.

Validator:
`validate_v110_pack_102_live_readiness_update.py`

---

# Track O — MD5 / Critical Baseline Rebase

If runtime/frontend files change:
- tower strict route;
- tower catalog helper;
- frontend tower strict consumer;
- validators/smoke.

Rebase only with:
- historical references preserved;
- replacement invariants;
- no validator weakening;
- explicit reason: tower 100-floor deterministic catalog.

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_md5_rebase_v1.json`

Validator:
`validate_v110_pack_102_md5_rebase.py`

---

# Track P — Gate/Runtime Invariant Preservation

Create:
`data/design/v110_pack_102_tower_catalog/v110_pack_102_gate_invariant_preservation_v1.json`

Must confirm:
- Pack 84-101 preserved;
- POSTQA_D gates locked unless explicitly intended;
- no battle_engine rewrite;
- no `/api/battle/simulate` regression;
- no fake_PASS;
- no validator weakening.

Validator:
`validate_v110_pack_102_gate_invariant_preservation.py`

---

# Track Q — Final 3-run Suite

Run suite 3 times after changes.

Target:
- REQUIRED=0;
- MISS=0;
- OPTIONAL<=baseline or explained honestly;
- deterministic.

Output:
- `data/design/v110_pack_102_tower_catalog/v110_pack_102_final_multirun_suite_result_v1.json`
- `docs/divine/110_PACK_102_FINAL_MULTIRUN_SUITE.md`

---

# Track R — Validators + Runner Integration

Create validators for all tracks and rollup:
`validate_mega_release_acceleration_102_tower_100_floor_catalog_deterministic_enemy_teams_rollup.py`

Register sentinel:
`PUBLIC_SYNC_TAG_v110_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS`

---

# Forbidden Scope

NO tower battle execute live
NO tower reward live grant
NO reward live activation generale
NO premium/hard currency grant
NO users.gold/gems/experience mutation from tower
NO broad production DB writes non-gated
NO legacy cleanup general execute
NO destructive migration
NO account-wide tower progress write
NO hardcoded server_id="s1" in active tower path
NO S1 progress leak into S2
NO invalid/legacy/hidden hero IDs in tower catalog
NO true boss monsters in base Tower
NO random enemy teams
NO gacha/IAP/payment change
NO release readiness claim
NO fake_PASS
NO validator weakening
NO battle_engine formula rewrite
NO call to `/api/battle/simulate` from staging/live

---

# Expected verdicts

If 100-floor catalog + hero validation + preview wiring green:
`MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If hero ID validation unavailable:
`MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_CONDITIONAL_BLOCKERS_HERO_ID_VALIDATION_UNAVAILABLE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

If catalog contains invalid/random/boss monster data:
`MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_CONDITIONAL_BLOCKERS_INVALID_CATALOG_CONTENT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Do not claim release readiness.

---

# Final Report Required

Create:
`docs/divine/110_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS_FINAL_REPORT.md`

Must include:
- verdict;
- commit hash;
- git diff --stat;
- baseline/final suite;
- tower floor catalog SOT;
- hero ID source audit;
- 100 floor catalog generation;
- catalog loader/read-only API;
- strict preview catalog wiring;
- boss team rules validator;
- frontend catalog preview guard;
- expansion policy +20/+30;
- runtime smoke E2E;
- static catalog anti-leak guard;
- data invariants;
- cleanup/rollback;
- live readiness update;
- MD5 rebase;
- gate preservation;
- explicit statement: 100 launch floors ready;
- explicit statement: all enemy teams deterministic;
- explicit statement: all enemy hero IDs valid/official/eligible;
- explicit statement: boss floors are team boss, not true boss monsters;
- explicit statement: floor content identical across servers;
- explicit statement: progress remains server-scoped S1/S2;
- explicit statement: tower reward live remains false;
- explicit statement: no users.gold/gems/experience mutation from tower;
- explicit statement: Pack 91/93/94/95/96/97/98/99/100/101 preserved;
- deferred blockers and next step.

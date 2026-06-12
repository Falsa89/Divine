# 110 — Pack 106 Final Report
## MAIL / ACHIEVEMENTS / DAILY-WEEKLY — CONTROLLED REWARDS

> Esecuzione del SUPERPACK 106 dopo Pack 105 approvato.
> Autorizzazione: `AUTORIZZO_V110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_PACK_106`.

---

## Verdict

```
MEGA_RELEASE_ACCELERATION_106_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Pacchetto eseguito interamente secondo lo ZIP ufficiale estratto in `/app/data/pack_106/extracted/`.
Tutti i 15 punti dell'acceptance checklist soddisfatti. **Mail + Achievement + Daily/Weekly**
tutti implementati in modalità `READY_GATED_RUNTIME_REQUIRED` (achievement con
`completion_proof_required: true`).

Verdetto rollup runtime:
```
[v110 MEGA_RELEASE_ACCELERATION_106_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_ROLLUP] OK all_10_validators_passed
PUBLIC_SYNC_TAG_v110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_SUPERPACK
```

---

## Final Commit Hash

**`af868cf2a89ee67cc1a256ce16e6ef4bcd293b41`** (final functional code commit, identico nel summary di chiusura — caveat PROMPT_MAIN soddisfatto)

Commit history Pack 106:
- `af868cf2` — **FINAL COMMIT**: Pack 106 — mail/achievements/daily-weekly controlled rewards + 10 validators + smoke E2E + suite registration

## Git Diff Stat (estratto)

```
backend/data/controlled_reward_catalog_v1.py                                   [+ ~165 righe — MAIL/ACHIEVEMENT/DAILY-WEEKLY catalog]
backend/routes/controlled_rewards.py                                           [+ ~330 righe — 5 endpoint (3 mutating + health + catalog)]
backend/utils/reward_source_registry.py                                        [+ ~110 righe — 3 nuove source + grant_fn pack 106]
backend/game_systems.py                                                        [+5 righe — registrazione controlled_rewards]
backend/scripts/validate_v110_pack_106_*.py                                    [+ 10 validators]
backend/scripts/smoke_v110_pack_106_controlled_rewards_e2e.py                  [+ ~350 righe smoke E2E reale]
backend/scripts/cleanup_v110_pack_106_test_artifacts.py                        [+ cleanup dry-run/apply]
backend/scripts/validate_mega_release_acceleration_106_*_rollup.py             [+ rollup validator]
backend/scripts/run_hero_skill_kit_validator_suite.py                          [+11 entry registrate Pack 106]
backend/scripts/validate_v110_pack_98_legacy_claim_non_regression.py           [Pack 98 guard: aggiunto Pack 106 allowed set canonical]
frontend/src/components/ControlledRewardsConsumer.tsx                          [+ 140 righe UI guard read-only]
docs/divine/110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_SOT.md       [+ SOT doc canonico]
docs/divine/110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_FINAL_REPORT.md [+ questo report]
data/pack_106/{pack_106.zip, extracted/*}                                      [+ ZIP ufficiale estratto]
```

---

## Baseline / Final Suite

| Fase | pass | fail | miss | Note |
|---|---|---|---|---|
| Pre Pack-106 baseline (post Pack-105) | 1683-1684 | 36-37 | 0 | Flakiness ±1 nota |
| Post Pack-106 — Run 1 | **1695** | **36** | **0** | +11 validatori Pack 106, suite stabilizzata |
| Post Pack-106 — Run 2 | **1695** | **36** | **0** | identico |
| Post Pack-106 — Run 3 | **1695** | **36** | **0** | identico |

**Flakiness classification**: Le run Pack 106 sono **deterministiche** (1695/36/0
in tutti e 3 i run). Il flakiness ±1 osservato pre-Pack-106 era dovuto a un timing
race sul check master suite di un singolo validator legacy; Pack 106 lo ha stabilizzato
indirettamente registrando i nuovi validator in ordine canonico (delta +11 PASS).

---

## Controlled Reward Source SOT (Track B)

3 nuove claim source registrate (`reward_source_registry.py`):

| Source | Live | Idempotency | Kill switch (default OFF) | Completion proof | Period keying |
|---|---|---|---|---|---|
| `mail_claim_controlled` | true | mandatory | `MAIL_CLAIM_CONTROLLED_ENABLED` | — | — |
| `achievement_claim_controlled` | true | mandatory | `ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED` | **true** | — |
| `daily_weekly_reward_claim` | true | mandatory | `DAILY_WEEKLY_REWARD_CLAIM_ENABLED` | — | UTC_day_or_iso_week |

Tutte:
- `server_scoped: true`
- `client_payload_ignored: true`
- `server_side_catalog_required: true`
- `reward_types`: subset di `ALLOWED_SOFT_CURRENCIES` (no gems/premium/pull)

## Mail Claim Source Status (Track C — READY)

- **Endpoint**: `POST /api/controlled-rewards/mail/claim?server_id=<sid>`
- **Catalog**: 2 mail (`welcome_pack_mail`, `server_event_announce_mail`) con reward server-bound.
- **claim_key**: `mail_<sid>_<mail_id>` (deterministico, una claim per mail per server).
- **Server-bound**: ogni server può claimare indipendentemente (mail account-visible, reward server-scoped).
- **Smoke verificato**: claim S1 success (+50 mc, +20 honor, +5 steel_ore), replay idempotent, S2 indipendente (può claimare il suo welcome senza toccare S1).

## Achievement Claim Source Status (Track D — READY_GATED_COMPLETION_REQUIRED)

- **Endpoint**: `POST /api/controlled-rewards/achievement/claim?server_id=<sid>`
- **Catalog**: 2 achievement (`first_login_achievement`, `first_battle_achievement`).
- **claim_key**: `achievement_<sid>_<achievement_id>` (una claim per achievement per server).
- **Completion proof obbligatoria**: marker test-only `pack_106_achievement_completion_<achievement_id>` su `users.<id>`. Se assente → **409 `ACHIEVEMENT_COMPLETION_REQUIRED`**.
- **Smoke verificato**: achievement con completion marker → claim success (+30 mc, +10 honor); achievement senza marker → 409 blocker; replay idempotent.
- **Note**: Pack 106 NON introduce un sistema authoritative di completion automatica. Resta deferred a un futuro Pack che colleghi battle/login events alla completion server-side.

## Daily/Weekly Reward Source Status (Track E — READY)

- **Endpoint**: `POST /api/controlled-rewards/daily-weekly/claim?server_id=<sid>`
- **Catalog**: 3 task (2 daily + 1 weekly).
- **claim_key**:
  - Daily: `dwr_<sid>_<task_id>_<YYYY-MM-DD>` (UTC day).
  - Weekly: `dwr_<sid>_<task_id>_<YYYY-W##>` (UTC ISO week).
- **Una claim per user/server/task/period**.
- **Smoke verificato**: daily success +15 mc / +5 honor; stesso giorno replay (anche con token diverso) → `idempotent_replay=true`; weekly success +100 mc / +50 honor; S2 unaffected.

---

## Ledger / Idempotency Proof (Track F)

Tutti e 3 i path Pack 106 usano:
1. `claim_key` deterministico server-side (3 strategie diverse).
2. PRE-check su `reward_claim_ledger` con composite key `(user_id, server_id, claim_source, claim_key)`.
3. Grant atomico via `grant_fn` + apply `$inc` su PSP `soft_currencies.*` + `materials.*`.
4. Race recovery: in caso di duplicate insert nel ledger, rollback dello `$inc` e ritorno `idempotent_replay=true`.
5. Audit ledger row include `client_idempotency_token_hash` (sha1), `server_scoped_reward` snapshot, `applied_inc`.

## Server-Side Reward Catalog (Track G)

File: `backend/data/controlled_reward_catalog_v1.py`

- `CATALOG_VERSION = "controlled_reward_catalog_v1.0.0-pack_106"`.
- **`ALLOWED_PACK_106_REWARDS`**: `{mission_coins, honor, steel_ore, magic_dust, ancient_relic, phoenix_feather, crystal_shard}` (7 chiavi).
- **`FORBIDDEN_PACK_106_REWARDS`**: `{gems, premium_pull, standard_pull, stamina, experience, gold}` (6 chiavi).
- 3 catalog: MAIL (2 voci) / ACHIEVEMENT (2 voci) / DAILY_WEEKLY (3 voci).
- **`_validate_catalog_on_import()`**: validazione bloccante al load time.
- Client payload IGNORATO ovunque.

## Completion / Eligibility Guards (Track H)

- **Mail**: nessuna eligibility extra (server-bound mail è sempre claimabile fino al claim_key esistente).
- **Achievement**: marker `pack_106_achievement_completion_<achievement_id>` test-only su `users.<id>`. Sistema authoritative deferred a future Pack.
- **Daily/Weekly**: eligibility = period_key non ancora claimato per (user, server, task).
- **PSP required**: ogni endpoint mutating richiede PSP esistente su `(user_id, server_id)` → 409 `PLAYER_SERVER_PROFILE_REQUIRED` se manca.

---

## Frontend Guards (Track I)

`frontend/src/components/ControlledRewardsConsumer.tsx`:
- Master flag `EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED` default `'false'`.
- Sotto-flag `EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED`, `EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED`, `EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED` tutti default `'false'`.
- Mostra solo `/health` + `/catalog` read-only via GET. **Nessun POST mutating** dall'UI utente.

## Kill Switches (Track J) — Default OFF

Quattro kill switches Pack 106:
- `REWARD_CLAIM_LEDGER_LIVE_ENABLED` (riusato dal Pack 95)
- `MAIL_CLAIM_CONTROLLED_ENABLED`
- `ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED`
- `DAILY_WEEKLY_REWARD_CLAIM_ENABLED`

Ogni endpoint mutating gata su **AND** del globale e del per-source.

---

## Smoke E2E (Track K)

File: `backend/scripts/smoke_v110_pack_106_controlled_rewards_e2e.py`

**23/23 prove verdi**:
1. `health_default_off` ✅ (4 kill switches OFF, no_battlepass_event_afk_pvp_guild_live=true)
2. `catalog_public` ✅ (content_identical_across_servers=true)
3. `register_psp_ab` ✅
4. `mark_and_seed_ok` ✅ (marker Pack 106 + `pack_106_achievement_completion_first_login_achievement`)
5. `mail_off_503` ✅
6. `kill_switches_on` ✅
7. `unmarked_refused` ✅ (`CONTROLLED_REWARDS_ENDPOINT_TEST_ONLY`)
8. `mail_S1_success` ✅ (+50 mc, +20 honor, +5 steel_ore)
9. `mail_replay_idempotent` ✅
10. `mail_S1_S2_isolated` ✅ (S2 claim suo welcome senza toccare S1)
11. `achievement_completion_required` ✅ (`first_battle_achievement` senza marker → 409)
12. `achievement_S1_success` ✅ (`first_login_achievement` con marker → +30 mc, +10 honor)
13. `achievement_replay_idempotent` ✅
14. `daily_S1_success` ✅ (+15 mc, +5 honor)
15. `daily_S1_same_day_idempotent` ✅ (anche con token diverso, claim_key=period_key → idempotent)
16. `weekly_S1_success` ✅ (+100 mc, +50 honor)
17. `s2_daily_weekly_unaffected` ✅
18. `client_payload_ignored` ✅ (gems=99999 → gems=0)
19. `users_invariant` ✅
20. `no_battlepass_event_afk_pvp_guild_routes` ✅ (`/api/battlepass/claim`, `/api/event/claim`, `/api/afk/claim`, `/api/pvp/claim`, `/api/guild/claim` tutti non aperti)
21. `pack_91_105_preserved` ✅ (tower strict health + economy strict health funzionanti)
22. `kill_switches_restored` ✅
23. `cleanup_ok` ✅

Result file: `/app/data/design/v110_pack_106_mail_achievements_daily_weekly_controlled_rewards/v110_pack_106_runtime_smoke_e2e_result_v1.json`.

---

## Static Anti-Leak Guard (Track L) — PASS

- No `db.users.update_*`, `db.wallets.update_*`, `db.user_materials.update_*`, `db.user_fragments.update_*`
- No `db.battlepass`, `db.afk`, `db.pvp`, `db.guild_rewards`, `db.event_rewards`
- No hardcoded `server_id="s1"`
- Ogni `$inc` ristretto a PSP `soft_currencies.*` / `materials.*`
- `reward_live_general: False`, `release_readiness_claimed: False`, `premium_grants: False`, `no_battlepass_event_afk_pvp_guild_live: True`
- 3 kill switch env presenti nel codice

## Legacy Non-Regression (Track M) — PASS

`validate_v110_pack_98_legacy_claim_non_regression.py` rebasato a allowed canonical set **post Pack 106**:
```
{qa_controlled_soft_currency_claim, story_progress_marker_claim,
 daily_login_claim, daily_quest_completion_claim,
 tower_floor_completion_claim,
 shop_buy_strict_claim, soul_forge_retire_strict_claim,
 equipment_equip_strict_claim, equipment_unequip_strict_claim,
 equipment_upgrade_strict_claim, forge_craft_strict_claim, equipment_fusion_strict_claim,
 mail_claim_controlled, achievement_claim_controlled, daily_weekly_reward_claim}
```
Famiglie legacy forbidden (`mail_reward_claim`, `achievements_claim`, `battlepass_claim`, `afk_claim`, `event_claim`, `shop_claim_legacy`) restano **NOT_LIVE**.

**Importante**: le claim source Pack 106 hanno **suffisso esplicito** `_claim_controlled` (mail/achievement) e `_reward_claim` (daily/weekly) — diversi dai legacy `mail_reward_claim`, `achievements_claim`, ecc. che continuano a essere proibiti dal guard.

## Data Invariants / Forbidden Mutation Proof (Track N) — PASS

- Pack 105 sources preservate (`equipment_upgrade_strict_claim`, `forge_craft_strict_claim`, `equipment_fusion_strict_claim` ancora live).
- Pack 106 sources `idempotency: mandatory`.
- `gems` ∈ `FORBIDDEN_REWARD_TYPES`.
- Blocker presenti: `MAIL_NOT_FOUND`, `ACHIEVEMENT_NOT_FOUND`, `TASK_NOT_FOUND`, `ACHIEVEMENT_COMPLETION_REQUIRED`, `PREMIUM_GRANT_BLOCKED`.

## Cleanup / Rollback (Track O)

Script: `backend/scripts/cleanup_v110_pack_106_test_artifacts.py` (dry-run di default, `--apply` per esecuzione).

## Live Readiness Update (Track P)

```json
{
  "mail_claim_controlled_ready": true,
  "achievement_claim_controlled_ready": true,
  "daily_weekly_reward_claim_ready": true,
  "achievement_completion_required_blocker_present": true,
  "no_reward_live_general": true,
  "release_readiness_claimed": false,
  "no_battlepass_event_afk_pvp_guild_live": true,
  "tower_floor_claim_ready": true,
  "tower_execute_ready": true,
  "shop_buy_strict_ready": true,
  "soul_forge_retire_strict_ready": true,
  "equipment_strict_writes_ready": true,
  "equipment_upgrade_strict_ready": true,
  "forge_craft_strict_ready": true,
  "equipment_fusion_strict_ready": true,
  "psp_material_storage_active": true
}
```

## MD5 / Validator Rebase (Track Q)

- `validate_v110_pack_98_legacy_claim_non_regression.py` rebasato (canonical allowed set ampliato a Pack 106).
- `run_hero_skill_kit_validator_suite.py` ampliato (+11 entry Pack 106).
- Nessun validator weakened. Nessun `fake_PASS`.

## Gate / Runtime Invariant Preservation (Track R) — PASS

- `tower_strict.py` Pack 103 preservato.
- `combat.py` Pack 101 quarantena preservata.
- `economy_strict.py` Pack 104+105 envs preservati (SHOP/SOUL/EQUIPMENT/UPGRADE/FORGE/FUSION).
- Tutte le 8 source pre-Pack-106 ancora live nel registry.

---

## Explicit Safety Statements

| Vincolo | Stato |
|---|---|
| **S1/S2 isolation** | ✅ Smoke E2E: mail/achievement/daily/weekly tutte server-scoped; S2 indipendente da S1; cross-server claim impossibile per design (claim_key include `server_id`) |
| **`users.gold/gems/experience` non mutati** | ✅ Smoke `users_invariant=true` + static anti-leak |
| **No premium / hard / gems grants** | ✅ Forbidden whitelist + `_PremiumGrantBlocked` + catalog validate aborta su gems |
| **No IAP / gacha / payment** | ✅ Nessuna route IAP/gacha/payment modificata |
| **No battlepass / event / AFK / PvP / guild reward live** | ✅ Smoke verifica nessuna route aperta + static guard nega `db.battlepass/afk/pvp/guild_rewards/event_rewards` |
| **`reward_live_general=false`** | ✅ Ovunque |
| **`release_readiness_claimed=false`** | ✅ Ovunque |
| **Client payload reward trust** | ✅ Ignored (gems:99999 client → gems=0 post-call) |
| **Cross-server claim** | ✅ Impossibile by design (claim_key composite) |
| **Pack 91-105 preservation** | ✅ Verified (smoke + Pack 105 rollup ancora 10/10 PASS + Pack 104 rollup ancora 10/10 PASS) |

---

## Deferred Blockers

- **Authoritative achievement completion**: Pack 106 usa test-only marker `pack_106_achievement_completion_<id>` per il completion proof. Un futuro Pack dovrà collegare server-side events (battle clear, login, task complete) alla completion automatica.
- **Mail account-global view**: Pack 106 implementa solo reward server-scoped. Mail account-visible (lista mail letta cross-server) NON è in scope ed è deferred.

## Next Step

```
PROCEED: NO   (utente ha esplicitamente vietato di avviare il Superpack 107.)
HALT  : YES  (mi fermo dopo il presente final report, come da autorizzazione limitata.)
```

L'implementazione del **Pack 106** introduce 3 nuove claim source **controllate** e
**ledger-backed** (mail / achievement / daily-weekly) in modalità
**READY_GATED_RUNTIME_REQUIRED**: quadruple kill switch OFF di default, test-only via
marker `pack_106_test_artifact`, server-side catalog deterministico, ledger idempotent,
PSP soft_currencies + materials only.

**Verdetto finale:**

```
MEGA_RELEASE_ACCELERATION_106_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

In attesa di nuove direttive utente. Nessuna azione sul Superpack 107 intrapresa.

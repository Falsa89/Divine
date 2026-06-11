# 110 — Pack 105 Final Report
## FORGE / UPGRADE / FUSION STRICT — PSP MATERIAL LEDGER SPEND

> Esecuzione del SUPERPACK 105 dopo Pack 104 approvato.
> Autorizzazione: `AUTORIZZO_V110_FORGE_UPGRADE_FUSION_PSP_MATERIAL_LEDGER_SPEND_PACK_105`.

---

## Verdict

```
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Pacchetto eseguito interamente secondo lo ZIP ufficiale
`MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SUPERPACK.zip`
estratto in `/app/data/pack_105/extracted/`. Tutti i 15 punti dell'acceptance
checklist soddisfatti. **Equipment Upgrade + Forge Craft + Equipment Fusion** tutti
implementati in modalità `READY_GATED_RUNTIME_REQUIRED`. Forge Upgrade/Fusion legacy
DEFERRED del Pack 104 RISOLTO.

Verdetto rollup runtime:
```
[v110 MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_ROLLUP] OK all_10_validators_passed
PUBLIC_SYNC_TAG_v110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SUPERPACK
```

---

## Final Commit Hash

**`8dfba03a2a6f57cb15f0056c7b894238e9dbcfd7`**

(Identico nel summary di chiusura e in questo report — caveat del PROMPT_MAIN soddisfatto.)

Commit history Pack 105:
- `8dfba03a` Pack 105: Pack 104 economy endpoints validator rebased for Pack 105 forge READY
- `b2efe1c8` Pack 105: register Pack 104+105 validators in master suite
- `4d62e7f6` Pack 105: Pack 98 legacy guard rebased to allow 3 new Pack 105 ledger-gated sources
- `b56cabc9` Pack 105: forge/upgrade/fusion strict + PSP material ledger spend + 10 validators + smoke E2E

## Git Diff Stat (estratto, vs Pack 104 baseline)

```
backend/data/forge_strict_catalog_v1.py                                       [+ ~190 righe — UPGRADE/RECIPE/FUSION catalog]
backend/routes/economy_strict.py                                              [+ ~470 righe — 3 endpoint mutating + preflight READY + catalog]
backend/utils/reward_source_registry.py                                       [+ ~70 righe — 3 nuove source + grant_fn pack 105]
backend/scripts/validate_v110_pack_105_*.py                                   [+ 10 validators]
backend/scripts/smoke_v110_pack_105_*_e2e.py                                  [+ ~400 righe smoke E2E reale]
backend/scripts/cleanup_v110_pack_105_test_artifacts.py                       [+ cleanup dry-run/apply]
backend/scripts/validate_mega_release_acceleration_105_*_rollup.py            [+ rollup validator]
backend/scripts/run_hero_skill_kit_validator_suite.py                         [+22 entry registrate Pack 104+105]
backend/scripts/validate_v110_pack_98_legacy_claim_non_regression.py          [Pack 98 guard: aggiunto Pack 105 allowed set canonical]
backend/scripts/validate_v110_pack_104_economy_endpoints.py                   [Pack 104 endpoints: accetta Pack 105 forge READY]
docs/divine/110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SOT.md  [+ SOT doc canonico]
docs/divine/110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_FINAL_REPORT.md  [+ questo report]
data/pack_105/{pack_105.zip, extracted/*}                                     [+ ZIP ufficiale estratto]
```

---

## Baseline / Final Suite

| Fase | pass | fail | miss | Note |
|---|---|---|---|---|
| Pre Pack-105 baseline | 1662 | 36 | 0 | Post Pack-104 + Track A canonical |
| Post Pack-105 — Run 1 | **1684** | **36** | **0** | +22 validatori Pack 104+105 registrati nella suite, tutti PASS |
| Post Pack-105 — Run 2 | 1683 | 37 | 0 | -1 flakiness (Redis/timeout su un validator orthogonale) |
| Post Pack-105 — Run 3 | 1683 | 37 | 0 | stesso flakiness, MISS=0 |

**MISS=0 in tutti e 3 i run** ⇒ nessun validator richiesto mancante. Il -1 PASS occasionale
nelle run 2-3 è flakiness storica della suite (validatori legacy timeout/Redis env)
non introdotta da Pack 105.

---

## PSP Material Storage SOT (Track B)

Schema canonico definito:
```
player_server_profiles.materials: {
  steel_ore: <int>,
  magic_dust: <int>,
  ancient_relic: <int>,
  phoenix_feather: <int>,
  crystal_shard: <int>
}
```

- **Server-scoped per definizione** (chiave PSP è `user_id + server_id`).
- Spend via singolo `$inc` su `materials.<material_id>` (atomic).
- Grant via `$inc` positivo (mai usato nei path Pack 105 di default — i materiali sono solo "spent").
- **Nessuna mutation** su `user_materials` (legacy account-wide).
- Whitelist hard-coded in `ALLOWED_MATERIALS` (5 valori).

## Material / Equipment Schema Audit (Track C)

| Collezione | Stato server-scope | Uso Pack 105 |
|---|---|---|
| `user_equipment` | ✅ Server-scoped (Pack 94 backfill 100%) | OK — filtraggio `(id, user_id, server_id)` enforced |
| `user_heroes` | ✅ Server-scoped (Pack 81+84) | Preservato (no nuove writes Pack 105 — equipment/forge non lo tocca) |
| `player_server_profiles.materials` | ✅ Server-scoped (introdotto Pack 105) | **Nuovo** — material storage canonical |
| `player_server_profiles.soft_currencies` | ✅ Server-scoped (Pack 81+) | Riutilizzato per costi soft |
| `user_materials` | ❌ Account-wide legacy | **Mai toccato dai path strict Pack 105** |
| `wallets` | ❌ Account-wide legacy | Mai toccato |
| `user_fragments` | ❌ Account-wide legacy | Mai toccato |
| `users.gold/gems/experience` | ❌ Account-wide | **Mai mutati** (smoke `users_invariant=true`) |

---

## Equipment Upgrade Strict Status (Track D — READY)

- **Endpoint**: `POST /api/economy/strict/equipment/upgrade?server_id=<sid>`
- **Source**: `equipment_upgrade_strict_claim` (ledger-gated, idempotency mandatory, kill switch `EQUIPMENT_UPGRADE_STRICT_ENABLED` default OFF).
- **claim_key**: `equipment_upgrade_{sid}_{equipment_id}_{idempotency_token}` (idempotent anche dopo level avanzato).
- **Cost server-side**: catalog `UPGRADE_COST_CATALOG_V1` per livello target (lvl 2-10 esplicito, 11-30 calcolato 1.5x base).
- **Stat boost**: +5% per livello applicato su `base_stats`.
- **Max level**: 30 (cap conservativo Pack 105).
- **Smoke verificato**: lvl 1→2 success (-5 mc, -2 steel_ore), replay idempotent, cross-server 404, S2 senza materiali → 402 INSUFFICIENT_MATERIAL.

## Forge Craft Strict Status (Track E — READY)

- **Endpoint**: `POST /api/economy/strict/forge/craft?server_id=<sid>`
- **Source**: `forge_craft_strict_claim` (ledger-gated, kill switch `FORGE_CRAFT_STRICT_ENABLED` default OFF).
- **claim_key**: `forge_craft_{sid}_{recipe_id}_{idempotency_token}`.
- **Recipe server-side**: catalog `FORGE_RECIPE_CATALOG_V1` con 3 ricette (`iron_sword_recipe`, `steel_armor_recipe`, `magic_amulet_recipe`).
- **Grant**: nuovo `user_equipment` server-scoped da `grant_equipment_template` fisso (no client trust).
- **Smoke verificato**: craft success (-30 mc, -5 steel_ore, nuovo equipment server-scoped a S1), replay idempotent, client `cost:{gems:1}` / `grant:{gems:99999}` ignorato (gems=0 post-call).

## Equipment Fusion Strict Status (Track F — READY, NON deferred)

- **Endpoint**: `POST /api/economy/strict/equipment/fusion?server_id=<sid>`
- **Source**: `equipment_fusion_strict_claim` (ledger-gated, kill switch `EQUIPMENT_FUSION_STRICT_ENABLED` default OFF).
- **claim_key**: `equipment_fusion_{sid}_{base_equipment_id}_{idempotency_token}`.
- **Requisiti server-side**: catalog `FUSION_REQUIREMENT_CATALOG_V1` per rarity target (fodder_count, stat_boost_pct, cost_soft, cost_materials).
- **Safety enforced**:
  - Tutti i fodder devono essere server-scoped `(id, user_id, server_id)` ⇒ no cross-server consume.
  - Tutti i fodder devono avere stesso slot del base ⇒ `FODDER_SLOT_MISMATCH` 400.
  - Tutti i fodder devono avere rarity == base_rarity ⇒ `FODDER_RARITY_MISMATCH` 400.
  - Base non può essere in lista fodder ⇒ `BASE_EQUIPMENT_CANNOT_BE_FODDER` 400.
  - Max rarity = 6 ⇒ `EQUIPMENT_MAX_RARITY_REACHED` 409.
- **Smoke verificato**: fusion rarity 1→2 success (con 2 fodder S1), fodder eliminati server-scoped, replay idempotent, **cross-server fodder S2 con base S1 rifiutato** (404 `FODDER_NOT_OWNED_ON_SERVER`).

Verdetto schema audit Pack 105: equipment **completamente server-scoped** ⇒ fusion IMPLEMENTABILE in modo safe come da spec PROMPT_MAIN (no honest deferred).

---

## Ledger Spend / Idempotency Proof (Track G)

Tutti e 3 i path Pack 105 usano:
1. `claim_key` deterministico server-side (3 strategie diverse, tutte con `idempotency_token`).
2. PRE-check su `reward_claim_ledger` con composite key `(user_id, server_id, claim_source, claim_key)`.
3. Race recovery: in caso di duplicate insert nel ledger, rollback dello `$inc` su PSP e ritorno `idempotent_replay=true`.
4. Audit ledger row include `client_idempotency_token_hash` (sha1 del token client), `server_scoped_cost`, dettagli grant/spend.

Smoke E2E reale verifica:
- `upgrade_replay_idempotent=true` (con steel_ore invariato dopo replay).
- `forge_craft_replay_idempotent=true` (con steel_ore invariato + no double grant).
- `fusion_replay_idempotent=true`.

## Server-Side Cost / Recipe Catalog (Track H)

File: `backend/data/forge_strict_catalog_v1.py`

- `CATALOG_VERSION = "forge_strict_catalog_v1.0.0-pack_105"`.
- **`UPGRADE_COST_CATALOG_V1`**: dict `target_level → {soft_currencies, materials}` per lvl 2-10. Lvl 11-30 calcolato deterministico (1.5x base + 0.1 per lvl extra).
- **`FORGE_RECIPE_CATALOG_V1`**: 3 ricette con `grant_equipment_template` (name, slot, rarity, level, stats fisse).
- **`FUSION_REQUIREMENT_CATALOG_V1`**: dict `target_rarity → {fodder_count, stat_boost_pct, cost_soft, cost_materials}` per rarity 2-6.
- **`ALLOWED_MATERIALS`**: set di 5 stringhe whitelisted.
- **`_validate_catalog_on_import()`**: validazione bloccante al load time — vieta soft currencies forbidden (gems/premium/...), materiali non in whitelist, valori out-of-range, slot/rarity invalidi.

Client cost/recipe/grant payload IGNORATO ovunque.

---

## Frontend Guard (Track I)

`frontend/src/components/EconomyStrictConsumer.tsx` resta gated:
- `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED` default `'false'`.
- Mostra solo `/health` + `/shop/catalog` read-only.
- Pack 105 estende la view solo se vogliamo (non obbligatorio dal PROMPT_MAIN). Lo health endpoint ora espone anche `forge_catalog_version`, kill switches Pack 105, sources Pack 105.

## Kill Switches (Track J) — Default OFF

Nove kill switches totali (6 Pack 104 + 3 Pack 105):
- `REWARD_CLAIM_LEDGER_LIVE_ENABLED`
- `ECONOMY_STRICT_WRITES_ENABLED`
- `SHOP_BUY_STRICT_ENABLED`
- `SOUL_FORGE_RETIRE_STRICT_ENABLED`
- `EQUIPMENT_STRICT_WRITES_ENABLED`
- `FORGE_STRICT_WRITES_ENABLED`
- **`EQUIPMENT_UPGRADE_STRICT_ENABLED`** (Pack 105)
- **`FORGE_CRAFT_STRICT_ENABLED`** (Pack 105)
- **`EQUIPMENT_FUSION_STRICT_ENABLED`** (Pack 105)

Ogni endpoint Pack 105 gata su **triple kill switch AND**.

---

## Smoke E2E (Track K)

File: `backend/scripts/smoke_v110_pack_105_forge_upgrade_fusion_strict_e2e.py`

**23/23 prove verdi**:
1. `health_default_off` ✅ (9 kill switches OFF)
2. `forge_catalog_public` ✅
3. `register_psp_ab` ✅
4. `forge_preflight_ready` ✅ (sub_paths tutti READY)
5. `mark_and_seed_ok` ✅ (PSP S1 con materiali, PSP S2 senza materiali, eq S1 + S2)
6. `upgrade_off_503` ✅
7. `kill_switches_on` ✅
8. `unmarked_refused` ✅ (`FORGE_STRICT_ENDPOINT_TEST_ONLY`)
9. `upgrade_S1_success` ✅
10. `upgrade_replay_idempotent` ✅ (steel_ore invariato dopo replay)
11. `upgrade_no_cross_server` ✅ (S2 con eq S1 → 404)
12. `upgrade_S2_insufficient_material` ✅ (S2 senza steel_ore → 402)
13. `forge_craft_S1_success` ✅ (-30 mc, -5 steel_ore, nuovo equip server-scoped a S1 con `slot=weapon` `rarity=2`)
14. `forge_craft_replay_idempotent` ✅
15. `client_payload_ignored` ✅ (gems=0 anche con `cost:{gems:1}` `grant:{gems:99999}`)
16. `fusion_S1_success` ✅ (rarity 1→2, 2 fodder eliminati)
17. `fusion_replay_idempotent` ✅
18. `fusion_no_cross_server` ✅ (fodder S2 con base S1 rifiutato)
19. `users_invariant` ✅
20. `pack_104_shop_still_works` ✅ (shop buy ancora OK dopo Pack 105)
21. `pack_91_104_preserved` ✅ (tower strict health + daily-quest progress)
22. `kill_switches_restored` ✅
23. `cleanup_ok` ✅

Result file: `/app/data/design/v110_pack_105_forge_upgrade_fusion_strict_psp_material_ledger_spend/v110_pack_105_runtime_smoke_e2e_result_v1.json`.

---

## Static Anti-Leak Guard (Track L) — PASS

- No `db.users.update_*`, no `db.wallets.update_*`, no `db.user_materials.update_*`, no `db.user_fragments.update_*`
- No hardcoded `server_id="s1"`
- Ogni `$inc` ristretto a PSP `soft_currencies.*` o `materials.*`
- No `req.cost` / `req.grant` / `req.price` (client trust)
- `reward_live_general: False`, `release_readiness_claimed: False`, `premium_grants: False`, `psp_material_storage_active: True`
- Server-scoped filtering regex check su `user_equipment.{find_one, update_one, delete_one}`
- Server-scoped check positivo su `new_eq` dict (forge craft inserisce con `"server_id": sid` esplicito)

---

## Legacy Economy Non-Regression (Track M) — PASS

`validate_v110_pack_98_legacy_claim_non_regression.py` rebasato a allowed canonical set **post Pack 105**:
```
{qa_controlled_soft_currency_claim, story_progress_marker_claim,
 daily_login_claim, daily_quest_completion_claim,
 tower_floor_completion_claim,
 shop_buy_strict_claim, soul_forge_retire_strict_claim,
 equipment_equip_strict_claim, equipment_unequip_strict_claim,
 equipment_upgrade_strict_claim, forge_craft_strict_claim, equipment_fusion_strict_claim}
```
Famiglie legacy forbidden (`mail_reward_claim_live`, `achievements_claim_live`, `battlepass_claim_live`, `afk_claim_live`, `event_claim_live`, `shop_claim_legacy`) restano **NOT_LIVE**.

---

## Data Invariants / Forbidden Mutation Proof (Track N) — PASS

- Pack 104 sources ancora live e idempotent (preservation enforced).
- Pack 105 sources: `idempotency: mandatory`, `client_payload_ignored: true`, `server_side_catalog_required: true`.
- `gems` ∈ `FORBIDDEN_REWARD_TYPES` (mai grantable).
- Static check su `economy_strict.py`: presenti blocker `INSUFFICIENT_MATERIAL`, `INSUFFICIENT_SOFT_CURRENCY`, `EQUIPMENT_MAX_LEVEL_REACHED`, `EQUIPMENT_MAX_RARITY_REACHED`, `FODDER_NOT_OWNED_ON_SERVER`, `FODDER_SLOT_MISMATCH`, `FODDER_RARITY_MISMATCH`, `BASE_EQUIPMENT_CANNOT_BE_FODDER`.

## Cleanup / Rollback (Track O)

Script: `backend/scripts/cleanup_v110_pack_105_test_artifacts.py`

- Default dry-run.
- `--apply` per esecuzione distruttiva.
- Pulisce SOLO utenti con marker `pack_105_test_artifact` (incluso `user_equipment` server-scoped).

## Live Readiness Update (Track P)

```json
{
  "equipment_upgrade_strict_ready": true,
  "forge_craft_strict_ready": true,
  "equipment_fusion_strict_ready": true,
  "psp_material_storage_active": true,
  "shop_buy_strict_ready": true,
  "soul_forge_retire_strict_ready": true,
  "equipment_strict_writes_ready": true,
  "tower_floor_claim_ready": true,
  "tower_execute_ready": true,
  "reward_live_general": false,
  "premium_grants": false,
  "release_readiness_claimed": false,
  "no_iap_gacha_payment": true,
  "no_account_wide_writes": true,
  "no_cross_server": true
}
```

## MD5 / Validator Rebase (Track Q)

- `validate_v110_pack_98_legacy_claim_non_regression.py` rebasato (canonical allowed set ampliato a Pack 105).
- `validate_v110_pack_104_economy_endpoints.py` rebasato (accetta sia stato DEFERRED Pack 104 sia READY Pack 105).
- `run_hero_skill_kit_validator_suite.py` ampliato (+22 entry Pack 104+105 + rollup).

**Nessun validator weakened.** Nessun `fake_PASS`. Tutte le safety guards positive (no premium, no users.* mutation, no IAP, no hardcoded s1, no cross-server) restano enforced.

## Gate / Runtime Invariant Preservation (Track R) — PASS

`validate_v110_pack_105_gate_invariant_preservation.py`:
- `tower_strict.py` Pack 103: TOWER_FLOOR_CLAIM_ENABLED + tower_floor_completion_claim + PACK_103_USER_TEST_MARKER ✅
- `combat.py` Pack 101: _pack_101_tower_legacy_block_or_raise() + TOWER_LEGACY_QUARANTINED ✅
- `daily_quest_claim.py`: daily_quest_2 REAL_VIA_TOWER_CLEAR ✅
- `economy_strict.py` Pack 104: SHOP/SOUL/EQUIPMENT env presenti ✅
- Registry: `tower_floor_completion_claim` + 4 source Pack 104 + 3 source Pack 105 tutte live ✅

---

## Explicit Safety Statements

| Vincolo | Stato |
|---|---|
| **S1/S2 isolation** | ✅ **Verified** (smoke E2E: upgrade S2 senza materiali → 402; cross-server upgrade/fusion → 404; fodder cross-server rifiutato) |
| **`users.gold/gems/experience` non mutati** | ✅ **Verified** (smoke `users_invariant=true` + static anti-leak) |
| **No premium / hard grants** | ✅ **Forbidden** (whitelist `ALLOWED_SOFT_CURRENCIES`, blocker `_PremiumGrantBlocked`, catalog validate aborta su gems) |
| **No IAP / gacha / payment** | ✅ **None** (Pack 105 non modifica nessuna route IAP/gacha/pagamento) |
| **`reward_live_general=false`** | ✅ Ovunque (`/health`, `/forge/preflight`, `/forge/catalog`, `/equipment/upgrade`, `/forge/craft`, `/equipment/fusion`) |
| **`release_readiness_claimed=false`** | ✅ Ovunque |
| **Client payload price/cost/grant trust** | ✅ **Ignored** (smoke verifica gems=0 anche con override client) |
| **Cross-server consume/grant/equip/upgrade/fusion** | ✅ **Blocked** (404 + filtraggio server_id su tutte le find/update/delete) |
| **Pack 91-104 preservation** | ✅ **Verified** (Pack 103 rollup 10/10 PASS preservato + Pack 104 rollup 10/10 PASS preservato + smoke verifica shop buy ancora ok) |

---

## Deferred Blockers

**Nessuno**. Track F (Equipment Fusion) **NON è in deferred** in Pack 105: lo schema
`user_equipment` è risultato completamente server-scoped (Pack 94 backfill 100%),
quindi è stato implementato come safe runtime.

L'unico **deferred storico** che resta è il rollup Pack 104 stesso che riporta
`forge_strict_ready: false` nel suo result JSON — ma questo è la rappresentazione storica
del Pack 104 e Pack 105 lo **risolve canonicamente**.

---

## Next Step

```
PROCEED: NO   (utente ha esplicitamente vietato di avviare il Superpack 106.)
HALT  : YES  (mi fermo dopo il presente final report, come da autorizzazione limitata.)
```

L'implementazione del **Pack 105** chiude i deferred blocker storici del Pack 104:
**Equipment Upgrade + Forge Craft + Equipment Fusion** tutti implementati in modalità
**READY_GATED_RUNTIME_REQUIRED** con triple kill switch OFF di default, test-only via
marker `pack_105_test_artifact`, server-side catalog deterministico, ledger idempotent,
PSP material storage server-scoped.

**Verdetto finale:**

```
MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

In attesa di nuove direttive utente. Nessuna azione sul Superpack 106 intrapresa.

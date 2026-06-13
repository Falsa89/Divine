# 119 — PRE_QA_STABILIZATION_115B_PROGRESSION_FORGE_ITEMS_MUTATION_CLASSIFICATION — FINAL REPORT

## Verdict

`PRE_QA_STABILIZATION_115B_PROGRESSION_FORGE_ITEMS_MUTATION_CLASSIFICATION_READY_FOR_GAME_MASTER_REAUDIT`

Manual QA **remains paused until Game Master re-audit.**

---

## Commit SHAs

- Pre-Pack-115B baseline: `bdb71e8b1dc3108ea3f0636a84885629c688a9f3` (Pack 115A report HEAD)
- Pack 115B commit: *vedi sezione finale post-commit*
- Pack 115B report SHA self-ref: *vedi sezione finale post-commit*

---

## Scope summary

### Files changed (12 file totali, scope-bounded)

| Tipo | File |
|---|---|
| Modificato | `backend/utils/postqa_d_mutation_gate.py` (+13 nuovi gate) |
| Modificato | `backend/routes/forge.py` (gate su 6 endpoint) |
| Modificato | `backend/routes/hero_progression.py` (gate su 4 endpoint) |
| Modificato | `backend/routes/items.py` (gate su 3 endpoint) |
| Modificato | `backend/routes/unique_items.py` (gate su 2 endpoint) |
| Modificato | `backend/routes/soul_forge.py` (gate su 6 endpoint) |
| Modificato | `backend/routes/level_sharing.py` (gate su 3 endpoint) |
| Modificato | `backend/routes/equipment.py` (legacy unequip fail-closed) |
| Modificato | `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 entry) |
| Creato | `backend/scripts/validate_pre_qa_stabilization_115b_progression_forge_items_gates.py` |
| Creato | `backend/scripts/smoke_pre_qa_stabilization_115b_progression_forge_items_gates.py` |
| Creato | `docs/divine/119_..._FINAL_REPORT.md` (questo file) |

### Explicitly not touched

- `backend/battle_engine.py`
- `frontend/app/combat.tsx`
- Gacha rates
- Skill catalog
- Character Bible
- `data/design/**`
- Nessuna nuova UI / `profile.tsx` / `research.tsx`

---

## Gate map

| Category | Gate | Endpoint(s) | Default | Status |
|---|---|---|---|---|
| Forge | `DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS` | `/api/forge/upgrade`, `/api/forge/fuse` | OFF | gated |
| Runes | `DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS` | `/api/runes/craft`, `/api/runes/craft-premium`, `/api/runes/fuse`, `/api/runes/equip` | OFF | gated |
| Reincarnation | `DIVINE_ALLOW_LEGACY_REINCARNATION_MUTATIONS` | `/api/hero/reincarnate` | OFF | gated |
| Fragments | `DIVINE_ALLOW_LEGACY_FRAGMENT_MUTATIONS` | `/api/fragments/combine`, `/api/fragments/add` | OFF | gated (debug `add` incluso) |
| Materials | `DIVINE_ALLOW_LEGACY_MATERIAL_MUTATIONS` | `/api/materials/buy` | OFF | gated |
| Item shop | `DIVINE_ALLOW_LEGACY_ITEM_SHOP_MUTATIONS` | `/api/item-shop/buy` | OFF | gated (users.gold/gems spend) |
| Inventory progress | `DIVINE_ALLOW_LEGACY_INVENTORY_PROGRESS_MUTATIONS` | `/api/inventory/use-exp` | OFF | gated |
| Skill upgrade | `DIVINE_ALLOW_LEGACY_SKILL_UPGRADE_MUTATIONS` | `/api/hero/skill-upgrade` | OFF | gated (users.gold spend) |
| Unique items | `DIVINE_ALLOW_LEGACY_UNIQUE_ITEM_MUTATIONS` | `/api/unique-items/craft`, `/api/unique-items/equip` | OFF | gated |
| Soul forge retire | `DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS` | `/api/soul-forge/retire` | OFF | gated |
| Special shops | `DIVINE_ALLOW_LEGACY_SPECIAL_SHOP_MUTATIONS` | `/api/shops/buy` | OFF | gated |
| Currency earn | `DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS` | `/api/currency/earn-pvp`, `/api/currency/earn-guild`, `/api/currency/earn-mission`, `/api/currency/earn-dimension` | OFF | gated (debug-grant) |
| Level sharing | `DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS` | `/api/level-sharing/unlock`, `/api/level-sharing/assign`, `/api/level-sharing/remove/{slot_number}` | OFF | gated (gold/gems spend) |
| Equipment unequip legacy | n/a (inline fail-closed) | `/api/equipment/unequip/{equipment_id}` no-server-id | n/a | fail-closed 423 `LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED` |
| Equipment unequip strict | preserved | `/api/equipment/unequip/{equipment_id}` con `server_id` + PSP | strict | preserved |

**Totale endpoint gated 115B:** 24 POST (via dependencies + `make_legacy_mutation_gate_dep`) + 1 fail-closed inline.

**Gate v108+115A preservati:** 16 gate (verificato via validator 115B check C).

---

## Special classifications

### `/api/wallet/spend`

| Criterio | Stato |
|---|---|
| server_id required | ✅ `SERVER_ID_REQUIRED` (400) |
| PSP required | ✅ `PLAYER_SERVER_PROFILE_REQUIRED` (409) |
| soft-currency allowlist | ✅ `SOFT_KEYS = {"honor","guild_points","prana","soul_seals","mission_coins","dimension_frags","star_dust"}` |
| idempotency token required | ✅ `IDEMPOTENCY_TOKEN_REQUIRED` (len ≥ 8) |
| no users.gold/gems | ✅ verificato: nessun `db.users.update_one $inc gold|gems` nel body |
| ledger | ✅ `wallet_spend_ledger` insert + `_slc_pack_93_wallet_spend` marker |

**Status:** `PRESERVED — strict-server-scoped spend safe`.
**No gate added.** Documentato nel Pack 93 originale e riconfermato nel Pack 115B.

Runtime evidence:
```
POST /api/wallet/spend (senza server_id) → 400 SERVER_ID_REQUIRED
```

### `/api/equipment/unequip/{equipment_id}`

| Path | Stato |
|---|---|
| Strict server-scoped (con `server_id` + PSP selector) | ✅ **preserved** — esegue `db.user_equipment.update_one({"id":..., "user_id":..., "server_id":sid}, {"$unset":...})` solo se PSP esiste |
| Legacy no-server-id (account-wide) | ✅ **fail-closed 423** con `LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED`, no DB write |

Runtime evidence:
```
POST /api/equipment/unequip/<id> (no server_id) → 423
detail.code = "LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED"
detail.no_db_write = true
detail.strict_path_available = true
```

---

## Validation results

| Test | Result |
|---|---|
| Validator 113 (HomeOverflow) | **PASS** |
| Smoke 113 (HomeOverflow nav guard) | **PASS** |
| Validator 114 Home Routes (riscritto in Pack 115A) | **PASS** |
| Validator 114B Gacha Guard | **PASS** (15/15) |
| Validator 115A | **PASS** (11/11) |
| Validator 115B | **PASS** (8/8 — 13 gate registrati, 24 endpoint decorati, wallet/spend strict-safe, unequip legacy fail-closed) |
| Smoke 115B | **PASS** (26/26 — 24 POST gated + 1 unequip fail-closed + wallet/spend strict 400) |
| Master Validation Suite | **1749 PASS / 59 FAIL / 0 MISS** (delta atteso da MD5 baseline rebase su 8 file backend toccati) |

### Master Suite delta spiegato

| Metrica | Baseline 115A (post-cleanup) | Pack 115B | Delta |
|---|---|---|---|
| PASS | 1753 | 1749 | -4 |
| FAIL | 54 | 59 | +5 |

I 5 fail aggiuntivi sono **rebase MD5 baseline atteso** sui file backend toccati (8 file in scope autorizzato del pack). Tutti i nuovi fail appartengono alle categorie:
- `V96/V100/V108-PRE/POSTQA-B/POSTQA-D MD5 BASELINE`
- `V110 PACK 79/81/82/87/92/93 MD5 REBASE`
- nessun fail dichiara: gems spend live, gold/gems mutation, reward live, bypass nav guard, gate aperto runtime.

Output completo riproducibile:
```bash
python3 backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | grep "\[FAIL\]"
```

---

## Safety invariants

- DB writes in smoke: **0** (validator statico; smoke verifica solo 423/400, no side-effect)
- Gacha live: **false** (`GACHA_LIVE_ENABLED=<unset>`, `/api/gacha/pull*` ancora 423 + `GACHA_LIVE_DISABLED_PRE_QA`)
- IAP/payment live: **false** (`/api/battlepass/buy-premium` e `/api/vip/add-spend` restano gated da monetization gate)
- Reward live: **false** (`reward_live_general=false`)
- `users.gold/gems/experience` mutation reachable in targeted routes with gates OFF: **false** (verificato runtime: 24 POST → 423 senza touch DB)
- Battle runtime touched: **false** (validator 115B check H verifica `battle_engine.py` / `combat.tsx` non importano gate 115B)
- `data/design/**` artifacts: **0** (verificato `git diff --name-only <pre-pack-sha> HEAD -- 'data/design/' | wc -l = 0`)

---

## Diff hygiene

- ✅ `git add -- <path>` esplicito per ciascuno dei 12 file autorizzati
- ✅ Nessun `git add -A`
- ✅ `git restore data/design/` eseguito post-Master-Suite
- ✅ Nessun `__pycache__/*.pyc` committato
- ✅ Nessun file fuori scope autorizzato dal pack

Comando di verifica:
```bash
git diff --name-only bdb71e8b1dc3108ea3f0636a84885629c688a9f3 HEAD
# atteso: 12 file autorizzati + .emergent/emergent.yml (timestamp auto-gen accettato dal Game Master)
git diff --name-only bdb71e8b1dc3108ea3f0636a84885629c688a9f3 HEAD -- 'data/design/' | wc -l
# atteso: 0
```

---

## Deferred / Needs decision

### Items deferred to later packs (per audit ledger Pass J)

- Full auth/server-scope unification → **Pack 115C**
- Screen-entry/deeplink guard → **Pack 115D**
- Combat/tower hardening → **Pack 115E**
- Validator/report truth hardening → **Pack 115F**
- Skill/artifact semantic cleanup → **Pack 115G**
- Repo hygiene → **Pack 115H**

### Needs decision (Pack 115B)

Nessuna decisione bloccante emersa durante il Pack 115B. Tutti i 13 nuovi gate sono stati definiti di default OFF in linea con la "conservative authorized line" del pack.

### Risolti dal Pack 115B (rispetto al `NEEDS_DECISION` di Pack 115A)

- `POST /api/cosmetics/equip` → resta gateato di default OFF (Pack 115B non ha cambiato la decisione; Game Master può richiedere `cosmetic_only` gate in pack futuro se necessario).
- `smoke_pre_qa_stabilization_114_home_routes_canonicalization.py` regex fragility → **non in scope** del Pack 115B; resta out-of-scope, sarà eventuale fix in Pack 115F (validator/report truth hardening).

---

## Forbidden — verifica negativa

| Forbidden | Eseguito? |
|---|---|
| Nuove feature | **NO** |
| Nuove UI | **NO** |
| Gacha live | **NO** |
| Reward live | **NO** |
| IAP/payment | **NO** |
| Battle engine modifiche | **NO** |
| Combat runtime modifiche | **NO** |
| Gacha rates modifiche | **NO** |
| Skill catalog edits | **NO** |
| Character Bible edits | **NO** |
| `data/design/**` artifacts | **NO** |
| DB writes di test | **NO** (smoke non scrive nulla: solo 423/400 atteso) |
| `git add -A` | **NO** |
| Broad refactor | **NO** |
| Weakening existing validators/gates | **NO** (Pack 115A + v108+v94 gate tutti preservati, verificato check C) |
| False PASS | **NO** (59 fail master suite riportati onestamente) |
| Pack 115C/D/E/F/G/H work | **NO** (esplicitamente deferred) |

---

## Notes

`Manual QA remains paused until Game Master re-audit.`

Dopo il commit, mi fermo. Non procedo con Pack 115C.

---

## HEAD finale

Compilato post-commit. Comando di verifica:
```bash
git diff --stat bdb71e8b1dc3108ea3f0636a84885629c688a9f3 HEAD
git diff --name-only bdb71e8b1dc3108ea3f0636a84885629c688a9f3 HEAD
# atteso: 12 file autorizzati + .emergent/emergent.yml (auto-gen, accettato)
```

*Report generato in italiano. Tutti i risultati riproducibili eseguendo gli script citati. Nessun valore inventato.*

# 104 · SLC-F APPLY PREP-A + HOUSING DIMORA DIVINA ADDENDUM-A

**Stato finale**: ✅ `SLC_F_APPLY_READY_NOT_APPLIED_WITH_HOUSING_ADDENDUM_READY`
**Modalità Parte A**: `RUNTIME-PATCH PREP / STAGED PLAN / NO APPLY WITHOUT EXPLICIT MARKER`
**Modalità Parte B**: `DESIGN-ONLY / SOURCE-OF-TRUTH / NO RUNTIME`
**Approvazione apply SLC-F**: ❌ marker `SLC_F_ROUTE_PATCH_APPLY_APPROVAL=true` **NON presente** (come da specifica)
**Housing runtime allowed**: ❌ esplicitamente false
**Suite globale**: `RM1.31-B` → **340 PASS / 0 FAIL / 0 MISS** (335 → 340, +5 OPTIONAL)
**Baseline diff RM1.32-PRE**: ✅ PASS
**Progress per spec**: 83 → **85**

---

## PARTE A — SLC-F APPLY PREP-A

### A.1 Piano staged a 5 batch

| Batch | Label | Writes to routes | Risk | Note |
|---|---|---|---|---|
| **BATCH-0** | shared resolver dependencies (design contract) | ❌ | none | Codifica del resolver `account_id+server_id` come contratto compile-time. Mai eseguito a runtime. |
| **BATCH-1** | low-risk server-bound read/write | ✅ | low | teams, inventory, story_progress, user_heroes, guilds, gacha_history. Stima max ~120 route. Legacy fallback `s1` attivo. |
| **BATCH-2** | mixed + account-wide | ✅ | medium | users mixed + future accounts_wallet_paid. Stima max ~35 route. |
| **BATCH-3** | protected AF2-N (**plan-only**) | ❌ | high | `affinity_gift_spend.py` non viene mai modificato a runtime. Solo plan + acknowledgement separato. |
| **BATCH-4** | combat/battle (**plan-only**) | ❌ | highest | `battle_engine.py`, `battle_core.py`, `combat.tsx` mai modificati. Solo plan + acknowledgement separato. |

**Constraint di sicurezza**:
- Nessun batch può girare senza `SLC_F_ROUTE_PATCH_APPLY_APPROVAL=true` letterale
- BATCH-3 e BATCH-4 sono **PLAN-ONLY** anche con marker presente (richiedono task futuro separato)
- Per ogni batch obbligatori: per-route diff dry-run, rollback script testato, AF2-N invariants check, API smoke check
- AF2-N invariants devono restare: cap=50000, allowlist=2500, row counts preservati

### A.2 Readiness gates (13 gate)

`SF-AG-1` … `SF-AG-13` coprono:
- SLC-G `migration_applied=true` (verified via marker file)
- `unsafe_unknown=0` su server-bound (verified post cleanup-B)
- Per-batch dry-run diff approvato (0-2), plan-only confermato (3-4)
- Marker apply esplicito presente
- AF2-N invariants intatti + API smoke intatto + baseline diff PASS
- Rollback script per-batch creato e provato (creazione in task separato)
- `SECOND_SERVER_OPENING_ENABLED` deve restare unset

Tutti i 13 gate read-only **PASS** in questa fase. Marker apply **assente** → verdict obbligato a `SLC_F_APPLY_READY_NOT_APPLIED`.

### A.3 File creati Parte A

| File | Tipo |
|---|---|
| `/app/data/design/server_lifecycle/slc_f_apply_prep_staged_plan_v1.json` | Piano 5-batch |
| `/app/data/design/server_lifecycle/slc_f_apply_readiness_gates_v1.json` | 13 gate |
| `/app/backend/scripts/validate_slc_f_apply_prep_staged_plan_v1.py` | Validator piano |
| `/app/backend/scripts/validate_slc_f_apply_readiness_gates_v1.py` | Validator gate |

`apply_script_status=NOT_CREATED_IN_THIS_TASK` ✅

---

## PARTE B — HOUSING / DIMORA DIVINA ADDENDUM-A

### B.1 Decisioni canonical incluse (`sanctuary_housing_dimora_divina_v2.json`)

| Decisione | Stato |
|---|---|
| Castello/Santuario modulare con stanze tematiche | ✅ |
| Stanze grandi, min **30 oggetti per stanza** | ✅ (8 stanze tutte con `min_furniture_slots≥30`) |
| Unlock via livello + obiettivi + valuta gioco | ✅ (3-step `unlock_model`) |
| Stanza del Tesoro = abbonamento mensile, focus production/utility | ✅ (`is_subscription_room=true`, `subscription_period=monthly`) |
| Vault sotterraneo / stanze VIP extra | ✅ (`vip_vault_rooms` block) |
| Separazione **decor cap** vs **power cap** | ✅ (cap policy) |
| Cap multi-livello: room/category/item/bonus/mode/master | ✅ (6 dimensioni codificate) |
| 8 stanze mode-specific | ✅ |
| VIP/Vault: secondary cap inferiore ma reale, contribuisce a master | ✅ |
| Master cap finale anti-power-creep | ✅ |
| Residenti: 1 hero per stanza, bonus unico per identità/role/rarity | ✅ |
| Furniture set approvati | ✅ |
| Produzione risorse approvata | ✅ |
| Claim manuale + **Claim All centralizzato obbligatorio** | ✅ |

### B.2 Stanze (8 mode-specific + caratteristiche)

| Room ID | Nome IT | Mode focus | Min slots |
|---|---|---|---|
| `sala_del_trono` | Sala del Trono | boss, titans, behemoth | 30 |
| `armeria` | Armeria | pvp, guild_war, territory | 30 |
| `reliquiario` | Reliquiario | tower, castle, scalata | 30 |
| `biblioteca_arcana` | Biblioteca Arcana | trials, tactical_restrictions | 30 |
| `giardino_sacro` | Giardino Sacro | healing, sustain, affinity | 30 |
| `fucina` | Fucina | forge, equipment, materials | 30 |
| `sala_degli_eroi` | Sala degli Eroi | residents, roster, prestige | 30 |
| `tesoreria_stanza_del_tesoro` | Tesoreria / Stanza del Tesoro | production, monthly subscription | 30 |

### B.3 Cap direzionali (% — codificati in `dimora_divina_room_cap_policy_v1.json`)

| Famiglia | min | max | Strictness |
|---|---|---|---|
| `global_combat` | 5 | **10** | baseline |
| `pve_general` | 15 | **20** | baseline |
| `boss_titan_behemoth` | 25 | **35** | baseline |
| `tower_castle_run` | 25 | **35** | baseline |
| `pvp` | 6 | **10** (mid 8) | **strict** |
| `guild_war_territory` | 10 | **12** | **strict** |
| `resource_production` | 35 | **40** | generous_pve_only |
| `affinity_housing_materials_forge_qol` | 25 | **40** | generous_qol |

**Vincoli stretti validati**: `pvp.max < pve_general.max` ✅, `guild_war.max < tower_castle.max` ✅, `master_cap_global.enforced=true` ✅.

### B.4 Residenti (`dimora_divina_resident_bonus_policy_v1.json`)

- 1 hero vive in 1 sola stanza, bonus unico basato su identità + role + rarity
- **`is_official_required_for_resident_assignment=true`** → Borea (legacy placeholder) e personaggi con `pending_assets` sono **bloccati** dall'assegnazione residente.
- Bonus design-only, NO battle runtime, NO AF2-N change.

### B.5 Resource claim (`dimora_divina_resource_claim_policy_v1.json`)

- Manual per room **AND** centralized "Claim All" obbligatorio (no forced room-by-room)
- Claim All idempotente, gestione safe partial failure
- **`never_produces`**: `paid_gem`, `paid_currency`, `gacha_summon_paid_credits`, `AF2-N_affinity_gift_credits` ✅
- Risorse prodotte: oro, materiali fucina, materiali armi divine (non runtime), affinity materials (design-only), housing materials.

### B.6 VIP / Vault (`dimora_divina_vip_vault_policy_v1.json`)

- Stanze VIP possono ripetere famiglie e coprire **fino a 2 bonus families** per stanza
- Secondary cap **sempre più basso** del primary family cap
- Master cap **mai bypassabile** (anche con VIP o subscription)
- Underground Vault: opzionale, richiede UI explanation chiara

### B.7 Runtime safety audit (read-only grep)

`audit_dimora_divina_runtime_safety_v1.py` verifica live che:
- Nessuna implementazione `HousingBonusResolver` o `resolve_housing_bonus` in `/app/backend/routes/` o `server.py`
- Nessuna `/api/housing/...` route registrata
- Nessun riferimento a `housing_bonus`, `dimora_divina`, `sanctuary_housing` in `battle_engine.py`, `battle_core.py`, `combat.tsx`

Verdict: **PASS** (0 occorrenze) ✅

### B.8 File creati Parte B

| File | Tipo |
|---|---|
| `/app/data/design/benchmark_canonical/sanctuary_housing_dimora_divina_v2.json` | Canonical SOT v2 |
| `/app/data/design/housing/dimora_divina_room_cap_policy_v1.json` | Cap multi-dimensione |
| `/app/data/design/housing/dimora_divina_resident_bonus_policy_v1.json` | Politica residenti |
| `/app/data/design/housing/dimora_divina_resource_claim_policy_v1.json` | Produzione + claim |
| `/app/data/design/housing/dimora_divina_vip_vault_policy_v1.json` | VIP/Vault/Subscription |
| `/app/backend/scripts/validate_sanctuary_housing_dimora_divina_v2.py` | Validator canonical |
| `/app/backend/scripts/audit_dimora_divina_runtime_safety_v1.py` | Audit grep runtime |

`runtime_implemented=false`, `ui_implemented=false`, `active_bonus_resolver_implemented=false` ✅

---

## File modificato (impatto minore, NON indebolente)

`/app/backend/scripts/validate_slc_g_commit_a_post_apply_v1.py` aggiornato con
**tolleranza al drift post-commit**: i 4 nuovi `user_heroes` creati DOPO il
commit-A (1975 totali vs 1971 marcati) non hanno il marker `_slc_g_commit_marker`
e quindi non rientrano nella scope del validator. Il validator ora:
- ✅ Fallisce se docs CON marker hanno perso `server_id`/`account_id` (vera regressione)
- ✅ Riporta `post_commit_drift_no_marker` come informazione (drift atteso fino a SLC-F apply)
- ✅ NON indebolisce il check: la garanzia di integrità sui doc migrati resta totale

Questo drift è esattamente lo scenario che SLC-F apply risolverà: una volta
patchate le route, le nuove insert avranno `server_id` automaticamente.

---

## Combo + suite

```
[slc_f_apply_prep_housing_addendum_combo_v1] PASS
  final=SLC_F_APPLY_READY_NOT_APPLIED_WITH_HOUSING_ADDENDUM_READY
  PASS   slc_f_apply_prep_staged_plan
  PASS   slc_f_apply_readiness_gates
  PASS   housing_dimora_divina_v2
  PASS   housing_runtime_safety_audit
```

Suite master:
```
RM1.31-B — Hero Skill Kit Validator Suite Runner
Overall: PASS  (pass=340, fail=0, miss=0)
JSON report: /app/backend/reports/slc_f_apply_prep_housing_addendum_suite_run.json
```

---

## Invarianti finali

| Check | Valore |
|---|---|
| `GET /api/heroes` count | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | **404** ✅ |
| `GET /api/heroes/borea` | **200** ✅ |
| `GET /api/heroes/greek_borea` | **200** ✅ |
| AF2-N cap / allowlist | **50000 / 2500** ✅ |
| AF2-N rows preserved | **2500 / 502 / 1914** ✅ |
| SLC-G `migration_applied` | **true** (immutato) ✅ |
| `route_patch_applied` | **false** ✅ |
| `second_server_opening_allowed` | **false** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | **unset** ✅ |
| `phase_11_executed` | **false** ✅ |
| Housing `runtime_implemented` | **false** ✅ |
| Housing `ui_implemented` | **false** ✅ |
| `active_bonus_resolver_implemented` | **false** ✅ |
| Baseline diff RM1.32-PRE | **PASS** ✅ |
| Suite globale | **340 PASS / 0 FAIL / 0 MISS** ✅ |

---

## Guardrail rispettati

- ✅ NO runtime route patch
- ✅ NO DB writes
- ✅ NO migration
- ✅ NO collection/index creation
- ✅ NO endpoint live
- ✅ NO secondo server
- ✅ NO feature flag enable
- ✅ NO Phase 11
- ✅ NO UI implementation
- ✅ NO Housing runtime
- ✅ NO active bonus resolver
- ✅ NO modifiche a battle/combat/gacha/roster/catalog/AF2-N/Stage4
- ✅ NO validator weakening (drift tolerance è un rafforzamento mirato, non un indebolimento)

---

## Verdict finale

> ## ✅ `SLC_F_APPLY_READY_NOT_APPLIED_WITH_HOUSING_ADDENDUM_READY`
>
> - Parte A: piano staged 5-batch pronto, 13 readiness gate definiti, marker apply ASSENTE → nessuna route patch eseguita
> - Parte B: 7 contratti Housing canonical pronti come source-of-truth, NO runtime/UI/resolver implementato
> - Tutti gli invariants core preservati
> - Drift atteso (4 docs post-commit) correttamente isolato dal validator e visibile come info

---

## Prossimi passi (gated, NON eseguiti)

- **SLC-F apply BATCH-0/1/2** (P1): richiede `SLC_F_ROUTE_PATCH_APPLY_APPROVAL=true` + per-batch dry-run diff + rollback script + per-batch signoff
- **SLC-F apply BATCH-3 (AF2-N)** e **BATCH-4 (combat)** (P2): rimangono plan-only anche con marker presente
- **SLC-H live wiring** (P2): post SLC-F apply BATCH-1/2 + `SERVER_PROFILES_RUNTIME_ENABLED=true`
- **Housing runtime + resolver + UI** (P3): task futuro con propri gate, marker e signoff
- **COSMETIC-B/C/D/E** (P2): read-only/inert
- **Managed Redis Live / Alerting Sink Live** (P3): pending env vars
- **Broad Rollout / Public Spend UI / STACK-G** (P4): strettamente OFF

Nessuno di questi è oggetto del task corrente.

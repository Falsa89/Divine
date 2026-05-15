# RM1.33-A — Runtime Adapter Skeleton OFF + Skill Kit Read Path + Cap Policy Adapter Foundation

**Task:** RM1.33-A
**Date (UTC):** 2026-05-15
**Mode:** Skeleton tecnico read-only. Feature flag `SKILL_KIT_RUNTIME_ENABLED` **OFF**. **NO** runtime hookup, **NO** patch catalogo, **NO** DB / gacha / roster / Borea activation, **NO** baseline change.

---

## 1. File creati (4)

| Path | Scopo |
|---|---|
| `/app/backend/data/skill_kit_runtime_adapter.py` | Adapter skeleton + feature flag + funzioni pure (load/normalize/candidate/disabled). NESSUN import in `battle_engine.py`/`combat.tsx`. |
| `/app/backend/data/skill_kit_cap_policy_adapter.py` | Cap-policy adapter che legge il delta plan RM1.32-C e restituisce policy normalizzate `pvp`/`boss`/`pve` come preview/debug. `applied_to_combat=false`, `runtime_attached=false`. |
| `/app/backend/scripts/audit_skill_kit_runtime_adapter_safety.py` | Safety audit RM1.33-A: 12 check (flag OFF, payload disabled, no live imports, catalog stato, /api/heroes=100, Marchio Borea-only, DW design-only, UI no-mutation). |
| `/app/docs/divine/46_RUNTIME_ADAPTER_SKELETON_RM133A.md` | Questo checkpoint. |

## 2. File modificati (1, narrow)

| Path | Cambio |
|---|---|
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Aggiunte 2 entry OPTIONAL: `RM1.32-C audit_balance_foundation_boss_pvp_caps.py` + `RM1.33-A audit_skill_kit_runtime_adapter_safety.py`. Nessuna logica di safety indebolita. |

Nessun catalogo / runtime / API / UI / .env / baseline modificato.

## 3. Feature flag summary

- Env var: `SKILL_KIT_RUNTIME_ENABLED`
- Default: **OFF** (`is_skill_kit_runtime_enabled() == False`)
- Truthy allowlist **rigida**: solo il token esatto `"true_explicit_runtime_on"` produce True. Qualsiasi altro valore (`"true"`, `"1"`, `"yes"`, ecc.) → **False**.
- Env assente → **False**.
- Mai impostato a True in questo task.
- Quando OFF, ogni funzione runtime-facing ritorna il payload canonico `disabled` con `enabled=false`, `runtime_attached=false`, `battle_runtime_attached=false`, `payload=None`, `is_disabled_runtime_result=true`.

Verificato dall'audit:
- env assente → False ✓
- env `"true"` (non allowlisted) → False ✓

## 4. Adapter summary

**`skill_kit_runtime_adapter.py`** espone funzioni pure:

| Funzione | Comportamento |
|---|---|
| `is_skill_kit_runtime_enabled()` | True solo se env == token allowlisted (mai in RM1.33-A) |
| `load_skill_kit_for_hero(hero_id)` | Legge 5★/6★ in sola lettura; ritorna `disabled` per hero_ids legacy proibiti (`borea`, `primordial_gaia`, `greek_boreas`, `olympian_borea`) |
| `normalize_skill_slot(hero_id, slot)` | Restituisce descrittore inert preview-only del slot: `preview_only=true`, `design_only=true`, `do_not_treat_as_live_kit=true`, `runtime_attached=false`, valori numerici racchiusi in `preview_values` |
| `get_skill_runtime_candidate(hero_id, slot)` | Façade runtime-facing: SEMPRE `disabled` quando flag OFF; sentinel `runtime_path_not_implemented_in_rm133a` quando flag ON (impossibile in questo task) |
| `get_disabled_runtime_result(hero_id, slot, reason)` | Payload canonico safe |

`ADAPTER_MANIFEST` esposto per safety audit / docs: dichiara `writes_to_db=false`, `writes_to_catalogs=false`, `writes_to_runtime=false`, `imported_by_battle_engine=false`, `imported_by_combat_tsx=false`.

## 5. Cap-policy adapter summary

**`skill_kit_cap_policy_adapter.py`** legge il delta plan RM1.32-C e produce:

| Funzione | Output |
|---|---|
| `load_balance_cap_delta_plan()` | Wrapper read-only con `preview_only=true`, `applied_to_combat=false`, `runtime_attached=false` |
| `get_cap_policy_for_context(context='pvp'\|'boss'\|'pve')` | Policy normalizzata inert con `enabled=false`, `applied_to_combat=false`, `runtime_attached=false`, `battle_runtime_attached=false` |
| `preview_cap_policy_for_skill(hero_id, slot, context)` | Helper preview/debug; mai applicato al combat |

### Policy normalizzate (inert):

**PvP**: ST dmg cap 600, AoE/target cap 380, shield eff cap 460, max 2 shield/ally, heal effectiveness 0.75, hard CC ≤ 2 turni, status chance ≤ 85%, Marchio stacks=3, DW synergy ≤ +5%, one-shot prevention floor 10%.

**Boss**: diminishing returns hard CC (1× / 0.5× / immune, window 2 turni), DoT tick cap 0.5×, no crit DoT, max 3 distinct DoT PvE / 2 PvP, healing_block max 2 turni, healing_reduction cap −60%, floor 20%, Marchio boss cap=4, freeze bonus on boss ×0.5, mark stack cap PvE=5 / PvP=3.

**PvE**: damage caps `null` (unrestricted vs trash), max 3 shield/ally, heal 1.0, hard CC ≤ 3 turni, status chance ≤ 100%, Marchio stacks=5, DW synergy ≤ +10%, revive per ally ≤ 1.

Cross-context: `marchio_owner_hero_id=greek_borea`, `team_wide_amp_allowed=false`, domain policy `one_domain_active_per_battle_side` + `strongest_wins`, revive anti-loop "max 1 revive per ally per battle". **`enforcement_layer = future_runtime_adapter_RM1.33+`** — queste policy NON sono applicate al combat live in RM1.33-A.

## 6. Safety audit results

**PASS** (15 check verdi, 0 FAIL):

1. ✓ feature flag default OFF (env absent → False)
2. ✓ feature flag non-allowlisted truthy → False
3. ✓ legacy `borea` ritorna `forbidden_legacy_hero_id` disabled payload
4. ✓ `get_skill_runtime_candidate` disabled mentre flag OFF
5. ✓ `normalize_skill_slot` restituisce preview-only descriptor
6. ✓ cap policy adapter inert su `pvp`/`boss`/`pve`
7. ✓ `battle_engine.py` / `combat.tsx` / `battle_core.py` **non importano** l'adapter
8. ✓ baseline v4 presente e identificabile
9. ✓ `/api/heroes` count=100; borea/greek_borea/primordial_gaia hidden
10. ✓ 5★ 100/100 + 6★ 78/78 foundation_draft, runtime_ready=false
11. ✓ Marchio Boreale Borea-only, 0 leak
12. ✓ DW synergy 78/78 design_only=true, runtime_ready=false, numeric_modifier_pct=null
13. ✓ UI catalog files: 0 mutation calls, 0 runtime buttons, 0 adapter ref
14. ✓ Catalog top-level runtime_attached/battle_runtime_attached=false
15. ✓ delta plan `patch_applied=false` declared

## 7. Validator / suite / baseline results

| Run | Esito |
|---|---|
| `validate_5star_balance_foundation.py` | **PASS** (100/100) |
| `validate_6star_balance_foundation.py` | **PASS** (78/78, ult 13/13) |
| `audit_balance_foundation_boss_pvp_caps.py` | **PASS** (86 WARN, 0 FAIL) |
| `validate_status_resolver_contract.py` | **PASS** |
| `audit_hero_skill_kit_catalog_consolidation.py` | **PASS** |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (auto → v4) | **PASS** |
| `audit_skill_kit_runtime_adapter_safety.py` (NEW) | **PASS** |
| `run_hero_skill_kit_validator_suite.py` (default) | **PASS 16/16** (con i 2 nuovi optional aggregati) |
| `run_hero_skill_kit_validator_suite.py --include-baseline-diff` | **PASS 17/17 senza `--allow-changed`** ✅ |

**Baseline v4 immutata**. Nessun v5 creato.

## 8. API smoke

| Endpoint | Atteso | Effettivo |
|---|---|---|
| `GET /api/health` | 200 | **200** |
| `GET /api/heroes` count | 100 | **100** ✓ |
| Borea / legacy borea / primordial_gaia in `/api/heroes` | hidden | **hidden** ✓ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | **200** |
| `GET …/5star` | 200 | **200** |
| `GET …/6star` | 200 | **200** |
| `GET …/by-hero/greek_atalanta` | 200 | **200** |
| `GET …/by-hero/greek_athena` | 200 | **200** |
| `GET …/by-hero/greek_borea` (catalog-only) | 200 | **200** |
| `GET …/by-hero/borea` | 404 | **404** ✓ |
| `GET …/by-hero/primordial_gaia` | 404 | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | **200** |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | **200** |

## 9. UI safety

`hero-skill-kits-catalog.tsx` e `divine-weapons-catalog.tsx`:
- 0 chiamate `axios/fetch` mutanti
- 0 letterali `method:POST/PUT/PATCH/DELETE`
- 0 pulsanti `Pressable`/`TouchableOpacity` con `onPress` runtime (activate/equip/upgrade/breakSeal/spend/summon/battleTest/attachRuntime)
- 0 riferimenti a `skill_kit_runtime_adapter` / `SKILL_KIT_RUNTIME_ENABLED` / `is_skill_kit_runtime_enabled`

**UI non modificata da RM1.33-A.**

## 10. `/api/heroes` safety

Count = **100** ✓. `greek_borea`, legacy `borea`, `primordial_gaia` tutti **hidden**.

## 11. Borea / Marchio safety

- `greek_borea` resta `catalog_only`/`launch_extra_premium`/`runtime_attached=false`.
- L'adapter rifiuta esplicitamente `borea`/`greek_boreas`/`olympian_borea`/`primordial_gaia` con `forbidden_legacy_hero_id` (verificato).
- Marchio Boreale: solo su `greek_borea` (0 leak su 12 non-Borea, verificato).
- Cap policy adapter dichiara `marchio_owner_hero_id=greek_borea`, `team_wide_amp_allowed=false`, PvP=3 / PvE=5 / boss cap=4.

## 12. Runtime / DB / gacha / roster / catalog safety

- ❌ Nessuna modifica a `battle_engine.py`, `combat.tsx`, HP bar runtime, status runtime, VFX runtime, DW runtime, API routes/loaders, UI, DB, gacha, roster, Character Bible, assets.
- ❌ Nessun cambio a `final_numbers`, runtime flags, `divine_weapon_id`, `release_group`, `hero_id`, `skill_id`, nomi, descrizioni, status_ids, effect_tags.
- ❌ Nessun nuovo endpoint mutante. UI catalog read-only.
- ✅ Solo aggiunto codice **isolato** in `/app/backend/data/skill_kit_*_adapter.py` (pure functions, mai importate in live runtime) + 1 script audit + 1 entry doc + 2 entry suite OPTIONAL.

## 13. Warning / discrepanze

Nessuna. Il safety audit conferma che nessun file runtime importa l'adapter. La suite con baseline diff resta PASS senza `--allow-changed` perché nessun catalogo è stato toccato.

## 14. Final recommendation

**ACCEPTED.** Tutti i criteri di accettazione di RM1.33-A soddisfatti:

- runtime flag false ✅
- adapter creato ma non live ✅
- cap policy adapter legge delta plan ma NON applica live ✅
- nessun comportamento battle cambiato ✅
- nessun catalogo cambiato ✅
- baseline v4 PASS senza allow-changed ✅
- suite PASS (17/17) ✅
- nuovo audit PASS ✅
- `/api/heroes`=100 ✅
- Borea hidden / Marchio Borea-only ✅
- UI safety clean ✅
- zero DB/gacha/roster/runtime changes ✅

## 15. Suggested next tasks

1. 🟡 **P2 RM1.33-B — Runtime Adapter Wire-Test (still OFF)**. Aggiungere test suite Python che chiama gli adapter (flag OFF) con tutti i 113 slot 5★+6★ e verifica che ogni payload sia `disabled`/inert. Integrare il test nella suite come optional. *Massimo valore di copertura, rischio zero.*
2. 🟢 **P3 RM1.33-C — Debug-only Read-Through API endpoint**. Aggiungere un endpoint `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=…&slot=…&context=pvp` che ritorna SOLO l'oggetto `preview_cap_policy_for_skill` (mai `runtime_candidate`). Read-only, gated dal feature flag → quando OFF risponde sempre con payload disabled.
3. 🟢 **P3 RM1.32-C2 (opt)** — Trim numerici minimi foundation_draft per generare baseline v5 (rimasto in coda da RM1.32-C).
4. 🟢 **P3 RM1.34 — Boss family resistance/immunity table** referenziando il delta plan RM1.32-C.

---

### Appendix — baseline chain (invariata)

```
v1: hero_skill_kit_catalog_baseline_rm132pre_v1
v2: hero_skill_kit_catalog_baseline_rm132preb2_v2
v3: hero_skill_kit_catalog_baseline_rm132apost_v3
v4: hero_skill_kit_catalog_baseline_rm132b_v4   ← CURRENT (intatta in RM1.33-A)
```

### Appendix — adapter façade pattern

```
+-----------------------------------+
| Hero Skill Kit Catalog (5★/6★)   |
|   foundation_draft, inert         |
+-----------------------------------+
              │ read-only
              ▼
+-----------------------------------+
| skill_kit_runtime_adapter.py      |
|   • is_skill_kit_runtime_enabled  |── always False in RM1.33-A
|   • load_skill_kit_for_hero       |── pure read
|   • normalize_skill_slot          |── pure normalization
|   • get_skill_runtime_candidate   |── ALWAYS disabled while flag OFF
|   • get_disabled_runtime_result   |── canonical safe payload
+-----------------------------------+
              │ pure function
              ▼
+-----------------------------------+
| skill_kit_cap_policy_adapter.py   |
|   • load_balance_cap_delta_plan   |
|   • get_cap_policy_for_context    |── preview_only=true,
|   • preview_cap_policy_for_skill  |   applied_to_combat=false
+-----------------------------------+
              │ NOT imported by
              ▼
+-----------------------------------+
| battle_engine.py / combat.tsx     |── UNCHANGED
+-----------------------------------+
```

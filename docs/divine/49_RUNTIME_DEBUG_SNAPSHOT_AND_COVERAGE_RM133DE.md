# RM1.33-D/E — Debug Snapshot Contract + Coverage Endpoint (OFF)

**Task:** RM1.33-D + RM1.33-E (combined one-shot)
**Date (UTC):** 2026-05-15
**Mode:** GET-only, debug/read-only. Feature flag `SKILL_KIT_RUNTIME_ENABLED` **OFF**. **NO** mutation, **NO** runtime hookup, **NO** baseline change, **NO** UI change.

---

## 1. File creati (4)

| Path | Scopo |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kit_runtime_debug_snapshot_fixtures_v1.json` | Snapshot fixtures (7 casi canonici) |
| `/app/backend/scripts/validate_runtime_debug_snapshot_contract.py` | Validator contract snapshot (deep-subset) |
| `/app/backend/scripts/audit_skill_kit_runtime_debug_coverage_safety.py` | Safety audit endpoint coverage |
| `/app/docs/divine/49_RUNTIME_DEBUG_SNAPSHOT_AND_COVERAGE_RM133DE.md` | Questo checkpoint |

## 2. File modificati (2, narrow)

| Path | Cambio |
|---|---|
| `/app/backend/routes/skill_kit_runtime_debug.py` | Aggiunto secondo handler GET `/hero-skill-kits/runtime/debug/coverage` (read-only). Nessun cambio al preview esistente. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | 2 nuove entry OPTIONAL: `RM1.33-D validate_runtime_debug_snapshot_contract.py` + `RM1.33-E audit_skill_kit_runtime_debug_coverage_safety.py`. |

Nessun catalogo / runtime / battle_engine / combat / battle_core / HP-bar / VFX / status / DW runtime / UI / .env / baseline modificato.

## 3. Snapshot fixture summary

`hero_skill_kit_runtime_debug_snapshot_fixtures_v1.json` definisce 7 casi canonici (deep-subset, volatile fields ignorati):

| # | Case | request | expected |
|---|---|---|---|
| 1 | `valid_5star_pvp` | `greek_atalanta / skill_2 / pvp` | 200 + runtime_candidate disabled + cap pvp inert |
| 2 | `valid_6star_boss` | `greek_athena / ultimate / boss` | 200 + `is_true_ultimate=true` in preview meta + cap boss inert |
| 3 | `valid_borea_catalog_only` | `greek_borea / ultimate / pvp` | 200 + borea_preview (`no_activation=true`, `release_group=launch_extra_premium`, `not_visible_in_heroes=true`, `marchio_boreale_owner_only=true`) |
| 4 | `valid_healer_pve` | `norse_eir / skill_2 / pve` | 200 + runtime disabled + cap pve inert |
| 5 | `forbidden_legacy_borea` | `borea / ultimate / pvp` | 404 + `error=forbidden_legacy_hero_id`, `fallback_disabled=true` |
| 6 | `invalid_5star_ultimate` | `greek_atalanta / ultimate / pvp` | 404 + `error=invalid_slot`, `reason=invalid_slot_for_5star` |
| 7 | `invalid_context` | `greek_atalanta / skill_2 / garbage` | 400 + `error=invalid_context` |

Volatile fields esplicitamente esclusi: `generated_at_utc`, `safety_envelope.runtime_enabled`.

## 4. Snapshot validator results

`validate_runtime_debug_snapshot_contract.py` → **PASS** (7/7):

```
- valid_5star_pvp:           OK
- valid_6star_boss:          OK
- valid_borea_catalog_only:  OK
- valid_healer_pve:          OK
- forbidden_legacy_borea:    404 OK
- invalid_5star_ultimate:    404 OK
- invalid_context:           400 OK
```

L'algoritmo usa una funzione `_deep_subset_match` che valida solo i campi dichiarati nell'expected (response può avere campi extra), ignorando timestamp volatili. Contract stabile a prova di drift non-strutturali.

## 5. Coverage endpoint summary

- **Path**: `GET /api/hero-skill-kits/runtime/debug/coverage`
- **Metodo**: solo GET (route file ha 4 `@router.get` totali tra preview + coverage; **0** decorator POST/PUT/PATCH/DELETE)
- **Source**: legge `/app/data/design/hero_skill_kits/hero_skill_kit_runtime_adapter_wiretest_report_v1.json` (RM1.33-B); fallback a costanti dichiarate se assente
- **Anchor baseline**: legge `hero_skill_kit_catalog_baseline_rm132b_v4.json` per esporre l'identità del baseline corrente
- **Risposta**: oggetto JSON di sola lettura con safety envelope + coverage facts + warning

## 6. Coverage endpoint results

`GET /api/hero-skill-kits/runtime/debug/coverage` → **200**, payload osservato:

```
debug_only=true, read_only=true, method=GET,
runtime_enabled=false, feature_flag_name=SKILL_KIT_RUNTIME_ENABLED,
applied_to_combat=false, runtime_attached=false, battle_runtime_attached=false,
db_write=false, catalog_write=false, roster_write=false, gacha_write=false,
ui_runtime_control=false,
total_slots_expected=178, total_slots_tested=178,
normalized_slots=178, runtime_candidates_disabled=178,
per_rarity={5star: 100, 6star: 78},
6star_ultimate_is_true_ultimate_preserved=13,
5star_ultimate_safely_rejected_count=20,
feature_flag_default=false,
forbidden_aliases_rejected=true,
forbidden_aliases=[borea, primordial_gaia, greek_boreas, olympian_borea],
adapter_imported_by_battle_runtime=false,
cap_policy_preview_inert=true,
cap_policy_contexts_supported=[pvp, boss, pve],
borea_catalog_only=true, marchio_boreale_borea_only=true,
no_runtime_activation=true, no_db_write=true, no_catalog_change=true,
baseline_anchor=hero_skill_kit_catalog_baseline_rm132b_v4,
report_source=wiretest_report,
overall_result=PASS,
warning="Debug coverage only. Not used by battle runtime."
```

**Tutti i 22 campi richiesti dal contract sono presenti e correttamente valorizzati.**

## 7. Feature flag / runtime disabled summary

- `SKILL_KIT_RUNTIME_ENABLED` OFF; allowlist strict `"true_explicit_runtime_on"` mai impostata.
- Coverage endpoint, sample debug GET, wire-test (178/178) → `runtime_enabled=false` ovunque.
- Tutti i sample preview 200 → `runtime_candidate.enabled=false`, `runtime_candidate.reason="feature_flag_off"`, `is_disabled_runtime_result=true`, `payload=null`.
- Cap policy preview `pvp/boss/pve` → `enabled=false`, `applied_to_combat=false`, `runtime_attached=false`.

## 8. Forbidden alias / Borea safety

- 4/4 forbidden aliases (`borea`, `primordial_gaia`, `greek_boreas`, `olympian_borea`) → **404** con `error=forbidden_legacy_hero_id`, `fallback_disabled=true`. Nessun fallback a `greek_borea`.
- 5★ ultimate → **404** con `error=invalid_slot`, `reason=invalid_slot_for_5star`.
- `greek_borea` resta `catalog_only`, `release_group=launch_extra_premium`, `runtime_attached=false`. Coverage endpoint dichiara `borea_catalog_only=true`, `marchio_boreale_borea_only=true`. Marchio Boreale: 0 leak su 12 non-Borea (verificato dai validator a monte).

## 9. Validator / suite / baseline results

| Run | Esito |
|---|---|
| `validate_runtime_debug_snapshot_contract.py` (NEW) | **PASS** (7/7) |
| `audit_skill_kit_runtime_debug_coverage_safety.py` (NEW) | **PASS** (8/8 check) |
| `audit_skill_kit_runtime_debug_endpoint_safety.py` | **PASS** |
| `audit_skill_kit_runtime_adapter_wiretest.py` | **PASS** (178/178) |
| `audit_skill_kit_runtime_adapter_safety.py` | **PASS** |
| `validate_5star_balance_foundation.py` | **PASS** |
| `validate_6star_balance_foundation.py` | **PASS** |
| `audit_balance_foundation_boss_pvp_caps.py` | **PASS** (86 WARN, 0 FAIL) |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (auto → v4) | **PASS** |
| `validate_status_resolver_contract.py` | **PASS** |
| `validate_divine_weapon_catalog.py` | **PASS** |
| `audit_divine_weapon_crosslinks.py` | **PASS** |
| Suite default | **PASS 20/20** |
| Suite `--include-baseline-diff` | **PASS 21/21 senza `--allow-changed` sotto v4** ✅ |

**Baseline v4 invariata.**

## 10. API smoke

| Endpoint | Atteso | Effettivo |
|---|---|---|
| `GET /api/health` | 200 | **200** |
| `GET /api/heroes` count | 100 | **100** ✓ |
| Borea / legacy borea / primordial_gaia hidden | hidden | **hidden** ✓ |
| `GET /api/hero-skill-kits/catalogs/summary\|5star\|6star\|by-hero/{atalanta,athena,greek_borea}` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/by-hero/{borea, primordial_gaia}` | 404 | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary\|by-hero/greek_borea` | 200 | **200** |
| `GET /api/hero-skill-kits/runtime/debug/coverage` | 200 | **200** (178/178) ✓ |
| Debug preview 3 valid samples | 200 | **200** ✓ |
| Debug preview 2 forbidden/invalid_slot | 404 | **404** ✓ |
| Debug preview 2 missing/invalid params | 400 | **400** ✓ |

## 11. UI safety

| File | mutation | runtime button | debug/adapter ref |
|---|---|---|---|
| `/app/frontend/app/hero-skill-kits-catalog.tsx` | 0 | 0 | 0 |
| `/app/frontend/app/divine-weapons-catalog.tsx` | 0 | 0 | 0 |

UI non modificata.

## 12. `/api/heroes` safety

Count = **100** ✓. Borea, legacy borea, primordial_gaia **hidden**.

## 13. Runtime / DB / gacha / roster / catalog safety

- ❌ Nessuna modifica a `battle_engine.py`, `combat.tsx`, `battle_core.py`, HP bar / status / VFX / DW runtime, API esistenti, UI, DB, gacha, roster, Character Bible, assets, `final_numbers`, runtime flags, `divine_weapon_id`, `release_group`, hero_id, skill_id, nomi, descrizioni, status_ids, effect_tags, baseline files.
- ✅ Solo aggiunti: 1 fixture JSON, 1 validator, 1 audit, 1 endpoint GET-only nel route file esistente, 2 entry OPTIONAL nella suite, 1 doc.
- ✅ Route file ha 0 mutation decorator e 0 DB write patterns (verificato dall'audit).

## 14. Warning / discrepanze

Un piccolo aggiustamento alle fixture durante l'esecuzione one-shot: il campo `present: true` era dichiarato nel `normalized_skill_slot` atteso, ma `normalize_skill_slot()` non restituisce quella chiave (è nel risultato di `load_skill_kit_for_hero`). Fixture corretta rimuovendo `present: true` — nessun cambio al contract dei campi safety o di Borea. Validator e audit sono ora entrambi GREEN.

## 15. Final recommendation

**ACCEPTED.** Tutti i 22 criteri di accettazione di RM1.33-D/E soddisfatti:

1–4 Fixture / snapshot validator / coverage endpoint GET-only / coverage safety audit creati ✅
5–6 Snapshot validator PASS; coverage endpoint 178/178 ✅
7–8 runtime_enabled=false; runtime candidates disabled negli snapshot ✅
9–10 Forbidden aliases rejected; Borea catalog-only/no_activation ✅
11–14 No POST/PUT/PATCH/DELETE; no DB writes; no catalog mutation; no baseline change ✅
15 No battle runtime imports ✅
16–17 Suite PASS 21/21; baseline diff under v4 PASS ✅
18–19 API smoke PASS; UI safety PASS ✅
20–21 `/api/heroes`=100; Borea hidden ✅
22 Docs/checkpoint creato ✅

## 16. Suggested next tasks

1. 🟡 **P2 RM1.34 — Boss family resistance/immunity table** (raccomandato). Authoring read-only di una tabella `boss_family_resistance_table_v1.json` che usa il delta plan RM1.32-C come contratto di design (diminishing returns hard CC, DoT cap 0.5×, healing block max 2 turni, Marchio cap=4 sui boss, ecc.). Nessun runtime hookup. Massimo valore design.
2. 🟢 **P3 RM1.32-C2 (opt)** — Trim numerici minimi foundation_draft per generare baseline v5 (rimasto in coda).
3. 🟢 **P3 RM1.33-F (opt)** — Aggiungere un secondo snapshot fixture set `…_v2.json` per i 13 6★ ultimate (1 caso per ogni hero), e validare in CI che la SHA dei payload preview resti stabile. Estende il contract a un sub-set rappresentativo dell'intero catalogo.

---

### Appendix — baseline chain (invariata)

```
v1 → v2 → v3 → v4 (CURRENT, intatta in RM1.33-D/E)
```

### Appendix — debug endpoints map

```
GET /api/hero-skill-kits/runtime/debug/preview?hero_id=…&slot=…&context=pvp|boss|pve
    → 200 normalized + cap policy + runtime_candidate disabled + safety_envelope
    → 400 missing/invalid params
    → 404 forbidden_legacy_hero_id | hero_not_in_catalog | invalid_slot

GET /api/hero-skill-kits/runtime/debug/coverage
    → 200 wire-test snapshot 178/178 + safety envelope + warning
```

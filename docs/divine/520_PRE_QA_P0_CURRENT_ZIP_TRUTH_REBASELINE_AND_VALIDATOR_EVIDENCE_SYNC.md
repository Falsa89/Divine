# Pack PRE_QA_P0 — Current ZIP Truth Rebaseline & Validator Evidence Sync — Final Report

> **Codice pack:** `PRE_QA_P0_CURRENT_ZIP_TRUTH_REBASELINE_AND_VALIDATOR_EVIDENCE_SYNC`
> **Tipo:** P0 di **verità / rebaseline**, NON un feature pack.
> **Scope:** Riallineamento di MD5 baseline, validator status, supersedence
> dei report storici, snapshot guardrail pubblico.
> **No-touch:** DB, backend runtime, battle_engine, combat runtime,
> economia, gacha, shop, VIP, Battle Pass, IAP, reward grant,
> Character Bible, asset, roster, skill kits, env flag.

## 1. Truth Rebaseline Verdict

**`PRE_QA_P0_CURRENT_ZIP_TRUTH_REBASELINE_AND_VALIDATOR_EVIDENCE_SYNC_COMPLETE`**

Tutti i 15 MD5 dichiarati nello snapshot canonico corrispondono ai MD5 reali
calcolati al momento dell'audit. Il vecchio MD5 di `battle_engine.py`
`151ca35ad3bc35f0a6209cb3744ed440` è marcato **SUPERSEDED/HISTORICAL**:
non è più la **current invariant**; la **current invariant** è
`8b7f55d4f58605138daa8bbace23f514`. Tutti i flag invarianti di
no-runtime-change / no-DB-write / no-live-unlock / no-reward-live sono
`false` come da contratto P0.

## 2. Current MD5 Snapshot

Sorgente di verità canonica:
`data/design/current_truth/current_code_md5_snapshot_v1.json`.

| File | Current MD5 |
| --- | --- |
| `backend/battle_engine.py` | `8b7f55d4f58605138daa8bbace23f514` |
| `backend/battle_core.py` | `80d94afba9eb2930e63b06cfed645b77` |
| `backend/server.py` | `ab011b0b3e788d48f13dd389aeb2033d` |
| `backend/game_systems.py` | `1a27bbcb26e353c783757081e8c657dd` |
| `frontend/app/combat.tsx` | `8ec731cabd965fdd542ed47840c09740` |
| `frontend/app/pre-battle-lobby.tsx` | `fef34e1eff31b7f30238dca6c7dd9e07` |
| `frontend/app/story.tsx` | `6325888d2efaf7176255a38b5d505519` |
| `frontend/app/(tabs)/menu.tsx` | `89e2f641e21cba537741d9749767dce6` |
| `frontend/src/utils/preQaNavGuard.ts` | `430f9bc72048a4138532634cc9373d15` |
| `frontend/app/(tabs)/gacha.tsx` | `6a28ad5338b6bdd776f4f794100657b2` |
| `frontend/app/shop.tsx` | `1fc3dde180993b878b3e881d6fa41970` |
| `frontend/app/item-shop.tsx` | `8af80875fa68a7a9f939acf526cba0ee` |
| `frontend/app/vip.tsx` | `a91485ac6863118544a2d5c075ed107f` |
| `frontend/app/battlepass.tsx` | `da23bff32388375106236392cd94cdd4` |
| `frontend/app/soul-forge.tsx` | `a36818389c6c1d0bf72114d6d4ef942b` |

I 15 MD5 reali sono stati verificati 1:1 con i MD5 forniti dall'audit
esterno ChatGPT sullo ZIP corrente.

## 3. Stale MD5 / Historical Report Policy

Sorgente: `data/design/current_truth/stale_md5_reference_inventory_v1.json`.

| Categoria | Count |
| --- | --- |
| `docs/divine/*.md` (storici) | 65 |
| `data/design/**.json` (storici) | 98 |
| `backend/scripts/validate_*.py` (con MD5 stale come baseline) | 93 |
| `backend/battle_engine.py` (commento storico self-referenced) | 1 |
| **Totale riferimenti al MD5 stale** | **257** |

Policy formale:

- **NON cancelliamo** docs storici (`docs/divine`, `data/design`).
- **NON riscriviamo** report storici per cambiarne il significato.
- I report storici **NON sono prova current-state**.
- I validator legacy con MD5 stale come `current_invariant` sono marcati
  `MARK_SUPERSEDED_HISTORICAL` o `UPDATE_BASELINE` nella matrix di
  affidabilità (vedi §4); restano nel filesystem come audit trail ma
  non vanno usati come prova current-state finché non riallineati.
- Il file `backend/battle_engine.py` contiene un singolo commento storico
  alla riga ~1455 che cita il vecchio MD5 come annotazione interna;
  questo è legittimo e non viene toccato (no runtime change).

## 4. Validator Reliability Matrix

Sorgente: `data/design/current_truth/validator_truth_status_matrix_v1.json`.

### 4.1 Current-state truth source (USE these as proof)

| Validator | Status | Action |
| --- | --- | --- |
| `validate_pre_qa_pack_119c_menu_public_snapshot.py` | PASS | KEEP_CURRENT |
| `validate_pre_qa_pack_119d_public_menu_route_health.py` | PASS | KEEP_CURRENT |
| `validate_pre_qa_pack_120a_controlled_unlock_prep.py` | PASS | KEEP_CURRENT |
| `validate_pre_qa_acceleration_120b_safe_playable_vertical_slice_combo.py` | PASS | KEEP_CURRENT |
| `validate_v89_home_battle_flow_audit.py` | PASS | KEEP_CURRENT |
| `validate_v89_no_asset_final_import_no_character_bible.py` | PASS | KEEP_CURRENT |
| `validate_v89_real_battlefield_tsx.py` | PASS | KEEP_CURRENT |
| `validate_mega_release_acceleration_38_v89_rollup.py` | PASS | KEEP_CURRENT |
| `validate_current_zip_truth_rebaseline_v1.py` (NEW) | PASS | KEEP_CURRENT |
| `validate_validator_path_relocatability_audit_v1.py` (NEW) | PASS | KEEP_CURRENT |
| `validate_stale_md5_supersedence_audit_v1.py` (NEW) | PASS | KEEP_CURRENT |
| `validate_current_public_guardrail_snapshot_v1.py` (NEW) | PASS | KEEP_CURRENT |

### 4.2 Warning (hygiene drift, not P0)

| Validator | Status | Note |
| --- | --- | --- |
| `run_player_route_static_audit.py` | WARN | `servers.tsx: missing lock marker matching _LOCKED_V2 / legacy / preview`. Hygiene drift, non runtime leak. |

### 4.3 Current-unsafe (NON usare come prova current-state)

| Validator | Status | Action |
| --- | --- | --- |
| `validate_beta_testing_track_a_baseline_v1.py` | FAIL | UPDATE_BASELINE |
| `validate_beta_testing_track_c_soul_forge_regression_v1.py` | FAIL | UPDATE_BASELINE |
| `validate_beta_testing_track_g_reporting_v1.py` | FAIL | MAKE_RELOCATABLE |
| `validate_beta_testing_track_i_completion_v1.py` | FAIL | MAKE_RELOCATABLE |
| `validate_project_full_runtime_feature_reality_audit_v1.py` | FAIL | MARK_SUPERSEDED_HISTORICAL |
| `validate_beta_testing_track_f_redis_v1.py` | FAIL | SPLIT_ENVIRONMENTAL_CHECK (Redis non garantito nel container) |

Audit relocatability completo (eseguito da `validate_validator_path_relocatability_audit_v1.py`):

- Validator totali scansionati: **1972**
- Relocatable (no `/app/` literal nel codice): **1318**
- Hardcoded `/app/` literal nel codice: **654**
- Current-state-truth validators con `/app/` literal: **0**

Nessun REQUIRED validator viene indebolito o rimosso. Nessun fake PASS.

## 5. Public Guardrail Snapshot

Sorgente: `data/design/current_truth/public_guardrail_current_snapshot_v1.json`.

Riesecuzione logica di 119C/119D/120A/120B sullo stato corrente:

| Metrica | Valore |
| --- | --- |
| Categorie pubbliche visibili | **6** |
| Voci pubbliche visibili | **22** |
| `safe_read_only` | 1 |
| `safe_preview_only` | 0 |
| `locked_deferred` | 3 |
| `mutation_sensitive_but_gated` | 18 |
| `unsafe_exposed` | **0** |
| `unknown_needs_review` | **0** |
| `leaked_blocked_routes` | **0** |
| Tier 0 / 1 / 2 / 3 | 1 / 5 / 11 / 5 |
| Hard blockers (Tier 4) | 13 |
| Battle preview modes | 5 (story / tower / arena / training / boss) |

Vincoli runtime ancora attivi:

- `pre-battle-lobby.tsx` contiene `is_preview`, `reward_policy`, `preview`,
  `blocked_no_team_for_server`, `battle_engine_mode`. ✅
- `combat.tsx` contiene `PREVIEW_REWARD_LOCK_ACTIVE`,
  `PREVIEW_NON_AUTHORITATIVE`. ✅
- `/shop`, `/vip`, `/battlepass`, `/gacha`, `/pvp`, `/guild`, `/gvg`,
  `/raid`, `/territory`, `/plaza`, `/dm`, `/events`, `/mail`, `/friends`,
  `/playable-mode-battle-preview`, `/skill-status-vfx-catalogs`,
  `/hero-skill-kits-catalog`, `/safe-previews` → tutti **bloccati**, mai
  esposti nel menu pubblico. ✅
- reward / EXP / progress / DB write / ranking / authoritative battle
  commit → **disabled by guard**. ✅

## 6. Next Macro-Pack Readiness

Sorgente: `data/design/current_truth/next_macro_pack_readiness_v1.json`.

| Campo | Valore |
| --- | --- |
| Candidato prossimo macro-pack | `PRE_QA_VERTICAL_SLICE_RUNTIME_DEVICE_QA_AND_NO_WRITE_PLAYTEST_PACK` |
| Ready to proceed | **true** |
| Vincoli da rispettare | no-write, no-reward, no-live, riusare i 4 validator current-state-truth come gate di non regressione |

Blockers residui (documentati, non bloccano lo step successivo):

| ID | Severity | Blocks next macro-pack | Blocks full release |
| --- | --- | --- | --- |
| `BLOCKER_DEVICE_QA_RUN` | P1 | no | yes |
| `BLOCKER_ROUTE_VISUAL_SMOKE` | P2 | no | no |
| `BLOCKER_PLAYWRIGHT_EXECUTION` | P2 | no | no |
| `BLOCKER_ASSET_AUDIO_PLACEHOLDER_REGISTRY` | P2 | no | no |
| `BLOCKER_REWARD_PROGRESS_LOCKED` | INVARIANT | no | yes (resta locked by design) |
| `BLOCKER_STALE_BASELINE_VALIDATORS` | P1 | no | no |
| `BLOCKER_HARDCODED_APP_PATH_AUDIT` | P2 | no | no |

## 7. File creati / modificati

```text
data/design/current_truth/current_code_md5_snapshot_v1.json
data/design/current_truth/stale_md5_reference_inventory_v1.json
data/design/current_truth/validator_truth_status_matrix_v1.json
data/design/current_truth/public_guardrail_current_snapshot_v1.json
data/design/current_truth/rebaseline_decision_record_v1.json
data/design/current_truth/next_macro_pack_readiness_v1.json
backend/scripts/validate_current_zip_truth_rebaseline_v1.py
backend/scripts/validate_validator_path_relocatability_audit_v1.py
backend/scripts/validate_stale_md5_supersedence_audit_v1.py
backend/scripts/validate_current_public_guardrail_snapshot_v1.py
backend/reports/current_zip_truth_rebaseline_latest.json (autogen)
docs/divine/520_PRE_QA_P0_CURRENT_ZIP_TRUTH_REBASELINE_AND_VALIDATOR_EVIDENCE_SYNC.md (questo file)
backend/scripts/run_hero_skill_kit_validator_suite.py (solo registrazione di 4 OPTIONAL tuples, nessun REQUIRED toccato)
```

**Nessun file runtime proibito modificato**:
`backend/battle_engine.py`, `backend/battle_core.py`, `backend/server.py`,
`backend/game_systems.py`, `frontend/app/combat.tsx`,
`frontend/app/pre-battle-lobby.tsx`, `frontend/app/story.tsx`,
`frontend/app/(tabs)/menu.tsx`, `frontend/src/utils/preQaNavGuard.ts`,
`frontend/app/(tabs)/gacha.tsx`, `frontend/app/shop.tsx`,
`frontend/app/item-shop.tsx`, `frontend/app/vip.tsx`,
`frontend/app/battlepass.tsx`, `frontend/app/soul-forge.tsx`,
Character Bible, roster/heroes, skill kits, asset, audio, env, supervisor,
DB scripts, migrations, reward/gacha/shop/VIP/BP/IAP runtime.

## 8. Suite Runner Registration (OPTIONAL tier, no REQUIRED weakening)

In `backend/scripts/run_hero_skill_kit_validator_suite.py` sono stati
**aggiunti 4 tuples nella lista OPTIONAL** (mai REQUIRED):

```python
('PRE-QA-P0-CURRENT-ZIP-TRUTH-REBASELINE',
 'validate_current_zip_truth_rebaseline_v1.py'),
('PRE-QA-P0-VALIDATOR-PATH-RELOCATABILITY-AUDIT',
 'validate_validator_path_relocatability_audit_v1.py'),
('PRE-QA-P0-STALE-MD5-SUPERSEDENCE-AUDIT',
 'validate_stale_md5_supersedence_audit_v1.py'),
('PRE-QA-P0-CURRENT-PUBLIC-GUARDRAIL-SNAPSHOT',
 'validate_current_public_guardrail_snapshot_v1.py'),
```

- Tuple count = 1 per ciascuno (nessun duplicato).
- Tier = **OPTIONAL** (never REQUIRED).
- Nessun REQUIRED entry toccato, rimosso o indebolito.
- Nessun validator esistente modificato.

## 9. Validator Result (eseguiti localmente in questo container)

```text
$ python3 backend/scripts/validate_current_zip_truth_rebaseline_v1.py
[v_p0_truth_rebaseline] OK files_verified=15
  battle_engine_md5=8b7f55d4f58605138daa8bbace23f514
  old_md5_marked_superseded=true runtime_changed=false
  db_write=false live_unlock=false

$ python3 backend/scripts/validate_validator_path_relocatability_audit_v1.py
[v_p0_relocatability_audit] OK current_state_truth_clean=True
  hardcoded_count=654 relocatable_count=1318

$ python3 backend/scripts/validate_stale_md5_supersedence_audit_v1.py
[v_p0_stale_md5_supersedence] OK no_fake_pass=true
  no_doc_deletion=true truth_snapshot_safe=true

$ python3 backend/scripts/validate_current_public_guardrail_snapshot_v1.py
[v_p0_current_public_guardrail_snapshot] OK unsafe_exposed=0
  unknown=0 leaked=0 no_unlock_applied=true
```

## 10. Safety Suite (regression)

```text
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK ...
[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK ...
[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP] OK ...
[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO] OK ...
```

## 11. Repo Hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

## 12. Conferma no-touch (zero runtime / gameplay / DB / live changes)

| Vincolo | Stato |
| --- | --- |
| Runtime changed by this pack | ✅ NO |
| Gameplay changed by this pack | ✅ NO |
| DB write performed | ✅ NO |
| Live unlock performed | ✅ NO |
| Reward live opened | ✅ NO |
| Gacha live opened | ✅ NO |
| Shop live opened | ✅ NO |
| VIP live opened | ✅ NO |
| Battle Pass live opened | ✅ NO |
| IAP opened | ✅ NO |
| Battle result commit opened | ✅ NO |
| EXP/progress commit opened | ✅ NO |
| Ranking live opened | ✅ NO |
| Character Bible changed | ✅ NO |
| Asset changed | ✅ NO |
| Env flag changed | ✅ NO |
| REQUIRED validator weakened | ✅ NO |
| REQUIRED validator removed | ✅ NO |
| Historical docs deleted | ✅ NO |
| Historical docs meaning changed | ✅ NO |

## 13. Honesty Statement

- **119C / 119D / 120A / 120B / v89** restano utili come **evidence** del
  current state.
- I **report con MD5 stale** non sono prova current-state: sono storici e
  vengono conservati come audit trail.
- I 5 validator beta-tracks-* + project_full_runtime_feature_reality_audit
  sono **NON affidabili** finché non riallineati (UPDATE_BASELINE) o
  marcati SUPERSEDED. Il P0 li **documenta**, non li sblocca.
- **Nessuna dichiarazione di "release ready" o "100% completo"** è
  contenuta in questo pack.
- **Nessun fake PASS**. Tutti i validator P0 producono evidence o falliscono
  in modo esplicito.

## 14. Commit SHA

Verrà aggiornato dopo `git commit`.

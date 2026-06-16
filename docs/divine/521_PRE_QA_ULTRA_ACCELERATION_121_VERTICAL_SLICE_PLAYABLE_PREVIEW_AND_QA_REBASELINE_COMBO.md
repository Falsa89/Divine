# Pack 121 — PRE_QA Ultra Acceleration — Vertical Slice Playable Preview & QA Rebaseline Combo

> **Codice pack:** `PRE_QA_ULTRA_ACCELERATION_121_VERTICAL_SLICE_PLAYABLE_PREVIEW_AND_QA_REBASELINE_COMBO`
> **Tipo:** Ultra-combo (Track A/B/C/D/E/F/G/H) — vertical slice preview
> testabile + route cleanup safe + no-write invariant validation +
> device QA manifest + current-unsafe validator triage + report unico.
> **Stato finale:** `PRE_QA_VERTICAL_SLICE_PLAYABLE_PREVIEW_READY_FOR_DEVICE_QA`.
> **NON dichiara:** release ready, gioco completo, reward live, gacha
> live, shop live, VIP/BP/IAP live.

## 1. Verdict

**`PRE_QA_ULTRA_ACCELERATION_121_VERTICAL_SLICE_READY_WITH_DEFERRED_VALIDATOR_REBASELINE_ITEMS`**

Tutti i nuovi validator 121 PASS. Tutti i regression gate PASS. Il triage
dei validator current-unsafe è completato in modo onesto: 1 marcato
SUPERSEDED_HISTORICAL (project_full_runtime_feature_reality_audit), 1
SPLIT_ENVIRONMENTAL_CHECK (beta-track-f Redis), 4 DEFER_TO_DEDICATED_PACK
(beta-track A/C/G/I). Nessun fake PASS introdotto, nessun REQUIRED
validator toccato.

Stato vertical slice playable preview: **READY_FOR_DEVICE_QA**.

## 2. Scope

- **Track A:** Playable preview flow matrix (5 mode).
- **Track B:** Public route reachability/copy matrix (22 voci pubbliche).
- **Track C:** No-write invariant hard scan validator.
- **Track D:** Route flow validator (5 deeplink lobby + back nav).
- **Track E:** Device QA manifest + checklist 23 step.
- **Track F:** Current-unsafe validator triage (6 entry).
- **Track G:** Questo report finale.
- **Track H:** Suite runner registrazione 5 OPTIONAL tuples (no REQUIRED
  touched).

Nessun unlock live. Nessun runtime change ai file forbidden. Nessun env
flag toccato.

## 3. Truth sources usate

- `data/design/current_truth/current_code_md5_snapshot_v1.json` (P0)
- `data/design/current_truth/validator_truth_status_matrix_v1.json` (P0)
- `data/design/current_truth/public_guardrail_current_snapshot_v1.json` (P0)
- `data/design/current_truth/rebaseline_decision_record_v1.json` (P0)
- `data/design/current_truth/stale_md5_reference_inventory_v1.json` (P0)
- `backend/reports/pre_qa_pack_119d_public_menu_route_health_latest.json`
- `backend/reports/pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json`

## 4. Files created (this pack)

```text
data/design/vertical_slice_qa/ultra_121_playable_preview_flow_matrix_v1.json
data/design/vertical_slice_qa/ultra_121_player_route_reachability_and_copy_matrix_v1.json
data/design/vertical_slice_qa/ultra_121_device_qa_manifest_v1.json
data/design/current_truth/ultra_121_current_unsafe_validator_triage_v1.json
backend/scripts/validate_pre_qa_ultra_121_no_write_invariants.py
backend/scripts/validate_pre_qa_ultra_121_route_flow.py
backend/scripts/validate_pre_qa_ultra_121_device_qa_manifest.py
backend/scripts/validate_pre_qa_ultra_121_report_completeness.py
backend/scripts/validate_pre_qa_ultra_121_current_unsafe_validator_triage.py
backend/reports/vertical_slice_qa/ultra_121_no_write_invariants_latest.json (autogen)
backend/reports/vertical_slice_qa/ultra_121_route_flow_latest.json (autogen)
backend/reports/vertical_slice_qa/ultra_121_device_qa_manifest_latest.json (autogen)
backend/reports/vertical_slice_qa/ultra_121_current_unsafe_validator_triage_latest.json (autogen)
docs/divine/521_PRE_QA_ULTRA_ACCELERATION_121_VERTICAL_SLICE_PLAYABLE_PREVIEW_AND_QA_REBASELINE_COMBO.md (questo file)
backend/scripts/run_hero_skill_kit_validator_suite.py (solo registrazione 5 OPTIONAL tuples)
```

**Nessun file runtime forbidden modificato.**

## 5. Playable preview flow matrix (Track A)

Sorgente: `data/design/vertical_slice_qa/ultra_121_playable_preview_flow_matrix_v1.json`.

| Mode | Entry route | Expected lobby | Combat preview | Reward policy | Progress policy | battle_engine_mode |
| --- | --- | --- | --- | --- | --- | --- |
| story | `/story` | `/pre-battle-lobby?mode=story` | `/combat` (preview) | preview | preview | preview |
| tower | `/tower-of-the-hells` | `/pre-battle-lobby?mode=tower` | `/combat` (preview) | preview | preview | preview |
| training | `/hero-training` | `/pre-battle-lobby?mode=training` | `/combat` (preview) | preview | preview | preview |
| arena | `/pre-battle-lobby?mode=arena` | `/pre-battle-lobby?mode=arena` | `/combat` (preview, no MM live) | preview | preview | preview |
| boss | `/pre-battle-lobby?mode=boss` | `/pre-battle-lobby?mode=boss` | `/combat` (preview boss) | preview | preview | preview |

Tutti i mode dichiarano `preview_only=true`, `no_write=true`,
`expected_missing_team_behavior = blocked_no_team_for_server`,
`expected_missing_encounter_behavior = deterministic_local_payload`.

## 6. Public route reachability / copy matrix (Track B)

Sorgente: `data/design/vertical_slice_qa/ultra_121_player_route_reachability_and_copy_matrix_v1.json`.

| Classificazione | Count |
| --- | --- |
| `reachable_visual` | 1 (`/rankings`) |
| `preview_only` | 7 (catalog/preview + 5 lobby mode) |
| `locked_deferred` | 3 (`/hero-collection`, `/artifacts-preview`, `/guide`) |
| `mutation_sensitive_but_gated` | 11 |
| `blocked_hidden` | 18 (shop/gacha/VIP/BP + dev catalog/wireframe) |
| `needs_device_qa` | 22 |

Invarianti verificati:

- ✅ Nessuna route pubblica con import mancante evidente.
- ✅ Nessuna route live-blocked esposta nel menu pubblico.
- ✅ Nessuna label tecnica QA/dev nel menu pubblico.
- ✅ Locked/deferred hanno copy comprensibile.
- ✅ Shop/Gacha/VIP/BP/IAP non accessibili pubblicamente.

**Known non-blocking warning**: `WARN_SERVERS_LOCK_MARKER_DRIFT` — il
route static audit segnala che `servers.tsx` non match il pattern token
`_LOCKED_V2 / legacy / preview`. Il file contiene già `locked`,
`disabled`, `fallback`, `deferred` come termini interni; il pattern
specifico atteso era di un pack precedente. Severità P3, **non blocca**
il pack 121 né il device QA. Documentato per pack hygiene futuro.
**Nessuna modifica runtime applicata** a `servers.tsx`.

## 7. No-write invariant evidence (Track C)

Validator: `validate_pre_qa_ultra_121_no_write_invariants.py` → **PASS**.

```text
[v121_no_write_invariants] PASS
  pb_tokens_ok=true combat_tokens_ok=true
  story/tower/training_no_sensitive_endpoints=true
```

Verificato:

- `pre-battle-lobby.tsx` contiene **tutti** i 4 marker richiesti:
  `is_preview`, `reward_policy`, `progress_policy`, `battle_engine_mode`.
- `combat.tsx` contiene **PREVIEW_REWARD_LOCK_ACTIVE** +
  `PREVIEW_NON_AUTHORITATIVE`.
- `story.tsx`, `tower-of-the-hells.tsx`, `hero-training.tsx`: **nessun**
  endpoint sensibile (reward/claim/grant/commit/gacha/shop/vip/battlepass/iap)
  nel codice eseguibile (commenti stripped).
- `preQaNavGuard.ts` blocca `/shop`, `/vip`, `/battlepass`, `/gacha`.
- `menu.tsx` non ha env flag hardcoded a `true` per legacy-unsafe.

## 8. Route flow evidence (Track D)

Validator: `validate_pre_qa_ultra_121_route_flow.py` → **PASS**.

```text
[v121_route_flow] PASS
  modes_covered=5 pb_handles_all_5_modes=true
  no_dev_route_in_back_nav=true
```

Verificato:

- File target `pre-battle-lobby.tsx`, `story.tsx`, `tower-of-the-hells.tsx`,
  `hero-training.tsx` tutti presenti.
- `pre-battle-lobby.tsx` contiene i 5 mode (`story`, `tower`, `training`,
  `arena`, `boss`).
- Nessuna `router.push/replace/navigate` punta a route dev/QA bloccate
  (`/playable-mode-battle-preview`, `/skill-status-vfx-catalogs`,
  `/hero-skill-kits-catalog`, `/safe-previews`, `/dev`, `/qa`).
- Auto-resolve in `story.tsx`: trovate 2 occorrenze entrambe in contesto
  `qa-autoresolve nascosto dal player-facing` e
  `qa-autoresolve gated (non più unico percorso giocabile)` →
  considerate gated e tollerate (env-flag `EXPO_PUBLIC_SHOW_QA_*` OFF
  by default).

## 9. Device QA manifest (Track E)

Validator: `validate_pre_qa_ultra_121_device_qa_manifest.py` → **PASS**.

```text
[v121_device_qa_manifest] PASS
  checklist_steps=23 all_5_modes_present=true scope_invariants_ok=true
```

Sorgente:
`data/design/vertical_slice_qa/ultra_121_device_qa_manifest_v1.json`.

23 step checklist coprono:

1–5: Avvio app, Home, Menu, 22 voci, no label QA.
6–9: Story (hub + lobby + combat preview + back nav).
10–11: Tower (lobby + combat preview).
12–13: Training (lobby + combat preview).
14–15: Arena (lobby + combat preview, no MM live).
16–17: Boss/Raid (lobby + combat preview, no drop live).
18: Banner/copy preview.
19: Verifica shop/gacha/VIP/BP non pubblicamente accessibili.
20: Locked/deferred screens comprensibili.
21: Back navigation globale.
22: Assenza crash.
23: Reward/EXP/progress immutati post-test.

Scope invariants: `no_purchase_test=true`,
`no_claim_reward_test=true`, `no_env_flag_override=true`,
`no_dev_qa_hidden_route_use=true`.

## 10. Current-unsafe validator triage (Track F)

Validator: `validate_pre_qa_ultra_121_current_unsafe_validator_triage.py` → **PASS**.

```text
[v121_unsafe_validator_triage] PASS
  unsafe_covered=6/6 decision_enum_ok=true honesty_ok=true
```

Sorgente:
`data/design/current_truth/ultra_121_current_unsafe_validator_triage_v1.json`.

| Validator | Decision 121 | Rationale |
| --- | --- | --- |
| `validate_beta_testing_track_a_baseline_v1.py` | DEFER_TO_DEDICATED_PACK | MD5 baseline stale di `battle_engine.py`. Aggiornare ora richiede pack dedicato per evitare fake PASS. |
| `validate_beta_testing_track_c_soul_forge_regression_v1.py` | DEFER_TO_DEDICATED_PACK | Stesso ragionamento di track A. |
| `validate_beta_testing_track_f_redis_v1.py` | SPLIT_ENVIRONMENTAL_CHECK | Dipendenza Redis → splittare in statico + smoke_runtime. |
| `validate_beta_testing_track_g_reporting_v1.py` | DEFER_TO_DEDICATED_PACK | MAKE_RELOCATABLE + UPDATE_BASELINE richiede pack dedicato. |
| `validate_beta_testing_track_i_completion_v1.py` | DEFER_TO_DEDICATED_PACK | Stesso ragionamento di track G. |
| `validate_project_full_runtime_feature_reality_audit_v1.py` | MARK_SUPERSEDED_HISTORICAL | Già coperto dalla validator_truth_status_matrix del P0. |

**Honesty statement**:
- `runtime_changes_introduced_by_triage = 0`
- `fake_pass_introduced = 0`
- `required_validator_weakened = 0`
- `historical_doc_deleted = 0`
- `deferred_count = 4` (esplicitamente documentati)

## 11. Validator results (this pack)

```text
[v121_no_write_invariants]            PASS
[v121_route_flow]                     PASS
[v121_device_qa_manifest]             PASS
[v121_unsafe_validator_triage]        PASS
[v121_report_completeness]            PASS (questo report)
```

## 12. Regression gate results

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT]            OK categories=6 items=22
[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH]        OK unsafe=0 unknown=0 leaked=0
[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP]          OK candidates=22 gates=6 blockers=13
[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO]            OK candidates=22 t01=6 t2=11 t3=5
[v_p0_truth_rebaseline]                             OK files_verified=15
[v_p0_current_public_guardrail_snapshot]            OK unsafe=0 unknown=0 leaked=0
[v_p0_stale_md5_supersedence]                       OK no_fake_pass no_doc_deletion
[v_p0_relocatability_audit]                         OK current_state_truth_clean=True

PRE-QA Safety Suite: 24/24 PASS  →  verdict: PRE_QA_SAFETY_SUITE_PASS
```

## 13. Repo hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

## 14. No-touch confirmation

| Vincolo | Stato |
| --- | --- |
| `backend/battle_engine.py` modificato | ✅ NO |
| `backend/battle_core.py` modificato | ✅ NO |
| `backend/server.py` modificato | ✅ NO |
| `backend/game_systems.py` modificato | ✅ NO |
| reward claim live routes | ✅ NO |
| gacha runtime | ✅ NO |
| shop runtime | ✅ NO |
| VIP runtime | ✅ NO |
| Battle Pass runtime | ✅ NO |
| IAP runtime | ✅ NO |
| mail claim runtime | ✅ NO |
| guild/PvP/raid live reward | ✅ NO |
| DB scripts apply | ✅ NO |
| migrations | ✅ NO |
| `.env` | ✅ NO |
| supervisor | ✅ NO |
| Character Bible | ✅ NO |
| roster/heroes master | ✅ NO |
| skill kits / final_numbers | ✅ NO |
| asset/audio | ✅ NO |
| premium currency logic | ✅ NO |
| account reset | ✅ NO |
| authoritative battle result commit | ✅ NO |
| EXP/progress commit | ✅ NO |
| menu.tsx / preQaNavGuard.ts | ✅ NO |
| pre-battle-lobby.tsx | ✅ NO |
| combat.tsx | ✅ NO |
| story.tsx / tower-of-the-hells.tsx / hero-training.tsx | ✅ NO |
| env flag attivata | ✅ NO |
| REQUIRED validator indebolito/rimosso | ✅ NO |
| docs storici cancellati | ✅ NO |

## 15. What remains blocked

- **Reward live / EXP / progress / ranking commit**: bloccati by design.
- **Gacha / Shop / VIP / Battle Pass / IAP**: bloccati pubblicamente; non
  esposti nel menu.
- **Mail claim live / Guild live / Raid reward live**: hard blocker (Tier 4).
- **5 validator beta-track A/C/G/I + project_full_runtime_feature_reality_audit**:
  current-unsafe (MD5 baseline stale / hardcoded `/app/` / env-dependent).
  Triage 121 dichiara DEFER/SUPERSEDE/SPLIT. **Non sono blocker** per
  device QA né per pack successivo non-live.
- **Hygiene warning `WARN_SERVERS_LOCK_MARKER_DRIFT`**: P3, non blocca.
- **Placeholder asset/audio registry**: out-of-scope, non blocca device QA.

## 16. Next recommended macro-pack

`PRE_QA_VERTICAL_SLICE_DEVICE_QA_RUN_AND_EVIDENCE_PACK`

Scope proposto:

- Esecuzione **reale** della checklist 23 step su iOS/Android (no-write).
- Capture screenshot per ogni step.
- Eventuale Playwright contro preview URL stabile.
- Report con evidence + eventuali blocker visivi.
- **Nessun unlock live**, **nessun reward**, **nessun DB write**.

Pack successivi a quello (per ordine logico, ognuno dedicato):

1. Beta-track validator rebaseline (UPDATE_BASELINE per A, C; MAKE_RELOCATABLE
   per G, I; SPLIT per F-Redis).
2. Hygiene marker pass per `servers.tsx` lock pattern.
3. Placeholder asset/audio registry (out-of-scope qui).
4. Tier 4 individual unlock design pack (uno alla volta, flag-gated + kill-switch).

## 17. Honesty Statement

- **Nessuna dichiarazione di "release ready" o "100% completo"**.
- **Nessun reward live / gacha live / shop live / VIP live / BP live / IAP
  pronto**.
- I validator 121 producono **evidence reale**, non fake PASS.
- Le 4 deferred triage entries sono **esplicitamente documentate**.
- I docs storici **non sono toccati**.
- Suite runner registrato con 5 OPTIONAL tuples; **nessun REQUIRED toccato
  / indebolito / rimosso**.

## 18. Commit SHA

Verrà aggiornato dopo `git commit`.

# 131 — Pre-QA Stabilization 118 — Manual QA Device Unlock Pass — FINAL REPORT

**Pack ID:** `PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS_READY_FOR_GAME_MASTER_REAUDIT`

---

## 2. Scope Summary

Pack 118 è puramente **diagnostico / documentale / read-only**. Prepara lo
sblocco controllato del Manual QA su device reale per le sole superfici già
verificate sicure (read-only o locked verified). Nessun sistema live attivato.
Nessuna modifica frontend. Nessuna modifica runtime backend. Tutte le
foundation 115A–117B preservate.

Roadmap compressa (confermata):

```text
117B = ACCEPTED_FOR_SCOPE
118  = MANUAL_QA_DEVICE_UNLOCK_PASS  ← QUESTO PACK
119  = POST-QA_FIX_AND_POLISH_PACK
120  = CONTROLLED_LIVE_UNLOCK_PREP
```

---

## 3. Files Created / Modified

| File | Stato |
|------|-------|
| `data/design/release_readiness/pre_qa_118_manual_qa_allowed_surface_matrix_v1.json` | **NEW** |
| `data/design/release_readiness/pre_qa_119_post_qa_triage_buckets_v1.json` | **NEW** |
| `docs/divine/qa/118_MANUAL_QA_DEVICE_RUNBOOK.md` | **NEW** |
| `docs/divine/qa/118_MANUAL_QA_EVIDENCE_TEMPLATE.md` | **NEW** |
| `backend/scripts/validate_pre_qa_stabilization_118_manual_qa_device_unlock_pass.py` | **NEW** |
| `backend/scripts/run_pre_qa_safety_validator_suite.py` | **MODIFIED** (registrato 118) |
| `docs/divine/131_PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS_FINAL_REPORT.md` | **NEW** |

**Nessuna modifica al codice runtime backend** (BP/RD/Hero Upgrade/server.py/route immutati). **Nessuna modifica frontend**.

---

## 4. Manual QA Allowed Surface Matrix

### 4.1 Stats
- **Righe totali:** 26
- **Aree coperte:** 11 (`home`, `menu`, `heroes`, `hero_detail`, `battle`, `battle_power_metadata`, `battle_power_breakdown`, `red_dot_metadata`, `hero_upgrade_metadata`, `hero_upgrade_negative`, `locked_routes`, `locked_or_deferred`, `warnings`, `negative_states`)
- **Required surfaces coperte: 13/13** ✅
  - `home_battle_power_display`, `home_red_dot_display`, `menu_red_dot_display`, `heroes_card_power_badge`, `hero_detail_power_and_upgrade_hint`, `battle_formation_slot_index`, `battle_power_metadata_and_summary`, `battle_power_breakdown_metadata_only`, `red_dot_metadata_and_summary`, `hero_upgrade_metadata_and_readiness`, `locked_plaza_dm_gacha`, `locked_or_deferred_shop_battlepass_mail_daily_events`, `negative_no_server_no_psp_no_team_source_unsafe_deferred`.

### 4.2 Distribuzione status (5/5 status_values usati)

| Status | # righe |
|--------|---------|
| `allowed_targeted_device_qa` | 8 |
| `allowed_read_only_endpoint_check` | 10 |
| `locked_verify_stays_locked` | 3 |
| `deferred_do_not_test_as_live` | 4 |
| `blocked_until_future_pack` | 1 |
| **TOTAL** | **26** |

### 4.3 Distribuzione severity_if_failed
- **P0:** 21 righe
- **P1:** 5 righe

---

## 5. Post-QA Triage Buckets (prep Pack 119)

9/9 bucket B1..B9 definiti con `safe_to_fix_in_pack_119` esplicito e `fix_policy`:

| Bucket | Sicuro in 119? | Descrizione breve |
|--------|----------------|-------------------|
| B1 UI copy/label | ✅ | Frontend-only string change. |
| B2 UI layout / safe area | ✅ | StyleSheet only, no business logic. |
| B3 Read-only endpoint polish | ✅ | Additive only, no rimozione/rename campi. |
| B4 Locked route copy polish | ✅ | Frontend copy, PreQaScreenGate intatto. |
| B5 Red Dot aggregation polish | ✅ | Anti-fakedot. |
| B6 Observability/log polish | ✅ | Log cleanup, no soppressione errori. |
| B7 Security/auth minor | ✅ | Auth Depends additive. |
| B8 Live unlock | ❌ | Attendere Pack 120+ Controlled Live Unlock Prep. |
| B9 Safety violation | ✅ P0 | Revert + harden + nuovo validator step. |

**Global invariants Pack 119**: lista esplicita di **13 pack preserved** (115A..115G, 116A, 116A-EXT FIX-A, 116B, 116C, 117A, 117B) + **12 must_not** (no battle_engine, no Character Bible rewrite, no gacha rates, no broad refactor, no formula change, etc.).

---

## 6. Manual QA Device Runbook

- 8 sezioni: premessa di sicurezza · pre-requisiti · setup sessione · ordine d'esecuzione (Fase A negative+metadata, Fase B UI player-visible, Fase C locked routes) · procedura per ogni riga · regole d'oro · triage buckets · fine sessione · stop conditions.
- 26 qa_id elencati nell'ordine consigliato.
- Stop conditions esplicite per crash/B9.
- Anti-claim warnings rigorosi.

## 7. Manual QA Evidence Template

- Header sessione (build_id, device, tester, account, UTC).
- Sommario PASS/FAIL/BLOCKED + bucket distribution.
- Regression check rapida (9 invarianti minime).
- Template YAML per riga QA.
- Issue summary per severity (P0/P1) + bucket.
- Verdetto finale tester + firma + allegati.

---

## 8. Validation Results

### 8.1 Validator 118 — step-by-step (PASS 14/14)
```
[1]  4 deliverable present + valid OK
[2]  QA matrix design_only + 5 allowed_status_values OK
[3]  QA matrix rows=26 required_fields + status validi OK
[4]  QA matrix coverage 13/13 surfaces + status_distribution coerente OK
[5]  QA matrix uses all 5 allowed statuses OK
[6]  Triage buckets 9/9 (B1..B9) + global invariants OK
[7]  Runbook contains required sections + anti-claim warnings OK
[8]  Evidence template contains required fields OK
[9]  Invariants preserved (BP/RD/HU versions + 116B contract + no can_upgrade_now=True) OK
[10] no DB mutation + no claim/upgrade/spend/push references in 118 files OK
[11] no out-of-scope imports in validator 118 OK
[12] no .pyc / __pycache__ tracked OK
[13] pre-QA safety suite registers 118 OK
[14] runtime smoke 4 endpoint metadata + flags invarianti OK
```

### 8.2 Catena validator richiesta — tutti PASS

| Validator | RC | Status |
|-----------|----|--------|
| `validate_pre_qa_stabilization_118_*` | 0 | ✅ **PASS** (14/14) |
| `validate_pre_qa_stabilization_117b_*` | 0 | ✅ **PASS** |
| `validate_pre_qa_stabilization_117a_*` | 0 | ✅ **PASS** |
| `validate_pre_qa_stabilization_116c_*` | 0 | ✅ **PASS** |
| `validate_pre_qa_stabilization_116b_*` | 0 | ✅ **PASS** |
| `validate_pre_qa_stabilization_116a_ext_fix_a_*` | 0 | ✅ **PASS** |
| `validate_pre_qa_stabilization_115f_*` | 0 | ✅ **PASS** |
| `sweep_repo_hygiene.py` | 0 | ✅ **clean=true** (0 bytecode tracciato) |

### 8.3 `run_pre_qa_safety_validator_suite.py`
```
totali:  23
PASS:    23
FAIL:    0
SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260615T021643Z.json`

---

## 9. Runtime / Curl Evidence (backend UP)

| Endpoint | Method | Auth | HTTP | Invariante chiave |
|----------|--------|------|------|-------------------|
| `/api/battle-power/metadata` | GET | no | **200** | `formula_version=battle_power_v1_preqa_derived` |
| `/api/battle-power/summary?server_id=s1` | GET | sì | **200** | `team_missing=true` (utente neo); formula invariata |
| `/api/battle-power/breakdown` | GET | no | **200** | `breakdown_version=battle_power_breakdown_v1_preqa_metadata_only`; `metadata_only_COMPLETE`; active=1 / deferred=13 |
| `/api/red-dot/metadata` | GET | no | **200** | `red_dot_summary_version=red_dot_v1_preqa_read_only_foundation`; `no_db_writes=true`; `no_push_notification=true` |
| `/api/red-dot/summary?server_id=s1` | GET | sì | **200** | source `server_profile_required` safe warning |
| `/api/hero-upgrade/metadata` | GET | no | **200** | `source_version=hero_upgrade_readiness_v1_preqa_read_only`; `safe_read_only=true`; `global_blocker=ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS` |
| `/api/hero-upgrade/readiness` (no server_id) | GET | sì | **400** | `code=SERVER_ID_REQUIRED`, `no_silent_s1_fallback=true` |
| `/api/hero-upgrade/readiness?server_id=s1` | GET | sì | **200** | `status=blocked_no_psp_for_server`, `any_red_dot_candidate=false` |
| `/api/user/heroes?server_id=s1` | GET | sì | **200** | neo-utente: 0 heroes, no mutation |

Tutti i flag invarianti delle foundation precedenti confermati.

---

## 10. Safety Invariants

| Invariante | Stato |
|------------|-------|
| DB writes | **0** |
| Reward grants | **NO** |
| Claim/read-all/spend/buy/summon/gacha activation | **NO** |
| Daily/achievement/mail/Battle Pass claim activation | **NO** |
| Shop/item-shop/VIP live activation | **NO** |
| Push notification activation | **NO** |
| Chat/DM/bot live activation | **NO** (116B preservato) |
| Hero Upgrade mutation | **NO** |
| Material consume | **NO** |
| Equip/fuse/forge mutation | **NO** |
| Battle Power formula change | **NO** (`battle_power_v1_preqa_derived` invariata) |
| Red Dot actionable resolver oltre warning safe | **NO** |
| Combat authoritative activation | **NO** |
| `battle_engine.py` toccato | **NO** |
| Combat/Tower runtime change | **NO** |
| Character Bible rewrite | **NO** |
| Gacha rates change | **NO** |
| Broad refactor | **NO** |
| Frontend code changes | **NO** (zero file modificati in `frontend/`) |
| Backend route/util runtime change | **NO** (solo NEW validator + MOD suite registration) |
| `.pyc` / `__pycache__` tracciati | **NO** |
| `git add -A` / `git add .` usato | **NO** (esplicito `git add -- <path>`) |
| False PASS | **NO** (suite 23/23 reale) |

---

## 11. Recommended Next Step

1. **Eseguire Manual QA su device fisico** seguendo `docs/divine/qa/118_MANUAL_QA_DEVICE_RUNBOOK.md`.
2. Compilare `docs/divine/qa/118_MANUAL_QA_EVIDENCE_TEMPLATE.md` con i risultati.
3. Game Master classifica eventuali FAIL nei 9 triage buckets (B1..B9).
4. Avviare **Pack 119 POST-QA Fix and Polish** SOLO per issue nei bucket sicuri (B1..B7 + B9). B8 → attendere Pack 120.

---

## 12. Commit SHAs

- **Baseline pre-118:** `064ce9dfc` (master, post-117B)
- **Pack commit 118:** `1fc034180` — verdetto `PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS_READY_FOR_GAME_MASTER_REAUDIT` (7 file NEW, 1 MOD suite).

---

## 13. Stop Condition

🛑 **Stop. Non procedere a 119. Attendere re-audit Game Master del Pack 118 + eventuale completamento Manual QA su device.**

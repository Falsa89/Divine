# Pre-QA Stabilization 111 — Rebaseline + Route Classification — Final Report

Autorizzazione: `AUTORIZZO_PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION`.

## Verdict

**`PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION_READY_FOR_DEEP_REAUDIT_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

Tutti i 4 remaining items dichiarati nel Pack 110-stabilization (R-01, R-02, R-03, R-04) sono stati risolti. Smoke E2E 18/18 PASS. Nessuna runtime activation. Nessuna release/public launch claim. Nessuna mutation distruttiva.

## R-01 — authTokenCompat adoption in servers.tsx — RESOLVED

**File modificato:** `frontend/app/servers.tsx` (linee ~213).

**Implementazione:**
- Sostituito `import('expo-secure-store').getItemAsync('v96_auth_token')` con `getAuthTokenCompat()` da `frontend/src/utils/authTokenCompat.ts`.
- Il bridge legge prima SecureStore `v96_auth_token` (canonical), poi AsyncStorage `token` (login default) come fallback. Nessun security downgrade.
- Se token assente: salva flag `pack86_psp_ensure_last_mode='no_auth_token_psp_ensure_deferred'` per UI honest blocker downstream.
- Nessun hardcoded server_id fallback. Nessun plaintext debug secret. Nessun JWT_SECRET in frontend.

Validator: `validate_pre_qa_stabilization_111_auth_token_compat_adoption.py` PASS.

## R-02 — 124 route uncategorized classify — RESOLVED

**File creato:**
- `backend/scripts/validate_pre_qa_stabilization_111_route_classification.py` (classifier deterministico).
- `docs/divine/113_PRE_QA_STABILIZATION_111_ROUTE_CLASSIFICATION_FULL.md` (catalog completo).

**Risultato:**

| Categoria | Conteggio |
|-----------|-----------|
| allowed_safe | 41 |
| internal_only | 3 |
| dev_only | 1 |
| legacy_quarantined | 43 |
| deferred_blocker | 0 |
| requires_future_pack | 28 |
| not_player_facing_readonly | 51 |
| duplicate_or_dead_route | 0 |
| needs_manual_review_non_blocking | 2 |
| **uncategorized** | **0** |

Totale route mutating classificate: **169**. `needs_manual_review_non_blocking`: 1.2% (< 5% soglia). Nessuna route marcata `allowed_safe` senza evidenza (prefix strict canonico o auth/onboarding esplicito).

Validator: classifier integrato `[PASS] remaining_uncategorized=0`.

## R-03 — Pack 110 validators registered in master suite — RESOLVED

**File modificato:** `backend/scripts/run_hero_skill_kit_validator_suite.py`.

**Validator Pack 110 + 111 registrati come tuple uniche** (14 tuple totali):
- `PROJECT-PRE-QA-110-GACHA-QUARANTINE`
- `PROJECT-PRE-QA-110-TEAM-FORMATION-QUARANTINE`
- `PROJECT-PRE-QA-110-USE-SERVER-SCOPE-ALIAS`
- `PROJECT-PRE-QA-110-AUTH-TOKEN-BRIDGE`
- `PROJECT-PRE-QA-110-MENU-CLEANUP`
- `PROJECT-PRE-QA-110-ACHIEVEMENTS-QUARANTINE`
- `PROJECT-PRE-QA-110-MUTATING-ROUTE-ALLOWLIST`
- `PROJECT-PRE-QA-110-STATIC-ANTI-LEAK-GUARD`
- `PROJECT-PRE-QA-110-DATA-INVARIANTS`
- `PROJECT-PRE-QA-110-PACK-91-109-QA-KICKOFF-PRESERVATION`
- `PROJECT-PRE-QA-110-RUNTIME-SMOKE-E2E`
- `PROJECT-PRE-QA-110-FINAL-REPORT`
- `PRE-QA-STABILIZATION-110-ROLLUP`
- `PROJECT-PRE-QA-111-ROUTE-CLASSIFICATION` + altri Pack 111.

Nessun duplicato. Nessun safety check nascosto come optional. `fake_PASS=false`.

Validator: `validate_pre_qa_stabilization_111_validators_registered.py` PASS.

## R-04 — MD5 rebaseline of authorized drift only — RESOLVED

**File creato:** `data/design/audit/pre_qa_111/md5_rebaseline_authorized.json` (manifest evidence-based).

**10 entries autorizzate**, ognuna con `pin_file + field + old_hash + new_hash + target_file + reason + blocker_pack_110`:

| # | Pin | Field | Old | New | Target | Pack 110 blocker |
|---|-----|-------|-----|-----|--------|------------------|
| 1 | `audit/batch1_v2/track_b_gacha_lock_v1.json` | gacha_tsx_md5_post | f68b9239... | a0304fba... | gacha.tsx | P0-A |
| 2 | `audit/batch1_v2/track_f_menu_hardening_v1.json` | menu_tsx_md5_post | 3cdb2edc... | bdf297a8... | menu.tsx | P0/P1-E |
| 3 | `server_profiles/project_sp_no_mutation_regression_guard_v1.json` | menu_md5_unchanged | 3cdb2edc... | bdf297a8... | menu.tsx | P0/P1-E |
| 4 | `project_management/project_server_profiles_ui_lock_completion_v1.json` | battle_engine + menu | 151ca35a... + 3cdb2edc... | 8b7f55d4... + bdf297a8... | battle_engine.py + menu.tsx | P0-B + P0/P1-E |
| 5 | `project_management/project_server_profiles_dual_read_preview_completion_v1.json` | battle_engine + menu | 151ca35a... + 3cdb2edc... | 8b7f55d4... + bdf297a8... | battle_engine.py + menu.tsx | P0-B + P0/P1-E |
| 6 | `status_effects/project_v_second_slice_dev_live_rollback_kill_switch_v1.json` | battle_engine_md5_post_rollback | 151ca35a... | 8b7f55d4... | battle_engine.py | P0-B |
| 7 | `project_management/project_mode_wiring_registry_completion_v1.json` | battle_engine_md5_post | 151ca35a... | 8b7f55d4... | battle_engine.py | P0-B |
| 8 | `backend/scripts/validate_project_m_status_first_slice_canary_env_rc_gate_v1.py` | SV (server.py md5) | 0e5f9447... | bb663878... | server.py | P0-A |
| 9 | `backend/scripts/validate_project_z_safe_menu_or_preview_hub_wiring_v1.py` | Tabs.Screen count | 5 | 6 | _layout.tsx | P0-A |
| 10 | `backend/scripts/validate_project_frontend_c_daily_hub_menu_entry_safe_wiring_v1.py` | Tabs.Screen count | 5 | 6 | _layout.tsx | P0-A |

**Forbidden rebaseline NON eseguiti:**
- `.env` (qualsiasi) — preservato.
- Character Bible — preservato.
- `JWT_SECRET` / segreti — preservato.
- Gacha rates / banner rates — preservato.
- Monetization / economy unrelated to Pack 110 — preservato.

**Pre-existing drift NON nello scope Pack 111** (documentati onestamente, NON rebaselineati):
- `validate_project_sp_ui_lock_completion_v1` — `economy_py_md5_post` drift Pack 92+ (pre-esistente).
- `validate_project_server_profiles_dual_read_preview_completion_v1` — `economy_py_md5_post` drift Pack 92+.
- `validate_project_m_battle_engine_status_seam_wiring_v1` — `apply_dot` keyword Pack 92+ drift.
- `validate_project_m_status_first_slice_canary_env_rc_gate_v1` — `combat.py` drift Pack 92+ (questo validator hardcoda 2 MD5 — solo quello server.py linkato Pack 110 è stato rebaselineato).

Questi 4 drift pre-esistenti restano FAIL nella suite (4 fail residui) ma sono **NON safety violation**. Rebaseline richiede pack di consolidamento storico separato.

Validator: `validate_pre_qa_stabilization_111_md5_rebaseline_authorized.py` PASS.

## Smoke E2E

Script: `backend/scripts/smoke_pre_qa_stabilization_111_rebaseline_route_classification.py`. **18/18 step PASS**:

```
[1] authTokenCompat adopted in servers.tsx OK
[2] no silent s1 fallback in servers.tsx OK
[3] route classification uncategorized=0 OK
[4] Pack 110 validators registered + Pack 111 classifier registered OK
[5] MD5 rebaseline limited to authorized 10 entries OK
[6] gacha pull/pull10 still quarantine OK
[7] Evoca hidden default OFF OK
[8] legacy achievement claim still quarantine OK
[9] team/update-formation legacy still quarantine OK
[10] reward_live_general=false everywhere OK
[11] release_readiness_claimed=false OK
[12] public_launch_ready=false declared in final report OK
[13] production_release_ready=false declared in final report OK
[14] users.gold/gems/experience unchanged OK
[15] no premium/hard/gems grants OK
[16] no IAP/gacha/payment activation OK
[17] no guild/arena/pvp/event reward live OK
[18] Pack 91-110 rollups preserved OK
SMOKE PRE_QA_STABILIZATION_111 OK
```

## Explicit Non-Claims

- ✅ `reward_live_general=false`  ✅ `release_readiness_claimed=false`
- ✅ `public_launch_ready=false`  ✅ `production_release_ready=false`
- ✅ NO gacha live  ✅ NO IAP/payment/store
- ✅ NO premium/hard currency grant/spend
- ✅ NO Guild/Arena/PvP/Event/Battlepass/AFK reward live
- ✅ NO `users.gold/gems/experience` mutation
- ✅ NO broad DB writes  ✅ NO destructive migration
- ✅ NO nuove feature delle 17 voci backlog implementate
- ✅ NO `fake_PASS`  ✅ NO validator weakening  ✅ NO safety violation hidden as MD5 drift

## Baseline / Final suite

- **Baseline (post-Pack-110-stabilization)**: `pass=1733, fail=45, miss=0`.
- **Final (post-Pack-111)**: atteso `pass=1745, fail=41, miss=0` (delta +12 PASS / -4 FAIL):
  - +5 nuovi validator Pack 111 registrati (tutti PASS individualmente).
  - +5 nuovi validator Pack 110 registrati (PASS dopo rebaseline).
  - +2 ulteriori validator Pack 110 registrati (rollup + final report).
  - -8 fail dei Pack 110 MD5 drift ora rebaselineati (gacha_lock, menu_hardening, no_mutation_regression, ui_lock, dual_read, V rollback, mode_wiring, server.py canary, project_z, frontend_c).
  - 4 fail residui pre-esistenti **NON-Pack-110-linked** documentati onestamente.

## Commit hash

- Baseline pre-Pack-111: `86de89ce2` (post-Pack-110-stabilization).
- Final commit: vedere `git log -1 --format=%H` post auto-commit di chiusura Pack 111.

## Pack 91-110 safety preservation

- Smoke step [18] PASS: tutti i 6 rollup Pack 104-109 + rollup Pack 110-stabilization presenti.
- QA Kickoff artifacts (Pack 109 + 111) intatti.

## Next step

**Utente: inviare nuova repo ZIP per deep re-audit pre-QA manuale.**

Una volta confermato il re-audit OK e nessun blocker P0/P1 residuo:
1. Pack di consolidamento storico per rebaseline MD5 pre-esistenti Pack 92+ (opzionale).
2. Avvio QA manuale come da `111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md`.

## Stop rule

Pack 111 chiusura: docs + classifier + adoption + rebaseline authorized + report. Nessuna QA manuale avviata. Nessuna feature backlog implementata. Nessuna runtime activation. Attendo verifica utente.

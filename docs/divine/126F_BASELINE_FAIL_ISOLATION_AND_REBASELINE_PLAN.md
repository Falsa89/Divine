# 126F — PROJECT_D Track F — BASELINE FAIL ISOLATION + REBASELINE PLAN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_F_BASELINE_FAIL_ISOLATION_READY`  
**Rollback**: N/A (audit only)

## 1. Stato baseline pre vs post V_D

| Suite run | PASS | FAIL | MISS | Note |
|---|---|---|---|---|
| Post V_C (reported) | 387 | 3 | 0 | cache state file `_slc_c_combo_v1_result.json` ancora PASS pre-V_C |
| **Post V_D (observed)** | **390** | **8** | **0** | V_D ha rieseguito SLC-C-COMBO v1 invalidando il cache → cluster fail completo visibile |

**Δ trasparenza**: i 5 fail aggiuntivi (`SLC-D-PREFLIGHT`, `SLC-BE-PREFLIGHT`, `SLC-BE-COMBO`, `SLC-F-PREFLIGHT`, `SLC-F-COMBO`) **NON sono regressioni** — sono manifestazione naturale del cluster di fail monocausale già esistente, ora pienamente visibile come richiesto dal principio anti-hiding del Track F.

## 2. Cluster di 8 fail (monocausale)

| Task ID | Script | Required | Classification | Cluster role |
|---|---|---|---|---|
| `SLC-C-REPO-PREFLIGHT` | `audit_slc_c_repo_multishard_preflight.py` | NO | `DEPRECATED_VALIDATOR` | **ROOT** |
| `SLC-C-COMBO` | `validate_slc_c_combo_v1.py` | NO | `DEPRECATED_VALIDATOR` | PROPAGATOR |
| `SLC-D-PREFLIGHT` | `validate_slc_d_preflight_v1.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |
| `SLC-D-COMBO` | `validate_slc_d_merge_tooling_combo_v1.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |
| `SLC-BE-PREFLIGHT` | `validate_slc_be_preflight_v1.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |
| `SLC-BE-COMBO` | `validate_slc_be_server_profile_selection_combo.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |
| `SLC-F-PREFLIGHT` | `validate_slc_f_preflight_v1.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |
| `SLC-F-COMBO` | `validate_slc_f_route_patch_dryrun_combo_v1.py` | NO | `TRANSITIVE_DEPRECATED_VALIDATOR` | DOWNSTREAM |

### Root cause unificato (cluster monocausale)

L'audit V1 `audit_slc_c_repo_multishard_preflight.py` enforz·a `multishard==design-only`. Dopo SLC-G commit-A (multishard runtime attivo come baseline), l'invariante non è più valido. Il combo `SLC-C-COMBO v1` produce il file di stato `_slc_c_combo_v1_result.json` con `status=FAIL`. I 6 downstream (`SLC-D/BE/F-PREFLIGHT` + `SLC-D/BE/F-COMBO`) leggono questo file e falliscono in cascata. **Tutti i sub-test interni dei 3 combo passano**: i fail sono indotti dal preflight obsoleto.

## 3. Classification summary

| Categoria | Count |
|---|---|
| SAFE_TO_REBASELINE | 0 |
| NEEDS_FIX | 0 |
| **DEPRECATED_VALIDATOR** | **2** (ROOT + PROPAGATOR) |
| **TRANSITIVE_DEPRECATED_VALIDATOR** | **6** (DOWNSTREAM) |
| BLOCKER | 0 |

## 4. Topology

```
ROOT       : SLC-C-REPO-PREFLIGHT
              │
              ▼
PROPAGATOR : SLC-C-COMBO ─── writes ──► _slc_c_combo_v1_result.json (status=FAIL)
              │                                      │
              └──────────────reads ──────────────────┘
                             │
                             ▼
DOWNSTREAM : SLC-D-PREFLIGHT ──► SLC-D-COMBO
             SLC-BE-PREFLIGHT ──► SLC-BE-COMBO
             SLC-F-PREFLIGHT  ──► SLC-F-COMBO
```

**Risolvendo ROOT in V_E si chiudono automaticamente PROPAGATOR e tutti i 6 DOWNSTREAM.**

## 5. Rebaseline plan (4 fasi)

| Phase | Pack | Azione |
|---|---|---|
| 1 | **V_D** | isolate + classify (questo pack): cluster di 8 fail mappato |
| 2 | V_E | emit 8 v2 successors (1 ROOT + 1 PROPAGATOR + 6 DOWNSTREAM) + suite registration |
| 3 | V_F | deprecare v1 dietro `SUITE_KEEP_DEPRECATED_AUDITS=true` (default OFF); rimuovere `_slc_c_combo_v1_result.json` |
| 4 | V_G | rimuovere v1 entries da OPTIONAL; cleanup documentazione |
| Final | post V_G | suite full green: `pass=N+8 fail=0 miss=0` |

## 6. Hard invariants Track F (anti-cheat)

- ❌ NO validator REQUIRED weakening
- ❌ NO hiding di failures
- ❌ NO fake PASS
- ❌ NO exit-code masking
- ❌ NO rimozione dei v1 entries fino a V_F
- ✅ tutti gli 8 script restano **registrati e in esecuzione** in OPTIONAL fino a V_F (la suite continua a riportare 8 FAIL)

## 7. Forbidden scope rispettato

Validator weakening ❌, hiding failures ❌, REQUIRED changes ❌, fake PASS ❌.

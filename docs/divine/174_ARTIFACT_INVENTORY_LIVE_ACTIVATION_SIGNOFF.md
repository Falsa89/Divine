# 174 — PROJECT ARTIFACT INVENTORY LIVE ACTIVATION SIGNOFF

## Verdetto locale
**`PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF_READY_NOT_APPLIED`**

> Diventerà `_COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo Save to GitHub → branch `main` → PUSH e verifica della repo pubblica.

---

## Natura del pack
Stage 7 è un **gate di signoff formale**, non un'attivazione runtime. Definisce — senza eseguire — tutto ciò che serve per un eventuale Stage 8 di live apply:

| Track | Output | Stato |
|---|---|:---:|
| A | Revalidation manifesto Stages 1–6 | ✅ READY |
| B | Approval matrix (9 approval, **0/9 granted**) | ✅ READY |
| C | Canary scope (allowlist vuota di default) + write budget | ✅ READY |
| D | Apply runbook + rollback (no apply eseguito) | ✅ READY |
| E | Post-apply lock policy (cosa resta lockato anche dopo apply) | ✅ READY |
| F | Validator + proof marker JSON per suite | ✅ READY |
| G | Public repo sync verification | ⏳ PENDING utente |
| H | Completion totals (0 DB writes, 0 env injection) | ✅ READY |

## ⚠️ Marker live richiesti per futuro apply (DEFINITI, NON IMPOSTATI)
```
PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL=true            ← non impostato
ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit         ← non impostato
ARTIFACT_INVENTORY_CANARY_SCOPE_APPROVED=true            ← non impostato
ARTIFACT_INVENTORY_ROLLBACK_OWNER_APPROVED=true          ← non impostato
ARTIFACT_INVENTORY_QA_APPROVED=true                      ← non impostato
```
**`backend/.env` MD5 invariato** `ff60bbb79efa329b71aa8ed351ea89b3` — nessun marker iniettato.

## 📋 Approval matrix (9 approval, design only)
1. **User/Product** — `PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL`
2. **Engineering** — `ARTIFACT_INVENTORY_RUNTIME_ENABLED`
3. **QA** — `ARTIFACT_INVENTORY_QA_APPROVED`
4. **Rollback owner** — `ARTIFACT_INVENTORY_ROLLBACK_OWNER_APPROVED`
5. **Data model** — schema design v1
6. **Security/safety** — forbidden_fields audit
7. **Economy/balance** — `gameplay_status=inactive/cosmetic_prestige_only`
8. **Server profile scoping** — `(user_id, server_profile_id, artifact_id)`
9. **Player visibility** — `ARTIFACT_INVENTORY_CANARY_SCOPE_APPROVED`

Tutti `NOT_GRANTED` in questo pack. Future apply **bloccato** fino al granting esplicito di tutti.

## 🎯 Canary scope (Track C)
| Vincolo | Valore |
|---|---|
| Scope type | `internal_only` |
| Player-facing | **false** |
| Allowlist | richiesta non vuota, default **[]**, max **5** users |
| Server IDs allowed | `["s1"]` |
| Artifact IDs initial | `["relic_aurora_eterna"]` |
| Source type initial | `system_seed` |
| Forbidden sources initial | `future_iap`, `future_gacha`, `future_shop`, `event_reward`, `compensation`, `admin_grant` |

### Write budget primo apply
| Collection | Max ops |
|---|:---:|
| `artifact_catalog_snapshot` | 32 inserts (snapshot Bible, idempotente) |
| `user_artifact_inventory` | 5 inserts / 0 updates |
| `artifact_inventory_ledger` | 5 append |
| `artifact_collection_state` | 5 upsert |
| `artifact_idempotency_registry` | 5 inserts |
| **Forbidden writes** | `users`, `user_artifacts`, `user_constellations`, `teams` → **0** |
| **Totale max** | **52 op**, abort se superato |

## 🛠️ Runbook (Track D, **non eseguito** in questo pack)
- 8 preflight checks (suite PASS, MD5 invariants, 423/200 smoke, hidden_banners check, mongodump backup, env marker check)
- Dry-run prima di apply
- Apply solo con tutti i 5 env marker + CLI flag `--i-understand-this-will-write`
- Post-apply checks su budget/ledger consistency/MD5
- Rollback: pre-live = drop in ordine inverso; post-live = compensating ledger entries (**never hard-delete**)
- 6 abort criteria + emergency stop documentati

## 🔒 Post-apply lock policy (Track E)
Anche dopo eventuale apply futuro restano lockati:
- ✅ Gacha banner artifact + constellation nascosti
- ✅ 7 POST mutativi legacy → 423
- ✅ Nessun endpoint equip/fuse/craft/pull aggiunto
- ✅ `/artifacts-preview` statico (eventuale wiring solo in pack frontend dedicato)
- ✅ Zero combat bonus, zero hero stat delta
- ✅ Zero IAP/Shop/BP/VIP collegamenti
- ✅ Nessuna route inventario pubblica (solo internal canary in apply pack)

## 🔐 Invarianti rispettati
| File | MD5 atteso | OK |
|---|---|:---:|
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | ✅ |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | ✅ |
| `backend/routes/artifacts.py` | `893f244d85fd45cbe825996463995293` | ✅ |
| `frontend/app/artifacts-preview.tsx` | `0e75c94e00899af773dbc9faf7326a15` | ✅ |
| `frontend/app/artifacts.tsx` | `8849e21c44207fc1d0074cae2cdc6879` | ✅ |
| `frontend/app/(tabs)/gacha.tsx` | `f68b9239cec04ea54879f0be381e772a` | ✅ |

## 🛡️ Anti-stale-push (lezione dai pack 171/173)
Visto che il watcher "Save to GitHub" ha avuto sync flaky sul suite runner, in questo pack:

1. **Sentinella v3 nel header** del suite runner: `# PUBLIC_SYNC_TAG: suite_runner_live_signoff_v3_force_resnapshot_2026_05_27` + 4 righe documentative
2. **Sentinella inline** sopra la registrazione Stage 7: `# STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL`
3. **Mantengo** la sentinella Stage 6 esistente per non perdere copertura
4. **Proof marker JSON dedicato** in `data/design/artifacts/live_signoff/artifact_live_signoff_suite_registration_proof_marker_v1.json`, in directory diversa già storicamente robusta al sync

## 📁 File aggiunti / modificati
| Op | Path |
|:---:|---|
| A | `data/design/artifacts/live_signoff/artifact_live_signoff_previous_stage_revalidation_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_live_activation_approval_matrix_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_live_canary_scope_write_budget_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_live_apply_runbook_rollback_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_runtime_locks_post_apply_policy_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_live_signoff_suite_registration_proof_marker_v1.json` |
| A | `data/design/artifacts/live_signoff/artifact_live_signoff_completion_v1.json` |
| A | `backend/scripts/validate_project_artifact_inventory_live_activation_signoff_v1.py` |
| M | `backend/scripts/run_hero_skill_kit_validator_suite.py` (sentinella v3 + registrazione OPTIONAL) |
| A | `docs/divine/174_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF.md` (questo file) |

## 🔜 Prossimo pack consigliato
`PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY_PACK` (Stage 8) — **solo** dopo che l'utente concede esplicitamente tutti i 5 live marker E fornisce una canary allowlist non vuota. Alternativa: shift di priorità su IAP/BP/Shop modernization.

# 125G — PROJECT_C Track G — LEGACY SERVER SELECT DEPRECATION METRICS

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_C`  
**Track**: G  
**Mode**: `metrics_design_only_no_route_mutation`  
**Verdict**: 🟢 `TRACK_G_LEGACY_SERVER_SELECT_DEPRECATION_METRICS_DESIGN_READY`  
**Rollback**: N/A (solo design, nessun wiring)

---

## 1. Scopo

Definire (ma **non emettere a runtime**) il set di **3 metriche** + **strategia di archiviazione log** + **kill-switch a 4 fasi** per la route legacy `POST /api/server/select`. Le metriche sono compatibili sia con Prometheus sia con la pipeline AF2-N V8.

## 2. Logger emitter (preesistente, invariato)

| Aspetto | Valore |
|---|---|
| Logger | `divine.deprecation` |
| Event token | `legacy_server_select_call` |
| Già attivo da | V7 BLOCK_A |
| Behavior change V_C | ❌ Nessuno |

## 3. Metriche design (3)

| Metric name | Tipo | Labels | Emitter |
|---|---|---|---|
| `divine_legacy_server_select_calls_total` | counter | `user_present`, `http_status` | deferred_to_metrics_block_v_d |
| `divine_legacy_server_select_deprecation_log_emit_total` | counter | `event_token` | deferred_to_metrics_block_v_d |
| `divine_legacy_server_select_unique_users_24h` | gauge | — | deferred_to_metrics_block_v_d |

Tutte le metriche sono Prometheus-compatible e AF2-N pipeline compatible.

## 4. Log archival design

| Aspetto | Valore |
|---|---|
| Target path | `/var/log/divine/deprecation_legacy_server_select.log` (proposto) |
| Max size | 64 MB |
| Max archives | 4 |
| Retention | 30 giorni |
| Attivo in V_C | ❌ No (solo design) |

## 5. Kill-switch a 4 fasi

| Phase | Pack | Azione |
|---|---|---|
| 1 | V_D | emit metrics counter |
| 2 | V_E | alert su soglia (es. > 100 calls / 24h) |
| 3 | V_F | gating dietro feature flag default OFF (post AF2-N rollout) |
| 4 | V_G | sunset route dopo 30 giorni di zero-call |

## 6. Forbidden scope rispettato

Server select behavior change ❌, users.server backfill ❌, DB migration ❌, battle mutation ❌, AF2-N runtime flip ❌, metric emitter runtime wiring ❌.

## 7. Validator

`/app/backend/scripts/validate_project_c_legacy_server_select_deprecation_metrics_v1.py` — verifica i 3 nomi metric canonici, emitter `deferred_to_metrics_block_v_d`, design archival inerte, 4-fase kill-switch.

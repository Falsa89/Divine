# 103 · SLC-H — SERVER SELECTION ENDPOINT DESIGN-ONLY

**Stato finale**: ✅ `SLC_H_DESIGN_READY_NOT_IMPLEMENTED`
**Modalità**: `DESIGN-ONLY / CONTRACT-ONLY / READ-ONLY / NO RUNTIME ROUTE`
**Suite globale**: `RM1.31-B` → **335 PASS / 0 FAIL / 0 MISS** (330 → 335, +5 SLC-H OPTIONAL)
**Baseline diff RM1.32-PRE**: ✅ PASS
**Runtime route count for SLC-H endpoints**: **0** (nessuna route live registrata)
**Progress percent (per spec)**: 80 → **83**

---

## 1. Obiettivo

Definire il contratto completo dei 5 futuri endpoint di selezione server, con
schemi request/response, modalità di rifiuto/fallimento, contratto degli stati
server, flusso futuro, note UI di handoff e gate di prontezza, **senza
implementare alcun endpoint runtime, alcuna route, alcuna UI**.

L'obiettivo è preparare il deliverable necessario perché in un futuro task gated
si possa attivare il flusso server-aware **dopo** SLC-F route patch e
`SERVER_PROFILES_RUNTIME_ENABLED=true` espliciti.

---

## 2. Endpoint contract (5 endpoint futuri)

| # | Method | Path | Auth | Idempotent | Note |
|---|---|---|---|---|---|
| SH-EP-001 | GET | `/api/servers` | no | ✅ | Lista pubblica dei server; nessun shard host o connection string esposto |
| SH-EP-002 | GET | `/api/account/server-profiles` | sì | ✅ | Profili server dell'account; per account legacy ritorna profilo implicito `s1` derivato da SLC-G |
| SH-EP-003 | POST | `/api/account/server-profiles/select` | sì | no | Setta server attivo (gated su `SERVER_PROFILES_RUNTIME_ENABLED`) |
| SH-EP-004 | GET | `/api/account/active-server` | sì | ✅ | Ritorna server attivo (default legacy `s1`) |
| SH-EP-005 | POST | `/api/account/server-profiles/create` | sì | no | **future-only**, bloccato finché `SECOND_SERVER_OPENING_ENABLED` resta unset |

Tutti gli endpoint sono **non implementati** in questa fase. `runtime_implementation_status=NOT_IMPLEMENTED`.

---

## 3. Failure modes (10 codici di rifiuto contrattuali)

| Error code | HTTP | Trigger | Retryable |
|---|---|---|---|
| `second_server_locked` | **423** | `SECOND_SERVER_OPENING_ENABLED` unset AND target ≠ `s1` | ❌ |
| `server_not_available_for_account` | **403** | status non in {open,crowded,closed_to_new} per il tipo account | ❌ |
| `server_archived` | **410** | status == archived | ❌ |
| `server_merged_redirect` | **308** | status == merged; risposta include `merged_into_server_id` | ❌ |
| `server_merge_pending` | **409** | status == merge_pending | ✅ |
| `route_patch_not_applied` | **423** | SLC-F `route_patch_applied=false` AND target ≠ `s1` | ❌ |
| `server_profiles_runtime_disabled` | **423** | `SERVER_PROFILES_RUNTIME_ENABLED` unset (POST endpoints) | ❌ |
| `auth_required` | **401** | manca auth token | ❌ |
| `rate_limited` | **429** | rate-limit superato | ✅ |
| `validation_error` | **422** | body invalido / server_id ignoto | ❌ |

Tutte le risposte di errore devono includere `retryable`; merge redirect deve
includere `merged_into_server_id`; nessuna risposta espone shard host /
connection string / load metrics interne.

---

## 4. Server status contract (7 stati con HTTP mapping)

| Status | new_account | existing_account | HTTP on select | Label UI (it) |
|---|---|---|---|---|
| `planned` | ❌ | ❌ | 403 | "in_arrivo" |
| `open` | ✅ | ✅ | 200 | "aperto" |
| `crowded` | ✅ | ✅ | 200 | "affollato" |
| `closed_to_new` | ❌ | ✅ | 200 | "chiuso_ai_nuovi" |
| `merge_pending` | ❌ | ❌ | 409 | "fusione_in_corso" |
| `merged` | ❌ | ❌ | 308 | "fuso" |
| `archived` | ❌ | ❌ | 410 | "archiviato" |

### Transizioni proibite (selezione)
- `merged → open` ❌
- `merged → closed_to_new` ❌
- `archived → open` ❌
- `archived → merge_pending` ❌

### Invarianti collegate
- Borea/`primordial_gaia` non subiscono mai modifiche di visibilità da cambio status server.
- AF2-N cap=50000 e allowlist=2500 **non possono variare** in funzione del server status.

---

## 5. Future flow (8 regole + decision tree)

Le 8 regole `FR-001…FR-008` coprono:
- Default legacy → `s1` via SLC-G migration.
- Nuovo account routing in base a `SECOND_SERVER_OPENING_ENABLED`.
- Esistente account: ripristina `active_server_id` salvato, fallback a `s1`.
- Nessuna copia automatica di risorse tra server.
- Valuta a pagamento: account-wide (SLC-C `paid_free_currency_split`).
- Risorse gratuite: server-bound.
- Server-aware route patch SLC-F deve essere applicato prima della selezione non-default.

Decision tree esplicito codificato in JSON (9 step IF/ELSE) per ogni richiesta
`POST /api/account/server-profiles/select`.

---

## 6. UI handoff notes (NO implementazione)

4 schermate documentate solo come contract di copy/layout/badge per la futura
implementazione:
- `server_selection_list` — flat-list di card profilo server
- `server_profile_card_detail` — dettaglio + CTA "seleziona_server" disabled per stati invalidi
- `new_server_warning_dialog` — copy italiano: "Ogni server ha eroi, gilde e progressi separati. La valuta a pagamento resta del tuo account, ma le risorse gratuite restano su questo server."
- `paid_currency_display_warning` — banner quando l'utente vede il wallet server-specific

Lingua copy: `it_IT`. Min tap target: 44 dp. Screen-reader friendly.

`hard_ui_no_go`: NO implementazione live, NO route registration in expo router,
NO modifica al login flow esistente, NO modifica a combat / gacha / roster.

---

## 7. Readiness gates (12 gate)

| Gate | Descrizione | Stato attuale |
|---|---|---|
| SH-G1 | SLC-G `migration_applied=true` | ✅ (marker file presente) |
| SH-G2 | SLC-F route patch plan accepted, applied is separate gate | ✅ |
| SH-G3 | No `unsafe_unknown` in server-bound | ✅ (verified by SLC-G + cleanup-B) |
| SH-G4 | Default legacy `s1` verified | ✅ |
| SH-G5 | Feature flags `SERVER_PROFILES_RUNTIME_ENABLED` + `SECOND_SERVER_OPENING_ENABLED` unset | ✅ |
| SH-G6 | Endpoint contract + schemas + rejection + status + flow + UI PASS | ✅ |
| SH-G7 | AF2-N invariants intatti | ✅ |
| SH-G8 | API smoke intatto | ✅ |
| SH-G9 | Baseline diff RM1.32-PRE PASS | ✅ |
| SH-G10 | Nessuna runtime route registrata per i 5 path SLC-H | ✅ (`grep`-verified su `/app/backend/routes/`) |
| SH-G11 | Nessuna UI screen registrata in questa fase | ✅ |
| SH-G12 | Signoff per-endpoint go/no-go in task separato richiesto prima del live wiring | ✅ (contratto codificato) |

Tutti i 12 gate **PASS** in modalità design-only.

---

## 8. File creati

### 8.1 Contratti JSON (`/app/data/design/server_lifecycle/`)

| File | Scopo |
|---|---|
| `slc_h_endpoint_contract_v1.json` | Contratto master dei 5 endpoint |
| `slc_h_request_response_schemas_v1.json` | 7 schemi request/response |
| `slc_h_rejection_failure_modes_v1.json` | 10 codici di rifiuto |
| `slc_h_server_status_contract_v1.json` | 7 stati server + transizioni |
| `slc_h_future_flow_contract_v1.json` | 8 regole flusso + decision tree |
| `slc_h_ui_handoff_notes_v1.json` | 4 schermate UI con copy IT |
| `slc_h_readiness_gates_v1.json` | 12 readiness gate |

### 8.2 Validator Python (read-only)

| Script | Funzione |
|---|---|
| `validate_slc_h_endpoint_contract_v1.py` | Validator contratto endpoint + schemi |
| `validate_slc_h_rejection_modes_v1.py` | Validator codici di rifiuto |
| `validate_slc_h_server_status_contract_v1.py` | Validator stati + flow + UI handoff |
| `validate_slc_h_readiness_gates_v1.py` | Validator gate + check marker SLC-G + assenza route runtime |
| `validate_slc_h_combo_v1.py` | Orchestratore combo + decisione `final_status` |

### 8.3 Registrazione suite

Aggiunti 5 task OPTIONAL:
```
SLC-H-ENDPOINT-CONTRACT
SLC-H-REJECTION-MODES
SLC-H-SERVER-STATUS-CONTRACT
SLC-H-READINESS-GATES
SLC-H-COMBO
```
Tutti `[PASS]` exit 0.

---

## 9. Invarianti finali

| Check | Valore |
|---|---|
| `GET /api/heroes` count | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | **404** ✅ |
| `GET /api/heroes/borea` | **200** ✅ |
| `GET /api/heroes/greek_borea` | **200** ✅ |
| AF2-N cap / allowlist | **50000 / 2500** ✅ |
| AF2-N row counts | **2500 / 502 / 1914** preserved ✅ |
| SLC-G `migration_applied` | **true** (immutato) ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` ✅ |
| `route_patch_applied` | **false** ✅ |
| `second_server_opening_allowed` | **false** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | **unset** ✅ |
| `phase_11_executed` | **false** ✅ |
| `legacy_fallback_removed` | **false** ✅ |
| Runtime route SLC-H registrate | **0** ✅ |
| Baseline diff RM1.32-PRE | **PASS** ✅ |
| Suite globale | **335 PASS / 0 FAIL / 0 MISS** ✅ |

---

## 10. Guardrail rispettati

- ✅ NO runtime route creation
- ✅ NO DB writes
- ✅ NO migration
- ✅ NO collection/index creation
- ✅ NO route patch runtime
- ✅ NO secondo server aperto
- ✅ NO feature flag enable
- ✅ NO legacy fallback removal
- ✅ NO Phase 11
- ✅ NO UI implementation
- ✅ NO modifiche a battle_engine.py / battle_core.py / combat.tsx
- ✅ NO modifiche a affinity_gift_spend.py / AF2-N / Stage4 / Redis runtime
- ✅ NO modifiche a gacha / roster / Character Bible / cataloghi / asset
- ✅ NO validator weakening

---

## 11. Verdict finale

> ## ✅ `SLC_H_DESIGN_READY_NOT_IMPLEMENTED`
>
> SLC-H consegna un contratto completo, validato e pronto per il futuro
> live-wiring. **Nessun endpoint runtime, nessuna UI, nessuna route** è stata
> registrata in questa fase. La transizione a `IMPLEMENTED` richiederà un task
> separato gated con signoff per-endpoint, SLC-F route patch applicato e
> `SERVER_PROFILES_RUNTIME_ENABLED=true` esplicito.

---

## 12. Prossimi passi (gated, NON eseguiti)

- **SLC-F apply** (P1): applicazione runtime del route patch (gated, approvazione separata)
- **SLC-H live wiring task** (P2): implementazione runtime dei 5 endpoint, richiede SLC-F apply + flag esplicito + per-endpoint signoff
- **COSMETIC-B/C/D/E** (P2): read-only/inert
- **Managed Redis Live / Alerting Sink Live** (P3): pending env vars
- **Broad Rollout / Public Spend UI / STACK-G** (P4): strettamente OFF

Nessuno di questi è oggetto del task corrente.

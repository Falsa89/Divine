# 115B — BLOCK B — HOUSEKEEPING DRIFT DOCS GACHA/SUMMON ONLY

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V1`  
**Block**: B — `HOUSEKEEPING_DRIFT_DOCS_GACHA_SUMMON_ONLY`  
**Verdict**: 🟢 `BLOCK_B_DRIFT_DOCS_HOUSEKEEPING_READY`  
**Modalità**: DOC/AUDIT ONLY (nessuna scrittura DB, nessuna correzione drift)  
**Timestamp**: 20260523T210000Z

---

## 1. Marker autorizzativi

| Marker | Status |
|---|---|
| `MEGA_COMBO_SLC_ACCELERATION_V1_APPROVAL=true` | ✅ |
| `SLC_ACCELERATION_MODE=MULTI_BLOCK_PARTIAL_SUCCESS` | ✅ |
| `BLOCK_B_DRIFT_DOCS_HOUSEKEEPING_APPROVAL=true` | ✅ |

---

## 2. Riepilogo drift docs

| Indicatore | Valore |
|---|---|
| Numero noto drift docs | **7** |
| Collection | `user_heroes` |
| Campo mancante | `server_id` |
| Impatto runtime | 🟢 NESSUNO (mitigato da SLC-G commit-A legacy s1 policy) |
| Bloccante? | ❌ No (informational only) |

---

## 3. Origin routes identificate

| File | Endpoint | Linea | Funzione | Motivo del drift |
|---|---|---|---|---|
| `/app/backend/routes/heroes.py` | `POST /api/gacha/pull` | 106 | `_do_gacha_pull` | `insert_one` senza `ensure_server_scope` |
| `/app/backend/routes/heroes.py` | `POST /api/gacha/pull10` | 146 | `gacha_pull_10` (guaranteed slot) | `insert_one` senza `ensure_server_scope` |

---

## 4. Perché i drift restano deferred

1. Il pack MEGA-COMBO V1 vieta esplicitamente la mutazione runtime di **gacha/summon** (forbidden globale).
2. Toccare `heroes.py` richiederebbe un Batch-3 dedicato con canonical classification banner/rate/pity/obtainable pool.
3. Correzione inline dei 7 documenti drift in DB richiederebbe un **backfill** (DB migration vietata in V1).
4. **SLC-G commit-A** ha già introdotto la legacy `s1` policy che neutralizza l'impatto runtime: i doc senza `server_id` sono trattati come `server=s1`.
5. Il broad rollout AF2-N V8 e il second server opening sono i veri requisiti di sblocco; finché non aperti, i drift restano informational.

---

## 5. Regola canonical introdotta

**Rule ID**: `DRIFT_DOCS_GACHA_SUMMON_KNOWN_NONBLOCKING_V1`

> I 7 drift docs in `user_heroes` provenienti da gacha/summon sono **noti**, classificati come **non-bloccanti** e NON devono essere riparati inline finché non viene approvato un Batch-3 AF2-N + gacha scope dedicato.

| Soglia | Valore |
|---|---|
| max_allowed_drift_count (baseline) | **7** |
| alert_threshold (warning) | **10** |
| fail_threshold | **15** |

---

## 6. Validator strategy

- **Script**: `/app/backend/scripts/audit_drift_docs_gacha_summon_count_v1.py`
- **Comportamento**: read-only count check; **NESSUNA** correzione automatica; **NESSUNA** scrittura DB.
- **Contract**: PASS se count ≤ 10; FAIL se count ≥ 15.
- **Aggiunto a suite**: in OPTIONAL_VALIDATORS.

---

## 7. Guardrail rispettati

- ❌ No DB write
- ❌ No runtime gacha/summon patch
- ❌ No correzione drift docs
- ❌ No `hero_ownership` mutation
- ❌ No Borea activation
- ❌ No roster/visibility change

---

## 8. Artefatti creati

- `/app/data/design/system_safety/gacha_summon_drift_docs_housekeeping_v1.json`
- `/app/docs/divine/115B_GACHA_SUMMON_DRIFT_DOCS_HOUSEKEEPING.md` (questo file)
- `/app/backend/scripts/audit_drift_docs_gacha_summon_count_v1.py`

---

## 9. Verdict

🟢 **`BLOCK_B_DRIFT_DOCS_HOUSEKEEPING_READY`**

Risoluzione effettiva differita a **Batch-3 AF2-N + gacha scope dedicato** (richiede V8 signoff).

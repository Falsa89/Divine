# 115C — BLOCK C — GVG USER_MAIL AMBIGUOUS CLASSIFICATION

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V1`  
**Block**: C — `GVG_USER_MAIL_AMBIGUOUS_CLASSIFICATION`  
**Verdict**: 🟢 `BLOCK_C_GVG_USER_MAIL_CLASSIFIED_READY`  
**Modalità**: CLASSIFICATION ONLY (nessun patch su gvg.py)  
**Timestamp**: 20260523T210000Z

---

## 1. Marker autorizzativi

| Marker | Status |
|---|---|
| `MEGA_COMBO_SLC_ACCELERATION_V1_APPROVAL=true` | ✅ |
| `SLC_ACCELERATION_MODE=MULTI_BLOCK_PARTIAL_SUCCESS` | ✅ |
| `BLOCK_C_GVG_USER_MAIL_CLASSIFICATION_APPROVAL=true` | ✅ |

---

## 2. Target surface

| Campo | Valore |
|---|---|
| File | `/app/backend/routes/gvg.py` |
| Endpoint | `resolve_gvg_war` (post-war reward distribution) |
| Linea insert | **355** |
| Collection | `user_mail` |
| Op | `insert_one` |
| Stato precedente | `AMBIGUOUS_DEFER` (SLC_F_MINOR_WRITE_SURFACES_AUDIT v1) |

---

## 3. Document shape

```python
{
  "id": uuid4(),
  "user_id": uid,                      # partecipante GvG
  "subject": "Guerra GvG Vinta/Persa/Pareggio",
  "body": "Risultato + danni inflitti",
  "rewards": {"gold": int, "gems": int},
  "claimed": True,
  "timestamp": datetime.utcnow()
}
```

---

## 4. Analisi di classificazione

### Evidenze SERVER_BOUND
- La mail nasce da una `gvg_war` che è stata già patchata come **server-bound** (SLC-F GVG WAR SCOPE).
- Il subject menziona esplicitamente i nomi delle gilde (entità server-bound).
- La rilevanza informativa è legata al server dove la guerra è stata combattuta.

### Evidenze ACCOUNT_WIDE
- L'inbox utente UI è attualmente unica (no tab per-server).
- Il reward `gems` è stato applicato account-wide (ma quello è il reward, non il record).

### Decisione canonical

🟢 **`SERVER_BOUND_BY_PRODUCER`**

La mail è un *side-effect notification* del producer GvG (server-bound). L'inbox UI globale è una UX decision indipendente dallo scope del record. Quindi è sicuro applicare `ensure_server_scope` alla insert in un futuro micro-batch.

---

## 5. Pattern raccomandato per futuro patch

```python
await db.user_mail.insert_one(ensure_server_scope({
    "id": str(uuid.uuid4()),
    "user_id": uid,
    ...
}, uid))
```

| Parametro | Valore |
|---|---|
| Rischio | 🟢 low |
| DB migration | ❌ No |
| Linee di diff stimate | **2** |
| Helper `ensure_server_scope` già importato in `gvg.py` | ✅ sì (verificato in SLC-F GVG WAR SCOPE) |

---

## 6. Prossimo micro-batch raccomandato

**Nome**: `SLC_F_GVG_USER_MAIL_SCOPE_MICRO_BATCH_V1`

- File: `/app/backend/routes/gvg.py` linea 355
- Validator da aggiungere: `validate_slc_f_gvg_user_mail_scope_post_apply_v1.py`
- Rollback script richiesto: ✅

---

## 7. Guardrail rispettati

- ❌ No patch su `gvg.py`
- ❌ No `ensure_server_scope` aggiunto
- ❌ No mail/inbox behavior change
- ❌ No DB write

---

## 8. Artefatti creati

- `/app/data/design/server_lifecycle/gvg_user_mail_scope_classification_v1.json`
- `/app/docs/divine/115C_GVG_USER_MAIL_SCOPE_CLASSIFICATION.md` (questo file)

---

## 9. Verdict

🟢 **`BLOCK_C_GVG_USER_MAIL_CLASSIFIED_READY`**

Classificazione canonical: `SERVER_BOUND_BY_PRODUCER`. Pronto per micro-batch dedicato low-risk.

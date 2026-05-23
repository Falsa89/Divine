# 116B — V2 BLOCK B — GVG USER_MAIL SCOPE MICRO-BATCH (APPLIED)

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V2`  
**Block**: B — `GVG_USER_MAIL_SCOPE_MICRO_BATCH`  
**Verdict**: 🟢 `BLOCK_B_GVG_USER_MAIL_SCOPE_APPLIED_SAFE`  
**Modalità**: APPLY SAFE METADATA-ONLY  
**Rollback ID**: `v2_block_b_gvg_user_mail_20260523T213000Z`

---

## 1. Marker autorizzativi

| Marker | Status |
|---|---|
| `MEGA_COMBO_SLC_ACCELERATION_V2_APPROVAL=true` | ✅ |
| `SLC_ACCELERATION_MODE=MULTI_BLOCK_PARTIAL_SUCCESS` | ✅ |
| `BLOCK_B_GVG_USER_MAIL_SCOPE_APPLY_APPROVAL=true` | ✅ |
| `BLOCK_B_GVG_USER_MAIL_SCOPE_ROLLBACK_APPROVAL=true` | ✅ |

---

## 2. Surface patchata

| Campo | Valore |
|---|---|
| File | `/app/backend/routes/gvg.py` |
| Endpoint context | `resolve_gvg_war` (post-war reward distribution) |
| Linea (pre-patch) | **355** |
| Collection | `user_mail` |
| Op | `insert_one` |
| Classificazione V1 | `SERVER_BOUND_BY_PRODUCER` |

---

## 3. Diff applicato

`ensure_server_scope` era **già importato** in `gvg.py` (linea 9, da SLC-F GVG WAR SCOPE). Patch:

```diff
  # Send mail
- await db.user_mail.insert_one({
+ await db.user_mail.insert_one(ensure_server_scope({
      "id": str(uuid.uuid4()),
      "user_id": uid,
      "subject": f"Guerra GvG {'Vinta!' if is_winner else 'Persa' if winner_id else 'Pareggio'}",
      "body": f"Risultato: {war['guild_a_name']} {score_a:,} vs {war['guild_b_name']} {score_b:,}\nI tuoi danni: {dmg:,}",
      "rewards": {"gold": gold, "gems": gems},
      "claimed": True,
      "timestamp": datetime.utcnow(),
- })
+ }, uid))
```

**Diff metrics**: 2 righe modificate, net delta 0 LOC.

---

## 4. Cosa NON è cambiato

| Aspetto | Status |
|---|---|
| Mail content (subject/body) | ❌ invariato |
| Recipient (`user_id`) | ❌ invariato |
| Inbox behavior (GET /api/mail) | ❌ invariato |
| GvG war logic / scoring / matching | ❌ invariato |
| Rewards (gold/gems) | ❌ invariato |
| Ranking / attack-defense | ❌ invariato |
| `gvg_wars` insert (già patchato in SLC-F) | ❌ invariato |

---

## 5. Validator + Rollback

| Tipo | Path |
|---|---|
| Post-apply validator | `/app/backend/scripts/validate_v2_gvg_user_mail_scope.py` |
| Rollback script (testuale) | `/app/backend/scripts/rollback_v2_gvg_user_mail_scope.py` |

Rollback runnable via: `python3 /app/backend/scripts/rollback_v2_gvg_user_mail_scope.py`

---

## 6. Verdict

🟢 **`BLOCK_B_GVG_USER_MAIL_SCOPE_APPLIED_SAFE`**

# 120C — V6 BLOCK C — SERVER_PROFILES CANONICAL SCHEMA PROPOSAL

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V6`  
**Block**: C — `SERVER_PROFILES_CANONICAL_SCHEMA_PROPOSAL_PACK`  
**Verdict**: 🟢 `BLOCK_C_SERVER_PROFILES_SCHEMA_PROPOSAL_READY`  
**Modalità**: DESIGN/SCHEMA PROPOSAL ONLY

---

## 1. P0 sbloccati da V5 BLOCK_D

- ✅ P0: `server_profiles` collection canonical schema (proposta qui)
- ✅ P0: `users.active_server_profile_id` field (parte della proposta)

---

## 2. Collection proposal: `server_profiles`

**Server-bound**.

### Document shape

| Field | Type | Note |
|---|---|---|
| `_id` | ObjectId | auto |
| `id` | str uuid4 | canonical identifier exposed via API |
| `user_id` | str | FK users.id (account-wide) |
| `server_id` | str | 's1', 's2', ... |
| `profile_name` | str | display name within server |
| `created_at` | datetime | utcnow |
| `last_active_at` | datetime | utcnow |
| `is_archived` | bool | default `False` |
| `archive_reason` | str\|null | null se attivo |
| `slc_version` | str | 'v1' |

### Constraints

- Unique: `(user_id, server_id)`

### Indexes

| Name | Fields | Unique |
|---|---|---|
| `idx_user_server` | user_id, server_id | ✅ |
| `idx_user_active` | user_id, is_archived | ❌ |
| `idx_server_active` | server_id, is_archived | ❌ |

### Lifecycle

- **Creation**: `POST /api/account/server-profiles/create` (SLC-H endpoint, NOT YET IMPLEMENTED)
- **Selection**: `POST /api/account/server-profiles/select` → setta `users.active_server_profile_id`
- **Archive**: `is_archived` flip; preserva la history; **never hard-delete**

---

## 3. Users field proposal: `active_server_profile_id`

| Campo | Valore |
|---|---|
| Type | `str \| null` |
| Default | `null` |

### Migration strategy proposal

| Phase | Action |
|---|---|
| **0** (design only) | V6 BLOCK_C (questo pack), no code |
| **1** dual_write | nuovo codice scrive sia legacy `users.server` sia `active_server_profile_id`; reads continuano legacy |
| **2** dual_read | reads da `active_server_profile_id` con fallback `users.server` |
| **3** legacy_removal | `users.server` rimosso (V6 BLOCK_D plan) |

---

## 4. Affected runtime consumers (audit only)

| Endpoint | Impact |
|---|---|
| `GET /api/account` | Deve esporre entrambi durante dual_*/dual_read |
| `POST /api/server/select` (legacy) | BLOCKED per removal (V6 BLOCK_D plan) |
| Tutte le callsite `ensure_server_scope` (24 ora attive) | Già `server_id`-aware, nessun cambio richiesto |

---

## 5. Acceptance criteria per implementation pack

1. Collection creata con i 3 indici canonical
2. `users.active_server_profile_id` introdotto (default null)
3. Dual-write attivato per compatibilità
4. `SERVER_PROFILES_RUNTIME_ENABLED` resta **FALSE** fino a phase_2 complete
5. Rollback script per ogni fase

---

## 6. Verdict

🟢 **`BLOCK_C_SERVER_PROFILES_SCHEMA_PROPOSAL_READY`**

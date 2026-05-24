# 122D — V8 BLOCK_D — LEGACY_SERVER_SELECT_DUAL_ROUTE_DESIGN

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V8`  
**Block**: D  
**Mode**: `design_doc_only`  
**Verdict**: 🟢 `BLOCK_D_LEGACY_SERVER_SELECT_DUAL_ROUTE_DESIGN_READY`  
**Rollback**: N/A (doc-only, nessuna runtime mutation)

---

## 1. Scopo

Definire la **strategia di compatibilita' dual-route** tra l'endpoint legacy `POST /api/server/select` e il futuro SLC-H endpoint `POST /api/server-profiles/select` su collezione `server_profiles`. **Design only**: nessuna implementazione, nessun feature flag attivato.

## 2. Upstream

- V6 BLOCK_D: removal plan 4-fasi (`120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md`)
- V7 BLOCK_A: Phase 1 deprecation notice **applied** (logger `divine.deprecation`)

## 3. 4-Phase Dual-Route Strategy

### Phase 1 — Deprecation Notice (APPLIED in V7)

- Status: ✅ **APPLIED V7 BLOCK_A**
- Behavior: WARNING-level log su ogni chiamata legacy; logica selezione invariata.

### Phase 2 — Dual-Route Compat (DESIGNED in V8)

| Aspetto | Spec |
|---|---|
| New route | `POST /api/server-profiles/select` |
| Legacy route | `POST /api/server/select` (mantenuto) |
| Response shape | identica tra i 2 endpoint (back-compat strict) |
| Source of truth | new route: `server_profiles.active`; legacy: `users.server` |
| Dual-write | new route scrive su `server_profiles` E mirror su `users.server` |
| Fallback | se `server_profiles` missing/empty per user → fallback a `users.server` con log `fallback_used` |

#### Response common shape
```json
{
  "success": true,
  "server": {"id": "...", "name": "...", "status": "..."}
}
```

#### Estensione opzionale solo new route
```json
{
  "server_profile_id": "...",
  "is_archived": false
}
```

### Phase 3 — Legacy Removal (DESIGNED)

Preconditions:
1. server_profiles collection popolata per tutti gli active users (apply pack V8 BLOCK_A eseguito)
2. Unique index `(user_id, server_id)` live e verificato
3. `divine.deprecation` log mostra **< 0.1% legacy calls/day per 7 giorni consecutivi**
4. Frontend migrato a `/api/server-profiles/select` OPPURE proxy in place
5. Esplicita autorizzazione utente per rimozione
6. Rollback path: legacy route conservata in `/app/backend/_attic/legacy_server_select.py`, re-add via single commit

Removal method: prima sostituire body con **HTTP 410 GONE** (legacy_sunset phase, una release), poi rimuovere la route.

### Phase 4 — users.server Field Drop (DESIGNED)

Preconditions:
1. Phase 3 completata per ≥ 1 release cycle
2. Zero read path su `users.server` ovunque nel backend
3. Backfill da `server_profiles` confermato authoritative

Action: drop `users.server` field via background migration (pack ops separato).

## 4. Fallback Policy Matrix

| Condizione | Azione |
|---|---|
| server_profiles missing | new route 503; legacy invariata |
| server_profiles vuoto per user | new route fallback su `users.server`; log `fallback_used` |
| Entrambi missing | new route 404 |
| Entrambi presenti, conflict | server_profiles vince; log `conflict_resolved_via_server_profiles`; legacy NON auto-aggiornata (reconcile manuale) |

## 5. Feature Flags referenced (non introdotti)

| Flag | Current | Required for |
|---|---|---|
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | Phase 2 |
| `SERVER_PROFILES_DUAL_WRITE_ENABLED` | unset (NOT introduced) | Phase 2 |
| `LEGACY_SERVER_SELECT_SUNSET_410` | unset (NOT introduced) | Phase 3 |

## 6. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Endpoint implementation | ❌ No |
| Route removal | ❌ No |
| Server selection behavior change | ❌ No |
| Second server | ❌ No |
| Feature flag enable | ❌ No |
| Frontend/UI change | ❌ No |

## 7. Cosa sblocca

Questo design **canonicalizza** la Phase 2/3/4 del removal plan V6 BLOCK_D. Una volta che V8 BLOCK_A apply ops pack avra' creato la collezione, sara' possibile implementare il new route in un pack `SERVER_PROFILES_DUAL_ROUTE_IMPLEMENTATION_PACK` autorizzato.

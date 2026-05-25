# 152A — Track A: `/servers` UI Legacy Usage Audit

**Verdict:** `TRACK_A_SERVER_UI_LEGACY_USAGE_AUDIT_READY` · audit-only

## Route file
- `/app/frontend/app/servers.tsx` (81 LOC)
- MD5: `26f5c796425aafa933f46979928165f4`
- Linked dal menu "Altro → Seleziona Server"

## API calls effettivi (2 — entrambi legacy)
| line | method | endpoint | mutation | target |
|---|---|---|---|---|
| 15 | GET | `/api/servers` | NO | list servers + load percent |
| 20 | POST | `/api/server/select` | **YES** | `users.server` field |

## UX evidence
- Alert.alert('Server Selezionato!', 'Benvenuto!') alla success → implica switching attivo.
- Nessun handling 503 dedicato.
- Nessun riferimento a `/api/server-profiles/select` in alcun file frontend.

## Risk
- **HIGH** — player-visible, mutation reale, zero fallback al nuovo endpoint.

## Recommendation
Lockare la UI come `SafeFeatureCard` o nascondere dal menu PRIMA di qualsiasi seed/migration di `server_profiles`.

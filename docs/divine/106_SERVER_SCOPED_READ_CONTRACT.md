# v106 — Server-Scoped Read Contract

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_server_scoped_read_contract_v1.json`
**Implementation packs**: v107, v108, v109

## Feature flag

`server_scoped_runtime_enabled` (default **false**).

## Endpoints (11 contract_only)

| Method | Path | Query | Filter | Pack |
|---|---|---|---|---|
| GET | `/api/server-profiles/current` | — | account_id + server_id (JWT + AS) | v106 |
| POST | `/api/server-profiles/select` | `{server_id}` | none | v107 |
| GET | `/api/user/heroes` | `server_id` | `(account_id, server_id)` | v107 |
| GET | `/api/team/get-formation` | `server_id` | `(account_id, server_id)` | v107 |
| GET | `/api/inventory` | `server_id` | `(account_id, server_id)` | v107 |
| GET | `/api/currencies` | `server_id` | split soft/hard | v107 |
| GET | `/api/story/progress` | `server_id` | `(account_id, server_id)` | v107 |
| GET | `/api/tower/progress` | `server_id` | `(account_id, server_id)` | v108 |
| GET | `/api/arena/profile` | `server_id` | `(account_id, server_id)` | v108 |
| GET | `/api/guild/membership` | `server_id` | `(account_id, server_id)` | v109 |
| GET | `/api/chat/messages` | `server_id, channel` | `(server_id, channel)` | v109 |

## Validation rules

- `server_id` required quando flag enabled.
- `server_id` deve corrispondere a profilo esistente o essere eligible per starter.
- Missing `server_id` con flag enabled → HTTP 400 `server_id_required`.
- Unknown `server_id` → HTTP 404 `server_not_found`.

## Fallback (flag disabled)

- Read account-wide come oggi.
- Banner obbligatorio `SERVER_DATA_ISOLATION_BACKEND_PENDING` (v104).

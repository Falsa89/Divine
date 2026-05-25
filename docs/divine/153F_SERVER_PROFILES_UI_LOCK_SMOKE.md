# 153F — Server Profiles UI Lock Smoke

**Verdict:** `TRACK_F_SERVER_PROFILES_UI_LOCK_SMOKE_READY`

## File smoke
- `servers.tsx` esiste · post-MD5 `c556dd20…`
- Menu (`menu.tsx`) punta ancora a `/servers` (invariato, MD5 `f3108ff3…`)
- `SafeFeatureCard` importato

## Forbidden substrings nel nuovo `servers.tsx`
| substring | count |
|---|---|
| `/api/server/select` | 0 |
| `selectServer` | 0 |
| `select_server` | 0 |
| `Server Selezionato!` | 0 |
| POST a `/api/server-profiles/select` | 0 |

## API smoke post-pack
- `GET /api/heroes` len=100 ✅
- `GET /api/heroes/primordial_gaia` = 404 ✅
- `GET /api/heroes/borea` = 200 ✅
- `GET /api/heroes/greek_borea` = 200 ✅
- `GET /api/server-profiles/select` = 503 ✅
- `POST /api/server-profiles/select` = 503 ✅
- `GET /api/servers` = 200 ✅
- `GET /api/health` = 200 ✅

## DB state
- writes_executed: 0
- users.server field writes: 0

# 95 — Real Formation Runtime Fetch

## Pack

`MEGA_RELEASE_ACCELERATION_44_v95`

## Stato attuale

Il backend non espone ancora `/api/team/get-formation` (404). Di conseguenza il real formation runtime fetch è marcato:

- `verdict = CONDITIONAL`
- `release_candidate_flag = BLOCKER_FOR_RELEASE_CANDIDATE`

La pre-battle lobby NON spaccia il fallback per formazione reale: la UI mostra esplicitamente la source attiva e il flag `fallback_used`.

## Chain di risoluzione implementata

```
saved_formation
   ↓ (se non disponibile)
local_cached_formation
   ↓ (se non disponibile)
safe_fallback_formation
```

UI label visibile in `frontend/app/pre-battle-lobby.tsx`:

```
Il Tuo Team · source: {playerFormation.source}
{playerFormation.fallback_used ? ' · fallback_used=true' : ''}
```

## Cosa serve in v96 per chiudere il blocker

- Esporre `/api/team/get-formation` (read-only, no DB writes).
- `pre-battle-lobby.tsx` deve fare fetch dell'endpoint e settare `source = saved_formation` quando i dati sono validi.
- `local_cached_formation` deve essere ottenuto da AsyncStorage come step intermedio prima del fallback.

## Safety

- `db_writes = 0`
- Nessuna mutazione team / roster / Character Bible.

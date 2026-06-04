# 93 — Real Formation Source and Team Editor Wiring (v93)

## Pack
`MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK_v93`

## Real Formation Source
La pre-battle lobby ora distingue 3 fonti:
- `saved_formation` (API `/api/team/get-formation` se safe)
- `local_cached_formation` (AsyncStorage opzionale)
- `safe_fallback_formation` (locale deterministic, etichettato come fallback)

La label e' visibile in UI. Quando `fallback_used=true` viene mostrato esplicitamente.

v93 NON applica scritture/mutazioni alla formazione.

## Team Editor Wiring
Il bottone Modifica Team routa a `/(tabs)/battle` (formation editor esistente):
- 3 colonne Support/DPS/Tank x 3 row
- drag heroes nella griglia 9-cell
- salva via `/api/team/update-formation` (endpoint pre-esistente)

Nessun blocker, nessuna nuova mutation. Wiring confermato OK.

## Safety
- db_writes=0
- reward_live=false
- formation_mutation_from_v93=false

# 86 · Playable Mode Visual Battle Routing — Audit

## Stato prima di v86
- Training, Story, Boss, Tower, Event, Arena: tutte le preview erano stub statici o timeline mock.
- Nessun runner visuale comune locale.
- Nessun payload deterministico riusabile per più modalità.

## Target v86
- Route unica condivisa: `playable-mode-battle-preview`.
- Payload deterministico per ogni modalità (team, nemici, timeline azioni preview).
- Label UI obbligatorie: `PREVIEW`, `LOCAL`, `NOT LIVE REWARD`, `NON AUTHORITATIVE`.
- Nessun reward live, nessun DB write, nessun endpoint live, nessun wiring autoritativo a `battle_engine.py`.

## Constraint hard
- `db_writes=0`
- `reward_live=false`
- `endpoint_live=false`
- `battle_engine_authoritative=false`
- Nessuna modifica MD5 dei file lockati.

# v105 — Battle Launch Contract Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_battle_launch_contract_audit_v1.json`

## Contract Target

```json
{
  "server_id": "<string>",
  "mode": "story|tower|arena|training|boss|raid|event|guild_war",
  "encounter_id": "<string>",
  "player_team_id": "<string>",
  "player_team_snapshot": [],
  "enemy_source_type": "authored|player_team|bot_team|boss|training_preset",
  "enemy_source_id": "<string>",
  "reward_policy": "none|preview|live_gated|live",
  "progress_policy": "none|preview|live_gated|live",
  "battle_engine_mode": "preview|authoritative",
  "idempotency_key": "<string>"
}
```

## Stato corrente

- `combat.tsx`: renderer reale, ma **non valida** `server_id`, `mode`, `encounter_id`, `enemy_source`, `reward_policy`, `progress_policy`, `idempotency_key`.
- `pre-battle-lobby.tsx`: presente ma **non produce** payload conforme.
- `visual-battle-preview-router.tsx`: routing preview, **non launcher**.
- `story.tsx`: usa **auto-resolve** `/api/story/battle`.
- `/api/battle/simulate`: **non autoritativo**, **non idempotente**, non accetta `server_id`/`mode`/`encounter_id`.
- ~10 surface lanciano battle preview con shape diversi.

## Gap principali

1. Nessun launcher centrale conforme al contract.
2. `combat.tsx` non valida i campi del contract.
3. Backend `/api/battle/simulate` non authoritative né idempotente.
4. Story by-passa il renderer reale con auto-resolve.
5. Surface multiple lanciano combat con payload divergenti.

## Required Fix Pack

**v107 Battle Launch Contract Unification + pre-battle-lobby**

Deliverables minimi:
- Schema `launch_context` v1 enforced in `combat.tsx`.
- `pre-battle-lobby` produce payload canonico.
- Endpoint `/api/battle/launch` authoritative + idempotente.
- Deprecazione `/api/story/battle` auto-resolve.

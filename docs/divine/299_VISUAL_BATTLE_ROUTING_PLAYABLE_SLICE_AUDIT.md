# 299 — Visual Battle Routing Playable Slice Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51`
**Track**: C
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION`
**Contract**: `visual_battle_routing_playable_slice_audit_v1`

## Policy
Tutte le battaglie utente-visibili devono mostrare la battaglia visiva, dove
possibile. **Guild War** è l'unica eccezione che consente autoresolve, ma deve
fornire un **replay link** obbligatorio.

## Modes (8)
| Mode | Visual required | Autoresolve | Replay link |
|---|---|---|---|
| story | true | false | false |
| material_raid | true | false | false |
| tower | true | false | false |
| arena | true | false | false |
| guild_war | false | **true** | **true** |
| training | true | false | false |
| event | true | false | false |
| boss | true | false | false |

## Garanzie
- `battle_engine.py` UNCHANGED
- `combat.tsx` / `story.tsx` UNCHANGED
- `/api/battle/simulate` / `/api/story/battle` UNCHANGED
- design-only, no runtime mutation

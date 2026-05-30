# 207A — FORGE SURFACE AUDIT

**Track**: A | **Verdict**: `TRACK_A_FORGE_SURFACE_AUDIT_READY`

## Legacy forge route presenti

| Path | Handler | DB writes |
|---|---|---|
| `GET /forge` | `get_forge_info` | NO |
| `POST /forge/upgrade` | `forge_upgrade` | **SÌ** (gold, equipment level/stats) |
| `POST /forge/fuse` | `forge_fuse_equipment` | **SÌ** (delete fodder, update base rarity/stats) |
| `GET /runes` | `get_runes` | NO |
| `POST /runes/craft` | `craft_rune` | **SÌ** (gold, runes insert) |

## Guards presenti su `/forge/fuse`

- auth_required ✅
- ownership (`user_id` filter) ✅
- base_not_in_fodder ✅
- rarity_cap_check ✅
- min_fodder_count ✅

## Guards MANCANTI (blockers per commit nel nuovo pack)

- `check_fodder_equipped_to` ❌
- `check_fodder_locked_or_favorite` ❌
- `check_base_not_in_active_team` ❌
- `check_protected_or_seasonal` ❌
- `transactional_atomicity_across_fodder_deletes` ❌
- `explicit_deterministic_result_envelope` ❌
- `negative_balance_pre_check_atomic` ❌

## Decisione

**`PREVIEW_ONLY_NEW_NAMESPACE`** — il legacy `/forge/*` resta intatto, il nuovo `/api/gear-forge/*`
è preview-only e gated.

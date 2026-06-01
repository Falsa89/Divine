# 253 — MEGA_ECONOMY_SAFETY_ACCELERATION_4_BATTLE_PASS_AND_MAIL_CLAIM_HARDENING_PACK_v40

**Phase**: MEGA_BATCH_ECONOMY_SAFETY_ACCELERATION_4

## Milestone

Questo pack chiude **gli ultimi 2 placeholder** del registry economy safety
v3:

- `battle_pass_reward_claim`
- `mail_reward_claim`

Dopo questo commit, **tutte le 8 operation_family** hanno un preview-only
safety layer attivo (registry v4 con
`all_8_operation_families_have_preview_safety_layer = true`).

## Tracks

### Track A — PROJECT_BATTLE_PASS_REWARD_CLAIM_SAFETY_HARDENING_PACK

Vedi doc 251.

### Track B — PROJECT_MAIL_REWARD_CLAIM_SAFETY_HARDENING_PACK

Vedi doc 252.

### Track C — PROJECT_REWARD_CLAIM_ECONOMY_SAFETY_REGISTRY_v4

Registry `reward_claim_economy_safety_registry_v4.json` (version=4,
supersedes v3). 8 op families con safety layer attivo:

1. `gem_socket_commit` (v37_track_a)
2. `material_raid_claim` (v37_track_b)
3. `gear_forge_fusion_commit` (v38_track_a)
4. `rune_scroll_talisman_commit` (v38_track_b)
5. `artifact_upgrade_commit` (v39_track_a)
6. `divine_weapon_upgrade_commit` (v39_track_b)
7. **`battle_pass_reward_claim` (v40_track_a) — NUOVO**
8. **`mail_reward_claim` (v40_track_b) — NUOVO**

Global: `all_8_operation_families_have_preview_safety_layer=true`,
`live_commit_allowed_in_this_pack=false`,
`live_claim_allowed_in_this_pack=false`, `db_writes=0`,
`reward_grant_enabled=false`, `premium_currency_used=false`,
`bp_delta_runtime_enabled=false`.

## Suite runner — tuple OPTIONAL registrate (count=1 ciascuna)

- `PROJECT-BATTLE-PASS-CLAIM-SAFETY-HARDENING`
- `PROJECT-MAIL-CLAIM-SAFETY-HARDENING`
- `MEGA-ECONOMY-SAFETY-ACCELERATION-4-v40-ROLLUP`

## server.py LOUD block

`PUBLIC_CONTENT_REGISTRATION_v40_BATTLE_PASS_AND_MAIL_CLAIM_SAFETY_LOUD`
aggiunto in `backend/server.py` con 2 imports + 2 `include_router` (count=1
ciascuno).

## Invarianti globali

- `db_writes = 0`
- 0 reward grant live (BP o Mail)
- 0 mutazioni inventory/materials/currency/user wallet
- 0 modifiche a `frontend/app/battlepass.tsx` (MD5 locked)
- 0 modifiche a `frontend/app/vip.tsx` (MD5 locked)
- 0 modifiche a `backend/routes/artifacts.py` (MD5 locked)
- 0 modifiche a `backend/battle_engine.py` / `backend/.env`
- 0 modifiche a Character Bible / hero final_numbers
- 0 BP Delta runtime trigger
- 0 mail read/delete/claim state mutation
- 0 premium BP unlock / purchase / VIP / shop / IAP mutation

## Caveat suite runner pubblico

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.

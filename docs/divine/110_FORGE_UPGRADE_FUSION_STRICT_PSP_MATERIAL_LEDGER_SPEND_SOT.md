# 110 — Pack 105 SOT (Source Of Truth)
## FORGE / UPGRADE / FUSION STRICT — PSP MATERIAL LEDGER SPEND

> Documento canonico Pack 105: upgrade equipment + forge craft + equipment fusion strict
> con PSP material storage e ledger spend.

## Strict keys

| Risorsa | Chiave server-scoped |
|---|---|
| material balance | `user_id + server_id + material_id` (su `player_server_profiles.materials`) |
| equipment ownership | `user_id + server_id + equipment_instance_id` |
| upgrade idempotency | `user_id + server_id + equipment_id + idempotency_token` |
| forge craft idempotency | `user_id + server_id + recipe_id + idempotency_token` |
| fusion idempotency | `user_id + server_id + base_equipment_id + idempotency_token` |

## PSP Material Storage Schema

Nuovo campo su `player_server_profiles`:

```
materials: {
  steel_ore: <int>,
  magic_dust: <int>,
  ancient_relic: <int>,
  phoenix_feather: <int>,
  crystal_shard: <int>,
}
```

Spend e grant via singolo `$inc` su `materials.<material_id>`. Server-scoped per definizione.
Nessuna mutation su `user_materials` legacy account-wide.

## Endpoints Pack 105

* `POST /api/economy/strict/forge/preflight?server_id=<sid>` — 200 OK con readiness map (non più 503).
* `GET  /api/economy/strict/forge/catalog`
* `POST /api/economy/strict/equipment/upgrade?server_id=<sid>`
* `POST /api/economy/strict/forge/craft?server_id=<sid>`
* `POST /api/economy/strict/equipment/fusion?server_id=<sid>`

## Reward source registry additions (Pack 105)

* `equipment_upgrade_strict_claim`
* `forge_craft_strict_claim`
* `equipment_fusion_strict_claim`

Tutte ledger-gated, idempotency mandatory, per-source kill switch default OFF.

## Kill switches (default OFF)

| Env | Scope |
|---|---|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` | global ledger live |
| `ECONOMY_STRICT_WRITES_ENABLED` | economy strict family |
| `EQUIPMENT_UPGRADE_STRICT_ENABLED` | upgrade strict |
| `FORGE_CRAFT_STRICT_ENABLED` | forge craft strict |
| `EQUIPMENT_FUSION_STRICT_ENABLED` | equipment fusion strict |

Ogni endpoint mutating Pack 105 gata su **triple AND** dei rispettivi kill switch.

## Server-Side Cost/Recipe Catalog

File: `backend/data/forge_strict_catalog_v1.py`

* `UPGRADE_COST_CATALOG_V1`: livelli 2-10 espliciti + lvl 11-30 calcolati (1.5x lvl-10 base).
* `FORGE_RECIPE_CATALOG_V1`: 3 ricette (`iron_sword_recipe`, `steel_armor_recipe`, `magic_amulet_recipe`).
* `FUSION_REQUIREMENT_CATALOG_V1`: requisiti per rarity 2-6 (fodder_count, stat_boost_pct, cost).
* `ALLOWED_MATERIALS`: 5 materiali whitelisted.
* `MAX_EQUIPMENT_LEVEL_STRICT = 30`.
* `MAX_EQUIPMENT_RARITY_STRICT = 6`.

Client cost/recipe/grant payload IGNORATO.

## Forbidden in Pack 105 strict paths

* silent `server_id="s1"`
* account-wide `wallets`/`user_materials`/`user_fragments` writes
* `users.gold/users.gems/users.experience` mutation
* hard/premium currency grant (gems esplicitamente bloccato)
* client-supplied reward payload / client-supplied cost/recipe trust
* non-idempotent repeat upgrade/craft/fusion
* cross-server consume/grant/equip/upgrade/fusion
* IAP / gacha / real-money payment
* `reward_live_general=true`
* `release_readiness_claimed=true`

## Frontend guard

* `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED` default `'false'`
* `EconomyStrictConsumer.tsx` aggiornato per mostrare anche health/catalog Pack 105 read-only
* Nessun POST mutating dall'UI utente

## Safety summary

- reward_live_general=false
- release_readiness_claimed=false
- premium_grants=false
- no_iap_gacha_payment=true
- no_account_wide_writes=true
- no_cross_server=true
- no users.gold/users.gems/users.experience mutation
- Pack 91-104 preservati (rollup verdi)
- PSP material storage server-scoped

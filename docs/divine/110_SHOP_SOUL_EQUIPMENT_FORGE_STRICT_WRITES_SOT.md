# 110 — Pack 104 SOT (Source Of Truth)
## SHOP / SOUL FORGE / EQUIPMENT / FORGE STRICT WRITES

> Documento canonico delle write path economy/progression del Pack 104.

## Strict keys

| Risorsa | Chiave server-scoped |
|---|---|
| currency/inventory | `user_id + server_id + item_id/currency_id` |
| equipment ownership | `user_id + server_id + equipment_instance_id` |
| equipped state | `user_id + server_id + hero_instance_id + slot` |
| soul forge retire | `user_id + server_id + hero_instance_id + idempotency_token` |
| shop buy | `user_id + server_id + shop_id + item_id + purchase_key/idempotency_token` |

## Endpoints (Pack 104)

* `GET  /api/economy/strict/health`
* `GET  /api/economy/strict/shop/catalog`
* `POST /api/economy/strict/shop/buy?server_id=<sid>`
* `POST /api/economy/strict/soul-forge/retire?server_id=<sid>`
* `POST /api/economy/strict/equipment/equip?server_id=<sid>`
* `POST /api/economy/strict/equipment/unequip?server_id=<sid>`
* `POST /api/economy/strict/forge/preflight?server_id=<sid>` → 503 **DEFERRED**

## Reward source registry additions

* `shop_buy_strict_claim`
* `soul_forge_retire_strict_claim`
* `equipment_equip_strict_claim` (no reward grant)
* `equipment_unequip_strict_claim` (no reward grant)

Tutte ledger-gated, idempotency mandatory, per-source kill switch default OFF.

## Kill switches (default OFF)

| Env | Scope |
|---|---|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` | global ledger live |
| `ECONOMY_STRICT_WRITES_ENABLED` | economy strict family |
| `SHOP_BUY_STRICT_ENABLED` | shop buy strict |
| `SOUL_FORGE_RETIRE_STRICT_ENABLED` | soul forge retire strict |
| `EQUIPMENT_STRICT_WRITES_ENABLED` | equipment equip/unequip strict |
| `FORGE_STRICT_WRITES_ENABLED` | forge upgrade/fusion (deferred) |

Ogni endpoint mutating gata su **triple AND** dei rispettivi kill switch.

## Frontend guard

* `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED` default `'false'`
* `EconomyStrictConsumer.tsx` mostra solo read-only health + catalog quando flag ON
* Nessun POST mutating dall'UI utente (gli endpoint sono test-only via marker)

## Forbidden in strict write paths

* silent `server_id="s1"`
* account-wide fallback
* `users.gold/users.gems/users.experience` mutation
* hard/premium currency grant
* client-supplied reward payload / client-supplied price trust
* non-idempotent repeat purchases/retire/upgrade
* cross-server equip/retire/buy/upgrade
* IAP / gacha / real-money payment
* `reward_live_general=true`
* `release_readiness_claimed=true`

## Forge / Upgrade / Fusion — DEFERRED

Blockers onesti restituiti da `/api/economy/strict/forge/preflight`:

* `FORGE_UPGRADE_STRICT_DEFERRED`
* `EQUIPMENT_FUSION_STRICT_DEFERRED`

Motivazione: upgrade/forge/fusion legacy mutano `wallets`/`user_materials`/`users.*`
account-wide — richiedono ledger spend dedicato e schema PSP material storage prima di
essere abilitati. **Pack 104 NON li attiva.**

## Safety summary

- reward_live_general=false
- release_readiness_claimed=false
- premium_grants=false
- no_iap_gacha_payment=true
- no_account_wide_writes=true
- no_cross_server=true
- no users.gold/users.gems/users.experience mutation
- Pack 91-103 preservati (rollup verdi)

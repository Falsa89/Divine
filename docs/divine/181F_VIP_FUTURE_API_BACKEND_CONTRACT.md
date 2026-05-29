# 181F — VIP Future API & Backend Contract

**Track:** F — Future API & Backend Contract
**Verdict:** `TRACK_F_VIP_FUTURE_API_BACKEND_CONTRACT_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Vincoli pack
- `no_runtime_implementation_added_in_this_pack`: `true`
- `no_db_writes_in_this_pack`: `true`
- `vip_endpoints_remain_gated`: `true`

## Feature Flag Design (forced off)
```
VIP_PROGRESSION_ENABLED       = false
VIP_DAILY_CLAIM_ENABLED       = false
VIP_BENEFITS_RUNTIME_ENABLED  = false
VIP_GRANT_ENABLED             = false
VIP_CANARY_ONLY               = true
VIP_GLOBAL_DISABLED           = true
```

## Future Endpoints (design-only, 5 endpoint)

### 1. `GET /api/vip/status`
- **Purpose:** Read-only VIP status per authenticated user.
- **Auth required:** ✅ | **Role:** `player` | **Account-scoped:** ✅
- **Response shape:**
```json
{
  "user_id": "string",
  "vip_points": 0,
  "current_tier": 0,
  "next_tier": 1,
  "next_tier_threshold_placeholder": "<<VIP_TIER_1>>",
  "vip_points_to_next_tier": 0,
  "benefits_active": [],
  "locked": true
}
```

### 2. `POST /api/vip/claim-daily`
- **Purpose:** Claim daily Divine Crystal stipend per current VIP tier. Idempotente per UTC day.
- **Auth required:** ✅ | **Role:** `player`
- **Request:** `{ user_id, utc_day (YYYY-MM-DD), idempotency_key }`
- **Response:** `{ status: CLAIMED|ALREADY_CLAIMED|NO_TIER|FEATURE_DISABLED|TIER_GATED, crystals_granted, wallet_after }`
- **Forbidden grants in response:** `artifact_id`, `constellation_id`, `sigilli_premium`, `sigilli_targeted`, `hero_direct_grant`, `combat_stat_boost`, `pity_skip`.

### 3. `POST /api/vip/grant` (system_only)
- **Purpose:** Credit `vip_points` dopo verified purchase. NOT player-callable.
- **Auth required:** ✅ | **Role:** `system_only`
- **Request:** `{ user_id, linked_purchase_id, delta_vip_points, source=iap_purchase_paid_crystal_component, idempotency_key }`
- **Response:** `{ status: APPLIED|DUPLICATE|REJECTED|FEATURE_DISABLED, vip_points_after, new_tier }`

### 4. `POST /api/vip/revoke` (system_only)
- **Purpose:** Revoke `vip_points` dopo refund/chargeback/ASSN/RTDN.
- **Auth required:** ✅ | **Role:** `system_only`
- **Request:** `{ user_id, linked_purchase_id, delta_vip_points_negative, reason: REFUND|CHARGEBACK|FRAUD_REVERSE, idempotency_key }`
- **Response:** `{ status: REVOKED|DUPLICATE|REJECTED|FEATURE_DISABLED, vip_points_after, new_tier }`

### 5. `GET /api/vip/history`
- **Purpose:** Read-only `vip_points` ledger history per authenticated user.
- **Auth required:** ✅ | **Role:** `player`

## Idempotency Design
- `daily_claim_key`: `<user_id>:<utc_day>`
- `grant_key`: `<user_id>:<linked_purchase_id>`
- `revoke_key`: `<user_id>:<linked_purchase_id>:REVOKE`
- `reuse_returns_same_result`: `true`

## Error Modes (globali)
- `FEATURE_FLAG_DISABLED` → **HTTP 423**
- `DUPLICATE` → HTTP 200 (replay safe)
- `NOT_AUTHORIZED` → HTTP 403
- `USER_MISMATCH` → HTTP 403
- `NO_TIER` → HTTP 200 (informational)

## Premium Entitlement Source
- **Primary source:** `purchase_ledger` from PROJECT_SHOP_IAP_INTEGRATION (179D)
- **Product family filter:** `divine_crystal_pack`, `launch_support_pack`, `monthly_pass` (paid crystal stipend portion only)

## Verdict
`TRACK_F_VIP_FUTURE_API_BACKEND_CONTRACT_READY` — 5 endpoint design-only, feature flags forced off, idempotency completa, forbidden grants whitelisted, premium entitlement derivato da purchase_ledger 179D.

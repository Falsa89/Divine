# 180A — BATTLE PASS SURFACE AUDIT (Track A)

## Verdict
`TRACK_A_BATTLE_PASS_SURFACE_AUDIT_READY`

## Markers
```
PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_APPROVAL = true
PROJECT_ACCELERATION_MODE                          = BATTLE_PASS_SURFACE_MODERNIZATION_LOCKED_ONLY
```

## Frontend battlepass.tsx
- MD5: `54568b8cb75a07033f78ef6593aba839` (164 righe)
- Classificazione: **locked**
- Lock tokens presenti: `BP_LOCKED_V2 = true`, `BP_PREMIUM_BUY_LOCKED_V2 = true`
- Claim disabilitato ✅, Premium buy disabilitato ✅, Lock banner visibile ✅
- Nessun import IAP SDK / StoreKit / Play Billing / RevenueCat ✅

## Backend
- Router `backend/routes/economy.py` contiene endpoint legacy:
  - `GET /api/battlepass`
  - `POST /api/battlepass/claim/{level}`
  - `POST /api/battlepass/buy-premium`
  - `POST /api/battlepass/add-exp`
- Endpoint **gated dal frontend lock**: `BP_LOCKED_V2` short-circuita prima di ogni `apiCall`. Nessuna `apiCall` parte mai dal frontend.
- Nessun receipt/payment code sul backend.

## Surface correlate (still locked)
- `frontend/app/shop.tsx` → `SHOP_LOCKED_V2 = true`
- `frontend/app/item-shop.tsx` → `ITEM_SHOP_LOCKED_V2 = true`
- `frontend/app/vip.tsx` → `VIP_LOCKED_V2 = true`

## Locks verificati
```
bp_locked:                  ✅
bp_premium_buy_locked:      ✅
shop_locked:                ✅
item_shop_locked:           ✅
vip_locked:                 ✅
premium_banner_locked:      ✅
targeted_banner_locked:     ✅
artifact_banner_hidden:     ✅
constellation_banner_hidden:✅
legacy_post_artifact_423:   ✅
```

## Invarianti MD5
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
```

Output JSON: `data/design/battle_pass/bp_surface_audit_v1.json`

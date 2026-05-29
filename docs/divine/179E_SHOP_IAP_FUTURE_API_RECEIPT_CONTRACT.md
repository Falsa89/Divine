# 179E — SHOP IAP FUTURE API & RECEIPT CONTRACT (Track E)

## Verdict
`TRACK_E_SHOP_IAP_FUTURE_API_RECEIPT_CONTRACT_READY`

**Design-only**. Nessun endpoint runtime aggiunto. Nessun bottone live. Nessun receipt verification live.

## Endpoint futuri (design-only)

| Method | Path                              | Scopo                                                                  |
|--------|-----------------------------------|------------------------------------------------------------------------|
| GET    | `/api/iap/products`               | Catalog server-authoritative per il display client                     |
| POST   | `/api/iap/verify/apple`           | Valida JWS signed transaction StoreKit (iOS)                           |
| POST   | `/api/iap/verify/google`          | Valida purchase token Google Play Billing (Android)                    |
| POST   | `/api/iap/fulfill`                | Applica entitlement delta al wallet (idempotente, post-verifica)      |
| POST   | `/api/iap/refund-reconcile`       | Webhook Apple ASSN / Google RTDN (refund/revoke/chargeback)            |
| GET    | `/api/iap/history`                | Storico acquisti + refund del player (read-only)                      |

## Request/Response shapes
Vedi `data/design/shop_iap/shop_iap_future_api_receipt_contract_v1.json` per i campi precisi di ciascun endpoint.

## Error modes globali
```
INVALID_SIGNATURE        → 401
DUPLICATE_TRANSACTION    → 200 (idempotent)
UNKNOWN_PRODUCT_ID       → 400
USER_MISMATCH            → 403
REVOKED_OR_REFUNDED      → 410
REPLAY_DETECTED          → 409
FEATURE_FLAG_DISABLED    → 423
```

## Feature flags (design)
```
IAP_PRODUCTS_ENDPOINT_ENABLED:    false
IAP_VERIFY_APPLE_ENABLED:         false
IAP_VERIFY_GOOGLE_ENABLED:        false
IAP_FULFILL_ENABLED:              false
IAP_REFUND_RECONCILE_ENABLED:     false
IAP_HISTORY_ENABLED:              false
IAP_FULFILLMENT_CANARY_ONLY:      true
IAP_GLOBAL_DISABLED:              true
```

## Payload vietati in fulfillment
- Grant `artifact_id` / `constellation_id`
- Grant `sigilli_premium` / `sigilli_targeted`
- Grant `pity_skip` / `hero_direct` / `combat_stat_boost`

Output JSON: `data/design/shop_iap/shop_iap_future_api_receipt_contract_v1.json`

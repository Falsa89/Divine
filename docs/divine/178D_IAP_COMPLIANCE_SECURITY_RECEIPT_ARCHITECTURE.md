# 178D — IAP COMPLIANCE, SECURITY & RECEIPT ARCHITECTURE (Track D)

## Verdict
`TRACK_D_IAP_COMPLIANCE_SECURITY_RECEIPT_ARCHITECTURE_READY`

**Design-only**. Nessun SDK runtime. Nessun endpoint live receipt. Zero DB writes. Zero secrets in `.env`.

## iOS — StoreKit / App Store Connect (high-level)
1. Client richiede catalog (server design-only + StoreKit).
2. User seleziona product → StoreKit avvia payment.
3. Client ottiene JWS signed transaction.
4. Client POST a `POST /api/iap/verify_apple` (futuro).
5. Server valida via App Store Server API.
6. Idempotency check sul `transaction_id`.
7. Append `purchase_ledger` + `wallet_ledger`.
8. Server ritorna entitlement delta. Client refresh wallet cache.

## Android — Google Play Billing (high-level)
1. Client richiede catalog (server + Google Play Billing).
2. `BillingClient.launchBillingFlow`.
3. Client ottiene `purchase token`.
4. Client POST a `POST /api/iap/verify_google` (futuro).
5. Server valida via Google Play Developer API.
6. Idempotency check su `purchase token`.
7. Append ledger entries.
8. Server `acknowledge` / `consume` via Google Play Developer API.
9. Client refresh wallet cache.

## Server receipt verification (futuro)
Endpoint futuri (NON implementati):
- `POST /api/iap/verify_apple`
- `POST /api/iap/verify_google`
- `POST /api/iap/refund_webhook_apple`
- `POST /api/iap/refund_webhook_google`

Error modes:
- `INVALID_SIGNATURE` → 401
- `DUPLICATE_TRANSACTION` → 200 idempotent
- `UNKNOWN_PRODUCT_ID` → 400
- `USER_MISMATCH` → 403
- `REVOKED_OR_REFUNDED` → 410
- `REPLAY_DETECTED` → 409

## Purchase ledger schema (futuro)
Campi: `purchase_id, user_id, server_profile_id, platform, platform_transaction_id, product_id_real, product_id_internal, verification_status, verification_signature_hash, timestamp_utc, price_local, price_local_currency, price_usd_estimate, entitlement_delta_summary, linked_wallet_ledger_ids, refund_status, refund_at_utc`.

## Fraud / duplicate prevention
- Unique index su `(platform, platform_transaction_id)`.
- JWS + nonce + timestamp window.
- Bind Apple/Google account ↔ internal user_id.
- Rate limit: 60/min per user.
- Suspicious burst flag → manual review.

## Sandbox / test plan
- Apple sandbox + Google license tester accounts.
- Internal test track (no production).
- Futuro canary: `sfqa@test.com`, `test@test.com` (stessa pattern di Artifact Stage 8).
- Nessun real purchase in produzione fino al Release Gate (Stage 10).

## Compliance checklist (design principles)
- App Store: solo StoreKit per digital content.
- Google Play: solo Google Play Billing per digital content.
- Pricing locale completo al point-of-purchase.
- **Loot box odds disclosure** (gacha trasparente).
- Refund + restore purchases per non-consumable/sub.
- Privacy/Terms pre-purchase.
- GDPR/CCPA wallet data + retention paid history.

Output JSON: `data/design/iap/iap_compliance_security_receipt_architecture_v1.json`

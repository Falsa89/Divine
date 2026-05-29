# 179D — SHOP IAP WALLET / LEDGER / FULFILLMENT CONTRACT (Track D)

## Verdict
`TRACK_D_SHOP_IAP_WALLET_LEDGER_FULFILLMENT_CONTRACT_READY`

**Design-only**. Zero DB writes. Zero balance changes.

## Tassonomia wallet
| Currency                    | Scope         | Refundable | Note |
|-----------------------------|---------------|------------|------|
| `divine_crystals_paid`      | account-wide  | ✅         | IAP-bound; segue account Apple/Google |
| `divine_crystals_free`      | server-bound  | ❌         | Earnings di gameplay/event |
| `sigilli_standard/elem/sel` | server-bound  | ❌         | Mai paid sigilli premium/targeted |
| `event_currencies`          | server-bound  | ❌         | Retention until rerun |
| `gold`                      | server-bound  | ❌         | Homepage visibile |
| `exp_account`               | account-wide  | ❌         | Homepage visibile |

## Ordine spesa
- **Summon**: Sigilli prima, poi Cristalli Divini.
- **Cristalli Divini**: FREE prima, poi PAID.
- Override non consentito.
- Motivo: preserva refundability del paid balance + trasparenza conversione.

## Conversione Cristalli → Sigilli
Modal in banner con conferma esplicita. Mostra: amount source (split free vs paid), amount target, rate, cancel sempre disponibile. Vietato: auto-convert, ratio nascosta, silent paid-balance consumption.

## Wallet ledger (futuro)
- `collection_name_future`: `wallet_ledger`
- Append-only, server-authoritative.
- Index: `ix_uniq_idempotency` (unique), `ix_user_time`.
- Campi: `ledger_id, user_id, server_profile_id_or_null_if_account_wide, currency_key, delta, balance_after, reason, source, timestamp_utc, idempotency_key, linked_purchase_id, linked_refund_ledger_id`.

## Purchase ledger (futuro)
- `collection_name_future`: `purchase_ledger`
- Index: `ix_uniq_tx` (unique su `platform + platform_transaction_id`).
- Campi: `purchase_id, user_id, platform, platform_transaction_id, product_id_real, product_id_internal_mock, verification_status, timestamp_utc, price_local, price_local_currency, entitlement_delta_summary, linked_wallet_ledger_ids, refund_status, refund_at_utc`.

## Fulfillment contract
Server-side, post-verified-receipt:
1. verify JWS/purchase token
2. map verified product id → mock product id
3. compute entitlement delta
4. append `purchase_ledger` + `wallet_ledger` (atomico)
5. return delta al client
6. client refresh wallet cache

**Vietati**: client-side grant, client-side validation, double fulfillment senza idempotency, grant di artifact/constellation/premium/targeted.

## Refund / Revoke
Apple ASSN + Google RTDN + manual support. Append revoke ledger; ricomputa paid balance; **mai revocare gacha results già eseguiti**; flag review se refund>spend.

## Idempotency
Format key: `<user_id>:<product_id_internal_mock>:<platform_transaction_id>`. Reuse → stesso delta.

## IAP grants vietati in questo pack
```
hero_direct:                 ❌
artifact_direct:             ❌
constellation_direct:        ❌
sigilli_premium_or_targeted: ❌
combat_stat:                 ❌
pity_skip:                   ❌
```

Output JSON: `data/design/shop_iap/shop_iap_wallet_ledger_fulfillment_contract_v1.json`

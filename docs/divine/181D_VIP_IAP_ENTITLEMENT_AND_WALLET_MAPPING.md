# 181D — VIP IAP Entitlement & Wallet Mapping

**Track:** D — IAP Entitlement & Wallet Mapping
**Verdict:** `TRACK_D_VIP_IAP_ENTITLEMENT_AND_WALLET_MAPPING_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Accrual Rule
- **Regola:** 1 paid Divine Crystal granted via verified IAP = 1 `vip_point`
- **Ratio placeholder:** `<<VIP_POINTS_PER_PAID_CRYSTAL>>`
- **Source:** `purchase_ledger` entries con `product_id_internal_mock` ∈ {crystal_pack family, launch_support_pack family con paid crystals component, monthly_pass daily crystals stipend portion}
- **Forbidden sources:**
  - free Divine Crystals (`divine_crystals_free`)
  - event currencies
  - gameplay-earned currencies
  - in-banner Crystal→Sigilli conversion (no double-count)

## Product Family Mapping

| Product Family | Contributes to vip_points | Basis / Reason |
|---|---|---|
| `divine_crystal_pack` | ✅ | granted_paid_crystals_amount |
| `launch_support_pack` | ✅ | paid_crystals_component_only |
| `monthly_pass` | ✅ | daily_paid_crystals_stipend_actually_received |
| `summon_pack` | ❌ | sigilli grant, not paid crystals; avoid double-rewarding gacha + VIP |
| `cosmetic_pack` | ❌ | non-consumable cosmetic; vip_points only via paid crystals |
| `battle_pass` | ❌ | BP entitlement separate; design boundary |
| `vip_tier` | ❌ | VIP è marker derivato da spend, NON prodotto acquistabile direttamente |
| `offer_code_promo` | ❌ | promo codes are server-redeemed non-IAP |

## Ledger Design (future collection)
- **Collection:** `vip_points_ledger`
- **Append-only:** `true`
- **Server-authoritative:** `true`
- **Required fields:**
  - `vip_ledger_id`, `user_id`, `timestamp_utc`
  - `delta_vip_points`, `vip_points_after`, `new_tier`
  - `source`, `linked_purchase_id`, `linked_refund_ledger_id`
  - `idempotency_key`
- **Indici:**
  - `ix_uniq_vip_idempotency` — unique, fields=[`idempotency_key`]
  - `ix_user_time` — fields=[`user_id`, `timestamp_utc`]

## Refund / Revoke Behavior
- **Trigger sources:** Apple ASSN, Google RTDN, manual support
- **Action:** append revoke entry a `vip_points_ledger`; `delta_vip_points` negativo; tier ricalcolato on next read; **mai revocare daily stipend VIP già claimato** retroattivamente eccetto chargeback fraud
- **Tier demotion on refund:** ✅ consentita
- **Silent partial demotion:** ❌ vietata
- **Reason:** paying players non devono perdere tier randomicamente; solo refund/chargeback demote.

## Idempotency Design
- `vip_points_grant_key`: `<user_id>:<linked_purchase_id>`
- `vip_points_revoke_key`: `<user_id>:<linked_purchase_id>:REVOKE`
- `reuse_returns_same_result`: `true`

## Wallet Separation Policy
- `vip_points_are_not_a_spendable_currency`: `true`
- `vip_points_are_progression_marker_only`: `true`
- `vip_points_visible_in_treasury`: `true`
- `vip_points_homepage_visible`: `false` (homepage = solo Oro + Cristalli Divini + EXP Account, design 178/179)

## Server Authority (assoluta)
- `client_never_grants_vip_points`: `true`
- `client_never_recomputes_tier`: `true`
- `server_validates_all_iap_receipts_before_grant`: `true`
- `server_writes_all_vip_ledger_entries`: `true`

## Runtime
- `applies_to_runtime`: `false`
- `runtime_blocked_by`: `VIP_LOCKED_V2` (frontend) + future flag `VIP_GRANT_ENABLED=false`
- **DB writes in this pack:** `0`

## Verdict
`TRACK_D_VIP_IAP_ENTITLEMENT_AND_WALLET_MAPPING_READY` — Accrual rule, ledger schema, refund handling, idempotency, wallet separation completamente disegnati. Zero DB writes, server-authoritative end-to-end.

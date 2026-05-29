# 178C — IAP CURRENCY & WALLET CONTRACT (Track C)

## Verdict
`TRACK_C_IAP_CURRENCY_WALLET_CONTRACT_READY`

**Design-only**. Zero scritture DB. Zero pricing reale.

## Tassonomia valute
- `divine_crystals_free` — gameplay/event/login
- `divine_crystals_paid` — solo IAP, **refundable**
- `sigilli_standard / elemental / selective` — gachable
- `sigilli_premium / targeted` — **locked**
- `event_currency_<event_id>` — **retention until rerun** (non auto-expired)
- `soul_essence` — out-of-scope (proprietà Soul Forge)

## Paid vs Free
- **Balance separati**.
- Ordine spesa **FREE_FIRST_THEN_PAID**, override non consentito.
- Motivo: preservare refundability del paid balance.

## Conversione Cristalli Divini → Sigilli
- Surface: **modal in banner con conferma esplicita** (già approvata).
- Mostra: amount source, amount target, conversion rate, wallet snapshot pre-commit, paid vs free.
- Cancel sempre disponibile prima del commit.
- Banner consentiti: `standard`, `elemental`, `selective`.
- Banner vietati: `premium`, `targeted`, `artifact`, `constellation`.

## Ledger design (futuro `wallet_ledger`)
Append-only, server-authoritative. Campi: `ledger_id, user_id, server_profile_id, timestamp_utc, currency_key, delta, balance_after, reason, source, product_id_design, transaction_id_design, idempotency_key, refund_link_ledger_id`.
Reconciliation job daily: `sum(ledger) == wallet_snapshot`.

## Idempotency
Formato chiave: `<user_id>:<product_id>:<purchase_token_or_transaction_id>`. Richiesto per purchase, refund/revoke, event grants, crystal→sigilli conversion.

## Refund/Revoke
Apple ASSN + Google RTDN. Append revoke ledger, ricomputa paid balance. **Non revocare gacha results già spesi.**

## Server authority
Client mai concede currency. Client mai valida receipt. Server è single source of truth.

## Grants vietati in questo pack
```
hero_direct_grant:        ❌
artifact_direct_grant:    ❌
constellation_direct_grant: ❌
premium_targeted_sigilli: ❌
pity_skip:                ❌
combat_stat_boost:        ❌
```

Output JSON: `data/design/iap/iap_currency_wallet_contract_v1.json`

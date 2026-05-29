# 180E — BATTLE PASS FUTURE API & BACKEND CONTRACT (Track E)

## Verdict
`TRACK_E_BATTLE_PASS_FUTURE_API_BACKEND_CONTRACT_READY`

**Design-only**. Nessuna implementazione runtime aggiunta. Zero DB writes.

## Feature flags
```
BP_LIVE_PROGRESSION_ENABLED:  false
BP_LIVE_CLAIM_ENABLED:        false
BP_PREMIUM_BUY_ENABLED:       false
BP_SEASON_PUBLIC_ENABLED:     false
BP_CANARY_ONLY:               true
BP_GLOBAL_DISABLED:           true
```

## Endpoint futuri (design-only)
| Method | Path                                  | Role            | Account/Profile scope            |
|--------|---------------------------------------|-----------------|----------------------------------|
| GET    | `/api/battlepass/season`              | player          | account-wide                     |
| GET    | `/api/battlepass/progress`            | player          | server-profile scoped            |
| POST   | `/api/battlepass/claim`               | player          | server-profile scoped            |
| POST   | `/api/battlepass/premium/verify`      | player          | account-wide                     |
| POST   | `/api/battlepass/xp/add`              | system/admin    | server-profile scoped            |
| GET    | `/api/battlepass/history`             | player          | account-wide                     |

Vedi JSON per request/response shapes precisi.

## Auth & role
- Player: season, progress, claim, premium/verify, history.
- System/Admin: xp/add (system route, NOT player-callable).

## Idempotency
```
claim_key:           <user_id>:<season_id>:<level>:<track_id>
premium_verify_key:  <user_id>:<verified_purchase_id>:<season_id>
xp_add_key:          <user_id>:<source>:<source_ref>
```
Reuse → same result.

## Reward claim ledger (futuro)
- `bp_reward_claim_ledger` append-only server-authoritative.
- Index: `ix_uniq_bp_claim` unique `(user_id, season_id, level, track_id)`, `ix_user_season`.
- Campi: claim_id, user_id, server_profile_id, season_id, level, track_id, timestamp_utc, entitlement_delta_summary, linked_wallet_ledger_ids, idempotency_key, refund_link_revoke_ledger_id.

## Premium entitlement mapping
- Source: `purchase_ledger.product_id_internal_mock` matching `monthly_pass` o futuro `bp_premium_pack`.
- Future mock IDs: `mock.divinewaifus.bp.premium.season`, `mock.divinewaifus.bp.deluxe.season`.
- Real store IDs: Stage 2 di 178F roadmap.

## Refund/Revoke
- Apple ASSN + Google RTDN.
- Append revoke ledger.
- Downgrade track al prossimo claim o reconciliation.
- **Mai** revocare rewards già claimed retroactively (eccetto chargeback fraud).

## Season rollover
- Hard reset a end_utc.
- Unclaimed expire.
- Premium entitlement **non** carry-over.
- History preserved.

## Scope
- XP/progress: **server_profile_scoped**.
- Premium entitlement: **account_wide**.
- Motivo: premium segue account Apple/Google; progress per server profile.

## Forbidden grants in claim response
artifact_id, constellation_id, sigilli_premium, sigilli_targeted, pity_skip, combat_stat_boost, hero_direct_grant, pvp_rank_skip — tutti **vietati**.

Output JSON: `data/design/battle_pass/bp_future_api_backend_contract_v1.json`

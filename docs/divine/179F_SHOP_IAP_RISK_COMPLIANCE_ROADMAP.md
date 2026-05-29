# 179F — SHOP IAP RISK, COMPLIANCE & ROADMAP (Track F)

## Verdict
`TRACK_F_SHOP_IAP_RISK_COMPLIANCE_ROADMAP_READY`

## Risk register (sintesi)
| ID  | Rischio                                                | Mitigation                                                                 |
|-----|--------------------------------------------------------|----------------------------------------------------------------------------|
| R1  | Replay attack on receipt verification                 | JWS + nonce + timestamp window + unique index `(platform, tx_id)`         |
| R2  | Cross-account purchase abuse                          | Bind Apple/Google account a internal user_id al primo acquisto             |
| R3  | Refund-then-spend exploit                             | Refund never reverses gacha; flag refund/spend ratio                       |
| R4  | Hidden odds non-compliance                            | Loot box odds disclosure obbligatoria per ogni summon_pack card + banner   |
| R5  | P2W combat purchase pressure                          | Hard family ban (no stat boost / artifact / premium / pity skip)           |
| R6  | Server merge / multishard wallet split inconsistency  | Paid currency account-wide, free server-bound; documentato in SLC          |
| R7  | Sandbox leakage → production fulfillment              | Feature flags + canary-only fino al release gate                           |
| R8  | Real product IDs leaked in code prima del catalog stage | Static validator forbids `com.divinewaifus.*` / `dw_real_*` in product code|
| R9  | User confusion paid vs free Divine Crystals           | Tesoreria split + conversion modal split                                   |
| R10 | Suite stale-push of validator runner                  | Tripled-sentinel (top tag + inline sentinel + proof marker JSON separato)  |

## Compliance checklist
- Apple StoreKit only su iOS / Google Play Billing only su Play.
- Pricing locale reale e completo al point-of-purchase.
- Loot box odds disclosure (per summon_pack card + per banner card).
- Refund / restore UX al Stage 8 della roadmap.
- Privacy/Terms pre-purchase.
- GDPR/CCPA wallet export + paid history retention.
- No dark patterns, no countdown < 60s, no surprise random charge.

## Allineamento con 178F roadmap
- **Questo pack** estende lo Stage 1 di 178F al contratto Shop↔IAP.
- **Prossimo Stage** (2): `PRODUCT_ID_MOCK_CATALOG` (allocate real Apple/Google product IDs).
- **Stage successivi** (3-10): purchase ledger schema dry-run, verify endpoint design-only DEV, sandbox StoreKit/Play Billing, canary fulfillment (stesso pattern Stage 8 artifact: sfqa + test), refund/revoke test, public shop IAP UI, pricing/localization signoff, release gate.

Output JSON: `data/design/shop_iap/shop_iap_risk_compliance_roadmap_v1.json`

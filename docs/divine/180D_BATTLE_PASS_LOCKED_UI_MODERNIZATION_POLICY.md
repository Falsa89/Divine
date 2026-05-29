# 180D — BATTLE PASS LOCKED UI MODERNIZATION POLICY (Track D)

## Verdict
`TRACK_D_BATTLE_PASS_LOCKED_UI_MODERNIZATION_POLICY_READY`

## Frontend modificato in questo pack?
**NO.** `frontend/app/battlepass.tsx` MD5 invariato (`54568b8cb75a07033f78ef6593aba839`).

**Motivo**: questo pack è il **design contract** per la futura modernizzazione. L'implementazione UI vera segue in un sub-pack dedicato con autorizzazione esplicita a toccare il file. Mantenere MD5 unchanged = rischio zero di regression.

## Future implementation — changes ALLOWED (con autorizzazione esplicita)
- Modernizzare copy locked: "Divine Pass / Patto Divino"
- Chiarire "in preparazione" con copy ETA-free
- Mostrare cards Free / Premium / Deluxe side-by-side (no purchase, no claim)
- Display placeholder reward icons + `<<TIER_X>>` (no live price)
- Link da Premium card a `/shop` preview (still locked)
- Accessibility: min touch target 44pt iOS / 48dp Android
- Mobile layout: SafeAreaView + ScrollView, no fixed positioning
- Loot box odds disclosure adiacente a summon-related rewards (link a banner)

## Future implementation — changes FORBIDDEN
- Active BUY/ACQUISTA button
- Active claim button bypassing `BP_LOCKED_V2`
- `apiCall` a `/api/battlepass/claim` o `/api/battlepass/buy-premium` quando locks sono true
- IAP SDK import
- Real product ID literal in codice
- Direct ledger write
- Countdown < 60s
- Hidden price / odds
- Removal o weakening di `BP_LOCKED_V2` / `BP_PREMIUM_BUY_LOCKED_V2`

## Locked state invariants (post-ANY future change)
```
BP_LOCKED_V2_must_remain_true:                ✅
BP_PREMIUM_BUY_LOCKED_V2_must_remain_true:    ✅
claim_button_disabled:                        ✅
premium_buy_button_disabled_or_hidden:        ✅
lock_banner_visible:                          ✅
no_live_api_call_on_press:                    ✅
```

## Copy proposals (IT)
| Element                  | Testo                                                                                  |
|--------------------------|----------------------------------------------------------------------------------------|
| Page title               | **Patto Divino**                                                                       |
| Lock banner              | Patto Divino — in preparazione. Nuovo contratto account-wide e sistema IAP in arrivo. |
| Free track label         | Cammino del Devoto (Free)                                                              |
| Premium track label      | Patto Divino Premium                                                                   |
| Premium track locked pill| Bloccato — in preparazione                                                            |
| Deluxe track label       | Patto Divino Eterno (Deluxe)                                                           |
| Deluxe track locked pill | Bloccato — in preparazione                                                            |
| Claim button (locked)    | Reclamabile presto                                                                     |
| Buy premium (locked)     | Disponibile presto                                                                     |
| Loot box odds link       | Vedi probabilità banner                                                               |

## Accessibility / Mobile
- Min touch target: 44pt iOS / 48dp Android.
- Screen reader labels presenti.
- High contrast locked pill color.
- SafeAreaView + ScrollView/FlashList; no fixed positioning; KeyboardAvoidingView non necessario (no input).

Output JSON: `data/design/battle_pass/bp_locked_ui_modernization_policy_v1.json`

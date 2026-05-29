# 179C — SHOP UI LOCK & PREVIEW POLICY (Track C)

## Verdict
`TRACK_C_SHOP_IAP_UI_LOCK_PREVIEW_POLICY_READY`

Shop e Item Shop restano **locked/preview** — nessun BUY/ACQUISTA live.

## Surface in scope
- `frontend/app/shop.tsx` (`SHOP_LOCKED_V2`)
- `frontend/app/item-shop.tsx` (`ITEM_SHOP_LOCKED_V2`)

## Stato lock richiesto
```
buttons_buy_or_acquista_disabled:  ✅ true
daily_claims_disabled:             ✅ true
lock_banner_visible:               ✅ true
redirect_to_paywall:               ❌ false
```

## Label/testo consentiti
- “In preparazione”
- “Preview”
- “Non acquistabile ora”
- “Prezzi non finali”
- “Sistema acquisti reali (IAP) in preparazione”
- “Negozio in revisione”
- “Anteprima informativa”

## Label/azioni vietati (live)
- “ACQUISTA ORA” (live), “BUY” (live), “Compra subito” (live)
- Aggiungi al carrello live
- Apertura StoreKit / Play Billing
- Redirect a checkout esterno
- Paywall popup silenzioso
- Countdown < 60s
- Hidden price / hidden odds

## Preview card contract
**Visibili**: mock label, family badge, price placeholder (es. `<<TIER_M>>`), descrizione currency in italiano, label lock esplicita.
**Vietati**: prezzo locale reale finalizzato, CTA buy attivo, countdown timer che triggera purchase.

## Loot box odds disclosure
- Card `summon_pack` → **deve** linkare a `banner_odds_modal` in `(tabs)/gacha.tsx`.
- Card `divine_crystal_pack` → può linkare odds (opzionale).

## Refund / Restore UI
Non visibili in questo pack. Appariranno allo Stage 8 della roadmap 178F (PUBLIC_SHOP_IAP_UI).

## Future unlock gate
- Marker: `PROJECT_SHOP_IAP_UI_LIVE_ROLLOUT_APPROVAL`
- Pack futuro: `PROJECT_SHOP_IAP_UI_LIVE_ROLLOUT_PACK`
- Rollback lever: ripristina `SHOP_LOCKED_V2=true` + `ITEM_SHOP_LOCKED_V2=true`.

Output JSON: `data/design/shop_iap/shop_iap_ui_lock_preview_policy_v1.json`

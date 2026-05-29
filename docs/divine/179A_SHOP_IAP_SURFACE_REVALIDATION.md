# 179A — SHOP IAP SURFACE REVALIDATION (Track A)

## Verdict
`TRACK_A_SHOP_IAP_SURFACE_REVALIDATION_READY`

Revalida fresca delle surface monetization rispetto al baseline 178.

## Markers
```
PROJECT_SHOP_IAP_INTEGRATION_APPROVAL = true
PROJECT_ACCELERATION_MODE             = SHOP_IAP_INTEGRATION_DESIGN_ONLY
```

## Drift check vs baseline 178
| Route                              | MD5 (current)                        | Drift |
|------------------------------------|--------------------------------------|-------|
| `frontend/app/shop.tsx`            | `1a39f50e8da9c09a1f0b017b25b73390`   | ❌    |
| `frontend/app/item-shop.tsx`       | `d09d616db14f4c6f98606e9ccd625379`   | ❌    |
| `frontend/app/treasury.tsx`        | `7dae97ac1530150e8270dfe6166bda24`   | ❌    |
| `frontend/app/(tabs)/gacha.tsx`    | `f68b9239cec04ea54879f0be381e772a`   | ❌    |
| `frontend/app/battlepass.tsx`      | `54568b8cb75a07033f78ef6593aba839`   | ❌    |
| `frontend/app/vip.tsx`             | `45fcc9890b6b128c37088bc33aa54caf`   | ❌    |
| `frontend/app/soul-forge.tsx`      | `b7659de11ac36f341e7a2f54fd29e6ed`   | ❌    |

## Locks verificati
- `SHOP_LOCKED_V2 = true` ✅
- `ITEM_SHOP_LOCKED_V2 = true` ✅
- `BP_LOCKED_V2 = true` + `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `VIP_LOCKED_V2 = true` ✅
- Premium/Targeted banner locked ✅
- Artifact/Constellation banner hidden ✅
- Legacy POST artifact/constellation → HTTP 423 ✅

## Currencies policy preservata
- Homepage: **Oro + Cristalli Divini + EXP Account**.
- Tesoreria: Sigilli, breakdown paid/free, event currencies.
- Summon: **Sigilli prima**, poi Cristalli Divini (conversione con conferma esplicita).
- Event currencies: **retained until rerun**, no auto-expire.

## Backend
- Nessun route `iap/receipt/purchase/billing` in `backend/routes/`.
- Nessun SDK pagamento in deps.
- `.env` invariato.

Output JSON: `data/design/shop_iap/shop_iap_surface_revalidation_v1.json`

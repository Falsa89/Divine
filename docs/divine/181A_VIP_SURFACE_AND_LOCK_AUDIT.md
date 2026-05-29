# 181A — VIP Surface & Lock Audit

**Track:** A — Surface & Lock Audit
**Verdict:** `TRACK_A_VIP_SURFACE_AND_LOCK_AUDIT_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Scope
Audit completo della superficie VIP (frontend `vip.tsx` + endpoint backend legacy) e verifica che tutti i lock restino attivi prima di disegnare il sistema di progressione spend-based.

## Frontend `frontend/app/vip.tsx`
- **MD5 corrente:** `45fcc9890b6b128c37088bc33aa54caf` (123 righe)
- **Classificazione:** `locked`
- **Lock tokens presenti:** `VIP_LOCKED_V2 = true`
- **Claim disabled:** `true` — `claimDaily` esegue short-circuit immediato senza mai chiamare `apiCall` finché `VIP_LOCKED_V2`
- **Buy button:** non visibile (VIP non è acquisto diretto)
- **Lock banner:** visibile
- **IAP SDK:** `false` (StoreKit/Google Play Billing/RevenueCat/react-native-iap/expo-in-app-purchases tutti non importati)

## Backend VIP endpoint legacy
- Router: `backend/routes/economy.py`
- Endpoint presenti: `GET /api/vip`, `POST /api/vip/claim-daily`
- **Reachable from frontend:** `false` — il frontend non li raggiunge mai a causa di `VIP_LOCKED_V2` short-circuit
- **IAP verified payment required:** `false`
- Nota: gli endpoint VIP legacy esistono ma sono completamente schermati dal frontend lock; nessuna mutazione possibile finché il flag client è true.

## Related Locked Surfaces (cross-check)
| Route | MD5 | Lock Token |
|---|---|---|
| `frontend/app/shop.tsx` | `1a39f50e8da9c09a1f0b017b25b73390` | `SHOP_LOCKED_V2 = true` |
| `frontend/app/item-shop.tsx` | `d09d616db14f4c6f98606e9ccd625379` | `ITEM_SHOP_LOCKED_V2 = true` |
| `frontend/app/battlepass.tsx` | `54568b8cb75a07033f78ef6593aba839` | `BP_LOCKED_V2 = true` + `BP_PREMIUM_BUY_LOCKED_V2 = true` |

## Unrelated Live Surfaces (must remain unchanged)
| Route | MD5 |
|---|---|
| `frontend/app/(tabs)/gacha.tsx` | `f68b9239cec04ea54879f0be381e772a` |
| `frontend/app/soul-forge.tsx` | `b7659de11ac36f341e7a2f54fd29e6ed` |

## Locks verified (10/10 ✅)
- `vip_locked`, `bp_locked`, `bp_premium_buy_locked`, `shop_locked`, `item_shop_locked`
- `premium_banner_locked`, `targeted_banner_locked`
- `artifact_banner_hidden`, `constellation_banner_hidden`
- `legacy_post_artifact_constellation_http_423`

## MD5 Invarianti baseline
- `backend/battle_engine.py` → `151ca35ad3bc35f0a6209cb3744ed440`
- `backend/.env` → `ff60bbb79efa329b71aa8ed351ea89b3`
- `backend/routes/artifacts.py` → `893f244d85fd45cbe825996463995293`

## Vincoli
- **DB writes:** `0`
- **Runtime changes:** `false`

## Verdict
`TRACK_A_VIP_SURFACE_AND_LOCK_AUDIT_READY` — Tutti i lock attivi, nessun IAP SDK importato, nessuna scrittura DB, nessun runtime change.

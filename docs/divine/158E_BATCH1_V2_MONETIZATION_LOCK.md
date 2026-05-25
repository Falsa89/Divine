# 158E — Shop / Item-Shop / Battle Pass / VIP Monetization Lock (Track E)

Verdetto: `TRACK_E_SHOP_BATTLEPASS_VIP_MONETIZATION_LOCK_IMPLEMENTED_SAFE`

## File modificati (UI lock only)
| File | Lock |
|---|---|
| `shop.tsx` | `SHOP_LOCKED_V2=true`: buy/claim_daily disabilitati, banner IN REVISIONE |
| `item-shop.tsx` | `ITEM_SHOP_LOCKED_V2=true`: buyMulti modal bloccato, badge 🔒 |
| `battlepass.tsx` | `BP_LOCKED_V2=true` + `BP_PREMIUM_BUY_LOCKED_V2=true`: claim/buy-premium disabilitati |
| `vip.tsx` | `VIP_LOCKED_V2=true`: claim daily disabilitato |

## Logica
La chiamata API mutativa rimane definita ma viene short-circuited subito (`if (LOCKED) return;`). Nessuna richiesta network parte dalle schermate finché i lock sono attivi.

## Vincoli
- 0 cambi prezzi/items/rewards/premium logic
- 0 IAP implementation
- 0 backend route changes
- 0 DB writes

La UI rimane visibile come **anteprima informativa** (cataloghi mostrati, stato VIP mostrato, livelli BP mostrati) finché il sistema IAP reale non è progettato e firmato.

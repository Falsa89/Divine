# 156E — Shop / IAP Readiness Audit (Track E)

Verdetto: `TRACK_E_SHOP_AND_IAP_READINESS_AUDIT_READY`

## Stato shop
- `frontend/app/shop.tsx` espone POST `/api/shop/buy` e `/api/shop/claim-daily/{itemId}` live.
- Nessun sistema IAP/real-money esistente.

## Sistemi mancanti per real-money
1. Configurazione prodotti IAP su App Store / Google Play
2. Validazione ricevute lato backend (StoreKit / Play Billing)
3. Anti-frode / replay protection
4. Separazione valuta pagata vs free nel ledger
5. Entitlement / ownership account-wide
6. Gestione refund / revoke
7. Compliance regionale (GDPR, COPPA, tasse)
8. Fallback purchase fallita + idempotenza retry

## Raccomandazione
**NON** implementare IAP in questo pack. Pack dedicato: `PROJECT_SHOP_IAP_DESIGN_AND_SAFE_SHOP_LOCK_PACK`. Nel frattempo: shop attuale potrebbe essere convertito in catalogo read-only.

## Vincoli rispettati
- Nessun cambio prezzi/items/claim, nessuna scrittura DB.

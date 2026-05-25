# 156F — Battle Pass Legacy Surface & Monetization Audit (Track F)

Verdetto: `TRACK_F_BATTLE_PASS_LEGACY_SURFACE_AND_MONETIZATION_AUDIT_READY`

## Superficie attuale
- `frontend/app/battlepass.tsx` espone:
  - `POST /api/battlepass/claim/{level}` (free)
  - `POST /api/battlepass/buy-premium` (premium, NON IAP-backed)
- UI percepita come legacy.

## Raccomandazioni
- Nascondere/lock del bottone `buy-premium` finché il sistema IAP non è progettato.
- Valutare lock del battle pass attuale fino a nuovo contratto account-wide.

Prossimo pack: `PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_PACK`.

## Vincoli rispettati
- Nessun cambio reward/premium behavior, nessuna scrittura DB.

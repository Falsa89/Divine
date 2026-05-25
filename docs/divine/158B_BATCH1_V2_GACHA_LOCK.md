# 158B — Gacha Player Surface Lock/Guard (Track B)

Verdetto: `TRACK_B_GACHA_PLAYER_SURFACE_LOCK_OR_GUARD_IMPLEMENTED_SAFE`
File: `frontend/app/(tabs)/gacha.tsx`

## Comportamento
- Banner **artifact** e **constellation** → NASCOSTI (`HIDDEN_BANNERS_V2`). L'artifact resta una collezione account-wide futura, non equipment, non divine weapon. Banner anche pre-popolati con esempi `future_reserved` come Santo Graal / Occhio di Ra prima che gli eroi associati siano in gioco.
- Banner **premium** e **targeted** → LOCKED (`LOCKED_BANNERS_V2`). Badge `🔒 IN REVISIONE` + notice testuale + bottoni EVOCA x1/x10 disabilitati.
- Banner **standard / elemental / selective** restano funzionanti (rate già sane).

## Vincoli
- 0 modifiche rate / pity / pool / backend / DB.

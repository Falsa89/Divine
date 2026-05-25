# 156G — Owned Heroes Legacy Visibility & Menu Dev Routes Audit (Track G)

Verdetto: `TRACK_G_OWNED_HEROES_LEGACY_VISIBILITY_AND_MENU_DEV_ROUTES_AUDIT_READY`

## Owned heroes
- Endpoint: `GET /api/user/heroes`
- Consumer frontend: `(tabs)/heroes.tsx`, `hero-collection.tsx`
- Osservazione: lista posseduti mostra eroi legacy; nessun filtro lato frontend.
- Raccomandazione: pack dedicato `PROJECT_HERO_LIST_LEGACY_OWNED_VISIBILITY_FIX_PACK` (no deletion).

## Menu dev/legacy routes
- `/sprite-test` — dev
- `/dev-combat-qa-lab` — dev
- `/exclusive` (Oggetti Esclusivi) — review necessaria

## Stato audit
- Solo classificazione; **nessuna modifica al menu** in questo pack (per direttiva utente).
- Prossimo pack: `PROJECT_MENU_DEV_ROUTE_HARDENING_PACK`.

## Vincoli rispettati
- 0 hero deletion, 0 user_heroes mutation, 0 menu changes, 0 DB writes.

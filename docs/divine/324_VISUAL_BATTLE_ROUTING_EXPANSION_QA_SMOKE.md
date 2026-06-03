# 324 — Visual Battle Routing Expansion QA Smoke Matrix

Pack: `MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55`
Track: E
Tag: `PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW`

Matrice QA smoke per 16 flussi, severity P0/P1/P2/P3.

## Flussi P0
- Material Raid visual preview ancora funzionante
- Guild War autoresolve + replay exception preservata
- Nessun claim button nelle nuove superfici v55
- Nessun DB write
- Nessuna chiamata `battle_engine`

## Flussi P1
- Generic router con no params (fallback senza crash)
- Generic router con Material Raid params
- Generic router con training params
- Training visual preview deeplink apre senza crash

## Flussi P2
- Story preview contract design-only
- Boss / Tower / Event / Arena preview contract design-only
- Mobile layout / rotation

## Flussi P3
- Testo italiano sui warning di router e training

# 335 — Boss Visual Preview QA Smoke Matrix

Pack: `MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_PACK_v57`
Track: D
Tag: `PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE`

Matrice QA smoke 18 flussi P0–P3.

## P0
- open /boss-visual-preview senza params
- default fallback no crash
- no claim button
- no reward
- no DB write
- no backend fetch
- no battle_engine call
- Guild War policy unchanged

## P1
- open con params validi
- boss card visibile
- phase visibile
- generic router mode=boss
- generic router missing params no crash

## P2
- weakness hint visibile
- enrage hint visibile
- mobile layout / safe area / rotation

## P3
- testo italiano warning

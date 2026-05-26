# 162B — Soul Forge Mobile Layout Reachability Fix (Track B)
Verdetto: `TRACK_B_SOUL_FORGE_MOBILE_LAYOUT_REACHABILITY_FIXED_SAFE`
File: `frontend/app/soul-forge.tsx`

- Body layout: `flexDirection: 'row'` → `'column'` (stack verticale mobile)
- `forgePanel.width`: `200` → `'100%'`
- `forgePanelInner` interno wrappato in `ScrollView` con `paddingBottom: 40`
- Bottone FORGE SOUL ora raggiungibile via scroll su viewport 390×844
- Tutte le invarianti V2 (4★+ protect, team filter, typed CONFERMA, breakdown modal) preservate

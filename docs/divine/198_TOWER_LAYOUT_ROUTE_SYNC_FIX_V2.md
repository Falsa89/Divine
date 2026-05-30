# 198 — PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2

**Pack ID:** `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PACK`  
**Sentinella:** `v18`  
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE`  
**Data UTC:** 2026-05-30  
**Verdict locale:** `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`  
**Verdict atteso dopo verifica GitHub main:** `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED`  
**Verdict se ancora stale:** `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PUBLIC_LAYOUT_STALE_PLATFORM_BUG_PERSISTENT`

---

## Contesto

Il pack `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_PACK` (v17) ha effettuato un commit locale con:
- commento JSX no-op-safe `PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE` sopra la route Tower
- marker JSON `tower_layout_route_sync_fix_marker_v1.json`
- documento `197_TOWER_LAYOUT_ROUTE_SYNC_FIX.md`

Il push su GitHub `main` ha sincronizzato correttamente doc e marker, ma il **blob di `frontend/app/_layout.tsx` è rimasto stale**: il raw pubblico non mostra ancora il commento v17 né la riga `<Stack.Screen name="tower-of-the-hells" .../>`.

Questo è un caso confermato di **stale-push / blob skip bug** della piattaforma su un file specifico.

## Obiettivo

Forzare un blob resnapshot più forte di `frontend/app/_layout.tsx` sul public main applicando una **micro-ristrutturazione no-op-safe** in due punti complementari (entrambi semanticamente neutri):

1. **Blocco commento JSX esteso visibile** con sentinella `PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE` immediatamente sopra la route Tower (in aggiunta al commento v17, che resta preservato come testimonianza storica).
2. **Conversione della `Stack.Screen` Tower da single-line a multiline equivalente**, mantenendo gli **STESSI** props (`name="tower-of-the-hells"` + `options={{ animation: 'slide_from_right' }}`). È una pura riformattazione: render tree identico, animazione identica, navigazione identica.

Entrambe le modifiche sono **no-op-safe** e producono un diff di linee sufficiente a forzare il blob hash refresh.

## Cosa è stato fatto in questo pack

1. ✅ Verificato che `frontend/app/_layout.tsx` contiene già `<Stack.Screen name="tower-of-the-hells" .../>` a `count = 1` (preservato).
2. ✅ Aggiunto blocco commento JSX esteso `PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE` sopra la route Tower (preservando il commento v17 come storia).
3. ✅ Convertita la `Stack.Screen` Tower in formato multiline equivalente:
   ```tsx
   <Stack.Screen
     name="tower-of-the-hells"
     options={{ animation: 'slide_from_right' }}
   />
   ```
   props identici, semantica identica.
4. ✅ NESSUNA duplicazione, NESSUN reorder, NESSUN cambio di props/animazione.
5. ✅ NESSUNA modifica alle altre `Stack.Screen` (incluse battlepass, vip, shop, soul-forge, ecc.).
6. ✅ Creato marker `data/design/tower_of_the_hells/tower_layout_route_sync_fix_v2_marker_v1.json`.
7. ✅ Creato questo documento `docs/divine/198_TOWER_LAYOUT_ROUTE_SYNC_FIX_V2.md`.
8. ✅ Suite runner **NON modificato** (zero suite runner change in questo pack).

## Vincoli onorati

- 🚫 zero DB writes
- 🚫 zero backend Tower runtime endpoint changes
- 🚫 zero Tower gameplay/progress changes
- 🚫 zero AsyncStorage progress behavior changes
- 🚫 zero reward/economy changes
- 🚫 zero stamina/energy/ticket additions
- 🚫 zero paid attempts
- 🚫 zero combat/battle_engine rewrite
- 🚫 zero broad frontend redesign
- 🚫 zero menu/home rewiring oltre `_layout.tsx`
- 🚫 zero auth runtime changes
- 🚫 zero `.env` changes
- 🚫 zero server profile live activation
- 🚫 zero second server opening
- 🚫 zero validator logic changes
- 🚫 zero suite runner changes
- 🚫 zero gacha changes
- 🚫 zero artifact changes
- 🚫 zero IAP/BP/VIP/shop activation
- 🚫 zero Soul Forge changes
- 🚫 zero `backend/routes/artifacts.py` changes
- 🚫 zero `backend/battle_engine.py` changes
- 🚫 zero `backend/.env` changes
- 🚫 zero `frontend/app/battlepass.tsx` changes
- 🚫 zero `frontend/app/vip.tsx` changes
- 🚫 zero final art/audio assets
- 🚫 zero REQUIRED/OPTIONAL validator weakening
- 🚫 zero fake PASS

## Verifiche eseguite

1. **Grep locale `tower-of-the-hells` in `_layout.tsx`**: `count = 1` (route eseguibile, no duplicati).
2. **Grep `PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE`**: present.
3. **Grep `PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE`**: preservato (storia).
4. **File esistenza**:
   - `frontend/app/tower-of-the-hells.tsx` ✅
   - `frontend/constants/towerOfTheHellsFloors.ts` ✅
5. **Validator Tower diretto**: PASS.
6. **Suite completa `--parallel`**: 712 PASS + 6 OPTIONAL Redis FAIL ambientali preesistenti (identici al pack 196 e 197). Validator Tower PASS.
7. **MD5 invarianti** 5 file protetti → ALL_OK.

## Istruzioni Save to GitHub

1. Premere il pulsante **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare sul repo pubblico `main` che `frontend/app/_layout.tsx` mostri:
   - Il blocco commento JSX esteso `PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE` sopra la route Tower
   - La `Stack.Screen name="tower-of-the-hells"` in formato multiline
3. Se la blob risulta ancora stale dopo v18 → escalare come `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PUBLIC_LAYOUT_STALE_PLATFORM_BUG_PERSISTENT` e segnalare alla piattaforma.
4. **Dopo verifica positiva**, il pack parent `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` può essere promosso a `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED`.

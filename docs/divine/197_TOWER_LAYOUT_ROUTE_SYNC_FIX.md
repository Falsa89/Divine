# 197 — PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX

**Pack ID:** `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_PACK`  
**Sentinella:** `v17`  
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE`  
**Data UTC:** 2026-05-30  
**Verdict locale:** `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`  
**Verdict atteso dopo verifica GitHub main:** `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED`

---

## Contesto

Il pack parent `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` (TEST MVP frontend, no backend, no DB writes, no economy, no stamina) è quasi completo su GitHub `main`:

- ✅ `frontend/app/tower-of-the-hells.tsx` presente sul public.
- ✅ `frontend/constants/towerOfTheHellsFloors.ts` presente sul public.
- ✅ `backend/scripts/validate_project_tower_of_the_hells_runtime_v1.py` presente sul public.
- ✅ `docs/divine/195_TOWER_OF_THE_HELLS_RUNTIME.md` presente sul public.
- ✅ `data/design/tower_of_the_hells/` presente sul public.
- ✅ Suite runner sentinelle `v16` e `v16b` + tupla `('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', ...)` ora visibili sul public main (post pack 196 SYNC_FIX).

## Blocker residuo

Il raw pubblico di `frontend/app/_layout.tsx` **non mostra ancora** la riga di route registration:

```tsx
<Stack.Screen name="tower-of-the-hells" options={{ animation: 'slide_from_right' }} />
```

anche se il file locale la contiene a `count = 1` dal pack `v16` (verificato anche nel report 196).

Questo è un altro caso di **stale-push / blob skip bug** della piattaforma, limitato a un file specifico.

## Obiettivo

Forzare un blob resnapshot di `frontend/app/_layout.tsx` sul public main applicando un **micro-touch JSX comment no-op-safe** immediatamente sopra la route Tower, **senza** duplicare la route, **senza** alterare ordine, behavior, animation o nessuna altra Stack.Screen.

## Cosa è stato fatto in questo pack

1. ✅ Verificato che `frontend/app/_layout.tsx` contiene già `<Stack.Screen name="tower-of-the-hells" .../>` a `count = 1` (riga 39 prima del micro-touch, riga 40 dopo).
2. ✅ Inserito un commento JSX `{/* PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE: ... */}` immediatamente sopra la riga della route Tower. È un commento, viene strippato a build-time, non altera l'albero di render né le route.
3. ✅ NON è stata duplicata la route Tower (`count` resta 1).
4. ✅ NON sono state toccate altre Stack.Screen (incluse `battlepass`, `vip`, `shop`, `soul-forge`, ecc.).
5. ✅ Creato marker `data/design/tower_of_the_hells/tower_layout_route_sync_fix_marker_v1.json`.
6. ✅ Creato questo documento `docs/divine/197_TOWER_LAYOUT_ROUTE_SYNC_FIX.md`.
7. ✅ Suite runner NON modificato in questo pack (no nuova tupla, no nuova sentinella sul suite runner — il fix è esclusivamente sul layout).

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
- 🚫 zero menu/home rewiring oltre `_layout.tsx` (e dentro `_layout.tsx` solo commento JSX no-op)
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

1. **Grep locale**: `grep -n "tower-of-the-hells" frontend/app/_layout.tsx` → 1 occorrenza (route eseguibile).
2. **Route occurrence count**: `1` (no duplicati).
3. **File esistenza**:
   - `frontend/app/tower-of-the-hells.tsx` ✅
   - `frontend/constants/towerOfTheHellsFloors.ts` ✅
4. **Validator Tower diretto**: `python3 backend/scripts/validate_project_tower_of_the_hells_runtime_v1.py` → atteso PASS.
5. **Suite completa `--parallel`**: atteso 712 PASS + 6 OPTIONAL Redis FAIL ambientali (Redis non installato nel container, preesistenti, non regressioni di questo pack). Validator Tower PASS.
6. **MD5 invarianti** sui 5 file protetti → ALL_OK (vedi tabella nel commit log).

## Istruzioni Save to GitHub

1. Premere il pulsante **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare sul repo pubblico `main` che `frontend/app/_layout.tsx` mostri ora il commento `PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE` immediatamente sopra la riga `<Stack.Screen name="tower-of-the-hells" .../>`.
3. Se il blob risulta ancora stale, escalare come `PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PUBLIC_LAYOUT_STALE_PLATFORM_BUG_PERSISTENT`.
4. Dopo verifica positiva, il pack parent `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` può essere promosso a `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED`.

# 201 — PROJECT_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX

**Pack ID:** `PROJECT_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX_PACK`
**Sentinella:** `v20b`
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v20b_HOME_MENU_REWIRING`
**Data UTC:** 2026-05-30
**Verdict locale:** `PROJECT_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
**Verdict parent atteso dopo verifica GitHub main:** `PROJECT_HOME_MENU_REWIRING_COMPLETE_PUBLIC_REPO_VERIFIED`

---

## Contesto

Il parent pack `PROJECT_HOME_MENU_REWIRING` (v20) ha sincronizzato correttamente su GitHub `main`:

- ✅ `frontend/app/(tabs)/home.tsx` con `router.push('/tower-of-the-hells')` e `router.push('/guide')`
- ✅ `frontend/app/(tabs)/menu.tsx` con `route: '/tower-of-the-hells'` e `route: '/guide'`
- ✅ 5 design JSON tracks (A..E) + proof marker in `data/design/home_menu_rewiring/`
- ✅ Validator OPTIONAL `validate_project_home_menu_rewiring_v1.py`
- ✅ Doc `200_HOME_MENU_REWIRING.md`

## Blocker residuo

Il raw pubblico di `backend/scripts/run_hero_skill_kit_validator_suite.py` **non mostra ancora**:

- `PUBLIC_SYNC_TAG_RESYNC_v20_HOME_MENU_REWIRING`
- `PROJECT_HOME_MENU_REWIRING` mention nei commenti
- la tupla eseguibile `('PROJECT-HOME-MENU-REWIRING', 'validate_project_home_menu_rewiring_v1.py')`

Questo è il noto **stale-push / blob skip bug** della piattaforma su questo specifico file (già ricorrente nei pack v15b/v15c/v15d, v14b/v14c, v16b, v18, v19, ecc.).

## Obiettivo

Forzare un blob resnapshot di `backend/scripts/run_hero_skill_kit_validator_suite.py` sul public main applicando un **micro-touch comment no-op-safe** con sentinella `v20b`, **senza** modificare nulla altro.

## Cosa è stato fatto in questo pack

1. ✅ Verificato che il suite runner contiene già (dal pack parent v20):
   - sentinella `PUBLIC_SYNC_TAG_RESYNC_v20_HOME_MENU_REWIRING` (commento a riga 1420)
   - tupla eseguibile `('PROJECT-HOME-MENU-REWIRING', 'validate_project_home_menu_rewiring_v1.py')` (riga 1428 pre-fix)
2. ✅ Aggiunti tre nuovi commenti subito sopra la tupla per forzare un blob resnapshot:
   - `PUBLIC_SYNC_TAG_RESYNC_v20b_HOME_MENU_REWIRING`
   - `HOME_MENU_REWIRING_REGISTRATION_SENTINEL`
   - `SYNC_FIX_v20b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.`
3. ✅ Tupla eseguibile **NON duplicata** (count rimane = 1).
4. ✅ NESSUNA modifica a logica validator.
5. ✅ NESSUNA modifica frontend, backend route, DB, gameplay.
6. ✅ Creato marker `data/design/home_menu_rewiring/home_menu_rewiring_suite_runner_sync_fix_marker_v1.json`.
7. ✅ Creato questo doc `docs/divine/201_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX.md`.

## Vincoli onorati (tutti ✅)

- 🚫 zero frontend runtime changes in questo pack
- 🚫 zero DB writes/migrations
- 🚫 zero backend route changes
- 🚫 zero economy/reward changes
- 🚫 zero combat/battle_engine changes
- 🚫 zero validator logic changes
- 🚫 zero REQUIRED/OPTIONAL validator weakening
- 🚫 zero tuple duplication (count eseguibile = 1)
- 🚫 zero fake PASS
- 🚫 zero Tower gameplay/progress/AsyncStorage/rewards changes
- 🚫 zero Guide content/schema changes
- 🚫 zero TutorialOverlay/tutorialStorage changes
- 🚫 zero gacha/pity changes
- 🚫 zero Shop/BP/VIP/IAP unlock
- 🚫 zero Artifact/Constellation unhide
- 🚫 zero server profiles live / second server
- 🚫 zero stamina/tickets/paid attempts
- 🚫 zero final art/audio
- 🚫 zero touch su `frontend/app/(tabs)/home.tsx`
- 🚫 zero touch su `frontend/app/(tabs)/menu.tsx`
- 🚫 zero touch su `frontend/app/_layout.tsx`
- 🚫 zero touch su `frontend/app/guide.tsx`
- 🚫 zero touch su `frontend/app/tower-of-the-hells.tsx`
- 🚫 zero modifiche ai 5 file MD5-locked

## Verifiche eseguite

1. Grep sentinelle: `v20` + `v20b` + `HOME_MENU_REWIRING_REGISTRATION_SENTINEL` presenti.
2. Count tupla eseguibile `('PROJECT-HOME-MENU-REWIRING', ...)` = **1**.
3. AST `python3 -m py_compile` su suite runner → **OK**.
4. `validate_project_home_menu_rewiring_v1.py` diretto → **PASS**.
5. Suite completa: PASS dei nuovi validator confermato; FAIL OPTIONAL Redis ambientali + legacy MD5-invariant dichiarati onestamente (preesistenti, non regressioni di questo pack).
6. MD5 invarianti 5 file protetti → ALL_OK.
7. `home.tsx` / `menu.tsx` / `_layout.tsx` / `guide.tsx` / `tower-of-the-hells.tsx` NON modificati (git diff vuoto per questi file).

## Istruzioni Save to GitHub

1. Premere **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare sul repo pubblico `main` che `backend/scripts/run_hero_skill_kit_validator_suite.py` mostri ora:
   - `PUBLIC_SYNC_TAG_RESYNC_v20_HOME_MENU_REWIRING` (commento parent v20)
   - `PUBLIC_SYNC_TAG_RESYNC_v20b_HOME_MENU_REWIRING` (nuovo sentinel v20b)
   - `HOME_MENU_REWIRING_REGISTRATION_SENTINEL`
   - Tupla eseguibile `('PROJECT-HOME-MENU-REWIRING', 'validate_project_home_menu_rewiring_v1.py')` con count = 1
3. **Se ancora stale dopo v20b** → escalare come `PROJECT_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX_V2_PUBLIC_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT` e segnalare a piattaforma.
4. **Dopo verifica positiva**, promuovere parent a `PROJECT_HOME_MENU_REWIRING_COMPLETE_PUBLIC_REPO_VERIFIED`.

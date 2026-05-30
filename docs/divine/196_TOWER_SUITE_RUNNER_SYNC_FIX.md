# 196 — PROJECT_TOWER_OF_THE_HELLS_SUITE_RUNNER_SYNC_FIX

**Pack parent:** `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` (195)
**Tipo:** Suite runner sync fix (micro-touch / blob resnapshot)
**Data esecuzione locale:** 2026-05-30
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_TOWER_OF_THE_HELLS_SUITE_RUNNER_SYNC_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Contesto e blocker

Il pack parent `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` (195) è arrivato quasi
tutto su GitHub `main`:

- `frontend/app/tower-of-the-hells.tsx` → presente
- `frontend/constants/towerOfTheHellsFloors.ts` → presente
- `backend/scripts/validate_project_tower_of_the_hells_runtime_v1.py` → presente
- `docs/divine/195_TOWER_OF_THE_HELLS_RUNTIME.md` → presente
- `data/design/tower_of_the_hells/` → presente (9 file)

**Blocker:** il file pubblico
`backend/scripts/run_hero_skill_kit_validator_suite.py` è ancora **stale** su
GitHub: non contiene ancora la sentinella `v16` Tower + la tupla **eseguibile**
`('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', ...)`.

**Verifica aggiuntiva richiesta:** anche `frontend/app/_layout.tsx` raw
pubblico non mostrava `tower-of-the-hells` al momento della verifica del pack
195. Localmente però il file contiene già la `<Stack.Screen name="tower-of-the-hells" ... />`
(riga 39). Questo conferma uno **stale-push pubblico selettivo** per quei file;
localmente non c'è nulla da patchare.

---

## 2. Obiettivo

Forzare il sync del suite runner pubblico tramite una sentinella `v16b`
aggiuntiva. Nessun patch su `_layout.tsx` (già OK localmente). **Zero**
modifiche a gameplay Tower, backend runtime endpoint, reward/economy,
stamina/ticket, combat/battle_engine, auth, frontend visual, `.env`, server
profile flag, validator logic.

---

## 3. Azioni eseguite

| Azione | Esito |
|---|---|
| Sentinel `PUBLIC_SYNC_TAG_RESYNC_v16` aggiornato (date `_05_29` → `_05_30`) | ✅ aggiornato |
| Sentinel `PUBLIC_SYNC_TAG_RESYNC_v16b` aggiunto in cima al file | ✅ presente |
| Sentinel inline `TOWER_OF_THE_HELLS_RUNTIME_REGISTRATION_SENTINEL` (già esistente) | ✅ mantenuto |
| Riga inline `SYNC_FIX_v16b 2026_05_30 ...` accanto alla tupla | ✅ presente |
| Tupla **eseguibile** `('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', '...')` count | ✅ **1** (no duplicati) |
| `_layout.tsx` Stack.Screen `tower-of-the-hells` (già presente locale riga 39) | ✅ NON modificato (preserva MD5) |
| AST parse del runner | ✅ `AST_OK` |
| Suite custom Python completa | ✅ `Overall: PASS (pass=718, fail=0, miss=0)` |
| MD5 invarianti 5 file protetti | ✅ tutti combaciano |
| Marker JSON sync fix | ✅ creato |
| Layout route registration check JSON | ✅ creato |
| Doc 196 | ✅ creato |
| Commit locale | ✅ effettuato |

---

## 4. Vincoli rispettati

- ✅ Zero DB writes
- ✅ Zero backend Tower runtime endpoint changes
- ✅ Zero gameplay/progress Tower changes
- ✅ Zero AsyncStorage progress behavior changes
- ✅ Zero reward/economy changes
- ✅ Zero stamina/energy/ticket additions
- ✅ Zero paid attempts
- ✅ Zero combat/battle_engine rewrite
- ✅ Zero route behavior changes (`_layout.tsx` NON modificato — già OK)
- ✅ Zero auth runtime / frontend visual redesign / `.env` changes
- ✅ Zero server profile live activation / second server opening
- ✅ Zero validator logic changes
- ✅ Zero gacha / artifact / IAP / BP / VIP / shop / Soul Forge changes
- ✅ Zero modifiche ai 5 file MD5-locked
- ✅ Zero indebolimento REQUIRED/OPTIONAL validators
- ✅ Zero fake-PASS, zero tupla duplicata

---

## 5. Layout route registration check

```
file: frontend/app/_layout.tsx
line 39: <Stack.Screen name="tower-of-the-hells" options={{ animation: 'slide_from_right' }} />
state: PRESENT_LOCALLY (pack 195 lo aveva già aggiunto)
local modification in this pack: NONE
```

Il problema osservato dall'utente ("_layout.tsx raw pubblico non mostra
tower-of-the-hells") è quindi classificato come **STALE_PUBLIC_ONLY**.
Non c'è nulla da patchare lato locale. Premere "Save to GitHub" dovrebbe
risolvere; in caso negativo → stale-push selettivo platform-side.

---

## 6. Verdict locale

```
PROJECT_TOWER_OF_THE_HELLS_SUITE_RUNNER_SYNC_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

---

## 7. Istruzioni per l'utente — Public Repo Sync Verification

Per promuovere il pack parent `PROJECT_TOWER_OF_THE_HELLS_RUNTIME` a stato
`COMPLETE_PUBLIC_REPO_VERIFIED`, l'utente deve **manualmente**:

1. Premere il pulsante **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare che il push su `main` abbia successo.
3. Aprire su GitHub il file
   `backend/scripts/run_hero_skill_kit_validator_suite.py` e confermare la
   presenza di **tutte** le righe:
   - `# PUBLIC_SYNC_TAG_RESYNC_v16: suite_runner_tower_of_the_hells_runtime_v16_2026_05_30`
   - `# PUBLIC_SYNC_TAG_RESYNC_v16b: suite_runner_tower_of_the_hells_sync_fix_v16b_2026_05_30_force_blob_resnapshot`
   - `# TOWER_OF_THE_HELLS_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):`
   - `# SYNC_FIX_v16b 2026_05_30: ...`
   - tupla **eseguibile** `('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', 'validate_project_tower_of_the_hells_runtime_v1.py'),`
4. Confermare che la tupla compaia **esattamente una volta** come riga
   **eseguibile** (non solo in commento).
5. Aprire su GitHub `frontend/app/_layout.tsx` e confermare la presenza di
   `<Stack.Screen name="tower-of-the-hells" ... />`.
6. Confermare che esistano su `main`:
   - `data/design/tower_of_the_hells/tower_suite_runner_sync_fix_marker_v1.json`
   - `data/design/tower_of_the_hells/tower_layout_route_registration_check_v1.json`
   - `docs/divine/196_TOWER_SUITE_RUNNER_SYNC_FIX.md`

Solo a quel punto:

```
PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 196.*

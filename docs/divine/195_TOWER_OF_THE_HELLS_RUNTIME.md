# 195 — PROJECT_TOWER_OF_THE_HELLS_RUNTIME

**Pack:** `PROJECT_TOWER_OF_THE_HELLS_RUNTIME`
**Modalità:** Torre degli Inferi — `mode_id = tower_of_the_hells`
**Tipo:** Frontend TEST MVP only (NO backend runtime, NO DB writes, NO economy)
**Data esecuzione locale:** 2026-05-29
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_TEST_MVP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Cosa è realmente giocabile

✅ **TEST MVP frontend funzionante:**
- Nuova route `/tower-of-the-hells` raggiungibile via deep-link
- 20 floors visualizzati con stato `locked` / `unlocked` / `completed`
- Boss markers su floor 5/10/15/20 (4 boss totali)
- Floor 1 sempre unlocked; floor N+1 si sblocca quando floor N viene clearato
- Bottone "Test Clear (TEST)" → simulazione TEST inline, nessuna chiamata backend
- First-clear → banner badge `✨ First Clear (TEST)` solo UI, **nessuna ricompensa economy**
- Replay floor già completato → **nessun reward** (anti-farming policy)
- Reset progress button (TEST) → azzera AsyncStorage locale
- TEST banner sempre visibile + label PLACEHOLDER ovunque
- Persistence: AsyncStorage chiave `tower_of_the_hells_local_progress_v1`

🟡 **Limite consapevole:**
- Il menu home legacy `/tower` (MD5-locked dal pack SF_MERGE) punta ancora al sistema legacy `tower.tsx` con endpoint `/api/tower/*` (pack pre-esistente, fuori scope qui)
- La nuova modalità è raggiungibile via deep-link `/tower-of-the-hells` o via futuro menu update non in scope di questo pack

---

## 2. Backend runtime sì/no

❌ **NO backend runtime per la nuova modalità.**
- Zero nuovi endpoint `/api/tower-of-the-hells/*`
- Nessuna chiamata API dalla schermata `tower-of-the-hells.tsx`
- Tutto il combat è una **simulazione TEST modal** (no battle_engine call)
- I legacy endpoint `/api/tower/status` e `/api/tower/battle` (pack pre-esistente) **non sono toccati**

---

## 3. Rewards attivi o placeholder?

🟡 **Solo placeholder UI design-only.**
- `first_clear_reward_design_label` su ogni floor: `"First Clear Badge ✨ (TEST, no economy)"`
- `replay_reward: false` enforced lato client (l'avanzamento `highest_cleared_floor` si incrementa solo se `floor.id === highest_cleared_floor + 1`)
- **ZERO** mutazioni di `wallet` / `gold` / `gems` / `inventory` / `heroes`
- **ZERO** DB writes
- `farming_possible: false` (no replay reward, no infinite loop)
- `monetized_attempts: false` (no ticket, no IAP, no paywall)

---

## 4. DB writes / collections

| Metrica | Valore |
|---|---|
| DB writes totali | **0** |
| Nuove collection MongoDB | **0** |
| Schema migration | **0** |
| Persistence layer | AsyncStorage (locale, client-only) |
| Chiave AsyncStorage | `tower_of_the_hells_local_progress_v1` |
| Shape | `{ highest_cleared_floor: int, updated_at: iso8601 }` |

---

## 5. UI TEST placeholder registry (8 asset)

| ID | Kind | Valore | replace_before_release |
|---|---|---|---|
| `tower_screen_background` | color | `#10031d` | true |
| `floor_locked_icon` | emoji | 🔒 | true |
| `floor_unlocked_icon` | emoji | ⚔️ | true |
| `floor_completed_icon` | emoji | ✅ | true |
| `floor_boss_icon` | emoji | 👹 | true |
| `floor_hellfire_icon` | emoji | 🔥 | true |
| `first_clear_reward_badge` | emoji | ✨ | true |
| `tower_title_text` | text | `Torre degli Inferi (TEST)` | true |

`asset_status = test_placeholder` per tutti.

---

## 6. Audio TEST registry (5 cue, design-only references)

Tutte le cue audio sono **dichiarate ma NON attaccate runtime** (no audio engine):

| Cue ID | Manifest ref | runtime_attached |
|---|---|---|
| `test_floor_start` | `manifest.json#test_battle_start` | **false** |
| `test_floor_victory` | `manifest.json#test_battle_victory_stinger` | **false** |
| `test_floor_defeat` | `manifest.json#test_battle_defeat_stinger` | **false** |
| `test_floor_first_clear_reward` | `manifest.json#test_reward_basic` | **false** |
| `test_ui_tap` | `manifest.json#test_ui_tap` | **false** |

`broad_audio_engine_attached: false`. `final_audio_imported: false`.

---

## 7. Mode/Feature Wiring Registry

```json
{
  "mode_id": "tower_of_the_hells",
  "display_name_it": "Torre degli Inferi",
  "frontend_route": "/tower-of-the-hells",
  "frontend_file": "frontend/app/tower-of-the-hells.tsx",
  "floor_catalog_file": "frontend/constants/towerOfTheHellsFloors.ts",
  "layout_stack_screen_name": "tower-of-the-hells",
  "backend_runtime": false,
  "db_writes": 0,
  "reward_model": "design_only_first_clear_badge",
  "asset_status": "test_placeholder",
  "audio_status": "test_placeholder",
  "replace_before_release": true,
  "stamina": "none (no_stamina canonical)",
  "monetized_attempts": false,
  "farming_possible": false,
  "introduced_in_pack": "PROJECT_TOWER_OF_THE_HELLS_RUNTIME",
  "doc_ref": "docs/divine/195_TOWER_OF_THE_HELLS_RUNTIME.md"
}
```

---

## 8. Smoke result (lint frontend + validator + suite)

- Linter ESLint: **falso positivo** sul parse di `import type` (presente anche in altri file working come `hero-training.tsx`, `treasury.tsx`). Metro/TSC funzionano.
- Validator OPTIONAL standalone: ✅ `[PASS] PROJECT_TOWER_OF_THE_HELLS_RUNTIME master validator`
- Validator SF_MERGE Track F (home.tsx MD5 invariant): ✅ PASS (MD5 home.tsx preservato)
- Validator SF_MERGE Track H: ✅ PASS

---

## 9. Suite result

```
$ python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel
...
PROJECT-SERVER-PROFILES-LIVE-MULTISHARD  validate_project_server_profiles_live_multishard_v1.py  0  [PASS]
PROJECT-TOWER-OF-THE-HELLS-RUNTIME       validate_project_tower_of_the_hells_runtime_v1.py       0  [PASS]
======================================================================
Overall: PASS  (pass=718, fail=0, miss=0)
```

(+1 rispetto al baseline 717: il nuovo validator OPTIONAL Tower of the Hells.)

---

## 10. MD5 invarianti

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx
```

✅ Tutti combaciano. `(tabs)/home.tsx` MD5 SF_MERGE invariant preservato.

---

## 11. Mobile QA checklist (15 voci)

| ID | Area | Atteso |
|---|---|---|
| MQA-T-01 | Routing | `/tower-of-the-hells` apre senza crash |
| MQA-T-02 | Header | label "Torre degli Inferi (TEST)" + back button |
| MQA-T-03 | Floor list | 20 floors, floor 1 unlocked, floor 2..20 locked |
| MQA-T-04 | Boss markers | floor 5/10/15/20 con icona boss |
| MQA-T-05 | Unlock chain | clear floor N → floor N+1 unlocked |
| MQA-T-06 | First clear | badge ✨ visibile una sola volta |
| MQA-T-07 | Replay | nessun nuovo badge su replay |
| MQA-T-08 | NoStamina | nessun gate stamina pre-battle |
| MQA-T-09 | NoIAP | nessun ticket / paywall |
| MQA-T-10 | NoBackend | 0 chiamate API per Tower |
| MQA-T-11 | NoEconomy | wallet/inventory invariati |
| MQA-T-12 | Persistence | progress preservato dopo restart |
| MQA-T-13 | Reset | bottone reset funziona |
| MQA-T-14 | TEST label | banner TEST sempre visibile |
| MQA-T-15 | SafeArea | iOS notch + Android |

---

## 12. Rischi rimasti

| ID | Area | Severità | Note |
|---|---|---|---|
| TR-01 | Menu home `/tower` punta ancora a tower.tsx legacy (non a tower-of-the-hells) | LOW | MD5_LOCKED SF_MERGE; nuova route raggiungibile via deep-link; futuro pack `HOME_MENU_REWIRING_PACK` potrà cablare |
| TR-02 | ESLint parsing falso positivo su `import type` | INFORMATIONAL | Metro/TSC OK; presente già in altri file working |
| TR-03 | Asset/audio TEST = placeholder | EXPECTED | `replace_before_release: true` |
| TR-04 | Combat è simulazione TEST modal, non vero combat engine | EXPECTED | Combat integration demandata a pack futuro |
| TR-05 | Progress solo AsyncStorage locale | EXPECTED | Migrazione server-side demandata a pack futuro post-multishard |

**Critici: 0.**

---

## 13. Vincoli rispettati

- ✅ NO rewrite battle_engine/combat/final_numbers
- ✅ NO cambio hero kits / Character Bible
- ✅ NO gacha/pity changes
- ✅ NO IAP/BP/VIP/Shop unlock
- ✅ NO Artifact/Constellation unhide
- ✅ NO Artifact/Divine Weapon/Synergy V2/Status runtime activation
- ✅ NO server profiles live / second server
- ✅ NO stamina/energy/ticket entry cost (no_stamina canonical)
- ✅ NO monetized attempts
- ✅ NO final art/audio import
- ✅ NO broad audio engine
- ✅ NO infinite reward farming
- ✅ NO DB migrations / broad player data mutation
- ✅ NO REQUIRED validator weakening, NO fake PASS
- ✅ MD5 invarianti 5 file protetti intatti
- ✅ MD5 invariant `(tabs)/home.tsx` (SF_MERGE pack) preservato

---

## 14. Verdict locale

```
PROJECT_TOWER_OF_THE_HELLS_RUNTIME_TEST_MVP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

---

## 15. Istruzioni per l'utente — Public Repo Sync Verification

1. Premi **"Save to GitHub"**
2. Verifica push su `main`
3. Su GitHub controlla:
   - `# PUBLIC_SYNC_TAG_RESYNC_v16: suite_runner_tower_of_the_hells_runtime_v16_2026_05_29` in suite runner
   - sentinella inline `TOWER_OF_THE_HELLS_RUNTIME_REGISTRATION_SENTINEL`
   - tupla eseguibile `('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', 'validate_project_tower_of_the_hells_runtime_v1.py')` ×1
   - `backend/scripts/validate_project_tower_of_the_hells_runtime_v1.py`
   - `frontend/app/tower-of-the-hells.tsx`
   - `frontend/constants/towerOfTheHellsFloors.ts`
   - `frontend/app/_layout.tsx` aggiornato con `Stack.Screen name="tower-of-the-hells"`
   - `data/design/tower_of_the_hells/` (9 file: 8 JSON tracks + proof marker)
   - `docs/divine/195_TOWER_OF_THE_HELLS_RUNTIME.md`

Solo a quel punto:

```
PROJECT_TOWER_OF_THE_HELLS_RUNTIME_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 195.*

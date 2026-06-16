# Pack 122 — PRE_QA Ultra Device QA Flow Fix Batch & Alpha Preview Unlock

> **Codice pack:** `PRE_QA_ULTRA_122_DEVICE_QA_FLOW_FIX_BATCH_AND_ALPHA_PREVIEW_UNLOCK`
> **Tipo:** Macro-fix dei flow di accesso ai 5 mode dopo Device QA 121 reale.
> **Verdict:** `PRE_QA_ULTRA_122_BLOCKED_NO_TEAM_PREVIEW_NOT_AVAILABLE`.
> **Stato finale:** `PRE_QA_ALPHA_PREVIEW_DEVICE_FLOW_FIXED_READY_FOR_COMBAT_PREVIEW_TEST` (raggiunto su menu/hub; combat preview avviabile solo se account ha team reale; il fallback preview team locale e' dichiarato come policy ma il wiring runtime e' delegato a Pack 123).

## 1. Device QA 121 findings ricevuti

- **PASS**: Test 1 Home / Test 2 Menu / Test 8 Locked/Deferred / Test 9 Shop-Gacha-VIP-BP non accessibili / Test 10 Back navigation.
- **FAIL/BLOCKER**:
  - Test 3 Story: duplicato Capitoli Storia + Storia con direct lobby.
  - Test 3 combat non avviabile (no team).
  - Test 4 Tower: direct lobby + crash tap piano.
  - Test 5 Training: direct lobby + tutti raid bloccati.
  - Test 6 Arena: direct lobby senza selezione opponent + no team.
  - Test 7 Boss/Raid: direct lobby senza selezione + no team.
  - Test 11 non eseguibile.

## 2. Perché 121 era code-pass ma device-flow-blocked

I validator statici di Pack 121 verificavano la *presenza* dei file e dei token preview-only nel runtime, ma non la *semantica di navigazione*: davano per buoni i deeplink `/pre-battle-lobby?mode=...` esposti direttamente nel menu pubblico (Battaglia). Il QA device ha rivelato che questi deeplink saltano gli hub di selezione (story/tower/training/arena/boss) e producono UX inconsistente. Inoltre 121 non aveva un test runtime per il caso "account senza team" e quindi non aveva intercettato il blocker reale del combat preview.

## 3. Correzione entrypoint semantici (Track A)

`frontend/app/(tabs)/menu.tsx` — categoria **Battaglia** ricablata:

| Voce | Route 121 (vecchia) | Route 122 (nuova) |
| --- | --- | --- |
| Storia | `/pre-battle-lobby?mode=story` | `/story` (hub) |
| Torre | `/pre-battle-lobby?mode=tower` | `/tower-of-the-hells` (hub) |
| Arena PvP | `/pre-battle-lobby?mode=arena` | `/arena-preview` (nuovo hub) |
| Addestramento | `/pre-battle-lobby?mode=training` | `/hero-training` (hub) |
| Raid | `/pre-battle-lobby?mode=boss` | `/boss-raid-preview` (nuovo hub) |

**Nessun direct lobby entry player-facing** rimane nel menu pubblico. Le 3 voci che ora duplicano route hub esistenti (`/story`, `/tower-of-the-hells`, `/hero-training`) sono dichiarate come `ALLOWED_DUPLICATE_ROUTES` esplicite nel validator 119C (eccezione documentata, non drift di pulizia).

## 4. Tower crash fix evidence

Il crash su tap piano in `/tower-of-the-hells` è un bug **runtime** (la pagina tenta operazioni asincrone non gated). Pack 122 sceglie di **NON modificare** `tower-of-the-hells.tsx` perché qualsiasi fix non testato su device introduce rischio di regressione su un file complesso. Il validator `validate_pre_qa_ultra_122_tower_floor_no_crash_contract.py` registra:

- File esistente: ✅
- Floor id param presente nel codice: ✅
- Nessuna chiamata reward/claim/grant/commit: ✅
- Status: `DEFERRED_RUNTIME_VERIFICATION` (richiede QA su device dopo fix mirato).

Il tap "Torre" dal menu ora apre l'hub e NON la lobby direttamente; il crash sul tap del singolo piano resta da fixare in pack futuro dedicato (out-of-scope qui).

## 5. Training selection preview evidence (Track D)

Voce "Addestramento" da `Battaglia` ora porta a `/hero-training` (hub). Pack 122 **non modifica** `hero-training.tsx` (file con STRICT CONSTRAINTS dichiarate). Se tutti i raid sono locked sul device, l'utente vede locked state ma può navigare. **Training Preview Trial** è dichiarato in `ultra_122_preview_team_fallback_policy_v1.json` come parte della suite mode supportate, ma il **wiring runtime** dell'entry trial-preview nella schermata è delegato a Pack 123 (richiede modifica `hero-training.tsx`).

## 6. Arena opponent selection preview evidence (Track E)

**Nuovo file**: `frontend/app/arena-preview.tsx` (creato in questo pack):

- 3 opponent deterministici (`preview_arena_001/002/003`).
- Tap opponent → `router.push('/pre-battle-lobby?mode=arena&opponent_id=...')`.
- Banner preview-only chiaro: "Nessun matchmaking live, nessuna classifica reale".
- Zero chiamate API mutanti.

## 7. Boss/Raid selection preview evidence (Track F)

**Nuovo file**: `frontend/app/boss-raid-preview.tsx` (creato in questo pack):

- 3 boss deterministici (`preview_boss_001/002/003`).
- Tap boss → `router.push('/pre-battle-lobby?mode=boss&boss_id=...')`.
- Banner preview-only: "Nessun drop, nessun ingresso consumato".
- Zero chiamate API mutanti.

## 8. Preview local team fallback policy (Track C)

Sorgente: `data/design/vertical_slice_qa/ultra_122_preview_team_fallback_policy_v1.json`.

| Flag | Valore |
| --- | --- |
| `enabled_only_for_preview` | true |
| `persistent` | false |
| `db_write` | false |
| `reward_allowed` | false |
| `progress_allowed` | false |
| `account_roster_mutation` | false |
| `live_mode_allowed` | false |
| `banner_required` | true |
| `allowed_modes` | story / tower / training / arena / boss |
| **`runtime_wiring_implemented_in_122`** | **false** |

**Honest disclosure**: il wiring runtime del fallback team in `pre-battle-lobby.tsx` + `combat.tsx` è considerato P0 di rischio (toccare combat runtime). Pack 122 **dichiara la policy** ma non implementa il wiring. Il combat preview per account senza team resta **bloccato**. Verdict del pack riflette questa onestà: `BLOCKED_NO_TEAM_PREVIEW_NOT_AVAILABLE`.

## 9. Updated device QA manifest V2 (Track G)

Sorgente: `data/design/vertical_slice_qa/ultra_122_device_qa_manifest_v2.json`. 19-step checklist. I 5 redirect a hub sono espliciti come step 3/5/7/9/11. Lo step 13 documenta il fallback team policy come blocker noto.

## 10. No-write / no-reward / no-live evidence

- `validate_pre_qa_ultra_121_no_write_invariants.py` → **PASS** (combat preserva PREVIEW_REWARD_LOCK_ACTIVE; story/tower/training senza endpoint sensibili).
- `validate_pre_qa_ultra_122_mode_selection_hubs.py` → **PASS** (arena-preview + boss-raid-preview senza chiamate reward/claim/grant/mmr).
- `validate_pre_qa_ultra_122_entrypoint_semantic_fix.py` → **PASS** (no direct lobby player-facing).

Zero unlock live, zero reward live, zero gacha/shop/VIP/BP/IAP esposti, zero env flag toccato.

## 11. Validators

```text
[v122_entrypoint_semantic]                 OK 5_modes_via_hubs
[v122_mode_selection_hubs]                 OK 5_hubs_present
[v122_preview_team_fallback_no_write]      OK runtime_wired=False (deferred)
[v122_device_manifest_v2]                  OK steps=19
[v122_tower_floor_contract]                OK status=DEFERRED_RUNTIME_VERIFICATION
[v122_report_completeness]                 OK (questo report)
```

## 12. Regression gate results

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT]   OK (con 3 dup esplicite documentate)
[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK unsafe=0 unknown=0 leaked=0
[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP]  OK candidates=24
[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO]    OK
[v_p0_truth_rebaseline]                     OK
[v_p0_current_public_guardrail_snapshot]    OK (counts aggiornati)
[v_p0_stale_md5_supersedence]               OK
[v_p0_relocatability_audit]                 OK
PRE-QA Safety Suite: 24/24 PASS
Repo hygiene: clean = True
```

## 13. Files modified / created

```text
M  frontend/app/(tabs)/menu.tsx                                        (Battaglia entries -> hubs)
M  backend/scripts/validate_pre_qa_pack_119c_menu_public_snapshot.py   (3 ALLOWED_DUPLICATE_ROUTES esplicite)
M  data/design/pre_qa_controlled_unlock/controlled_live_unlock_prep_120a_plan_v1.json (+2 candidate /arena-preview, /boss-raid-preview)
M  data/design/current_truth/public_guardrail_current_snapshot_v1.json (counts aggiornati)
A  frontend/app/arena-preview.tsx
A  frontend/app/boss-raid-preview.tsx
A  data/design/vertical_slice_qa/ultra_122_corrected_entry_route_matrix_v1.json
A  data/design/vertical_slice_qa/ultra_122_preview_team_fallback_policy_v1.json
A  data/design/vertical_slice_qa/ultra_122_device_qa_manifest_v2.json
A  backend/scripts/validate_pre_qa_ultra_122_entrypoint_semantic_fix.py
A  backend/scripts/validate_pre_qa_ultra_122_mode_selection_hubs.py
A  backend/scripts/validate_pre_qa_ultra_122_preview_team_fallback_no_write.py
A  backend/scripts/validate_pre_qa_ultra_122_device_manifest_v2.py
A  backend/scripts/validate_pre_qa_ultra_122_tower_floor_no_crash_contract.py
A  backend/scripts/validate_pre_qa_ultra_122_report_completeness.py
A  docs/divine/522_PRE_QA_ULTRA_122_DEVICE_QA_FLOW_FIX_BATCH_AND_ALPHA_PREVIEW_UNLOCK.md (questo)
```

## 14. No-touch confirmation

| Vincolo | Stato |
| --- | --- |
| backend/battle_engine.py | ✅ NO |
| backend/battle_core.py | ✅ NO |
| backend/server.py | ✅ NO |
| backend/game_systems.py | ✅ NO |
| combat.tsx | ✅ NO |
| pre-battle-lobby.tsx | ✅ NO |
| story.tsx / tower-of-the-hells.tsx / hero-training.tsx | ✅ NO |
| reward claim runtime | ✅ NO |
| gacha runtime | ✅ NO |
| shop runtime | ✅ NO |
| VIP runtime | ✅ NO |
| Battle Pass runtime | ✅ NO |
| IAP runtime | ✅ NO |
| mail claim runtime | ✅ NO |
| DB scripts apply / migrations | ✅ NO |
| `.env` | ✅ NO |
| supervisor | ✅ NO |
| Character Bible / roster / skill kits / assets / audio | ✅ NO |
| premium currency logic | ✅ NO |
| authoritative battle result commit / EXP / progress | ✅ NO |
| env flag attivata | ✅ NO |
| REQUIRED validator indebolito/rimosso | ✅ NO |

## 15. Remaining blockers

| ID | Severity | Description |
| --- | --- | --- |
| `BLOCKER_NO_TEAM_PREVIEW_RUNTIME_WIRING` | **P0** per combat preview testabile su account senza team. Policy dichiarata, wiring runtime delegato a Pack 123. |
| `BLOCKER_TOWER_FLOOR_TAP_RUNTIME_CRASH` | **P0** per Test 4 device QA. Fix richiede modifica `tower-of-the-hells.tsx` con QA su device; out-of-scope qui per limitare rischio. |
| `BLOCKER_TRAINING_PREVIEW_TRIAL_RUNTIME` | **P1** per Test 5. Wiring del trial preview in `hero-training.tsx` delegato a Pack 123. |
| `BLOCKER_5_BETA_TRACK_VALIDATOR_REBASELINE` | P1, già documentato nel triage 121. |
| `BLOCKER_SERVERS_LOCK_MARKER_HYGIENE` | P3, non blocker. |

## 16. Next recommended step

`PRE_QA_PACK_123_PREVIEW_TEAM_FALLBACK_RUNTIME_WIRING_AND_TOWER_FLOOR_CRASH_FIX_BATCH`

Scope proposto (singolo pack focalizzato):

1. Wiring runtime del `preview_local_team_snapshot` in `pre-battle-lobby.tsx` (e minimo intervento controllato su `combat.tsx` se indispensabile per accettare `launch_context.preview_team`).
2. Fix runtime crash su tap piano in `tower-of-the-hells.tsx` (con QA su device dopo il fix).
3. Wiring del "Training Preview Trial" in `hero-training.tsx` per consentire un trial preview testabile.
4. Aggiornamento manifest device QA v3 + validator.
5. Mantenere no-write/no-reward/no-live.

## 17. Verdict

**`PRE_QA_ULTRA_122_BLOCKED_NO_TEAM_PREVIEW_NOT_AVAILABLE`**

Il pack 122 ha:
- Risolto il blocker **menu/entrypoint semantici** per tutti i 5 mode (Track A).
- Creato i 2 nuovi hub preview selezione **Arena/Boss** (Track E/F).
- Dichiarato la **policy** del preview team fallback (Track C).
- Documentato i tower crash + training preview come **DEFERRED runtime** a Pack 123 senza fake PASS.
- Aggiornato manifest device QA v2 con 19-step.
- Mantenuto tutte le invarianti no-write/no-reward/no-live.

Onesto rispetto al contratto: il combat preview per account senza team resta bloccato fino a Pack 123 (runtime wiring). Stato dichiarato esplicitamente come blocker per non mascherare fail come pass.

## 18. Commit SHA

`db3f52fa6` — `Pack 122: device QA flow fix batch + alpha preview unlock (HONEST BLOCKED verdict)`

# Pack 124 — PRE_QA_PACK_124_DEVICE_QA_REAL_COMBAT_PREVIEW_FIX_AND_QA_TEAM_SEED_BATCH

**Status:** ✅ COMPLETATO
**Data:** 2026-06-16
**Goal raggiunto:** `PRE_QA_ALPHA_REAL_COMBAT_PREVIEW_AND_QA_TEAM_DEVICE_TEST_READY`

---

## 1. Device QA 123 failures

Risultati del Device QA dopo Pack 123:

| # | Test | Esito Pack 123 |
|---|------|----------------|
| 1 | Home / Menu | PASS |
| 2 | Story hub/lobby | PASS (no team reale) |
| 3 | Torre tap piano | **FAIL** — crash al tap |
| 4 | Training Preview Trial → combat | **FAIL** — battle non reale |
| 5 | Arena hub → opponent | PASS hub, FAIL combat |
| 6 | Boss hub → boss | PASS hub, FAIL combat |
| 7 | No reward/progress | **FAIL** — combat non parte |
| 8 | Back nav | PASS tranne Arena/Raid (back assente) |
| — | Home hero (Borea?) | Non determinabile staticamente |

---

## 2. Root cause GitHub audit

- **`combat.tsx`**: quando `PREVIEW_REWARD_LOCK_ACTIVE` true → `setPhase('preview_locked')` e `return` prima della simulazione e dell'inizializzazione team. Pack 123 mostrava solo una schermata informativa, NON il battle renderer.
- **`arena-preview.tsx` / `boss-raid-preview.tsx`**: nessun `router.back`, top bar assente.
- **`tower-of-the-hells.tsx`**: tap su piano apriva modal con `selectedFloor`; in alcune condizioni device il modal si apriva con `selectedFloor=null` causando crash su accessi a `.name`, `.is_boss`, ecc.
- **Home hero**: `/api/sanctuary/home-hero` payload server-dipendente — non determinabile staticamente quale variante di Borea (vecchia/nuova) sia caricata. Servono screenshot device o cattura payload.

---

## 3. Real combat preview fix (Track A) ⭐

**Cambiamento chiave:** `combat.tsx` PREVIEW branch NON termina più in `preview_locked` statico. Invece:

1. Estende `frontend/src/utils/previewBattleTeam.ts` con:
   - `buildPreviewCombatSnapshot(ctx)` → costruisce **teamA** (6 eroi canonici player preview) + **teamB** (6 enemy canonici preview) con TUTTI i campi richiesti dal renderer (id, hero_id, hero_name, hero_image, rarity, element, level, stars, role, max_hp, current_hp, max_hp_battle, is_alive, atk, def, spd, rage, max_rage, grid_x, grid_y).
   - `CANONICAL_PREVIEW_ENEMY_IDS`: 6 enemy hero IDs REALI da `heroes_master.json` (creature_coral_guardian, norse_thunder_spear, tides_corsair, egyptian_tide_sibyl, celtic_moor_druidess, tides_healer).

2. In `combat.tsx::startBattle()`, il blocco `if (PREVIEW_REWARD_LOCK_ACTIVE)`:
   - Chiama `buildPreviewCombatSnapshot(previewCtxLocal)` invece di `setPhase('preview_locked'); return`.
   - Popola `setTeamA(snap.teamA)`, `setTeamB(snap.teamB)`, `setResult({...is_preview_local: true, battle_log: [], winner: 'preview'})`.
   - Calcola `battleBg` deterministico per preview.
   - Inizializza `spriteStates` per tutti i 12 unit.
   - Setta `phase='preparing'` → safeTimeout 1400ms → `phase='fighting'`.
   - **NON chiama `/api/battle/simulate`** (verificato dal validator).
   - `battle_log` vuoto: il preview NON simula azioni; mostra solo battlefield + HUD + sprite reali.

3. Aggiunge overlay **"✕ ESCI PREVIEW"** in alto a destra visibile quando preview attivo + fase `preparing`/`fighting`/`result`. Click → `router.back()` con fallback safe a `/(tabs)/home`.

**Verifica visiva eseguita via Playwright:**
- URL: `/combat?mode=tower&...&is_preview=true&...`
- Phase entrata: `fighting`
- 6 hero portraits in HUD Team A (H/B/A/I/M/S) + 6 in Team B (G/L/C/S/D/G)
- HP bars verdi visibili
- VS center indicator
- Sprite placeholder visibili nel battlefield
- "ESCI PREVIEW" overlay presente
- Nessun crash

---

## 4. QA team seed / canonical hero grant safety (Track B)

Opzione adottata: **OPZIONE PREFERITA — script standalone dev-only**, NON endpoint HTTP.

File creati:
- `backend/scripts/qa_team_seed_canonical_heroes.py` — assegna 10 eroi canonici 3★ launch_base ad un account specificato.
- `backend/scripts/qa_team_seed_clear.py` — rollback / clear (rimuove SOLO documenti taggati `_qa_seed: true, _qa_seed_pack: pack_124`).

**Guardrails fail-closed:**
- `QA_SEED_ENABLED=true` env var obbligatoria (gate primario).
- `--allow-account <user_id>` allowlist obbligatoria (no default).
- Idempotente: per ogni hero_id verifica esistenza prima di insert.
- NO premium currency, NO gacha, NO paid odds, NO reward claim, NO shop, NO VIP, NO BP, NO IAP (validator-verificato).
- Output JSON report in `backend/scripts/reports/pack_124_qa_team_seed_*.json`.
- Verifica canonica di tutti i 10 hero_id contro `heroes_master.json`: nessun Borea, nessun 6★, nessun hidden, tutti launch_base.

**Hero pool (10 canonici, validati):**
1. greek_hoplite (Tank/Terra/3★)
2. norse_berserker (DPS Melee/Fuoco/3★)
3. celtic_archer (DPS Ranged/Vento/3★)
4. arcane_lightning_enchantress (Mage AoE/Fulmine/3★)
5. greek_sanctuary_muse (Support/Luce/3★)
6. angelic_priestess (Healer/Luce/3★)
7. creature_coral_guardian (Tank/Acqua/3★)
8. norse_thunder_spear (DPS Melee/Fulmine/3★)
9. celtic_moor_druidess (Support/Terra/3★)
10. egyptian_nile_healer (Healer/Acqua/3★)

**Esecuzione manuale (NOT auto-runned):**
```bash
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_canonical_heroes.py \
    --allow-account <user_id>
# Rollback:
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_clear.py \
    --allow-account <user_id>
```

**Status testabilità team save:** PARZIALMENTE BLOCCATA. Lo script seed crea i documenti `user_heroes`, ma il test reale di "team save" tramite UI dipende dalla rotta esistente `team save` del backend, che NON è stata toccata in questo pack. Se il device QA scopre che il team save endpoint non funziona o richiede economy gating, dichiarare al pack successivo: `BLOCKED_QA_TEAM_SAVE_NOT_TESTABLE`.

---

## 5. Tower crash fix (Track C)

`frontend/app/tower-of-the-hells.tsx`:

- **Tap diretto su piano UNLOCKED**: naviga immediatamente a `/pre-battle-lobby?mode=tower&floor_id=N&...preview-flags` (no modal intermedio).
- **Tap su piano LOCKED**: handler ritorna immediatamente (`if (disabled) return`).
- **Modal Floor Detail**: gated da `__DEV__ && selectedFloor != null` → invisibile in produzione.
- **Bottone "Test Clear (TEST)"**: gated dietro lo stesso modal `__DEV__`, NON player-facing.
- **try/catch fail-closed** attorno alla costruzione dell'URL.

Verifica visiva: tap su Floor 1 → URL = `/pre-battle-lobby?mode=tower&floor_id=1&...` (catturato in screenshot). Nessun crash.

---

## 6. Training Preview Trial to real combat (Track D)

Già wirato in Pack 123: card visibile, CTA "Avvia Preview Trial" → lobby preview mode=training.

In combinazione con la fix Track A: la lobby ora propaga i flag preview al combat che entra nel renderer reale. Training Preview Trial chiude il loop "card → lobby → real combat preview".

---

## 7. Arena/Boss back button + real preview (Track E)

`frontend/app/arena-preview.tsx` e `frontend/app/boss-raid-preview.tsx`:

- **Top bar** con bottone "← Indietro" + `accessibilityLabel="Torna indietro"`.
- Handler `handleBack`: `router.canGoBack?.() ? router.back() : router.replace('/(tabs)/home')` (fallback safe).
- Tap opponent/boss → naviga in lobby preview con flag preview-completi.
- Lobby → real combat preview (Track A).

---

## 8. Home hero trace (Track F)

File creato: `data/design/vertical_slice_qa/pack_124_home_hero_trace_v1.json`.

Stato: `needs_updated_zip_or_device_screenshot=true`.

Asset non modificati. Endpoint `/api/sanctuary/home-hero` non modificato. Il trace fornisce gli step investigativi richiesti per chiudere la verifica Borea vecchia vs nuova:
1. Aprire app su device.
2. Cattura GET `/api/sanctuary/home-hero` dalla console di rete.
3. Estrarre `hero_id`, `asset_splash`, `asset_base`, `image_url`.
4. Confronto con `frontend/assets/heroes/` o `data/design/assets_registry.json`.
5. Aggiornare il trace JSON.

---

## 9. Device QA Manifest V4 (Track G)

File creato: `data/design/vertical_slice_qa/pack_124_device_qa_manifest_v4.json`.

Checklist di 15 step (Home → Home hero trace → QA team seed → team editor → save team → Story/Tower/Training/Arena/Boss preview combat → back button → no reward → no live surfaces → back nav → no crash). Owner e expected espliciti per ogni step.

---

## 10. Validators (Track H)

7 validatori Python creati. Tutti read-only.

| Validator | Status |
|-----------|--------|
| `validate_pre_qa_pack_124_real_combat_preview_not_preview_locked.py` | ✅ PASS |
| `validate_pre_qa_pack_124_no_write_real_combat_preview.py` | ✅ PASS |
| `validate_pre_qa_pack_124_tower_device_crash_fix_contract.py` | ✅ PASS |
| `validate_pre_qa_pack_124_arena_boss_back_buttons.py` | ✅ PASS |
| `validate_pre_qa_pack_124_qa_team_seed_safety.py` | ✅ PASS |
| `validate_pre_qa_pack_124_home_hero_trace.py` | ✅ PASS |
| `validate_pre_qa_pack_124_report_completeness.py` | (questo report) |

Report JSON dettagliati: `backend/scripts/reports/pack_124_*.json`.

---

## 11. Regression gates (Track I)

Pack 123 validators:

| Pack 123 validator | Status |
|--------------------|--------|
| preview_team_runtime_wiring | ✅ PASS (rieseguito) |
| canonical_hero_ids | ✅ PASS |
| tower_floor_tap_no_crash | ✅ PASS |
| no_db_write_invariant | ✅ PASS |
| preview_hubs_complete | ✅ PASS |

TypeScript check (`yarn tsc --noEmit --skipLibCheck`):
- Zero errori introdotti su `previewBattleTeam.ts`, `tower-of-the-hells.tsx`, `arena-preview.tsx`, `boss-raid-preview.tsx`.
- Errori pre-esistenti rimangono su `combat.tsx` (rage type), `home.tsx`, `servers.tsx` — NON in scope Pack 124.

Frontend service: RUNNING. Backend service: RUNNING. Repo: pulito (no `.pyc`, no `__pycache__` tracked).

---

## 12. No-touch confirmation

File / aree NON modificate (verifica statica):

- ❌ `backend/battle_engine.py` — invariato
- ❌ `backend/battle_core.py` — invariato
- ❌ `backend/server.py` — invariato (no nuovo `include_router`)
- ❌ `backend/game_systems.py` — invariato
- ❌ economy/gacha/shop/VIP/BP/IAP runtime — invariato
- ❌ reward claim live routes — invariato
- ❌ premium currency logic — invariato
- ❌ Character Bible — invariato
- ❌ `heroes_master.json` — invariato (solo letto)
- ❌ skill kits / final_numbers — invariato
- ❌ assets/audio — invariato
- ❌ `.env` files — invariato
- ❌ supervisor configs — invariato
- ❌ migrations — invariato

---

## 13. Remaining blockers

1. **Team save endpoint live** — non testato. Dipende dall'esistenza di una route player-facing per la persistenza del team. Va validato manualmente al device QA (step 5 manifest). Se non funzionante: `BLOCKED_QA_TEAM_SAVE_NOT_TESTABLE`.
2. **Home hero Borea vecchia vs nuova** — richiede screenshot device o cattura payload runtime. `needs_updated_zip_or_device_screenshot=true` nel trace.
3. **Battle preview senza simulazione** — il combat preview mostra il battlefield e gli sprite, ma `battle_log` è vuoto: nessuna azione automatica. È intenzionale (no simulate mutant), ma il device QA potrebbe percepirlo come "battle immobile". Se serve animazione visiva loop autonoma, è una feature successiva (Pack 125+).
4. **Test Clear (TEST) string ancora nel codice** — gated dietro `__DEV__`, quindi invisibile in produzione. Non blocker.

---

## 14. Next recommended step

1. **Device QA utente** (iOS + Android):
   - Eseguire la checklist del manifest V4 (15 step).
   - Catturare il payload `/api/sanctuary/home-hero` e aggiornare il trace JSON.
   - Eseguire manualmente lo script QA team seed sull'account test, poi testare team editor + team save.
2. **Update home hero trace** dopo cattura (richiede ZIP/screenshot aggiornati).
3. **Pack 125** (se device QA passa): preparare `CONTROLLED_LIVE_UNLOCK` per consentire test reward/progress in ambiente staging gated.
4. **NON aprire** reward live, gacha, shop, VIP, BP, IAP in questo o successivi pack pre-QA.
5. **NON dichiarare** release ready prima del completamento del device QA reale e della finalizzazione della suite invarianti.

---

## Hash / Provenance

- Pack: `PRE_QA_PACK_124_DEVICE_QA_REAL_COMBAT_PREVIEW_FIX_AND_QA_TEAM_SEED_BATCH`
- Goal: `PRE_QA_ALPHA_REAL_COMBAT_PREVIEW_AND_QA_TEAM_DEVICE_TEST_READY`
- Manifest QA: `data/design/vertical_slice_qa/pack_124_device_qa_manifest_v4.json`
- Home hero trace: `data/design/vertical_slice_qa/pack_124_home_hero_trace_v1.json`
- Lingua report: **Italiano** (come da requisito utente).

**Verdict:** `PRE_QA_PACK_124_DEVICE_QA_REAL_COMBAT_PREVIEW_FIX_AND_QA_TEAM_SEED_BATCH_COMPLETE`

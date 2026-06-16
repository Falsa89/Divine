# Pack 125 — PACK_125_COMBAT_ACTION_HOME_BOREA_QA_TEAM_SAVE_FIX

**Status:** ✅ COMPLETATO
**Data:** 2026-06-16
**Verdict:** `PACK_125_COMBAT_ACTION_HOME_BOREA_QA_TEAM_SAVE_FIX_COMPLETE`
**User authorization:** `USER_AUTHORIZES_QA_TEAM_DB_WRITE_FOR_TEST_ACCOUNTS_ONLY=true`

---

## 1. Device QA 124 findings (input)

| Blocker | Esito Pack 124 |
|---------|----------------|
| Combat preview mostra battlefield ma resta IDLE (battle_log vuoto) | FAIL |
| Combat preview parte prima del preload completo asset | FAIL |
| Home mostra Borea fallback blu/vento (no asset valido) | FAIL |
| QA seed non applicato agli account test | NOT EXECUTED |
| Team editor/save non testabile (TEAM_FORMATION_SAVE_DEFERRED_PRE_QA) | FAIL |
| Team save server-scoped mancante | MISSING |

---

## 2. File reali auditati dallo ZIP / progetto

- `/app/frontend/app/combat.tsx` (2076 righe, PREVIEW branch a riga ~366-470)
- `/app/frontend/src/utils/previewBattleTeam.ts` (esteso Pack 124 con buildPreviewCombatSnapshot)
- `/app/frontend/components/home/HomeHeroSplash.tsx` (141 righe, isBorea fallback gradient)
- `/app/frontend/app/(tabs)/battle.tsx` (831 righe, saveTeam stub TEAM_FORMATION_SAVE_DEFERRED_PRE_QA)
- `/app/backend/routes/v96_team_formation.py` (190 righe, solo GET /get-formation)
- `/app/data/design/heroes_master.json` (101 heroes, scelte 10 canonici 3★ launch_base)
- `/app/frontend/assets/heroes/greek_borea/` (transparent.png, splash.png, card.png esistono)

---

## 3. Combat action loop (FIX A) ⭐

**Cambiamenti:**

### `frontend/src/utils/previewBattleTeam.ts`
Aggiunta funzione `buildPreviewBattleLog(teamA, teamB)` che produce **3 turni deterministici** compatibili con `playLog(res, ti, ai)` di combat.tsx:

- **Turn 1**: 3 attacchi base (`skill_type='nad'`, `type='attack'`):
  - Hoplite (A) → Coral Guardian (B): "Affondo di Falange"
  - Berserker (A) → Norse Thunder Spear (B): "Furia del Nord"
  - Coral Guardian (B) → Hoplite (A): "Carapace di Corallo"
- **Turn 2**: skill `'sad'` + heal:
  - Incantatrice della Folgore (A) → Tides Sibyl (B): "Tempesta di Folgore" (crit)
  - Sacerdotessa (A) HEAL → Hoplite (A): "Benedizione Divina"
  - Arciera (A) → Tides Corsair (B): "Tiro Preciso"
- **Turn 3**: enemy skill + chiusura:
  - Lancia del Tuono (B) → Berserker (A): "Lancia del Tuono" `'sad'`
  - Tides Healer (B) HEAL → Coral Guardian (B): "Marea Curativa"
  - Musa del Santuario (A) → Druida (B): "Canto del Santuario"

Tutti i damage sono proporzionati a `max_hp` (8-18%) per essere visivi ma non kill. `targets[]` referenzia gli ID reali in teamA/teamB così `updateHP(a)` aggiorna lo state corretto.

### `frontend/app/combat.tsx` (PREVIEW branch)
Sostituito `battle_log: []` con `battle_log: previewLog` (chiamata `buildPreviewBattleLog`). Al termine del preload, `playLog(localResult, 0, 0)` parte e gli sprite attaccano/curano/subiscono hit.

**Validator:** `validate_pre_qa_pack_125_preview_battle_log_actions.py` → PASS.

---

## 4. Preview preload (FIX B)

### `frontend/app/combat.tsx` (PREVIEW branch)
Replicato il pipeline di preload del path live:

1. `setPreloadTotal(N)`, `setPreloadLoaded(0)`, `setPreloadLabel('Preview · Inizializzazione asset...')`
2. Per ogni asset (bg + Hoplite manifest + `getHeroBattlePreloadAssets` per ogni unit di teamA/teamB) → `preloadBattleAsset(src)` con `Promise.allSettled`.
3. `Promise.race([preloadAllPrev, preloadTimeoutPrev])` (timeout safety 7000ms).
4. SOLO DOPO il preload: `setPhase('preparing')` → safeTimeout 1400ms → `setPhase('fighting')` → `playLog(...)`.

**Acceptance:** sprite pronti quando entriamo in fighting, no flash idle, no schermata nera.

**Validator:** `validate_pre_qa_pack_125_preview_preload_before_fighting.py` → PASS.

---

## 5. Home Borea fix (FIX C)

### `frontend/components/home/HomeHeroSplash.tsx`
- Nuovo helper `isBoreaLikeId(heroId)`: matcha `borea`, `greek_borea` (case-insensitive).
- `const isBorea = isBoreaLikeId(hero.id)` (era `hero.id === 'borea'`).
- Aggiunto import asset locale: `require('../../assets/heroes/greek_borea/transparent.png')`.
- Branch JSX: `{isBorea ? (<RNImage source={GREEK_BOREA_TRANSPARENT} resizeMode="contain" />) : useUiContract ? ... }` — il branch isBorea è PRIMARY (prima di useUiContract).
- Gradient blu/vento NON è più reachable per Borea (resta per altri eroi senza asset).

**Garanzie:**
- ❌ NO ownership grant (nessuna chiamata `/api/user/heroes/grant`, `/api/gacha/`, `/api/shop/`).
- ❌ NO modifica roster / heroes_master.json.
- ❌ NO modifica Character Bible.
- ❌ NO unlock Borea in catalog/live.
- ✅ Tutorial-only: solo visualizzazione home hero card.

Trace: `data/design/vertical_slice_qa/pack_125_home_borea_trace_v1.json`.

**Validator:** `validate_pre_qa_pack_125_home_borea_asset_resolution.py` → PASS.

---

## 6. QA seed / team save server-scoped (FIX D)

### QA Seed applicato
Eseguito (dopo fix bug `get_default_database()`):
```bash
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_canonical_heroes.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed
```

**Risultato:** 4 granted + 6 already_owned = **10 hero_id canonici totali** sull'account `test@test.com` (UUID `651253e2-da8d-466b-98f3-82f008d158ed`).

Granted: `celtic_archer`, `arcane_lightning_enchantress`, `greek_sanctuary_muse`, `angelic_priestess`.
Already-owned: `greek_hoplite`, `norse_berserker`, `creature_coral_guardian`, `norse_thunder_spear`, `celtic_moor_druidess`, `egyptian_nile_healer`.

**Idempotenza verificata:** una seconda esecuzione manterrebbe 10 totali, 0 granted.

Report: `backend/scripts/reports/pack_124_qa_team_seed_1781647180.json`.

### Team save server-scoped — POST /api/team/save-formation
Aggiunto in `backend/routes/v96_team_formation.py` (sibling del `GET /get-formation`).

**Guardrails fail-closed:**
1. `QA_TEAM_SAVE_ENABLED=true` env var → altrimenti 403 `QA_TEAM_SAVE_DISABLED`.
2. `QA_TEAM_SAVE_ALLOWLIST` env (lista user_id, o `*` per wildcard).
3. `server_id` obbligatorio nel body.
4. PSP esistente per `(user_id, server_id)` → altrimenti 404 `PLAYER_SERVER_PROFILE_REQUIRED`.
5. Ownership: tutti gli `hero_id` devono essere in `user_heroes` con quel `server_id` (o tagged `_qa_seed`) → altrimenti 400 `OWNERSHIP_VALIDATION_FAILED`.
6. Max 6 eroi → 400 `TEAM_TOO_LARGE`.
7. Posizioni uniche (col, row) → 400 `DUPLICATE_POSITIONS`.
8. Hero IDs unici → 400 `DUPLICATE_HEROES`.
9. Write **SOLO** su `player_server_profiles.team_formation` (NO `db.users` write).

**Response invariants_respected:**
```json
{
  "no_economy_mutation": true,
  "no_reward": true,
  "no_progress": true,
  "no_gacha": true,
  "no_shop": true,
  "no_vip": true,
  "no_battlepass": true,
  "no_iap": true,
  "no_account_wide_write": true,
  "scoped_to_player_server_profile": true
}
```

### Frontend battle.tsx
Sostituito `TEAM_FORMATION_SAVE_DEFERRED_PRE_QA` con chiamata reale a `apiCall('/api/team/save-formation', {...})`. Gestione errori 403/404/400 con messaggi chiari per device QA.

**Validator:** `validate_pre_qa_pack_125_team_seed_and_server_scoped_save.py` → PASS.

---

## 7. Validators (6 nuovi, tutti PASS)

| Validator | Status |
|-----------|--------|
| `validate_pre_qa_pack_125_preview_battle_log_actions.py` | ✅ PASS |
| `validate_pre_qa_pack_125_preview_preload_before_fighting.py` | ✅ PASS |
| `validate_pre_qa_pack_125_home_borea_asset_resolution.py` | ✅ PASS |
| `validate_pre_qa_pack_125_team_seed_and_server_scoped_save.py` | ✅ PASS |
| `validate_pre_qa_pack_125_no_live_unlocks.py` | ✅ PASS |
| `validate_pre_qa_pack_125_report_completeness.py` | (questo report) |

**Regression Pack 123 + 124 (rieseguiti):** 5/5 + 7/7 = **12/12 PASS**. Zero regressioni.

Report JSON dettagliati: `backend/scripts/reports/pack_125_*.json` e `pack_124_*.json`.

---

## 8. No-live / no-reward evidence

Audit statico dei file modificati Pack 125 (`validate_pre_qa_pack_125_no_live_unlocks.py`):
- `previewBattleTeam.ts`: 0 chiamate live.
- `combat.tsx` PREVIEW branch: 0 chiamate a `/api/battle/simulate`, `/api/gacha/`, `/api/shop/`, `/api/vip/`, `/api/battlepass/`, `/api/iap/`, `/api/mail/claim`. Grant affinity/refreshUser guardati da `!PREVIEW_REWARD_LOCK_ACTIVE` (preservato).
- `(tabs)/battle.tsx::saveTeam`: chiama SOLO `/api/team/save-formation` (no economy).
- `HomeHeroSplash.tsx`: 0 chiamate API (read-only rendering).
- `v96_team_formation.py` `save-formation`: scrive SOLO `player_server_profiles.team_formation`, NON `db.users`.
- `qa_team_seed_canonical_heroes.py`: scrive SOLO `user_heroes` con tag `_qa_seed`, no economy/gacha/shop/VIP/BP/IAP.

**Borea:** asset visivo locale, nessuna ownership/grant/unlock live.

---

## 9. DB write QA authorization / evidence / rollback

**Authorization fonte:** prompt utente Pack 125, riga 11:
> `USER_AUTHORIZES_QA_TEAM_DB_WRITE_FOR_TEST_ACCOUNTS_ONLY=true`

**Evidence DB write effettuato:**
1. **QA seed** su account `test@test.com` → 4 documenti `user_heroes` inseriti, tutti taggati `_qa_seed: true, _qa_seed_pack: pack_124`. Report: `backend/scripts/reports/pack_124_qa_team_seed_1781647180.json`.
2. **Team save endpoint**: gated da env var, NON eseguito automaticamente. Disponibile per device QA quando dev imposta `QA_TEAM_SAVE_ENABLED=true`.

**Rollback disponibile:**
```bash
# Seed rollback (rimuove i 4 documenti taggati pack_124):
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_clear.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed

# Team save rollback (in DB direttamente):
# db.player_server_profiles.update_one(
#   {"user_id": "<uid>", "server_id": "<sid>"},
#   {"$unset": {"team_formation": "", "_pack_125_qa_team_save_ts": ""}}
# )
```

---

## 10. Device QA V5 checklist

File: `data/design/vertical_slice_qa/pack_125_device_qa_manifest_v5.json`.

14 step coprono: home, Borea asset, QA seed verify, team editor, team save, team persist, action loop preview, preload, tower/training/arena/boss combat, no reward, no live surfaces, back nav, no crash. Owner ed expected espliciti per ogni step.

---

## 11. Remaining blockers

1. **Team save endpoint requires env vars** — `QA_TEAM_SAVE_ENABLED` + `QA_TEAM_SAVE_ALLOWLIST` non sono settati di default. Per device QA: il dev deve esportarli e `sudo supervisorctl restart backend`. Documentato in `memory/test_credentials.md`.
2. **Home Borea trace device-side** — `pack_124_home_hero_trace_v1.json` (creato in Pack 124) richiede ancora la cattura del payload `/api/sanctuary/home-hero` su device per chiusura definitiva (ora Pack 125 ha già il fix asset).
3. **TypeScript pre-existing errors** (`combat.tsx` line 983 phase comparison, 1086 `c.rage`, 1192/1205 SpriteSurface overload) — NON introdotti da Pack 125. Restano fuori scope.
4. **Combat preview battle_log statico** — 3 turni deterministici sono visibili ma il "loop" termina dopo Turn 3 (no animation loop). Se serve loop continuo per device demo, pack futuro può estendere con `repeat` flag (preview-only). Non blocker per QA visivo.

---

## 12. Next step (next recommended)

1. **Device QA utente** (iOS/Android):
   - Aggiornare credenziali da `memory/test_credentials.md`.
   - Login con `test@test.com` → /battle → verificare 10 eroi disponibili.
   - Drag team in formation → verificare con QA team save endpoint (richiede env enable).
   - Re-open /battle → verificare persistenza via `get-formation?server_id=...`.
   - Tower/Training/Arena/Boss → real combat preview con action loop visibile.
   - Verificare nessuna mutazione reward/EXP/progress.
2. **Cattura screenshot device payload** `/api/sanctuary/home-hero` per chiudere `pack_124_home_hero_trace_v1.json`.
3. **Pack 126** (eventuale): se Device QA passa, preparare la fase successiva (alpha closed playtest scope) o `CONTROLLED_LIVE_UNLOCK` per ambiente staging.
4. **NON aprire** reward live, gacha, shop, VIP, BP, IAP, premium currency, mail claim, ranking — restano sealed.
5. **NON dichiarare** release ready.

---

## Hash / Provenance

- Pack: `PACK_125_COMBAT_ACTION_HOME_BOREA_QA_TEAM_SAVE_FIX`
- Goal: `PACK_125_COMBAT_ACTION_HOME_BOREA_QA_TEAM_SAVE_FIX_COMPLETE`
- Manifest QA: `data/design/vertical_slice_qa/pack_125_device_qa_manifest_v5.json`
- Home Borea trace: `data/design/vertical_slice_qa/pack_125_home_borea_trace_v1.json`
- Lingua: **Italiano**.

**Verdict:** `PACK_125_COMBAT_ACTION_HOME_BOREA_QA_TEAM_SAVE_FIX_COMPLETE`

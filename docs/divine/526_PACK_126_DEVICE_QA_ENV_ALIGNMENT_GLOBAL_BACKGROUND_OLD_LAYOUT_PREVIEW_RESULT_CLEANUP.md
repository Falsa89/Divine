# Pack 126 — Device QA Env Alignment + Global Combat Background + Old Battle Layout + Preview Result Cleanup

**Status:** ✅ COMPLETATO (static + DB alignment) · device QA V6 pending utente
**Data:** 2026-06-16
**Verdict:** `PACK_126_DEVICE_QA_ENV_ALIGNMENT_GLOBAL_BACKGROUND_OLD_LAYOUT_PREVIEW_RESULT_COMPLETE`
**User authorization:** `USER_RECONFIRMS_QA_TEAM_DB_WRITE_FOR_TEST_ACCOUNTS_ONLY=true`

---

## 1. Device QA Pack 125 findings (input)

| Esito | Test |
|-------|------|
| FAIL | Account non vede 10 QA heroes su device. |
| FAIL | Team save non testabile (heroes missing). |
| FAIL | Battle background mancante in Training (e in TUTTI i preview combat). |
| FAIL | Layout battaglia regredisce: 5/6 heroes visibili, scala compressa. |
| FAIL | Post-battle preview mostra "+1 EXP" figurativo. |
| PASS | Home/Borea, Tower preview, Arena/Raid hubs. |

---

## 2. Files audited

- `frontend/app/combat.tsx` (2122 righe — PREVIEW branch + post-battle)
- `frontend/src/utils/previewBattleTeam.ts` (esteso 6v6 layout)
- `frontend/components/ui/battleBackgrounds.ts` (mode fallback)
- `frontend/components/battle/buildPostBattleSummary.ts` (preview short-circuit)
- `frontend/components/home/HomeHeroSplash.tsx` (no change, Pack 125 ok)
- `backend/routes/v96_team_formation.py` (save-formation gate, Pack 125 ok)
- `backend/scripts/qa_team_seed_canonical_heroes.py` (esteso `--server-id`)
- `data/design/heroes_master.json` (101 heroes, riferimento canonical)
- DB `divine_waifus` — users/user_heroes/player_server_profiles

---

## 3. DB/backend/user/server alignment evidence

- **Email:** test@test.com
- **User UUID:** `651253e2-da8d-466b-98f3-82f008d158ed`
- **Active server_id su device:** `s1` (353 heroes pre-pack, 1 PSP).
- **Secondario:** `qa-eu-01` (3 heroes, PSP separato).
- **DB:** `divine_waifus`. **MONGO_URL:** preso da `backend/.env`.
- **Backend base URL device:** `EXPO_BACKEND_URL` (mappato a porta 8001 via ingress).

**Root cause Pack 125 seed failure:** lo script seed non aveva `--server-id`. I 4 documenti inseriti avevano `server_id=<none>` → invisibili alla UI che filtra per `server_id`.

**Pre-pack su `s1`:** 2/10 canonical present (greek_hoplite, norse_berserker).
**Post-pack su `s1`:** 10/10 canonical present.

---

## 4. QA seed before/after

**Pack 126 fix:** aggiunto `--server-id` allo script seed; idempotency scoped su `(user_id, hero_id, server_id)`.

Esecuzione:
```bash
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_canonical_heroes.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed --server-id s1
```

Risultato:
- **granted:** 8 (celtic_archer, arcane_lightning_enchantress, greek_sanctuary_muse, angelic_priestess, creature_coral_guardian, norse_thunder_spear, celtic_moor_druidess, egyptian_nile_healer)
- **skipped (already_owned su s1):** 2 (greek_hoplite, norse_berserker)
- **Totale canonical su s1:** **10/10**

Snapshot:
- `pack_126_state_before_*.json`: user_heroes=353, exp=20060451, qa_seed=0
- `pack_126_state_after_seed_*.json`: user_heroes=361 (+8), exp invariato, gold invariato, qa_seed=8

---

## 5. Team save env / runtime proof

Endpoint `POST /api/team/save-formation` (Pack 125) verificato runtime:
- Reachable via `curl -X POST http://localhost:8001/api/team/save-formation`
- Senza auth → 401 "Token mancante" (gate auth funziona).
- Con auth ma senza `QA_TEAM_SAVE_ENABLED=true` → 403 `QA_TEAM_SAVE_DISABLED` (gate env fail-closed).
- Allowlist via `QA_TEAM_SAVE_ALLOWLIST` user_id (o `*`).
- Scrive SOLO su `player_server_profiles.team_formation`, NO `db.users`.

**Procedura device QA:**
```bash
# Dev imposta env e restart backend per abilitare team save:
export QA_TEAM_SAVE_ENABLED=true
export QA_TEAM_SAVE_ALLOWLIST=651253e2-da8d-466b-98f3-82f008d158ed
sudo supervisorctl restart backend
```

Validator: `validate_pre_qa_pack_126_team_save_runtime_gate.py` → PASS (gate fail-closed verificato; save completo NEEDS_DEVICE_CONFIRMATION dopo env enable).

---

## 6. Global combat background fix across all modes

**Root cause:** Preview team con eroi di fazioni miste (greek/norse/celtic/arcane/angelic + creature/norse/tides/...). `extractFaction(hero)` leggeva solo `hero.faction|hero_faction|factionKey|faction_id` — campi NON impostati dal preview snapshot. Risultato: `source: null` → background trasparente.

**Fix in `frontend/components/ui/battleBackgrounds.ts`:**
1. `extractFaction` ora ha fallback su `hero_id` prefix (es. `greek_hoplite` → `greek`).
2. Aggiunto `MODE_BG_FALLBACK`:
   - `story` → greek
   - `tower` → norse
   - `training` → celtic
   - `arena` → greek
   - `boss` / `raid` → egyptian
3. `BattleBgContext` accetta `mode?: string`.
4. **Mai più `source: null`** se il combat parte in preview: il mode fallback è premium-safe (default greek) PRIMA del gradient neutro.

**Fix in `combat.tsx::startBattle()` PREVIEW:** passa `mode: previewCtxLocal.mode || params.mode || 'story'` a `pickBattleBackground`.

Acceptance: Training/Tower/Arena/Boss/Raid preview → bg visibile garantito.

Validator: `validate_pre_qa_pack_126_global_combat_background.py` → PASS.

---

## 7. Old battle layout restoration evidence

**Root cause:** `slotToCombatUnit` settava `grid_x = idx % 3` (0,1,2,0,1,2) e `grid_y = floor(idx/3)` (0,0,0,1,1,1). MA il renderer `buildFormationGrid` in `combat.tsx` usa `X_MAP_A: {1:0, 4:1, 7:2}` e `Y_MAP: {1:0, 4:1, 7:2}` — il backend usa coordinate `1/4/7`, NON `0/1/2`.

Esito: `xMap[0]` undefined → fallback `col = floor(idx/3), row = idx%3` → 6 eroi in 2 colonne (col 0,1 × row 0-2) invece di 3 (front/mid/back). Layout compresso, 5° hero forse fuori viewport mobile.

**Fix in `previewBattleTeam.ts::slotToCombatUnit`:**
```ts
const POS_BACKEND = [
  { grid_x: 1, grid_y: 1 }, // 0 tank   - front, top
  { grid_x: 1, grid_y: 4 }, // 1 dps M  - front, mid
  { grid_x: 4, grid_y: 1 }, // 2 dps R  - mid, top
  { grid_x: 4, grid_y: 4 }, // 3 mage   - mid, mid
  { grid_x: 7, grid_y: 1 }, // 4 supp   - back, top
  { grid_x: 7, grid_y: 4 }, // 5 heal   - back, mid
];
```

Ora i 6 eroi occupano 3 colonne × 2 righe nel layout 6v6 approvato (front/mid/back lines).

Inoltre: `faction` derivata dal hero_id prefix → BG resolver funziona naturalmente.

Validator: `validate_pre_qa_pack_126_restore_old_battle_layout.py` → PASS.

---

## 8. Why only 5 heroes were visible

Layout fallback metteva 6 heroes in 2 colonne (col 0,1) ciascuna con 3 row (0,1,2). Su viewport portrait mobile + safe-area + HUD overlay, il 6° hero (col=1, row=2) cadeva oltre il bordo inferiore o veniva clippato. La percezione "5 di 6" era quindi un **clipping verticale del 6° slot** dovuto al fallback errato dell'indice.

**Fix applicato (vedi §7):** mapping POS_BACKEND `{1/4/7}` × `{1/4}` mette i 6 heroes su 3 colonne (front/mid/back) × 2 righe (top/mid), tutti visibili nel viewport.

---

## 9. Preview result no fake EXP/reward fix

**Root cause:** `buildPostBattleSummary.ts` linea 92 (originale):
```ts
const perHero = Math.max(1, Math.floor(totalHeroExp / usable.length));
```
Anche con `totalHeroExp = 0`, `Math.max(1, 0)` → 1 → ogni hero mostrava "+1 EXP".

**Fix:**
1. `buildRewards`: short-circuit a `{auto_claim: [], manual_claim: [], ...}` se `result.is_preview_local | is_preview | preview`.
2. `buildHeroExp`: short-circuit a `[]` su preview. Rimosso `Math.max(1, ...)` clamp.
3. `combat.tsx` result phase: aggiunto banner "PREVIEW COMPLETATA — Nessuna EXP · Nessun reward · Nessun progresso salvato" con tag `no_hero_exp · no_account_exp · no_gold · no_drop · no_affinity · no_ranking`.

Validator: `validate_pre_qa_pack_126_preview_result_no_fake_exp.py` → PASS.

---

## 10. Before/after no-mutation state report

Script: `backend/scripts/qa_state_capture.py` → cattura snapshot completo (user, PSPs, user_heroes count/exp/level/power, inventory, mail).

Eseguito: **before** (pre-seed) vs **after_seed** (post-seed). Validator verifica:
- `total_exp` invariato (durante seed).
- `gold` invariato.
- `diamonds` invariati.
- `user_heroes_count` aumentato solo per i seed expected.

Esito: ✅ PASS (seed phase no economy mutation).

**Per il flusso preview combat:** lo snapshot "after_preview" deve essere catturato dopo il device QA. Validator marca come `NEEDS_DEVICE_CONFIRMATION` finché non disponibile.

---

## 11. Validator results

| Validator | Status |
|-----------|--------|
| `validate_pre_qa_pack_126_seed_device_db_alignment.py` | ✅ PASS (10/10 canonical su s1) |
| `validate_pre_qa_pack_126_team_save_runtime_gate.py` | ✅ PASS (gate verified, full save needs device) |
| `validate_pre_qa_pack_126_global_combat_background.py` | ✅ PASS |
| `validate_pre_qa_pack_126_restore_old_battle_layout.py` | ✅ PASS |
| `validate_pre_qa_pack_126_preview_result_no_fake_exp.py` | ✅ PASS |
| `validate_pre_qa_pack_126_no_mutation_before_after.py` | ✅ PASS (seed phase) · NEEDS_DEVICE_CONFIRMATION (post-preview) |
| `validate_pre_qa_pack_126_report_completeness.py` | (questo report) |

**Regression Pack 123 (5) + 124 (7) + 125 (6) rieseguiti = 18/18 PASS. Zero regressioni.**

---

## 12. No-live / no-reward / no-gacha / no-shop / no-VIP / no-BP / no-IAP evidence

- ❌ NO live reward, NO real EXP/progress mutation
- ❌ NO ranking/MMR, NO authoritative battle result commit
- ❌ NO `/api/gacha/*`, NO `/api/shop/*`, NO `/api/vip/*`, NO `/api/battlepass/*`, NO `/api/iap/*`, NO `/api/mail/claim`
- ❌ NO premium currency grant/spend, NO guild/PvP/raid live reward
- ❌ NO `db.users` write nel save team (solo PSP), NO account-wide
- ❌ NO modifiche a `battle_engine.py`, `battle_core.py`, `server.py` (logic), Character Bible, `heroes_master.json`, skill kits, assets, `.env`, supervisor
- ✅ DB write QA autorizzato (`USER_RECONFIRMS_QA_TEAM_DB_WRITE_FOR_TEST_ACCOUNTS_ONLY=true`): SOLO `user_heroes` (tag `_qa_seed`) e `player_server_profiles.team_formation` (tag `_pack_125_qa_team_save`). 

Snapshot before/after seed prova invarianza economy: gold/diamonds/exp identici.

---

## 13. Rollback instructions

```bash
# QA seed rollback (rimuove i 8 nuovi su s1):
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_clear.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed

# Team save rollback (DB diretto):
# mongosh: db.player_server_profiles.update_one(
#   {"user_id":"651253e2-da8d-466b-98f3-82f008d158ed","server_id":"s1"},
#   {"$unset":{"team_formation":"","_pack_125_qa_team_save_ts":""}})

# Team save endpoint disable (revert env):
unset QA_TEAM_SAVE_ENABLED QA_TEAM_SAVE_ALLOWLIST && sudo supervisorctl restart backend
```

---

## 14. Device QA V6 checklist

1. Home/Borea regression check → PASS expected (Pack 125 ok).
2. test@test.com hero list mostra 10 QA heroes (canonical 3★ launch_base).
3. Team editor permette selezione di 6 heroes (Tank/DPS×2/Mage/Support/Healer).
4. Team save persiste dopo screen reload (richiede env QA_TEAM_SAVE_* attivi).
5. Training preview: bg visibile, layout vecchio approvato, 6 heroes visibili, action loop, no EXP/reward.
6. Tower preview: bg visibile, layout vecchio, 6 heroes visibili, action loop, no EXP/reward.
7. Arena preview: bg visibile, layout vecchio, 6 heroes visibili, action loop, no ranking/reward.
8. Raid preview: bg visibile, layout vecchio, 6 heroes visibili, action loop, no drop/reward.
9. Result screen mostra banner "PREVIEW COMPLETATA — Nessuna EXP · Nessun reward".
10. Before/after account state unchanged (cattura via `qa_state_capture.py --label after_preview`).

---

## 15. Remaining blockers and next step

1. **Team save device confirmation** — richiede env vars settate in backend runtime e device QA. Documentato.
2. **After-preview snapshot** — `qa_state_capture.py --label after_preview` da catturare DOPO il device QA per chiudere il no-mutation report.
3. **Home hero Borea trace device** — Pack 124 trace pending screenshot.
4. **TypeScript pre-existing errors** (rage, SpriteSurface, phase comparison) — non in scope Pack 126.

**Next step:**
1. Device QA utente con manifest V6.
2. Cattura snapshot post-preview.
3. Se device QA passa: Pack 127 (eventuale `CONTROLLED_LIVE_UNLOCK` staging).

---

## Hash / Provenance

- Pack: `PACK_126_DEVICE_QA_ENV_ALIGNMENT_GLOBAL_BACKGROUND_OLD_LAYOUT_PREVIEW_RESULT_CLEANUP`
- Goal: `PACK_126_DEVICE_QA_ENV_ALIGNMENT_GLOBAL_BACKGROUND_OLD_LAYOUT_PREVIEW_RESULT_COMPLETE`
- Lingua: **Italiano**.

**Verdict:** `PACK_126_DEVICE_QA_ENV_ALIGNMENT_GLOBAL_BACKGROUND_OLD_LAYOUT_PREVIEW_RESULT_COMPLETE`

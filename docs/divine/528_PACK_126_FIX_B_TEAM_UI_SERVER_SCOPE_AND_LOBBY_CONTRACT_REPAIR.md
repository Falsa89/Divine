# Pack 126-FIX-B — Team UI Server Scope and Lobby Contract Repair

**Status:** ✅ COMPLETATO
**Verdict:** `PACK_126_FIX_B_TEAM_UI_SERVER_SCOPE_AND_LOBBY_CONTRACT_REPAIR_COMPLETE`
**Scope:** hotfix chirurgico — NO nuovo sistema, NO live/prod, NO reward/gacha/shop/VIP/BP/IAP.

---

## 1. Audit device (root cause)

Verifica runtime con token `test@test.com`:

| Endpoint | Risultato |
|----------|-----------|
| `GET /api/user/profile` | HTTP 200. `selected_server_id=null`, `current_server_id=null`, ma `user.server="eu_1"`. **Profilo non espone selected_server_id**, device legge da AsyncStorage `v101_selected_server_id`. |
| `GET /api/user/heroes` (no filter) | 418 totali account-wide |
| `GET /api/user/heroes?server_id=s1` | **361 · 10/10 canonical seedati** (Pack 126 prima) |
| `GET /api/user/heroes?server_id=qa-eu-01` | **3 · 0/10 canonical** ← **questo è quello che il device vede** |
| `GET /api/team/get-formation?server_id=s1` | 2 slot Pack 125+ `{hero_id, col, row}` |

**Root cause confermata:** device usa `qa-eu-01` (3 eroi), seed Pack 126 era su `s1`. Mismatch.

---

## 2. Fix server alignment (DB)

Eseguito seed su `qa-eu-01`:
```bash
QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_canonical_heroes.py \
    --allow-account 651253e2-da8d-466b-98f3-82f008d158ed --server-id qa-eu-01
```
**Risultato:** granted **10/10**, skipped 0. Gold/diamonds invariati (snapshot before/after).

Snapshot:
- `pack_126_state_before_qaeu01_*.json`: user_heroes=3 (server qa-eu-01), qa_seed=0
- `pack_126_state_after_seed_qaeu01_*.json`: user_heroes=13 (+10), exp/gold invariati, qa_seed=10

---

## 3. FIX A — Team editor debug/contract hardening

File: `frontend/app/(tabs)/battle.tsx`
- Aggiunta trace QA (`__DEV__`): selected_server_id + heroes_count + saved_formation_count + team_keys + constellations.
- Sostituito `catch (e) {}` vuoto con warn dev-only e `setHeroes([])` di sicurezza.
- Roster da `/api/user/heroes?server_id=<selected_server_id>` confermato (Pack 92).

---

## 4. FIX B — Hero list refresh on server change

File: `frontend/app/hero-collection.tsx`
- Aggiunte `selected_server_id` e `refreshToken` al `useServerScope()` destructuring.
- `useEffect` deps array ora include `[token, userHeroesVersion, selected_server_id, refreshToken]` → refetch automatico al cambio server (era bug: stale list).

---

## 5. FIX C — Pre-battle-lobby contract repair (adapter)

File: `frontend/app/pre-battle-lobby.tsx`
- `heroMap` ora indicizzato per `id`, `hero_id` E `canonical_id` (Pack 87 + Pack 125+ + alias).
- Lettura team: `d.team_formation || (d as any).formation` (entrambi formati).
- Filtro slot: chiave robusta `e.user_hero_id || e.hero_id || e.canonical_id` (no più solo `user_hero_id`).
- Lookup nel roster con triplo predicato `hh?.id || hh?.hero_id || hh?.canonical_id`.
- Slot mapping ora include `name: h.hero_name || h.name || '—'` e `hero_image` reali → niente placeholder per player team.

---

## 6. FIX D — Backend URL consistency

File: `frontend/app/pre-battle-lobby.tsx`
- Sostituito `process.env.EXPO_BACKEND_URL` con `getCanonicalBackendUrl()` da `src/utils/backendUrl.ts`.
- Stesso resolver usato dal resto dell'app (`apiCall`, hooks). Garantisce consistenza web/mobile.

---

## 7. FIX E — Placeholder policy

- Player team mapping ora deriva sempre `name` e `hero_image` dal roster reale (`heroes`).
- Se mancano: nome `'—'` esplicito invece di placeholder fake.
- Honest blocker `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` già presente (Pack 88).
- Preview fallback già etichettato chiaramente: banner "PACK 123 — PREVIEW TEAM FALLBACK ATTIVO" (Pack 123).
- Enemy placeholders (`alpha_trainee_hero_`, `tower_minion_`, ecc.) restano **solo lato avversari** in `CANONICAL_ENCOUNTERS.*.enemies`, validator-verificato che siano scoped a `enemies:`.

---

## 8. Validator Results

| Validator | Status |
|-----------|--------|
| `validate_pack_126_fix_b_selected_server_id_propagation.py` | ✅ PASS |
| `validate_pack_126_fix_b_hero_collection_refetch_deps.py` | ✅ PASS |
| `validate_pack_126_fix_b_lobby_team_formation_contract.py` | ✅ PASS |
| `validate_pack_126_fix_b_lobby_no_fake_player_team.py` | ✅ PASS |
| `validate_pack_126_fix_b_no_live_unlocks.py` | ✅ PASS |

**Regression totale:** Pack 123 (5) + 124 (7) + 125 (6) + 126 (7) + FIX-A (3) + FIX-B (5) = **33/33 PASS**.
**TypeScript check:** zero errori su `battle.tsx`, `hero-collection.tsx`, `pre-battle-lobby.tsx`.

---

## 9. Invarianti rispettati

- ❌ NO live reward, EXP, progress mutation
- ❌ NO gacha/shop/VIP/BP/IAP/mail-claim opening
- ❌ NO premium currency grant/spend
- ❌ NO modifiche a `battle_engine.py`, `battle_core.py`, `server.py`, Character Bible, `heroes_master.json`, skill kits, assets, `.env`, supervisor (codice)
- ❌ NO nuovo backend endpoint, NO route change
- ✅ FIX-B è puramente frontend adapter + 1 seed runtime QA su `qa-eu-01` (autorizzato `USER_RECONFIRMS_QA_TEAM_DB_WRITE_FOR_TEST_ACCOUNTS_ONLY=true`, rollback disponibile).

---

## 10. File modificati

- `frontend/app/(tabs)/battle.tsx` — trace QA + no-empty-catch (~15 righe additive)
- `frontend/app/hero-collection.tsx` — deps array + refreshToken (3 righe)
- `frontend/app/pre-battle-lobby.tsx` — adapter contract + canonical URL resolver (~20 righe)

## 11. File creati

- 5 validators Python (`validate_pack_126_fix_b_*.py`)
- 5 JSON reports + 2 state snapshot reports
- Questo report MD

---

## Device QA confirmation procedure

1. Login `test@test.com` su device.
2. Verificare server selezionato (AsyncStorage `v101_selected_server_id`).
3. Aprire `/hero-collection` → deve mostrare 10+ eroi (per `qa-eu-01`: 13; per `s1`: 361).
4. Aprire `/battle` → griglia mostra team salvato (se presente sul server).
5. "Modifica Team" → lista eroi disponibili visibile, drag funziona.
6. Salva → reload → team persistito.
7. Preview combat → nomi/immagini reali (no placeholder per player).

**Verdict:** `PACK_126_FIX_B_TEAM_UI_SERVER_SCOPE_AND_LOBBY_CONTRACT_REPAIR_COMPLETE`

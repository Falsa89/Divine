# Pack 126-FIX-A — Team Formation Contract Repair

**Status:** ✅ COMPLETATO
**Data:** 2026-06-16
**Verdict:** `PACK_126_FIX_A_TEAM_FORMATION_CONTRACT_REPAIR_COMPLETE`
**Scope:** hotfix mirato frontend adapter — NESSUN nuovo sistema, NESSUN backend change, NESSUN reward/gacha/shop/VIP/BP/IAP touch.

---

## Bug di contratto frontend/backend (Device QA Pack 126)

| Layer | Contract |
|-------|----------|
| Backend `GET /api/team/get-formation?server_id=s1` | Restituisce **`team_formation`** (Pack 125+) con slot `{hero_id, col, row}`. La risposta contiene anche key legacy `formation` per backcompat. |
| Backend `POST /api/team/save-formation` | Persiste `team_formation` con slot `{hero_id, col, row}` su `player_server_profiles`. |
| Frontend `battle.tsx` (PRE-FIX) | Leggeva solo `team.formation`. Lookup eroe solo via `f.user_hero_id` e `uh[].id === f.user_hero_id`. Posizione solo via `x/y` (legacy) o `slot_index`. |
| **Risultato device** | Backend persisteva il team correttamente (verificato runtime: 2 slot salvati), ma la UI ricaricata mostrava griglia vuota perché: <br>1. `team.formation` undefined → `if (team?.formation?.length)` falso → skip parse.<br>2. Anche se forzato, `f.user_hero_id` mancante (formato Pack 125+ usa `hero_id`).<br>3. Anche se forzato, `col/row` non riconosciuti. |

---

## Fix applicato (FIX-A — solo frontend adapter)

**File:** `frontend/app/(tabs)/battle.tsx` (block `loadTeamData()`)

### A. Normalizzazione risposta team

```ts
const savedFormation: any[] = (team?.team_formation || team?.formation || []) as any[];
if (savedFormation.length) { ... }
```

Accetta entrambi i formati: Pack 125+ (`team_formation`) e legacy (`formation`).

### B. Lookup eroe robusto

```ts
const savedHeroKey = f?.user_hero_id || f?.hero_id || f?.canonical_id;
const h = (uh || []).find((x: any) =>
  x?.id === savedHeroKey ||
  x?.hero_id === savedHeroKey ||
  x?.canonical_id === savedHeroKey
);
```

Triplo fallback: `user_hero_id` (Pack 87 ownership ID) → `hero_id` (Pack 125+ canonical) → `canonical_id` (alias). Lookup nel roster con triplo predicato.

### C. Mapping posizioni con priorità chiara

```ts
if (typeof f.col === 'number' && typeof f.row === 'number') {
  ci = clamp(f.col, 0, 2); ri = clamp(f.row, 0, 2);  // Pack 125+ slot format
} else if (typeof f.x === 'number' && typeof f.y === 'number') {
  // Legacy 1-based grid (Pack pre-87)
} else if (typeof f.slot_index === 'number') {
  // Pack 87 starter format
} else {
  // fallback sequenziale
}
```

---

## D. Verifica API runtime (account test)

Eseguito su backend RUNNING dopo abilitazione QA env vars:

| API | Risultato |
|-----|-----------|
| `GET /api/user/heroes?server_id=s1` | **HTTP 200** · 361 heroes totali · **10/10 canonical seedati** presenti (greek_hoplite, norse_berserker, celtic_archer, arcane_lightning_enchantress, greek_sanctuary_muse, angelic_priestess, creature_coral_guardian, norse_thunder_spear, celtic_moor_druidess, egyptian_nile_healer). Shape hero include sia `id` che `hero_id`. |
| `GET /api/team/get-formation?server_id=s1` | **HTTP 200** · key principale `team_formation` (NON `formation`) · 2 slot `{hero_id: 'greek_hoplite', col: 0, row: 0}` + `{hero_id: 'norse_berserker', col: 1, row: 0}` salvati dal test runtime Pack 126. |
| `POST /api/team/save-formation` (allowlisted) | **HTTP 200** · invariants_respected all true. |
| `POST /api/team/save-formation` (non-allowlisted) | **HTTP 403** `QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED`. |

**Conclusione D:** gli eroi sono presenti nell'API (10/10 canonical) E la formazione è in `team_formation` → la fix è **puramente frontend adapter** (caso F del prompt).

**Blocker E:** NON applicabile (eroi presenti in API). Conferma: `PACK_126_FIX_A_BLOCKED_USER_HEROES_NOT_RETURNED_FOR_DEVICE_SERVER` non scattato.

---

## Validator Results

| Validator | Status |
|-----------|--------|
| `validate_pack_126_fix_a_battle_reads_team_formation.py` | ✅ PASS |
| `validate_pack_126_fix_a_load_grid_hero_id_and_colrow.py` | ✅ PASS |
| `validate_pack_126_fix_a_no_live_unlocks.py` | ✅ PASS |

Regression Pack 123 (5) + 124 (7) + 125 (6) + 126 (7) + FIX-A (3) = **28/28 PASS**. Zero regressioni.

TypeScript check su `battle.tsx`: **0 errori**.

---

## Invarianti rispettati

- ❌ NO reward live, NO real EXP/progress mutation, NO ranking/MMR
- ❌ NO authoritative battle commit, NO `/api/gacha/*`, NO `/api/shop/*`, NO `/api/vip/*`, NO `/api/battlepass/*`, NO `/api/iap/*`, NO `/api/mail/claim`
- ❌ NO premium currency grant/spend
- ❌ NO modifiche a `battle_engine.py`, `battle_core.py`, `server.py`, backend routes, Character Bible, `heroes_master.json`, skill kits, assets, `.env`, supervisor (codice)
- ✅ FIX-A è puramente frontend adapter su `battle.tsx::loadTeamData()`.
- ✅ Le env vars runtime QA (`QA_TEAM_SAVE_ENABLED`, `QA_TEAM_SAVE_ALLOWLIST`) restano **TEMPORARY DEVICE QA SOLO** (vedi precedente runtime enablement). Rollback in `/tmp/backend.conf.bak.pack126`.

---

## File modificati

- `frontend/app/(tabs)/battle.tsx` — solo il blocco `loadTeamData()` (≈ 60 righe modificate, additive).

## File creati

- `backend/scripts/validate_pack_126_fix_a_battle_reads_team_formation.py`
- `backend/scripts/validate_pack_126_fix_a_load_grid_hero_id_and_colrow.py`
- `backend/scripts/validate_pack_126_fix_a_no_live_unlocks.py`
- `backend/scripts/reports/pack_126_fix_a_*.json` (3 report JSON)
- `docs/divine/527_PACK_126_FIX_A_TEAM_FORMATION_CONTRACT_REPAIR.md` (questo file)

---

## Device QA confirmation procedure

1. Login `test@test.com` su device.
2. Aprire `/battle` (team editor).
3. Verificare che la griglia mostri i 2 eroi già salvati (greek_hoplite + norse_berserker).
4. Drag altri eroi per completare formazione 6v6.
5. Tap "Salva formazione" → conferma `team_size=6`.
6. Reload screen → verificare griglia mostra il team salvato (no più "vuota").

---

**Verdict:** `PACK_126_FIX_A_TEAM_FORMATION_CONTRACT_REPAIR_COMPLETE`

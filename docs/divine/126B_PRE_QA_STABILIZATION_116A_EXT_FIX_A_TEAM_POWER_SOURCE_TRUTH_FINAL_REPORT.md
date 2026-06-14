# 126B_PRE_QA_STABILIZATION_116A_EXT_FIX_A_TEAM_POWER_SOURCE_TRUTH_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_116A_EXT_FIX_A_TEAM_POWER_SOURCE_TRUTH_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-FIX-A): `db62b9c06f0548effcc927080b1419616960b53c`
- Pack 116A-EXT FIX-A commit: *aggiornato al momento del commit esplicito file-by-file.*
- Report/self-ref:            *aggiornato dopo il commit del self-ref.*

> **Commit policy** preservata: MAI `git add -A` / `git add .`. Tutti i file con `git add -- <path>` esplicito.

## Root cause analysis — perche' Home mostrava BP 936

**Diagnosi truthful**: il valore `936 = 3 × 312` era **matematicamente corretto**. Il backend stava leggendo correttamente il `team_formation` del PSP, che contiene effettivamente **3 starter heroes** (auto-inizializzati al primo `/api/psp/starter/claim` — vedi `server.py:482-489`). La formula 116A `battle_power_v1_preqa_derived` ha calcolato `312` per ciascun starter hero (base stats + level=1 + rarity=1 + stars=1), per un totale di `3 × 312 = 936`.

→ **Caso A del pack** (PSP ha davvero 3 starter heroes nel team).

**Sotto-causa del mismatch UX** (perche' l'utente diceva "no eroi nel team"): la UI Battle tab (`(tabs)/battle.tsx`) mappava la formation usando `(f.x, f.y)` ma gli starter team Pack 87 scrivono solo `slot_index` (0, 1, 2) **senza** `x`/`y`. Il vecchio codice:
```ts
const ci = (f.x || 0) <= 2 ? 0 : (f.x || 0) <= 5 ? 1 : 2;
const ri = (f.y || 0) <= 2 ? 0 : (f.y || 0) <= 5 ? 1 : 2;
if (!ng[ci][ri]) ng[ci][ri] = h;
```
collassava tutti e 3 gli starter su `grid[0][0]`, e l'`if (!ng[ci][ri])` lasciava SOLO 1 dei 3 visibile. L'utente vedeva la grid sostanzialmente vuota e concludeva "no team", mentre Home leggeva il valore corretto.

## Scope / files changed

**Created**:
- `backend/scripts/validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py` — validator FIX-A (12 check).
- `docs/divine/126B_PRE_QA_STABILIZATION_116A_EXT_FIX_A_TEAM_POWER_SOURCE_TRUTH_FINAL_REPORT.md` — questo file.

**Modified**:
- `backend/routes/battle_power.py` — `/api/battle-power/summary` ora espone metadata truth (`team_source`, `team_slot_count`, `valid_team_slot_count`, `invalid_team_slot_count`, `team_missing_reason`) e applica truth on validity: se 0 slot valido → `team_missing=True` + `active_team_power=0`.
- `frontend/app/(tabs)/battle.tsx` — mapping `team.formation` ora gestisce `slot_index` come fallback a `x/y`, **risolve il bug di visualizzazione delle starter team** (3 starter heroes ora visibili come 3 celle separate nella grid). Cell-collision: scorrimento sequenziale fino a prima cella libera (truth: mai sovrascrivere).
- `backend/scripts/run_pre_qa_safety_validator_suite.py` — registrato 116A-EXT FIX-A come 18ª voce.

**Untouched** (vincoli rispettati):
- Formula numerica 116A: **invariata** (`battle_power_v1_preqa_derived` produce sempre gli stessi power).
- `battle_engine.py`, combat/tower runtime, gacha, reward, Character Bible: **untouched**.
- `data/design/**`: **0 path toccato**.
- `home.tsx`, `hero-detail.tsx`, `heroes.tsx`: invariati rispetto a 116A-EXT.
- Pack 115F / 116A FIX-A repo hygiene: **0 .pyc / 0 __pycache__ tracciati**.

## Backend: `/api/battle-power/summary` truth metadata

### Nuovi campi esposti (envelope)
| Campo | Tipo | Significato |
|---|---|---|
| `team_source` | string | `"player_server_profile"` se PSP.team_formation ha slot · `"none"` altrimenti |
| `team_slot_count` | int | Numero totale di slot in `PSP.team_formation` |
| `valid_team_slot_count` | int | Slot che risolvono verso (user_hero server-scoped posseduto E hero catalog NON deactivated) |
| `invalid_team_slot_count` | int | Slot fantasma/stale (non risolti, o eroe deactivated) |
| `team_missing_reason` | string \| null | `"PLAYER_SERVER_PROFILE_REQUIRED"` · `"TEAM_FORMATION_EMPTY"` · `"TEAM_FORMATION_PRESENT_BUT_NO_VALID_SLOTS"` · `null` |
| `team_slots[].valid` | bool | Per ciascuno slot, validity status |
| `team_slots[].resolved_user_hero` | bool | Per slot, se user_hero e' stato risolto |
| `team_slots[].resolved_hero_catalog` | bool | Per slot, se hero catalog e' stato risolto |

### Truth-on-validity logic
```python
# Conta slot validi
if uh_doc and hero_doc:
    deactivated = hero_doc.get("deactivated_at")
    is_valid = not bool(deactivated)
    if is_valid:
        p = compute_hero_battle_power_v1(hero_doc, uh_doc)
    else:
        p = 0
# Accumula condizionalmente
if is_valid:
    valid_team_slot_count += 1
    active_team_power += p
else:
    invalid_team_slot_count += 1

# Truth: 0 slot validi → team_missing=True, no falso power
if valid_team_slot_count == 0:
    team_missing = True
    active_team_power = 0  # MAI somma owned_hero_count, MAI fallback
```

### Curl evidence (live, backend up)

**Case A — PSP con 3 starter heroes (utente con `/api/psp/starter/claim` eseguito):**
```
GET /api/battle-power/summary?server_id=s1
HTTP 200
  status                  = ok
  team_source             = player_server_profile
  team_slot_count         = 3
  valid_team_slot_count   = 3
  invalid_team_slot_count = 0
  active_team_power       = 936
  team_missing            = False
  team_missing_reason     = null
  owned_hero_count        = 3
  max_owned_hero_power    = 312
  team_slots:
    slot 1: power=312, valid=True,  resolved_user_hero=True,  resolved_hero_catalog=True
    slot 2: power=312, valid=True,  resolved_user_hero=True,  resolved_hero_catalog=True
    slot 3: power=312, valid=True,  resolved_user_hero=True,  resolved_hero_catalog=True
```

**Case B — PSP senza team (PSP ensure ma NO starter claim):** *(verificato dal validator check [12])*
```
GET /api/battle-power/summary?server_id=s1
HTTP 200
  status                  = ok
  team_source             = none
  team_slot_count         = 0
  valid_team_slot_count   = 0
  invalid_team_slot_count = 0
  active_team_power       = 0
  team_missing            = True
  team_missing_reason     = TEAM_FORMATION_EMPTY
```

**Case (no-PSP)** — fresh user senza PSP:
```
GET /api/battle-power/summary?server_id=s1
HTTP 200
  status                  = blocked_no_psp_for_server
  team_source             = none
  team_slot_count         = 0
  active_team_power       = 0
  team_missing            = True
  team_missing_reason     = PLAYER_SERVER_PROFILE_REQUIRED
  blocker                 = PLAYER_SERVER_PROFILE_REQUIRED
```

### Confronto endpoint UI Battle (`/api/team/get-formation`)
```
GET /api/team/get-formation?server_id=s1
HTTP 200
  team_source = player_server_profile
  source = saved_formation_server_scoped
  team_formation: 3 slots (slot_index=0,1,2, user_hero_id risolto, x/y assenti)
```
→ Stessa fonte (PSP). Stesso conteggio (3). UI Battle ora visualizza i 3 starter (vedi fix `slot_index` sotto).

## Frontend: `battle.tsx` slot_index mapping fix

### Before (bug)
```ts
team.formation.forEach((f: any) => {
  if (!f.user_hero_id) return;
  const h = uh.find((x: any) => x.id === f.user_hero_id);
  if (!h) return;
  // Map x to column: x<=2 → 0 (Support), x<=5 → 1 (DPS), x<=8 → 2 (Tank)
  const ci = (f.x || 0) <= 2 ? 0 : (f.x || 0) <= 5 ? 1 : 2;
  const ri = (f.y || 0) <= 2 ? 0 : (f.y || 0) <= 5 ? 1 : 2;
  if (!ng[ci][ri]) ng[ci][ri] = h;  // 3 starter heroes ALL hit grid[0][0]
});                                  // Only 1 visible
```

### After (truth)
```ts
team.formation.forEach((f: any, i: number) => {
  if (!f.user_hero_id) return;
  const h = uh.find((x: any) => x.id === f.user_hero_id);
  if (!h) return;
  let ci: number, ri: number;
  if (typeof f.x === 'number' && typeof f.y === 'number' && (f.x > 0 || f.y > 0)) {
    // Legacy 1-based grid (Pack pre-87).
    ci = f.x <= 2 ? 0 : f.x <= 5 ? 1 : 2;
    ri = f.y <= 2 ? 0 : f.y <= 5 ? 1 : 2;
  } else if (typeof f.slot_index === 'number') {
    // Pack 87 starter team: slot_index 0..8 → (col, row)
    const si = f.slot_index;
    ci = Math.max(0, Math.min(2, Math.floor(si / 3)));
    ri = Math.max(0, Math.min(2, si % 3));
  } else {
    ci = Math.max(0, Math.min(2, Math.floor(cursor / 3)));
    ri = Math.max(0, Math.min(2, cursor % 3));
    cursor++;
  }
  // Truth: mai sovrascrivere. Cell collision → scroll sequenziale.
  if (ng[ci][ri]) {
    let placed = false;
    for (let cc = 0; cc < 3 && !placed; cc++) {
      for (let rr = 0; rr < 3 && !placed; rr++) {
        if (!ng[cc][rr]) { ng[cc][rr] = h; placed = true; }
      }
    }
  } else {
    ng[ci][ri] = h;
  }
});
```

→ Ora i 3 starter heroes (slot_index=0,1,2) vengono visualizzati come 3 celle separate nella grid Battle: `grid[0][0]`, `grid[0][1]`, `grid[0][2]`. UI Battle e BP Home sono ora **coerenti** (entrambi mostrano 3 eroi nel team attivo).

## Validator results

### `python3 backend/scripts/validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py`
**PASS — 12/12** (11 statici + 1 runtime):
1. `[1] route exposes truth metadata (team_source/slot_count/valid/invalid/missing_reason) OK`
2. `[2] slot validity counting (valid/invalid + conditional active_team_power) OK`
3. `[3] no fake team (valid=0 → team_missing=True, power=0) OK`
4. `[4] owned heroes NOT summed when team missing OK`
5. `[5] no account-wide team fallback in battle_power route OK`
6. `[6] no DB writes in battle_power route OK`
7. `[7] formula version invariata (battle_power_v1_preqa_derived) OK`
8. `[8] battle.tsx: no /api/team account-wide + supporta slot_index OK`
9. `[9] home.tsx still uses useBattlePowerSummary (no regression) OK`
10. `[10] no out-of-scope imports OK`
11. `[11] pre-QA safety suite registers 116A-EXT FIX-A OK`
12. `[12] runtime summary truth metadata OK (PSP-only no team: team_missing=True, reason=TEAM_FORMATION_EMPTY)` *(backend up)*

### Catena completa di validazione richiesta dal pack
| Script | Risultato |
|---|---|
| `validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py` | **12/12 PASS** |
| `validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py` | 11/11 PASS |
| `validate_pre_qa_stabilization_116a_battle_power_foundation.py` | 11/11 PASS |
| `validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py` | 7/7 PASS |
| `sweep_repo_hygiene.py` | `clean=true` |
| `run_pre_qa_safety_validator_suite.py` | **18/18 PASS, 0 FAIL, 0 SKIP** |

## Safety invariants
- DB writes: **0** in tutto il pack (battle_power.py route, util, validator: tutti read-only).
- Roster mutation: **0**.
- Team mutation: **0** (lo starter flow Pack 87 e' preesistente, NON modificato).
- Starter grant: **NON triggerato in questo pack**.
- Gacha/summon unlock: **0**.
- Reward/progress mutation: **0**.
- Combat authoritative activation: **false** (preserved).
- `battle_engine.py`: **untouched**.
- Combat/Tower runtime: **untouched**.
- Red Dot / Chat Bot: **NON implementati**.
- Character Bible: **untouched**.
- gacha rates: **untouched**.
- `data/design/**`: **0 path toccato**.
- Formula 116A numerica: **invariata** (`battle_power_v1_preqa_derived` produce gli stessi power di prima del fix; il fix riguarda metadata + UI truthful, non il valore).
- Account-wide team fallback: **vietato** (verificato statico + battle.tsx continua a usare `/api/team/get-formation?server_id=...`).
- N+1 chiamate: **preservate eliminazioni di 116A-EXT** (batch-load heroes in `/api/user/heroes`).
- Tracked `.pyc` / `__pycache__` in git: **0**.

## Truth statement
| Domanda Game Master | Risposta truthful |
|---|---|
| Home mostra BP 936 mentre utente dice "no team" — bug o coerente? | **Coerente** (Caso A): il PSP ha auto-inizializzato 3 starter heroes nel team_formation durante `psp/starter/claim`. `3 × 312 = 936`. |
| Backend stava contando slot ghost/stale? | **No**: lo dimostra il nuovo metadata `valid_team_slot_count=3, invalid=0` per il Case A. |
| Backend somma owned heroes come team power? | **No**: verifica statica check [4] + path `team_missing=True → active_team_power=0` blindato. |
| UI Battle mostrava i 3 starter heroes prima del fix? | **No**: mapping (x,y) collassava tutti su grid[0][0] e ne mostrava 1. **Fix incluso in questo pack** (slot_index fallback) — ora la UI mostra i 3 eroi come Home dichiara. |
| `/api/team/get-formation` e `/api/battle-power/summary` leggono la stessa fonte? | **Sì**: entrambi leggono `player_server_profiles.team_formation`. Stessa source-of-truth. |

## Deferred / non in 116A-EXT FIX-A
- 116B (Chat/Bot quality cleanup): non ancora iniziato.
- 116C (Red Dot foundation): non ancora iniziato.
- 117+ (resolver runtime-safe per gear/gem/rune/artifact_global/divine_weapon/team_synergy/cosmetics cappati/ascension/elevation/reincarnation/constellations/skill_upgrade): roadmap deferred (vedi source map 116A-EXT).

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 116B** prima del re-audit esplicito.

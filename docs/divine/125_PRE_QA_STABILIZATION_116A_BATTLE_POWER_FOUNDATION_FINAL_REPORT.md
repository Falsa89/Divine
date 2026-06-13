# 125_PRE_QA_STABILIZATION_116A_BATTLE_POWER_FOUNDATION_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_116A_BATTLE_POWER_FOUNDATION_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-116A): `8b711627a7f938549756f6441850bf3afe3ec503`
- Pack 116A commit:    `053b34dccbd6f71e17775b61f3ab03a6eeaf0eca`
- Report/self-ref:     `024fca9d034d8412f469fbcb743f912310ad493c`

> **Commit policy**: il commit del Pack 116A segue il vincolo esplicito utente: **MAI `git add -A` / `git add .`**. Tutti i file sono stati aggiunti con `git add -- <path>` esplicito file-by-file.

## Scope / files changed
**Created**:
- `backend/utils/battle_power.py` — Helper puro Battle Power v1 (formula + metadata).
- `backend/routes/battle_power.py` — Route `/api/battle-power/summary` + `/metadata`.
- `frontend/src/hooks/useBattlePowerSummary.ts` — Hook React Native consumer.
- `backend/scripts/validate_pre_qa_stabilization_116a_battle_power_foundation.py` — Validator 116A (11 check).
- `docs/divine/125_PRE_QA_STABILIZATION_116A_BATTLE_POWER_FOUNDATION_FINAL_REPORT.md` — questo file.

**Modified**:
- `backend/server.py` — registrazione include_router (post-team_formation_router).
- `backend/scripts/run_pre_qa_safety_validator_suite.py` — registrato 116A come 16ª voce.
- `frontend/app/(tabs)/home.tsx` — rimosso `user?.power || user?.total_power || 0`; ora usa `useBattlePowerSummary` + `powerLabel`.
- `frontend/app/(tabs)/battle.tsx` — rimossa `power` state + `team.total_power`; ora usa `useBattlePowerSummary`; preserva `/api/team/get-formation?server_id=...` server-scoped (NO `/api/team` account-wide fallback).
- `frontend/app/hero-detail.tsx` — display fallback coerente `—` invece di undefined/0 falso.
- `memory/test_credentials.md` — annotato il test user effimero usato per la curl evidence.

**Nessuna modifica sotto `data/design/**`** · **`battle_engine.py` UNTOUCHED**.

## Battle Power v1 — semantic contract

| Campo | Valore |
|---|---|
| `formula_version` | `battle_power_v1_preqa_derived` |
| `source` | `derived_read_only` |
| `runtime_attached` | `false` |
| `combat_authoritative` | `false` |
| `reward_authoritative` | `false` |
| `balance_final` | `false` |
| `server_scoped` | `true` |

### Formula (deterministica, pure function)
```
base = phys_damage(or attack)
     + magic_damage
     + phys_defense(or defense)
     + magic_defense
     + (hp // 10)
     + speed
     + (healing // 2)

power = int(base * (1 + (level - 1) * 0.05) * (1 + rarity * 0.2))

# Bonus stelle foundation-only (no balance final):
# +3% per ogni stella OLTRE la rarity nativa, capped a +15%.
star_delta = max(0, stars - rarity)
star_bonus = min(0.15, star_delta * 0.03)
power = int(power * (1 + star_bonus))
```

Riusa la stessa shape di `calculate_hero_power` gia' in `server.py:867`, ma versionata e dichiarata `read-only/derived`. Cio' evita duplicazioni numeriche divergenti senza implicare `runtime_attached/combat_authoritative`.

### Campi base inclusi
- `base_stats.physical_damage` (fallback `attack`)
- `base_stats.magic_damage`
- `base_stats.physical_defense` (fallback `defense`)
- `base_stats.magic_defense`
- `base_stats.hp` // 10
- `base_stats.speed`
- `base_stats.healing` // 2
- `rarity` (native)
- `level` (server-scoped)
- `stars` (server-scoped)

### Campi esplicitamente esclusi (`excluded_power_sources`)
`artifacts`, `divine_weapons`, `cosmetics`, `titles`, `skill_final_numbers`, `live_rewards`, `equipment`, `runes`, `gem_sockets`, `account_wide_bonuses`, `guild_bonuses`, `server_bonuses`, `affinity_bonuses`, `sanctuary_bonuses`.

### Fallback conservativi dichiarati
Se mancano campi numerici su hero/user_hero: `phys_damage=100`, `phys_defense=50`, `hp=1000`, `speed=10`, `level=1`, `rarity=1`. Nessun crash. Nessun bonus esterno inventato.

## Endpoint map

| Method | Path | Auth | Mutation | Note |
|---|---|---|---|---|
| `GET` | `/api/battle-power/metadata` | ❌ (introspection) | ❌ | Solo metadata read-only |
| `GET` | `/api/battle-power/summary?server_id=<sid>` | ✅ Bearer | ❌ | `server_id` REQUIRED, no silent s1 fallback |

### Response envelope `/summary`
```json
{
  "status": "ok | blocked_no_psp_for_server",
  "server_id": "<sid>",
  "formula_version": "battle_power_v1_preqa_derived",
  "source": "derived_read_only",
  "runtime_attached": false,
  "combat_authoritative": false,
  "reward_authoritative": false,
  "balance_final": false,
  "server_scoped": true,
  "excluded_power_sources": ["artifacts", "divine_weapons", "cosmetics", "titles", "skill_final_numbers", "live_rewards", "equipment", "runes", "gem_sockets", "account_wide_bonuses", "guild_bonuses", "server_bonuses", "affinity_bonuses", "sanctuary_bonuses"],
  "psp_present_for_server": true | false,
  "active_team_power": 12345,
  "team_missing": true | false,
  "team_slots": [{"slot": 1, "user_hero_id": "...", "hero_id": "...", "power": 1234}],
  "owned_hero_count": 12,
  "max_owned_hero_power": 2345,
  "owned_heroes_preview": [...up to 10...],
  "blocker": null | "PLAYER_SERVER_PROFILE_REQUIRED"
}
```

### Error: missing `server_id` → HTTP 400
```json
{
  "detail": {
    "code": "SERVER_ID_REQUIRED",
    "message": "Battle Power 116A e' strictly server-scoped. Fornire `server_id` esplicito; nessun silent s1 fallback.",
    "no_silent_s1_fallback": true,
    "formula_version": "battle_power_v1_preqa_derived",
    "source": "derived_read_only",
    "runtime_attached": false,
    "combat_authoritative": false,
    "reward_authoritative": false,
    "balance_final": false,
    ...
  }
}
```

## UI display changes (truthful, no false `Power 0`)

### Home `(tabs)/home.tsx`
**Before:**
```ts
const power = user?.power || user?.total_power || 0;  // sempre 0 in pre-QA
// ... <Text>{Number(power).toLocaleString()}</Text>  // "0"
```

**After:**
```ts
const bp = useBattlePowerSummary();          // server-scoped derived
const powerLabel = bp.displayTeamPowerLabel; // "1.234" | "Server richiesto" | "Profilo server mancante" | "Team non impostato" | "…" | "—"
// ... <Text>{powerLabel}</Text>
```

Stati visualizzati dall'UI (mai falso `0`):
| Stato hook | Label mostrata | Caso |
|---|---|---|
| `idle` | `—` | server scope non pronto |
| `no_server` | `Server richiesto` | nessun server selezionato |
| `loading` | `…` | fetch in corso |
| `no_psp` | `Profilo server mancante` | PSP assente per il server selezionato |
| `no_team` | `Team non impostato` | team_missing=true |
| `ok` | numero formattato (es. `12.345`) | active_team_power disponibile |
| `error` | `—` | errore di rete |

### Battle `(tabs)/battle.tsx`
- Rimossa `const [power, setPower] = useState(0)` e `setPower(team.total_power || 0)`.
- Aggiunto `useBattlePowerSummary` per il display nel header (`powerBadge`).
- Mantenuto `apiCall('/api/team/get-formation?server_id=...')` server-scoped per la lettura della formation (Pack 115C).
- **Nessun fallback `/api/team` account-wide reintrodotto** (verificato dal validator check [8] via regex).

### hero-detail `hero-detail.tsx`
- `data.power?.toLocaleString()` → `typeof data.power === 'number' && data.power > 0 ? data.power.toLocaleString() : '\u2014'`.
- Niente piu' undefined/falso 0 sul badge power dell'header.

## Validator results

### `python3 backend/scripts/validate_pre_qa_stabilization_116a_battle_power_foundation.py`
**PASS — 11/11** (10 statici + 1 runtime):
1. `[1] util battle_power module + formula version OK`
2. `[2] route module + endpoint shape (no silent s1 fallback) OK`
3. `[3] util + route are READ-ONLY (no insert/update/delete calls, no $set/$inc operators) OK`
4. `[4] metadata builder declares non-authoritative flags OK`
5. `[5] excluded sources (artifacts/divine_weapons/cosmetics/titles/skill_final_numbers/live_rewards) dichiarati OK`
6. `[6] Home no longer uses 'user?.power || user?.total_power || 0' OK`
7. `[7] Home uses useBattlePowerSummary hook + honest placeholders OK`
8. `[8] Battle tab no /api/team account-wide + uses hook + server-scoped formation OK`
9. `[9] no out-of-scope imports + no data/design writes OK`
10. `[10] pre-QA safety suite includes 116A validator OK`
11. `[11] runtime metadata endpoint OK (live, formula+flags coerenti)` *(backend up)*

### `python3 backend/scripts/run_pre_qa_safety_validator_suite.py`
**PASS — 16/16** (verdict: `PRE_QA_SAFETY_SUITE_PASS`):

| # | Entry | Stato |
|---|---|---|
| 1  | Validator 113 HomeOverflow | PASS |
| 2  | Smoke 113 HomeOverflow | PASS |
| 3  | Validator 114 Home Routes | PASS |
| 4  | Smoke 114 Home Routes | PASS |
| 5  | Rollup 114 Home Routes | PASS |
| 6  | Validator 114B Gacha/Combat/Lobby Guard | PASS |
| 7  | Validator 115A P0 Hard Gates | PASS |
| 8  | Smoke 115A P0 Hard Gates (runtime) | PASS *(backend up)* |
| 9  | Validator 115B Progression/Forge/Items | PASS |
| 10 | Smoke 115B Progression/Forge/Items (runtime) | PASS *(backend up)* |
| 11 | Validator 115C Auth/Server Scope | PASS |
| 12 | Validator 115D Screen-Entry/Deeplink Guard | PASS |
| 13 | Validator 115E Combat/Tower Legacy Hardening | PASS |
| 14 | Validator 115F Repo Hygiene & Validator Truth | PASS |
| 15 | Validator 115G Skill/Artifact Semantic Cleanup | PASS |
| 16 | **Validator 116A Battle Power Foundation** | **PASS** |

Totali: 16 · PASS: 16 · FAIL: 0 · SKIPPED: 0 · backend_up: true.

JSON path: `backend/reports/pre_qa_safety_validator_suite_latest.json`.

## Curl evidence (backend up, test user effimero `qa116a_1781391350@test.com`)

```
[A] GET /api/battle-power/metadata (no auth)
    HTTP=200
    formula_version       = battle_power_v1_preqa_derived
    source                = derived_read_only
    runtime_attached      = False
    combat_authoritative  = False
    reward_authoritative  = False
    balance_final         = False

[B] GET /api/battle-power/summary WITHOUT server_id
    HTTP=400
    detail.code                   = SERVER_ID_REQUIRED
    detail.no_silent_s1_fallback  = True

[C] GET /api/battle-power/summary?server_id=s1   (fresh user, no PSP)
    HTTP=200
    status                  = blocked_no_psp_for_server
    formula_version         = battle_power_v1_preqa_derived
    team_missing            = True
    active_team_power       = 0
    psp_present_for_server  = False
    blocker                 = PLAYER_SERVER_PROFILE_REQUIRED
```

> Nota: l'`active_team_power=0` in caso [C] e' tecnicamente coerente con `team_missing=true` + `psp_present_for_server=false`. **L'UI NON visualizza questo `0`** perche' l'hook lo riconosce come `state='no_psp'` e mostra il placeholder `Profilo server mancante`, NON `0`. Verita' preservata end-to-end.

## Frontend smoke
- Expo Metro bundler: `Web Bundled 27971ms ... 2765 modules` → bundle servito su `:3000` con HTTP 200.
- Screenshot login screen "DIVINE WAIFUS" — UI carica correttamente.
- Nessun crash da `Cannot read property` su `useBattlePowerSummary` (selettori difensivi `null`-safe sui campi del summary).

## Safety invariants
- DB writes: **0** (utility e route entrambi statici/read-only).
- Reward live: **false**.
- Gacha live: **false**.
- IAP/payment: **false**.
- Combat authoritative activation: **false** (`combat_authoritative=false` dichiarato in envelope + verificato).
- `battle_engine.py`: **untouched**.
- Combat runtime: **untouched**.
- Tower runtime: **untouched**.
- Red Dot: **non implementato** (verificato dal validator check [9]).
- Chat/Bot cleanup: **non implementato** (verificato dal validator check [9]).
- Skill/Artifact semantic: **invariato** rispetto a 115G.
- Character Bible: **untouched**.
- gacha rates: **untouched**.
- `data/design/**`: **0 path toccato** (verificato via `git diff --stat`).
- Account-wide fallback: **vietato** — endpoint solleva 400 senza `server_id`; Battle tab continua a usare `/api/team/get-formation?server_id=...` server-scoped.
- Tracked `.pyc` / `__pycache__` in git: **0** (hygiene 115F preservata).

## Deferred (post-116A roadmap)
- **116B — Chat/Bot quality + legacy chat cleanup**: cleanup chat/bot UI e routing, *separato*.
- **116C — Red Dot notification badge foundation**: badge di notifica, *separato* (NB: nessuna push notification implementata o suggerita autonomamente).
- **Equipment/Runes power integration**: deferred. Sara' valutata SOLO quando equipment/runes saranno strict-server-scoped/read-only-safe (probabilmente Pack 117+).
- **Balance final pass**: deferred. La formula 116A NON e' una formula di bilanciamento finale: `balance_final=false` esplicito.

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 116B** prima del re-audit esplicito.

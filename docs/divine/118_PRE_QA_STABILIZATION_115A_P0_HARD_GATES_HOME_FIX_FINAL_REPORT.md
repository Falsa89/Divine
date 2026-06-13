# 118 — PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX — FINAL REPORT

## Verdict

`PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX_READY_FOR_GAME_MASTER_REAUDIT`

Manual QA **remains paused until Game Master re-audit.**

---

## Commit

- Branch: `master`
- Commit SHA (Pack 115A code+validators+smoke+report): `0fda3f5a3574d45c6f3171afe2a0b45d781c30f5`
- Pre-Pack-115A baseline tip: `774a95ac23504dffb9c5fa7a609a82c2fae68592` (Pack 114C cleanup HEAD)

---

## Scope Summary

### Files changed (codice runtime)

1. `frontend/app/(tabs)/home.tsx` — 4 push diretti a `/profile` ora guarded inline con `isRouteAllowedInPreQa('/profile')` + `Alert PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`.
2. `frontend/src/utils/preQaNavGuard.ts` — aggiunto `'/research'` a `PRE_QA_BLOCKED_PLAYER_ROUTES`.
3. `backend/utils/postqa_d_mutation_gate.py` — aggiunti 9 nuovi gate default-OFF + helper `is_legacy_mutation_gate_enabled`.
4. `backend/routes/economy.py` — gateati 7 endpoint POST + 2 GET (via `is_legacy_mutation_gate_enabled` no-write).
5. `backend/routes/gvg.py` — gateati 2 endpoint POST (matchmake, attack); end-war ADMIN gate preservato.
6. `backend/routes/raids.py` — gateati 3 endpoint POST (raid/create, raid/attack, exclusive-items/craft); aggiunto import gate module.
7. `backend/routes/cosmetics.py` — gateati 3 endpoint POST (cosmetics/buy, cosmetics/equip, territory/attack); aggiunto import gate module.
8. `backend/scripts/validate_pre_qa_stabilization_114_home_routes_canonicalization.py` — riscritto con bracket-matching robusto + check 115A.
9. `backend/scripts/run_hero_skill_kit_validator_suite.py` — registry +1 entry validator 115A.

### Files created

10. `backend/scripts/validate_pre_qa_stabilization_115a_p0_hard_gates_home_fix.py` — 11 check statici.
11. `backend/scripts/smoke_pre_qa_stabilization_115a_p0_hard_gates_home_fix.py` — 17 step runtime (15 POST gate + 2 GET no-write).
12. `docs/divine/118_PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX_FINAL_REPORT.md` — questo file.

### Files intentionally untouched (forbidden)

- `backend/battle_engine.py`
- `frontend/app/combat.tsx`
- Gacha rates, shop catalogs, raid boss design data
- Auth/server-scope unification (deferred a Pack 115C)
- Skill catalog `final_numbers` cleanup (deferred a Pack 115G)
- `data/design/**` artifacts (hygiene su commit)
- Nessuna nuova schermata `profile.tsx` o `research.tsx` creata

---

## Home Fix Proof

### `/profile` direct push count before/after

| Misura | Before | After |
|---|---|---|
| Direct `router.push('/profile' as any)` (4 occorrenze fisiche) | 4 senza guard inline | 4 con guard inline `isRouteAllowedInPreQa('/profile')` |
| Direct push UNGUARDED a `/profile` | 4 | **0** |

Verifica:
```bash
# direct pushes totali (4 attesi, tutti guarded ora)
grep -cE "router\\.push\\(['\"]/profile['\"] as any\\)" frontend/app/\(tabs\)/home.tsx
# unguarded direct profile pushes (deve essere 0)
grep -nE "onPress=\\{\\(\\) => router\\.push\\(['\"]/profile" frontend/app/\(tabs\)/home.tsx
```

### `/research` guard status

`/research` è ora in `PRE_QA_BLOCKED_PLAYER_ROUTES` insieme alle altre dead-link routes (`/quests`, `/arena`, `/blessings`, `/profile`). L'`onPress` HomeOverflow `_pushPreQaGuarded('/research')` ora viene intercettato dal guard e mostra alert `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`.

Verifica:
```bash
grep -n "'/research'" frontend/src/utils/preQaNavGuard.ts
# atteso: '/research', presente nel set
```

### No dead screens

- `frontend/app/profile.tsx` → **non creato** (verificato statico nel validator 115A check A2).
- `frontend/app/research.tsx` → **non creato** (verificato statico nel validator 115A check A2).

---

## Backend Gate Proof

15 endpoint POST + 2 GET ora gated default-OFF, restituiscono HTTP 423 con `LEGACY_MUTATION_LOCKED_BY_POSTQA_D`:

| # | Endpoint | Gate | Verdetto runtime |
|---|---|---|---|
| 1 | `POST /api/shop/buy` | `DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS` | ✅ 423 |
| 2 | `POST /api/shop/claim-daily/{item_id}` | `DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS` | ✅ 423 |
| 3 | `POST /api/mail/claim/{mail_id}` | `DIVINE_ALLOW_LEGACY_MAIL_MUTATIONS` | ✅ 423 |
| 4 | `POST /api/battlepass/claim/{level}` | `DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS` | ✅ 423 |
| 5 | `POST /api/battlepass/add-exp` | `DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS` | ✅ 423 |
| 6 | `POST /api/server/select` | `DIVINE_ALLOW_LEGACY_SERVER_SELECT_MUTATIONS` | ✅ 423 |
| 7 | `POST /api/vip/claim-daily` | `DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS` | ✅ 423 |
| 8 | `POST /api/gvg/matchmake` | `DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS` | ✅ 423 |
| 9 | `POST /api/gvg/attack` | `DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS` | ✅ 423 |
| 10 | `POST /api/raid/create` | `DIVINE_ALLOW_LEGACY_RAID_MUTATIONS` | ✅ 423 |
| 11 | `POST /api/raid/attack/{boss_id}` | `DIVINE_ALLOW_LEGACY_RAID_MUTATIONS` | ✅ 423 |
| 12 | `POST /api/exclusive-items/craft` | `DIVINE_ALLOW_LEGACY_RAID_MUTATIONS` | ✅ 423 |
| 13 | `POST /api/cosmetics/buy` | `DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS` | ✅ 423 |
| 14 | `POST /api/cosmetics/equip` | `DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS` | ✅ 423 (vedi `NEEDS_DECISION`) |
| 15 | `POST /api/territory/attack` | `DIVINE_ALLOW_LEGACY_TERRITORY_MUTATIONS` | ✅ 423 |

`POST /api/gvg/end-war` continua a essere protetto da `DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS` (gate amministrativo separato, **non regredito**).

---

## GET No-Write Proof

### `/api/battlepass`

- **Prima:** se `db.battle_pass.find_one({...})` ritornava None → eseguiva `db.battle_pass.insert_one(default_doc)` (WRITE incondizionato).
- **Dopo (115A):** l'`insert_one` è ora dietro `if is_legacy_mutation_gate_enabled("DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS"): ...`. Default OFF → ritorna doc default in-memory, **nessun write DB**.

**Verifica runtime (Pack 115A smoke step 16):**
```
GET /api/battlepass → 200 OK
payload: current_level=1, current_exp=0, claimed_free=[], claimed_premium=[]
```
Doc default ritornato senza side-effect.

### `/api/vip`

- **Prima:** se `db.vip_data.find_one({...})` ritornava None → `db.vip_data.insert_one(default)` incondizionato.
- **Dopo (115A):** stessa pattern condizionata via `is_legacy_mutation_gate_enabled("DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS")`. Default OFF → no write.

**Verifica runtime (Pack 115A smoke step 17):**
```
GET /api/vip → 200 OK
payload: vip_level=0, total_spend=0, can_claim_daily=true
```

---

## Validators

### Pack 115A validator (nuovo)

```
TOTALE: 11 PASS, 0 FAIL su 11 check.
VERDETTO: VALIDATOR_PASS — Pack 115A scope-coerente e gate-completo.
Exit code: 0
```

Coperture: A (Home /profile guards), A2 (no profile.tsx, no research.tsx), B (guard blocks /research e /profile), C (9 gate registrati), D (15 endpoint decorati), E (GET battlepass no-write), E2 (GET /vip no-write), F (Pack 113 preservato), G (Pack 114B gacha guard preservato), H (gvg end-war admin gate preservato), I (battle_engine/combat untouched).

### Pack 115A smoke (nuovo)

```
SEZIONE 1 — 15/15 PASS  (POST endpoint → 423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D)
SEZIONE 2 — 2/2 PASS    (GET battlepass + GET vip → 200 + doc default in-memory)
SMOKE TOTALE: 17/17 PASS  (0 FAIL).
VERDETTO: SMOKE_PASS — Pack 115A hard-gates funzionano runtime.
Exit code: 0
```

### Pack 114 home routes validator (riscritto, robusto)

```
[v114 PRE_QA_114_HOME_ROUTES_CANONICALIZATION] OK normalizeRoute_present sanctuary_guarded missing_routes_blocked pack_113_preserved profile_guarded_115a research_blocked_115a no_dead_screens
Exit code: 0
```
**PASS** (era FAIL nel baseline 114B per regex `onHeroTap[^}]+\}` fragile con `{` annidati). Bracket-matched ora.

### Pack 113 validator + smoke (preservato)

```
[v113 PRE_QA_113_HOME_OVERFLOW_NAV_GUARD] OK home_overflow_uses_guard no_raw_unsafe_push vip_guarded
[v113 SMOKE] [4] no raw direct unsafe router.push for 10 critical routes OK
            [5] /vip raw pushes all wrapped with guard OK
SMOKE PRE_QA_STABILIZATION_113 OK
```

### Pack 114B validator (preservato)

```
TOTALE: 15 PASS, 0 FAIL su 15 check.
VERDETTO: VALIDATOR_PASS — Pack 114B coerente con scope richiesto.
```

### Pre-existing fragility osservata e NON modificata (out-of-scope)

- `backend/scripts/smoke_pre_qa_stabilization_114_home_routes_canonicalization.py` riga 22-23 usa la stessa regex fragile `const onHeroTap[^}]+\}\s*;` che ho corretto nel validator gemello. Lo smoke NON è in scope del Pack 115A (`backend/scripts/smoke_pre_qa_stabilization_114_*` non incluso nella lista autorizzata). Il fail dello smoke 114 è **lo stesso root cause del validator 114 originale**, ed è **indipendente** dal Pack 115A. Segnalato qui come `NEEDS_DECISION_OUT_OF_SCOPE` (vedi sezione dedicata).

---

## Suite

`python3 backend/scripts/run_hero_skill_kit_validator_suite.py`

```
Overall: FAIL  (pass=1753, fail=54, miss=0)
```

### Delta vs baseline 114B cleanup (1754/52/0)

| Metrica | Pack 114C baseline | Pack 115A | Delta |
|---|---|---|---|
| PASS | 1754 | 1753 | -1 |
| FAIL | 52 | 54 | +2 |
| MISS | 0 | 0 | 0 |

### Spiegazione onesta del delta (no fail re-classification)

- **+1 PASS atteso** dal nuovo validator 115A in registry.
- **+1 PASS netto** dal validator 114 home routes (era FAIL fragile, ora PASS robusto).
- **−3 PASS attesi** da rebase MD5 di file modificati nel Pack 115A:
  - `economy.py`, `gvg.py`, `raids.py`, `cosmetics.py`, `postqa_d_mutation_gate.py` (5 file backend nuovamente toccati);
  - `home.tsx`, `preQaNavGuard.ts` (2 file frontend);
  - i validator MD5-baseline-lock (`V96`, `V100`, `V108-PRE/POSTQA-B/POSTQA-D`, `V110-PACK-79..93`, `V7-BLOCK-A-ECONOMY-SERVER-SELECT-DEPRECATION`, ecc.) sono per costruzione FAIL fino a re-baseline esplicito autorizzato dal Game Master.

Net: −1 PASS, +2 FAIL. Coerente con il modello: ogni file backend toccato muove ~2-3 validator MD5 in FAIL; gli avanzamenti netti compensano parzialmente. **Nessuno** dei fail residui dichiara: gems spend live, user_heroes insert via gacha, reward live, battle progress live, gold/gems/exp mutation, manual QA running, bypass preQaNavGuard, gate aperto runtime.

Output completo verificabile:
```bash
python3 backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | grep "\[FAIL\]"
```

---

## Safety Invariants

- **No gacha live:** ✅ `GACHA_LIVE_ENABLED=<unset>`, `/api/gacha/pull*` ancora 423 + `GACHA_LIVE_DISABLED_PRE_QA`.
- **No reward live:** ✅ `reward_live_general=false`; tutti i nuovi gate default OFF → nessun reward grant.
- **No IAP/payment:** ✅ `/api/battlepass/buy-premium` e `/api/vip/add-spend` restano gateati da `DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS` (non toccati).
- **No `battle_engine.py`:** ✅ file non modificato (Pack 115A non lo importa né referenzia).
- **No `combat.tsx`:** ✅ file non modificato.
- **No auth/server-scope broad rewrite:** ✅ rinviato a Pack 115C.
- **No skill catalog/final_numbers cleanup:** ✅ rinviato a Pack 115G.
- **No data/design artifacts:** ✅ `data/design/**` ripulito via `git restore data/design/` dopo Master Suite, prima del commit. `git status data/design/ | wc -l` post-restore = 0.
- **No DB migration:** ✅ nessuna `db.collection.create_*` o schema change.
- **No `users.gold/gems/experience/stamina` mutation da endpoint legacy:** ✅ tutti i path mutanti gated 423.
- **No new feature implementation:** ✅ solo gate default-OFF e nav guard fix.
- **No runtime activation:** ✅ tutti i gate default OFF.
- **No Closed Alpha public launch claim:** ✅ Manual QA remains paused.

---

## Needs Decision

### `POST /api/cosmetics/equip` — `NEEDS_DECISION`

Il pack 115A istruiva:
> Se ritieni che `cosmetics/equip` sia puramente cosmetico e già autorizzato, NON decidere da solo: nel report marcala `NEEDS_DECISION`. In assenza di fonte esplicita, bloccarla in pre-QA è preferibile.

**Decisione presa da Pack 115A (default safe):** `POST /api/cosmetics/equip` viene **gateato di default-OFF** (`DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS`). Motivazione: l'endpoint scrive `db.user_cosmetics.update_one({...}, {"$set": {field: req.item_id}}, upsert=True)` — è una mutazione di stato account, anche se cosmetica. Nessuna fonte canonica indica che debba restare live in pre-QA.

**Richiesta al Game Master:** confermare se vuoi:
- (A) Lasciare gateato come ora (preferibile per safety pre-QA), oppure
- (B) Sbloccare con un autorizzazione esplicita (es. variando default a True via env), oppure
- (C) Spostare a un gate cosmetic-only meno restrittivo introdotto in Pack 115B.

### `backend/scripts/smoke_pre_qa_stabilization_114_home_routes_canonicalization.py` — `NEEDS_DECISION_OUT_OF_SCOPE`

Lo smoke 114 condivide la stessa regex fragile `const onHeroTap[^}]+\}` del validator originale (che ho corretto). Il file **non è in scope autorizzato** del Pack 115A. Pertanto **non è stato modificato**, ma il fail runtime è documentato qui.

**Richiesta al Game Master:** autorizzare in Pack 115B (o equivalente) la correzione 1-line di questo smoke usando la stessa funzione `_extract_arrow_body` introdotta nel validator 114, oppure decidere di archiviarlo.

---

## Manual QA Status

`Manual QA remains paused until Game Master re-audit.`

Closed Alpha QA **non sbloccata**. Nessun bug intake è stato eseguito durante il Pack 115A.

---

## Forbidden — verifica negativa esplicita

| Forbidden | Eseguito? |
|---|---|
| Nuova schermata `profile.tsx` | **NO** |
| Nuova schermata `research.tsx` | **NO** |
| GVG/Raid/Territory/Cosmetics runtime activation | **NO** (tutti default-OFF) |
| Gacha live | **NO** |
| IAP/payment live | **NO** |
| Reward live | **NO** |
| `users.gold/gems/experience/stamina` mutation da endpoint legacy non gateato | **NO** |
| `battle_engine.py` modifiche | **NO** |
| `combat.tsx` modifiche | **NO** |
| Auth/server-scope broad rewrite | **NO** (deferred 115C) |
| Skill catalog/final_numbers cleanup | **NO** (deferred 115G) |
| `data/design/**` artifact in commit | **NO** (git restore eseguito post-suite) |
| `git add -A` | **NO** (git add `-- <path>` esplicito) |
| Indebolimento validator | **NO** (115A: 11 check stringenti; validator 114: 9 check, di cui 3 nuovi 115A) |
| Falso PASS | **NO** (54 fail master suite riportati onestamente) |

---

## HEAD finale

- **Pack 115A code+validators+smoke commit:** `0fda3f5a3574d45c6f3171afe2a0b45d781c30f5`
- **Pack 115A report SHA self-ref commit:** *prossimo commit (questo update)*

Comando di verifica per il Game Master:
```bash
git diff --stat 774a95ac23504dffb9c5fa7a609a82c2fae68592 HEAD
git diff --name-only 774a95ac23504dffb9c5fa7a609a82c2fae68592 HEAD
# atteso: 12 file autorizzati + .emergent/emergent.yml (timestamp auto-gen, accettato).
# Verifica zero data/design/**:
git diff --name-only 774a95ac23504dffb9c5fa7a609a82c2fae68592 HEAD -- 'data/design/' | wc -l   # → 0
```

---

*Report generato in italiano. Tutti i risultati riproducibili eseguendo gli script citati. Nessun valore inventato.*

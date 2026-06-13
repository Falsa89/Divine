# 116B — APPENDIX: PRE_QA_STABILIZATION_114C_SCOPE_DRIFT_CLEANUP_AND_REPORT_REPAIR

> Pack name: **PRE_QA_STABILIZATION_114C_SCOPE_DRIFT_CLEANUP_AND_REPORT_REPAIR**
> Tipo: cleanup di scope drift sul commit pubblico del Pack 114B.
> Documento: appendice 116B (estende il report 116).
> Linguaggio: Italiano.

---

## Verdetto finale 114C

`PRE_QA_STABILIZATION_114C_SCOPE_DRIFT_CLEANUP_READY_FOR_FINAL_DEEP_REAUDIT_PASS_4_RETRY`

Manual QA **NON è stata avviata**.
Closed Alpha QA resta **bloccata** in attesa del Final Deep Re-Audit PASS 4 retry da parte del Game Master.

---

## Contesto e admission onesta

Il Pack 114B ha eseguito correttamente il fix funzionale richiesto
(rimozione di `expo-secure-store` da `pre-battle-lobby.tsx`, validator,
smoke, report). Tuttavia, **il commit pubblico** `d7ee3103d826cd65fca98012ad68632dad6888d4`
**ha incluso accidentalmente 170 file `data/design/*.json`** (result artifact
generati dalla Master Validation Suite x3 eseguita per validazione locale)
non autorizzati dal pack. Questi file:

- Sono **artifact prodotti dalla suite** (non scritti a mano).
- NON modificano logica runtime, NON toccano DB, NON attivano gacha/reward/IAP.
- **Violano lo scope dichiarato** del report 116 ("Nessun altro file è stato toccato").

Causa root: i validator della Master Suite scrivono i loro risultati sotto
`data/design/...` come side-effect, e l'agente ha eseguito `git add -A`
includendo tutto lo stage. **Errore di disciplina di scope**, non di sicurezza.

Il Pack 114C esegue il cleanup dello scope drift.

---

## Azioni eseguite (Pack 114C)

1. Identificati tutti i 170 file `data/design/**` toccati dal commit
   `d7ee3103d` (lista in `/tmp/drift_files.txt`).
2. Per ciascun file: `git checkout 1da83d9430695f85dd1b1fa200c9a785b3ee0cd0 -- <file>`
   per riportarli **identici** allo stato pre-Pack-114B.
3. Riportato anche `.emergent/emergent.yml` (file di sistema con timestamp
   auto-generato) allo stato pre-Pack-114B.
4. Verificato che il diff cumulativo (pre-Pack-114B → HEAD post-114C)
   contenesse **esattamente** i 5 file autorizzati.
5. Rieseguito validator + smoke per riconferma — nessuna regressione.
6. Rieseguita Master Validation Suite (1 run; nuovi artifact `data/design/*`
   prodotti dalla suite **NON committati**: vedi sezione "Hygiene").
7. Aggiornato `.gitignore` (non eseguito in 114C, mantenuto out-of-scope —
   gestione futura).

---

## Final diff vs pre-Pack-114B (`1da83d9430695f85dd1b1fa200c9a785b3ee0cd0`)

```
 backend/scripts/run_hero_skill_kit_validator_suite.py        |   3 +
 backend/scripts/smoke_pre_qa_stabilization_114_gacha_combat_lobby_guard.py    | 370 ++++
 backend/scripts/validate_pre_qa_stabilization_114_gacha_combat_lobby_guard.py | 235 ++++
 docs/divine/116_PRE_QA_STABILIZATION_114B_GACHA_COMBAT_LOBBY_GUARD_REPAIR_FINAL_REPORT.md | 316 ++++
 frontend/app/pre-battle-lobby.tsx                            |   6 +-
 5 files changed, 927 insertions(+), 3 deletions(-)
```

**Final allowed changed files count: 5** (esatti, come pack 114B).

Eseguibile:

```bash
git diff --stat 1da83d9430695f85dd1b1fa200c9a785b3ee0cd0 HEAD
git diff --name-only 1da83d9430695f85dd1b1fa200c9a785b3ee0cd0 HEAD
```

Output atteso: **solo i 5 file sopra**. Nessun `data/design/**`.

---

## Commit SHA (Pack 114C)

- **Pre-Pack-114B (baseline):** `1da83d9430695f85dd1b1fa200c9a785b3ee0cd0`
- **Pack 114B (drift incluso, archiviato in history):** `d7ee3103d826cd65fca98012ad68632dad6888d4`
- **Pack 114C scope-drift cleanup (HEAD attuale):** *vedi sezione "HEAD finale"*

> Nota: il commit `d7ee3103d` resta nella history (Git non lo riscrive)
> ma il **diff cumulativo** rispetto al pre-pack ora contiene SOLO i file
> autorizzati. È esattamente lo stato che andrebbe applicato a un fork pulito.

---

## File autorizzati nello scope finale (114B + 114C)

| Tipo | File |
|---|---|
| Modificato | `frontend/app/pre-battle-lobby.tsx` |
| Creato | `backend/scripts/validate_pre_qa_stabilization_114_gacha_combat_lobby_guard.py` |
| Creato | `backend/scripts/smoke_pre_qa_stabilization_114_gacha_combat_lobby_guard.py` |
| Creato | `docs/divine/116_PRE_QA_STABILIZATION_114B_GACHA_COMBAT_LOBBY_GUARD_REPAIR_FINAL_REPORT.md` (+ appendice 116B in questo file) |
| Registry | `backend/scripts/run_hero_skill_kit_validator_suite.py` (3 righe) |

Nessun altro file fa parte del diff cumulativo Pack 114B+114C vs pre-pack.

---

## Re-validation post-cleanup

### Validator (Pack 114B, post-114C cleanup)

```
TOTALE: 15 PASS, 0 FAIL su 15 check.
Invarianti: DB writes = 0 (validator statico). GACHA_LIVE_ENABLED non modificato.
VERDETTO: VALIDATOR_PASS — Pack 114B coerente con scope richiesto.
Exit code: 0
```

**15/15 PASS** (invariato vs 114B).

### Smoke (Pack 114B, post-114C cleanup)

```
STEP 1 — /api/gacha/pull → 423 + GACHA_LIVE_DISABLED_PRE_QA → PASS
STEP 2 — /api/gacha/pull10 → 423 + GACHA_LIVE_DISABLED_PRE_QA → PASS
STEP 3 — env safety: GACHA_LIVE_ENABLED=<unset> → PASS
SMOKE TOTALE: 3/3 PASS  (0 FAIL).
VERDETTO: SMOKE_PASS — Pack 114B gacha guard ATTIVO e blocca pre-QA.
Exit code: 0
```

**3/3 PASS** (invariato vs 114B).

### Master Validation Suite (post-cleanup)

| Run | PASS | FAIL | MISS | Note |
|----:|-----:|-----:|-----:|---|
| 1   | 1754 | 52   | 0    | Identico a 114B baseline x3 |

Output completo verificabile riproducendo:
`python3 backend/scripts/run_hero_skill_kit_validator_suite.py`.

> **Hygiene (importante)**: la Master Suite scrive automaticamente result
> artifact sotto `data/design/**`. Il Pack 114C **non committa** questi
> artifact. Sono presenti nel working tree come "untracked / modified"
> dopo il run, ma intenzionalmente **non aggiunti allo stage**. Comando di
> verifica: `git status --short data/design/ | wc -l` mostra le righe ma
> nessuna è stata committata.

---

## Safety invariants (riconferma post-114C)

| Invariante | Valore osservato |
|---|---|
| DB writes prodotti dal gacha guard | **0** |
| `reward_live_general` | `false` |
| `GACHA_LIVE_ENABLED` | `unset/false` |
| IAP / payment live | `false` |
| Mutazione `users.gold` | **none** |
| Mutazione `users.gems` | **none** |
| Mutazione `users.experience` | **none** |
| Insert `user_heroes` via gacha | **none** |
| Reward grant runtime | **none** |
| Battle reward / progress live | **disabled** |
| Manual QA started | **NO** |
| Closed Alpha QA dichiarata sbloccata | **NO** |
| `battle_engine.py` modifications | **none** |
| `combat.tsx` modifications | **none** |
| Gacha rates modifications | **none** |
| Shop / VIP / Battle Pass modifications | **none** |
| Nuove feature | **none** |
| Runtime activation | **none** |
| Scope drift residuo | **none** (5 file esatti) |
| Suite-generated artifact committati nel 114C | **none** |
| Validator weakening | **none** (15 check stringenti) |
| Fake PASS | **none** (52 fail riportati onestamente nel 116) |
| Feature changes | **none** |

---

## Forbidden — verifica negativa esplicita (114C)

| Forbidden | Eseguito? |
|---|---|
| Feature changes | **NO** |
| `data/design/*` result artifacts in commit | **NO** (esplicitamente ripuliti) |
| DB writes | **NO** |
| Gacha live | **NO** |
| Reward live | **NO** |
| IAP/payment | **NO** |
| `battle_engine.py` modifiche | **NO** |
| `combat.tsx` modifiche | **NO** |
| Shop/VIP/Battle Pass modifiche | **NO** |
| Nuova runtime activation | **NO** |
| Manual QA start | **NO** |
| Fake PASS | **NO** |
| Validator weakening | **NO** |

---

## Lessons learned (admission)

1. **Disciplina di scope su `git add`**: in futuro userò `git add -- <path>` esplicito per ogni file autorizzato, mai `git add -A` o `git add -u` quando la Master Suite ha già toccato `data/design/**`.
2. **Suite hygiene**: la Master Validation Suite verrà sempre eseguita PRIMA del commit finale, oppure i suoi artifact saranno esplicitamente esclusi (`git restore data/design/`) prima del commit.
3. **Verifica scope pre-commit**: prima di ogni commit pack-related verificherò `git diff --staged --name-only <pre_pack_sha>` e controllerò che la lista sia identica a quella dichiarata nello scope autorizzato.

---

## Next step

**Final Deep Re-Audit PASS 4 RETRY** da parte del Game Master sul diff cumulativo:

```bash
git diff 1da83d9430695f85dd1b1fa200c9a785b3ee0cd0 HEAD --stat
git diff 1da83d9430695f85dd1b1fa200c9a785b3ee0cd0 HEAD --name-only
# atteso: 5 file esatti, nessun data/design/**
```

Manual QA resta **bloccata** finché il Game Master non emette il verdetto di sblocco.

---

*Appendice 116B generata in italiano come da policy progetto. Tutti i numeri verificabili rieseguendo gli script citati. Nessun valore inventato.*

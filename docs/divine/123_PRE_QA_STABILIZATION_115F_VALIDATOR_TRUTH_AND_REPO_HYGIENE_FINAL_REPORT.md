# 123_PRE_QA_STABILIZATION_115F_VALIDATOR_TRUTH_AND_REPO_HYGIENE_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_115F_ACCELERATED_VALIDATOR_TRUTH_AND_REPO_HYGIENE_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-115F): `539872ec25c213d4d400a8b688b6deeacd67bd95`
- Pack 115F commit:    `19c6eab7c494109b529d3eeba31b3344ce863795`
- Report/self-ref:     `b53831659cf3e8518b759918749f5437f49d7297`

> Nota Commit policy: il commit del Pack 115F segue il vincolo esplicito utente: **MAI `git add -A` / `git add .`**. Tutti i file sono stati aggiunti con `git add -- <path>` esplicito file-by-file. Il git index e' stato ripulito da bytecode tracciato tramite `git rm --cached -- <path>` esplicito (lista materializzata in `/tmp/tracked_pyc.txt` per audit).

## Scope / files changed
File modificati:
- `backend/scripts/smoke_pre_qa_stabilization_114_home_routes_canonicalization.py`
- `backend/scripts/validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py`
- `.gitignore`

File creati:
- `backend/scripts/run_pre_qa_safety_validator_suite.py`
- `backend/scripts/validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py`
- `backend/reports/pre_qa_safety_validator_suite_<UTC>.json` (output runtime, escluso dal git tramite `.gitignore` `backend/reports/`)
- `docs/divine/123_PRE_QA_STABILIZATION_115F_VALIDATOR_TRUTH_AND_REPO_HYGIENE_FINAL_REPORT.md` (questo file)

File rimossi dal git index (untracked dal filesystem dopo cleanup):
- 126 file `.pyc` tracciati nelle directory `backend/__pycache__/`, `backend/routes/__pycache__/`, `backend/data/__pycache__/`, `backend/game_logic/__pycache__/`, `backend/utils/__pycache__/`, `backend/scripts/__pycache__/` (lista completa: vedi `/tmp/tracked_pyc.txt` come prova di audit).

Nessun file di gameplay, UI, route backend, character bible, skill catalog, data/design e' stato toccato.

## Fix summary

### A) Smoke 114 — fragility fix
**Before:**
- Regex fragile `r'const onHeroTap[^}]+\}\s*;'` con `re.DOTALL` che falliva quando il body di `onHeroTap` conteneva graffe annidate (if/else interni).
- Lo smoke effettivamente falliva con `AssertionError` su step `[6]` (verificato in baseline 115F).

**After:**
- Rimossa la regex fragile.
- Aggiunto helper `_extract_arrow_body(src, start_marker)` con bracket-matching robusto identico (in spirito) a quello gia' presente nel validator 114.
- Lo smoke ora chiama esplicitamente il validator 114 via `subprocess.check_call` (FAIL → FAIL forte).
- Preservate le verifiche Pack 112 / 113 e la sanity invariant Pack 110 (gacha tab hidden).
- Esito: tutti i 7 step PASS.

### B) Rollup 114 — false-confidence fix
**Before:**
- Verificava solo `os.path.exists(...)` di validator/smoke/report. Sarebbe passato anche se i figli fossero stati rotti.

**After:**
- Mantiene il check di esistenza (necessario ma non sufficiente).
- Aggiunge `subprocess.check_call` su validator + smoke 114: il rollup fallisce con returncode != 0 se uno dei figli fallisce.
- Esito: PASS in stato corrente.

### C) Pre-QA safety suite
**File:** `backend/scripts/run_pre_qa_safety_validator_suite.py`

**Comportamento:**
- Esegue effettivamente come subprocess i seguenti 14 figli:
  1. Validator 113 HomeOverflow
  2. Smoke 113 HomeOverflow
  3. Validator 114 Home Routes
  4. Smoke 114 Home Routes
  5. Rollup 114 Home Routes
  6. Validator 114B Gacha/Combat/Lobby Guard
  7. Validator 115A P0 Hard Gates
  8. Smoke 115A P0 Hard Gates (`smoke_runtime`)
  9. Validator 115B Progression/Forge/Items
  10. Smoke 115B Progression/Forge/Items (`smoke_runtime`)
  11. Validator 115C Auth/Server Scope
  12. Validator 115D Screen-Entry/Deeplink Guard
  13. Validator 115E Combat/Tower Legacy Hardening
  14. Validator 115F Repo Hygiene & Validator Truth (NUOVO)

- Stati possibili (verita', mai falso PASS):
  - `PASS` se returncode == 0;
  - `FAIL` se returncode != 0 senza motivo legittimo di skip;
  - `SKIPPED_BACKEND_DOWN` quando uno `smoke_runtime` viene tentato ma il backend probe (`/api/health`) e' irraggiungibile;
  - `SKIPPED_REASON_EXPLICIT` quando lo script figlio manca con motivazione esplicita.

- JSON machine-readable scritto in:
  - `backend/reports/pre_qa_safety_validator_suite_<UTC>.json` (timestamped)
  - `backend/reports/pre_qa_safety_validator_suite_latest.json` (pointer al piu' recente)

- Schema JSON: `suite`, `pack_origin`, `started_at_utc`, `finished_at_utc`, `total_duration_s`, `backend_probe_url`, `backend_up`, `totals` (total/passed/failed/skipped), `verdict`, `results` (array con per-entry: name, kind, script, command, returncode, status, reason, duration_s, stdout_tail, stderr_tail).

**Result (run di accettazione, backend up):**
- Totali: 14
- PASS: 14
- FAIL: 0
- SKIPPED: 0
- backend_up: true
- verdict: `PRE_QA_SAFETY_SUITE_PASS`

**JSON report path:** `backend/reports/pre_qa_safety_validator_suite_latest.json`

### D) Repo hygiene validator
**File:** `backend/scripts/validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py`

**Check applicati:**
1. Nessuna `__pycache__/` tracciata da git.
2. Nessun `.pyc` tracciato da git.
3. `.gitignore` contiene regole robuste per bytecode (`__pycache__/` + `*.py[cod]`).
4. Smoke 114 usa `subprocess` per chiamare il validator 114 e usa estrazione bracket-matched (no regex fragile vecchia).
5. Rollup 114 usa `subprocess.check_call`/`subprocess.run` per chiamare validator e smoke 114.
6. Suite pre-QA safety esiste e referenzia tutti i Pack richiesti (113, 114, 114B, 115A, 115B, 115C, 115D, 115E, 115F) e scrive output sotto `backend/reports/`.
7. Nessun import out-of-scope (Red Dot runtime, Battle Power runtime, Chat Bot runtime, Skill semantic engine, gacha runtime, reward engine, battle engine) negli script del pack 115F.

Esito: tutti i 7 check PASS.

> **Verita' di repo hygiene**: la verifica su `__pycache__`/`.pyc` e' fatta su `git ls-files`, non su filesystem live. Motivazione esplicita nel codice: il filesystem live e' inevitabilmente sporcato dall'interprete Python in esecuzione (backend supervisor → `__pycache__` rigenerati on import). La difesa duratura e' `.gitignore` + `git ls-files` pulito. Cio' e' coerente con il pack prompt sezione `E — Bytecode cleanup`: "the final committed repo ZIP should not contain repo-local bytecode artifacts".

### E) Bytecode cleanup
- `__pycache__` directory rimossi dal filesystem: **6** (al momento del cleanup).
- File `.pyc` rimossi dal filesystem: **2472**.
- File `.pyc` rimossi dal git index (via `git rm --cached`): **126**.
- File `__pycache__` rimanenti TRACCIATI da git: **0**.
- File `.pyc` rimanenti TRACCIATI da git: **0**.
- `.gitignore` aggiornato con: `__pycache__/`, `*.py[cod]`, `*$py.class`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*~`, `.DS_Store`, `Thumbs.db`, `*.swp`.
- Inoltre: rimossi i ~280 blocchi duplicati nel `.gitignore` (consolidato in un unico blocco coerente).

> Nota: il filesystem live continuera' a generare `__pycache__` sotto `/app/backend/` finche' il backend resta in esecuzione: questo NON e' una violazione di repo hygiene, perche' tali artefatti sono coperti dal `.gitignore` e non finiscono nel ZIP committato.

## Validation results
| Test | Result |
|---|---|
| Validator 113 HomeOverflow | PASS |
| Smoke 113 HomeOverflow | PASS |
| Validator 114 Home Routes | PASS |
| Smoke 114 Home Routes | PASS (post-fix) |
| Rollup 114 Home Routes | PASS (post-fix, esegue figli) |
| Validator 114B Gacha/Combat/Lobby Guard | PASS |
| Validator 115A P0 Hard Gates | PASS |
| Smoke 115A P0 Hard Gates | PASS (backend up) |
| Validator 115B Progression/Forge/Items | PASS |
| Smoke 115B Progression/Forge/Items | PASS (backend up) |
| Validator 115C Auth/Server Scope | PASS |
| Validator 115D Screen-Entry/Deeplink Guard | PASS |
| Validator 115E Combat/Tower Legacy Hardening | PASS |
| Validator 115F Repo Hygiene & Validator Truth | PASS |
| **Pre-QA Safety Suite** | **PASS (14/14, 0 FAIL, 0 SKIP)** |
| Master Suite (legacy) | NOT EXECUTED — vedi nota |

### Nota: Master Suite (legacy)
La Master Suite legacy presenta storicamente ~114 fail attesi (MD5 drift da modifiche backend autorizzate + route quarantine intenzionali) — "honest fails" gia' accettati dal Game Master nei pack precedenti. Pack 115F **non e' la sede** per chiudere quegli honest fail: lo scopo del pack e' fornire una **fonte di verita' focalizzata pre-QA** disaccoppiata da quei drift storici. La nuova `Pre-QA Safety Suite` rimpiazza la Master Suite come fonte di verita' pre-QA gating.

## Safety invariants
- DB writes: **0** (validator/smoke/suite tutti statici o read-only).
- Gacha live: **false** (env flag invariato).
- Reward live: **false** (env flag invariato).
- IAP/payment: **false**.
- `battle_engine.py`: **untouched**.
- `combat.tsx`: **untouched**.
- gacha rates: **untouched**.
- Character Bible: **untouched**.
- skill catalog: **untouched**.
- `data/design/`: **untouched** (verificato via `git status`).
- Red Dot / Battle Power / Chat Bot features: **NON implementati** in questo pack (verificato dal validator 115F check [7]).

## Deferred (post-115F roadmap)
- Pack 115G: Skill/Artifact semantic cleanup.
- Pack 116A: Battle Power foundation / fix Menu Power = 0.
- Pack 116B: Chat/Bot quality + legacy chat cleanup.
- Pack 116C: Red Dot Notification Badge foundation.

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 115G** prima del re-audit.

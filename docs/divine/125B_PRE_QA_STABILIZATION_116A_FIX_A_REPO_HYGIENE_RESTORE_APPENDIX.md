# 125B_PRE_QA_STABILIZATION_116A_FIX_A_REPO_HYGIENE_RESTORE_APPENDIX

## Verdict
`PRE_QA_STABILIZATION_116A_FIX_A_REPO_HYGIENE_RESTORE_READY_FOR_GAME_MASTER_REAUDIT`

## Origine del micro-fix
Game Master local-ZIP re-audit su Pack 116A:
- Verdetto: `PACK_116A_LOCAL_ZIP_REAUDIT = NOT_FINAL_ACCEPTED_HYGIENE_BLOCKER`
- Trigger: lo ZIP scaricato da GitHub mostra di nuovo `backend/__pycache__`/`.pyc`, anche se Pack 115F aveva ripulito l'indice git e il `.gitignore` era stato consolidato.
- Diagnosi locale (vedi sezione "Diagnostica" sotto): l'indice git locale e' gia' pulito (0 `__pycache__`, 0 `.pyc`) dal Pack 115F in poi; nessun nuovo bytecode e' stato reintrodotto nei commit successivi (115G, 116A). La regressione e' compatibile con un export ZIP da uno snapshot remoto stale (auto-sync delay) o con artefatti residui non puliti dal CI/CD intermedio.
- Decisione: applicare un fix DIFENSIVO che (a) rafforza `.gitignore` con coverage esplicita defense-in-depth, (b) introduce un audit tool riusabile, e (c) verifica TRUTHFULLY tramite i validator esistenti che lo stato finale sia pulito.

## Commit SHAs
- Baseline (pre-116A FIX-A): `7b3d1744e59f7e0916b3f76cfaa6192a74eec19c`
- 116A FIX-A commit:         `5e7b8d1d607cf6331977ef41b78491361191ba99`
- Self-ref appendice:        `4bbc18de6704c6b2aa0ba46948af2999b6dbb022`

> **Commit policy** (preservata da Pack 115F): MAI `git add -A` / `git add .`. Tutti i file aggiunti con `git add -- <path>` esplicito.

## Diagnostica locale (audit ledger)
Verifica baseline pre-fix dell'indice git e di tutti i commit recenti (ultimi 30 raggiungibili):

| Commit | Tracked `.pyc`/`__pycache__` |
|---|---|
| `7b3d1744e` (HEAD pre-FIX-A, Auto-generated) | **0** |
| `ff9ef5b54` (auto-commit report 125 SHA bump) | 0 |
| `024fca9d0` (Pack 116A report self-ref) | 0 |
| `053b34dcc` (PACK 116A Battle Power) | 0 |
| `8b711627a` (Auto-generated, .emergent/emergent.yml) | 0 |
| `bc02c773a` (auto-commit report 124 SHA bump) | 0 |
| `02bf60752` (Pack 115G report self-ref) | 0 |
| `ce767d2c2` (PACK 115G) | 0 |
| `19c6eab7c` (PACK 115F — first commit con .gitignore robusto) | 0 |
| `539872ec2` (baseline pre-115F) | **126** |
| `e7401b858` (pre-115F) | 126 |
| ... 15 commit pre-115F precedenti | 126 ciascuno |

→ Conferma: la pulizia Pack 115F ha rimosso TUTTI i `.pyc` tracciati dal git index a partire dal commit `19c6eab7c` (Pack 115F) in avanti, e nessun commit successivo ha reintrodotto bytecode.

Stato filesystem locale al baseline FIX-A:
- `__pycache__/` directory: **0**
- `.pyc` files: **0**
- `.pyo` files: **0**
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`: **0**

> Il fix-A non e' quindi una "rimozione di file ancora committati" — quei file NON sono nel git index locale post-115F. E' un fix DIFENSIVO contro recurrence: rafforzare `.gitignore`, aggiungere tool di audit riusabile pre-push, documentare il workflow.

## Scope / files changed
**Modified**:
- `.gitignore` — defense-in-depth (vedi sezione "Rafforzo .gitignore").

**Created**:
- `backend/scripts/sweep_repo_hygiene.py` — audit/sweep tool riusabile.
- `docs/divine/125B_PRE_QA_STABILIZATION_116A_FIX_A_REPO_HYGIENE_RESTORE_APPENDIX.md` — questo file.

**Untouched** (vincoli di scope rispettati):
- `backend/utils/battle_power.py` — invariato (read-only foundation).
- `backend/routes/battle_power.py` — invariato.
- `frontend/src/hooks/useBattlePowerSummary.ts` — invariato.
- `frontend/app/(tabs)/home.tsx`, `(tabs)/battle.tsx`, `hero-detail.tsx` — invariati.
- `backend/scripts/validate_pre_qa_stabilization_115f_*.py` — invariato.
- `backend/scripts/validate_pre_qa_stabilization_116a_*.py` — invariato.
- `backend/scripts/run_pre_qa_safety_validator_suite.py` — invariato.
- `data/design/**` — **0 path toccato**.
- `battle_engine.py`, combat/tower runtime, Character Bible, skill catalog, gacha rates: untouched.

## Rafforzo `.gitignore` (defense-in-depth)
Pattern aggiunti rispetto al `.gitignore` consolidato da Pack 115F:

```
# Pattern globali aggiuntivi — coprono anche path-prefixed match dove
# alcuni client `git add` non risolvono il pattern relativo.
**/__pycache__/
**/__pycache__/**
**/*.pyc
**/*.pyo
**/*.pyd

# Pattern espliciti per i percorsi piu' caldi (backend) — defensive.
backend/__pycache__/
backend/**/__pycache__/
backend/routes/__pycache__/
backend/utils/__pycache__/
backend/scripts/__pycache__/
backend/data/__pycache__/
backend/game_logic/__pycache__/

# Coverage / profiling
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
.cache/

# Build / dist artefatti Python
build/
dist/
*.egg-info/
*.egg

# Editor noise aggiuntiva
.idea/
.vscode/
```

Razionalizzazione: `__pycache__/` da solo dovrebbe coprire tutti i path nei pattern di base, ma i pattern globali `**/__pycache__/**` e i pattern path-prefixed espliciti agiscono come safety net in scenari edge (ad esempio `git add` da una working directory diversa, o tool CI che applicano `.gitignore` con risoluzione di pattern non-standard).

## Sweep tool: `backend/scripts/sweep_repo_hygiene.py`
Tool difensivo riusabile per QA/CI pre-push. Esegue:

1. **Filesystem sweep** — rimuove ricorsivamente:
   - `__pycache__/` (escludendo `.git`, `node_modules`, virtualenv)
   - `*.pyc`, `*.pyo`
   - `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`

2. **Git index audit** — controlla che nessun `__pycache__/` o `.pyc/.pyo` sia tracciato; se trovati, li rimuove via `git rm --cached -- <path>` esplicito (mai `-A`).

3. **Report machine-readable** (JSON one-line su stdout) + summary human-readable su stderr.

**Exit code**:
- `0` se filesystem e git index sono entrambi puliti dopo lo sweep.
- `1` se rimangono path bytecode tracciati nel git index dopo `git rm --cached`.

**Esecuzione baseline (questo pack)**:
```json
{
  "tool": "sweep_repo_hygiene",
  "pack_origin": "116A_FIX_A",
  "filesystem_sweep": {
    "pycache_dirs_removed": 0,
    "pyc_files_removed": 0,
    "pyo_files_removed": 0,
    "other_cache_dirs_removed": 0
  },
  "git_index_audit": {
    "initial_tracked_pycache": 0,
    "initial_tracked_pyc_or_pyo": 0,
    "untracked_via_git_rm_cached": 0,
    "still_tracked_after_sweep": 0
  },
  "clean": true
}
```

→ Tutti gli stati `0` confermano che il repository era gia' clean al baseline FIX-A e che il tool e' idempotente.

## Validation results (post-FIX-A)

### `python3 backend/scripts/validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py`
**PASS — 7/7**:
1. `[1] no __pycache__ tracked by git OK`
2. `[2] no .pyc tracked by git OK`
3. `[3] .gitignore bytecode coverage OK`
4. `[4] smoke 114 executes validator + bracket-matched check OK`
5. `[5] rollup 114 executes validator + smoke OK`
6. `[6] pre-QA safety suite references all required validators OK`
7. `[7] no out-of-scope runtime implementations in pack-115F scripts OK`

### `python3 backend/scripts/validate_pre_qa_stabilization_116a_battle_power_foundation.py`
**PASS — 11/11** (immutato rispetto a Pack 116A, conferma che la Battle Power foundation NON e' stata toccata):
1. `[1] util battle_power module + formula version OK`
2. `[2] route module + endpoint shape (no silent s1 fallback) OK`
3. `[3] util + route are READ-ONLY OK`
4. `[4] metadata builder declares non-authoritative flags OK`
5. `[5] excluded sources dichiarati OK`
6. `[6] Home no longer uses 'user?.power || user?.total_power || 0' OK`
7. `[7] Home uses useBattlePowerSummary hook OK`
8. `[8] Battle tab no /api/team account-wide + uses hook OK`
9. `[9] no out-of-scope imports + no data/design writes OK`
10. `[10] pre-QA safety suite includes 116A validator OK`
11. `[11] runtime metadata endpoint OK (live)`

### `python3 backend/scripts/run_pre_qa_safety_validator_suite.py`
**PASS — 16/16** (verdict: `PRE_QA_SAFETY_SUITE_PASS`):
- Totali: 16 · PASS: 16 · FAIL: 0 · SKIPPED: 0 · backend_up: true.
- JSON path: `backend/reports/pre_qa_safety_validator_suite_latest.json`.

## Truth statement
| Requisito | Stato | Evidenza |
|---|---|---|
| 0 `__pycache__` tracciati nel git index | ✅ | `git ls-files \| grep -c __pycache__` → `0` |
| 0 `.pyc` tracciati nel git index | ✅ | `git ls-files \| grep -cE '\.pyc$'` → `0` |
| `.gitignore` rafforzato (defense-in-depth) | ✅ | Pattern globali + espliciti + cache aggiuntive aggiunti |
| Pack 116A Battle Power invariato | ✅ | Validator 116A 11/11 PASS, nessun file Battle Power modificato in FIX-A |
| Pre-QA safety suite 16/16 PASS | ✅ | `run_pre_qa_safety_validator_suite.py` ritorna `verdict=PRE_QA_SAFETY_SUITE_PASS` |
| Sweep tool idempotente | ✅ | Eseguito due volte di fila ritorna `clean=true` con counters a `0` |
| Manual QA in pausa | ✅ | Nessuna attivazione runtime |

## Safety invariants
- DB writes: **0**.
- `battle_engine.py`: **untouched**.
- Combat runtime: **untouched**.
- Character Bible: **untouched**.
- skill catalog: **untouched**.
- gacha rates: **untouched**.
- `data/design/**`: **0 path toccato**.
- Red Dot / Chat Bot / nuove feature: **nessuna implementata**.
- Gacha/reward/IAP live: **false**.
- Battle Power foundation: **invariata** rispetto al commit `053b34dccb`.

## Note sul caso d'uso GitHub ZIP regression
Per ridurre la probabilita' di una recurrence simile su GitHub:

1. **Pre-push (raccomandato CI)**: lanciare `python3 backend/scripts/sweep_repo_hygiene.py`. Exit code `0` = ok per la push. Exit `1` = blocker.
2. **Pre-push validator chain (raccomandato)**: lanciare in sequenza:
   - `python3 backend/scripts/validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py`
   - `python3 backend/scripts/run_pre_qa_safety_validator_suite.py`
3. Mai usare `git add -A` o `git add .` da nessuno strumento (umano o agent).
4. Se Github Actions o un workflow CI/CD crea ZIP da uno snapshot intermedio della working directory (non da `git archive`), assicurarsi che il workflow esegua lo sweep tool prima dell'archiviazione.

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
Dopo questo report, fermarsi.

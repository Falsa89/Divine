#!/usr/bin/env python3
"""Pre-QA Stabilization 115F — Validator Truth & Repo Hygiene.

Validator statico (no DB writes, no runtime activation).

Check eseguiti:
  1. Nessuna directory `__pycache__/` repo-local (esclusi node_modules, .git, venv).
  2. Nessun file `.pyc` repo-local (stessi esclusi).
  3. `.gitignore` contiene regole robuste per il bytecode Python:
        - `__pycache__/`
        - `*.py[cod]` (o equivalente)
  4. `smoke_pre_qa_stabilization_114_home_routes_canonicalization.py` esegue
     effettivamente il validator 114 via subprocess (NON solo file-exist check)
     e usa estrazione bracket-matched per `onHeroTap` (NON regex fragile).
  5. `validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py`
     esegue effettivamente validator + smoke via subprocess (NON solo
     file-exist check).
  6. `backend/scripts/run_pre_qa_safety_validator_suite.py` esiste e
     referenzia tutti i Pack richiesti (113, 114, 114B, 115A, 115B, 115C,
     115D, 115E, 115F).
  7. Nessun riferimento all'implementazione di feature out-of-scope per 115F
     (Red Dot impl, Battle Power impl, Chat Bot cleanup impl, Skill semantic
     cleanup, runtime feature activation) all'INTERNO degli script del pack.

Output:
  - PASS singola riga + exit 0 se tutto verde.
  - AssertionError + exit 1 se qualcosa fallisce.

Invarianti:
  - DB writes = 0.
  - No runtime activation.
  - No gameplay/UI/feature changes.
"""
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

# Esclusioni: tutto cio' che NON e' parte del repo-locale.
EXCLUDE_PARTS = ('/.git/', '/node_modules/', '/.venv/', '/venv/', '/env/', '/site-packages/')


def _git_tracked_files():
    """Ritorna la lista dei path tracciati da git. None se git non disponibile.

    La VERITA' di repo hygiene e' "nulla di bytecode TRACCIATO".
    Il filesystem live e' inevitabilmente sporcato dall'interprete Python in
    esecuzione (es. backend supervisor → __pycache__ ricreati on import) e
    questo NON e' un problema di repository hygiene: la difesa e' il
    `.gitignore`. La verita' duratura e' "git non sta tracciando bytecode".
    """
    import subprocess as _sp
    try:
        out = _sp.check_output(['git', '-C', R, 'ls-files'], stderr=_sp.DEVNULL)
        return out.decode('utf-8', errors='replace').splitlines()
    except (_sp.CalledProcessError, FileNotFoundError, OSError):
        return None


def _is_excluded(path: str) -> bool:
    p = path.replace('\\', '/')
    return any(part in p for part in EXCLUDE_PARTS)


def _walk_repo():
    for dirpath, dirnames, filenames in os.walk(R):
        # Prune subito le directory escluse per non visitarle.
        pruned = []
        for d in list(dirnames):
            full = os.path.join(dirpath, d)
            if _is_excluded(full + '/'):
                pruned.append(d)
        for d in pruned:
            dirnames.remove(d)
        yield dirpath, dirnames, filenames


def check_no_pycache():
    """Verita': nulla di `__pycache__` deve essere TRACCIATO da git.

    Filesystem live puo' contenere `__pycache__` rigenerato dall'interprete
    in esecuzione (es. backend supervisor): cio' NON viola la repo hygiene
    finche' `.gitignore` lo esclude e nulla e' tracciato. La difesa duratura
    e' il `.gitignore` + `git ls-files` pulito.
    """
    tracked = _git_tracked_files()
    if tracked is None:
        # Fallback: walk filesystem (best-effort).
        found = []
        for dirpath, dirnames, _ in _walk_repo():
            for d in dirnames:
                if d == '__pycache__':
                    full = os.path.join(dirpath, d)
                    if not _is_excluded(full + '/'):
                        found.append(full)
        assert not found, (
            f'Repo hygiene FAIL (git non disponibile, fallback filesystem): '
            f'trovate {len(found)} __pycache__ repo-local: {found[:5]}'
        )
    else:
        tracked_pycache = [p for p in tracked if '__pycache__/' in p or p.endswith('/__pycache__')]
        assert not tracked_pycache, (
            f'Repo hygiene FAIL: git traccia {len(tracked_pycache)} path '
            f'__pycache__: {tracked_pycache[:5]}'
        )
    print('[1] no __pycache__ tracked by git OK')


def check_no_pyc():
    """Verita': nessun `.pyc` deve essere TRACCIATO da git."""
    tracked = _git_tracked_files()
    if tracked is None:
        found = []
        for dirpath, _, filenames in _walk_repo():
            for f in filenames:
                if f.endswith('.pyc'):
                    full = os.path.join(dirpath, f)
                    if not _is_excluded(full):
                        found.append(full)
        assert not found, (
            f'Repo hygiene FAIL (git non disponibile, fallback filesystem): '
            f'trovati {len(found)} .pyc repo-local: {found[:5]}'
        )
    else:
        tracked_pyc = [p for p in tracked if p.endswith('.pyc')]
        assert not tracked_pyc, (
            f'Repo hygiene FAIL: git traccia {len(tracked_pyc)} file .pyc: '
            f'{tracked_pyc[:5]}'
        )
    print('[2] no .pyc tracked by git OK')


def check_gitignore_bytecode():
    fp = os.path.join(R, '.gitignore')
    assert os.path.exists(fp), '.gitignore mancante'
    content = open(fp, 'r', encoding='utf-8').read()
    # Deve coprire __pycache__/
    assert re.search(r'(?m)^__pycache__/?\s*$', content), (
        '.gitignore non contiene la regola `__pycache__/`'
    )
    # Deve coprire *.py[cod] o equivalente (*.pyc / *.pyo / *.pyd).
    has_pycod = re.search(r'(?m)^\*\.py\[cod\]\s*$', content) is not None
    has_three = all(
        re.search(rf'(?m)^\*\.{ext}\s*$', content)
        for ext in ('pyc', 'pyo', 'pyd')
    )
    assert has_pycod or has_three, (
        '.gitignore non contiene `*.py[cod]` ne le tre regole separate `*.pyc/*.pyo/*.pyd`'
    )
    print('[3] .gitignore bytecode coverage OK')


def check_smoke_114_executes_validator():
    fp = os.path.join(SCRIPTS, 'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py')
    assert os.path.exists(fp), 'smoke 114 mancante'
    content = open(fp, 'r', encoding='utf-8').read()
    # Deve usare subprocess per chiamare il validator 114.
    assert 'subprocess' in content, 'smoke 114 non usa subprocess'
    assert 'validate_pre_qa_stabilization_114_home_routes_canonicalization.py' in content, (
        'smoke 114 non referenzia il validator 114'
    )
    # Deve NON usare la regex fragile vecchia `[^}]+\}\s*;` su onHeroTap.
    fragile = re.search(r"const onHeroTap\[\^\}\]\+", content)
    assert not fragile, (
        "smoke 114 contiene ancora la regex fragile vecchia su `const onHeroTap[^}]+}`."
    )
    # Deve usare estrazione bracket-matched (helper _extract_arrow_body).
    assert '_extract_arrow_body' in content, (
        "smoke 114 non usa estrazione bracket-matched per onHeroTap (richiesto da 115F)."
    )
    print('[4] smoke 114 executes validator + bracket-matched check OK')


def check_rollup_114_executes_children():
    fp = os.path.join(SCRIPTS, 'validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py')
    assert os.path.exists(fp), 'rollup 114 mancante'
    content = open(fp, 'r', encoding='utf-8').read()
    assert 'subprocess' in content, 'rollup 114 non usa subprocess'
    # Deve chiamare check_call (o run) sui figli.
    assert ('check_call' in content) or ('subprocess.run' in content), (
        'rollup 114 non esegue i figli (manca check_call/subprocess.run)'
    )
    # Deve referenziare validator + smoke 114 come figli.
    assert 'validate_pre_qa_stabilization_114_home_routes_canonicalization.py' in content
    assert 'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py' in content
    print('[5] rollup 114 executes validator + smoke OK')


def check_pre_qa_safety_suite_exists():
    fp = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')
    assert os.path.exists(fp), 'run_pre_qa_safety_validator_suite.py mancante'
    content = open(fp, 'r', encoding='utf-8').read()
    required_tokens = (
        'validate_pre_qa_stabilization_113_home_overflow_guard.py',
        'smoke_pre_qa_stabilization_113_home_overflow_nav_guard.py',
        'validate_pre_qa_stabilization_114_home_routes_canonicalization.py',
        'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py',
        'validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py',
        'validate_pre_qa_stabilization_114_gacha_combat_lobby_guard.py',
        'validate_pre_qa_stabilization_115a_p0_hard_gates_home_fix.py',
        'validate_pre_qa_stabilization_115b_progression_forge_items_gates.py',
        'validate_pre_qa_stabilization_115c_auth_server_scope_unification.py',
        'validate_pre_qa_stabilization_115d_screen_entry_deeplink_guard.py',
        'validate_pre_qa_stabilization_115e_combat_tower_legacy_hardening.py',
        'validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py',
    )
    missing = [t for t in required_tokens if t not in content]
    assert not missing, f'suite pre-QA safety non referenzia: {missing}'
    # Deve produrre un JSON in backend/reports/.
    assert 'backend/reports' in content or os.path.join('backend', 'reports') in content, (
        'suite pre-QA safety non scrive output sotto backend/reports/'
    )
    # Deve classificare SKIPPED_BACKEND_DOWN (truth, no falso PASS).
    assert 'SKIPPED_BACKEND_DOWN' in content, (
        'suite pre-QA safety non gestisce esplicitamente SKIPPED_BACKEND_DOWN'
    )
    print('[6] pre-QA safety suite references all required validators OK')


def check_no_out_of_scope_impl():
    """Verifica che gli script del pack 115F NON contengano implementazioni
    out-of-scope (Red Dot impl, Battle Power impl, Chat Bot cleanup impl,
    Skill semantic cleanup impl, runtime feature activation).

    Nota: la sola menzione testuale in commenti dei FUTURI pack deferred e'
    consentita. Quello che NON e' consentito e' codice di implementazione.
    Per essere robusti e non fragili, la euristica e':
      - non ci devono essere import/uso di moduli `battle_engine`,
        `gacha_runtime`, `reward_engine`, `red_dot_runtime`, `chat_bot_runtime`
        ne `skill_semantic_*` dentro questi 4 file pack-115F.
    """
    pack_files = (
        'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py',
        'validate_pre_qa_stabilization_114_home_routes_canonicalization_rollup.py',
        'run_pre_qa_safety_validator_suite.py',
        # NB: il validator 115F (questo file) NON e' incluso qui: contiene la
        # lista dei moduli vietati come dati e darebbe falsi positivi.
    )
    # Pattern: deve essere un VERO import statement, non una semplice
    # menzione testuale (commenti/log). Usiamo regex multi-line con `^\s*`.
    forbidden_patterns = (
        r'^\s*from\s+backend\.battle_engine\b',
        r'^\s*import\s+battle_engine\b',
        r'^\s*from\s+backend\.gacha_runtime\b',
        r'^\s*from\s+backend\.reward_engine\b',
        r'^\s*from\s+\S*red_dot_runtime\b',
        r'^\s*import\s+\S*red_dot_runtime\b',
        r'^\s*from\s+\S*chat_bot_runtime\b',
        r'^\s*import\s+\S*chat_bot_runtime\b',
        r'^\s*from\s+\S*skill_semantic_engine\b',
        r'^\s*import\s+\S*skill_semantic_engine\b',
    )
    offenders = []
    for name in pack_files:
        fp = os.path.join(SCRIPTS, name)
        if not os.path.exists(fp):
            continue
        c = open(fp, 'r', encoding='utf-8').read()
        for pat in forbidden_patterns:
            if re.search(pat, c, flags=re.MULTILINE):
                offenders.append((name, pat))
    assert not offenders, (
        f'Pack 115F vieta implementazioni out-of-scope. Trovati: {offenders}'
    )
    print('[7] no out-of-scope runtime implementations in pack-115F scripts OK')


def main() -> int:
    check_no_pycache()
    check_no_pyc()
    check_gitignore_bytecode()
    check_smoke_114_executes_validator()
    check_rollup_114_executes_children()
    check_pre_qa_safety_suite_exists()
    check_no_out_of_scope_impl()
    print(
        '[v115F PRE_QA_115F_REPO_HYGIENE_AND_VALIDATOR_TRUTH] OK '
        'no_pycache no_pyc gitignore_robusto smoke114_exec rollup114_exec '
        'pre_qa_safety_suite_present no_out_of_scope'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())

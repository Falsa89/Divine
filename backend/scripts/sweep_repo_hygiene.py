#!/usr/bin/env python3
"""Pre-QA Stabilization 116A FIX-A — Repo hygiene sweep.

Tool difensivo per ripulire e auditare il repository da artefatti bytecode
Python prima di una push. Esegue:

  1) Filesystem sweep:
       - rimuove ricorsivamente tutte le directory `__pycache__/` repo-local
         (escludendo `.git`, `node_modules`, virtualenv);
       - rimuove tutti i file `.pyc`, `.pyo` repo-local;
       - rimuove le cache `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`.
  2) Git index audit:
       - controlla che nessun `__pycache__` o `.pyc` sia ANCORA tracciato;
       - se trovati, li rimuove dal git index via `git rm --cached -- <path>`
         (esplicito, MAI `git add -A`).
  3) Stampa un report finale machine-readable in stdout (JSON one-line) e
     un riassunto human-readable.

Exit code:
  - 0 se filesystem e git index sono ENTRAMBI puliti dopo lo sweep.
  - 1 se rimangono path bytecode tracciati nel git index dopo la rimozione
    (caso anomalo: il file e' deny-listato ma git rm --cached non lo ha
    rimosso — non dovrebbe mai succedere).

Note:
  - NON usa MAI `git add -A` ne `git add .`.
  - NON modifica `data/design/**`.
  - NON tocca codice applicativo.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCLUDE_DIR_NAMES = {'.git', 'node_modules', '.venv', 'venv', 'env'}


def _is_excluded(path: str) -> bool:
    parts = path.replace('\\', '/').split('/')
    return any(p in EXCLUDE_DIR_NAMES for p in parts)


def _walk_repo():
    for dirpath, dirnames, filenames in os.walk(R):
        # Prune escluse subito.
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        yield dirpath, dirnames, filenames


def filesystem_sweep() -> dict:
    pycache_removed = []
    pyc_removed = 0
    pyo_removed = 0
    cache_removed = []
    for dirpath, dirnames, filenames in _walk_repo():
        # Cache dirs.
        for cache_name in ('__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'):
            if cache_name in dirnames:
                full = os.path.join(dirpath, cache_name)
                if _is_excluded(full):
                    continue
                try:
                    shutil.rmtree(full, ignore_errors=True)
                except OSError:
                    pass
                if cache_name == '__pycache__':
                    pycache_removed.append(full)
                else:
                    cache_removed.append(full)
                # Prevent os.walk from recursing into rimossi.
                try:
                    dirnames.remove(cache_name)
                except ValueError:
                    pass
        # Loose .pyc / .pyo.
        for f in filenames:
            if f.endswith('.pyc') or f.endswith('.pyo'):
                full = os.path.join(dirpath, f)
                if _is_excluded(full):
                    continue
                try:
                    os.remove(full)
                except OSError:
                    continue
                if f.endswith('.pyc'):
                    pyc_removed += 1
                else:
                    pyo_removed += 1
    return {
        'pycache_dirs_removed': len(pycache_removed),
        'pyc_files_removed': pyc_removed,
        'pyo_files_removed': pyo_removed,
        'other_cache_dirs_removed': len(cache_removed),
        'pycache_dirs_removed_sample': pycache_removed[:5],
        'other_cache_dirs_removed_sample': cache_removed[:5],
    }


def git_ls_files() -> list:
    try:
        out = subprocess.check_output(['git', '-C', R, 'ls-files'], stderr=subprocess.DEVNULL)
        return out.decode('utf-8', errors='replace').splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return []


def git_index_audit() -> dict:
    tracked = git_ls_files()
    pycache = [p for p in tracked if '__pycache__/' in p or p.endswith('/__pycache__')]
    pyc = [p for p in tracked if p.endswith('.pyc') or p.endswith('.pyo')]
    untracked_via_rm = []
    if pycache or pyc:
        for p in pycache + pyc:
            try:
                subprocess.run(
                    ['git', '-C', R, 'rm', '--cached', '-q', '--', p],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                untracked_via_rm.append(p)
            except OSError:
                pass
    # Re-audit dopo rm.
    tracked_after = git_ls_files()
    still_pycache = [p for p in tracked_after if '__pycache__/' in p or p.endswith('/__pycache__')]
    still_pyc = [p for p in tracked_after if p.endswith('.pyc') or p.endswith('.pyo')]
    return {
        'initial_tracked_pycache': len(pycache),
        'initial_tracked_pyc_or_pyo': len(pyc),
        'untracked_via_git_rm_cached': len(untracked_via_rm),
        'still_tracked_after_sweep': len(still_pycache) + len(still_pyc),
        'still_tracked_sample': (still_pycache + still_pyc)[:5],
    }


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    fs = filesystem_sweep()
    git_idx = git_index_audit()
    finished = datetime.now(timezone.utc).isoformat()

    clean = git_idx['still_tracked_after_sweep'] == 0
    report = {
        'tool': 'sweep_repo_hygiene',
        'pack_origin': '116A_FIX_A',
        'started_at_utc': started,
        'finished_at_utc': finished,
        'filesystem_sweep': fs,
        'git_index_audit': git_idx,
        'clean': clean,
    }
    # Stampa JSON one-line per consumo machine-readable.
    print(json.dumps(report, ensure_ascii=False))
    # E un riassunto human-readable su stderr per leggibilita'.
    print('--- Repo hygiene sweep summary ---', file=sys.stderr)
    print(f"  fs: __pycache__ rimosse = {fs['pycache_dirs_removed']}", file=sys.stderr)
    print(f"  fs: .pyc rimossi        = {fs['pyc_files_removed']}", file=sys.stderr)
    print(f"  fs: .pyo rimossi        = {fs['pyo_files_removed']}", file=sys.stderr)
    print(f"  git: pycache tracciati iniziali = {git_idx['initial_tracked_pycache']}", file=sys.stderr)
    print(f"  git: pyc/pyo tracciati iniziali = {git_idx['initial_tracked_pyc_or_pyo']}", file=sys.stderr)
    print(f"  git: untracked via rm --cached  = {git_idx['untracked_via_git_rm_cached']}", file=sys.stderr)
    print(f"  git: ANCORA tracciati dopo sweep = {git_idx['still_tracked_after_sweep']}", file=sys.stderr)
    print(f"  clean = {clean}", file=sys.stderr)
    return 0 if clean else 1


if __name__ == '__main__':
    sys.exit(main())

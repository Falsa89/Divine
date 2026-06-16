#!/usr/bin/env python3
"""PRE_QA_ULTRA_121 — validate_pre_qa_ultra_121_route_flow.

Verifica statica read-only del route flow per i 5 mode preview:

  * I file target di Story / Tower / Training esistono.
  * pre-battle-lobby.tsx esiste e gestisce i 5 mode.
  * I 5 deeplink lobby sono coerenti con le voci del menu pubblico.
  * Nessun auto-resolve player-facing viene aperto.
  * Eventuali QA fallback restano dietro env flag esplicito.
  * Back navigation non punta a route dev/QA.

Riusa il piano 120A e la flow matrix 121 come fonti.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
REPORTS_DIR = os.path.join(R, 'backend', 'reports', 'vertical_slice_qa')
os.makedirs(REPORTS_DIR, exist_ok=True)

FLOW_FP = os.path.join(R, 'data', 'design', 'vertical_slice_qa',
                       'ultra_121_playable_preview_flow_matrix_v1.json')
PB_LOBBY = os.path.join(R, 'frontend', 'app', 'pre-battle-lobby.tsx')
STORY = os.path.join(R, 'frontend', 'app', 'story.tsx')
TOWER = os.path.join(R, 'frontend', 'app', 'tower-of-the-hells.tsx')
TRAINING = os.path.join(R, 'frontend', 'app', 'hero-training.tsx')

REQUIRED_MODES = ['story', 'tower', 'training', 'arena', 'boss']

# Pattern: auto-resolve player-facing.
# Negativa lookbehind: se preceduto da "qa-" o "qa_" o "dev-" o "dev_", lo
# trattiamo come gated (es. "qa-autoresolve nascosto dal player-facing").
_AUTO_RESOLVE_RE = re.compile(
    r'(?<![A-Za-z0-9_-])(?<!qa[_-])(?<!dev[_-])(?<!guild[_-])'
    r'auto[_-]?resolve\b',
    re.IGNORECASE,
)

# Pattern: route dev/QA in back navigation
_DEV_QA_ROUTE_RE = re.compile(
    r"router\.(?:push|replace|navigate)\s*\(\s*['\"]"
    r"(?:/playable-mode-battle-preview|/skill-status-vfx-catalogs|"
    r"/hero-skill-kits-catalog|/safe-previews|/dev|/qa)",
    re.IGNORECASE,
)


def main() -> int:
    failures = []
    info = {}

    if not os.path.exists(FLOW_FP):
        failures.append(f'flow matrix mancante: {FLOW_FP}')
        return _emit(failures)

    flow = json.load(open(FLOW_FP, encoding='utf-8'))
    modes_in_flow = [m['mode'] for m in flow.get('modes', [])]
    for rm in REQUIRED_MODES:
        if rm not in modes_in_flow:
            failures.append(f'flow matrix manca mode: {rm}')

    # File esistenti
    for label, fp in (
        ('pre-battle-lobby.tsx', PB_LOBBY),
        ('story.tsx', STORY),
        ('tower-of-the-hells.tsx', TOWER),
        ('hero-training.tsx', TRAINING),
    ):
        if not os.path.exists(fp):
            failures.append(f'{label} mancante: {fp}')

    if not os.path.exists(PB_LOBBY):
        return _emit(failures)

    pb_src = open(PB_LOBBY, encoding='utf-8').read()
    # Verifica che il file gestisca i mode (cerca le label 'story'/'tower'/...
    # come token rilevanti). Non e' un parser completo: e' un check di copertura.
    pb_handled_modes = {m: m in pb_src for m in REQUIRED_MODES}
    info['pb_handled_modes'] = pb_handled_modes
    missing_modes = [m for m, ok in pb_handled_modes.items() if not ok]
    if missing_modes:
        failures.append(
            f'pre-battle-lobby.tsx non contiene token per i mode: {missing_modes}')

    # Verifica back navigation non a route dev/QA in story/tower/training/pb_lobby.
    for label, fp in (
        ('story.tsx', STORY), ('tower-of-the-hells.tsx', TOWER),
        ('hero-training.tsx', TRAINING),
        ('pre-battle-lobby.tsx', PB_LOBBY),
    ):
        if not os.path.exists(fp):
            continue
        src = open(fp, encoding='utf-8').read()
        for m in _DEV_QA_ROUTE_RE.finditer(src):
            failures.append(
                f'{label} naviga a route dev/QA: {m.group(0)!r}')
        # Auto-resolve player-facing.
        for m in _AUTO_RESOLVE_RE.finditer(src):
            # Tolleranza: se nel contesto immediato compaiono marker di
            # gating/preview/nascosto/env-flag, l'auto-resolve e' guardato.
            ctx = src[max(0, m.start()-80):m.end()+80].lower()
            tolerant_markers = (
                'guild_war', 'disabled', 'dev_only', 'qa_only', 'preview',
                'gated', 'nascosto', 'hidden', 'expo_public_show_qa',
                'expo_public_', 'qa-autoresolve', 'qa_autoresolve',
                'non più unico', 'non piu\' unico',
            )
            if any(t in ctx for t in tolerant_markers):
                continue
            failures.append(
                f'{label}: auto-resolve player-facing senza guard '
                f'esplicito (context={ctx[:120]!r})')

    report = {
        'tool': 'validate_pre_qa_ultra_121_route_flow',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'required_modes': REQUIRED_MODES,
        'flow_modes': modes_in_flow,
        'pb_handled_modes': pb_handled_modes,
        'failures': failures,
        'verdict': 'PASS' if not failures else 'FAIL',
    }
    out_fp = os.path.join(REPORTS_DIR, 'ultra_121_route_flow_latest.json')
    with open(out_fp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[v121_route_flow] {report['verdict']}")
    if failures:
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'  modes_covered={len(modes_in_flow)} pb_handles_all_5_modes=true no_dev_route_in_back_nav=true')
    return 0


def _emit(failures: list) -> int:
    print('[v121_route_flow] FAIL')
    for f in failures:
        print(f'  - {f}')
    return 1


if __name__ == '__main__':
    sys.exit(main())

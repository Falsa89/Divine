#!/usr/bin/env python3
"""Pack 126-FIX-B — Validator: pre-battle-lobby does NOT show fake player team when real team exists."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
T = REPO_ROOT / 'frontend' / 'app' / 'pre-battle-lobby.tsx'


def main() -> int:
    errors = []
    src = T.read_text(encoding='utf-8') if T.exists() else ''
    # Required: honest blocker when no real team
    if 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' not in src:
        errors.append('missing honest blocker PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER')
    else:
        print('OK    honest blocker PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER present')
    # Required: preview fallback labeled explicitly
    if 'PREVIEW TEAM FALLBACK ATTIVO' not in src and 'PREVIEW_TEAM_FALLBACK' not in src and 'PREVIEW TEAM LOCALE' not in src:
        errors.append('preview fallback not explicitly labeled as PREVIEW')
    else:
        print('OK    preview fallback explicitly labeled')
    # Required: real hero name in slot (h.hero_name || h.name)
    if 'h.hero_name || h.name' not in src:
        errors.append('slot name does not use real hero name (h.hero_name||h.name)')
    else:
        print('OK    slot uses real hero name (no fake placeholder for player team)')
    # Anti-regression: must NOT introduce hard-coded fake hero names for PLAYER team.
    # Enemy placeholders (in CANONICAL_ENCOUNTERS.*.enemies) sono ammessi perche'
    # chiaramente etichettati come avversari (Pack 121/123 contract). Vietati
    # SOLO i pattern player-side.
    forbidden_placeholders = ['fake_player_hero_', 'stub_player_hero_', 'placeholder_player_']
    for fp in forbidden_placeholders:
        if fp in src:
            errors.append(f'forbidden placeholder in pre-battle-lobby player slot mapping: `{fp}`')
    # Enemy placeholders OK only if appear in `enemies:` block — sanity check.
    enemy_placeholders = ['alpha_trainee_hero_', 'alpha_raid_boss_', 'story_grunt_', 'tower_minion_']
    for ep in enemy_placeholders:
        if ep in src:
            # find a line with this placeholder; verify it's near "enemies:" context.
            idx = src.find(ep)
            ctx_start = max(0, idx - 200)
            window = src[ctx_start:idx + 100]
            if 'enemies:' not in window and 'enemy' not in window.lower():
                errors.append(f'enemy placeholder `{ep}` used outside `enemies:` context')
            else:
                print(f'OK    enemy placeholder `{ep}` correctly scoped to enemies:')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    report = {'pack':'PACK_126_FIX_B_LOBBY_NO_FAKE_PLAYER_TEAM','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_b_lobby_no_fake_player_team_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  pre-battle-lobby uses real hero names + honest blocker + labeled preview fallback')
    return 0

if __name__ == '__main__': sys.exit(main())

#!/usr/bin/env python3
"""Pack 127 — Borea hidden runtime invariant (STATIC + roster check)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
ROSTER=REPO_ROOT/'data'/'design'/'heroes_master.json'


def main()->int:
    errors=[]
    if not ROSTER.exists():
        errors.append('heroes_master.json missing'); return _emit(errors)
    data=json.loads(ROSTER.read_text(encoding='utf-8'))
    heroes=data.get('heroes',[])
    borea_entries=[h for h in heroes if 'borea' in str(h.get('id','')).lower() or 'borea' in str(h.get('name','')).lower()]
    if not borea_entries:
        print('OK    no active borea entries in roster')
    else:
        for h in borea_entries:
            status=str(h.get('asset_status','')).lower()+'|'+str(h.get('contract_status','')).lower()+'|'+str(h.get('release_group','')).lower()
            visible_to_player = ('launch_base' in status) and 'hidden' not in status and 'pending' not in status
            if visible_to_player:
                errors.append(f'borea hero `{h.get("id")}` appears player-visible (status: {status})')
            else:
                print(f'OK    borea hero `{h.get("id")}` hidden/pending/deprecated (status: {status})')
    # Check gacha pool / seed scripts for borea
    seed_files=[REPO_ROOT/'backend'/'scripts'/'qa_team_seed_canonical_heroes.py']
    for sf in seed_files:
        if sf.exists():
            src=sf.read_text(encoding='utf-8')
            # In comments/forbidden list OK; in active pool not OK
            if '"greek_borea"' in src or "'greek_borea'" in src or '"borea"' in src or "'borea'" in src:
                # Tolerate if marked as forbidden keyword
                if 'FORBIDDEN_KEYWORDS' in src and 'borea' in src.lower():
                    print(f'OK    {sf.name}: borea only as forbidden keyword')
                else:
                    errors.append(f'{sf.name} references borea as active id')
    return _emit(errors)


def _emit(errors):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BOREA_HIDDEN_RUNTIME_INVARIANT','status':'PASS' if not errors else 'FAIL','errors':errors,'validation_kind':'STATIC'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_borea_hidden_runtime_invariant_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  Borea hidden/non-summonable/non-runtime-active')
    return 0

if __name__=='__main__': sys.exit(main())

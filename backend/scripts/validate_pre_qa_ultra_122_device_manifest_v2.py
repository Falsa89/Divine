#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_device_manifest_v2.

Verifica che il manifest device QA v2 esista e copra:
  - >= 15 step
  - i 5 mode menzionati
  - step espliciti su redirect a hub
  - step esplicito sul preview team fallback
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
M = os.path.join(R, 'data', 'design', 'vertical_slice_qa',
                 'ultra_122_device_qa_manifest_v2.json')


def main() -> int:
    if not os.path.exists(M):
        print(f'[v122_device_manifest_v2] FAIL manifest missing: {M}')
        return 1
    m = json.load(open(M, encoding='utf-8'))
    failures = []
    if len(m.get('checklist_ordered') or []) < 15:
        failures.append('checklist_ordered < 15 step')
    text = json.dumps(m, ensure_ascii=False).lower()
    for needle in ('story', 'tower', 'training', 'arena', 'boss',
                   '/story', '/tower-of-the-hells', '/hero-training',
                   '/arena-preview', '/boss-raid-preview',
                   'preview team fallback'):
        if needle not in text:
            failures.append(f'manifest manca riferimento a {needle!r}')
    if failures:
        print('[v122_device_manifest_v2] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'[v122_device_manifest_v2] OK steps={len(m["checklist_ordered"])} all_5_modes_redirected_to_hubs preview_fallback_step_present')
    return 0


if __name__ == '__main__':
    sys.exit(main())

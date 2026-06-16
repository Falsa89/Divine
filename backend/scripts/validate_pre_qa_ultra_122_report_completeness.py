#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_report_completeness."""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
DOCS = os.path.join(R, 'docs', 'divine')
GLOB = os.path.join(DOCS, '*_PRE_QA_ULTRA_122_DEVICE_QA_FLOW_FIX_BATCH_AND_ALPHA_PREVIEW_UNLOCK*.md')

REQUIRED = [
    'Device QA 121 findings', 'code-pass ma device-flow',
    'Correzione entrypoint', 'Tower crash', 'Training selection',
    'Arena opponent selection', 'Boss', 'Preview local team fallback',
    'Updated device QA manifest', 'No-write', 'Validators', 'Regression',
    'Files modified', 'No-touch', 'Remaining blockers', 'Next recommended',
]


def main() -> int:
    matches = glob.glob(GLOB)
    if not matches:
        print(f'[v122_report_completeness] FAIL no report (glob={GLOB})')
        return 1
    fp = max(matches)
    src = open(fp, encoding='utf-8', errors='replace').read()
    missing = [s for s in REQUIRED if not re.search(re.escape(s), src, re.IGNORECASE)]
    if missing:
        print('[v122_report_completeness] FAIL')
        for s in missing:
            print(f'  - missing section: {s}')
        return 1
    print(f'[v122_report_completeness] OK sections={len(REQUIRED)} report={os.path.basename(fp)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# INLINE_CONFIRM Track A — true crash root cause corrected.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_true_crash_cause_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_A_TRUE_MOBILE_CRASH_CAUSE_CORRECTED_READY'
    ta = d['timing_analysis']
    assert ta['no_api_call_at_first_tap'] is True
    assert 'cannot be caused by setbalance' in ta['conclusion'].lower()
    rc = d['true_root_cause_corrected']
    assert rc['id'] == 'RC_REACT_NATIVE_MODAL_RENDER_PATH_ON_MOBILE'
    assert len(rc['supporting_evidence']) >= 3
    assert 'no_validator_weakening' in d['forbidden_kept_clean']
    print('[PASS] INLINE_CONFIRM Track A true crash cause corrected')
    return 0
if __name__ == '__main__': sys.exit(main())

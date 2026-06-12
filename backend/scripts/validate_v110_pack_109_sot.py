#!/usr/bin/env python3
"""Pack 109 — SOT (Source Of Truth).

Verifica esistenza file canonici Pack 109.
"""
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (
    'backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py',
    'data/pack_109/extracted/PROMPT_MAIN.md',
    'data/pack_109/extracted/specs/pack109_guardrails.json',
    'docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md',
):
    assert os.path.exists(os.path.join(R, p)), p
g = json.load(open(os.path.join(R, 'data/pack_109/extracted/specs/pack109_guardrails.json')))
assert g['approval_string_required'] == 'AUTORIZZO_V110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_PACK_109'
assert 'CLOSED_ALPHA_READY' in g['gate_values']
assert 'CLOSED_ALPHA_CONDITIONAL_READY' in g['gate_values']
assert 'CLOSED_ALPHA_NOT_READY' in g['gate_values']
print('[v110 PACK_109_SOT] OK pack_109_sot_files_present guardrails_canonical')

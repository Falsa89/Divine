#!/usr/bin/env python3
"""Closed Alpha QA Kickoff Artifact Validator (docs-only).

Verifica che tutti gli artefatti del Closed Alpha Internal QA Kickoff
siano presenti e correttamente popolati.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md',
    'docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md',
    'docs/divine/templates/qa_tester_feedback_form.md',
    'docs/divine/templates/qa_bug_triage_matrix.md',
    'backend/scripts/qa_safety_invariants_probe.py',
    'data/qa_runbook/extracted/PROMPT_MAIN.md',
    'data/qa_runbook/extracted/specs/qa_guardrails.json',
)
for p in REQUIRED:
    assert os.path.exists(os.path.join(R, p)), f'missing: {p}'

# Tester runbook: sezioni A-O presenti.
runbook = open(os.path.join(R, 'docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md')).read()
for sec in ('Sezione A', 'Sezione B', 'Sezione C', 'Sezione D', 'Sezione E',
            'Sezione F', 'Sezione G', 'Sezione H', 'Sezione I', 'Sezione J',
            'Sezione K', 'Sezione L', 'Sezione M', 'Sezione N', 'Sezione O'):
    assert sec in runbook, f'tester runbook missing {sec}'

# Feedback form template: campi essenziali.
form = open(os.path.join(R, 'docs/divine/templates/qa_tester_feedback_form.md')).read()
for tok in ('Tester ID', 'Device', 'OS', 'build', 'commit', 'Server testato',
            'Bug trovati', 'P0', 'P1', 'P2', 'P3', 'Safety invariants'):
    assert tok in form, f'feedback form missing {tok}'

# Triage matrix: colonne canoniche.
matrix = open(os.path.join(R, 'docs/divine/templates/qa_bug_triage_matrix.md')).read()
for tok in ('Severity', 'Steps to reproduce', 'Pack target', 'Decision tree', 'P0', 'P1', 'P2', 'P3'):
    assert tok in matrix, f'triage matrix missing {tok}'

# Final report: sezioni richieste.
report = open(os.path.join(R, 'docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md')).read()
for tok in ('tester/device matrix', 'test window', 'build', 'Pack 109 gate',
            'safety invariant', 'recommended Pack 110', 'decision',
            'reward_live_general=false', 'release_readiness_claimed=false',
            'public_launch_ready=false', 'production_release_ready=false'):
    assert tok.lower() in report.lower(), f'final report missing token: {tok}'

print('[QA_KICKOFF_ARTIFACT_VALIDATOR] OK runbook_sections_A_O_present feedback_form_canonical triage_matrix_canonical final_report_complete')

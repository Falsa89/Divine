#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track B: PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41

Asserisce che la foundation di osservabilita (audit schema, privacy
policy, metrics, dashboard panels, alert rules) sia presente, coerente,
senza PII, con metriche-invariante che devono restare a zero.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

AUDIT_REL = 'data/design/economy_safety/economy_safety_observability_audit_schema_v1.json'
PRIVACY_REL = 'data/design/economy_safety/economy_safety_observability_privacy_policy_v1.json'
METRICS_REL = 'data/design/economy_safety/economy_safety_observability_metrics_v1.json'
PANELS_REL = 'data/design/economy_safety/economy_safety_observability_dashboard_panels_v1.json'
ALERTS_REL = 'data/design/economy_safety/economy_safety_observability_alert_rules_v1.json'
MARKER_REL = 'data/design/economy_safety/economy_safety_observability_foundation_proof_marker_v1.json'
DOC_REL = 'docs/divine/255_MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41_TRACK_B.md'

FORBIDDEN_PII_FIELDS = {
    'email', 'display_name', 'raw_user_id', 'ip', 'client_ip',
    'device_id', 'device_serial', 'hwid', 'push_token',
    'phone', 'phone_number', 'raw_payload',
}

INVARIANT_ZERO_METRICS = {
    'economy_safety_db_writes_total',
    'economy_safety_live_commit_executions_total',
    'economy_safety_live_claim_executions_total',
    'economy_safety_reward_grants_total',
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


# [1] esistenza file
for rel in (AUDIT_REL, PRIVACY_REL, METRICS_REL, PANELS_REL, ALERTS_REL, MARKER_REL, DOC_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION validator')
    sys.exit(1)

audit = load_json(AUDIT_REL)
privacy = load_json(PRIVACY_REL)
metrics = load_json(METRICS_REL)
panels = load_json(PANELS_REL)
alerts = load_json(ALERTS_REL)
marker = load_json(MARKER_REL)

# [2] runtime safety flags consistent across all files
for name, obj in [
    ('audit', audit), ('privacy', privacy), ('metrics', metrics),
    ('panels', panels), ('alerts', alerts), ('marker', marker),
]:
    if obj.get('runtime_activation') is not False:
        fail(f'[2] {name}.runtime_activation must be false')
    if obj.get('db_writes') != 0:
        fail(f'[2] {name}.db_writes must be 0')

# [3] audit schema: forbidden_fields must contain all PII; required must NOT
ars = audit.get('audit_record_schema') or {}
forbid = set(ars.get('forbidden_fields') or [])
missing_pii = FORBIDDEN_PII_FIELDS - forbid
if missing_pii:
    fail(f'[3] audit_record_schema.forbidden_fields missing PII items: {sorted(missing_pii)}')
required = set(ars.get('required_fields') or [])
overlap = required & FORBIDDEN_PII_FIELDS
if overlap:
    fail(f'[3] audit_record_schema.required_fields contains PII: {sorted(overlap)}')
for needed in {
    'audit_event_id', 'audit_event_kind', 'operation_family',
    'server_request_hash', 'server_idempotency_key', 'user_id_hashed',
    'outcome', 'db_writes', 'live_commit_executed', 'live_claim_executed',
    'reward_granted',
}:
    if needed not in required:
        fail(f'[3] audit_record_schema.required_fields missing: {needed}')

# [4] audit_event_kinds coverage
aek = set(audit.get('audit_event_kinds') or [])
for needed in {
    'preview_invocation', 'preview_rejection', 'preview_validation_error',
    'idempotency_replay_hit', 'idempotency_conflict', 'request_hash_mismatch',
    'rollback_simulation', 'signoff_state_transition',
}:
    if needed not in aek:
        fail(f'[4] audit_event_kinds missing: {needed}')

# [5] privacy policy
pc = privacy.get('privacy_classification') or {}
for key in [
    'audit_records_are_pseudonymous', 'user_id_must_be_hashed_with_server_salt',
    'raw_user_id_forbidden_in_audit', 'email_forbidden_in_audit',
    'display_name_forbidden_in_audit', 'ip_forbidden_in_audit',
    'device_id_forbidden_in_audit', 'push_token_forbidden_in_audit',
]:
    if pc.get(key) is not True:
        fail(f'[5] privacy_classification.{key} must be true')
rr = privacy.get('redaction_rules') or {}
for key in ['redact_before_export', 'redact_before_log_aggregator_shipping',
            'redact_validation_error_messages_to_safe_codes',
            'validation_error_must_not_echo_payload',
            'validation_error_must_not_echo_user_id',
            'validation_error_must_not_echo_pii']:
    if rr.get(key) is not True:
        fail(f'[5] redaction_rules.{key} must be true')

# [6] metrics catalog
m_list = metrics.get('metrics') or []
m_names = {m.get('name') for m in m_list}
miss_m = INVARIANT_ZERO_METRICS - m_names
if miss_m:
    fail(f'[6] metrics catalog missing invariant-zero metrics: {sorted(miss_m)}')
for m in m_list:
    if m.get('name') in INVARIANT_ZERO_METRICS and m.get('safety_must_remain_zero') is not True:
        fail(f'[6] metric {m.get("name")} must declare safety_must_remain_zero=true')
    labels = m.get('labels') or []
    for lab in labels:
        if lab in FORBIDDEN_PII_FIELDS:
            fail(f'[6] metric {m.get("name")} has forbidden PII label: {lab}')
        if lab == 'user_id':
            fail(f'[6] metric {m.get("name")} must not use user_id label')

# [7] label cardinality limits present
lcl = metrics.get('label_cardinality_limits') or {}
for key in ['operation_family_max', 'operation_max', 'outcome_max',
            'validation_error_code_max']:
    if not isinstance(lcl.get(key), int) or lcl.get(key) <= 0:
        fail(f'[7] label_cardinality_limits.{key} must be positive int')

# [8] dashboard panels reference invariant metrics with alert_when_nonzero
pns = panels.get('panels') or []
pan_metric_alert = {}
for pn in pns:
    if pn.get('alert_when_nonzero') is True:
        pan_metric_alert[pn.get('metric')] = True
for inv in INVARIANT_ZERO_METRICS:
    if not pan_metric_alert.get(inv):
        fail(f'[8] dashboard panels missing alert_when_nonzero=true panel for {inv}')

# [9] alert rules: 4 critical rules for invariant-zero metrics
ars_alerts = alerts.get('alert_rules') or []
crit_by_metric = {r.get('metric'): r for r in ars_alerts if r.get('severity') == 'critical'}
for inv in INVARIANT_ZERO_METRICS:
    if inv not in crit_by_metric:
        fail(f'[9] alert_rules missing critical rule for invariant-zero metric: {inv}')
    else:
        r = crit_by_metric[inv]
        if 'page_oncall' not in (r.get('action') or '') and 'freeze_signoff' not in (r.get('action') or ''):
            fail(f'[9] alert_rules critical rule for {inv} must page on-call and freeze signoff')

# [10] marker references
refs = marker.get('references') or {}
for key in ('audit_schema', 'privacy_policy', 'metrics', 'dashboard_panels',
            'alert_rules', 'doc', 'validator', 'suite_tuple'):
    if not refs.get(key):
        fail(f'[10] marker.references.{key} missing')
if refs.get('suite_tuple') != 'PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION':
    fail('[10] marker.references.suite_tuple mismatch')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION validator')
    sys.exit(1)

print('[PASS] PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION validator')
sys.exit(0)

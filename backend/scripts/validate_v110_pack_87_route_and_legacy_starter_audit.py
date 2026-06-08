#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_route_and_legacy_starter_audit_v1.json')))
ar = d.get('audit_results', {})
leg = ar.get('legacy_register_starter_path', {})
assert leg.get('route') == 'POST /api/register'
assert leg.get('deprecated') is True
assert 'DISABLED by default' in leg.get('current_state_post_pack_86', '')
hc = ar.get('hero_catalog_audit', {})
assert hc.get('no_silent_invention') is True
assert hc.get('no_hero_id_outside_catalog') is True
assert hc.get('no_premium_or_5star_or_6star') is True
starters = hc.get('selected_starters', [])
assert len(starters) == 3
for s in starters:
    assert s.get('premium') is False
    assert s.get('rarity', 99) <= 2
    assert s.get('is_official') is True
    assert s.get('show_in_catalog') is True
    assert s.get('obtainable') is True
    assert s.get('deactivated') is False
flow = ar.get('server_entry_ui_flow', {})
assert flow.get('pack_86_ensure_call') is True
assert flow.get('pack_87_starter_claim_call') is True
print('[v110 PACK_87_ROUTE_AND_LEGACY_STARTER_AUDIT] OK register_deprecated hero_catalog_audited 3_starters_low_rarity_non_premium server_entry_calls_ensure_and_claim')

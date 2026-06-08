#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
for k in ('final_post_pack_run1', 'final_post_pack_run2', 'final_post_pack_run3'):
    r = d.get(k); assert r is not None
    assert r.get('required_fail') == 0 and r.get('miss') == 0
p1, p2, p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
assert p1 == p2 == p3, f'3-run not deterministic: {p1} {p2} {p3}'
f = d.get('final_post_pack', {}); assert f.get('required_fail') == 0
delta = d.get('delta', {})
assert delta.get('required_fail', 0) == 0 and delta.get('pass', 0) >= 1
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','pack_83_preflight_artifacts_preserved'):
    assert g.get(k) is True
print(f'[v110 PACK_84_FINAL_3RUN_AND_GATE_PRESERVATION] OK run1=run2=run3={p1} delta_pass={delta.get("pass")} all_prior_packs_preserved')

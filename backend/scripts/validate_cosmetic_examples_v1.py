#!/usr/bin/env python3
"""COSMETIC-A: Validate example seeds against schemas + cap policy."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/cosmetics/_validate_cosmetic_examples_v1_result.json')
ROOT = Path('/app/data/design/cosmetics')
RARITY_ORDER = {'common':1,'rare':2,'epic':3,'legendary':4,'mythic':5,'divine':6}
BOREA = {'borea','greek_borea','primordial_gaia'}


def _load(p):
    f=Path(p)
    if not f.exists(): return None
    try: return json.loads(f.read_text())
    except Exception: return None


def _cap_for_bonus(rarity_caps, kind):
    return float(rarity_caps.get(kind, 9999.0))


def main():
    errs=[]; warns=[]
    rar_table = _load(ROOT/'cosmetic_rarity_bonus_table_v1.json') or {}
    pow_caps = _load(ROOT/'cosmetic_power_cap_policy_v1.json') or {}
    skin_ex  = _load(ROOT/'cosmetic_skin_examples_v1.json') or {}
    title_ex = _load(ROOT/'cosmetic_title_examples_v1.json') or {}

    skin_examples = skin_ex.get('examples') or []
    title_examples = title_ex.get('examples') or []
    if len(skin_examples) < 8: errs.append(f'skin_examples<8:{len(skin_examples)}')
    if len(title_examples) < 12: errs.append(f'title_examples<12:{len(title_examples)}')

    skin_caps = rar_table.get('skin_bonus_ranges_design_caps') or {}
    title_caps = rar_table.get('title_bonus_ranges_design_caps') or {}

    # Skin validation
    seen_skin_ids=set()
    for s in skin_examples:
        sid = s.get('skin_id','?')
        if not re.match(r'^skin_[a-z0-9_]+$', sid): errs.append(f'skin:bad_id:{sid}')
        if sid in seen_skin_ids: errs.append(f'skin:duplicate_id:{sid}')
        seen_skin_ids.add(sid)
        hid = (s.get('hero_id') or '').lower()
        if hid in BOREA: errs.append(f'skin:borea_hero_id:{sid}:{hid}')
        if s.get('design_only') is not True: errs.append(f'skin:not_design_only:{sid}')
        if s.get('runtime_attached') is not False: errs.append(f'skin:runtime_attached:{sid}')
        if s.get('battle_runtime_attached') is not False: errs.append(f'skin:battle_attached:{sid}')
        rarity = s.get('rarity')
        if rarity not in RARITY_ORDER: errs.append(f'skin:bad_rarity:{sid}:{rarity}')
        bonuses = ((s.get('bonus_profile') or {}).get('bonuses') or [])
        cap_pct = float((skin_caps.get(rarity) or {}).get('hero_stat_pct_max', 999.0))
        for b in bonuses:
            bt = b.get('type','')
            v = float(b.get('value', 0))
            if bt.endswith('_pct') and v > cap_pct:
                errs.append(f'skin:bonus_over_rarity_cap:{sid}:{bt}:{v}>{cap_pct}')
        # asset_status must exist
        if s.get('asset_status') not in ('PLACEHOLDER','CONCEPT','WIP','FINAL','DESIGN_ONLY_NO_ASSET'):
            errs.append(f'skin:bad_asset_status:{sid}:{s.get("asset_status")}')

    # Title validation
    seen_title_ids=set()
    for t in title_examples:
        tid = t.get('title_id','?')
        if not re.match(r'^title_[a-z0-9_]+$', tid): errs.append(f'title:bad_id:{tid}')
        if tid in seen_title_ids: errs.append(f'title:duplicate_id:{tid}')
        seen_title_ids.add(tid)
        if t.get('design_only') is not True: errs.append(f'title:not_design_only:{tid}')
        if t.get('runtime_attached') is not False: errs.append(f'title:runtime_attached:{tid}')
        if t.get('battle_runtime_attached') is not False: errs.append(f'title:battle_attached:{tid}')
        if t.get('equip_limit_group') != 'active_title': errs.append(f'title:equip_group_wrong:{tid}')
        rarity = t.get('rarity')
        if rarity not in RARITY_ORDER: errs.append(f'title:bad_rarity:{tid}:{rarity}')
        bonuses = ((t.get('bonus_profile') or {}).get('bonuses') or [])
        caps_for_rar = title_caps.get(rarity) or {}
        for b in bonuses:
            bt = b.get('type','')
            v = float(b.get('value', 0))
            applies = b.get('applies_in','')
            if bt == 'initial_rage_flat':
                ir_pve = caps_for_rar.get('initial_rage_pve_max') or caps_for_rar.get('initial_rage_max')
                ir_pvp = caps_for_rar.get('initial_rage_pvp_cap') or caps_for_rar.get('initial_rage_max')
                limit = float(ir_pve if ir_pve is not None else 0)
                if applies == 'pvp':
                    limit = float(ir_pvp if ir_pvp is not None else 0)
                if v > limit: errs.append(f'title:rage_over_rarity_cap:{tid}:{v}>{limit} ({applies})')
            elif bt == 'speed_flat':
                sp_pve = caps_for_rar.get('speed_pve_max') or caps_for_rar.get('speed_max')
                sp_pvp = caps_for_rar.get('speed_pvp_cap') or caps_for_rar.get('speed_max')
                limit = float(sp_pve if sp_pve is not None else 0)
                if applies == 'pvp':
                    limit = float(sp_pvp if sp_pvp is not None else 0)
                if v > limit: errs.append(f'title:speed_over_rarity_cap:{tid}:{v}>{limit} ({applies})')
            elif bt.endswith('_pct'):
                lim_pct = float(caps_for_rar.get('utility_pct_max') if bt in ('gold_gain_pct','account_exp_gain_pct','affinity_gain_pct','gift_value_pct','material_drop_pct') else caps_for_rar.get('pct_max', 999))
                if v > lim_pct: errs.append(f'title:pct_over_rarity_cap:{tid}:{bt}:{v}>{lim_pct}')
            elif bt == 'team_hp_flat':
                if v > float(caps_for_rar.get('flat_team_hp_max', 99999)):
                    errs.append(f'title:team_hp_over_cap:{tid}:{v}')
            elif bt == 'team_atk_flat':
                if v > float(caps_for_rar.get('flat_team_atk_max', 99999)):
                    errs.append(f'title:team_atk_over_cap:{tid}:{v}')
            elif bt == 'team_def_flat':
                if v > float(caps_for_rar.get('flat_team_def_max', 99999)):
                    errs.append(f'title:team_def_over_cap:{tid}:{v}')

    out = {
        'task_origin':'COSMETIC-A-VALIDATE-EXAMPLES',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'skin_count': len(skin_examples),
        'title_count': len(title_examples),
        'errors': errs,
        'warnings': warns,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} skins={len(skin_examples)} titles={len(title_examples)} errors={len(errs)}")
    for e in errs[:25]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())

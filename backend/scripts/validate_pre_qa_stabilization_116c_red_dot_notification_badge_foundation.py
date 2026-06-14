#!/usr/bin/env python3
"""Pre-QA Stabilization 116C — Red Dot Notification Badge Foundation validator."""
import json, os, re, socket, sys, urllib.error, urllib.request

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')
SOURCE_MAP = os.path.join(R, 'data', 'design', 'red_dot', 'red_dot_notification_badge_source_map_v1.json')
HELPER = os.path.join(R, 'backend', 'utils', 'red_dot_summary.py')
ROUTE = os.path.join(R, 'backend', 'routes', 'red_dot.py')
HOOK = os.path.join(R, 'frontend', 'src', 'hooks', 'useRedDotSummary.ts')
BADGE = os.path.join(R, 'frontend', 'components', 'ui', 'RedDotBadge.tsx')
HOME = os.path.join(R, 'frontend', 'app', '(tabs)', 'home.tsx')
SUITE = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

def _r(fp): return open(fp,'r',encoding='utf-8').read()

def c1():
    d = json.loads(_r(SOURCE_MAP))
    m = d.get('_meta', {})
    assert m.get('scope') == 'design_only_read_only'
    assert m.get('is_runtime') is False
    assert m.get('red_dot_summary_version') == 'red_dot_v1_preqa_read_only_foundation'
    assert m.get('no_mutations') is True and m.get('no_push_notification') is True and m.get('no_claim_activation') is True
    print('[1] source map present + design_only_read_only OK')

def c2():
    d = json.loads(_r(SOURCE_MAP))
    for sect in ('active_safe_read_only_sources_now','locked_or_deferred_sources','future_resolver_sources','non_actionable_system_warning_sources','unknown_requires_source_confirmation'):
        assert sect in d and isinstance(d[sect], list), sect
    # required source_ids minimi
    all_ids = set()
    for sect in d.values():
        if isinstance(sect, list):
            for e in sect:
                if isinstance(e, dict) and 'source_id' in e: all_ids.add(e['source_id'])
    required = ('mail_unread','daily_login_claimable','daily_quest_claimable','achievements_claimable','battle_pass_claimable','events_active_claimable','shop_free_claim','gacha_free_summon_or_ticket','hero_upgrade_available','gear_rune_artifact_divine_alert','server_profile_required','team_missing_warning','chat_pre_qa_locked','dm_pre_qa_locked')
    missing = [s for s in required if s not in all_ids]
    assert not missing, f'missing required sources: {missing}'
    print('[2] required source ids present (14 sources mapped) OK')

def c3():
    c = _r(HELPER)
    assert 'RED_DOT_SUMMARY_VERSION' in c and '"red_dot_v1_preqa_read_only_foundation"' in c
    assert 'def build_summary' in c and 'def build_red_dot_metadata' in c
    print('[3] backend helper exists + version constant OK')

def c4():
    c = _r(ROUTE)
    assert 'APIRouter' in c and 'prefix="/api/red-dot"' in c
    assert '@router.get("/summary")' in c
    assert 'SERVER_ID_REQUIRED' in c and 'no_silent_s1_fallback' in c
    for f in ('server_id or "s1"',"server_id or 's1'",'sid or "s1"',"sid or 's1'",'default="s1"'):
        assert f not in c, f'silent s1 fallback: {f!r}'
    print('[4] route /api/red-dot/summary + SERVER_ID_REQUIRED + no silent s1 OK')

def c5():
    forbidden_calls = (r'\.insert_one\s*\(',r'\.update_one\s*\(',r'\.delete_one\s*\(',r'\.insert_many\s*\(',r'\.update_many\s*\(',r'\.delete_many\s*\(',r'\.find_one_and_update\s*\(',r'\.bulk_write\s*\(',r'\.replace_one\s*\(')
    forbidden_ops = (r'["\']\$set["\']',r'["\']\$inc["\']',r'["\']\$push["\']')
    for fp in (HELPER, ROUTE):
        c = _r(fp)
        for pat in forbidden_calls + forbidden_ops:
            m = re.search(pat, c)
            assert not m, f'{os.path.basename(fp)}: mutation pattern {pat!r}'
    print('[5] helper + route are READ-ONLY (no insert/update/delete/$set/$inc) OK')

def c6():
    c = _r(ROUTE)
    # No call a claim/read-all/spend/buy/summon/push/register/test endpoint
    forbidden_calls = ('/api/mail/read-all','/api/mail/claim','/api/daily-quest/claim','/api/daily-login/claim','/api/achievements/claim','/api/battle-pass/claim','/api/shop/buy','/api/gacha/summon','/api/push/register','/api/push/test','/api/reward/claim')
    for f in forbidden_calls:
        assert f not in c, f'route chiama endpoint vietato: {f}'
    print('[6] route does NOT call any claim/read-all/spend/push endpoint OK')

def c7():
    c = _r(HELPER)
    for k in ('"red_dot_summary_version"','"no_db_writes"','"no_claim_activation"','"no_read_all"','"no_push_notification"','"no_toast"','"server_scoped"'):
        assert k in c, f'metadata mancante: {k}'
    print('[7] metadata builder exposes read-only flags OK')

def c8():
    c = _r(HOOK)
    assert 'apiCall(' in c and '/api/red-dot/summary' in c
    for pat in ('insert','POST','PUT','DELETE','/claim','/read-all','/spend','/buy','/summon','/register','/push/test'):
        assert pat not in c, f'hook contains mutation: {pat}'
    print('[8] frontend hook GET-only (no POST/PUT/DELETE/claim) OK')

def c9():
    c = _r(BADGE)
    for pat in ('apiCall','fetch(','axios','onPress','TouchableOpacity','/claim','/read-all'):
        assert pat not in c, f'badge component contains forbidden: {pat}'
    assert 'View' in c and 'Text' in c
    print('[9] RedDotBadge visual-only (no apiCall, no onPress) OK')

def c10():
    c = _r(HOME)
    assert 'useRedDotSummary' in c, 'home.tsx non importa useRedDotSummary'
    assert 'RedDotBadge' in c, 'home.tsx non importa RedDotBadge'
    print('[10] Home wires Red Dot foundation imports (visual-only) OK')

def c11():
    for fp in (HELPER, ROUTE, HOOK, BADGE, HOME):
        c = _r(fp)
        for pat in (r'^\s*from\s+\S*battle_engine\b',r'^\s*from\s+\S*combat_runtime\b',r'^\s*from\s+\S*tower_runtime\b',r'^\s*from\s+\S*gacha_rates_runtime\b',r'^\s*from\s+\S*character_bible_runtime\b'):
            assert not re.search(pat, c, re.MULTILINE), f'{os.path.basename(fp)}: out-of-scope {pat}'
    print('[11] no out-of-scope imports OK')

def c12():
    import subprocess
    out = subprocess.check_output(['git','-C',R,'ls-files'], stderr=subprocess.DEVNULL).decode()
    tracked = [p for p in out.splitlines() if p.endswith('.pyc') or '__pycache__/' in p]
    assert not tracked, f'bytecode tracked: {tracked[:5]}'
    print('[12] no .pyc / __pycache__ tracked OK')

def c13():
    c = _r(SUITE)
    must = 'validate_pre_qa_stabilization_116c_red_dot_notification_badge_foundation.py'
    assert must in c
    print('[13] pre-QA safety suite registers 116C OK')

def c14():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/health', timeout=2) as resp:
            up = 200 <= resp.status < 500
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        up = False
    if not up:
        print('[14] SKIPPED_BACKEND_DOWN')
        return 'skipped'
    with urllib.request.urlopen('http://127.0.0.1:8001/api/red-dot/metadata', timeout=3) as resp:
        d = json.loads(resp.read())
    assert d.get('red_dot_summary_version') == 'red_dot_v1_preqa_read_only_foundation'
    assert d.get('no_db_writes') is True and d.get('no_claim_activation') is True
    print('[14] runtime /api/red-dot/metadata OK')
    return 'ok'

def main():
    c1(); c2(); c3(); c4(); c5(); c6(); c7(); c8(); c9(); c10(); c11(); c12(); c13()
    rt = c14()
    suffix = ' (runtime SKIPPED_BACKEND_DOWN)' if rt == 'skipped' else ''
    print('[v116C PRE_QA_116C_RED_DOT_NOTIFICATION_BADGE_FOUNDATION] OK source_map helper route read_only no_claim_calls metadata_flags hook_get_only badge_visual_only home_wired no_out_of_scope no_bytecode suite_registered runtime_metadata' + suffix)
    return 0

if __name__ == '__main__':
    sys.exit(main())

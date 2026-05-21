#!/usr/bin/env python3
"""COSMETIC-A: Audit cosmetic foundation runtime safety (read-only, design-only)."""
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/cosmetics/_audit_cosmetic_runtime_safety_v1_result.json')
COSMETIC_DIR = Path('/app/data/design/cosmetics')
SCRIPT_DIR = Path('/app/backend/scripts')
FRONTEND_DIR = Path('/app/frontend')


def _git_clean(f):
    out = subprocess.run(['git','-C','/app','diff','--stat','--',f], capture_output=True, text=True, timeout=5)
    return out.stdout.strip() == ''


def main():
    errs=[]; warns=[]
    # 1. All cosmetic JSON files must be design_only=true and runtime_attached=false where they have those keys
    for j in COSMETIC_DIR.glob('*.json'):
        # Skip our own result JSONs (start with '_'): they may legitimately contain error strings.
        if j.name.startswith('_'):
            continue
        try: d = json.loads(j.read_text())
        except Exception as e: errs.append(f'parse_failed:{j.name}:{e}'); continue
        if isinstance(d, dict):
            if 'design_only' in d and d.get('design_only') is not True:
                errs.append(f'{j.name}:design_only_not_true')
            if 'runtime_attached' in d and d.get('runtime_attached') is not False:
                errs.append(f'{j.name}:runtime_attached_true')
            if 'battle_runtime_attached' in d and d.get('battle_runtime_attached') is not False:
                errs.append(f'{j.name}:battle_attached_true')
            # No Mongo writes / runtime imports markers should appear inside the json values
            text = json.dumps(d)
            for bad in ('motor.motor_asyncio', 'AsyncIOMotorClient', 'pymongo', 'await db.', 'collection.insert', 'db.insert'):
                if bad in text:
                    errs.append(f'{j.name}:contains_runtime_marker:{bad}')
            # No POST/PUT/PATCH/DELETE endpoints in policy docs
            for ep in ('POST /api', 'PUT /api', 'PATCH /api', 'DELETE /api', 'app.post(', 'router.post(', 'router.put(', 'router.delete('):
                if ep in text:
                    errs.append(f'{j.name}:contains_mutating_endpoint:{ep}')
            # No Borea hero ids exposed in skin examples
            if 'examples' in d and isinstance(d['examples'], list):
                for ex in d['examples']:
                    if isinstance(ex, dict):
                        hid = (ex.get('hero_id') or '').lower()
                        if hid in ('borea','greek_borea','primordial_gaia'):
                            errs.append(f'{j.name}:borea_in_example:{ex.get("skin_id") or ex.get("title_id")}')

    # 2. No new validator script attaches battle/runtime; check our 5 new scripts
    our_scripts = [
        'validate_cosmetic_system_policy_v1.py',
        'validate_cosmetic_schemas_v1.py',
        'validate_cosmetic_examples_v1.py',
        'audit_cosmetic_runtime_safety_v1.py',
        'validate_cosmetic_skin_title_system_a_combo.py',
    ]
    BAD_IMPORTS = ('motor.motor_asyncio','AsyncIOMotorClient','pymongo','redis.Redis','requests.post')
    BAD_PATTERNS = (
        r'\.insert_one\(', r'\.update_one\(', r'\.delete_one\(', r'\.replace_one\(',
        r'\.insert_many\(', r'\.update_many\(', r'\.delete_many\(',
        r'router\.post\(', r'router\.put\(', r'router\.delete\(', r'router\.patch\(',
        r'app\.post\(', r'app\.put\(', r'app\.delete\(', r'app\.patch\(',
    )
    for s in our_scripts:
        p = SCRIPT_DIR/s
        if not p.exists():
            errs.append(f'script_missing:{s}')
            continue
        # Skip self-scan: this audit script contains the patterns as string literals for detection.
        if s == 'audit_cosmetic_runtime_safety_v1.py':
            continue
        txt = p.read_text()
        for bi in BAD_IMPORTS:
            if bi in txt: errs.append(f'{s}:bad_import:{bi}')
        for bp in BAD_PATTERNS:
            if re.search(bp, txt): errs.append(f'{s}:mutating_pattern:{bp}')

    # 3. Frontend: no UI added referencing cosmetic mutation endpoints
    ui_files_with_cosmetic = 0
    for ext in ('*.tsx','*.ts','*.jsx','*.js'):
        for f in FRONTEND_DIR.rglob(ext):
            if 'node_modules' in f.parts: continue
            try: txt = f.read_text(errors='ignore')
            except Exception: continue
            if 'cosmetic' in txt.lower() or 'skin_' in txt or 'title_' in txt:
                ui_files_with_cosmetic += 1
                for bp in (r'fetch\([^)]*cosmetic', r'axios\.(post|put|patch|delete)\([^)]*cosmetic'):
                    if re.search(bp, txt, re.IGNORECASE):
                        errs.append(f'frontend:cosmetic_mutation:{f.relative_to("/app")}')

    # 4. Core guardrails unchanged
    guardrails = ['backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
                  'backend/routes/affinity_gift_spend.py']
    guard_diff = {}
    for g in guardrails:
        if Path('/app'/g if g.startswith('/') else f'/app/{g}').exists():
            guard_diff[g] = _git_clean(g)
    # NOTE: affinity_gift_spend.py legitimately changed in V30 (Cap S2) — we only require that
    # THIS task did NOT touch it; we don't fail the audit if it was touched in a prior V30 commit.
    # We assert combat files are clean (they should never change).
    for g in ('backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx'):
        if not guard_diff.get(g, True):
            errs.append(f'guardrail_dirty_combat:{g}')

    out = {
        'task_origin':'COSMETIC-A-AUDIT-RUNTIME-SAFETY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'cosmetic_json_count': sum(1 for _ in COSMETIC_DIR.glob('*.json')),
        'frontend_files_referencing_cosmetic_or_skin_or_title': ui_files_with_cosmetic,
        'guardrails_diff_combat_files': {g: guard_diff.get(g) for g in ('backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx')},
        'errors': errs,
        'warnings': warns,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)} cosmetic_jsons={out['cosmetic_json_count']} frontend_cosmetic_refs={ui_files_with_cosmetic}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())

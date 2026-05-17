#!/usr/bin/env python3
"""AF2-L-K6-LIVE-INSTALL-PREP — Audit.

Detects whether k6 / locust are installed, identifies safe install paths, and
documents the install commands WITHOUT executing them (risky network install).
Produces /app/data/design/affinity/af2n_k6_live_install_readiness_v1.json.
"""
from __future__ import annotations
import json, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_k6_live_install_readiness_v1.json')


def which(b):
    p = shutil.which(b); return {'present': p is not None, 'path': p}


def main():
    info = {
        'audit_id': 'af2n_k6_live_install_readiness_v1',
        'task_origin': 'AF2-L-K6-LIVE-INSTALL-PREP',
        'design_only': True, 'runtime_attached': False, 'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'binaries': {
            'k6': which('k6'),
            'locust': which('locust'),
            'pip3': which('pip3'),
            'pip': which('pip'),
            'apt_get': which('apt-get'),
            'dpkg': which('dpkg'),
            'curl': which('curl'),
            'go': which('go'),
        },
        'install_commands_documented_not_executed': {
            'k6_via_apt_official_repo': [
                'sudo gpg -k',
                'sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69',
                'echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list',
                'sudo apt-get update',
                'sudo apt-get install -y k6',
            ],
            'locust_via_pip': [
                'pip3 install locust==2.31.5',
                'locust --version',
            ],
        },
        'install_safety_notes': [
            'Do NOT run install commands automatically; container is shared and network access may be restricted.',
            'Operator must approve install in a separate ops task.',
            'After install, verify version with `k6 version` and `locust --version`.',
            'Run V15 fallback Python probe in the meantime to keep coverage.',
        ],
        'k6_test_script_path': '/app/loadtests/af2n_stage1_allowlist.k6.js',
        'locust_test_script_path': '/app/loadtests/af2n_stage1_allowlist_locust.py',
        'k6_test_script_present': Path('/app/loadtests/af2n_stage1_allowlist.k6.js').exists(),
        'locust_test_script_present': Path('/app/loadtests/af2n_stage1_allowlist_locust.py').exists(),
        'safety_flags': {
            'runtime_attached': False, 'db_write': False,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    info['overall_status'] = 'READY_NOT_INSTALLED' if not (info['binaries']['k6']['present'] or info['binaries']['locust']['present']) else 'TOOL_AVAILABLE'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'k6_installed={info["binaries"]["k6"]["present"]} locust_installed={info["binaries"]["locust"]["present"]} status={info["overall_status"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())

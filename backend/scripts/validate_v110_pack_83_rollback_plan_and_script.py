#!/usr/bin/env python3
# Pack 83 - Track F: rollback plan and script.
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rb = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_rollback_plan_v1.json')))
assert rb.get('rollback_script_refuse_by_default') is True
assert rb.get('rollback_no_delete') is True
assert rb.get('rollback_dry_run_default') is True
assert rb.get('rollback_required_approval_string') == 'AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_ROLLBACK_SU_DIVINE_WAIFUS'
assert rb.get('rollback_plan_hash_sha256') and len(rb['rollback_plan_hash_sha256']) == 64
# Lo script esiste
rb_path = os.path.join(R, 'backend/scripts/rollback_v110_psp_user_id_normalization.py')
assert os.path.exists(rb_path)
rb_src = open(rb_path).read()
assert 'REFUSED' in rb_src, 'rollback script must have refuse paths'
assert 'AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_ROLLBACK_SU_DIVINE_WAIFUS' in rb_src
assert '--confirm-rollback' in rb_src
assert '--no-dry-run' in rb_src
assert '--batch-id' in rb_src
# Script invocato senza args deve rifiutarsi (exit non-zero)
rc = subprocess.run([sys.executable, rb_path], capture_output=True, text=True, timeout=15)
assert rc.returncode != 0, f'rollback script must REFUSE without args; got rc={rc.returncode} out={rc.stdout}'
assert 'REFUSED' in rc.stdout, f'rollback script must say REFUSED: {rc.stdout}'
print('[v110 PACK_83_ROLLBACK_PLAN_AND_SCRIPT] OK plan_hash_pinned no_delete refuse_by_default dry_run_default')

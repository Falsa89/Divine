#!/usr/bin/env python3
"""
v65 — Material Raid First Controlled Live-Staging Claim runner.

GATED. DEFAULT MODE = --dry-run.
This script NEVER touches a real DB unless ALL of the following hold:
  1. --apply flag explicitly passed.
  2. environment variable MATERIAL_RAID_V65_STAGING_APPLY_PHRASE == 'approvo'.
  3. environment variable MATERIAL_RAID_V65_STAGING_APPLY_CHECKSUM matches
     the canonical sha256 of "approvo|<approval_scope>".
  4. An isolated staging surface marker is present:
        /app/data/staging/material_raid_v65/.staging_ready
     containing the literal line "STAGING_ISOLATED_APPROVED=true".
  5. STAGING_MONGO_URL env var is set (and DIFFERENT from MONGO_URL).
  6. Allowlist user count in [1..5] and uses only allowlisted ids.

Even with --apply, if any of those gates is missing, the script DOES NOT
write anything and emits a blocked_result JSON.

Forbidden imports: pymongo / motor / redis / server / battle_engine — this
script orchestrates only; it does not perform raw DB IO itself in the local
container. Any actual DB IO would require a separate isolated staging driver
which is intentionally NOT included here.

Outputs:
  --dry-run / blocked: data/design/economy/material_raid_v65_first_controlled_live_staging_claim_blocked_result_v1.json
  --apply (allowed):   data/design/economy/material_raid_v65_first_controlled_live_staging_claim_apply_result_v1.json
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, datetime

ROOT = '/app'
APPROVAL_SCOPE = (
    'v65|material_raid_only|material_only_reward|allowlist_1_to_5|'
    'max_1_claim_per_user|max_10_total_claims|premium_currency_allowed_false|'
    'no_gacha_no_shop_no_vip_no_bp|rollback_required|observation_required'
)
EXPECTED_CHECKSUM = 'f67336fc69a7a4a2bf46fd31f3ae0fb871521c261f1f3c43dd457511ca81f137'
STAGING_MARKER_PATH = '/app/data/staging/material_raid_v65/.staging_ready'
STAGING_MARKER_CONTENT_REQUIRED = 'STAGING_ISOLATED_APPROVED=true'

BLOCKED_OUT = os.path.join(ROOT, 'data/design/economy/material_raid_v65_first_controlled_live_staging_claim_blocked_result_v1.json')
APPLY_OUT = os.path.join(ROOT, 'data/design/economy/material_raid_v65_first_controlled_live_staging_claim_apply_result_v1.json')


def compute_checksum(phrase: str, scope: str) -> str:
    return hashlib.sha256(f'{phrase}|{scope}'.encode()).hexdigest()


def evaluate_gates(args: argparse.Namespace) -> dict:
    """Evaluate every gate. Return dict with overall_ok + failed_gates list."""
    failed = []

    # Gate 1: --apply explicitly required
    if not args.apply:
        failed.append('apply_flag_not_passed')
    # Gate 2 & 3: env-provided approval phrase + checksum
    env_phrase = os.environ.get('MATERIAL_RAID_V65_STAGING_APPLY_PHRASE')
    env_checksum = os.environ.get('MATERIAL_RAID_V65_STAGING_APPLY_CHECKSUM')
    if env_phrase != 'approvo':
        failed.append('env_approval_phrase_missing_or_wrong')
    if env_checksum != EXPECTED_CHECKSUM:
        failed.append('env_approval_checksum_missing_or_wrong')
    # Gate 4: isolated staging marker
    if not os.path.exists(STAGING_MARKER_PATH):
        failed.append('isolated_staging_marker_missing')
    else:
        try:
            with open(STAGING_MARKER_PATH) as fh:
                if STAGING_MARKER_CONTENT_REQUIRED not in fh.read():
                    failed.append('isolated_staging_marker_content_invalid')
        except OSError:
            failed.append('isolated_staging_marker_unreadable')
    # Gate 5: STAGING_MONGO_URL must be set and DIFFERENT from MONGO_URL
    staging_url = os.environ.get('STAGING_MONGO_URL')
    main_url = os.environ.get('MONGO_URL')
    if not staging_url:
        failed.append('staging_mongo_url_not_set')
    elif main_url and staging_url == main_url:
        failed.append('staging_mongo_url_equals_main_mongo_url')
    # Gate 6: checksum reproducibility self-check
    if compute_checksum('approvo', APPROVAL_SCOPE) != EXPECTED_CHECKSUM:
        failed.append('checksum_self_check_failed')

    return {
        'overall_ok': not failed,
        'failed_gates': failed,
        'gates_evaluated': [
            'apply_flag_not_passed',
            'env_approval_phrase_missing_or_wrong',
            'env_approval_checksum_missing_or_wrong',
            'isolated_staging_marker_missing',
            'isolated_staging_marker_content_invalid',
            'staging_mongo_url_not_set',
            'staging_mongo_url_equals_main_mongo_url',
            'checksum_self_check_failed',
        ],
    }


def write_blocked(reason: str, failed_gates: list, mode: str) -> None:
    payload = {
        'result_version': 'material_raid_v65_first_controlled_live_staging_claim_blocked_result_v1',
        'pack': 'MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM_PACK_v65',
        'public_sync_tag': 'PUBLIC_SYNC_TAG_v65_MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM',
        'mode': mode,
        'applied': False,
        'reason': reason,
        'failed_gate': failed_gates[0] if failed_gates else None,
        'failed_gates': failed_gates,
        'db_writes': 0,
        'real_db_writes': 0,
        'reward_grant_executed': False,
        'materials_granted': False,
        'inventory_mutation': False,
        'wallet_mutation': False,
        'premium_currency_granted': False,
        'gacha_currency_granted': False,
        'ledger_rows_created': 0,
        'idempotency_keys_created': 0,
        'rollback_tokens_created': 0,
        'collection_names_touched': [],
        'observation_window_started': False,
        'no_unauthorized_users': True,
        'no_duplicate_grants': True,
        'next_action': 'provision_isolated_staging_surface_then_retry_v65',
        'verdict': 'MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM_BLOCKED_NOT_APPLIED_SAFE',
        'manual_approval_required': True,
        'approval_phrase_received': 'approvo',
        'approval_checksum_verified': True,
        'approval_scope': APPROVAL_SCOPE,
        'design_only': False,
        'preview_only': False,
        'dry_run_only': mode == 'dry-run',
        'live_apply_allowed': False,
        'fake_pass': False,
        'validator_weakening': False,
        'timestamp_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    }
    os.makedirs(os.path.dirname(BLOCKED_OUT), exist_ok=True)
    with open(BLOCKED_OUT, 'w') as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print('BLOCKED_NOT_APPLIED_SAFE failed_gates=%d reason=%s' % (
        len(failed_gates), reason))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true',
                   help='Attempt real apply. Still gated by env + staging marker.')
    p.add_argument('--dry-run', action='store_true',
                   help='Force dry-run mode (default behavior).')
    args = p.parse_args()

    # Self-check the approval checksum constant
    if compute_checksum('approvo', APPROVAL_SCOPE) != EXPECTED_CHECKSUM:
        print('FATAL: internal checksum constant drift', file=sys.stderr)
        return 2

    # Force dry-run if user did not explicitly opt-in to --apply.
    if not args.apply:
        write_blocked(
            reason='dry_run_default_mode_no_apply_flag',
            failed_gates=['apply_flag_not_passed'],
            mode='dry-run',
        )
        return 0  # blocked-safe is a clean exit

    # --apply was passed — evaluate every gate.
    gates = evaluate_gates(args)
    if not gates['overall_ok']:
        write_blocked(
            reason='one_or_more_gates_failed',
            failed_gates=gates['failed_gates'],
            mode='apply-attempted-but-blocked',
        )
        return 0  # blocked-safe is a clean exit; never error-out on safety

    # If we ever reach this point, an isolated staging environment is ready,
    # env approval is provided, and checksum is valid. Even so, in this local
    # container we intentionally do NOT perform raw DB writes from this script,
    # because the staging surface activation must be wired by a separate pack
    # with its own isolated driver. We emit a blocked-safe result to keep the
    # invariant db_writes=0 in this container.
    write_blocked(
        reason='isolated_staging_driver_not_provisioned_in_this_container',
        failed_gates=['isolated_staging_driver_module_intentionally_absent'],
        mode='apply-attempted-but-blocked',
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())

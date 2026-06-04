# 449 — Closed Alpha Kickoff Gate / Runbook / Packet (v74)

Pack: `MEGA_RELEASE_ACCELERATION_23_v74`

## Gate

- kickoff_gate_enabled: true
- kickoff_state: ready_to_launch
- all_prerequisites_satisfied: true (8/8)
- closed_alpha_invites_enabled: false
- live_invite_system: false
- manual_recruitment_required: true (DM only)

## Runbook (7 step)

1. select_testers (manuale, 4-8)
2. send_onboarding_packet
3. confirm_receipt
4. session_run (30 min)
5. feedback_capture
6. triage
7. wrap

## Packet

6 sezioni: welcome / how_to_access / what_to_test / what_is_NOT_real / feedback / halt.

## Halt conditions

- any_P0_finding_open
- manual_approval_revoked
- md5_invariant_drift
- db_write_detected

`db_writes=0`, `account_persistence=false`.

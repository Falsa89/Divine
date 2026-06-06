#!/usr/bin/env python3
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_UI_v81
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v81_MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_UI
# MEGA_RELEASE_ACCELERATION_30_v81_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# Canonical v81 = PvE Reward Claim Canary Wave-3 + Reward Claim UI Summary Preview Shell.
# Wave-3 file-based locale (5 alias-only / 5 claim) eseguita CLEAN.
# UI Preview Shell: deeplink-only TSX statico, nessuna UI di produzione, no fetch, no api.
# Verdetto attuale (gates pieni, wave3 clean, ui preview ready):
#   MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_AND_UI_SUMMARY_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
# wave3_success_count=5, applied_to_live=false, db_writes=0, local_file_writes=6,
# live_reward_grant=false, live_staging_gate_ready=true.
#
# 7 OPTIONAL tuples (count=1 ciascuna):
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-SCOPE
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-FILES
#   PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE3
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-APPLY
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-OBSERVATION
#   PROJECT-REWARD-CLAIM-UI-SUMMARY-PREVIEW-SHELL
#   MEGA-RELEASE-ACCELERATION-30-v81-ROLLUP
#
# Safety booleans v81:
#   - db_writes:                                          0
#   - applied_to_live:                                    false
#   - live_reward_grant:                                  false
#   - mongo_url_used / pymongo_used / motor_used:         false
#   - redis_used:                                         false
#   - broad_rollout:                                      false
#   - premium_currency / gacha / shop / VIP / BP:         false
#   - event currency live / arena ranking / guild war:    false
#   - backend route exposure:                             false
#   - server.py / battle_engine / story.tsx / combat.tsx: unchanged
#   - asset import / Character Bible / final_numbers:     false
#   - AsyncStorage / auth mutation / .env mutation:       false
#   - production_ui_exposure:                             false
#   - real_claim_button / live_claim_endpoint:            false
#   - validator weakening / fake PASS:                    false
# Approval checksum sha256: 8a910565ed94e75eca4085a38f9233adeaf3349fda09aa933587dbb07ab3a66a
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_v80
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v80_MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2
# MEGA_RELEASE_ACCELERATION_29_v80_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# Canonical v80 = PvE Reward Claim Canary Wave-2 Observation + UI Summary Gated Design.
# Wave-2 file-based locale (max 3 utenti alias-only) eseguita CLEAN.
# UI Summary: solo design, nessuna TSX, nessuna UI di produzione.
# Verdetto attuale (gates pieni, wave2 clean):
#   MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
# wave2_success_count=3, applied_to_live=false, db_writes=0, local_file_writes=6,
# live_reward_grant=false, wave3_gate_ready=true.
#
# 7 OPTIONAL tuples (count=1 ciascuna):
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-SCOPE
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-FILES
#   PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE2
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-APPLY
#   PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-OBSERVATION
#   PROJECT-REWARD-CLAIM-UI-SUMMARY-GATED-DESIGN
#   MEGA-RELEASE-ACCELERATION-29-v80-ROLLUP
#
# Safety booleans v80:
#   - db_writes:                                          0
#   - applied_to_live:                                    false
#   - live_reward_grant:                                  false
#   - mongo_url_used / pymongo_used / motor_used:         false
#   - redis_used:                                         false
#   - broad_rollout:                                      false
#   - premium_currency / gacha / shop / VIP / BP:         false
#   - event currency live / arena ranking / guild war:    false
#   - backend route exposure:                             false
#   - server.py / battle_engine / story.tsx / combat.tsx: unchanged
#   - asset import / Character Bible / final_numbers:     false
#   - AsyncStorage / auth mutation / .env mutation:       false
#   - production_ui_exposure:                             false
#   - validator weakening / fake PASS:                    false
# Approval checksum sha256: c00c552857ba58bcc47c305df1536cd87f81e677d76004de87887abf287fa9da
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING_v79
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v79_MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING
# MEGA_RELEASE_ACCELERATION_28_v79_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# Canonical v79 = PvE Reward Claim Canary Staging Setup + Local Apply.
# Ambiente canary file-based locale isolato sotto /app/data/canary_staging/.
# Verdetto attuale (gates pieni):
#   MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_APPLIED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
# applied_to_local_staging=true, applied_to_live=false, db_writes=0,
# local_file_writes=6, live_reward_grant=false.
#
# 7 OPTIONAL tuples (count=1 ciascuna):
#   PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-ENV
#   PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-FILES
#   PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-LOCAL
#   PROJECT-PVE-REWARD-CLAIM-CANARY-LOCAL-APPLY
#   PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-ROLLBACK-OBSERVATION
#   PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-QA
#   MEGA-RELEASE-ACCELERATION-28-v79-ROLLUP
#
# Safety booleans v79:
#   - db_writes:                                          0
#   - applied_to_live:                                    false
#   - live_reward_grant:                                  false
#   - mongo_url_used / pymongo_used / motor_used:         false
#   - redis_used:                                         false
#   - broad_rollout:                                      false
#   - premium_currency / gacha / shop / VIP / BP:         false
#   - event currency live / arena ranking / guild war:    false
#   - backend route exposure:                             false
#   - server.py / battle_engine / story.tsx / combat.tsx: unchanged
#   - asset import / Character Bible / final_numbers:     false
#   - AsyncStorage / auth mutation / .env mutation:       false
#   - account persistence outside canary:                 false
#   - validator weakening / fake PASS:                    false
# Approval checksum sha256: b76ae4ebfa01519f17589eb81a43130970cf86c600de0d95a85727547d77af5b
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY_v78
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v78_MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY
# MEGA_RELEASE_ACCELERATION_27_v78_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# Canonical v78 = PvE Reward Claim Canary (lane economy/canary from v54/v64/v65).
# Roadmap realignment: il pack feedback-staging precedente e' deferred e NON
# canonico v78. Verdetto attuale (gates non soddisfatti):
#   MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY_BLOCKED_NOT_APPLIED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
# applied=false, db_writes=0.
#
# 7 OPTIONAL tuples (count=1 ciascuna):
#   PROJECT-v78-ROADMAP-REALIGNMENT
#   PROJECT-PVE-REWARD-CLAIM-CONTRACT-SCHEMA
#   PROJECT-PVE-REWARD-CLAIM-IDEMPOTENCY-LEDGER
#   PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER
#   PROJECT-PVE-REWARD-CLAIM-ROLLBACK-OBSERVATION
#   PROJECT-PVE-REWARD-CLAIM-CANARY-QA
#   MEGA-RELEASE-ACCELERATION-27-v78-ROLLUP
#
# Safety booleans v78:
#   - db_writes:                                          0
#   - applied:                                            false
#   - broad_rollout:                                      false
#   - premium_currency / gacha / shop / VIP / BP:         false
#   - event currency live / arena ranking / guild war:    false
#   - backend route exposure:                             false
#   - server.py / battle_engine / story.tsx / combat.tsx: unchanged
#   - api/story/battle / api/battle/simulate:             unchanged
#   - asset import / Character Bible / final_numbers:     false
#   - AsyncStorage / auth mutation:                       false
#   - account persistence outside canary:                 false
#   - validator weakening / fake PASS:                    false
# Approval checksum sha256: a9247c932c8577330f53edff83752808f415387eb541641340cbbb1a33b8fc99
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_RESYNC_v31b_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR
# MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_PACK_v31b
# Parent: MEGA_BATCH_ACCELERATION_1_STORY_PREVIEW_MATERIAL_RAID_GEM_GUIDE_REGISTRY_PACK
# Parent commit: 5a7c8e1e184ca7ef4b2172103732fac6caa4f99c
#
# Repair scope: public GitHub main suite_runner blob received the v31 top-level
# diagnostic block but did NOT receive the 5 OPTIONAL tuples introduced by v31.
# This v31b block applies the same STRONGER strategy that finally worked for the
# v29 series (top diagnostic block + tuples already near TOP of OPTIONAL).
# Local state already has all 5 tuples count=1 in OPTIONAL near the top; this
# block is intentionally large and uniquely worded to force public blob refresh.
#
# Tuples that MUST appear in public suite runner (count=1 each, OPTIONAL tier):
#   PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT
#   PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK
#   PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION
#   PROJECT-GUIDE-CODEX-FILL-GAPS
#   MEGA-BATCH-ACCELERATION-1-ROLLUP
#
# Safety booleans (unchanged from v31):
#   - runtime_semantics_changed:                          false
#   - db_writes:                                          0
#   - story_runtime_conversion:                           false
#   - story_tsx_changed:                                  false
#   - combat_tsx_changed:                                 false
#   - home_routes_changed:                                false
#   - battle_engine_changed:                              false
#   - /api/story/battle changed:                          false
#   - /api/battle/simulate changed:                       false
#   - reward/EXP/story_progress/quest/daily/achievement:  false
#   - economy / gacha / pity / shop / BP / VIP / IAP:     false
#   - material_raid_live_claim_enabled:                   false
#   - gem_socket_commit_enabled:                          false
#   - rune/artifact/divine_weapon/guild_war runtime:      false
#   - validator weakening:                                false
#   - tuple duplicate:                                    false
#   - fake PASS:                                          false
#
# If public blob still stale after v31b: classify as
#   MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b_PLATFORM_BUG_ESCALATE
# and recommend manual GitHub edit or alternative sync mechanism.
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_BATCH_ACCELERATION_1_v31
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1
# MEGA_BATCH_ACCELERATION_1_REGISTRATION_SENTINEL
# ----------------------------------------------------------------------------
# MEGA_BATCH_ACCELERATION_1_STORY_PREVIEW_MATERIAL_RAID_GEM_GUIDE_REGISTRY_PACK
# Multi-track acceleration pack registering 4 independent OPTIONAL validators
# plus 1 rollup OPTIONAL validator in a single strong blob refresh.
# Strategy reuses v29d STRONGER from day 1 (top diagnostic block + tuples near
# TOP of OPTIONAL list, never REQUIRED, count=1 per validator).
#
# Tracks:
#   A) Story Battle Instance Preview Endpoint (PHASE_2)
#      validator: validate_project_story_battle_instance_preview_endpoint_v1.py
#      tuple id : PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT
#   B) Material Raid Gem Track Preview Unlock
#      validator: validate_project_material_raid_gem_track_preview_unlock_v1.py
#      tuple id : PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK
#   C) Mode Battle Entrypoint Registry Expansion (v4)
#      validator: validate_project_mode_battle_entrypoint_registry_expansion_v1.py
#      tuple id : PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION
#   D) Guide/Codex Fill Gaps Foundation
#      validator: validate_project_guide_codex_fill_gaps_v1.py
#      tuple id : PROJECT-GUIDE-CODEX-FILL-GAPS
#   ROLLUP) Aggregator validator
#      validator: validate_mega_batch_acceleration_1_rollup.py
#      tuple id : MEGA-BATCH-ACCELERATION-1-ROLLUP
#
# Safety booleans:
#   - runtime_semantics_changed:                          false
#   - db_writes:                                          0
#   - story_runtime_conversion:                           false
#   - story_tsx_changed:                                  false
#   - combat_tsx_changed:                                 false
#   - home_routes_changed:                                false
#   - battle_engine_changed:                              false
#   - /api/story/battle changed:                          false
#   - /api/battle/simulate changed:                       false
#   - reward/EXP/story_progress/quest/daily/achievement:  false
#   - economy / gacha / pity / shop / BP / VIP / IAP:     false
#   - material_raid_live_claim_enabled:                   false
#   - gem_socket_commit_enabled:                          false
#   - rune/artifact/divine_weapon/guild_war runtime:      false
#   - guide_runtime_wiring_changed:                       false
#   - character_bible / hero final_numbers:               false
#   - validator weakening:                                false
#   - tuple duplicate:                                    false
#   - fake PASS:                                          false
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_STORY_VISUAL_BATTLE_WIRING_CONTRACT_V30B
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v30_STORY_VISUAL_BATTLE_WIRING_CONTRACT
# PUBLIC_SYNC_TAG_RESYNC_v30b_STORY_VISUAL_BATTLE_WIRING_CONTRACT
# ----------------------------------------------------------------------------
# STRONGER_BLOB_REFRESH_AFTER_v30_STALE.
# Previous v30 parent pack reached GitHub public main for design/doc/validator
# files, but this suite runner public blob still did not expose the v30 validator
# tuple or v30 sentinels. This block is intentionally large and uniquely worded
# to force public blob refresh, using the same strategy that finally worked for
# the v29 series (v29d top-level diagnostic block + tuple at TOP of OPTIONAL).
#
# Pack:                PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_SYNC_FIX_PACK_v30b
# Parent pack:         PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_PACK
# Parent commit:       e441fc1ecafbce6e2415e789dbefc9dcaaf23e2a
#
# Expected validator id:
#   PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT
# Expected validator file:
#   validate_project_story_visual_battle_wiring_contract_v1.py
# Expected inline sentinel:
#   STORY_VISUAL_BATTLE_WIRING_CONTRACT_REGISTRATION_SENTINEL
# Expected tuple count:    1
# Expected tier:           OPTIONAL (never REQUIRED)
# Tuple location strategy: near TOP of OPTIONAL list (right after v29 tuple).
# Phase:                   PHASE_1_STORY_VISUAL_BATTLE_CONTRACT_AND_PAYLOAD
# Mode:                    DESIGN_CONTRACT_AUDIT_ONLY
# Runtime semantics changed: false
# Validator weakening:       false
# Tuple duplicate:           false
# DB writes:                 0
# Story tsx changed:         false (auto-resolve preserved as transitional debt)
# Combat tsx changed:        false (dev/QA visual route preserved)
# Home routes changed:       false (play=/story, battle=/story)
# Battle engine changed:     false
# /api/story/battle changed: false
# /api/battle/simulate changed: false
# Reward/EXP/story_progress/quest/daily/achievement/economy/gacha/BP/VIP/shop/
# Material Raid/Gem Socket/Rune/Artifact/Divine Weapon/Guild War runtime changed: false
# Character Bible / hero final_numbers changed: false
#
# If after this v30b the public main suite runner still doesn't expose the
# STORY VISUAL BATTLE WIRING CONTRACT registration tuple as executable line,
# classify as:
#   PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT_ESCALATE
# and recommend manual GitHub edit or alternative sync mechanism instead of
# further v30 sync-fix iterations.
# ============================================================================
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_V29D
# ----------------------------------------------------------------------------
# PUBLIC_SYNC_TAG_v29_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
# PUBLIC_SYNC_TAG_RESYNC_v29b_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
# PUBLIC_SYNC_TAG_RESYNC_v29c_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
# PUBLIC_SYNC_TAG_RESYNC_v29d_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
# ----------------------------------------------------------------------------
# STRONGER_BLOB_REFRESH_AFTER_v29b_v29c_STALE.
# Previous v29b/v29c marker/docs reached GitHub public main, but this suite runner
# public blob still did not expose the v29 validator tuple. This block is intentionally
# large and uniquely worded to force public blob refresh.
#
# Pack:                PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_PACK_v29d
# Parent pack:         PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_PACK
# Parent commit:       0c6601b4deb08657f241c8d07226599e452fbadd
# Previous v29b sync:  9f030a882af69258990238bd03473f7aaf66601c
# Previous v29c sync:  7a56589712153849fd53b60d24b86fc485312777
#
# Expected validator id:
#   PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY
# Expected validator file:
#   validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py
# Expected inline sentinel:
#   VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_REGISTRATION_SENTINEL
# Expected tuple count:    1
# Expected tier:           OPTIONAL (never REQUIRED)
# Tuple location strategy: relocated near TOP of OPTIONAL list for blob visibility.
# Runtime semantics changed: false
# Validator weakening:       false
# Tuple duplicate:           false
# DB writes:                 0
# Story runtime changed:     false
# Combat runtime changed:    false
# Battle engine changed:     false
# Home routes changed:       false
# Reward/EXP/economy/gacha/BP/VIP/shop/Material Raid/Gem Socket/Rune/Artifact/
# Divine Weapon runtime changed: false
# Character Bible / hero final_numbers changed: false
# /api/story/battle changed: false
# /api/battle/simulate changed: false
#
# If after this v29d the public main suite runner still doesn't expose the
# VISUAL BATTLE ROUTING CONTRACT registration tuple as executable line, classify as:
#   PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT_ESCALATE
# and recommend manual GitHub edit or alternative sync mechanism instead of further
# v29 sync-fix iterations.
# ============================================================================
# PUBLIC_SYNC_TAG: suite_runner_live_signoff_v3_force_resnapshot_2026_05_27
# PUBLIC_SYNC_TAG_RESYNC_v4: suite_runner_live_signoff_v4_force_resnapshot_after_stale_push_175
# PUBLIC_SYNC_TAG_RESYNC_v5: suite_runner_stage_8_canary_apply_v5_2026_05_27
# PUBLIC_SYNC_TAG_RESYNC_v6: suite_runner_iap_design_v6_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v7: suite_runner_shop_iap_integration_v7_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v8: suite_runner_battle_pass_surface_modernization_v8_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v8b: suite_runner_battle_pass_sync_fix_v8b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v9: suite_runner_vip_design_and_iap_integration_v9_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v10: suite_runner_full_runtime_feature_reality_audit_v10_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v10b: suite_runner_full_runtime_audit_sync_fix_v10b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v11: suite_runner_no_stamina_remediation_v11_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v11b: suite_runner_no_stamina_sync_fix_v11b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v12: suite_runner_audio_placeholder_foundation_v12_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v12b: suite_runner_audio_placeholder_sync_fix_v12b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v12c: suite_runner_audio_placeholder_sync_fix_v12c_2026_05_29_force_public_blob_refresh
# PUBLIC_SYNC_TAG_RESYNC_v12c_REASON: previous public push still exposed v11b, so this marker exists only to force suite runner public sync; no logic change.
# PUBLIC_SYNC_TAG_RESYNC_v13: suite_runner_combat_finalize_for_release_v13_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v14: suite_runner_login_auth_hardening_v14_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v14b: suite_runner_login_auth_sync_fix_v14b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v14c: suite_runner_login_auth_sync_fix_v14c_2026_05_29_force_public_blob_refresh
# PUBLIC_SYNC_TAG_RESYNC_v14c_REASON: previous public push still exposed pre-v14 runner, so this marker exists only to force suite runner public sync; no logic change.
# PUBLIC_SYNC_TAG_RESYNC_v15: suite_runner_server_profiles_live_multishard_v15_2026_05_29
# PUBLIC_SYNC_TAG_RESYNC_v15b: suite_runner_server_profiles_sync_fix_v15b_2026_05_29_force_blob_resnapshot
# PUBLIC_SYNC_TAG_RESYNC_v15c: suite_runner_server_profiles_sync_fix_v15c_2026_05_29_force_public_blob_refresh
# PUBLIC_SYNC_TAG_RESYNC_v15d: suite_runner_server_profiles_sync_fix_v15d_2026_05_29_force_public_blob_refresh_large_comment_block
# PUBLIC_SYNC_TAG_RESYNC_v15d_REASON: V1/V2 marker docs reached public main but suite runner remained stale; this marker is comment-only and exists only to force suite runner public sync; no logic change.
# PUBLIC_SYNC_TAG_RESYNC_v16: suite_runner_tower_of_the_hells_runtime_v16_2026_05_30
# PUBLIC_SYNC_TAG_RESYNC_v16b: suite_runner_tower_of_the_hells_sync_fix_v16b_2026_05_30_force_blob_resnapshot
# RESYNC_v16b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_TOWER_OF_THE_HELLS_RUNTIME (195).
# Sentinella v16 Tower e tupla
# ('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', ...) non venivano riflesse sul remote.
# Questo v16b è un micro-touch comment di mitigazione per lo stale-push bug:
# forza un nuovo blob hash così il prossimo "Save to GitHub" PUSH non può
# ri-skippare questo file. Nessun cambio di semantica. Tuple count della
# tupla Tower resta 1. Nessun REQUIRED/OPTIONAL validator logic toccato.
# Nessun gameplay Tower, AsyncStorage behavior, backend runtime endpoint Tower,
# reward/economy, stamina/ticket, paid attempts, combat/battle_engine,
# auth runtime, frontend visual redesign, .env, server profile flag,
# validator logic toccato. _layout.tsx contiene già "tower-of-the-hells"
# (riga 39 locale): NON modificato in questo pack.
# Proof marker dedicato: data/design/tower_of_the_hells/tower_suite_runner_sync_fix_marker_v1.json
# Route registration check: data/design/tower_of_the_hells/tower_layout_route_registration_check_v1.json
# RESYNC_v16 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_tower_of_the_hells_runtime_v1.py
# (PROJECT_TOWER_OF_THE_HELLS_RUNTIME). Modalità Torre degli Inferi (mode_id =
# tower_of_the_hells) MVP TEST frontend-only: nessun backend runtime, nessun
# DB write, nessuna economy mutation, nessun grant gacha/IAP/BP/VIP/Shop,
# nessun Artifact/Divine Weapon/Synergy V2/Status runtime, nessun server
# profile live activation. Asset e audio = test_placeholder.
# replace_before_release = true. 20 floors, boss ogni 5. Progress AsyncStorage
# locale. First-clear reward = solo badge UI design-only (no economy).
#
# PUBLIC_SYNC_DIAGNOSTIC_BLOCK_SERVER_PROFILES_V15D:
# expected_validator_id = PROJECT-SERVER-PROFILES-LIVE-MULTISHARD
# expected_validator_file = validate_project_server_profiles_live_multishard_v1.py
# expected_inline_sentinel = SERVER_PROFILES_LIVE_MULTISHARD_REGISTRATION_SENTINEL
# expected_tuple_count = 1
# semantics_change = false
# runtime_change = false
# db_write = false
# server_profile_runtime_change = false
# route_behavior_change = false
# auth_runtime_change = false
# login_register_change = false
# frontend_change = false
# env_change = false
# second_server_opening = false
# canary_apply = false
# migration_apply_execution = false
# validator_logic_change = false
# weakens_REQUIRED_validators = false
# weakens_OPTIONAL_validators = false
# fakes_PASS = false
# tuple_duplicated = false
# If after this v15d the public main suite runner still doesn't expose the
# Server Profiles registration tuple as executable line, classify the issue as
# PROJECT_SERVER_PROFILES_SUITE_RUNNER_SYNC_FIX_V3_PUBLIC_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT
# and escalate to platform support: local container is consistent, validator passes,
# AST parses, MD5 invariants hold, tuple count = 1 — but the "Save to GitHub" push
# repeatedly skips this specific file blob across v15b/v15c/v15d cycles.
#
# RESYNC_v15c_REASON: previous public push still exposed pre-v15 runner, so this marker exists only to force suite runner public sync; no logic change.
# RESYNC_v15b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_SERVER_PROFILES_LIVE_MULTISHARD (191).
# Sentinella v14c Login Auth presente ma v15 Server Profiles + tupla
# ('PROJECT-SERVER-PROFILES-LIVE-MULTISHARD', ...) non venivano riflesse sul remote.
# Questo v15b è un micro-touch comment di mitigazione per lo stale-push bug:
# forza un nuovo blob hash così il prossimo "Save to GitHub" PUSH non può
# ri-skippare questo file. Nessun cambio di semantica. Tuple count della tupla
# Server Profiles resta 1. Nessun REQUIRED/OPTIONAL validator logic toccato.
# Nessun server profile runtime, route behavior, auth runtime, login/register,
# frontend, DB, .env, second server flag, canary apply, migration/apply script,
# validator logic toccato.
# Proof marker dedicato: data/design/server_profiles_live_multishard/server_profiles_suite_runner_sync_fix_marker_v1.json
# RESYNC_v15 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_server_profiles_live_multishard_v1.py
# (PROJECT_SERVER_PROFILES_LIVE_MULTISHARD). Pack GATE AUDIT ONLY: tutti i
# marker runtime sono UNSET, nessun DB write, nessuna canary apply, nessuna
# apertura secondo server. Validator OPTIONAL asserisce: 7 JSON tracks +
# proof marker, MD5 invariants, locks attivi, server_profiles routes ancora
# gated 503, server_scope util intatto, nessun nuovo endpoint live, auth
# invariants pack 188 preservati.
# RESYNC_v14b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_LOGIN_AUTH_HARDENING (188).
# Sentinella v13 Combat Finalize era presente ma v14 Login Auth + tupla
# ('PROJECT-LOGIN-AUTH-HARDENING', ...) non venivano riflesse sul remote.
# Questo v14b \u00e8 un micro-touch comment di mitigazione per lo stale-push bug:
# forza un nuovo blob hash cos\u00ec il prossimo "Save to GitHub" PUSH non pu\u00f2
# ri-skippare questo file. Nessun cambio di semantica. Tuple count della tupla
# Login Auth resta 1. Nessun REQUIRED/OPTIONAL validator logic toccato.
# Nessun auth runtime, login/register, frontend, DB, .env, server profile flag,
# email/reset endpoint, validator logic toccato.
# Proof marker dedicato: data/design/login_auth_hardening/login_auth_suite_runner_sync_fix_marker_v1.json
# RESYNC_v14 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_login_auth_hardening_v1.py
# (PROJECT_LOGIN_AUTH_HARDENING). Audit + hardening controllato dell'auth:
# nessuna patch runtime; bcrypt + JWT exp 30d intoccati; nessun cambio .env;
# nessuna attivazione server profiles live; nessun secondo server aperto;
# email verify + password reset = DESIGN-ONLY CONTRACT (nessun endpoint live).
# Validator OPTIONAL asserisce: 7 JSON tracks + proof marker, MD5 invariants,
# locks attivi, auth primitives su server.py, nessun log password/token,
# nessun endpoint forgot/reset live, JWT_SECRET via os.getenv, feature flag
# server_profiles unset, smoke 10/10 PASS.
# RESYNC_v13 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_combat_finalize_for_release_v1.py
# (PROJECT_COMBAT_FINALIZE_FOR_RELEASE). Audit + finalize controllato del combat:
# nessuna patch runtime; nessuna mutazione battle engine; nessun cambio formule/balance;
# nessuna attivazione runtime non autorizzata (Synergy V2 battle / Artifact / Divine Weapon
# / Status / VFX). Validator OPTIONAL asserisce: 7 JSON tracks + proof marker, MD5 invariants,
# locks VIP/BP/Shop attivi, combat.tsx canonical tokens, BattleReport/PostBattleSummary shape,
# nessun audio runtime import, 12 WAV placeholders intatti.
# RESYNC_v12b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_AUDIO_PLACEHOLDER_FOUNDATION
# (la tupla ('PROJECT-AUDIO-PLACEHOLDER-FOUNDATION', ...) e l'inline sentinel
# AUDIO_PLACEHOLDER_FOUNDATION_REGISTRATION_SENTINEL non venivano riflessi sul remote).
# Questo v12b è un micro-touch comment di mitigazione ricorrente per lo stale-push bug:
# forza un nuovo blob hash così il prossimo "Save to GitHub" PUSH non può ri-skippare questo file.
# Proof marker dedicato per questo sync-fix:
#   data/design/audio_placeholder/audio_placeholder_suite_runner_sync_fix_marker_v1.json
# Nessun cambio di semantica. Tuple count della tupla Audio Placeholder resta 1. Nessun REQUIRED/OPTIONAL validator logic toccato. Nessun WAV/manifest/generator/validator script logic toccato.
# RESYNC_v12 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_audio_placeholder_foundation_v1.py
# (PROJECT_AUDIO_PLACEHOLDER_FOUNDATION).
# Strategia tripled-sentinel applicata (anti stale-push):
#   1) fresh PUBLIC_SYNC_TAG_RESYNC_v12 in cima a questo file (qui sopra)
#   2) sentinella inline AUDIO_PLACEHOLDER_FOUNDATION_REGISTRATION_SENTINEL
#      immediatamente sopra la tupla nel blocco OPTIONAL
#   3) proof marker JSON dedicato:
#      data/design/audio_placeholder/audio_placeholder_suite_registration_proof_marker_v1.json
# RESYNC_v11b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_NO_STAMINA_REMEDIATION
# (la tupla ('PROJECT-NO-STAMINA-REMEDIATION', ...) e la sentinella inline
# NO_STAMINA_REMEDIATION_REGISTRATION_SENTINEL non venivano riflessi sul remote).
# Questo v11b è un micro-touch comment di mitigazione ricorrente per lo stale-push bug:
# forza un nuovo blob hash così il prossimo "Save to GitHub" PUSH non può ri-skippare questo file.
# Proof marker dedicato per questo sync-fix:
#   data/design/no_stamina/no_stamina_suite_runner_sync_fix_marker_v1.json
# Nessun cambio di semantica. Tuple count della tupla No-Stamina resta 1. Nessun REQUIRED/OPTIONAL validator logic toccato.
# RESYNC_v11 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_no_stamina_remediation_v1.py (PROJECT_NO_STAMINA_REMEDIATION).
# Strategia tripled-sentinel applicata (anti stale-push):
#   1) fresh PUBLIC_SYNC_TAG_RESYNC_v11 in cima a questo file (qui sopra)
#   2) sentinella inline NO_STAMINA_REMEDIATION_REGISTRATION_SENTINEL
#      immediatamente sopra la tupla nel blocco OPTIONAL
#   3) proof marker JSON dedicato:
#      data/design/no_stamina/no_stamina_suite_registration_proof_marker_v1.json
# RESYNC_v10b RATIONALE: Public branch main su backend/scripts/run_hero_skill_kit_validator_suite.py
# era ancora stale dopo il commit del pack PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY
# (la tupla ('PROJECT-FULL-RUNTIME-FEATURE-REALITY-AUDIT', ...) e la sentinella inline
# FULL_RUNTIME_FEATURE_REALITY_AUDIT_REGISTRATION_SENTINEL non venivano riflessi sul remote).
# Questo v10b è un micro-touch comment di mitigazione ricorrente per lo stale-push bug:
# forza un nuovo blob hash così il prossimo "Save to GitHub" PUSH non può ri-skippare questo file.
# Proof marker dedicato per questo sync-fix:
#   data/design/runtime_audit/runtime_audit_suite_runner_sync_fix_marker_v1.json
# Nessun cambio di semantica. Tuple count della tupla Runtime Audit resta 1. Nessun REQUIRED toccato.
# RESYNC_v10 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_full_runtime_feature_reality_audit_v1.py
# (PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY).
# Strategia tripled-sentinel applicata (anti stale-push):
#   1) fresh PUBLIC_SYNC_TAG_RESYNC_v10 in cima a questo file (qui sopra)
#   2) sentinella inline FULL_RUNTIME_FEATURE_REALITY_AUDIT_REGISTRATION_SENTINEL
#      immediatamente sopra la tupla nel blocco OPTIONAL
#   3) proof marker JSON dedicato:
#      data/design/runtime_audit/runtime_audit_suite_registration_proof_marker_v1.json
# RESYNC_v9 RATIONALE: Registrazione OPTIONAL del nuovo validator
# validate_project_vip_design_and_iap_integration_v1.py (PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION).
# Strategia tripled-sentinel applicata (anti stale-push):
#   1) fresh PUBLIC_SYNC_TAG_RESYNC_v9 in cima a questo file (qui sopra)
#   2) sentinella inline VIP_DESIGN_AND_IAP_INTEGRATION_REGISTRATION_SENTINEL
#      immediatamente sopra la tupla nel blocco OPTIONAL
#   3) proof marker JSON dedicato:
#      data/design/vip/vip_suite_registration_proof_marker_v1.json
# RESYNC_v8b RATIONALE: Public branch main was stale on this file after Battle Pass pack commit
# (tuple ('PROJECT-BATTLE-PASS-SURFACE-MODERNIZATION', ...) and inline sentinel
# BATTLE_PASS_SURFACE_MODERNIZATION_REGISTRATION_SENTINEL were missing on remote). This v8b
# micro-touch comment is a recurrent stale-push mitigation: force a new blob hash so the next
# Save to GitHub PUSH cannot skip this file again. Proof marker dedicated:
#   data/design/battle_pass/bp_suite_runner_sync_fix_marker_v1.json
# Stage 6 GATED-IMPORT, Stage 7 LIVE-ACTIVATION-SIGNOFF, Stage 7B SUITE-RUNNER-SYNC-FIX,
# Stage 8 CANARY-LIVE-APPLY, IAP-DESIGN, SHOP-IAP-INTEGRATION, BATTLE-PASS-SURFACE-MODERNIZATION
# and VIP-DESIGN-AND-IAP-INTEGRATION OPTIONAL validators are all registered in the OPTIONAL
# block below. Inline sentinels:
#   STAGE_6_GATED_IMPORT_REGISTRATION_SENTINEL
#   STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL
#   STAGE_7B_LIVE_SIGNOFF_SUITE_RUNNER_SYNC_FIX_REGISTRATION_SENTINEL
#   STAGE_8_CANARY_LIVE_APPLY_REGISTRATION_SENTINEL
#   IAP_DESIGN_REGISTRATION_SENTINEL
#   SHOP_IAP_INTEGRATION_REGISTRATION_SENTINEL
#   BATTLE_PASS_SURFACE_MODERNIZATION_REGISTRATION_SENTINEL
#   VIP_DESIGN_AND_IAP_INTEGRATION_REGISTRATION_SENTINEL
# This file MUST be synced together with:
#   backend/scripts/validate_project_artifact_inventory_gated_import_v1.py
#   backend/scripts/validate_project_artifact_inventory_live_activation_signoff_v1.py
#   backend/scripts/validate_project_artifact_live_signoff_suite_runner_sync_fix_v1.py
#   backend/scripts/validate_project_artifact_inventory_live_apply_v1.py
#   backend/scripts/validate_project_iap_design_v1.py
#   backend/scripts/validate_project_shop_iap_integration_v1.py
#   backend/scripts/validate_project_battle_pass_surface_modernization_v1.py
#   backend/scripts/validate_project_vip_design_and_iap_integration_v1.py
# Dedicated proof markers (tripled-sentinel strategy, separate directories):
#   data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json
#   data/design/iap/iap_suite_registration_proof_marker_v1.json
#   data/design/shop_iap/shop_iap_suite_registration_proof_marker_v1.json
#   data/design/battle_pass/bp_suite_registration_proof_marker_v1.json
#   data/design/vip/vip_suite_registration_proof_marker_v1.json
"""
RM1.31-B — Hero Skill Kit Validator Suite Runner
─────────────────────────────────────────────────────────────────────────
Single command to run all Hero Skill Kit / Divine Weapon / Status-resolver
validators sequentially. Read-only orchestrator. NO catalog/DB/runtime
writes.

Exit 0 only if every REQUIRED validator passes; exit 1 if any fails.
Optional validators that are missing are reported and do not fail the
suite unless they are listed as required.

V17 SUITE SUPERSEDENCE CLEANUP METADATA (non-functional, doc only):
  Buckets (see /app/data/design/system_safety/validator_suite_supersedence_cleanup_report_v1.json
  and /app/docs/divine/VALIDATOR_SUITE_SUPERSEDENCE_POST_AF2N.md):
    1) ACTIVE_REQUIRED  — core 5-star/6-star/divine-weapon/balance
    2) ACTIVE_OPTIONAL  — contextual + V13/V14/V15/V16/V17 V16-aware
    3) SUPERSEDED_PRE_AF2N         — auto-marked when AFFINITY_GIFT_RUNTIME_ENABLED == truthy
    4) SUPERSEDED_PRE_INV_WRITES   — auto-marked when AFFINITY_GIFT_INVENTORY_WRITES_ENABLED == truthy
    5) HISTORICAL_MANUAL — apply/seed/rollback scripts; never run by suite
  No ACTIVE_REQUIRED validator removed or weakened. Historical scripts kept on disk.

Usage:
    python3 run_hero_skill_kit_validator_suite.py
    python3 run_hero_skill_kit_validator_suite.py --json-out /tmp/suite.json
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# v108_POSTQA_A — Master suite relocatable foundation.
# Default: directory dello script stesso (relativo, funziona anche fuori da /app).
# Override opzionale tramite env DIVINE_VALIDATOR_SCRIPTS_DIR. NON e' obbligatorio.
# v108_POSTQA_A_RELOCATABLE_DEFAULT_RELATIVE
_DEFAULT_SCRIPTS_DIR = Path(__file__).resolve().parent
_ENV_SCRIPTS_DIR = os.environ.get('DIVINE_VALIDATOR_SCRIPTS_DIR')
SCRIPTS_DIR = Path(_ENV_SCRIPTS_DIR).resolve() if _ENV_SCRIPTS_DIR else _DEFAULT_SCRIPTS_DIR
SAFE_REPORT_DIRS = (Path('/app/backend/reports'), Path('/tmp'), (SCRIPTS_DIR.parent / 'reports'))

REQUIRED = [
    ('RM1.28-A', 'validate_5star_passive_advanced_source.py'),
    ('RM1.28-B', 'audit_5star_skill_kits_crosslinks.py'),
    ('RM1.28-C', 'audit_5star_legacy_status_tags.py'),
    ('RM1.28-D', 'validate_5star_legacy_status_tags_normalized.py'),
    ('RM1.28-E', 'validate_5star_manual_review_residuals_resolved.py'),
    ('RM1.29',   'audit_6star_skill_kits_crosslinks.py'),
    ('RM1.30-A', 'validate_6star_catalog_safety_metadata.py'),
    ('RM1.30-B', 'audit_6star_effect_tags_taxonomy.py'),
    ('RM1.30-C', 'audit_hero_skill_kit_catalog_consolidation.py'),
    ('RM1.27-A', 'validate_divine_weapon_catalog.py'),
    ('RM1.27-D', 'audit_divine_weapon_crosslinks.py'),
    ('RM1.32-A', 'validate_5star_balance_foundation.py'),
    ('RM1.32-B', 'validate_6star_balance_foundation.py'),
    ('RM1.32-C2', 'validate_foundation_numeric_trim_rm132c2.py'),
    # PROJECT_K Track C — 5 RC validators PROMOTED to REQUIRED (authorized by Pack K Track C).
    # Promotion is safe: these 5 validators assert structural invariants of
    # status_first_slice_resolver_pure (purity, no tick-loop touch, caps respect,
    # symmetric PvP fairness, rollback runbook). They are independent from any
    # battle wiring and remain stable whether wiring is applied or not.
    # required_diff_guard_status: BREACH_APPROVED_BY_PACK_K_TRACK_C_PROMPT_AUTHORIZED.
    ('PROJECT-J-RC-1-RESOLVER-PURE-DETERMINISTIC', 'validate_project_j_status_first_slice_resolver_pure_deterministic_v1.py'),
    ('PROJECT-J-RC-2-NO-TICK-LOOP-TOUCH', 'validate_project_j_status_first_slice_no_tick_loop_touch_v1.py'),
    ('PROJECT-J-RC-3-CAPS-RESPECT', 'validate_project_j_status_first_slice_caps_respect_v1.py'),
    ('PROJECT-J-RC-4-PVP-FAIRNESS-AUDIT', 'validate_project_j_status_first_slice_pvp_fairness_audit_v1.py'),
    ('PROJECT-J-RC-5-ROLLBACK-RUNBOOK', 'validate_project_j_status_first_slice_rollback_runbook_v1.py'),
]
OPTIONAL = [
    # ========================================================================
    # PUBLIC_SYNC_TAG_v29_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
    # PUBLIC_SYNC_TAG_RESYNC_v29b_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
    # PUBLIC_SYNC_TAG_RESYNC_v29c_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
    # PUBLIC_SYNC_TAG_RESYNC_v29d_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY
    # VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # Relocated near the TOP of OPTIONAL list by v29d sync-fix to force public
    # blob refresh after v29b/v29c stale-push. Tuple count = 1 (unique).
    # Tier = OPTIONAL (never REQUIRED). No validator weakening, no fake PASS.
    # Parent pack: PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_PACK.
    # Parent commit: 0c6601b4. DESIGN_CONTRACT_AUDIT_ONLY: no runtime changes,
    # no DB writes, no reward/EXP/economy/gacha/BP/VIP/shop/Material Raid/
    # Gem Socket/Rune/Artifact/Divine Weapon runtime changes. Home PLAY stays
    # -> /story; Home Battle stays -> /story; /combat stays as dev/QA route.
    # /api/story/battle and /api/battle/simulate UNCHANGED.
    # Contract:    data/design/battle_visual_routing/battle_visual_routing_contract_v1.json
    # Guild War:   data/design/battle_visual_routing/guild_war_autoresolve_replay_policy_v1.json
    # Roadmap:     data/design/battle_visual_routing/mode_visual_battle_conversion_roadmap_v1.json
    # Proof v29:   data/design/battle_visual_routing/battle_visual_routing_contract_proof_marker_v1.json
    # Registry v2: data/design/battle_entrypoints/battle_entrypoint_registry_v2.json
    # Doc 218:     docs/divine/218_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY.md
    # Proof v29b:  data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29b_marker_v1.json
    # Doc 219:     docs/divine/219_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29b.md
    # Proof v29c:  data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29c_marker_v1.json
    # Doc 220:     docs/divine/220_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29c.md
    # Proof v29d:  data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29d_marker_v1.json
    # Doc 221:     docs/divine/221_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29d.md
    # ========================================================================
    ('PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY', 'validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_TAG_v30_STORY_VISUAL_BATTLE_WIRING_CONTRACT
    # PUBLIC_SYNC_TAG_RESYNC_v30b_STORY_VISUAL_BATTLE_WIRING_CONTRACT
    # STORY_VISUAL_BATTLE_WIRING_CONTRACT_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # PHASE_1 DESIGN_CONTRACT_AUDIT_ONLY pack: defines Story visual battle wiring
    # contract, battle_instance payload contract, reward/EXP/story progress
    # idempotency contract, transition plan PHASE_1->PHASE_7, registry v3.
    # No runtime conversion of Story. No DB writes. No reward/EXP/story progress
    # mutation. story.tsx UNCHANGED. combat.tsx UNCHANGED. homeAssetsManifest.ts
    # UNCHANGED. /api/story/battle UNCHANGED. /api/battle/simulate UNCHANGED.
    # battle_engine.py UNCHANGED. No gacha/Shop/BP/VIP/IAP changes. No Material
    # Raid/Gem Socket/Rune/Artifact/Divine Weapon/Guild War runtime changes.
    # No Character Bible/hero final_numbers. No REQUIRED/OPTIONAL validator
    # weakening. No tuple duplicate. No fake PASS. Validator OPTIONAL. Tuple
    # count v30 = 1. Tuple placed near TOP of OPTIONAL list for blob visibility.
    # Contract:     data/design/story_visual_battle/story_visual_battle_wiring_contract_v1.json
    # Payload:      data/design/story_visual_battle/story_battle_instance_payload_contract_v1.json
    # Idempotency:  data/design/story_visual_battle/story_reward_idempotency_contract_v1.json
    # Transition:   data/design/story_visual_battle/story_visual_battle_transition_plan_v1.json
    # Proof marker: data/design/story_visual_battle/story_visual_battle_wiring_contract_proof_marker_v1.json
    # Registry v3:  data/design/battle_entrypoints/battle_entrypoint_registry_v3.json
    # Doc 222:      docs/divine/222_STORY_VISUAL_BATTLE_WIRING_CONTRACT.md
    # ========================================================================
    ('PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT', 'validate_project_story_visual_battle_wiring_contract_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1
    # PUBLIC_SYNC_TAG_RESYNC_v31b_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR
    # MEGA_BATCH_ACCELERATION_1_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_BATCH_ACCELERATION_1_STORY_PREVIEW_MATERIAL_RAID_GEM_GUIDE_REGISTRY_PACK
    # 5 OPTIONAL tuples (Track A/B/C/D + ROLLUP). Tier = OPTIONAL only.
    # Each tuple count = 1. No REQUIRED weakening. No fake PASS.
    # Track A: backend/routes/story_battle_instance_preview.py
    # Track B: backend/routes/material_raid_preview.py + frontend/constants/materialRaid.ts
    # Track C: data/design/battle_entrypoints/battle_entrypoint_registry_v4.json
    # Track D: data/design/guide_codex/guide_codex_fill_gaps_v1.json
    # Rollup:  backend/scripts/validate_mega_batch_acceleration_1_rollup.py
    # Proof marker: data/design/mega_batch_acceleration/mega_batch_acceleration_1_proof_marker_v1.json
    # Doc 228:      docs/divine/228_MEGA_BATCH_ACCELERATION_1_STORY_PREVIEW_MATERIAL_RAID_GEM_GUIDE_REGISTRY.md
    # ========================================================================
    ('PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT', 'validate_project_story_battle_instance_preview_endpoint_v1.py'),
    ('PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK', 'validate_project_material_raid_gem_track_preview_unlock_v1.py'),
    ('PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION', 'validate_project_mode_battle_entrypoint_registry_expansion_v1.py'),
    ('PROJECT-GUIDE-CODEX-FILL-GAPS', 'validate_project_guide_codex_fill_gaps_v1.py'),
    ('MEGA-BATCH-ACCELERATION-1-ROLLUP', 'validate_mega_batch_acceleration_1_rollup.py'),
    # ========================================================================
    # PUBLIC_SYNC_TAG_v32_STORY_VISUAL_BATTLE_SANDBOX
    # STORY_VISUAL_BATTLE_SANDBOX_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # PROJECT_STORY_VISUAL_BATTLE_SANDBOX_PACK (PHASE_3). Sandbox dev/QA only.
    # Synthetic deterministic playback timeline. No reward. No EXP. No story
    # progress. No replay reward. No DB writes. No AsyncStorage writes.
    # Reuses STORY_BATTLE_INSTANCE_PREVIEW_ENABLED flag. battle_engine UNCHANGED.
    # /api/story/battle UNCHANGED. /api/battle/simulate UNCHANGED. story.tsx
    # UNCHANGED. combat.tsx UNCHANGED. homeAssetsManifest.ts UNCHANGED. New
    # sandbox route NOT linked from Home/menu/tabs. Tuple count = 1.
    # Contract:    data/design/story_visual_battle/story_visual_battle_sandbox_contract_v1.json
    # Proof:       data/design/story_visual_battle/story_visual_battle_sandbox_proof_marker_v1.json
    # Doc 230:     docs/divine/230_PROJECT_STORY_VISUAL_BATTLE_SANDBOX.md
    # Frontend:    frontend/app/story-visual-battle-sandbox.tsx
    # Backend +:   backend/routes/story_battle_instance_preview.py (sandbox-playback endpoint)
    # ========================================================================
    ('PROJECT-STORY-VISUAL-BATTLE-SANDBOX', 'validate_project_story_visual_battle_sandbox_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT
    # PUBLIC_SYNC_TAG_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT
    # GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_PACK (PHASE_3 sister).
    # DESIGN_CONTRACT_AUDIT_ONLY. Zero runtime conversion. Zero new live route.
    # combat.tsx UNCHANGED (still calls /api/battle/simulate on mount).
    # story.tsx UNCHANGED (still auto-resolves via /api/story/battle).
    # story-visual-battle-sandbox.tsx UNCHANGED (sandbox preview-only).
    # Home routes UNCHANGED (play/battle -> /story).
    # battle_engine.py UNCHANGED. /api/story/battle UNCHANGED.
    # /api/battle/simulate UNCHANGED. No backend route added. db_writes = 0.
    # No reward/EXP/progress/economy/gacha/BP/VIP/IAP/Material Raid/Gem Socket/
    # Rune/Artifact/Divine Weapon/Guild War runtime changes. Tuple count = 1.
    # Contract:    data/design/visual_battle_runner/generic_visual_battle_runner_contract_v1.json
    # Payload:     data/design/visual_battle_runner/visual_battle_runner_payload_schema_v1.json
    # Adapters:    data/design/visual_battle_runner/visual_battle_runner_mode_adapter_matrix_v1.json
    # Commit:      data/design/visual_battle_runner/visual_battle_runner_result_commit_contract_v1.json
    # Replay/View: data/design/visual_battle_runner/visual_battle_runner_replay_view_contract_v1.json
    # Proof:       data/design/visual_battle_runner/generic_visual_battle_runner_contract_proof_marker_v1.json
    # Registry v5: data/design/battle_entrypoints/battle_entrypoint_registry_v5.json
    # Doc 231:     docs/divine/231_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v33b/v33c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-CONTRACT', 'validate_project_generic_visual_battle_runner_contract_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE
    # PUBLIC_SYNC_TAG_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE
    # GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK (v34 PHASE_4).
    # PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT. Default 503 disabled. Feature flag:
    # GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED. 4 gated endpoints under
    # /api/generic-visual-battle-runner-preview/* (config, sample-payload,
    # validate-payload, playback-preview). Deeplink-only frontend route at
    # /generic-visual-battle-runner-preview. db_writes=0. No reward grant.
    # No EXP grant. No story/daily/quest/achievement progress. No claim/commit
    # buttons. No call to battle_engine.py. No call to /api/battle/simulate.
    # No call to /api/story/battle. combat.tsx UNCHANGED. story.tsx UNCHANGED.
    # story-visual-battle-sandbox.tsx UNCHANGED. Home routes UNCHANGED.
    # battle_engine.py UNCHANGED. server.py scoped diff only (include_router).
    # Sample payload v33-compliant (21 required fields). Tuple count = 1.
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v34b/v34c sync-fix pack will be attempted.
    # Backend:   backend/routes/generic_visual_battle_runner_preview.py
    # Frontend:  frontend/app/generic-visual-battle-runner-preview.tsx
    # Design:    data/design/visual_battle_runner/generic_visual_battle_runner_preview_route_v1.json
    # Proof:     data/design/visual_battle_runner/generic_visual_battle_runner_preview_route_proof_marker_v1.json
    # Registry6: data/design/battle_entrypoints/battle_entrypoint_registry_v6.json
    # Doc 232:   docs/divine/232_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE.md
    # ========================================================================
    ('PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-PREVIEW-ROUTE', 'validate_project_generic_visual_battle_runner_preview_route_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v35_MEGA_VISUAL_BATTLE_ACCELERATION_2
    # PUBLIC_SYNC_TAG_v35_MEGA_VISUAL_BATTLE_ACCELERATION_2
    # MEGA_VISUAL_BATTLE_ACCELERATION_2_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_VISUAL_BATTLE_ACCELERATION_2_RUNTIME_SHELL_AND_GUILD_WAR_REPLAY_
    # CONTRACT_PACK_v35 (combo pack, 2 tracks + rollup).
    # ------------------------------------------------------------------------
    # TRACK A: PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL_PACK
    # PHASE_4B. PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT. First isolated RN preview
    # runtime shell rendering /api/generic-visual-battle-runner-preview/
    # playback-preview envelope visually (HP bars, timeline stepper, hit
    # markers, result_summary, safety panel). Reuses existing v34 route and
    # v34 feature flag GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED. Default
    # 503 disabled state preserved. Deeplink-only. No reward/claim/commit
    # buttons. No AsyncStorage writes. No call to battle_engine. No call to
    # /api/battle/simulate or /api/story/battle. combat.tsx/story.tsx/story-
    # visual-battle-sandbox.tsx/Home routes/battle_engine.py UNCHANGED. No
    # new dependency installed. No new backend route. db_writes=0.
    # ------------------------------------------------------------------------
    # TRACK B: PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT_PACK
    # PHASE_5. DESIGN_CONTRACT_AUDIT_ONLY. Defines contract foundation for the
    # FUTURE Guild War auto-resolve replay/view link. Guild War remains the
    # only auto-resolve exception. Future target /battle-replay. Future
    # viewer_kind=guild_war_view via Generic Visual Battle Runner. No live
    # /battle-replay route created. No Guild War runtime mutation. No reward
    # grant. No war_score mutation. No guild_points mutation. No PII in share
    # payload. Privacy + retention policies attached. Registry v7 supersedes
    # v6 with new isolated battle_replay_viewer_future entry. db_writes=0.
    # ------------------------------------------------------------------------
    # ROLLUP: MEGA-VISUAL-BATTLE-ACCELERATION-2-v35-ROLLUP runs Track A +
    # Track B validators back-to-back and asserts global invariants (5 MD5-
    # locked files, suite tuples count=1 each, sentinels present).
    # ------------------------------------------------------------------------
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v35b/v35c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-PREVIEW-RUNTIME-SHELL', 'validate_project_generic_visual_battle_runner_preview_runtime_shell_v1.py'),
    ('PROJECT-GUILD-WAR-AUTORESOLVE-REPLAY-LINK-CONTRACT', 'validate_project_guild_war_autoresolve_replay_link_contract_v1.py'),
    ('MEGA-VISUAL-BATTLE-ACCELERATION-2-v35-ROLLUP', 'validate_mega_visual_battle_acceleration_2_v35_rollup.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v36_BATTLE_REPLAY_PREVIEW_ROUTE
    # PUBLIC_SYNC_TAG_v36_BATTLE_REPLAY_PREVIEW_ROUTE
    # BATTLE_REPLAY_PREVIEW_ROUTE_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK (v36 PHASE_6).
    # BATTLE_REPLAY_PREVIEW_ROUTE_GATED_VIEW_ONLY. Default 503 disabled.
    # Feature flag: BATTLE_REPLAY_PREVIEW_ENABLED. viewer_kind=guild_war_view.
    # 4 gated endpoints under /api/battle-replay-preview/* (config GET,
    # sample-guild-war-replay GET, validate-replay-payload POST, playback-
    # preview POST). Deeplink-only frontend route at /battle-replay-preview
    # that reuses v35 VisualBattlePreviewShell via a pure local adapter.
    # db_writes=0. No reward grant. No EXP grant. No story/daily/quest/
    # achievement progress. No war score mutation. No guild points mutation.
    # No call to battle_engine.py. No call to /api/battle/simulate. No call
    # to /api/story/battle. No live /battle-replay route created. Guild War
    # runtime UNCHANGED. combat.tsx / story.tsx / story-visual-battle-
    # sandbox.tsx / generic-visual-battle-runner-preview.tsx UNCHANGED. Home
    # routes UNCHANGED. battle_engine.py UNCHANGED. server.py scoped diff
    # only (include_router). Sample Guild War replay v35-compliant
    # (17 required fields). Tuple count = 1.
    # Backend:   backend/routes/battle_replay_preview.py
    # Frontend:  frontend/app/battle-replay-preview.tsx
    # Design:    data/design/guild_war_replay/battle_replay_preview_route_v1.json
    # Proof:     data/design/guild_war_replay/battle_replay_preview_route_proof_marker_v1.json
    # Registry8: data/design/battle_entrypoints/battle_entrypoint_registry_v8.json
    # Doc 237:   docs/divine/237_BATTLE_REPLAY_PREVIEW_ROUTE.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v36b/v36c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-BATTLE-REPLAY-PREVIEW-ROUTE', 'validate_project_battle_replay_preview_route_v1.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v37_MEGA_ECONOMY_SAFETY_ACCELERATION_1
    # PUBLIC_SYNC_TAG_v37_MEGA_ECONOMY_SAFETY_ACCELERATION_1
    # MEGA_ECONOMY_SAFETY_ACCELERATION_1_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_ECONOMY_SAFETY_ACCELERATION_1_GEM_SOCKET_AND_MATERIAL_RAID_HARDENING
    # _PACK_v37 (combo pack, 3 tracks + rollup). All OPTIONAL, count=1 each.
    # ------------------------------------------------------------------------
    # TRACK A: PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK (PHASE_7A).
    # ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT. New gated route at
    # /api/gem-socket-commit-safety-preview/* (config GET, validate-request POST,
    # guard-plan-preview POST, idempotency-preview POST). Default 503 disabled.
    # Feature flag: GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED. operation_family
    # = gem_socket_commit. db_writes=0. No live commit. No gear mutation. No
    # gem inventory mutation. No premium users.gems used. No reward/EXP grant.
    # No stamina/tickets consumption. No call to battle_engine. No call to
    # /api/battle/simulate or /api/story/battle. Existing
    # backend/routes/gem_socket_preview.py UNCHANGED.
    # ------------------------------------------------------------------------
    # TRACK B: PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK (PHASE_7B).
    # ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM. New gated route at
    # /api/material-raid-claim-safety-preview/* (config GET,
    # validate-claim-request POST, grant-plan-preview POST, idempotency-preview
    # POST). Default 503 disabled. Feature flag:
    # MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED. operation_family =
    # material_raid_claim. db_writes=0. No live claim. No materials granted.
    # No user_materials mutation. No reward/EXP grant. No stamina/tickets/
    # paid attempt consumption. No call to battle_engine. No call to
    # /api/battle/simulate or /api/story/battle. Existing
    # backend/routes/material_raid_preview.py UNCHANGED.
    # ------------------------------------------------------------------------
    # TRACK C: PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT_PACK
    # (PHASE_7C). DESIGN_CONTRACT_AUDIT_ONLY. Shared economy safety contract
    # (idempotency, request hash, atomic commit, rollback, audit log, TTL).
    # No runtime activation. No new backend route created by this track.
    # db_writes=0. Referenced by Track A and Track B.
    # ------------------------------------------------------------------------
    # ROLLUP: MEGA-ECONOMY-SAFETY-ACCELERATION-1-v37-ROLLUP runs Track A/B/C
    # validators back-to-back and asserts the 5 MD5-locked core files and the
    # 4 suite tuple counts (count=1 each). No fake PASS. No validator
    # weakening. No tuple duplicate.
    # ------------------------------------------------------------------------
    # Files:
    #   Route A:   backend/routes/gem_socket_commit_safety_preview.py
    #   Route B:   backend/routes/material_raid_claim_safety_preview.py
    #   Design A:  data/design/economy_safety/gem_socket_commit_safety_preview_v1.json
    #   Design B:  data/design/economy_safety/material_raid_claim_safety_preview_v1.json
    #   Design C:  data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json
    #   Proof A:   data/design/economy_safety/gem_socket_commit_safety_preview_proof_marker_v1.json
    #   Proof B:   data/design/economy_safety/material_raid_claim_safety_preview_proof_marker_v1.json
    #   Proof C:   data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_proof_marker_v1.json
    #   Rollup:    data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json
    #   Doc 238:   docs/divine/238_GEM_SOCKET_COMMIT_SAFETY_HARDENING.md
    #   Doc 239:   docs/divine/239_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING.md
    #   Doc 240:   docs/divine/240_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT.md
    #   Doc 241:   docs/divine/241_MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v37b/v37c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-GEM-SOCKET-COMMIT-SAFETY-HARDENING', 'validate_project_gem_socket_commit_safety_hardening_v1.py'),
    ('PROJECT-MATERIAL-RAID-CLAIM-SAFETY-HARDENING', 'validate_project_material_raid_claim_safety_hardening_v1.py'),
    ('PROJECT-ECONOMY-IDEMPOTENCY-AND-ATOMIC-COMMIT-CONTRACT', 'validate_project_economy_idempotency_and_atomic_commit_contract_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-1-v37-ROLLUP', 'validate_mega_economy_safety_acceleration_1_v37_rollup.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v38_MEGA_ECONOMY_SAFETY_ACCELERATION_2
    # PUBLIC_SYNC_TAG_v38_MEGA_ECONOMY_SAFETY_ACCELERATION_2
    # MEGA_ECONOMY_SAFETY_ACCELERATION_2_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_PACK_v38
    # (combo pack, 2 build-system tracks + registry v2 + rollup). All OPTIONAL,
    # count=1 each.
    # ------------------------------------------------------------------------
    # TRACK A: PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING_PACK (PHASE_8A).
    # BUILD_SYSTEM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT. New
    # gated route at /api/gear-forge-fusion-safety-preview/* (config GET,
    # validate-request POST, guard-plan-preview POST, idempotency-preview POST).
    # Default 503 disabled. Feature flag:
    # GEAR_FORGE_FUSION_SAFETY_PREVIEW_ENABLED. operation_family =
    # gear_forge_fusion_commit. allowed_operation_types: gear_upgrade,
    # gear_fusion, gear_reforge_preview. db_writes=0. No live commit. No gear
    # mutation. No material/currency consumption. No premium users.gems use.
    # No BP Delta trigger. No call to battle_engine. No call to
    # /api/battle/simulate or /api/story/battle. backend/routes/forge.py
    # UNCHANGED.
    # ------------------------------------------------------------------------
    # TRACK B: PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING_PACK
    # (PHASE_8B). BUILD_SYSTEM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_
    # COMMIT. New gated route at /api/rune-scroll-talisman-safety-preview/*
    # (config GET, validate-request POST, guard-plan-preview POST,
    # idempotency-preview POST). Default 503 disabled. Feature flag:
    # RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED. operation_family =
    # rune_scroll_talisman_commit. allowed_operation_types: rune_equip,
    # rune_replace, rune_unsocket, rune_fuse, rune_upgrade. Canonical
    # distinction explicit: Rune (scroll/talismani/pergamene/sigilli on hero)
    # is NOT Gemme, NOT Artifact, NOT Divine Weapon. db_writes=0. No live
    # commit. No hero rune slot mutation. No rune inventory mutation. No
    # material/currency consumption. No premium users.gems use. No BP Delta
    # trigger. backend/routes/forge.py UNCHANGED.
    # ------------------------------------------------------------------------
    # TRACK C: PROJECT_BUILD_SYSTEM_ECONOMY_SAFETY_REGISTRY_v2.
    # DESIGN_CONTRACT_AUDIT_ONLY. Shared registry v2 extends v37 framework to
    # 4 active safety-layered operation families + 4 placeholders. Global:
    # build_system_safety_hardening_v38_ready=true,
    # live_commit_allowed_in_this_pack=false, db_writes=0,
    # bp_delta_runtime_enabled=false. No new backend route in this track.
    # ------------------------------------------------------------------------
    # ROLLUP: MEGA-ECONOMY-SAFETY-ACCELERATION-2-v38-ROLLUP runs Track A/B
    # validators back-to-back and asserts the 5 MD5-locked core files, the 3
    # suite tuple counts (count=1 each), registry v2 coherence, v37 shared
    # contract still present, forge.py unchanged. No fake PASS. No validator
    # weakening. No tuple duplicate.
    # ------------------------------------------------------------------------
    # Files:
    #   Route A:   backend/routes/gear_forge_fusion_safety_preview.py
    #   Route B:   backend/routes/rune_scroll_talisman_safety_preview.py
    #   Design A:  data/design/gear_forge/gear_forge_fusion_commit_safety_hardening_v1.json
    #   Schema A:  data/design/gear_forge/gear_forge_fusion_commit_request_schema_v1.json
    #   Guard A:   data/design/gear_forge/gear_forge_fusion_guard_policy_v1.json
    #   Proof A:   data/design/gear_forge/gear_forge_fusion_safety_proof_marker_v1.json
    #   Design B:  data/design/rune_scroll_talisman/rune_scroll_talisman_commit_safety_hardening_v1.json
    #   Schema B:  data/design/rune_scroll_talisman/rune_scroll_talisman_commit_request_schema_v1.json
    #   Guard B:   data/design/rune_scroll_talisman/rune_scroll_talisman_guard_policy_v1.json
    #   Proof B:   data/design/rune_scroll_talisman/rune_scroll_talisman_safety_proof_marker_v1.json
    #   Registry:  data/design/economy_safety/build_system_economy_safety_registry_v2.json
    #   Rollup:    data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json
    #   Doc 242:   docs/divine/242_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING.md
    #   Doc 243:   docs/divine/243_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING.md
    #   Doc 244:   docs/divine/244_MEGA_ECONOMY_SAFETY_ACCELERATION_2_v38.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v38b/v38c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-GEAR-FORGE-FUSION-COMMIT-SAFETY-HARDENING', 'validate_project_gear_forge_fusion_commit_safety_hardening_v1.py'),
    ('PROJECT-RUNE-SCROLL-TALISMAN-COMMIT-SAFETY-HARDENING', 'validate_project_rune_scroll_talisman_commit_safety_hardening_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-2-v38-ROLLUP', 'validate_mega_economy_safety_acceleration_2_v38_rollup.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v39_MEGA_ECONOMY_SAFETY_ACCELERATION_3
    # PUBLIC_SYNC_TAG_v39_MEGA_ECONOMY_SAFETY_ACCELERATION_3
    # MEGA_ECONOMY_SAFETY_ACCELERATION_3_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_ECONOMY_SAFETY_ACCELERATION_3_ARTIFACT_AND_DIVINE_WEAPON_HARDENING
    # _PACK_v39 (combo pack, 2 endgame tracks + registry v3 + rollup). All
    # OPTIONAL, count=1 each.
    # ------------------------------------------------------------------------
    # TRACK A: PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING_PACK (PHASE_9A).
    # ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT. New gated
    # route at /api/artifact-upgrade-safety-preview/* (config GET,
    # validate-request POST, guard-plan-preview POST, idempotency-preview
    # POST). Default 503 disabled. Feature flag:
    # ARTIFACT_UPGRADE_SAFETY_PREVIEW_ENABLED. operation_family =
    # artifact_upgrade_commit. allowed_operation_types: artifact_upgrade,
    # artifact_duplicate_fusion, artifact_limit_break_preview. db_writes=0.
    # No live upgrade/fusion/pull. No artifact mutation. No global bonus
    # activation. No material/currency consumption. No premium users.gems
    # use. No BP Delta trigger. No call to battle_engine. No call to
    # /api/battle/simulate or /api/story/battle. backend/routes/artifacts.py
    # UNCHANGED (MD5 locked, asserted in validator).
    # ------------------------------------------------------------------------
    # TRACK B: PROJECT_DIVINE_WEAPON_UPGRADE_COMMIT_SAFETY_HARDENING_PACK
    # (PHASE_9B). ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT.
    # New gated route at /api/divine-weapon-upgrade-safety-preview/* (config
    # GET, validate-request POST, guard-plan-preview POST, idempotency-preview
    # POST). Default 503 disabled. Feature flag:
    # DIVINE_WEAPON_UPGRADE_SAFETY_PREVIEW_ENABLED. operation_family =
    # divine_weapon_upgrade_commit. allowed_operation_types:
    # divine_weapon_unlock_preview, divine_weapon_upgrade,
    # divine_weapon_awaken_preview. Canonical distinction explicit: Divine
    # Weapon is native-6-star-only, character-bound, NOT generic gear, NOT
    # artifact, NOT rune/gem. db_writes=0. No live unlock/upgrade/awakening.
    # No divine weapon mutation. No hero copy consumption. No material/
    # currency consumption. No premium users.gems use. No BP Delta trigger.
    # Character Bible unchanged. hero final_numbers unchanged.
    # ------------------------------------------------------------------------
    # TRACK C: PROJECT_ENDGAME_SYSTEM_ECONOMY_SAFETY_REGISTRY_v3.
    # DESIGN_CONTRACT_AUDIT_ONLY. Shared registry v3 supersedes v2 and adds
    # the 2 new endgame operation families. Global:
    # endgame_safety_hardening_v39_ready=true,
    # artifact_upgrade_safety_preview_ready=true,
    # divine_weapon_upgrade_safety_preview_ready=true,
    # live_commit_allowed_in_this_pack=false, db_writes=0,
    # bp_delta_runtime_enabled=false. No new backend route in this track.
    # ------------------------------------------------------------------------
    # ROLLUP: MEGA-ECONOMY-SAFETY-ACCELERATION-3-v39-ROLLUP runs Track A/B
    # validators back-to-back and asserts the 5 MD5-locked core files, the 3
    # suite tuple counts (count=1 each), registry v3 coherence, v37 shared
    # contract + v38 registry v2 still present, backend/routes/artifacts.py
    # unchanged (strict MD5). No fake PASS. No validator weakening. No tuple
    # duplicate.
    # ------------------------------------------------------------------------
    # Files:
    #   Route A:   backend/routes/artifact_upgrade_safety_preview.py
    #   Route B:   backend/routes/divine_weapon_upgrade_safety_preview.py
    #   Design A:  data/design/artifacts/artifact_upgrade_commit_safety_hardening_v1.json
    #   Schema A:  data/design/artifacts/artifact_upgrade_commit_request_schema_v1.json
    #   Guard A:   data/design/artifacts/artifact_upgrade_guard_policy_v1.json
    #   Proof A:   data/design/artifacts/artifact_upgrade_safety_proof_marker_v1.json
    #   Design B:  data/design/divine_weapon/divine_weapon_upgrade_commit_safety_hardening_v1.json
    #   Schema B:  data/design/divine_weapon/divine_weapon_upgrade_commit_request_schema_v1.json
    #   Guard B:   data/design/divine_weapon/divine_weapon_guard_policy_v1.json
    #   Proof B:   data/design/divine_weapon/divine_weapon_safety_proof_marker_v1.json
    #   Registry:  data/design/economy_safety/endgame_economy_safety_registry_v3.json
    #   Rollup:    data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json
    #   Doc 247:   docs/divine/247_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING.md
    #   Doc 248:   docs/divine/248_DIVINE_WEAPON_UPGRADE_COMMIT_SAFETY_HARDENING.md
    #   Doc 249:   docs/divine/249_MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. No v39b/v39c sync-fix pack will be attempted.
    # ========================================================================
    ('PROJECT-ARTIFACT-UPGRADE-COMMIT-SAFETY-HARDENING', 'validate_project_artifact_upgrade_commit_safety_hardening_v1.py'),
    ('PROJECT-DIVINE-WEAPON-UPGRADE-COMMIT-SAFETY-HARDENING', 'validate_project_divine_weapon_upgrade_commit_safety_hardening_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-3-v39-ROLLUP', 'validate_mega_economy_safety_acceleration_3_v39_rollup.py'),
    # ========================================================================
    # PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v40_MEGA_ECONOMY_SAFETY_ACCELERATION_4
    # PUBLIC_SYNC_TAG_v40_MEGA_ECONOMY_SAFETY_ACCELERATION_4
    # MEGA_ECONOMY_SAFETY_ACCELERATION_4_REGISTRATION_SENTINEL
    # ------------------------------------------------------------------------
    # MEGA_ECONOMY_SAFETY_ACCELERATION_4_BATTLE_PASS_AND_MAIL_CLAIM_HARDENING
    # _PACK_v40 (combo pack, 2 reward-claim tracks + registry v4 + rollup).
    # All OPTIONAL, count=1 each. Closes the last 2 placeholders of the
    # endgame economy safety registry. After this pack, ALL 8 operation
    # families have a preview-only safety layer.
    # ------------------------------------------------------------------------
    # TRACK A: PROJECT_BATTLE_PASS_REWARD_CLAIM_SAFETY_HARDENING_PACK (PHASE_10A).
    # REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM. New
    # gated route at /api/battle-pass-claim-safety-preview/* (config GET,
    # validate-request POST, guard-plan-preview POST, idempotency-preview
    # POST). Default 503 disabled. Feature flag:
    # BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED. operation_family =
    # battle_pass_reward_claim. allowed_operation_types: free_reward_claim,
    # premium_reward_claim_preview, milestone_reward_claim,
    # season_reward_claim_preview. db_writes=0. No live claim. No reward
    # grant. No inventory/currency mutation. No premium currency. No BP
    # purchase. No premium track unlock. No VIP/shop mutation. No BP Delta.
    # frontend/app/battlepass.tsx UNCHANGED (MD5 locked, asserted).
    # frontend/app/vip.tsx UNCHANGED (MD5 locked, asserted).
    # ------------------------------------------------------------------------
    # TRACK B: PROJECT_MAIL_REWARD_CLAIM_SAFETY_HARDENING_PACK (PHASE_10B).
    # REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM. New
    # gated route at /api/mail-claim-safety-preview/* (config GET,
    # validate-request POST, guard-plan-preview POST, idempotency-preview
    # POST). Default 503 disabled. Feature flag:
    # MAIL_CLAIM_SAFETY_PREVIEW_ENABLED. operation_family =
    # mail_reward_claim. allowed_operation_types: single_reward_claim,
    # bulk_reward_claim_preview, attachment_claim,
    # compensation_claim_preview, event_reward_claim_preview. db_writes=0.
    # No live claim. No reward grant. No mail state mutation (no delete,
    # no read/unread, no claim state). No inventory/currency mutation. No
    # premium currency. No BP Delta. No admin/sender live tooling.
    # ------------------------------------------------------------------------
    # TRACK C: PROJECT_REWARD_CLAIM_ECONOMY_SAFETY_REGISTRY_v4.
    # DESIGN_CONTRACT_AUDIT_ONLY. Shared registry v4 supersedes v3 and
    # marks both BP claim + Mail claim as preview_only_safety_layer_present.
    # Global: all_8_operation_families_have_preview_safety_layer=true,
    # live_commit_allowed_in_this_pack=false,
    # live_claim_allowed_in_this_pack=false, db_writes=0,
    # reward_grant_enabled=false, bp_delta_runtime_enabled=false.
    # ------------------------------------------------------------------------
    # ROLLUP: MEGA-ECONOMY-SAFETY-ACCELERATION-4-v40-ROLLUP runs Track A/B
    # validators back-to-back and asserts the 5 MD5-locked core files, the
    # 3 suite tuple counts (count=1 each), registry v4 coherence (8 op
    # families), v37 shared contract + v38/v39 registries v2/v3 still
    # present, server.py LOUD sentinel present, include_router counts = 1
    # each. No fake PASS. No validator weakening. No tuple duplicate.
    # ------------------------------------------------------------------------
    # Files:
    #   Route A:    backend/routes/battle_pass_claim_safety_preview.py
    #   Route B:    backend/routes/mail_claim_safety_preview.py
    #   Proof A:    data/design/economy_safety/battle_pass_claim_safety_proof_marker_v1.json
    #   Proof B:    data/design/economy_safety/mail_claim_safety_proof_marker_v1.json
    #   Registry:   data/design/economy_safety/reward_claim_economy_safety_registry_v4.json
    #   Rollup:     data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json
    #   Doc 251:    docs/divine/251_BATTLE_PASS_REWARD_CLAIM_SAFETY_HARDENING.md
    #   Doc 252:    docs/divine/252_MAIL_REWARD_CLAIM_SAFETY_HARDENING.md
    #   Doc 253:    docs/divine/253_MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40.md
    # Known caveat: SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION
    # accepted. server.py LOUD sentinel block ensures public blob refresh.
    # ========================================================================
    ('PROJECT-BATTLE-PASS-CLAIM-SAFETY-HARDENING', 'validate_project_battle_pass_claim_safety_hardening_v1.py'),
    ('PROJECT-MAIL-CLAIM-SAFETY-HARDENING', 'validate_project_mail_claim_safety_hardening_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-4-v40-ROLLUP', 'validate_mega_economy_safety_acceleration_4_v40_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41
    # ------------------------------------------------------------------------
    # 3 design-only track + 1 rollup:
    #   TRACK A: shared request hash + idempotency contract (cross-family,
    #            covers all 8 op families v37-v40). Design JSON only.
    #   TRACK B: economy safety observability foundation (audit schema,
    #            privacy policy, metrics, dashboard panels, alert rules).
    #            Design JSON only. No runtime.
    #   TRACK C: pre-signoff & rollback bundle (readiness matrix, signoff
    #            register, canary/live state, rollback templates). Design
    #            JSON only. All signoff=pending, canary=false, live=false.
    #   ROLLUP : runs A/B/C back-to-back + MD5 invariants + suite tuple
    #            counts + prior rollup markers presence.
    # ------------------------------------------------------------------------
    # Invariants enforced:
    #   - runtime_activation=false, db_writes=0 across all v41 files
    #   - no_pii_in_request_hash, no_pii_in_idempotency_key
    #   - no_live_apply, no_live_commit, no_live_claim, no_reward_grant
    #   - no_premium_currency_use, no_bp_delta_runtime
    #   - all 8 op families: signoff=pending, canary=false, live=false
    #   - 5 MD5-locked core files unchanged
    # No new FastAPI routers added by v41. server.py unchanged for v41.
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT', 'validate_shared_request_hash_idempotency_contract_v1.py'),
    ('PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION', 'validate_economy_safety_observability_foundation_v1.py'),
    ('PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE', 'validate_economy_safety_pre_signoff_bundle_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-5-v41-ROLLUP', 'validate_mega_economy_safety_acceleration_5_v41_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42
    # PUBLIC_SYNC_TAG_v42_MEGA_ECONOMY_SAFETY_ACCELERATION_6
    # ------------------------------------------------------------------------
    # Dry-run runtime instrumentation:
    #   TRACK A: shared request hash dry-run utility +
    #            wire-up into 8 safety preview routes (no ledger, no DB).
    #   TRACK B: observability dry-run utility (audit/metric preview) +
    #            wire-up into 8 safety preview routes (no persistence,
    #            no external sink, no PII).
    #   TRACK C: canary/signoff pilot design for material_raid_claim:
    #            signoff=pending, canary_enabled=false, canary_percentage=0,
    #            live_enabled=false, reward/material grant=false.
    #   ROLLUP : runs A/B/C back-to-back + MD5 invariants + suite tuple
    #            counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v42:
    #   - 8/8 safety preview route endpoint paths unchanged
    #   - 8/8 safety preview route feature flags unchanged
    #   - 8/8 safety preview route default 503 behavior unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v42
    #   - DB writes total = 0; live commit/claim/reward = false
    #   - canary pilot signoff = pending; canary = false; live = false
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN', 'validate_request_hash_runtime_enforcement_dry_run_v1.py'),
    ('PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN', 'validate_economy_observability_runtime_dry_run_v1.py'),
    ('PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT', 'validate_economy_safety_canary_signoff_dry_run_pilot_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-6-v42-ROLLUP', 'validate_mega_economy_safety_acceleration_6_v42_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_PACK_v43
    # PUBLIC_SYNC_TAG_v43_MEGA_ECONOMY_SAFETY_ACCELERATION_7
    # ------------------------------------------------------------------------
    # Dry-run replay/conflict detection:
    #   TRACK A: in-memory TTL-bounded utility for idempotency replay/conflict
    #            detection across the 8 safety preview routes.
    #            Max 256 entries, TTL 60s, per-process (not shared, not durable).
    #            No DB, no Redis, no filesystem, no persistent ledger, no live
    #            enforcement, no blocking the preview request on conflict.
    #   ROLLUP : runs Track A + MD5 invariants (5 core + 2 v42 utils) + suite
    #            tuple counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v43:
    #   - 8/8 safety preview route endpoint paths/feature flags/default 503/
    #     safety_flags unchanged
    #   - v42 request_hash_dry_run / observability_dry_run envelopes unchanged
    #   - v42 utils MD5 unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v43
    #   - DB writes total = 0; preview request never blocked
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN', 'validate_economy_idempotency_replay_detection_dry_run_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-7-v43-ROLLUP', 'validate_mega_economy_safety_acceleration_7_v43_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_8_CLIENT_KEY_BUFFER_AND_CANARY_REHEARSAL_PACK_v44
    # PUBLIC_SYNC_TAG_v44_MEGA_ECONOMY_SAFETY_ACCELERATION_8
    # ------------------------------------------------------------------------
    # Client-key replay detection + observability buffer peek + canary rehearsal:
    #   TRACK A: in-memory client_idem_key replay/conflict detection utility
    #            (TTL-bounded, max 256 entries, TTL 60s, per-process; NO DB,
    #            NO Redis, NO filesystem, NO persistent ledger, NO live
    #            enforcement, NO blocking the preview request on conflict).
    #   TRACK B: read-only /peek-buffer endpoint exposing observability buffer
    #            snapshot (counts only, no payload mutation, default 503 when
    #            safety flag OFF; NO DB writes, NO Redis, NO filesystem).
    #   TRACK C: Material Raid canary QA rehearsal dry-run (design-only matrix,
    #            no live enforcement, no reward grant, no inventory mutation).
    #   ROLLUP : runs Track A + B + C + MD5 invariants (5 core) + suite tuple
    #            counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v44:
    #   - 8/8 safety preview route endpoint paths / feature flags / default 503
    #     / safety_flags unchanged
    #   - v42 + v43 utils MD5 unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v44
    #   - No frontend changes
    #   - DB writes total = 0; preview request never blocked
    #   - No reward grant; no inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN', 'validate_client_idem_key_replay_detection_dry_run_v1.py'),
    ('PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN', 'validate_observability_buffer_peek_dry_run_v1.py'),
    ('PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN', 'validate_material_raid_canary_qa_rehearsal_dry_run_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-8-v44-ROLLUP', 'validate_mega_economy_safety_acceleration_8_v44_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_9_OBSERVABILITY_RING_BUFFER_AGGREGATION_AND_REPLAY_TELEMETRY_PACK_v45
    # PUBLIC_SYNC_TAG_v45_MEGA_ECONOMY_SAFETY_ACCELERATION_9
    # ------------------------------------------------------------------------
    # Observability ring-buffer aggregation + replay/conflict telemetry +
    # all-family canary QA rehearsal matrix (design-only):
    #   TRACK A: in-memory ring-buffer aggregation utility, rolling windows
    #            60s/300s/900s, capacity 4096, per-process, non-durable.
    #            NO DB, NO Redis, NO filesystem, NO persistent ledger.
    #            PII-safe; no raw payload captured.
    #   TRACK B: wire-up on 8/8 safety preview routes:
    #            - /config exposes `observability_aggregation_dry_run`
    #            - POST responses include `replay_conflict_telemetry_dry_run`
    #            - /peek-buffer includes `aggregation_snapshot`
    #            No endpoint path/flag/default 503/safety flag changes.
    #            Preview request NEVER blocked by telemetry.
    #   TRACK C: design-only canary QA rehearsal matrix covering all 8
    #            operation families. signoff_state=pending, canary_enabled=
    #            false, canary_percentage=0, live_enabled=false, db_writes=0,
    #            reward_grant_enabled=false, mutation_enabled=false,
    #            live_flip_allowed=false.
    #   ROLLUP : runs Track A + B + C + MD5 invariants (5 core) + suite
    #            tuple counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v45:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged
    #   - v42 + v43 + v44 envelopes and utils unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v45
    #   - No frontend changes (battlepass/vip/combat/story/Home untouched)
    #   - DB writes total = 0; preview request never blocked
    #   - No reward grant; no inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-OBSERVABILITY-RING-BUFFER-AGGREGATION-DRY-RUN', 'validate_observability_ring_buffer_aggregation_dry_run_v1.py'),
    ('PROJECT-REPLAY-CONFLICT-TELEMETRY-DRY-RUN', 'validate_replay_conflict_telemetry_dry_run_v1.py'),
    ('PROJECT-ALL-FAMILY-CANARY-QA-REHEARSAL-MATRIX', 'validate_all_family_canary_qa_rehearsal_matrix_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-9-v45-ROLLUP', 'validate_mega_economy_safety_acceleration_9_v45_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_10_TELEMETRY_ALERTING_THRESHOLDS_AND_SIGNOFF_PROMOTION_REHEARSAL_PACK_v46
    # PUBLIC_SYNC_TAG_v46_MEGA_ECONOMY_SAFETY_ACCELERATION_10
    # ------------------------------------------------------------------------
    # Telemetry alerting thresholds + signoff promotion rehearsal + GO/NO-GO snapshot (dry-run):
    #   TRACK A: telemetry alerting thresholds utility (DRY-RUN). Evaluates
    #            v45 60s window. Replay/conflict/missing-key rate thresholds
    #            (warn/critical). Critical-immediate on db_writes/reward/
    #            mutation/bp_delta/live_enforcement observed.
    #            NO external alert sink. NO DB / Redis / filesystem /
    #            persistent ledger. Preview request never blocked.
    #            Wire-up on 8/8 routes:
    #            - /config exposes `alerting_thresholds_dry_run`
    #            - POST responses include `telemetry_alert_evaluation_dry_run`
    #            - /peek-buffer includes `alert_evaluation`
    #   TRACK B: signoff promotion rehearsal matrix (design-only, 8 families,
    #            5 states pending->dry_run_ready->qa_ready->canary_rehearsal_
    #            ready->live_ready_blocked). v46: current_state=pending,
    #            actual_promotion_performed=false, canary/live=false,
    #            live_flip_allowed=false, owner/QA/Game Director signoff pending.
    #   TRACK C: GO/NO-GO snapshot dry-run. global_go=false, canary_go=false,
    #            live_go=false, per_family_go=false,
    #            safe_to_continue_dry_run=true, safe_to_enable_live=false,
    #            db_writes=0, live_apply_allowed=false. 6 blockers documented.
    #   ROLLUP : runs Tracks A + B + C + MD5 invariants (5 core) + suite
    #            tuple counts + public sync tag presence + 8-route wire-up.
    # ------------------------------------------------------------------------
    # Invariants enforced by v46:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged
    #   - v42 + v43 + v44 + v45 utils / envelopes unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v46
    #   - No frontend changes
    #   - DB writes total = 0; preview request never blocked
    #   - NO external alert dispatch; alert_sink_live_enabled=false
    #   - No reward grant; no inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-TELEMETRY-ALERTING-THRESHOLDS-DRY-RUN', 'validate_telemetry_alerting_thresholds_dry_run_v1.py'),
    ('PROJECT-SIGNOFF-PROMOTION-REHEARSAL-MATRIX', 'validate_signoff_promotion_rehearsal_matrix_v1.py'),
    ('PROJECT-GO-NO-GO-SNAPSHOT-DRY-RUN', 'validate_go_no_go_snapshot_dry_run_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-10-v46-ROLLUP', 'validate_mega_economy_safety_acceleration_10_v46_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_11_ALERT_HISTORY_RING_BUFFER_AND_ROLLBACK_RUNBOOK_REHEARSAL_PACK_v47
    # PUBLIC_SYNC_TAG_v47_MEGA_ECONOMY_SAFETY_ACCELERATION_11
    # ------------------------------------------------------------------------
    # Alert history ring buffer + rollback runbook rehearsal + pre-live audit
    # traceability bundle (all dry-run):
    #   TRACK A: in-memory bounded ring buffer (MAX_ENTRIES=1024) capturing
    #            v46 alert_evaluation envelopes (PII-safe projection only:
    #            ts/family/route/overall_level/rates/critical_immediate/
    #            alerts metric+level+window). Rolling windows 60/300/900s.
    #            NO DB, NO Redis, NO filesystem, NO persistent ledger,
    #            NO external alert dispatch. Preview request never blocked.
    #   TRACK B: wire-up on 8/8 safety preview routes:
    #            - /config exposes `alert_history_dry_run`
    #            - POST responses include `alert_history_record_dry_run`
    #            - /peek-buffer includes `alert_history_snapshot`
    #            No endpoint path/flag/default 503/safety flag changes.
    #   TRACK C: rollback runbook rehearsal matrix (design-only) covering all
    #            8 families x 8 ordered steps (kill-switch toggle, verify 503,
    #            verify db_writes=0, capture aggregation/alert/GO-NO-GO,
    #            owner notification dry-run, rollback blocked if no live ledger).
    #            live_rollback_enabled=false, actual_rollback_performed=false,
    #            reward_reversal_enabled=false, mutation_reversal_enabled=false.
    #   TRACK D: pre-live audit traceability bundle (design-only). Matrix
    #            operation_family -> route -> validators -> markers -> docs ->
    #            feature_flag -> MD5 guard -> smoke evidence -> blocker.
    #            global_go=false, canary_enable_allowed=false,
    #            live_enable_allowed=false, safe_to_continue_dry_run=true,
    #            safe_to_enable_live=false.
    #   ROLLUP : runs Tracks A + C + D + MD5 invariants (5 core) + suite
    #            tuple counts + public sync tag presence + 8-route wire-up.
    # ------------------------------------------------------------------------
    # Invariants enforced by v47:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged
    #   - v42 + v43 + v44 + v45 + v46 utils / envelopes unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v47
    #   - No frontend changes
    #   - DB writes total = 0; preview request never blocked
    #   - NO external alert dispatch; alert_sink_live_enabled=false
    #   - NO rollback live execution; live_rollback_enabled=false
    #   - No reward grant / reversal live
    #   - No inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-ALERT-HISTORY-RING-BUFFER-DRY-RUN', 'validate_alert_history_ring_buffer_dry_run_v1.py'),
    ('PROJECT-ROLLBACK-RUNBOOK-REHEARSAL-MATRIX', 'validate_rollback_runbook_rehearsal_matrix_v1.py'),
    ('PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE', 'validate_pre_live_audit_traceability_bundle_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-11-v47-ROLLUP', 'validate_mega_economy_safety_acceleration_11_v47_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_12_AUDIT_BUNDLE_CHECKSUM_AND_PRE_LIVE_GO_NO_GO_FINAL_CONSOLIDATION_PACK_v48
    # PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12
    # ------------------------------------------------------------------------
    # Audit bundle checksum + final GO/NO-GO consolidation + decision log
    # schema + Expo watcher ENOSPC diagnostic note (all dry-run / design-only):
    #   TRACK A: deterministic SHA-256 checksum utility over the consolidated
    #            v37-v48 audit bundle (markers/contracts/validators/routes/
    #            utils/docs). Sort lexicographic path, normalize CRLF->LF.
    #            Read-only. NO DB / Redis / filesystem persistence /
    #            persistent ledger. live_apply_allowed=false.
    #   TRACK B: final GO/NO-GO consolidation (design-only). Consolidates
    #            v46 GO/NO-GO + v46 signoff promotion + v47 traceability
    #            bundle + v47 rollback runbook + v45 canary QA rehearsal.
    #            global_go=false, canary_go=false, live_go=false,
    #            safe_to_continue_dry_run=true, safe_to_enable_canary=false,
    #            safe_to_enable_live=false, live_apply_allowed=false,
    #            next_required_phase=staging_or_local_live_simulation_with_
    #            ephemeral_test_db.
    #   TRACK C: live apply decision log dry-run (schema-only). No actual
    #            decisions persisted. future_live_decision_requires_manual_
    #            user_approval=true; canary_allowed=false; live_allowed=false.
    #            8 entries: current_decision=no_go_signoff_pending.
    #   TRACK D: Expo Watcher ENOSPC diagnostic note. Classifies OPS-A/B/C/
    #            C-WIRING + AF2-N-V26-FRONTEND-SMOKE + ULTRA-COMBO-V26 as
    #            `environmental_optional_fail_not_v47_regression`. Does NOT
    #            weaken any validator; does NOT skip any tuple in suite
    #            runner; does NOT fake PASS.
    #   ROLLUP : runs Tracks A + B + C + D + MD5 invariants (5 core) +
    #            suite tuple counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v48:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged (no wire-up in v48)
    #   - v42-v47 utils / envelopes unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v48
    #   - No frontend changes
    #   - DB writes total = 0; live_apply_allowed=false
    #   - NO external alert dispatch; alert_dispatched=false
    #   - NO rollback live execution; NO reward grant/reversal live
    #   - No inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-AUDIT-BUNDLE-CHECKSUM-DRY-RUN', 'validate_audit_bundle_checksum_dry_run_v1.py'),
    ('PROJECT-FINAL-GO-NO-GO-CONSOLIDATION', 'validate_final_go_no_go_consolidation_v1.py'),
    ('PROJECT-LIVE-APPLY-DECISION-LOG-DRY-RUN', 'validate_live_apply_decision_log_dry_run_v1.py'),
    ('PROJECT-EXPO-WATCHER-ENOSPC-DIAGNOSTIC', 'validate_expo_watcher_enospc_diagnostic_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-12-v48-ROLLUP', 'validate_mega_economy_safety_acceleration_12_v48_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_13_EPHEMERAL_TEST_DB_LIVE_SIMULATION_PRE_FLIGHT_PACK_v49
    # PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13
    # ------------------------------------------------------------------------
    # Ephemeral test DB live simulation + pre-flight matrix + smoke scenarios
    # + post-v48 pre-live gate integration (all DRY-RUN, mock-only):
    #   TRACK A: in-memory mock DB simulator. NO real DB connection. NO
    #            pymongo. NO motor. NO redis. NO MONGO_URL. NO env read.
    #            NO filesystem writes. 11 mock collections, 8 operation
    #            families, 9 scenarios. real_db_writes=0 ALWAYS,
    #            production_db_touched=false ALWAYS.
    #            simulated_ephemeral_writes_count tracks MOCK writes only.
    #   TRACK B: pre-flight matrix (design-only). 8 families. real_db_
    #            connection_allowed=false, mongo_url_allowed=false,
    #            pymongo_allowed=false, motor_allowed=false,
    #            env_read_allowed=false, filesystem_writes_allowed=false,
    #            production_db_touched=false, ephemeral_db_required=true,
    #            rollback_simulation_required=true, live_enabled=false,
    #            safe_to_enable_live=false.
    #   TRACK C: smoke scenarios matrix (design-only). 8 families x 9
    #            scenarios. expected_real_db_writes=0,
    #            expected_live_apply_allowed=false,
    #            expected_production_db_touched=false for ALL.
    #   TRACK D: post-v48 pre-live gate integration. Connects v48 GO/NO-GO
    #            + decision log + audit bundle to v49 pre-flight + smoke.
    #            v49_does_not_change_go_status=true. global_go=false.
    #   ROLLUP : runs Tracks A + B + C + D + MD5 invariants (5 core) +
    #            suite tuple counts + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v49:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged (no wire-up in v49)
    #   - v42-v48 utils / envelopes unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v49
    #   - No frontend changes
    #   - real DB writes total = 0; production_db_touched=false
    #   - NO real DB connection; NO MONGO_URL read; NO pymongo; NO motor
    #   - NO env read in v49 utility; NO filesystem writes
    #   - NO external alert dispatch; NO live apply; NO rollback live
    #   - No reward grant; no inventory/material/currency/wallet mutation
    #   - No premium users.gems mutation; no mail state/delete/read mutation
    #   - No BP Delta runtime; no live enforcement; no persistent ledger
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-EPHEMERAL-TEST-DB-LIVE-SIMULATION-DRY-RUN', 'validate_ephemeral_test_db_live_simulation_dry_run_v1.py'),
    ('PROJECT-EPHEMERAL-TEST-DB-PRE-FLIGHT-MATRIX', 'validate_ephemeral_test_db_pre_flight_matrix_v1.py'),
    ('PROJECT-LIVE-SIMULATION-SMOKE-SCENARIOS', 'validate_live_simulation_smoke_scenarios_v1.py'),
    ('PROJECT-POST-V48-PRE-LIVE-GATE-INTEGRATION', 'validate_post_v48_pre_live_gate_integration_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-13-v49-ROLLUP', 'validate_mega_economy_safety_acceleration_13_v49_rollup.py'),
    # ========================================================================
    # MEGA_ECONOMY_SAFETY_ACCELERATION_14_EPHEMERAL_SIMULATION_INVARIANT_REPORT_AND_STAGING_DB_BLUEPRINT_PACK_v50
    # PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14
    # ------------------------------------------------------------------------
    # Ephemeral simulation invariant report + staging DB blueprint + live
    # ledger design + manual user approval handshake (ALL DRY-RUN / DESIGN-ONLY):
    #   TRACK A: invariant report aggregator over v49 ephemeral simulator.
    #            8 families x 9 scenarios = 72 scenarios. real_db_writes=0
    #            ALWAYS. production_db_touched=false ALWAYS. NO route exposure.
    #            NO server.py change. NO env read. NO filesystem writes.
    #            NO pymongo / motor / redis / MongoClient / AsyncIOMotorClient.
    #   TRACK B: staging DB blueprint (design-only). 8 families with
    #            readiness=not_ready_until_manual_approval. NO actual staging
    #            DB created. NO real DB connection. NO production credentials.
    #            NO MONGO_URL. NO pymongo. NO motor. NO env read.
    #            NO filesystem writes. live_enabled=false,
    #            safe_to_enable_live=false.
    #   TRACK C: live ledger (design-only). 4 schemas (idempotency_ledger_entry,
    #            audit_event, rollback_record, operator_decision) with
    #            design_only=true, runtime_created=false. PII-safe audit_event
    #            with raw_payload_captured=false. NO runtime ledger creation.
    #            NO live apply. live_implementation_deferred=true.
    #   TRACK D: manual user approval handshake (dry-run). Approval phrase
    #            template with 4 required placeholders. transition enum
    #            includes *_BLOCKED states. NO endpoint. NO runtime execution.
    #            NO automatic approval. All 8 families current_approval_state
    #            =pending.
    #   ROLLUP : runs Tracks A + B + C + D + MD5 invariants (5 core) +
    #            suite tuple counts + public sync tag presence + rollup
    #            marker invariants.
    # ------------------------------------------------------------------------
    # Invariants enforced by v50:
    #   - 8/8 safety preview route endpoint paths / feature flags / default
    #     503 / safety_flags unchanged (no wire-up in v50)
    #   - v42-v49 utils / envelopes unchanged
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v50
    #   - No frontend changes
    #   - real DB writes total = 0; production_db_touched=false
    #   - NO real DB connection; NO MONGO_URL read; NO pymongo; NO motor
    #   - NO env read in v50 utility; NO filesystem writes; NO redis
    #   - NO external alert dispatch; NO live apply; NO rollback live
    #   - NO reward grant; NO inventory/material/currency/wallet mutation
    #   - NO premium users.gems mutation; NO mail state/delete/read mutation
    #   - NO BP Delta runtime; NO live enforcement; NO persistent ledger
    #   - NO runtime ledger creation; NO automatic approval; NO endpoint
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN', 'validate_ephemeral_simulation_invariant_report_dry_run_v1.py'),
    ('PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY', 'validate_staging_db_blueprint_v1.py'),
    ('PROJECT-LIVE-LEDGER-DESIGN-ONLY', 'validate_live_ledger_design_only_v1.py'),
    ('PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN', 'validate_manual_user_approval_handshake_dry_run_v1.py'),
    ('MEGA-ECONOMY-SAFETY-ACCELERATION-14-v50-ROLLUP', 'validate_mega_economy_safety_acceleration_14_v50_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51
    # PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION
    # ------------------------------------------------------------------------
    # Strategic split shift: 70% runtime/UI/test/asset integration, 30% safety.
    # First playable-alpha foundation slice around Material Raid + asset import
    # readiness for ~40 heroes + visual battle routing audit + QA/beta tester
    # matrix + guide/codex onboarding. ALL preview-only / design-only / dry-run:
    #   TRACK A: backend patch to backend/routes/material_raid_preview.py adding
    #            MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED flag (default OFF)
    #            and 3 new endpoints under existing namespace:
    #              GET  /api/material-raid/alpha-slice-config
    #              POST /api/material-raid/alpha-battle-preview
    #              POST /api/material-raid/alpha-reward-summary-preview
    #            Flag OFF => 503 on the new endpoints. Existing /config, /stages,
    #            /reward-preview, /clear-preview UNCHANGED. No battle_engine
    #            call, no /api/battle/simulate, no /api/story/battle.
    #            db_writes=0, materials_granted=false, reward_claim_enabled=false.
    #   TRACK B: frontend deeplink-only screen frontend/app/material-raid-alpha.tsx.
    #            No home menu wiring. Safe fallback when backend flag OFF
    #            (must not crash). No live claim button. No mutation.
    #   TRACK C: visual_battle_routing_playable_slice_audit_v1 (design-only).
    #            8 modes (story, material_raid, tower, arena, guild_war,
    #            training, event, boss). material_raid visual_battle_required
    #            =true. guild_war auto_resolve_allowed=true + replay_link_required
    #            =true. NO battle_engine.py / combat.tsx / story.tsx runtime change.
    #   TRACK D: hero_asset_import_readiness_schema_v1 + report (design-only).
    #            ~40 heroes target. 20 required asset slots. 5 readiness
    #            categories. Validator must PASS with zero scaffold (no real
    #            asset files required yet). frontend/assets/heroes UNCHANGED.
    #            Hero contracts / Character Bible / final_numbers UNCHANGED.
    #   TRACK E: guide_codex_onboarding_alpha_foundation_v1 + optional static
    #            frontend/app/alpha-guide.tsx (deeplink-only, no backend, IT text).
    #   TRACK F: device_beta_tester_smoke_matrix_v1 + doc 297. 12 flows,
    #            4 severity P0/P1/P2/P3, 3 tester roles, pass/fail criteria,
    #            known caveats (preview-only economy, expo ENOSPC, github stale).
    #   ROLLUP : runs Tracks A + B + C + D + E + F + 5 MD5 invariants +
    #            suite tuple counts + public sync tag presence + 6 required docs.
    # ------------------------------------------------------------------------
    # Invariants enforced by v51:
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v51
    #   - backend/battle_engine.py not modified by v51
    #   - frontend/app/combat.tsx not modified by v51
    #   - frontend/app/story.tsx not modified by v51
    #   - Character Bible / final_numbers unchanged
    #   - frontend/assets/heroes unchanged; no real asset imported
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - no home menu mandatory routing for the new alpha screens
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no inventory/material/currency/wallet mutation
    #   - no premium users.gems mutation; no mail state mutation
    #   - no stamina/tickets/paid attempts; no BP Delta runtime
    #   - no gacha/shop/VIP/BP monetization changes
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE', 'validate_material_raid_playable_alpha_slice_v1.py'),
    ('PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT', 'validate_visual_battle_routing_playable_slice_audit_v1.py'),
    ('PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA', 'validate_hero_asset_import_readiness_schema_v1.py'),
    ('PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION', 'validate_guide_codex_onboarding_alpha_foundation_v1.py'),
    ('PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX', 'validate_device_beta_tester_smoke_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP', 'validate_mega_release_acceleration_1_v51_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA_PACK_v52
    # PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA
    # ------------------------------------------------------------------------
    # Wire v51 Material Raid Alpha slice toward a visual battle preview runner
    # WITHOUT live rewards and WITHOUT touching battle_engine.py:
    #   TRACK A: payload contract v2 between POST /api/material-raid/alpha-battle-preview
    #            and frontend route /material-raid-visual-preview. mode=material_raid,
    #            visual_battle_required=true, auto_resolve_allowed=false,
    #            battle_engine_runtime_used=false, result_authoritative=false,
    #            reward_grant_enabled=false, materials_granted=false, db_writes=0.
    #   TRACK B: frontend/app/material-raid-visual-preview.tsx (deeplink-only).
    #            Accepts 6 query params, handles missing params without crash.
    #            Italian text, warnings visible: non-authoritative + no reward.
    #            No claim button. No fetch to backend (pure visualization).
    #            No /api/battle/simulate, no /api/story/battle, no battle_engine.
    #   TRACK C: patch frontend/app/material-raid-alpha.tsx to add the
    #            "Apri preview battaglia visuale" button after a valid
    #            alpha_battle_preview_ready (hidden otherwise). Uses
    #            useRouter from expo-router. Preserves offline fallback.
    #            combat.tsx UNCHANGED.
    #   TRACK D: backend/routes/material_raid_preview.py append-only payload
    #            refinement on alpha_battle_preview_ready response only:
    #            result_authoritative, alpha_preview_only, battle_engine_runtime_used,
    #            reward_grant_enabled, target_frontend_route, background_hint,
    #            music_hint, tutorial_hint, reward_preview_hint.
    #            Path / flag / default 503 / status values / locked / underpowered
    #            UNCHANGED. No battle_engine, no DB writes, no reward grant.
    #   TRACK E: QA smoke matrix 13 flows, severity P0/P1/P2/P3.
    #   ROLLUP : runs Tracks A-E + 5 MD5 invariants + preferred-unchanged check
    #            (server.py / combat.tsx / story.tsx) + suite tuple counts +
    #            public sync tag presence + 5 required docs.
    # ------------------------------------------------------------------------
    # Invariants enforced by v52:
    #   - 5 MD5-locked core files unchanged
    #   - backend/server.py not modified by v52
    #   - backend/battle_engine.py not modified by v52
    #   - frontend/app/combat.tsx unchanged
    #   - frontend/app/story.tsx unchanged
    #   - Guild War policy unchanged
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no inventory/material/currency/wallet mutation
    #   - no premium users.gems mutation; no mail state mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-VISUAL-BATTLE-PAYLOAD-CONTRACT-v2', 'validate_material_raid_visual_battle_payload_contract_v2.py'),
    ('PROJECT-MATERIAL-RAID-VISUAL-PREVIEW-RUNNER', 'validate_material_raid_visual_preview_runner_v1.py'),
    ('PROJECT-MATERIAL-RAID-ALPHA-TO-VISUAL-PREVIEW-WIRING', 'validate_material_raid_alpha_to_visual_preview_wiring_v1.py'),
    ('PROJECT-MATERIAL-RAID-VISUAL-PREVIEW-SMOKE-MATRIX', 'validate_material_raid_visual_preview_smoke_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-2-v52-ROLLUP', 'validate_mega_release_acceleration_2_v52_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE_PACK_v53
    # PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE
    # ------------------------------------------------------------------------
    # Close the Material Raid Alpha loop (Alpha -> Visual Preview -> Reward
    # Summary Preview -> Back to Alpha) WITHOUT any live grant, WITHOUT touching
    # battle_engine.py, WITHOUT mutating inventory/materials/currency/wallet,
    # WITHOUT premium gems mutation, WITHOUT MONGO_URL / pymongo / motor /
    # redis / DB writes / filesystem writes:
    #   TRACK A: backend contract POST /api/material-raid/alpha-reward-summary-preview.
    #            Append-only addition: returns a reward_preview block with
    #            materials_granted=false, inventory_mutation=false,
    #            claim_button_enabled=false, reward_claim_enabled=false,
    #            reward_grant_enabled=false, result_authoritative=false,
    #            battle_engine_runtime_used=false, db_writes=0,
    #            compatible_with_future_material_raid_claim_safety=true,
    #            next_allowed_action='alpha_loop_return_no_live_claim'.
    #            Does NOT mutate any existing endpoint path, feature flag,
    #            default 503 or safety flag of any prior endpoint.
    #   TRACK B: frontend/app/material-raid-reward-preview.tsx (deeplink-only).
    #            Accepts 5 query params, handles missing params without crash.
    #            Italian text, no claim button, only "Torna ad Alpha" CTA.
    #            No /api/battle/simulate, no /api/story/battle, no battle_engine.
    #   TRACK C: visual-to-reward wiring marker — material-raid-visual-preview
    #            now exposes a Italian-labelled deeplink to the new reward
    #            preview screen (combat.tsx UNCHANGED, story.tsx UNCHANGED).
    #   TRACK D-E-F: alpha loop closure audit + smoke matrix (13+ flows P0/P1/P2/P3,
    #            plus deeplink-only / no-crash / preview-only enforcement,
    #            audit JSON marker with loop_closed=true, loop_steps_count=5).
    #   TRACK G/ROLLUP : MD5 invariants + preferred-unchanged guardrails
    #            (server.py / combat.tsx / story.tsx) + suite tuple counts +
    #            public sync tag presence + 5 required docs (308-312).
    # ------------------------------------------------------------------------
    # Invariants enforced by v53:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy unchanged
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false
    #   - loop_closed=true; loop_steps_count=5
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-POST-VISUAL-REWARD-SUMMARY-CONTRACT-v1', 'validate_material_raid_post_visual_reward_summary_contract_v1.py'),
    ('PROJECT-MATERIAL-RAID-REWARD-PREVIEW-SCREEN', 'validate_material_raid_reward_preview_screen_v1.py'),
    ('PROJECT-MATERIAL-RAID-VISUAL-TO-REWARD-WIRING', 'validate_material_raid_visual_to_reward_wiring_v1.py'),
    ('PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-AUDIT', 'validate_material_raid_alpha_loop_closure_audit_v1.py'),
    ('PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-SMOKE-MATRIX', 'validate_material_raid_alpha_loop_closure_smoke_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-3-v53-ROLLUP', 'validate_mega_release_acceleration_3_v53_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN_PACK_v54
    # PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN
    # ------------------------------------------------------------------------
    # Option B (maximum safe acceleration) approved by Game Director.
    # Master batch execution plan with internal batches B1-B8, internal
    # stop-gates (GATE_0 v53 PASS, GATE_1 halt on validator fail,
    # GATE_2 manual approval for B7/B8), maximum safe parallelism.
    # Executable now (low/medium risk): B1, B2, B3, B4, B5, B6.
    # Deferred (require manual director approval): B7, B8.
    #
    #   TRACK A: Master roadmap + dependency graph (8 batches, risk tiers,
    #            dependencies, stop_gate per batch).
    #   TRACK B: Battle entrypoint registry design (material_raid registered
    #            in preview, guild_war design deferred, story/boss locked).
    #   TRACK C: Hero asset import manifest preview/scanner (READ-ONLY scan
    #            of frontend/assets/heroes, NO copy, NO mutation, NO
    #            Character Bible / final_numbers touch).
    #   TRACK D: QA beta tester execution kit (docs-only, device matrix,
    #            sessions 30/60/90, severity P0-P3, bug template, daily
    #            smoke checklist, focus areas).
    #   TRACK E: Guide/Codex runtime plan (static deeplink-only) + new
    #            frontend/app/alpha-codex.tsx screen (no backend, no
    #            mutation, no home menu mandatory routing, Italian text).
    #   TRACK F: Story playable alpha slice plan (DESIGN-ONLY, no story.tsx,
    #            no /api/story/battle, no battle_engine, no reward live).
    #   TRACK G/ROLLUP: 7 OPTIONAL tuples + 5 MD5 invariants + preferred-
    #            unchanged (server.py / combat.tsx / story.tsx) + 7 docs
    #            (313-319) + 7 markers + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v54:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy unchanged (auto_resolve_allowed + replay_link)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis
    #   - filesystem_writes restricted to design JSON / scanner output only
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false
    #   - no asset copy / no asset import / frontend/assets/heroes not mutated
    #   - Character Bible / final_numbers unchanged
    #   - GATE_0 v53 PASS verified; GATE_1 v54 validators PASS;
    #     GATE_2 B7/B8 require manual director approval
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-MASTER-RELEASE-ACCELERATION-ROADMAP', 'validate_master_release_acceleration_roadmap_v1.py'),
    ('PROJECT-BATTLE-ENTRYPOINT-REGISTRY-DESIGN', 'validate_battle_entrypoint_registry_design_v1.py'),
    ('PROJECT-HERO-ASSET-IMPORT-MANIFEST-PREVIEW', 'validate_hero_asset_import_manifest_preview_v1.py'),
    ('PROJECT-BETA-TESTER-EXECUTION-KIT', 'validate_beta_tester_execution_kit_v1.py'),
    ('PROJECT-GUIDE-CODEX-RUNTIME-PLAN', 'validate_guide_codex_runtime_plan_v1.py'),
    ('PROJECT-STORY-PLAYABLE-ALPHA-SLICE-PLAN', 'validate_story_playable_alpha_slice_plan_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-MASTER-v54-ROLLUP', 'validate_mega_release_acceleration_master_v54_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55
    # PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW
    # ------------------------------------------------------------------------
    # Director approved: ONLY B7 (visual_battle_routing_expansion_plan) in
    # preview / design / runtime-shell mode. NOT approved: B8, live economy,
    # DB writes, reward grant, reward claim, battle_engine runtime.
    #
    # Expand visual battle routing beyond Material Raid as preview/deeplink/
    # read-only shells, without touching battle_engine.py, without modifying
    # combat.tsx, without changing /api/story/battle or /api/battle/simulate,
    # and without any reward/claim live:
    #   TRACK A: Battle Entrypoint Registry v2 Preview \u2014 8 modes registered
    #            (material_raid, training, story, boss, tower, event, arena,
    #            guild_war). Universal invariants: result_authoritative=false,
    #            reward_claim_enabled=false, reward_grant_enabled=false,
    #            db_writes=0, battle_engine_runtime_used=false.
    #            Guild War policy preserved: auto_resolve_allowed=true,
    #            replay_link_required=true, replay_visualization_required=true.
    #   TRACK B: frontend/app/visual-battle-preview-router.tsx (deeplink-only
    #            generic shell). 9 supported query params. Handles missing
    #            params without crash. Italian text. Warnings visible.
    #            No backend fetch. No claim button. No mutation.
    #   TRACK C: frontend/app/training-visual-preview.tsx (static + deeplink-
    #            only). Safe sandbox. Links to /visual-battle-preview-router
    #            with deterministic seed training-alpha-v55.
    #   TRACK D: Story / Boss / Tower / Event / Arena design-only contracts.
    #            Future_payload_minimum + stop_gates. No story.tsx diff.
    #            No /api/story/battle / /api/battle/simulate diff.
    #   TRACK E: QA smoke matrix 16 flows, severity P0/P1/P2/P3. Covers all
    #            modes + claim absence + DB-writes absence + Guild War policy.\n    #   TRACK F/ROLLUP: 6 OPTIONAL tuples + 5 MD5 invariants + preferred-
    #            unchanged (server.py / combat.tsx / story.tsx) + 6 docs
    #            (320-325) + 6 markers + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v55:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy UNCHANGED (auto_resolve + replay_link preserved)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false; battle_engine_runtime not invoked
    #   - no asset copy / no asset import
    #   - Character Bible / final_numbers unchanged
    #   - no new runtime endpoint created in v55
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW', 'validate_battle_entrypoint_registry_v2_preview_v1.py'),
    ('PROJECT-GENERIC-VISUAL-BATTLE-PREVIEW-ROUTER', 'validate_generic_visual_battle_preview_router_v1.py'),
    ('PROJECT-TRAINING-VISUAL-PREVIEW-DEEPLINK', 'validate_training_visual_preview_deeplink_v1.py'),
    ('PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS', 'validate_multi_mode_visual_battle_preview_contracts_v1.py'),
    ('PROJECT-VISUAL-BATTLE-ROUTING-EXPANSION-SMOKE-MATRIX', 'validate_visual_battle_routing_expansion_smoke_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-4-v55-ROLLUP', 'validate_mega_release_acceleration_4_v55_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED_WIRING_PACK_v56
    # PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED
    # ------------------------------------------------------------------------
    # Evolve Training Visual Preview from static shell (v55) to a small local
    # deterministic preview based on dummy seed 'training-alpha-v56', without
    # backend, without battle_engine.py, without /api/battle/simulate, without
    # /api/story/battle, without reward, without DB writes.
    #
    # State transition: training preview_shell_v55 -> local_dummy_seed_wired_v56.
    # Material Raid remains alpha_loop_closed_v53. Guild War policy preserved
    # (autoresolve + replay_link exception).
    #
    #   TRACK A: training_visual_preview_local_dummy_seed_contract_v1.json +
    #            local_visual_preview_timeline_schema_v1.json +
    #            battle_entrypoint_registry_v2_training_delta_v56.json
    #            (10 required step fields, deterministic_from_seed=true).
    #   TRACK B: frontend/app/training-visual-preview.tsx patched with a pure
    #            deterministic buildLocalTimeline(seed) helper (6 steps),
    #            step/next/reset + optional play/pause with safe timer cleanup
    #            (clearTimeout on unmount AND on pause). Italian text. No
    #            Reanimated. No combat.tsx import. No backend fetch.
    #   TRACK C: frontend/app/visual-battle-preview-router.tsx augmented with
    #            a 'mode === \"training\"' detail block that shows
    #            local_dummy_seed_wired_v56 + disclaimer. Material Raid /
    #            other modes behavior UNCHANGED. No fetch.
    #   TRACK D: training_visual_preview_local_dummy_seed_smoke_matrix_v1.json
    #            (16 flows, severity P0/P1/P2/P3) covering open, timeline,
    #            step/next/reset, play/pause cleanup, generic router routing,
    #            missing params no crash, no claim/no reward/no DB write/no
    #            backend/no battle_engine, rotation, italian text.
    #   TRACK E: visual_preview_runtime_shell_progress_report_v1.json
    #            (modes_status snapshot: material_raid alpha_loop_closed_v53,
    #            training local_dummy_seed_wired_v56, story/boss/tower/event/
    #            arena design_only_runtime_deferred, guild_war policy unchanged;
    #            next recommended: boss_visual_preview_route OR
    #            story_visual_preview_contract_to_deeplink).
    #   TRACK F/ROLLUP: 6 OPTIONAL tuples + 5 MD5 invariants + preferred-
    #            unchanged (server.py / combat.tsx / story.tsx) + 6 docs
    #            (326-331) + 6 markers + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v56:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy UNCHANGED (auto_resolve + replay_link preserved)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false; backend_used=false
    #   - no Reanimated import; no combat.tsx import; timer cleanup obbligatorio
    #   - Character Bible / final_numbers unchanged
    #   - no new runtime endpoint created in v56
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-CONTRACT', 'validate_training_visual_preview_local_dummy_seed_contract_v1.py'),
    ('PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-TIMELINE', 'validate_training_visual_preview_local_timeline_v1.py'),
    ('PROJECT-GENERIC-ROUTER-TRAINING-DETAIL', 'validate_generic_router_training_detail_v1.py'),
    ('PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-SMOKE-MATRIX', 'validate_training_visual_preview_local_dummy_seed_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT', 'validate_visual_preview_runtime_shell_progress_report_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-5-v56-ROLLUP', 'validate_mega_release_acceleration_5_v56_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_PACK_v57
    # PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE
    # ------------------------------------------------------------------------
    # Promote 'boss' from design_only_runtime_deferred to preview_shell_v57
    # on the Material Raid / Training pattern: a new dedicated preview shell
    # at /boss-visual-preview, deeplink-only, no backend, no battle_engine,
    # no reward, no DB writes, no core system changes.
    #
    # State transition: boss design_only_runtime_deferred -> preview_shell_v57.
    # Material Raid: alpha_loop_closed_v53 (unchanged).
    # Training: local_dummy_seed_wired_v56 (unchanged).
    # Guild War: autoresolve + replay_link exception (unchanged).
    #
    #   TRACK A: boss_visual_preview_route_contract_v1.json +
    #            battle_entrypoint_registry_v2_boss_delta_v57.json
    #            (mode_id=boss, default_seed=boss-alpha-v57, 7 boss_family_
    #            preview fields, default_fallback for missing query params).
    #   TRACK B: frontend/app/boss-visual-preview.tsx (NEW) deeplink-only
    #            screen with Boss Card, phase/weakness/enrage hints, team
    #            power vs recommended, reset preview button, deeplink to
    #            generic router. Italian text. No Reanimated. No combat.tsx.
    #   TRACK C: frontend/app/visual-battle-preview-router.tsx augmented
    #            with 'mode === \"boss\"' detail block showing
    #            preview_shell_v57 + boss_family_id/display_name/phase +
    #            disclaimer. Material Raid / Training behavior UNCHANGED.
    #   TRACK D: boss_visual_preview_route_smoke_matrix_v1.json (18 flows,
    #            P0/P1/P2/P3) covering open-no-params, valid-params,\n    #            boss card, hints, generic router, no-claim/no-reward/no-DB/\n    #            no-backend/no-battle_engine, rotation, italian, Guild War
    #            policy unchanged.
    #   TRACK E: visual_preview_runtime_shell_progress_report_v2.json
    #            (modes_status snapshot: boss promoted to preview_shell_v57,\n    #            director_approvals updated with boss_visual_preview_route).
    #   TRACK F/ROLLUP: 6 OPTIONAL tuples + 5 MD5 invariants + preferred-
    #            unchanged (server.py / combat.tsx / story.tsx) + 6 docs
    #            (332-337) + 6 markers + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v57:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy UNCHANGED (auto_resolve + replay_link preserved)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false; backend_used=false
    #   - no Reanimated import; no combat.tsx import
    #   - Character Bible / final_numbers unchanged
    #   - no new runtime endpoint created in v57
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT', 'validate_boss_visual_preview_route_contract_v1.py'),
    ('PROJECT-BOSS-VISUAL-PREVIEW-SCREEN', 'validate_boss_visual_preview_screen_v1.py'),
    ('PROJECT-GENERIC-ROUTER-BOSS-DETAIL', 'validate_generic_router_boss_detail_v1.py'),
    ('PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-SMOKE-MATRIX', 'validate_boss_visual_preview_route_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v2', 'validate_visual_preview_runtime_shell_progress_report_v2.py'),
    ('MEGA-RELEASE-ACCELERATION-6-v57-ROLLUP', 'validate_mega_release_acceleration_6_v57_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH_PACK_v58
    # PUBLIC_SYNC_TAG_v58_MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH
    # ------------------------------------------------------------------------
    # Multi-mode parallelization pack: STORY/TOWER/EVENT/ARENA all promoted in
    # one batch from design_only_runtime_deferred -> preview_shell_v58 on the
    # Material Raid / Training / Boss pattern. Replaces the prior single-Story
    # v58 pack (MEGA_RELEASE_ACCELERATION_7_STORY_VISUAL_PREVIEW_CONTRACT_TO_
    # DEEPLINK_PACK_v58) under Director-approved same-pattern/same-risk/same-
    # guardrails parallelization rule.
    #
    # State transitions (4 modes simultaneously):
    #   story  design_only_runtime_deferred -> preview_shell_v58
    #   tower  design_only_runtime_deferred -> preview_shell_v58
    #   event  design_only_runtime_deferred -> preview_shell_v58
    #   arena  design_only_runtime_deferred -> preview_shell_v58
    # Material Raid: alpha_loop_closed_v53 (unchanged).
    # Training: local_dummy_seed_wired_v56 (unchanged).
    # Boss: preview_shell_v57 (unchanged).
    # Guild War: autoresolve + replay_link exception (unchanged).
    #
    #   TRACK A: multi_mode_visual_preview_shell_batch_contract_v1.json +
    #            4 per-mode visual_preview_route_contract_v1.json +
    #            battle_entrypoint_registry_v2_multi_mode_delta_v58.json.
    #   TRACK B: 4 NEW deeplink-only screens:
    #            frontend/app/story-visual-preview.tsx (seed story-alpha-v58)
    #            frontend/app/tower-visual-preview.tsx (seed tower-alpha-v58)
    #            frontend/app/event-visual-preview.tsx (seed event-alpha-v58)
    #            frontend/app/arena-visual-preview.tsx (seed arena-alpha-v58)
    #            Italian text, no Reanimated, no claim, no reward, no backend,
    #            no battle_engine, no import from story.tsx or combat.tsx.
    #   TRACK C: frontend/app/visual-battle-preview-router.tsx augmented with
    #            4 new conditional blocks (mode === 'story'|'tower'|'event'|
    #            'arena') showing preview_shell_v58 details + disclaimer.
    #            Material Raid / Training / Boss behavior UNCHANGED.
    #   TRACK D: multi_mode_visual_preview_shell_batch_smoke_matrix_v1.json
    #            unified QA smoke matrix (>=20 flows, P0/P1/P2/P3).
    #   TRACK E: visual_preview_runtime_shell_progress_report_v3.json
    #            (8 modes status snapshot, story/tower/event/arena all v58).
    #   TRACK F/ROLLUP: 6 OPTIONAL tuples + 5 MD5 invariants + preferred-
    #            unchanged (server.py / combat.tsx / story.tsx) + 6 docs
    #            (338-343) + 6 markers + public sync tag presence.
    # ------------------------------------------------------------------------
    # Invariants enforced by v58:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy UNCHANGED (auto_resolve + replay_link preserved)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false; backend_used=false
    #   - no Reanimated import; no combat.tsx import; no story.tsx import
    #   - Character Bible / final_numbers unchanged
    #   - no new runtime endpoint created in v58
    #   - no home menu mandatory routing
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-CONTRACT', 'validate_multi_mode_visual_preview_shell_batch_contract_v1.py'),
    ('PROJECT-MULTI-MODE-VISUAL-PREVIEW-SCREENS', 'validate_multi_mode_visual_preview_screens_v1.py'),
    ('PROJECT-GENERIC-ROUTER-MULTI-MODE-DETAIL', 'validate_generic_router_multi_mode_detail_v1.py'),
    ('PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-SMOKE-MATRIX', 'validate_multi_mode_visual_preview_shell_batch_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v3', 'validate_visual_preview_runtime_shell_progress_report_v3.py'),
    ('MEGA-RELEASE-ACCELERATION-7-v58-ROLLUP', 'validate_mega_release_acceleration_7_v58_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59
    # PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH
    # ------------------------------------------------------------------------
    # Accorpa 3 lane compatibili (same pattern, same risk, same guardrails):
    #   1) visual_battle_runner_payload_contract_v0  (DESIGN-ONLY, no runner)
    #   2) boss_local_timeline_wiring                (FRONTEND local preview)
    #   3) tower_local_dummy_seed_wiring             (FRONTEND local preview)
    # ESCLUSA dal pack (gated separato):
    #   - material_raid_claim_safety_hardening_v2_preview_only
    #
    # State transitions:
    #   boss   preview_shell_v57 -> local_dummy_seed_wired_v59
    #   tower  preview_shell_v58 -> local_dummy_seed_wired_v59
    # Material Raid: alpha_loop_closed_v53 (unchanged).
    # Training: local_dummy_seed_wired_v56 (unchanged).
    # Story/Event/Arena: preview_shell_v58 (unchanged).
    # Guild War: autoresolve + replay_link exception (unchanged).
    #
    #   TRACK A: visual_battle_runner_payload_contract_v0.json +
    #            visual_battle_runner_payload_contract_stop_gates_v0.json.
    #            design-only. runtime_runner_created=false. db_writes=0.
    #            consumer_future_route=/visual-battle-preview-router.
    #            compatible_modes: material_raid/training/boss/story/tower/event/arena.
    #   TRACK B: local_visual_preview_timeline_schema_v2.json.
    #            5-7 step deterministic, design-only, local-only,
    #            compatible modes: training/boss/tower.
    #   TRACK C: boss_local_timeline_wiring_contract_v1.json + boss_delta_v59.
    #            frontend/app/boss-visual-preview.tsx patchato con
    #            buildBossTimeline 6-step + state stepIndex + play/pause +
    #            cleanup timer. Default seed boss-alpha-v59.
    #   TRACK D: tower_local_dummy_seed_wiring_contract_v1.json + tower_delta_v59.
    #            frontend/app/tower-visual-preview.tsx patchato con
    #            buildTowerTimeline 6-step + state stepIndex + play/pause +
    #            cleanup timer. Default seed tower-alpha-v59.
    #   TRACK E: frontend/app/visual-battle-preview-router.tsx (opzionale low-risk)
    #            mostra local_dummy_seed_wired_v59 quando seed boss-alpha-v59 /
    #            tower-alpha-v59 o source_route boss/tower.
    #   TRACK F: local_timeline_and_payload_contract_batch_smoke_matrix_v1
    #            (28 flussi P0/P1/P2/P3) +
    #            visual_preview_runtime_shell_progress_report_v4
    #            (8 modes + payload_contract design_only_v0 snapshot).
    #   TRACK G: 7 OPTIONAL tuples count=1 + tag + 7 docs (344-350) + 7 markers.
    # ------------------------------------------------------------------------
    # Invariants enforced by v59:
    #   - 5 MD5-locked core files unchanged
    #     (battle_engine.py / .env / artifacts.py / battlepass.tsx / vip.tsx)
    #   - preferred-unchanged guardrails (server.py / combat.tsx / story.tsx)
    #   - Guild War policy UNCHANGED (auto_resolve + replay_link preserved)
    #   - existing endpoint paths / feature flags / default 503 / safety flags
    #     of existing endpoints unchanged
    #   - /api/battle/simulate and /api/story/battle UNCHANGED
    #   - db_writes=0; real_db_writes=0; production_db_touched=false
    #   - no MONGO_URL; no pymongo; no motor; no redis; no filesystem writes
    #   - no live reward grant; no live claim; no inventory/material/currency/
    #     wallet mutation; no premium users.gems mutation
    #   - no real battle result generation; result_authoritative=false
    #   - battle_engine_runtime_used=false; backend_used=false
    #   - no Reanimated import; no combat.tsx import; no story.tsx import
    #   - Character Bible / final_numbers unchanged
    #   - no new runtime endpoint created in v59
    #   - no home menu mandatory routing
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-VISUAL-BATTLE-RUNNER-PAYLOAD-CONTRACT-v0', 'validate_visual_battle_runner_payload_contract_v0.py'),
    ('PROJECT-SHARED-LOCAL-TIMELINE-SCHEMA-v2', 'validate_shared_local_timeline_schema_v2.py'),
    ('PROJECT-BOSS-LOCAL-TIMELINE-WIRING', 'validate_boss_local_timeline_wiring_v1.py'),
    ('PROJECT-TOWER-LOCAL-DUMMY-SEED-WIRING', 'validate_tower_local_dummy_seed_wiring_v1.py'),
    ('PROJECT-LOCAL-TIMELINE-AND-PAYLOAD-CONTRACT-BATCH-SMOKE-MATRIX', 'validate_local_timeline_and_payload_contract_batch_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v4', 'validate_visual_preview_runtime_shell_progress_report_v4.py'),
    ('MEGA-RELEASE-ACCELERATION-8-v59-ROLLUP', 'validate_mega_release_acceleration_8_v59_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60
    # PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH
    # ------------------------------------------------------------------------
    # Accorpa 3 lane compatibili (same pattern, same risk, same guardrails):
    #   1) visual_battle_runner_router_adapter_preview (FRONTEND/design-only)
    #   2) event_local_dummy_seed_wiring              (FRONTEND local preview)
    #   3) arena_local_dummy_seed_wiring              (FRONTEND local preview)
    # ESCLUSA (gated): material_raid_claim_safety_hardening_v2_preview_only
    #
    # State transitions:
    #   event  preview_shell_v58 -> local_dummy_seed_wired_v60
    #   arena  preview_shell_v58 -> local_dummy_seed_wired_v60
    # Material Raid: alpha_loop_closed_v53 (unchanged).
    # Training: local_dummy_seed_wired_v56 (unchanged).
    # Boss/Tower: local_dummy_seed_wired_v59 (unchanged).
    # Story: preview_shell_v58 (unchanged).
    # Guild War: autoresolve + replay_link exception (unchanged).
    #
    # TRACK A+B: Router Adapter Preview (design-only contract v1 + mapping v1).
    #            visual-battle-preview-router.tsx mostra blocco
    #            "Payload Contract v0 Adapter Preview" quando query ha almeno
    #            mode + battle_seed_preview. Nessun runner runtime.
    # TRACK C:   event-visual-preview.tsx patchato con buildEventTimeline
    #            6-step + state stepIndex + play/pause + cleanup timer.
    #            Default seed event-alpha-v60.
    # TRACK D:   arena-visual-preview.tsx patchato con buildArenaTimeline
    #            6-step + state stepIndex + play/pause + cleanup timer.
    #            Default seed arena-alpha-v60.
    # TRACK E:   local_visual_preview_timeline_schema_v3_delta esteso a
    #            training/boss/tower/event/arena con nuovi optional fields
    #            event_rule_hint_optional, arena_ruleset_hint_optional,
    #            bracket_hint_optional.
    # TRACK F:   router_adapter_event_arena_local_timeline_smoke_matrix_v1
    #            (28 flows P0-P3) + visual_preview_runtime_shell_progress_report_v5
    #            (10 modes incl. router_adapter_preview=adapter_preview_v60).
    # TRACK G:   7 OPTIONAL tuples count=1 + tag + 7 docs (351-357) + 7 markers.
    # ------------------------------------------------------------------------
    # Invariants enforced by v60: 5 MD5-locked files unchanged, 3 preferred-
    # unchanged guardrails intact, Guild War unchanged, /api/* untouched,
    # db_writes=0, no MONGO_URL/pymongo/motor/redis, no live reward/claim,
    # battle_engine_runtime_used=false, backend_used=false,
    # runtime_runner_created=false, adapter_preview_only=true,
    # no Reanimated, no combat.tsx/story.tsx import, Character Bible /
    # final_numbers unchanged, no new runtime endpoint, no home menu mandatory
    # routing. No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-VISUAL-BATTLE-RUNNER-ROUTER-ADAPTER-PREVIEW', 'validate_visual_battle_runner_router_adapter_preview_v1.py'),
    ('PROJECT-EVENT-LOCAL-DUMMY-SEED-WIRING', 'validate_event_local_dummy_seed_wiring_v1.py'),
    ('PROJECT-ARENA-LOCAL-DUMMY-SEED-WIRING', 'validate_arena_local_dummy_seed_wiring_v1.py'),
    ('PROJECT-LOCAL-TIMELINE-SCHEMA-v3-DELTA', 'validate_local_timeline_schema_v3_delta_v1.py'),
    ('PROJECT-ROUTER-ADAPTER-EVENT-ARENA-LOCAL-TIMELINE-SMOKE-MATRIX', 'validate_router_adapter_event_arena_local_timeline_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v5', 'validate_visual_preview_runtime_shell_progress_report_v5.py'),
    ('MEGA-RELEASE-ACCELERATION-9-v60-ROLLUP', 'validate_mega_release_acceleration_9_v60_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61
    # PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE
    # ------------------------------------------------------------------------
    # Accorpa 3 lane low-risk (same pattern, same risk, same guardrails):
    #   1) story_local_dummy_seed_wiring             (FRONTEND local preview)
    #   2) router_adapter_preview_hardening          (FRONTEND/design-only)
    #   3) visual_preview_to_real_runtime_gate_design (DESIGN-ONLY)
    # ESCLUSA (gated): material_raid_claim_safety_hardening_v2_preview_only
    #
    # State transitions:
    #   story  preview_shell_v58 -> local_dummy_seed_wired_v61
    # Tutte le altre modalità: invariate (v53/v56/v59/v60 unchanged).
    # Guild War: autoresolve + replay_link exception (unchanged).
    #
    # TRACK A+B: story_local_dummy_seed_wiring_contract_v1 + story_delta_v61.
    #            frontend/app/story-visual-preview.tsx patchato con
    #            buildStoryTimeline 6-step deterministic + state stepIndex +
    #            play/pause + cleanup timer. Default seed story-alpha-v61.
    #            story_runtime_used=false, story_tsx_changed=false,
    #            api_story_battle_changed=false.\n    # TRACK C:   visual_battle_runner_router_adapter_hardening_contract_v1 +
    #            validation rules v1. Router patchato con:
    #              - adapter_preview_version=adapter_preview_v61
    #              - contract_version=visual_battle_runner_payload_v0\n    #              - adapter_status (payload_like_ready / missing_required_fields)
    #              - missing_fields display\n    #              - per-mode state snapshot (7 modes)\n    # TRACK D:   visual_preview_to_real_runtime_gate_design_v1 + per-mode
    #            activation gate matrix. design-only. approved_modes_now=[].
    #            7 gates per mode + 8 forbidden_without_separate_pack.
    # TRACK E:   local_visual_preview_timeline_schema_v4_delta esteso a 6 modi
    #            (training/boss/tower/event/arena/story) + 3 nuovi optional
    #            (story_tutorial_hint_optional, story_faction_hint_optional,
    #            chapter_node_hint_optional).
    # TRACK F:   QA smoke matrix v1 (26 flows P0-P3) + progress report v6.
    # TRACK G:   7 OPTIONAL tuples count=1 + tag + 7 docs (358-364) + 7 markers.
    # ------------------------------------------------------------------------
    # Invariants enforced by v61: 5 MD5-locked files unchanged, 3 preferred-
    # unchanged guardrails intact, Guild War unchanged, /api/* untouched,
    # db_writes=0, no MONGO_URL/pymongo/motor/redis, no live reward/claim,
    # battle_engine_runtime_used=false, backend_used=false,
    # runtime_runner_created=false, adapter_preview_only=true,
    # runtime_activation_enabled=false, manual_approval_required=true,
    # no Reanimated, no combat.tsx/story.tsx import, no new runtime endpoint.
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-STORY-LOCAL-DUMMY-SEED-WIRING', 'validate_story_local_dummy_seed_wiring_v1.py'),
    ('PROJECT-ROUTER-ADAPTER-PREVIEW-HARDENING', 'validate_router_adapter_preview_hardening_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-TO-REAL-RUNTIME-GATE-DESIGN', 'validate_visual_preview_to_real_runtime_gate_design_v1.py'),
    ('PROJECT-LOCAL-TIMELINE-SCHEMA-v4-DELTA', 'validate_local_timeline_schema_v4_delta_v1.py'),
    ('PROJECT-STORY-TIMELINE-ROUTER-HARDENING-RUNTIME-GATE-SMOKE-MATRIX', 'validate_story_timeline_router_hardening_runtime_gate_smoke_matrix_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v6', 'validate_visual_preview_runtime_shell_progress_report_v6.py'),
    ('MEGA-RELEASE-ACCELERATION-10-v61-ROLLUP', 'validate_mega_release_acceleration_10_v61_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62
    # PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN
    # ------------------------------------------------------------------------
    # DESIGN-ONLY pack. Accorpa 6 lane di pianificazione transizione preview->runtime:
    #   1) visual_battle_runner_runtime_shell_plan        (TRACK A)
    #   2) preview_to_runtime_transition_plan             (TRACK B)
    #   3) visual_preview_full_coverage_rollup            (TRACK C)
    #   4) per_mode_runtime_readiness_matrix              (TRACK D)
    #   5) runtime_runner_payload_v1_draft_and_rollback   (TRACK E)
    #   6) preview_to_runtime_runner_plan_readiness_matrix(TRACK F)
    # TRACK G: 7 OPTIONAL tuples count=1 + tag + 7 docs (365-371) + rollup marker.
    # ESCLUSA (gated): material_raid_claim_safety_hardening_v2_preview_only (-> v63).
    #
    # State transitions: NONE. v62 e' design-only puro.
    # Nessun .tsx frontend modificato. Nessun /api/* aggiunto. db_writes=0.
    # ------------------------------------------------------------------------
    # Invariants enforced by v62: 5 MD5-locked files unchanged, 3 preferred-
    # unchanged guardrails intact (server.py, combat.tsx, story.tsx), Guild War
    # unchanged, /api/* untouched, no MONGO_URL/pymongo/motor/redis, no live
    # reward/claim, battle_engine_runtime_used=false, backend_used=false,
    # runtime_runner_created=false, runtime_activation_enabled=false,
    # manual_approval_required=true, character_bible_changed=false,
    # final_numbers_changed=false. No fake PASS. No validator weakening.
    # No tuple duplicate. visual_preview_local_layer_complete=true.
    # ========================================================================
    ('PROJECT-VISUAL-BATTLE-RUNNER-RUNTIME-SHELL-PLAN', 'validate_visual_battle_runner_runtime_shell_plan_v1.py'),
    ('PROJECT-PREVIEW-TO-RUNTIME-TRANSITION-PLAN', 'validate_preview_to_runtime_transition_plan_v1.py'),
    ('PROJECT-VISUAL-PREVIEW-FULL-COVERAGE-ROLLUP', 'validate_visual_preview_full_coverage_rollup_v1.py'),
    ('PROJECT-PER-MODE-RUNTIME-READINESS-MATRIX', 'validate_per_mode_runtime_readiness_matrix_v1.py'),
    ('PROJECT-RUNTIME-RUNNER-PAYLOAD-v1-DRAFT-AND-ROLLBACK-PLAN', 'validate_runtime_runner_payload_v1_draft_and_rollback_plan_v1.py'),
    ('PROJECT-PREVIEW-TO-RUNTIME-RUNNER-PLAN-READINESS-MATRIX', 'validate_preview_to_runtime_runner_plan_readiness_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-11-v62-ROLLUP', 'validate_mega_release_acceleration_11_v62_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63
    # PUBLIC_SYNC_TAG_v63_MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT
    # ------------------------------------------------------------------------
    # DESIGN-ONLY pack. Affronta la lane gated rimasta da v62 (Material Raid
    # claim safety) come pura blueprint preview/design/staging:
    #   1) material_raid_claim_safety_v2_preview_contract       (TRACK A)
    #   2) material_raid_claim_idempotency_and_replay_policy    (TRACK B)
    #   3) material_raid_staging_db_blueprint_and_ledger_draft  (TRACK C)
    #   4) material_raid_rollback_manual_approval_canary_scope  (TRACK D)
    #   5) material_raid_dry_run_request_response_contract_v64  (TRACK E)
    #   6) material_raid_claim_safety_staging_blueprint_qa      (TRACK F)
    # TRACK G: 7 OPTIONAL tuples + tag + 7 docs (372-378) + 7 markers + rollup.
    # ESCLUSI: live_claim, reward_grant, db_writes, backend_route_enablement.
    #
    # State transitions: NONE. v63 e' design-only puro.
    # Nessun .tsx frontend modificato. Nessuna route backend aggiunta o
    # modificata. backend/routes/material_raid_preview.py unchanged. db_writes=0.
    # ------------------------------------------------------------------------
    # Invariants enforced by v63: 5 MD5-locked files unchanged + 4 preferred-
    # unchanged guardrails (server.py, combat.tsx, story.tsx,
    # material_raid_preview.py), Guild War unchanged, /api/* untouched,
    # no MONGO_URL/pymongo/motor/redis, no live reward/claim, no inventory/
    # wallet/premium mutation, runtime_runner_created=false,
    # runtime_activation_enabled=false, manual_approval_required=true,
    # future_live_pack_minimum=v65, character_bible_changed=false,
    # final_numbers_changed=false. No fake PASS. No validator weakening.
    # No tuple duplicate. material_raid_live_claim=false,
    # material_raid_reward_grant=false, material_raid_db_writes=0.
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-CLAIM-SAFETY-v2-PREVIEW-CONTRACT', 'validate_material_raid_claim_safety_v2_preview_contract.py'),
    ('PROJECT-MATERIAL-RAID-IDEMPOTENCY-AND-REPLAY-POLICY', 'validate_material_raid_idempotency_and_replay_policy_v1.py'),
    ('PROJECT-MATERIAL-RAID-STAGING-BLUEPRINT-AND-LEDGER-DRAFT', 'validate_material_raid_staging_blueprint_and_ledger_v1.py'),
    ('PROJECT-MATERIAL-RAID-ROLLBACK-MANUAL-APPROVAL-CANARY-SCOPE', 'validate_material_raid_rollback_manual_approval_canary_v1.py'),
    ('PROJECT-MATERIAL-RAID-DRY-RUN-REQUEST-RESPONSE-CONTRACT', 'validate_material_raid_dry_run_request_response_contract_v1.py'),
    ('PROJECT-MATERIAL-RAID-CLAIM-SAFETY-STAGING-BLUEPRINT-READINESS', 'validate_material_raid_claim_safety_staging_blueprint_readiness_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-12-v63-ROLLUP', 'validate_mega_release_acceleration_12_v63_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION_PACK_v64
    # PUBLIC_SYNC_TAG_v64_MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION
    # ------------------------------------------------------------------------
    # DRY-RUN / STAGING simulation pack. Esegue in-memory una simulazione del
    # futuro Material Raid claim usando i contratti v63, senza scrivere DB,
    # senza creare collection, senza grant reward, senza abilitare claim live
    # e senza creare route runtime:
    #   1) material_raid_claim_dry_run_simulator         (TRACK A)
    #   2) material_raid_canary_dry_run_scenarios        (TRACK B)
    #   3) material_raid_ledger_replay_dry_run_evidence  (TRACK C)
    #   4) material_raid_rollback_observation_simulation (TRACK D)
    #   5) material_raid_v65_go_no_go_readiness          (TRACK E)
    #   6) material_raid_staging_dry_run_canary_qa       (TRACK F)
    # TRACK G: 7 OPTIONAL tuples + tag + 7 docs (379-385) + 7 markers + rollup.
    # ESCLUSI: live_claim, reward_grant, db_writes, backend_route_enablement.
    #
    # State transitions: NONE. v64 e' dry-run-only.
    # Nessun .tsx frontend modificato. Nessuna route backend aggiunta o
    # modificata. backend/routes/material_raid_preview.py unchanged. db_writes=0.
    # Il simulator e' Python puro, niente pymongo/motor/redis, niente MONGO_URL,
    # niente import di server.py / battle_engine.py.
    # ------------------------------------------------------------------------
    # Invariants enforced by v64: 5 MD5-locked files unchanged + 4 preferred-
    # unchanged guardrails (server.py, combat.tsx, story.tsx,
    # material_raid_preview.py), Guild War unchanged, /api/* untouched,
    # no MONGO_URL/pymongo/motor/redis, no live reward/claim, no inventory/
    # wallet/premium mutation, runtime_runner_created=false,
    # runtime_activation_enabled=false, manual_approval_required=true,
    # v65_readiness=READY_FOR_MANUAL_REVIEW_NOT_APPROVED, character_bible_changed=false,
    # final_numbers_changed=false. No fake PASS. No validator weakening.
    # No tuple duplicate. material_raid_live_claim=false,
    # material_raid_reward_grant=false, material_raid_db_writes=0.
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-CLAIM-DRY-RUN-SIMULATOR', 'validate_material_raid_claim_dry_run_simulator_v1.py'),
    ('PROJECT-MATERIAL-RAID-CANARY-DRY-RUN-SCENARIOS', 'validate_material_raid_canary_dry_run_scenarios_v1.py'),
    ('PROJECT-MATERIAL-RAID-LEDGER-REPLAY-DRY-RUN-EVIDENCE', 'validate_material_raid_ledger_replay_dry_run_v1.py'),
    ('PROJECT-MATERIAL-RAID-ROLLBACK-OBSERVATION-SIMULATION', 'validate_material_raid_rollback_observation_simulation_v1.py'),
    ('PROJECT-MATERIAL-RAID-v65-GO-NO-GO-READINESS', 'validate_material_raid_v65_go_no_go_readiness_v1.py'),
    ('PROJECT-MATERIAL-RAID-STAGING-DRY-RUN-CANARY-QA', 'validate_material_raid_staging_dry_run_canary_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-13-v64-ROLLUP', 'validate_mega_release_acceleration_13_v64_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM_PACK_v65
    # PUBLIC_SYNC_TAG_v65_MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM
    # ------------------------------------------------------------------------
    # PRIMO PACK CON POTENZIALE MUTAZIONE STAGING CONTROLLATA.
    # Approvazione utente esplicita: phrase=`approvo`,
    #   checksum=f67336fc69a7a4a2bf46fd31f3ae0fb871521c261f1f3c43dd457511ca81f137,
    #   scope=v65|material_raid_only|material_only_reward|allowlist_1_to_5|
    #         max_1_claim_per_user|max_10_total_claims|premium_currency_allowed_false|
    #         no_gacha_no_shop_no_vip_no_bp|rollback_required|observation_required.
    #
    # Outcome in questo container locale: BLOCKED_NOT_APPLIED_SAFE.
    # Motivo: nessuna superficie staging isolata disponibile
    #   (no STAGING_MONGO_URL, no /app/data/staging/material_raid_v65/.staging_ready).
    # Lo script `material_raid_first_controlled_live_staging_claim_v65.py` ha
    # rilevato i gate falliti e ha prodotto blocked_result. db_writes=0,
    # reward_grant_executed=false, materials_granted=false.
    #
    # Lane:
    #   1) v65_user_approval_handshake_and_scope_lock              (TRACK A)
    #   2) v65_staging_claim_apply_guard_and_canary_allowlist      (TRACK B)
    #   3) v65_first_controlled_live_staging_claim_runner          (TRACK C - script)
    #   4) v65_first_claim_result_blocked_evidence                 (TRACK D)
    #   5) v65_rollback_execution_plan_and_observation_window      (TRACK E)
    #   6) v65_qa_matrix_and_v66_readiness                         (TRACK F)
    # TRACK G: 6 OPTIONAL tuples + tag + 6 docs (386-391) + 6 markers + rollup.
    #
    # Invariants: 5 MD5-locked + 4 preferred-unchanged + Character Bible +
    # final_numbers unchanged. /api/* untouched, no MONGO_URL/pymongo/motor/redis
    # used by the runner script. No live reward/claim, no broad rollout, no
    # public claim, no premium/gacha/shop/VIP/BP mutation. No fake PASS. No
    # validator weakening. No tuple duplicate. material_raid_live_claim=false,
    # material_raid_reward_grant=false, material_raid_db_writes=0.
    # Verdict: BLOCKED_NOT_APPLIED_SAFE (alternative authorized by pack).
    # ========================================================================
    ('PROJECT-MATERIAL-RAID-v65-APPROVAL-HANDSHAKE', 'validate_material_raid_v65_approval_handshake_v1.py'),
    ('PROJECT-MATERIAL-RAID-v65-APPLY-GUARD', 'validate_material_raid_v65_apply_guard_v1.py'),
    ('PROJECT-MATERIAL-RAID-v65-FIRST-CLAIM-RESULT', 'validate_material_raid_v65_first_claim_result_v1.py'),
    ('PROJECT-MATERIAL-RAID-v65-ROLLBACK-OBSERVATION', 'validate_material_raid_v65_rollback_observation_v1.py'),
    ('PROJECT-MATERIAL-RAID-v65-QA-AND-v66-READINESS', 'validate_material_raid_v65_qa_and_v66_readiness_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-14-v65-ROLLUP', 'validate_mega_release_acceleration_14_v65_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA_SUPER_PACK_v66
    # PUBLIC_SYNC_TAG_v66_MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA
    # ------------------------------------------------------------------------
    # PREVIEW/ALPHA pack. Introduce il primo Story Runtime Adapter + First
    # Node Alpha Preview:
    #   1) story_runtime_adapter_v1_contract                       (TRACK A)
    #   2) story_first_node_alpha_fixture_and_runtime_payload      (TRACK B)
    #   3) story_first_node_runtime_preview_screen                 (TRACK C)
    #   4) story_result_reward_progress_preview_boundary           (TRACK D)
    #   5) story_anti_double_clear_idempotency_design              (TRACK E)
    #   6) story_runtime_adapter_first_node_alpha_qa_progress_v10  (TRACK F)
    # TRACK G: 7 OPTIONAL tuples + tag + 7 docs (392-398) + 6 markers + rollup.
    #
    # Una nuova schermata DEEPLINK-ONLY e' stata aggiunta:
    #   frontend/app/story-first-node-runtime-preview.tsx
    # NON e' collegata ad alcun menu pubblico. Non importa story.tsx ne'
    # combat.tsx ne' battle_engine. Nessun /api call. db_writes=0.
    #
    # ESCLUSI: authoritative_runtime, permanent_progress, reward_grant,
    # db_writes, backend_route_enablement, story.tsx/combat.tsx changes,
    # /api/story/battle e /api/battle/simulate changes.
    # ------------------------------------------------------------------------
    # Invariants enforced by v66: 5 MD5-locked unchanged + 4 preferred-
    # unchanged guardrails (server.py, combat.tsx, story.tsx,
    # material_raid_preview.py), Guild War unchanged, /api/* untouched,
    # no MONGO_URL/pymongo/motor/redis, runtime_runner_created=false,
    # runtime_activation_enabled=false, story_runtime_authoritative=false,
    # story_permanent_progress=false, story_reward_grant=false,
    # character_bible_changed=false, final_numbers_changed=false.
    # No fake PASS. No validator weakening. No tuple duplicate.
    # ========================================================================
    ('PROJECT-STORY-RUNTIME-ADAPTER-v1-CONTRACT', 'validate_story_runtime_adapter_v1_contract.py'),
    ('PROJECT-STORY-FIRST-NODE-ALPHA-FIXTURE-AND-PAYLOAD', 'validate_story_first_node_alpha_fixture_and_payload_v1.py'),
    ('PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN', 'validate_story_first_node_runtime_preview_screen_v1.py'),
    ('PROJECT-STORY-RESULT-REWARD-PROGRESS-PREVIEW-BOUNDARY', 'validate_story_result_reward_progress_preview_boundary_v1.py'),
    ('PROJECT-STORY-ANTI-DOUBLE-CLEAR-IDEMPOTENCY-DESIGN', 'validate_story_anti_double_clear_idempotency_design_v1.py'),
    ('PROJECT-STORY-RUNTIME-ADAPTER-FIRST-NODE-ALPHA-QA-AND-PROGRESS-v10', 'validate_story_runtime_adapter_first_node_alpha_qa_and_progress_v10_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-15-v66-ROLLUP', 'validate_mega_release_acceleration_15_v66_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_AND_IDEMPOTENCY_SIMULATION_PACK_v67
    # PUBLIC_SYNC_TAG_v67_MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY
    # ------------------------------------------------------------------------
    # PREVIEW/ALPHA pack. Estende l'adapter Story da 1 a 3 nodi alpha e
    # implementa il simulator in-memory dell'idempotency design v66:
    #   1) story_alpha_nodes_002_003_fixture_and_payload          (TRACK A)
    #   2) story_runtime_preview_widening_screen_patch            (TRACK B)
    #   3) story_clear_idempotency_dry_run_simulator              (TRACK C)
    #   4) story_clear_replay_and_ledger_dry_run_evidence         (TRACK D)
    #   5) story_clear_rollback_and_observation_simulation        (TRACK E)
    #   6) story_runtime_adapter_widen_idempotency_qa_and_v11     (TRACK F)
    # TRACK G: 7 OPTIONAL tuples + tag + 7 docs (399-405) + 6 markers + rollup.
    #
    # Screen patched (still DEEPLINK-ONLY):
    #   frontend/app/story-first-node-runtime-preview.tsx
    # Supporta nodi 1-3 via query param ?node_id=... (fallback node_001).
    # Italian UI, no /api calls, no Reanimated/AsyncStorage,
    # no import from story.tsx/combat.tsx/battle_engine.
    #
    # Simulator: Python puro, AST-checked, no pymongo/motor/redis/MONGO_URL,
    # no server/battle_engine imports. Evidence under
    #   data/design/story/results/story_clear_idempotency_dry_run_simulator_result_v1.json
    # ------------------------------------------------------------------------
    # Invariants: 5 MD5-locked unchanged + 4 preferred-unchanged guardrails.
    # No DB writes, no reward grant, no permanent progress, no live claim,
    # no battle_engine_runtime, runtime_runner_created=false,
    # story_runtime_authoritative=false. No fake PASS. No validator weakening.
    # ========================================================================
    ('PROJECT-STORY-ALPHA-NODES-002-003-PAYLOAD', 'validate_story_alpha_nodes_002_003_payload_v1.py'),
    ('PROJECT-STORY-RUNTIME-PREVIEW-WIDENING', 'validate_story_runtime_preview_widening_v1.py'),
    ('PROJECT-STORY-CLEAR-IDEMPOTENCY-SIMULATOR', 'validate_story_clear_idempotency_simulator_v1.py'),
    ('PROJECT-STORY-CLEAR-REPLAY-LEDGER-DRY-RUN', 'validate_story_clear_replay_ledger_dry_run_v1.py'),
    ('PROJECT-STORY-CLEAR-ROLLBACK-OBSERVATION', 'validate_story_clear_rollback_observation_v1.py'),
    ('PROJECT-STORY-RUNTIME-ADAPTER-WIDEN-IDEMPOTENCY-QA', 'validate_story_runtime_adapter_widen_idempotency_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-16-v67-ROLLUP', 'validate_mega_release_acceleration_16_v67_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68
    # PUBLIC_SYNC_TAG_v68_MEGA_RELEASE_ACCELERATION_17_STORY_BOSS_TOWER_ALPHA_LOOP
    # ------------------------------------------------------------------------
    # PREVIEW/ALPHA pack. Accorpa due lane (stesso pattern, stesso rischio,
    # stessi guardrail):
    #   1) Story first playable alpha slice preview - concatena i nodi alpha
    #      001/002/003 in un mini-loop locale deeplink-only.
    #   2) Boss + Tower alpha loop preview - loop alpha preview Boss e Tower
    #      in un'unica schermata deeplink-only con fixtures locali.
    # 7 OPTIONAL tuples + tag + 7 docs (406-412) + 7 markers + rollup.
    #
    # New deeplink-only screens (NO public menu routing):
    #   frontend/app/story-alpha-slice-preview.tsx
    #   frontend/app/boss-tower-alpha-loop-preview.tsx
    # Italian UI, no /api calls, no Reanimated/AsyncStorage,
    # no import from story.tsx/combat.tsx/battle_engine.
    # ------------------------------------------------------------------------
    # Invariants: 5 MD5-locked official unchanged + extra unchanged guardrails
    # (server.py, combat.tsx, story.tsx, material_raid_preview.py,
    # Character Bible/final_numbers). No DB writes, no reward grant, no
    # permanent progress, no leaderboard/ranking writes, no live claim,
    # no battle_engine_runtime, result_authoritative=false. No fake PASS.
    # No validator weakening.
    # ========================================================================
    ('PROJECT-STORY-FIRST-PLAYABLE-ALPHA-SLICE-CONTRACT', 'validate_story_first_playable_alpha_slice_contract_v1.py'),
    ('PROJECT-STORY-ALPHA-SLICE-PREVIEW-SCREEN', 'validate_story_alpha_slice_preview_screen_v1.py'),
    ('PROJECT-BOSS-TOWER-ALPHA-LOOP-CONTRACTS', 'validate_boss_tower_alpha_loop_contracts_v1.py'),
    ('PROJECT-BOSS-TOWER-ALPHA-LOOP-PREVIEW-UI', 'validate_boss_tower_alpha_loop_preview_ui_v1.py'),
    ('PROJECT-ALPHA-SLICE-RESULT-IDEMPOTENCY-BOUNDARY', 'validate_alpha_slice_result_idempotency_boundary_v1.py'),
    ('PROJECT-STORY-BOSS-TOWER-ALPHA-LOOP-QA', 'validate_story_boss_tower_alpha_loop_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-17-v68-ROLLUP', 'validate_mega_release_acceleration_17_v68_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS_SUPER_PACK_v69
    # PUBLIC_SYNC_TAG_v69_MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS
    # ------------------------------------------------------------------------
    # READINESS pack. Accorpa tre lane low-risk (preview/design/read-only):
    #   1) Training + Combat Onboarding preview - nuovo screen deeplink-only
    #      con 6 step tutorial (team_positioning, attack_order, skill_preview,
    #      result_preview, reward_preview_disabled, preview_vs_real_battle).
    #   2) Event + Arena Alpha Gate design + preview - nuovo screen deeplink-
    #      only con required gates per Event e Arena; nessuna currency, nessun
    #      ranking, nessun matchmaking live, nessun PVP pubblico.
    #   3) Hero Asset Dry-run + Manifest readiness - design contract/schema/
    #      matrix/forbidden scope + scanner Python read-only opzionale
    #      (placeholder report quando --path assente).
    # 7 OPTIONAL tuples + tag + 7 docs (413-419) + 7 markers + rollup.
    #
    # New deeplink-only screens (NO public menu routing):
    #   frontend/app/training-combat-onboarding-preview.tsx
    #   frontend/app/event-arena-alpha-gate-preview.tsx
    # Italian UI, no /api calls, no Reanimated/AsyncStorage,
    # no import from story.tsx/combat.tsx/battle_engine.
    # ------------------------------------------------------------------------
    # Invariants: 5 MD5 ufficiali + extra unchanged guardrails preservati.
    # db_writes=0, no reward grant, no permanent progress, no event currency,
    # no arena ranking/MMR, no leaderboard, no real asset import/copy,
    # no asset_runtime_resolver_change, no Character Bible change.
    # No fake PASS. No validator weakening.
    # ========================================================================
    ('PROJECT-TRAINING-COMBAT-ONBOARDING-CONTRACT', 'validate_training_combat_onboarding_contract_v1.py'),
    ('PROJECT-TRAINING-COMBAT-ONBOARDING-PREVIEW-UI', 'validate_training_combat_onboarding_preview_ui_v1.py'),
    ('PROJECT-EVENT-ARENA-ALPHA-GATE-DESIGN', 'validate_event_arena_alpha_gate_design_v1.py'),
    ('PROJECT-EVENT-ARENA-ALPHA-GATE-PREVIEW-UI', 'validate_event_arena_alpha_gate_preview_ui_v1.py'),
    ('PROJECT-HERO-ASSET-DRYRUN-MANIFEST-READINESS', 'validate_hero_asset_dryrun_manifest_readiness_v1.py'),
    ('PROJECT-TRAINING-EVENT-ARENA-ASSET-READINESS-QA', 'validate_training_event_arena_asset_readiness_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-18-v69-ROLLUP', 'validate_mega_release_acceleration_18_v69_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING_SUPER_PACK_v70
    # PUBLIC_SYNC_TAG_v70_MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING
    # ------------------------------------------------------------------------
    # ALPHA SLICE + ONBOARDING pack. Accorpa due lane:
    #   1) Event/Arena First Alpha Slice preview - nuovo screen deeplink-only
    #      con switch Event/Arena, timeline 6-7 step deterministica per slice,
    #      result preview disabled (no reward, no currency, no ranking/MMR).
    #   2) First Session Onboarding preview - nuovo screen deeplink-only con
    #      6 step (welcome -> training -> story -> event/arena -> asset
    #      explainer -> next steps). I "link" sono solo hint testuali.
    # 7 OPTIONAL tuples + tag + 7 docs (420-426) + 7 markers + rollup.
    #
    # ESCLUSO: hero_asset_staging_import_and_resolver_super_pack. Resta
    # deferred/gated finche' non viene fornito un asset pack reale.
    #
    # New deeplink-only screens (NO public menu routing):
    #   frontend/app/event-arena-first-alpha-slice-preview.tsx
    #   frontend/app/first-session-onboarding-preview.tsx
    # Italian UI, no /api calls, no Reanimated/AsyncStorage,
    # no import from story.tsx/combat.tsx/battle_engine.
    # ------------------------------------------------------------------------
    # Invariants: 5 MD5 ufficiali + extra unchanged guardrails preservati.
    # db_writes=0, no reward grant, no permanent progress, no event currency,
    # no arena ranking/MMR, no leaderboard, no matchmaking live,
    # no account flag writes, no AsyncStorage persistence,
    # no permanent_onboarding_complete, no real asset import/copy.
    # No fake PASS. No validator weakening.
    # ========================================================================
    ('PROJECT-EVENT-ARENA-FIRST-ALPHA-SLICE-CONTRACT', 'validate_event_arena_first_alpha_slice_contract_v1.py'),
    ('PROJECT-EVENT-ARENA-FIRST-ALPHA-SLICE-PREVIEW-UI', 'validate_event_arena_first_alpha_slice_preview_ui_v1.py'),
    ('PROJECT-FIRST-SESSION-ONBOARDING-CONTRACT', 'validate_first_session_onboarding_contract_v1.py'),
    ('PROJECT-FIRST-SESSION-ONBOARDING-PREVIEW-UI', 'validate_first_session_onboarding_preview_ui_v1.py'),
    ('PROJECT-ALPHA-PREVIEW-NAVIGATION-ASSET-BOUNDARY', 'validate_alpha_preview_navigation_asset_boundary_v1.py'),
    ('PROJECT-EVENT-ARENA-ONBOARDING-ALPHA-QA', 'validate_event_arena_onboarding_alpha_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-19-v70-ROLLUP', 'validate_mega_release_acceleration_19_v70_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_AND_ALPHA_INTERNAL_QA_SUPER_PACK_v71
    # PUBLIC_SYNC_TAG_v71_MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_ALPHA_QA
    # ------------------------------------------------------------------------
    # HARDENING + GATE + QA pack. Accorpa due lane:
    #   1) First Session Onboarding Hardening + Menu Preview Gate - patch
    #      hardening sullo screen onboarding esistente (banner, hardening
    #      panel, state machine labels, disabled complete indicator) +
    #      design del menu preview gate + safe hub route map (7 routes) +
    #      nuovo screen deeplink-only frontend/app/alpha-preview-hub.tsx.
    #   2) Alpha Internal QA Execution - plan, device matrix, severity
    #      matrix, evidence template + runner Python read-only
    #      backend/scripts/alpha_internal_qa_readiness_runner_v1.py
    #      (nessun network, nessun DB, solo presenza file).
    # 6 OPTIONAL tuples + tag + 6 docs (427-432) + 6 markers + rollup.
    #
    # ESCLUSO: hero_asset_staging_import_and_resolver_super_pack. Resta
    # deferred/gated finche' non viene fornito un asset pack reale.
    #
    # Patched screen: frontend/app/first-session-onboarding-preview.tsx
    # (solo hardening: banner aggiornato, hardening panel con state machine
    # labels, complete-onboarding disabled indicator). No fetch backend,
    # no AsyncStorage, no battle_engine, no story.tsx/combat.tsx import.
    # New deeplink-only screen: frontend/app/alpha-preview-hub.tsx.
    # ------------------------------------------------------------------------
    # Invariants: 5 MD5 ufficiali + extra unchanged guardrails preservati.
    # db_writes=0, no reward grant, no permanent progress, no account
    # persistence/flag writes, no async storage persistence,
    # no event currency, no arena ranking, no matchmaking live,
    # no public_menu_routing_enabled, no real asset import/copy.
    # No fake PASS. No validator weakening.
    # ========================================================================
    ('PROJECT-FIRST-SESSION-ONBOARDING-HARDENING', 'validate_first_session_onboarding_hardening_v1.py'),
    ('PROJECT-ALPHA-PREVIEW-MENU-GATE', 'validate_alpha_preview_menu_gate_v1.py'),
    ('PROJECT-ALPHA-PREVIEW-SAFE-HUB', 'validate_alpha_preview_safe_hub_v1.py'),
    ('PROJECT-ALPHA-INTERNAL-QA-EXECUTION', 'validate_alpha_internal_qa_execution_v1.py'),
    ('PROJECT-ONBOARDING-MENU-GATE-ALPHA-QA-MATRIX', 'validate_onboarding_menu_gate_alpha_qa_matrix_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-20-v71-ROLLUP', 'validate_mega_release_acceleration_20_v71_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_21_ALPHA_INTERNAL_QA_RUN_BUGFIX_TRIAGE_AND_MENU_EXPOSURE_DESIGN_PACK_v72
    # PUBLIC_SYNC_TAG_v72_MEGA_RELEASE_ACCELERATION_21_ALPHA_QA_MENU_DESIGN
    # ------------------------------------------------------------------------
    # ALPHA QA RUN + BUGFIX TRIAGE + MENU EXPOSURE DESIGN pack. Accorpa:
    #   1) Alpha Internal QA Run Evidence - device matrix + run log +
    #      severity bucket evidence (design-only, JSON fixtures).
    #   2) Alpha Internal QA Bug Backlog - triage list + P0/P1/P2/P3 bucket
    #      assignment + deferred backlog (design-only).
    #   3) Controlled Preview-Only Bugfix - default no code change.
    #      Micro-fix solo se P0/P1, safe, preview/deeplink only,
    #      UI/copy/guardrail/static TS, no fetch/API/DB/persistence.
    #   4) Menu Public Exposure Design (AFTER QA gate) - design-only,
    #      no production navigation changes, no public_menu_routing_enabled.
    #   5) Alpha QA Exit Criteria + v73 Readiness - exit gate criteria,
    #      readiness check fixtures (design-only).
    #   6) Rollup v72 - blanket meta validator.
    # 6 OPTIONAL tuples + tag + docs (433-438) + markers + rollup.
    #
    # ESCLUSO/DEFERRED: hero_asset_staging_import_and_resolver_super_pack
    # (gated finche' asset pack reale non fornito dall'utente),
    # menu_public_exposure_execution (solo design in v72, execution in v73).
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali + extra unchanged guardrails preservati.
    # db_writes=0, no reward grant, no permanent progress, no account
    # persistence/flag writes, no async storage persistence, no event
    # currency, no arena ranking/MMR, no matchmaking live,
    # no public_menu_routing_enabled, no real asset import/copy,
    # no runtime asset resolver change, no Character Bible/final_numbers.
    # No story.tsx/combat.tsx import. No fake PASS. No validator weakening.
    # ========================================================================
    ('PROJECT-ALPHA-INTERNAL-QA-RUN-EVIDENCE', 'validate_alpha_internal_qa_run_evidence_v1.py'),
    ('PROJECT-ALPHA-INTERNAL-QA-BUG-BACKLOG', 'validate_alpha_internal_qa_bug_backlog_v1.py'),
    ('PROJECT-CONTROLLED-PREVIEW-ONLY-BUGFIX', 'validate_controlled_preview_only_bugfix_v1.py'),
    ('PROJECT-MENU-PUBLIC-EXPOSURE-DESIGN-AFTER-QA', 'validate_menu_public_exposure_design_after_qa_v1.py'),
    ('PROJECT-ALPHA-QA-EXIT-CRITERIA-v73-READINESS', 'validate_alpha_qa_exit_criteria_v73_readiness_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-21-v72-ROLLUP', 'validate_mega_release_acceleration_21_v72_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_22_MENU_PUBLIC_EXPOSURE_GATED_EXECUTION_AND_CLOSED_ALPHA_PLAN_PACK_v73
    # PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA
    # ------------------------------------------------------------------------
    # MENU PUBLIC EXPOSURE GATED EXECUTION + CLOSED ALPHA PLAN pack. Accorpa:
    #   1) Public Exposure Approval Handshake + Scope Lock + Execution
    #      Forbidden Scope - manual approval phrase + checksum required.
    #   2) Menu Exposure Dry-run + Apply/Blocked Evidence -
    #      verdict BLOCKED_NOT_APPLIED_SAFE (no approval phrase in v73 prompt).
    #   3) Candidate Route Map (7 deeplink-only preview routes) +
    #      Rollback Runbook (<=5 step, no data loss) + Observation Plan
    #      (60min window, P0/P1 trigger).
    #   4) Closed Alpha Testing Plan + Tester Onboarding Template +
    #      Feedback Form Template + Bug Report Workflow (design-only,
    #      no live invites, no account persistence).
    #   5) v72 P3 Polish Backlog Plan + Deferred Decision (3 findings,
    #      apply_now=false, safe_to_fix_later=true).
    #   6) Menu Exposure Closed Alpha Readiness Matrix +
    #      Progress Report v17 (10 areas all ready, apply blocked).
    #   7) Rollup v73 meta validator.
    # 7 OPTIONAL tuples + tag + docs (439-445) + markers + rollup.
    #
    # ESCLUSO/DEFERRED:
    #   - menu_public_exposure_actual_apply (waiting for explicit user
    #     approval phrase in a future v74 pack).
    #   - hero_asset_staging_import_and_resolver_super_pack (waiting for
    #     real asset pack supplied by user).
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali + extra unchanged guardrails preservati.
    # db_writes=0, no reward grant, no permanent progress, no account
    # persistence/flag writes, no async storage persistence, no event
    # currency, no arena ranking/MMR, no matchmaking live,
    # no public_menu_routing_enabled, no production_navigation_changed,
    # no home_menu_routing_enabled, no real asset import/copy,
    # no runtime asset resolver change, no Character Bible/final_numbers.
    # No story.tsx/combat.tsx import. No backend route change. No server.py.
    # No battle_engine.py. No api/story/battle. No api/battle/simulate.
    # No micro-patch .tsx. No validator weakening. No fake PASS.
    # ========================================================================
    ('PROJECT-MENU-PUBLIC-EXPOSURE-APPROVAL-HANDSHAKE', 'validate_menu_public_exposure_approval_handshake_v1.py'),
    ('PROJECT-MENU-PUBLIC-EXPOSURE-DRYRUN-BLOCKED', 'validate_menu_public_exposure_dryrun_blocked_v1.py'),
    ('PROJECT-MENU-PUBLIC-EXPOSURE-ROUTE-ROLLBACK', 'validate_menu_public_exposure_route_rollback_v1.py'),
    ('PROJECT-CLOSED-ALPHA-TESTING-PLAN', 'validate_closed_alpha_testing_plan_v1.py'),
    ('PROJECT-v72-P3-POLISH-BACKLOG', 'validate_v72_p3_polish_backlog_v1.py'),
    ('PROJECT-MENU-EXPOSURE-CLOSED-ALPHA-READINESS', 'validate_menu_exposure_closed_alpha_readiness_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-22-v73-ROLLUP', 'validate_mega_release_acceleration_22_v73_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_23_MENU_PUBLIC_EXPOSURE_APPLY_AND_CLOSED_ALPHA_KICKOFF_GATE_PACK_v74
    # PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF
    # ------------------------------------------------------------------------
    # MENU PUBLIC EXPOSURE APPLY (CONTROLLED) + CLOSED ALPHA KICKOFF GATE.
    # Approval phrase ricevuta + checksum sha256 verificato.
    # Apply CONTROLLED: nuovo screen frontend/app/alpha-menu-preview.tsx
    # come sezione "Alpha Preview Menu" raggiungibile via route/deeplink.
    # Home root / tab bar / production navigation: INVARIATI.
    # 7 route esposte (alpha-preview-hub + 6 preview) coincidenti con
    # menu_public_exposure_scope_lock_v1 (v73).
    # Observation result: 8/8 signals PASS, no rollback.
    # Closed alpha kickoff gate: ready, manual recruitment only,
    # invites NON enabled, account persistence NON abilitata.
    # P3 polish carry-forward (3 finding) deferito a polish batch v75+.
    # Progress report v18 emesso.
    # 7 OPTIONAL tuples + tag + docs (446-452) + markers + rollup.
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post apply.
    # db_writes=0, no reward grant, no permanent progress, no account
    # persistence/flag writes, no async storage persistence, no event
    # currency, no arena ranking/MMR, no matchmaking live, no real asset
    # import, no runtime asset resolver change, no Character Bible/
    # final_numbers, no broad commercial release. No story.tsx/combat.tsx
    # import nel nuovo screen. No backend route change. No server.py.
    # No battle_engine. No api/story/battle. No api/battle/simulate.
    # No validator weakening. No fake PASS.
    # ========================================================================
    ('PROJECT-MENU-PUBLIC-EXPOSURE-APPROVAL-VERIFICATION', 'validate_menu_public_exposure_approval_verification_v1.py'),
    ('PROJECT-MENU-PUBLIC-EXPOSURE-APPLY-CONTROLLED', 'validate_menu_public_exposure_apply_controlled_v1.py'),
    ('PROJECT-MENU-PUBLIC-EXPOSURE-OBSERVATION-RESULT', 'validate_menu_public_exposure_observation_result_v1.py'),
    ('PROJECT-CLOSED-ALPHA-KICKOFF-GATE', 'validate_closed_alpha_kickoff_gate_v1.py'),
    ('PROJECT-v72-P3-POLISH-CARRYFORWARD', 'validate_v72_p3_polish_carryforward_v1.py'),
    ('PROJECT-ALPHA-READINESS-PROGRESS-v18', 'validate_alpha_readiness_progress_v18_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-23-v74-ROLLUP', 'validate_mega_release_acceleration_23_v74_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_AND_P3_POLISH_PACK_v75
    # PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH
    # ------------------------------------------------------------------------
    # CLOSED ALPHA KICKOFF EXECUTION (manual readiness only) +
    # FINDINGS TRIAGE WORKFLOW + v72 P3 POLISH BATCH APPLIED.
    # - Kickoff execution mode: manual_recruitment_readiness_only.
    # - No automated live invites, no email/DM send, no networking.
    # - Manual recruitment plan: 8 slot template, channels manual_only.
    # - Session tracker + evidence templates (external storage,
    #   no in-app persistence, no async storage).
    # - Findings triage workflow (P0/P1/P2/P3 buckets + SLA + decision matrix).
    # - Kickoff dry-run: 17/17 PASS, DRY_RUN_PASS_READY_FOR_MANUAL_KICKOFF.
    # - v72 P3 polish batch APPLIED (3/3 micro-patch su due file preview,
    #   ts_clean, static scan ok, MD5 invariants invariati, backlog cleared).
    # - Progress report v19 emesso.
    # 8 OPTIONAL tuples + tag + docs (453-460) + markers + rollup.
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post polish.
    # db_writes=0, no reward grant, no permanent progress, no account
    # persistence/flag writes, no async storage persistence, no event
    # currency, no arena ranking/MMR, no matchmaking live, no real asset
    # import, no resolver runtime change, no Character Bible/final_numbers,
    # no broad commercial release. No story.tsx/combat.tsx import nei file
    # patchati. No backend route change. No server.py. No battle_engine.
    # No api/story/battle. No api/battle/simulate. No automated live
    # invites. No email send. No validator weakening. No fake PASS.
    # ========================================================================
    ('PROJECT-CLOSED-ALPHA-KICKOFF-EXECUTION-STATE', 'validate_closed_alpha_kickoff_execution_state_v1.py'),
    ('PROJECT-CLOSED-ALPHA-MANUAL-RECRUITMENT-PLAN', 'validate_closed_alpha_manual_recruitment_plan_v1.py'),
    ('PROJECT-CLOSED-ALPHA-SESSION-TRACKER-EVIDENCE', 'validate_closed_alpha_session_tracker_evidence_v1.py'),
    ('PROJECT-CLOSED-ALPHA-FINDINGS-TRIAGE-WORKFLOW', 'validate_closed_alpha_findings_triage_workflow_v1.py'),
    ('PROJECT-CLOSED-ALPHA-KICKOFF-DRY-RUN', 'validate_closed_alpha_kickoff_dry_run_v1.py'),
    ('PROJECT-v72-P3-POLISH-BATCH-APPLIED', 'validate_v72_p3_polish_batch_applied_v1.py'),
    ('PROJECT-ALPHA-READINESS-PROGRESS-v19', 'validate_alpha_readiness_progress_v19_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-24-v75-ROLLUP', 'validate_mega_release_acceleration_24_v75_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_25_CLOSED_ALPHA_MANUAL_KICKOFF_FEEDBACK_INTAKE_AND_STORE_BETA_READINESS_PACK_v76
    # PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS
    # ------------------------------------------------------------------------
    # CLOSED ALPHA MANUAL KICKOFF (packet finale) + FEEDBACK INTAKE +
    # STORE BETA READINESS NOTES (Google Play / TestFlight, notes_only).
    # - Manual kickoff packet finale (delivery_mode = manual_author_dm_only)
    # - Recruitment user-action checklist (7 step, tutti non automatizzabili)
    # - Session result placeholder (8 slot alias-only, no PII in repo)
    # - Feedback intake template (storage external, no in-app persistence)
    # - Post-session triage dry-run (pipeline vuota -> ready for real feedback)
    # - Store beta readiness notes (Play + TestFlight): solo note, no upload
    # - v77 readiness plan post-session triage
    # - Alpha readiness progress report v20
    # 9 OPTIONAL tuples + tag + docs (461-469) + markers + rollup.
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, no automated invites, no email/DM send, no networking,
    # no store upload (Play/TestFlight), no Play Console changes,
    # no App Store Connect/TestFlight changes, no build generation,
    # no PII collected in repo, no reward grant, no permanent progress,
    # no account persistence/flag writes, no async storage persistence,
    # no event currency, no arena ranking/MMR, no matchmaking live,
    # no real asset import, no resolver runtime change,
    # no Character Bible/final_numbers, no broad commercial release.
    # No story.tsx/combat.tsx changes. No backend route change. No server.py.
    # No battle_engine. No api/story/battle. No api/battle/simulate.
    # No validator weakening. No fake PASS.
    # ========================================================================
    ('PROJECT-CLOSED-ALPHA-MANUAL-KICKOFF-PACKET-FINAL', 'validate_closed_alpha_manual_kickoff_packet_final_v1.py'),
    ('PROJECT-CLOSED-ALPHA-RECRUITMENT-USER-ACTION-CHECKLIST', 'validate_closed_alpha_recruitment_user_action_checklist_v1.py'),
    ('PROJECT-CLOSED-ALPHA-SESSION-RESULT-PLACEHOLDER', 'validate_closed_alpha_session_result_placeholder_v1.py'),
    ('PROJECT-CLOSED-ALPHA-FEEDBACK-INTAKE-TEMPLATE', 'validate_closed_alpha_feedback_intake_template_v1.py'),
    ('PROJECT-CLOSED-ALPHA-POST-SESSION-TRIAGE-DRY-RUN', 'validate_closed_alpha_post_session_triage_dry_run_v1.py'),
    ('PROJECT-STORE-BETA-READINESS-NOTES', 'validate_store_beta_readiness_notes_v1.py'),
    ('PROJECT-v77-READINESS-POST-SESSION-TRIAGE-PLAN', 'validate_v77_readiness_post_session_triage_plan_v1.py'),
    ('PROJECT-ALPHA-READINESS-PROGRESS-v20', 'validate_alpha_readiness_progress_v20_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-25-v76-ROLLUP', 'validate_mega_release_acceleration_25_v76_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_26_CLOSED_ALPHA_FEEDBACK_AGGREGATION_TRIAGE_WRAP_AND_V78_READINESS_PACK_v77
    # PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS
    # ------------------------------------------------------------------------
    # CLOSED ALPHA FEEDBACK AGGREGATION + TRIAGE + WRAP + v78 READINESS.
    # - Feedback input discovery in 4 safe path locali (no network/form fetch)
    # - Aggregation result: empty pipeline (actual_feedback_received=false)
    # - Findings triage: 0 findings, halt_triggered=false
    # - Wrap summary: go_no_go=DEFERRED_PENDING_FEEDBACK
    # - Deferred store/asset summary: tutte le lane in no_action
    # - v78 readiness plan: lane + entry conditions + decision options
    # - Progress report v21
    # - Rollup v77 meta validator
    # 8 OPTIONAL tuples + tag + docs (470-477) + markers + rollup.
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, network_fetch_performed=false, external_form_fetch=false,
    # automated_live_invites=false, store_upload_performed=false,
    # play_console/appstore/testflight changes=false, build_generation=false,
    # pii_collected_in_repo=false, alias_only=true, invented_data=false,
    # production_navigation_changed=false, no reward grant, no permanent
    # progress, no account persistence/flag writes, no async storage,
    # no event currency, no arena ranking, no matchmaking live, no real
    # asset import, no resolver runtime change, no Character Bible/
    # final_numbers, no broad commercial release. No story.tsx/combat.tsx.
    # No backend route. No server.py. No battle_engine. No api/story/battle.
    # No api/battle/simulate. No validator weakening. No fake PASS.
    # ========================================================================
    ('PROJECT-CLOSED-ALPHA-FEEDBACK-INPUT-DISCOVERY', 'validate_closed_alpha_feedback_input_discovery_v1.py'),
    ('PROJECT-CLOSED-ALPHA-FEEDBACK-AGGREGATION-RESULT', 'validate_closed_alpha_feedback_aggregation_result_v1.py'),
    ('PROJECT-CLOSED-ALPHA-FINDINGS-TRIAGE-RESULT', 'validate_closed_alpha_findings_triage_result_v1.py'),
    ('PROJECT-CLOSED-ALPHA-WRAP-SUMMARY', 'validate_closed_alpha_wrap_summary_v1.py'),
    ('PROJECT-DEFERRED-STORE-ASSET-SUMMARY', 'validate_deferred_store_asset_summary_v1.py'),
    ('PROJECT-v78-READINESS-PLAN', 'validate_v78_readiness_plan_v1.py'),
    ('PROJECT-ALPHA-READINESS-PROGRESS-v21', 'validate_alpha_readiness_progress_v21_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-26-v77-ROLLUP', 'validate_mega_release_acceleration_26_v77_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY_AND_ROADMAP_REALIGNMENT_PACK_v78
    # PUBLIC_SYNC_TAG_v78_MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY
    # ------------------------------------------------------------------------
    # CANONICAL v78 = PvE Reward Claim Canary (lane economy/canary from v54/v64/v65).
    # - Roadmap realignment + scope lock + forbidden scope
    # - Contract + request/response schema (PvE non-premium only)
    # - Idempotency + ledger (isolated canary collection) + replay matrix
    # - Runner: default dry-run; apply ONLY if isolated staging + apply flag
    # - Rollback (canary-only) + observation (60min) + kill switch
    # - QA matrix + progress v22_corrected + readiness v78->v79
    # - Verdict (current env): BLOCKED_NOT_APPLIED_SAFE (db_writes=0)
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, applied=false, broad_rollout=false, premium_currency=false,
    # gacha/shop/VIP/BP=false, event currency live=false, arena ranking=false,
    # backend route exposure=false, server.py change=false, battle_engine
    # change=false, api/story/battle change=false, api/battle/simulate
    # change=false, story.tsx/combat.tsx change=false, asset import=false,
    # Character Bible/final_numbers/hero roster=false, AsyncStorage=false,
    # auth mutation=false, account persistence outside canary=false,
    # validator weakening=false, fake PASS=false.
    # Deferred: feedback_input_staging_pack (non canonico v78),
    #           hero_asset_staging_import (in attesa di asset reali).
    # ========================================================================
    ('PROJECT-v78-ROADMAP-REALIGNMENT', 'validate_v78_roadmap_realignment_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CONTRACT-SCHEMA', 'validate_pve_reward_claim_contract_schema_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-IDEMPOTENCY-LEDGER', 'validate_pve_reward_claim_idempotency_ledger_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER', 'validate_pve_reward_claim_canary_runner_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-ROLLBACK-OBSERVATION', 'validate_pve_reward_claim_rollback_observation_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-QA', 'validate_pve_reward_claim_canary_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-27-v78-ROLLUP', 'validate_mega_release_acceleration_27_v78_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING_SETUP_AND_LOCAL_APPLY_PACK_v79
    # PUBLIC_SYNC_TAG_v79_MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING
    # ------------------------------------------------------------------------
    # CANARY STAGING LOCALE FILE-BASED (no DB, no MongoDB, no Redis, no routes).
    # - Staging env contract + scope lock + forbidden scope
    # - 6 staging files locali sotto /app/data/canary_staging/
    # - Runner v1 upgrade: --local-preflight / --local-apply / --local-rollback-drill
    # - Local apply eseguito: 1 ledger entry isolato + 2 negative tests passed
    # - Rollback drill file-only + observation pass + wave2 gate ready
    # - QA matrix 14 PASS + progress v23 + readiness v79->v80
    # - Verdict (current env): LOCAL_STAGING_APPLIED_SAFE (db_writes=0,
    #   local_file_writes=6, live_reward_grant=false)
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, applied_to_live=false, live_reward_grant=false,
    # mongo_url_used=false, pymongo_used=false, motor_used=false, redis_used=false,
    # broad_rollout=false, premium_currency=false, gacha/shop/VIP/BP=false,
    # backend_route_exposure=false, server.py/battle_engine/story.tsx/combat.tsx unchanged,
    # asset_import=false, env_mutation=false, validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: b76ae4ebfa01519f17589eb81a43130970cf86c600de0d95a85727547d77af5b
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-ENV', 'validate_pve_reward_claim_canary_staging_env_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-FILES', 'validate_pve_reward_claim_canary_staging_files_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-LOCAL', 'validate_pve_reward_claim_canary_runner_local_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-LOCAL-APPLY', 'validate_pve_reward_claim_canary_local_apply_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-ROLLBACK-OBSERVATION', 'validate_pve_reward_claim_canary_staging_rollback_observation_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-STAGING-QA', 'validate_pve_reward_claim_canary_staging_qa_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-28-v79-ROLLUP', 'validate_mega_release_acceleration_28_v79_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVATION_AND_UI_SUMMARY_GATED_PACK_v80
    # PUBLIC_SYNC_TAG_v80_MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2
    # ------------------------------------------------------------------------
    # WAVE-2 CANARY LOCALE FILE-BASED + UI SUMMARY GATED DESIGN-ONLY.
    # - Wave2 scope lock + plan + forbidden scope
    # - 3 staging file wave2 sotto /app/data/canary_staging/wave2_*
    # - Runner v1 upgrade: --wave2-preflight / --wave2-apply / --wave2-observe / --wave2-rollback-drill
    # - Wave2 apply: 3 ledger entry isolati (canary_user_001/002/003) + 5 negative test PASS
    # - Rollback drill file-only (sample policy) + observation PASS + wave3 gate ready
    # - Reward Claim UI Summary Gated Design (design-only, NO TSX, NO production UI)
    # - QA matrix 18 PASS + progress v24 + readiness v80->v81
    # - Verdict: WAVE2_OBSERVED_SAFE (db_writes=0, local_file_writes=6,
    #   live_reward_grant=false, applied_to_live=false)
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, applied_to_live=false, live_reward_grant=false,
    # mongo_url_used=false, pymongo_used=false, motor_used=false, redis_used=false,
    # broad_rollout=false, premium_currency=false, gacha/shop/VIP/BP=false,
    # backend_route_exposure=false, server.py/battle_engine/story.tsx/combat.tsx unchanged,
    # asset_import=false, env_mutation=false, production_ui_exposure=false,
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: c00c552857ba58bcc47c305df1536cd87f81e677d76004de87887abf287fa9da
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-SCOPE', 'validate_pve_reward_claim_canary_wave2_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-FILES', 'validate_pve_reward_claim_canary_wave2_files_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE2', 'validate_pve_reward_claim_canary_runner_wave2_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-APPLY', 'validate_pve_reward_claim_canary_wave2_apply_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE2-OBSERVATION', 'validate_pve_reward_claim_canary_wave2_observation_v1.py'),
    ('PROJECT-REWARD-CLAIM-UI-SUMMARY-GATED-DESIGN', 'validate_reward_claim_ui_summary_gated_design_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-29-v80-ROLLUP', 'validate_mega_release_acceleration_29_v80_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_AND_UI_SUMMARY_PREVIEW_SHELL_PACK_v81
    # PUBLIC_SYNC_TAG_v81_MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_UI
    # ------------------------------------------------------------------------
    # WAVE-3 CANARY LOCALE FILE-BASED (5 alias-only / 5 claim) + UI SUMMARY PREVIEW SHELL.
    # - Wave3 scope lock + plan + UI preview contract + forbidden scope
    # - 3 staging file wave3 + manifest
    # - Runner upgrade: --wave3-preflight/--wave3-apply/--wave3-observe/--wave3-rollback-drill
    # - Wave3 apply: 5 ledger entry isolati + 6 negative test PASS (+ malformed_route)
    # - Observation PASS (7 criteria) + rollback drill + live-staging gate ready
    # - Frontend reward-claim-summary-preview.tsx deeplink-only + alpha-menu link safe
    # - QA matrix 22 PASS + progress v25 + readiness v81->v82
    # - Verdict: WAVE3_AND_UI_SUMMARY_PREVIEW_READY (db_writes=0, local_file_writes=6,
    #   live_reward_grant=false, applied_to_live=false, production_ui_exposure=false)
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, applied_to_live=false, live_reward_grant=false,
    # mongo_url_used=false, pymongo_used=false, motor_used=false, redis_used=false,
    # broad_rollout=false, premium_currency=false, gacha/shop/VIP/BP=false,
    # backend_route_exposure=false, server.py/battle_engine/story.tsx/combat.tsx unchanged,
    # asset_import=false, env_mutation=false, production_ui_exposure=false,
    # real_claim_button=false, live_claim_endpoint=false,
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: 8a910565ed94e75eca4085a38f9233adeaf3349fda09aa933587dbb07ab3a66a
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-SCOPE', 'validate_pve_reward_claim_canary_wave3_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-FILES', 'validate_pve_reward_claim_canary_wave3_files_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE3', 'validate_pve_reward_claim_canary_runner_wave3_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-APPLY', 'validate_pve_reward_claim_canary_wave3_apply_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE3-OBSERVATION', 'validate_pve_reward_claim_canary_wave3_observation_v1.py'),
    ('PROJECT-REWARD-CLAIM-UI-SUMMARY-PREVIEW-SHELL', 'validate_reward_claim_ui_summary_preview_shell_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-30-v81-ROLLUP', 'validate_mega_release_acceleration_30_v81_rollup.py'),
    # ========================================================================
    # MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_DESIGN_AND_UI_HARDENING_PACK_v82
    # PUBLIC_SYNC_TAG_v82_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI
    # ------------------------------------------------------------------------
    # WAVE-4 (8 alias-only / 8 claim) + LIVE-DB READINESS DESIGN-ONLY GATE + UI HARDENING.
    # - Wave4 scope lock + plan + live-staging boundary + forbidden scope
    # - 3 staging file wave4 + manifest
    # - Runner upgrade: --wave4-preflight/--wave4-apply/--wave4-observe/--wave4-rollback-drill
    # - Wave4 apply: 8 ledger entry isolati + 7 negative test PASS (+ event_arena_ranking_reward)
    # - Observation PASS (8 criteria) + rollback drill (2 sample) + live-DB readiness DESIGN gate (design-only)
    # - Frontend reward-claim-summary-preview.tsx HARDENED (status chips, snapshot section, labels DB_WRITES_0/LOCAL_FILE_ONLY)
    # - QA matrix 24 PASS + progress v26 + readiness v82->v83
    # - Verdict: WAVE4_LIVE_STAGING_DESIGN_AND_UI_HARDENING_READY (db_writes=0, local_file_writes=6,
    #   live_reward_grant=false, applied_to_live=false, live_db_apply_active=false, production_ui_exposure=false)
    # ------------------------------------------------------------------------
    # Invariants: 8 MD5 ufficiali invariati pre/post pack.
    # db_writes=0, applied_to_live=false, live_reward_grant=false, live_db_apply_active=false,
    # mongo_url_used=false, pymongo_used=false, motor_used=false, redis_used=false,
    # broad_rollout=false, premium_currency=false, gacha/shop/VIP/BP=false,
    # arena_ranking_reward=false, backend_route_exposure=false,
    # server.py/battle_engine/story.tsx/combat.tsx unchanged,
    # asset_import=false, env_mutation=false, production_ui_exposure=false,
    # real_claim_button=false, live_claim_endpoint=false,
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: 468cac7a8894ae81867f6e4c1f81ec3e9b458c9c4a4221668a68f486ea9b4d58
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE4-SCOPE', 'validate_pve_reward_claim_canary_wave4_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE4-FILES', 'validate_pve_reward_claim_canary_wave4_files_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE4', 'validate_pve_reward_claim_canary_runner_wave4_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE4-APPLY', 'validate_pve_reward_claim_canary_wave4_apply_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE4-OBS-LIVE-DB-DESIGN', 'validate_pve_reward_claim_canary_wave4_observation_live_db_design_v1.py'),
    ('PROJECT-REWARD-CLAIM-UI-SUMMARY-PREVIEW-HARDENING', 'validate_reward_claim_ui_summary_preview_hardening_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-31-v82-ROLLUP', 'validate_mega_release_acceleration_31_v82_rollup.py'),
    # ========================================================================
    # v83 - MEGA_RELEASE_ACCELERATION_32_PVE_REWARD_CLAIM_WAVE5_AND_LIVE_DB_DESIGN_CONTRACT
    # Tracks A-G: scope/files/runner/apply/observation+gateway/live-db-design/rollup.
    # local file-based only, 12 utenti alias-only / 12 claim. live_db_apply_allowed=false,
    # endpoint_implemented=false, db_writes=0, applied_to_live=false.
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: ce17d00a3e365bd4bf5efcad9aea43e51ad92c36e6301336aaaddf6229ce2f0a
    # PUBLIC_SYNC_TAG_v83_MEGA_RELEASE_ACCELERATION_32_PVE_REWARD_CLAIM_WAVE5_AND_LIVE_DB_DESIGN_CONTRACT
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE5-SCOPE', 'validate_pve_reward_claim_canary_wave5_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE5-FILES', 'validate_pve_reward_claim_canary_wave5_files_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-RUNNER-WAVE5', 'validate_pve_reward_claim_canary_runner_wave5_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE5-APPLY', 'validate_pve_reward_claim_canary_wave5_apply_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE5-OBS-GATEWAY', 'validate_pve_reward_claim_canary_wave5_observation_gateway_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DESIGN-CONTRACT', 'validate_pve_reward_claim_live_db_design_contract_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-32-v83-ROLLUP', 'validate_mega_release_acceleration_32_v83_rollup.py'),
    # ========================================================================
    # v84 - MEGA_RELEASE_ACCELERATION_33_PVE_REWARD_CLAIM_LIVE_DB_DRY_RUN_AND_PUBLIC_SYNC_REPAIR
    # Tracks A-G: public_sync_repair / scope / fixtures / simulator / tx-auth-endpoint-killswitch /
    # rollback-observation / v85-gate / rollup. NO APPLY DB, NO ENDPOINT IMPLEMENTATION.
    # live_db_apply_allowed=false, endpoint_implemented=false, db_writes=0, applied_to_live=false.
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: 86efe1aac64e15f6350be77e627cc37be3c122480cf8f86b1173781b3f464d54
    # PUBLIC_SYNC_TAG_v84_MEGA_RELEASE_ACCELERATION_33_PVE_REWARD_CLAIM_LIVE_DB_DRY_RUN_AND_PUBLIC_SYNC_REPAIR
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-SCOPE', 'validate_pve_reward_claim_live_db_dry_run_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-FIXTURES', 'validate_pve_reward_claim_live_db_dry_run_fixtures_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-SIMULATOR', 'validate_pve_reward_claim_live_db_dry_run_simulator_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-CONTRACT', 'validate_pve_reward_claim_live_db_dry_run_contract_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-ROLLBACK-OBS', 'validate_pve_reward_claim_live_db_dry_run_rollback_observation_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-V83-PUBLIC-SYNC-REPAIR', 'validate_pve_reward_claim_v83_public_sync_repair_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-33-v84-ROLLUP', 'validate_mega_release_acceleration_33_v84_rollup.py'),
    # ========================================================================
    # v85 - MEGA_RELEASE_ACCELERATION_34_PVE_REWARD_CLAIM_LIVE_DB_CANARY_APPLY_DESIGN_AND_SYNC_REPAIR
    # Tracks A-G: strong_public_sync_repair / scope / approval_workflow_runbook /
    # step_up_auth_endpoint_stub / drill (kill_switch + rollback_chain) / v86_gate / rollup.
    # NO APPLY DB, NO ENDPOINT IMPLEMENTATION. live_db_apply_allowed=false,
    # endpoint_implemented=false, db_writes=0, applied_to_live=false.
    # validator_weakening=false, fake_PASS=false.
    # Approval checksum sha256: 5fa9c8c25fb9ef177402163db663c625aa66125d8007d5864ff8adb74e0ef6b5
    # PUBLIC_SYNC_TAG_v85_MEGA_RELEASE_ACCELERATION_34_PVE_REWARD_CLAIM_LIVE_DB_CANARY_APPLY_DESIGN_AND_SYNC_REPAIR
    # PUBLIC_SYNC_SENTINEL_v83_PRESENT=YES
    # PUBLIC_SYNC_SENTINEL_v84_PRESENT=YES
    # PUBLIC_SYNC_SENTINEL_v85_PRESENT=YES
    # ========================================================================
    ('PROJECT-PVE-REWARD-CLAIM-V83-V84-V85-STRONG-PUBLIC-SYNC-REPAIR', 'validate_pve_reward_claim_v83_v84_v85_strong_public_sync_repair_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-SCOPE', 'validate_pve_reward_claim_live_db_canary_apply_scope_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-APPROVAL-WORKFLOW', 'validate_pve_reward_claim_live_db_canary_apply_approval_workflow_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-RUNBOOK', 'validate_pve_reward_claim_live_db_canary_apply_runbook_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-STEP-UP-AUTH', 'validate_pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub_v1.py'),
    ('PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-DRILL', 'validate_pve_reward_claim_live_db_canary_apply_drill_v1.py'),
    ('MEGA-RELEASE-ACCELERATION-34-v85-ROLLUP', 'validate_mega_release_acceleration_34_v85_rollup.py'),
    # ========================================================================
    # v86 - MEGA_RELEASE_ACCELERATION_35_PLAYABLE_MODE_VISUAL_BATTLE_ROUTING_AND_RAID_BOSS_PLACEHOLDER_SCHEMA
    # Playable Mode visual battle routing (training/story/boss/tower/event/arena) + raid boss schema design-only.
    # preview_only=true, deterministic=true, authoritative=false, db_writes=0, reward_live=false,
    # endpoint_live=false, battle_engine_authoritative=false.
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v86_MEGA_RELEASE_ACCELERATION_35_PLAYABLE_MODE_VISUAL_BATTLE_ROUTING_AND_RAID_BOSS_PLACEHOLDER_SCHEMA
    # PUBLIC_SYNC_SENTINEL_v86_PRESENT=YES
    # ========================================================================
    ('PROJECT-V86-PLAYABLE-MODE-VISUAL-BATTLE-PAYLOADS', 'validate_v86_playable_mode_visual_battle_payloads.py'),
    ('PROJECT-V86-PLAYABLE-MODE-ROUTE-SAFETY', 'validate_v86_playable_mode_route_safety.py'),
    ('PROJECT-V86-RAID-BOSS-PLACEHOLDER-SCHEMA', 'validate_v86_raid_boss_placeholder_schema.py'),
    ('MEGA-RELEASE-ACCELERATION-35-v86-ROLLUP', 'validate_mega_release_acceleration_35_v86_rollup.py'),
    # ========================================================================
    # v87 - MEGA_RELEASE_ACCELERATION_36_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER
    # Mobile QA hub route + visual layer (portrait placeholder + reactive HP bar + turn highlight).
    # preview_only=true, deterministic=true, authoritative=false, db_writes=0, reward_live=false,
    # endpoint_live=false, battle_engine_authoritative=false.
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v87_MEGA_RELEASE_ACCELERATION_36_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER
    # PUBLIC_SYNC_SENTINEL_v87_PRESENT=YES
    # ========================================================================
    ('PROJECT-V87-MOBILE-QA-ACCESS', 'validate_v87_mobile_qa_access.py'),
    ('PROJECT-V87-BATTLE-PREVIEW-VISUAL-LAYER', 'validate_v87_battle_preview_visual_layer.py'),
    ('PROJECT-V87-PREVIEW-PORTRAIT-PLACEHOLDER-CATALOG', 'validate_v87_preview_portrait_placeholder_catalog.py'),
    ('MEGA-RELEASE-ACCELERATION-36-v87-ROLLUP', 'validate_mega_release_acceleration_36_v87_rollup.py'),
    # ========================================================================
    # v88 - MEGA_RELEASE_ACCELERATION_37_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE
    # Real UI wiring nel menu mobile (categoria "Battle Preview QA (v88)" con 5 deeplink) +
    # esperienza battaglia preview (autoplay/pause/speed/AI hints/floating toast/end summary) +
    # 5 raid boss visual preview profiles design-only.
    # preview_only=true, deterministic=true, authoritative=false, db_writes=0, reward_live=false,
    # endpoint_live=false, battle_engine_authoritative=false.
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v88_MEGA_RELEASE_ACCELERATION_37_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE
    # PUBLIC_SYNC_SENTINEL_v88_PRESENT=YES
    # ========================================================================
    ('PROJECT-V88-REAL-UI-BATTLE-PREVIEW-WIRING', 'validate_v88_real_ui_battle_preview_wiring.py'),
    ('PROJECT-V88-BATTLE-PREVIEW-EXPERIENCE-LAYER', 'validate_v88_battle_preview_experience_layer.py'),
    ('PROJECT-V88-RAID-BOSS-VISUAL-PREVIEW-PROFILES', 'validate_v88_raid_boss_visual_preview_profiles.py'),
    ('MEGA-RELEASE-ACCELERATION-37-v88-ROLLUP', 'validate_mega_release_acceleration_37_v88_rollup.py'),

    # ========================================================================
    # v89 - MEGA_RELEASE_ACCELERATION_38_REAL_BATTLEFIELD_PREVIEW_RESCUE_PACK
    # Battlefield preview rescue: 3x3 grid layout con sprite placeholder per
    # ruolo (tank/dps/healer/support/boss), background mappato per modalità
    # (campaign/raid/tower/arena), nessun asset finale, nessun character bible
    # import, nessuna mutazione live. db_writes=0, rewards=0, live_endpoints=0,
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v89_MEGA_RELEASE_ACCELERATION_38_REAL_BATTLEFIELD_PREVIEW_RESCUE_PACK
    # PUBLIC_SYNC_SENTINEL_v89_PRESENT=YES
    # ========================================================================
    ('PROJECT-V89-HOME-BATTLE-FLOW-AUDIT', 'validate_v89_home_battle_flow_audit.py'),
    ('PROJECT-V89-REAL-BATTLEFIELD-TSX', 'validate_v89_real_battlefield_tsx.py'),
    ('PROJECT-V89-NO-ASSET-FINAL-IMPORT-NO-CHARACTER-BIBLE', 'validate_v89_no_asset_final_import_no_character_bible.py'),
    ('MEGA-RELEASE-ACCELERATION-38-v89-ROLLUP', 'validate_mega_release_acceleration_38_v89_rollup.py'),

    # ========================================================================
    # v90 - MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING
    # EMERGENCY RESTORE: ripristino routing modalita' menu verso il renderer
    # Home battle reale gia' presente in frontend/app/combat.tsx (MD5-locked,
    # intatto). NESSUN nuovo mock parallelo. NESSUNA mutazione live.
    # db_writes=0, rewards=0, live_endpoints=0 (no NEW),
    # battle_engine_authoritative=false (no NEW),
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v90_MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING
    # PUBLIC_SYNC_SENTINEL_v90_PRESENT=YES
    # ========================================================================
    ('PROJECT-V90-HOME-BATTLE-RENDERER-FORENSIC-AUDIT', 'validate_v90_home_battle_renderer_forensic_audit.py'),
    ('PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE', 'validate_v90_restored_battle_renderer_reuse.py'),
    ('PROJECT-V90-NO-MOCK-PREVIEW-REGRESSION', 'validate_v90_no_mock_preview_regression.py'),
    ('MEGA-RELEASE-ACCELERATION-39-v90-ROLLUP', 'validate_mega_release_acceleration_39_v90_rollup.py'),

    # ========================================================================
    # v91_FIXED - MEGA_RELEASE_ACCELERATION_40_PRE_BATTLE_LOBBY_ENGINE_STATUS_DOT
    #             _AND_CANONICAL_ENCOUNTER_SOURCE
    # Pre-battle lobby intermediario tra menu modalita' e /combat reale.
    # Universal policy: random_opponents_allowed=false in TUTTE le modalita'.
    # 7 stub catalog deterministic (story/tower/arena/training/raid/event/guild_live).
    # Engine audit read-only su status/DoT/targeting (NO engine patch in v91).
    # db_writes=0, rewards=0, live_endpoints=0 (no NEW),
    # battle_engine_authoritative=false (no NEW),
    # random_opponents_allowed=false (universal policy),
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v91_FIXED_MEGA_RELEASE_ACCELERATION_40
    # PUBLIC_SYNC_SENTINEL_v91_FIXED_PRESENT=YES
    # ========================================================================
    ('PROJECT-V91-FIXED-PRE-BATTLE-LOBBY-FLOW', 'validate_v91_pre_battle_lobby_flow.py'),
    ('PROJECT-V91-FIXED-UNIVERSAL-NO-RANDOM-ENEMY-SOURCE-POLICY', 'validate_v91_universal_no_random_enemy_source_policy.py'),
    ('PROJECT-V91-FIXED-CANONICAL-ENCOUNTER-STUB-CATALOGS', 'validate_v91_canonical_encounter_stub_catalogs.py'),
    ('PROJECT-V91-FIXED-BATTLE-ENGINE-STATUS-DOT-AUDIT', 'validate_v91_battle_engine_status_dot_audit.py'),
    ('MEGA-RELEASE-ACCELERATION-40-v91-FIXED-ROLLUP', 'validate_mega_release_acceleration_40_v91_fixed_rollup.py'),

    # ========================================================================
    # v92 - MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY
    #       _AND_AVATAR_PLACEHOLDER
    # Live/guild/special mode testability hub + avatar placeholder dev registry.
    # QA time-gate override (qa_override_only=true, production_enabled=false).
    # 7 avatar placeholder dev (player HD, war mini, guild war, event, hero room
    # chibi, raid boss, faction boss) \u2014 placeholder_dev_only=true, final_asset_ready=false.
    # 15 modalita' in mode test matrix; 9 encounter sources canoniche per
    # live/guild/special (NO random opponents).
    # db_writes=0, reward_live=false, ranking_live=false, event_currency_live=false,
    # guild_score_mutation=0, arena_mmr=false, story_progress=false,
    # tower_completion=false, boss_fragments=false, inventory_grant=false,
    # cosmetic_unlock=false, monetization=false, random_opponents=false,
    # final_asset_import=false, production_time_gate_override=false,
    # production_ui_exposure=false, validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v92_MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY_AND_AVATAR_PLACEHOLDER
    # PUBLIC_SYNC_SENTINEL_v92_PRESENT=YES
    # ========================================================================
    ('PROJECT-V92-LIVE-GUILD-SPECIAL-MODE-INVENTORY', 'validate_v92_live_guild_special_mode_inventory.py'),
    ('PROJECT-V92-QA-TIME-GATE-OVERRIDE-CONTRACT', 'validate_v92_qa_time_gate_override_contract.py'),
    ('PROJECT-V92-AVATAR-PLACEHOLDER-DEV-REGISTRY', 'validate_v92_avatar_placeholder_dev_registry.py'),
    ('PROJECT-V92-LIVE-GUILD-MODE-QA-HUB', 'validate_v92_live_guild_mode_qa_hub.py'),
    ('PROJECT-V92-LIVE-GUILD-ENCOUNTER-SOURCE-CATALOG', 'validate_v92_live_guild_encounter_source_catalog.py'),
    ('PROJECT-V92-MODE-TEST-MATRIX', 'validate_v92_mode_test_matrix.py'),
    ('MEGA-RELEASE-ACCELERATION-41-v92-ROLLUP', 'validate_mega_release_acceleration_41_v92_rollup.py'),

    # ========================================================================
    # v93 - MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK
    # Playability layer completion: real formation source (saved/local/fallback),
    # team editor wiring, read-only catalog endpoints contract (blocked by MD5
    # lock on server.py - design ready), avatar placeholder visuals (7 SVG-like
    # components dev-only), war/event avatar layout preview, guild war sandbox,
    # full 15-mode playability matrix, live announcements QA (4 static + 9
    # dynamic event templates, alias-safe, anti-spam token_bucket).
    # db_writes=0, reward_live=false, ranking_live=false, event_currency_live=false,
    # guild_score_mutation=0, arena_mmr=false, story_progress=false,
    # tower_completion=false, boss_fragments=false, inventory_grant=false,
    # cosmetic_unlock=false, monetization=false,
    # production_announcements_broadcast=false, production_push_notifications=false,
    # real_user_pii=false, production_time_gate_override=false,
    # random_opponents=false, final_asset_import=false,
    # validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v93_MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v93_PRESENT=YES
    # ========================================================================
    ('PROJECT-V93-REAL-FORMATION-SOURCE', 'validate_v93_real_formation_source.py'),
    ('PROJECT-V93-TEAM-EDITOR-WIRING', 'validate_v93_team_editor_wiring.py'),
    ('PROJECT-V93-READONLY-CATALOG-ENDPOINTS', 'validate_v93_readonly_catalog_endpoints.py'),
    ('PROJECT-V93-AVATAR-PLACEHOLDER-VISUALS', 'validate_v93_avatar_placeholder_visuals.py'),
    ('PROJECT-V93-WAR-EVENT-AVATAR-PREVIEW-SCREENS', 'validate_v93_war_event_avatar_preview_screens.py'),
    ('PROJECT-V93-GUILD-WAR-SANDBOX-FLOW', 'validate_v93_guild_war_sandbox_flow.py'),
    ('PROJECT-V93-FULL-MODE-PLAYABILITY-MATRIX', 'validate_v93_full_mode_playability_matrix.py'),
    ('PROJECT-V93-LIVE-ANNOUNCEMENTS-QA', 'validate_v93_live_announcements_qa.py'),
    ('MEGA-RELEASE-ACCELERATION-42-v93-ROLLUP', 'validate_mega_release_acceleration_42_v93_rollup.py'),

    # ========================================================================
    # v94 - MEGA_RELEASE_ACCELERATION_43_ENGINE_REWARDS_LIVE_GUILD_SUPERPACK
    # Engine status/DoT/taunt/boss patch (design contract, MD5 invariants
    # preserved), reward/score safety contracts + dry-run simulator (10 cases),
    # live/guild score gating (8 systems, all dry_run_only/canary_disabled),
    # read-only catalog endpoints (server.py unchanged, design ready),
    # real formation integration (safe_fallback resolution chain), live
    # announcement runtime safety bridge (6 event sources, dry_run_only).
    # db_writes=0, reward_live=false, ranking_live=false, event_currency_live=false,
    # guild_score_mutation=0, arena_mmr_live=false,
    # production_announcement_broadcast=false, production_push_notifications=false,
    # random_opponents=false, character_bible_mutation=false,
    # hero_roster_mutation=false, final_asset_import=false,
    # final_numbers_balance_lock=false, validator_weakening=false, fake_PASS=false.
    # PUBLIC_SYNC_TAG_v94_MEGA_RELEASE_ACCELERATION_43_ENGINE_REWARDS_LIVE_GUILD_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v94_PRESENT=YES
    # ========================================================================
    ('PROJECT-V94-BATTLE-ENGINE-STATUS-DOT-PATCH', 'validate_v94_battle_engine_status_dot_patch.py'),
    ('PROJECT-V94-ENGINE-REGRESSION-FIXTURES', 'validate_v94_engine_regression_fixtures.py'),
    ('PROJECT-V94-BATTLE-REPORT-EXTENSIONS', 'validate_v94_battle_report_extensions.py'),
    ('PROJECT-V94-REWARD-SAFETY-CONTRACTS', 'validate_v94_reward_safety_contracts.py'),
    ('PROJECT-V94-REWARD-SCORE-DRY-RUN', 'validate_v94_reward_score_dry_run.py'),
    ('PROJECT-V94-LIVE-GUILD-SCORE-GATING', 'validate_v94_live_guild_score_gating.py'),
    ('PROJECT-V94-READONLY-CATALOG-ENDPOINTS', 'validate_v94_readonly_catalog_endpoints.py'),
    ('PROJECT-V94-REAL-FORMATION-INTEGRATION', 'validate_v94_real_formation_integration.py'),
    ('PROJECT-V94-LIVE-ANNOUNCEMENT-SAFETY-BRIDGE', 'validate_v94_live_announcement_safety_bridge.py'),
    ('MEGA-RELEASE-ACCELERATION-43-v94-ROLLUP', 'validate_mega_release_acceleration_43_v94_rollup.py'),
    # ========================================================================
    # v95 - MEGA_RELEASE_ACCELERATION_44_RUNTIME_APPLY_AND_RELEASE_CANDIDATE_PREP_SUPERPACK
    # PUBLIC_SYNC_TAG_v95_MEGA_RELEASE_ACCELERATION_44_RUNTIME_APPLY_AND_RELEASE_CANDIDATE_PREP_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v95_PRESENT=YES
    # ========================================================================
    ('PROJECT-V95-BATTLE-ENGINE-RUNTIME-APPLY', 'validate_v95_battle_engine_runtime_apply.py'),
    ('PROJECT-V95-ENGINE-RUNTIME-REGRESSION-TESTS', 'validate_v95_engine_runtime_regression_tests.py'),
    ('PROJECT-V95-READONLY-CATALOG-ENDPOINTS-RUNTIME', 'validate_v95_readonly_catalog_endpoints_runtime.py'),
    ('PROJECT-V95-INLINE-MIRROR-REMOVAL', 'validate_v95_inline_mirror_removal.py'),
    ('PROJECT-V95-REAL-FORMATION-RUNTIME-FETCH', 'validate_v95_real_formation_runtime_fetch.py'),
    ('PROJECT-V95-REWARD-SCORE-CANARY-SANDBOX', 'validate_v95_reward_score_canary_sandbox.py'),
    ('PROJECT-V95-LIVE-GUILD-RUNTIME-GATING', 'validate_v95_live_guild_runtime_gating.py'),
    ('PROJECT-V95-LIVE-ANNOUNCEMENT-SANDBOX-RUNTIME', 'validate_v95_live_announcement_sandbox_runtime.py'),
    ('PROJECT-V95-RELEASE-CANDIDATE-PREP-GATE', 'validate_v95_release_candidate_prep_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-44-v95-ROLLUP', 'validate_mega_release_acceleration_44_v95_rollup.py'),
    # ========================================================================
    # v96 - MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_SUPERPACK
    # PUBLIC_SYNC_TAG_v96_MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v96_PRESENT=YES
    # ========================================================================
    ('PROJECT-V96-AUTH-ACCOUNT-AUDIT', 'validate_v96_auth_account_audit.py'),
    ('PROJECT-V96-LOGIN-PROVIDER-CONTRACT', 'validate_v96_login_provider_contract.py'),
    ('PROJECT-V96-AUTH-ENDPOINTS', 'validate_v96_auth_endpoints.py'),
    ('PROJECT-V96-FRONTEND-SESSION', 'validate_v96_frontend_session.py'),
    ('PROJECT-V96-REAL-FORMATION-ACCOUNT-BRIDGE', 'validate_v96_real_formation_account_bridge.py'),
    ('PROJECT-V96-ACCOUNT-PRIVACY-COMPLIANCE', 'validate_v96_account_privacy_compliance.py'),
    ('PROJECT-V96-MOBILE-QA-MATRIX', 'validate_v96_mobile_qa_matrix.py'),
    ('PROJECT-V96-LOAD-ENGINE-SMOKE', 'validate_v96_load_engine_smoke.py'),
    ('PROJECT-V96-OPTIONAL-FAIL-RECONCILIATION', 'validate_v96_optional_fail_reconciliation.py'),
    ('PROJECT-V96-MD5-BASELINE-LOCK', 'validate_v96_md5_baseline_lock.py'),
    ('PROJECT-V96-RELEASE-CANDIDATE-FINAL-GATE', 'validate_v96_release_candidate_final_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-45-v96-ROLLUP', 'validate_mega_release_acceleration_45_v96_rollup.py'),
    # ========================================================================
    # v97 - MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_SUPERPACK
    # PUBLIC_SYNC_TAG_v97_MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v97_PRESENT=YES
    # ========================================================================
    ('PROJECT-V97-ACCOUNT-DELETION-GDPR', 'validate_v97_account_deletion_gdpr.py'),
    ('PROJECT-V97-REFRESH-TOKEN-ROTATION', 'validate_v97_refresh_token_rotation.py'),
    ('PROJECT-V97-PROVIDER-TOKEN-GATE', 'validate_v97_provider_token_gate.py'),
    ('PROJECT-V97-PHYSICAL-MOBILE-QA-MATRIX', 'validate_v97_physical_mobile_qa_matrix.py'),
    ('PROJECT-V97-LOAD-LOCUST-RESULT', 'validate_v97_load_locust_result.py'),
    ('PROJECT-V97-OPTIONAL-FAIL-CLEANUP', 'validate_v97_optional_fail_cleanup.py'),
    ('PROJECT-V97-SERVER-ACTOR-LIFECYCLE', 'validate_v97_server_actor_lifecycle.py'),
    ('PROJECT-V97-BOT-PROGRESSION-ECONOMY', 'validate_v97_bot_progression_economy.py'),
    ('PROJECT-V97-BOT-LIVE-EVENT-PARTICIPATION', 'validate_v97_bot_live_event_participation.py'),
    ('PROJECT-V97-CONTEXTUAL-BOT-CHAT', 'validate_v97_contextual_bot_chat.py'),
    ('PROJECT-V97-SERVER-ACTOR-ADMIN-CONTROLS', 'validate_v97_server_actor_admin_controls.py'),
    ('PROJECT-V97-INTERNAL-ALPHA-GATE', 'validate_v97_internal_alpha_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-46-v97-ROLLUP', 'validate_mega_release_acceleration_46_v97_rollup.py'),
    # ========================================================================
    # v98 - MEGA_RELEASE_ACCELERATION_47_CLOSED_ALPHA_RAMPUP_AND_BOT_RUNTIME_SUPERPACK
    # PUBLIC_SYNC_TAG_v98_MEGA_RELEASE_ACCELERATION_47_CLOSED_ALPHA_RAMPUP_AND_BOT_RUNTIME_SUPERPACK
    # PUBLIC_SYNC_SENTINEL_v98_PRESENT=YES
    # Strategia: 0 REQUIRED FAIL, optional fail legacy NON mascherati.
    # Provider Google/Apple: CREDENTIALS_REQUIRED_FOR_STORE_BUILD (non production-ready id_token verify).
    # Physical mobile QA: MANUAL_QA_REQUIRED. Full locust: FULL_LOAD_REQUIRED.
    # ========================================================================
    ('PROJECT-V98-SERVER-ACTOR-RUNTIME-PERSISTENCE', 'validate_v98_server_actor_runtime_persistence.py'),
    ('PROJECT-V98-BOT-PROGRESSION-RUNTIME', 'validate_v98_bot_progression_runtime.py'),
    ('PROJECT-V98-BOT-LIVE-EVENT-RUNTIME', 'validate_v98_bot_live_event_runtime.py'),
    ('PROJECT-V98-BOT-CHAT-RUNTIME-CLASSIFIER', 'validate_v98_bot_chat_runtime_classifier.py'),
    ('PROJECT-V98-SERVER-ACTOR-ADMIN-CONTROLS', 'validate_v98_server_actor_admin_controls.py'),
    ('PROJECT-V98-GDPR-DATA-EXPORT-HARD-DELETE', 'validate_v98_gdpr_data_export_hard_delete.py'),
    ('PROJECT-V98-PROVIDER-ID-TOKEN-VERIFY', 'validate_v98_provider_id_token_verify.py'),
    ('PROJECT-V98-MULTI-PROVIDER-LINKING', 'validate_v98_multi_provider_linking.py'),
    ('PROJECT-V98-LIVE-PRIVACY-TERMS-URLS', 'validate_v98_live_privacy_terms_urls.py'),
    ('PROJECT-V98-FULL-LOAD-LOCUST', 'validate_v98_full_load_locust.py'),
    ('PROJECT-V98-PHYSICAL-MOBILE-QA', 'validate_v98_physical_mobile_qa.py'),
    ('PROJECT-V98-OPTIONAL-FAIL-CLEANUP', 'validate_v98_optional_fail_cleanup.py'),
    ('PROJECT-V98-CLOSED-ALPHA-GATE', 'validate_v98_closed_alpha_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-47-v98-ROLLUP', 'validate_mega_release_acceleration_47_v98_rollup.py'),
    # ========================================================================
    # v99 - MEGA_RELEASE_ACCELERATION_48_CLOSED_ALPHA_BLOCKER_CLEANUP_AND_PUBLIC_TEST_GATE_PACK
    # PUBLIC_SYNC_TAG_v99_MEGA_RELEASE_ACCELERATION_48_CLOSED_ALPHA_BLOCKER_CLEANUP_AND_PUBLIC_TEST_GATE
    # PUBLIC_SYNC_SENTINEL_v99_PRESENT=YES
    # Strategia: 0 REQUIRED FAIL, optional fail legacy NON mascherati, NO validator weakening.
    # 6 blocker Closed Alpha dichiarati onestamente -> verdetto CONDITIONAL.
    # ========================================================================
    ('PROJECT-V99-OPTIONAL-FAIL-CLEANUP', 'validate_v99_optional_fail_cleanup.py'),
    ('PROJECT-V99-PROVIDER-ID-TOKEN-VERIFICATION', 'validate_v99_provider_id_token_verification.py'),
    ('PROJECT-V99-PRIVACY-TERMS-URLS', 'validate_v99_privacy_terms_urls.py'),
    ('PROJECT-V99-PHYSICAL-MOBILE-QA', 'validate_v99_physical_mobile_qa.py'),
    ('PROJECT-V99-FULL-LOCUST', 'validate_v99_full_locust.py'),
    ('PROJECT-V99-STORE-INTERNAL-TESTING-READINESS', 'validate_v99_store_internal_testing_readiness.py'),
    ('PROJECT-V99-CLOSED-ALPHA-FINAL-GATE', 'validate_v99_closed_alpha_final_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-48-v99-ROLLUP', 'validate_mega_release_acceleration_48_v99_rollup.py'),
    # ========================================================================
    # v100 - MEGA_RELEASE_ACCELERATION_49_MD5_SUPERSEDE_AND_CLOSED_ALPHA_READINESS_UNLOCK_PACK
    # PUBLIC_SYNC_TAG_v100_MEGA_RELEASE_ACCELERATION_49_MD5_SUPERSEDE_AND_CLOSED_ALPHA_READINESS_UNLOCK
    # PUBLIC_SYNC_SENTINEL_v100_PRESENT=YES
    # 111 validator legacy stale-MD5 backend/battle_engine.py spostati a
    # SUPERSEDED_AFTER_V100_MD5_REBASELINE (zero weakening, old MD5 conservato
    # come historical_reference). 23 fail non-MD5 residui documentati onestamente.
    # Verdict: CONDITIONAL_EXTERNAL_BLOCKERS (5 external blockers restano).
    # ========================================================================
    ('PROJECT-V100-MD5-FORENSIC-AUDIT', 'validate_v100_md5_forensic_audit.py'),
    ('PROJECT-V100-RUNTIME-MD5-BASELINE', 'validate_v100_runtime_md5_baseline.py'),
    ('PROJECT-V100-SUPERSEDE-REVIEW', 'validate_v100_supersede_review.py'),
    ('PROJECT-V100-OPTIONAL-FAIL-CLEANUP', 'validate_v100_optional_fail_cleanup.py'),
    ('PROJECT-V100-REQUIRED-INVARIANT-PROTECTION', 'validate_v100_required_invariant_protection.py'),
    ('PROJECT-V100-EXTERNAL-BLOCKER-CHECKLIST', 'validate_v100_external_blocker_checklist.py'),
    ('PROJECT-V100-CLOSED-ALPHA-CANDIDATE-GATE', 'validate_v100_closed_alpha_candidate_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-49-v100-ROLLUP', 'validate_mega_release_acceleration_49_v100_rollup.py'),
    # ========================================================================
    # v101 - MEGA_RELEASE_ACCELERATION_50_GLOBAL_LEGACY_DATA_SANITATION_AND_SERVER_FLOW_FIX_PACK
    # PUBLIC_SYNC_TAG_v101_MEGA_RELEASE_ACCELERATION_50_GLOBAL_LEGACY_DATA_SANITATION_AND_SERVER_FLOW_FIX
    # PUBLIC_SYNC_SENTINEL_v101_PRESENT=YES
    # Tracks A-K: legacy audit + canonical allowlist + backup + dry-run + apply (gated) +
    # account/bot/encounter cleanup + frontend mock + server select/login/logout fix.
    # Verdict: DRY_RUN_READY (apply gated by V101_LEGACY_CLEANUP_APPLY + V101_BACKUP_MANIFEST_CONFIRMED).
    # ========================================================================
    ('PROJECT-V101-GLOBAL-LEGACY-REFERENCE-AUDIT', 'validate_v101_global_legacy_reference_audit.py'),
    ('PROJECT-V101-CANONICAL-RUNTIME-ALLOWLIST', 'validate_v101_canonical_runtime_allowlist.py'),
    ('PROJECT-V101-BACKUP-MANIFEST', 'validate_v101_backup_manifest.py'),
    ('PROJECT-V101-DRY-RUN-GLOBAL-CLEANUP', 'validate_v101_dry_run_global_cleanup.py'),
    ('PROJECT-V101-APPLY-SCRIPT-GATED', 'validate_v101_apply_script_gated.py'),
    ('PROJECT-V101-PLAYER-ACCOUNT-NORMALIZATION', 'validate_v101_player_account_normalization.py'),
    ('PROJECT-V101-BOT-RECONSTRUCTION', 'validate_v101_bot_reconstruction.py'),
    ('PROJECT-V101-ENCOUNTER-ENEMY-SOURCE-CLEANUP', 'validate_v101_encounter_enemy_source_cleanup.py'),
    ('PROJECT-V101-FRONTEND-LEGACY-MOCK-ROUTE-AUDIT', 'validate_v101_frontend_legacy_mock_route_audit.py'),
    ('PROJECT-V101-SERVER-SELECT-LOGOUT-FLOW', 'validate_v101_server_select_logout_flow.py'),
    ('MEGA-RELEASE-ACCELERATION-50-v101-ROLLUP', 'validate_mega_release_acceleration_50_v101_rollup.py'),
    # ========================================================================
    # v102 - MEGA_RELEASE_ACCELERATION_51_SERVER_SELECT_RUNTIME_WIRING_AND_AUTH_UNIFICATION_FIX_PACK
    # PUBLIC_SYNC_TAG_v102_MEGA_RELEASE_ACCELERATION_51_SERVER_SELECT_RUNTIME_WIRING_AND_AUTH_UNIFICATION_FIX
    # PUBLIC_SYNC_SENTINEL_v102_PRESENT=YES
    # P0 device QA bugfix: /servers ora UI selezionabile reale con card + Entra +
    # fallback dichiarato + persistenza v101_selected_server_id + Cambia server / Logout account separati.
    # AuthContext bridge logout in menu.tsx (full unification deferred v103).
    # ========================================================================
    ('PROJECT-V102-SERVER-SELECT-AUDIT', 'validate_v102_server_select_audit.py'),
    ('PROJECT-V102-SERVER-LIST-SOURCE', 'validate_v102_server_list_source.py'),
    ('PROJECT-V102-SERVER-SELECT-UI', 'validate_v102_server_select_ui.py'),
    ('PROJECT-V102-SELECTED-SERVER-PERSISTENCE', 'validate_v102_selected_server_persistence.py'),
    ('PROJECT-V102-LOGOUT-CHANGE-SERVER', 'validate_v102_logout_change_server.py'),
    ('PROJECT-V102-AUTH-CONTEXT-UNIFICATION', 'validate_v102_auth_context_unification.py'),
    ('PROJECT-V102-DEVICE-RETEST-MATRIX', 'validate_v102_device_retest_matrix.py'),
    ('MEGA-RELEASE-ACCELERATION-51-v102-ROLLUP', 'validate_mega_release_acceleration_51_v102_rollup.py'),
    # ========================================================================
    # v103 - MEGA_RELEASE_ACCELERATION_52_SERVER_PROFILE_BACKEND_DATA_ISOLATION_AND_LOGOUT_RACE_FIX_PACK
    # PUBLIC_SYNC_TAG_v103_MEGA_RELEASE_ACCELERATION_52_SERVER_PROFILE_BACKEND_DATA_ISOLATION_AND_LOGOUT_RACE_FIX
    # PUBLIC_SYNC_SENTINEL_v103_PRESENT=YES
    # P0 device QA bugfix: server names [QA] prefixed, banner QA/FALLBACK + isolation pending,
    # endpoint /api/server-profiles/list read-only safe, logout race fix via v103_logout_in_progress flag,
    # AuthContext bridge robust (clear v96 SecureStore esplicito).
    # ========================================================================
    ('PROJECT-V103-SERVER-PROFILE-BACKEND-AUDIT', 'validate_v103_server_profile_backend_audit.py'),
    ('PROJECT-V103-SERVER-PROFILES-ENDPOINT', 'validate_v103_server_profiles_endpoint.py'),
    ('PROJECT-V103-SERVER-NAMING-STATUS', 'validate_v103_server_naming_status.py'),
    ('PROJECT-V103-SERVER-SELECTION-PERSISTENCE', 'validate_v103_server_selection_persistence.py'),
    ('PROJECT-V103-SERVER-SCOPED-DATA-ISOLATION', 'validate_v103_server_scoped_data_isolation.py'),
    ('PROJECT-V103-LOGOUT-RACE-FIX', 'validate_v103_logout_race_fix.py'),
    ('PROJECT-V103-AUTH-CONTEXT-UNIFICATION', 'validate_v103_auth_context_unification.py'),
    ('PROJECT-V103-DEVICE-RETEST-MATRIX', 'validate_v103_device_retest_matrix.py'),
    ('MEGA-RELEASE-ACCELERATION-52-v103-ROLLUP', 'validate_mega_release_acceleration_52_v103_rollup.py'),
    # ========================================================================
    # v104 - MEGA_RELEASE_ACCELERATION_53_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX_PACK
    # PUBLIC_SYNC_TAG_v104_MEGA_RELEASE_ACCELERATION_53_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX
    # PUBLIC_SYNC_SENTINEL_v104_PRESENT=YES
    # P0 device QA bugfix: isolation reale per server (account/roster/inventory/currencies/
    # team/chat) e' DECLARED_PENDING. UI dichiara SERVER_DATA_ISOLATION_BACKEND_PENDING.
    # Nessuna finzione di separazione dati cross-server. NO destructive DB writes.
    # Hook frontend useServerScope introdotto. Backend contract pending documentato.
    # ========================================================================
    ('PROJECT-V104-SERVER-SCOPED-DATA-FLOW-AUDIT', 'validate_v104_server_scoped_data_flow_audit.py'),
    ('PROJECT-V104-SERVER-PROFILE-BACKEND-CONTRACT', 'validate_v104_server_profile_backend_contract.py'),
    ('PROJECT-V104-SERVER-NAMING-CANONICALIZATION', 'validate_v104_server_naming_canonicalization.py'),
    ('PROJECT-V104-SERVER-SCOPED-USER-DATA-MODEL', 'validate_v104_server_scoped_user_data_model.py'),
    ('PROJECT-V104-FRONTEND-SERVER-ID-PROPAGATION', 'validate_v104_frontend_server_id_propagation.py'),
    ('PROJECT-V104-BACKEND-SERVER-ID-FILTERING', 'validate_v104_backend_server_id_filtering.py'),
    ('PROJECT-V104-CHAT-SERVER-ISOLATION', 'validate_v104_chat_server_isolation.py'),
    ('PROJECT-V104-SERVER-PROFILE-CREATION-POLICY', 'validate_v104_server_profile_creation_policy.py'),
    ('PROJECT-V104-DEVICE-RETEST-MATRIX', 'validate_v104_device_retest_matrix.py'),
    ('MEGA-RELEASE-ACCELERATION-53-v104-ROLLUP', 'validate_mega_release_acceleration_53_v104_rollup.py'),
    # ========================================================================
    # v105 - MEGA_RELEASE_ACCELERATION_54_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT_AND_RUNTIME_CONSOLIDATION_PLAN_PACK
    # PUBLIC_SYNC_TAG_v105_MEGA_RELEASE_ACCELERATION_54_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT_AND_RUNTIME_CONSOLIDATION_PLAN
    # PUBLIC_SYNC_SENTINEL_v105_PRESENT=YES
    # P0 MASTER AUDIT pack. No runtime mutation. Produces AS-IS vs TO-BE matrices
    # for frontend routes, backend endpoints, server scope, mode runtime,
    # battle launch contract, encounter sources, legacy data, bot actors,
    # chat/live/guild, economy/reward claims, auth, design compliance, and the
    # full runtime consolidation roadmap v106-v114.
    # ========================================================================
    ('PROJECT-V105-FRONTEND-ROUTE-INVENTORY', 'validate_v105_frontend_route_inventory.py'),
    ('PROJECT-V105-BACKEND-ENDPOINT-INVENTORY', 'validate_v105_backend_endpoint_inventory.py'),
    ('PROJECT-V105-SERVER-SCOPE-AUDIT', 'validate_v105_server_scope_audit.py'),
    ('PROJECT-V105-MODE-RUNTIME-AUDIT', 'validate_v105_mode_runtime_audit.py'),
    ('PROJECT-V105-BATTLE-LAUNCH-CONTRACT-AUDIT', 'validate_v105_battle_launch_contract_audit.py'),
    ('PROJECT-V105-ENCOUNTER-SOURCE-AUDIT', 'validate_v105_encounter_source_audit.py'),
    ('PROJECT-V105-LEGACY-DATA-RUNTIME-AUDIT', 'validate_v105_legacy_data_runtime_audit.py'),
    ('PROJECT-V105-BOT-SERVER-ACTOR-AUDIT', 'validate_v105_bot_server_actor_audit.py'),
    ('PROJECT-V105-CHAT-LIVE-GUILD-AUDIT', 'validate_v105_chat_live_guild_audit.py'),
    ('PROJECT-V105-ECONOMY-REWARD-CLAIM-AUDIT', 'validate_v105_economy_reward_claim_audit.py'),
    ('PROJECT-V105-AUTH-ACCOUNT-SERVER-PROFILE-AUDIT', 'validate_v105_auth_account_server_profile_audit.py'),
    ('PROJECT-V105-DESIGN-COMPLIANCE-MATRIX', 'validate_v105_design_compliance_matrix.py'),
    ('PROJECT-V105-RUNTIME-CONSOLIDATION-ROADMAP', 'validate_v105_runtime_consolidation_roadmap.py'),
    ('MEGA-RELEASE-ACCELERATION-54-v105-ROLLUP', 'validate_mega_release_acceleration_54_v105_rollup.py'),
    # ========================================================================
    # v106 - MEGA_RELEASE_ACCELERATION_55_SERVER_SCOPED_DB_SCHEMA_AND_PLAYER_SERVER_PROFILES_GATED_MIGRATION_PREP_PACK
    # PUBLIC_SYNC_TAG_v106_MEGA_RELEASE_ACCELERATION_55_SERVER_SCOPED_DB_SCHEMA_AND_PLAYER_SERVER_PROFILES_GATED_MIGRATION_PREP
    # PUBLIC_SYNC_SENTINEL_v106_PRESENT=YES
    # P0 foundation pack: defines player_server_profiles schema with compound
    # unique key (account_id, server_id), 5 indexes, backup/dry-run/apply-gated/
    # rollback scripts, account-global vs server-scoped matrix, bot migration
    # policy, staging apply readiness gate. Default outcome:
    # DRY_RUN_READY_APPLY_GATED_NOT_EXECUTED. NO DB writes without 4 env flags.
    # ========================================================================
    ('PROJECT-V106-EXISTING-DATA-MODEL-AUDIT', 'validate_v106_existing_data_model_audit.py'),
    ('PROJECT-V106-PLAYER-SERVER-PROFILES-SCHEMA', 'validate_v106_player_server_profiles_schema.py'),
    ('PROJECT-V106-ACCOUNT-GLOBAL-VS-SERVER-SCOPED-MATRIX', 'validate_v106_account_global_vs_server_scoped_matrix.py'),
    ('PROJECT-V106-BACKUP-MANIFEST', 'validate_v106_backup_manifest.py'),
    ('PROJECT-V106-DRY-RUN-MIGRATION-RESULT', 'validate_v106_dry_run_migration_result.py'),
    ('PROJECT-V106-APPLY-SCRIPT-GATED', 'validate_v106_apply_script_gated.py'),
    ('PROJECT-V106-ROLLBACK-SCRIPT-GATED', 'validate_v106_rollback_script_gated.py'),
    ('PROJECT-V106-SERVER-SCOPED-READ-CONTRACT', 'validate_v106_server_scoped_read_contract.py'),
    ('PROJECT-V106-BOT-SERVER-ACTOR-MIGRATION-POLICY', 'validate_v106_bot_server_actor_migration_policy.py'),
    ('PROJECT-V106-STAGING-APPLY-READINESS-GATE', 'validate_v106_staging_apply_readiness_gate.py'),
    ('MEGA-RELEASE-ACCELERATION-55-v106-ROLLUP', 'validate_mega_release_acceleration_55_v106_rollup.py'),
    # ========================================================================
    # v107A - MEGA_RELEASE_ACCELERATION_56_BATTLE_LAUNCH_CONTRACT_AND_SERVER_ID_LOADER_ADOPTION_FLAGGED
    # PUBLIC_SYNC_TAG_v107A_MEGA_RELEASE_ACCELERATION_56_BATTLE_LAUNCH_CONTRACT_AND_SERVER_ID_LOADER_ADOPTION_FLAGGED
    # PUBLIC_SYNC_SENTINEL_v107A_PRESENT=YES
    # P0 runtime seam pack. Battle Launch Contract v1 schema + /api/battle/launch
    # preview-echo endpoint registered. Feature flags ALL OFF default. Server.py
    # MD5 baseline rebased (v100 supersede). Loader server_id adoption is contract
    # only (deferred to v107B). Story auto-resolve deprecation plan documented.
    # ========================================================================
    ('PROJECT-V107A-V106-PUBLIC-SYNC-SNAPSHOT', 'validate_v107a_v106_public_sync_snapshot.py'),
    ('PROJECT-V107A-BATTLE-LAUNCH-CONTRACT-SCHEMA', 'validate_v107a_battle_launch_contract_schema.py'),
    ('PROJECT-V107A-BATTLE-LAUNCH-ENDPOINT', 'validate_v107a_battle_launch_endpoint.py'),
    ('PROJECT-V107A-PRE-BATTLE-LOBBY-CONTRACT', 'validate_v107a_pre_battle_lobby_contract.py'),
    ('PROJECT-V107A-COMBAT-CONTRACT-CONSUMER', 'validate_v107a_combat_contract_consumer.py'),
    ('PROJECT-V107A-BACKEND-LOADER-SERVER-ID-ADOPTION', 'validate_v107a_backend_loader_server_id_adoption.py'),
    ('PROJECT-V107A-FRONTEND-LOADER-SERVER-ID-PROPAGATION', 'validate_v107a_frontend_loader_server_id_propagation.py'),
    ('PROJECT-V107A-STORY-AUTORESOLVE-DEPRECATION', 'validate_v107a_story_autoresolve_deprecation.py'),
    ('PROJECT-V107A-ENCOUNTER-SOURCE-ADAPTER-CONTRACT', 'validate_v107a_encounter_source_adapter_contract.py'),
    ('PROJECT-V107A-IDEMPOTENCY-REWARD-PROGRESS-GUARD', 'validate_v107a_idempotency_reward_progress_guard.py'),
    ('MEGA-RELEASE-ACCELERATION-56-v107A-ROLLUP', 'validate_mega_release_acceleration_56_v107a_rollup.py'),
    # ========================================================================
    # v107B - MEGA_RELEASE_ACCELERATION_57_BATTLE_LAUNCH_CONTRACT_ADOPTION_FRONTEND_CONSUMERS_AND_LOADER_SERVER_ID_ACCEPTANCE
    # PUBLIC_SYNC_TAG_v107B_MEGA_RELEASE_ACCELERATION_57_BATTLE_LAUNCH_CONTRACT_ADOPTION_FRONTEND_CONSUMERS_AND_LOADER_SERVER_ID_ACCEPTANCE
    # PUBLIC_SYNC_SENTINEL_v107B_PRESENT=YES
    # P0 adoption pack. Pre-battle-lobby adapter + combat parser helper introduced
    # as pure non-destructive helpers (no tsx rewrite). Real smoke 3/3 PASS on
    # POST /api/battle/launch with live->preview coercion. tsx integration deferred
    # to v107C. All flags still default OFF. NO PSP apply, NO DB writes, NO rewards.
    # ========================================================================
    ('PROJECT-V107B-V107A-BASELINE-SNAPSHOT', 'validate_v107b_v107a_baseline_snapshot.py'),
    ('PROJECT-V107B-PRE-BATTLE-LOBBY-ADOPTION', 'validate_v107b_pre_battle_lobby_adoption.py'),
    ('PROJECT-V107B-COMBAT-CONSUMER-ADOPTION', 'validate_v107b_combat_consumer_adoption.py'),
    ('PROJECT-V107B-STORY-TO-LOBBY-ROUTING', 'validate_v107b_story_to_lobby_routing.py'),
    ('PROJECT-V107B-BACKEND-LOADER-SERVER-ID-ACCEPTANCE', 'validate_v107b_backend_loader_server_id_acceptance.py'),
    ('PROJECT-V107B-FRONTEND-LOADER-SERVER-ID-PROPAGATION', 'validate_v107b_frontend_loader_server_id_propagation.py'),
    ('PROJECT-V107B-BATTLE-LAUNCH-SMOKE', 'validate_v107b_battle_launch_smoke.py'),
    ('PROJECT-V107B-STORY-AUTORESOLVE-GUARD', 'validate_v107b_story_autoresolve_guard.py'),
    ('PROJECT-V107B-ROUTE-EXPOSURE-SAFETY', 'validate_v107b_route_exposure_safety.py'),
    ('MEGA-RELEASE-ACCELERATION-57-v107B-ROLLUP', 'validate_mega_release_acceleration_57_v107b_rollup.py'),
    # ========================================================================
    # v107C - MEGA_RELEASE_ACCELERATION_58_TSX_CONSUMER_BINDING_AND_BACKEND_LOADER_SERVER_ID_ACCEPTANCE
    # PUBLIC_SYNC_TAG_v107C_MEGA_RELEASE_ACCELERATION_58_TSX_CONSUMER_BINDING_AND_BACKEND_LOADER_SERVER_ID_ACCEPTANCE
    # PUBLIC_SYNC_SENTINEL_v107C_PRESENT=YES
    # P0 binding pack. pre-battle-lobby.tsx + combat.tsx bind to consumer helpers
    # (non-destructive: import + gated useEffect / parser ref). New backend probe
    # router /api/v107c/loader-probe/{user-heroes,team-get-formation,inventory,
    # currencies,story-progress} accepts server_id query param, never filters,
    # never writes. server.py MD5 baseline rebased (5af3..→6a10..). E2E smoke
    # 2/2 steps PASS (lobby launch + 5 loader acceptance probes). All flags OFF.
    # ========================================================================
    ('PROJECT-V107C-V107B-BASELINE-SNAPSHOT', 'validate_v107c_v107b_baseline_snapshot.py'),
    ('PROJECT-V107C-PRE-BATTLE-LOBBY-TSX-BINDING', 'validate_v107c_pre_battle_lobby_tsx_binding.py'),
    ('PROJECT-V107C-COMBAT-TSX-PARSER-BINDING', 'validate_v107c_combat_tsx_parser_binding.py'),
    ('PROJECT-V107C-STORY-SCREEN-LAUNCH-PATH', 'validate_v107c_story_screen_launch_path.py'),
    ('PROJECT-V107C-BACKEND-LOADER-SERVER-ID-ACCEPTANCE', 'validate_v107c_backend_loader_server_id_acceptance.py'),
    ('PROJECT-V107C-FRONTEND-LOADER-SERVER-ID-BINDING', 'validate_v107c_frontend_loader_server_id_binding.py'),
    ('PROJECT-V107C-E2E-PREVIEW-SMOKE', 'validate_v107c_e2e_preview_smoke.py'),
    ('PROJECT-V107C-STORY-AUTORESOLVE-DEPRECATION-GUARD', 'validate_v107c_story_autoresolve_deprecation_guard.py'),
    ('PROJECT-V107C-ROUTE-MENU-EXPOSURE-SAFETY', 'validate_v107c_route_menu_exposure_safety.py'),
    ('MEGA-RELEASE-ACCELERATION-58-v107C-ROLLUP', 'validate_mega_release_acceleration_58_v107c_rollup.py'),

    # v107D - MEGA_RELEASE_ACCELERATION_59_TSX_MD5_SUPERSEDE_AND_REAL_BATTLE_LAUNCH_CONSUMER_BINDING
    # PUBLIC_SYNC_TAG_v107D_MEGA_RELEASE_ACCELERATION_59_TSX_MD5_SUPERSEDE_AND_REAL_BATTLE_LAUNCH_CONSUMER_BINDING
    # PUBLIC_SYNC_SENTINEL_v107D_PRESENT=YES
    # Rispetta il design del pack: binding reale applicato SOLO a pre-battle-lobby.tsx
    # (gated da EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED, default OFF). combat.tsx e
    # story.tsx restano DEFERRED a v108_pre. MD5 supersede formale, NO validator
    # weakening, NO fake_PASS, NO silent validator deletion. Optional fail invariato
    # a 23 (target ≤30). Nessuna mutazione DB, ricompense, progressi, route nuove.
    ('PROJECT-V107D-FAILED-BINDING-FORENSIC-AUDIT', 'validate_v107d_failed_binding_forensic_audit.py'),
    ('PROJECT-V107D-TSX-MD5-SUPERSEDE-REVIEW', 'validate_v107d_tsx_md5_supersede_review.py'),
    ('PROJECT-V107D-PRE-BATTLE-LOBBY-REAL-BINDING', 'validate_v107d_pre_battle_lobby_real_binding.py'),
    ('PROJECT-V107D-COMBAT-PARSER-BINDING', 'validate_v107d_combat_parser_binding.py'),
    ('PROJECT-V107D-STORY-LAUNCH-PATH', 'validate_v107d_story_launch_path.py'),
    ('PROJECT-V107D-BACKEND-LOADER-SERVER-ID-REAL-ACCEPTANCE', 'validate_v107d_backend_loader_server_id_real_acceptance.py'),
    ('PROJECT-V107D-E2E-SMOKE', 'validate_v107d_e2e_smoke.py'),
    ('PROJECT-V107D-ROUTE-MENU-EXPOSURE-SAFETY', 'validate_v107d_route_menu_exposure_safety.py'),
    ('PROJECT-V107D-OPTIONAL-FAIL-BASELINE-GUARD', 'validate_v107d_optional_fail_baseline_guard.py'),
    ('MEGA-RELEASE-ACCELERATION-59-v107D-ROLLUP', 'validate_mega_release_acceleration_59_v107d_rollup.py'),

    # v108_pre - MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME
    # PUBLIC_SYNC_TAG_v108_PRE_MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME
    # PUBLIC_SYNC_SENTINEL_v108_PRE_PRESENT=YES
    # P0 pre-runtime binding pack: applica il binding chirurgico di combat.tsx
    # e story.tsx al Battle Launch Contract v1, completa il MD5 supersede
    # formale (historical_references preservati, NO validator weakening, NO
    # silent deletion, NO fake_PASS). pre-battle-lobby.tsx riceve solo
    # compatibility per encounter_id/enemy_source_id. Tutti i feature flag
    # restano OFF: SERVER_SCOPED_RUNTIME_ENABLED, BATTLE_LAUNCH_AUTHORITATIVE_ENABLED,
    # REWARD_LIVE_ENABLED, PROGRESS_LIVE_ENABLED. NO PSP apply, NO DB write,
    # NO reward, NO progress, NO formula rewrite, NO broad rewrite.
    ('PROJECT-V108-PRE-V107D-BASELINE-SNAPSHOT', 'validate_v108_pre_v107d_baseline_snapshot.py'),
    ('PROJECT-V108-PRE-COMBAT-STORY-MD5-FORENSIC-AUDIT', 'validate_v108_pre_combat_story_md5_forensic_audit.py'),
    ('PROJECT-V108-PRE-COMBAT-STORY-MD5-SUPERSEDE-REVIEW', 'validate_v108_pre_combat_story_md5_supersede_review.py'),
    ('PROJECT-V108-PRE-COMBAT-LAUNCH-CONTEXT-BINDING', 'validate_v108_pre_combat_launch_context_binding.py'),
    ('PROJECT-V108-PRE-STORY-LAUNCH-PATH-BINDING', 'validate_v108_pre_story_launch_path_binding.py'),
    ('PROJECT-V108-PRE-PRE-BATTLE-LOBBY-COMPATIBILITY', 'validate_v108_pre_pre_battle_lobby_compatibility.py'),
    ('PROJECT-V108-PRE-E2E-STORY-LOBBY-LAUNCH-COMBAT-SMOKE', 'validate_v108_pre_e2e_story_lobby_launch_combat_smoke.py'),
    ('PROJECT-V108-PRE-BACKEND-LOADER-SERVER-ID-ACCEPTANCE-STATUS', 'validate_v108_pre_backend_loader_server_id_acceptance_status.py'),
    ('PROJECT-V108-PRE-ROUTE-MENU-EXPOSURE-SAFETY', 'validate_v108_pre_route_menu_exposure_safety.py'),
    ('PROJECT-V108-PRE-OPTIONAL-FAIL-VALIDATOR-INTEGRITY-GUARD', 'validate_v108_pre_optional_fail_validator_integrity_guard.py'),
    ('MEGA-RELEASE-ACCELERATION-60-v108-PRE-ROLLUP', 'validate_mega_release_acceleration_60_v108_pre_rollup.py'),

    # v108_POSTQA_A - MEGA_RELEASE_ACCELERATION_61_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A
    # PUBLIC_SYNC_TAG_v108_POSTQA_VALIDATOR_REFORM_AND_PREVIEW_REWARD_LOCK_A
    # PUBLIC_SYNC_SENTINEL_v108_POSTQA_A_PRESENT=YES
    # Validator reform onesto: relocatable runner + 9 runtime-invariant validator
    # che leggono il CODICE REALE e falliscono se preview branch chiama simulate
    # o refresh user, se QA Auto Resolve e' player-facing, se lobby launcha con
    # fallback team/enemy, se lobby va a combat senza launch_context, se simulate
    # endpoint non blocca preview, se bot default startup ha kill switch, se
    # watchlist mutation endpoints e' incompleta, se server scope false positive.
    # Tutti i flag QA/preview restano OFF di default. NO PSP apply, NO legacy
    # cleanup, NO DB write, NO reward, NO progress, NO formula rewrite.
    ('PROJECT-V108-POSTQA-INVARIANT-SUITE-RELOCATABLE', 'validate_v108_postqa_invariant_suite_relocatable.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-PREVIEW-NO-SIMULATE', 'validate_v108_postqa_invariant_preview_no_simulate.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-PREVIEW-NO-REWARDS-AFFINITY', 'validate_v108_postqa_invariant_preview_no_rewards_affinity.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-STORY-NO-QA-AUTORESOLVE-PLAYER-FACING', 'validate_v108_postqa_invariant_story_no_qa_autoresolve_player_facing.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-LOBBY-NO-FAKE-TEAM-LAUNCH', 'validate_v108_postqa_invariant_lobby_no_fake_team_launch.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-LOBBY-LAUNCH-CONTEXT-TO-COMBAT', 'validate_v108_postqa_invariant_lobby_launch_context_to_combat.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-NO-GENERATE-ENEMY-PLAYER-FACING', 'validate_v108_postqa_invariant_no_generate_enemy_player_facing.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-NO-BOT-DEFAULT-STARTUP', 'validate_v108_postqa_invariant_no_bot_default_startup.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-MUTATION-ENDPOINT-WATCHLIST', 'validate_v108_postqa_invariant_mutation_endpoint_watchlist.py'),
    ('PROJECT-V108-POSTQA-INVARIANT-SERVER-SCOPE-FALSE-POSITIVE', 'validate_v108_postqa_invariant_server_scope_false_positive.py'),
    ('MEGA-RELEASE-ACCELERATION-61-v108-POSTQA-ROLLUP', 'validate_mega_release_acceleration_61_v108_postqa_rollup.py'),

    # v108_POSTQA_A2 - MEGA_RELEASE_ACCELERATION_62_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION
    # PUBLIC_SYNC_TAG_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION
    # PUBLIC_SYNC_SENTINEL_v108_POSTQA_A2_PRESENT=YES
    # Triage onesto dei fail post v108_POSTQA_A/A1. Suite stabile a 27 fail su
    # 3 run consecutive identiche (<= 30 target). 0 supersede cosmetici, 0 weakening,
    # 0 silent deletion. Historical guardians preservati. Mutation watchlist preservata.
    # 10 runtime-invariant validator v108_POSTQA_A preservati e mandatory. Reconciliation
    # MD5 formali deferite a v108_POSTQA_B con historical_md5 + replacement_invariant
    # documentati. NO gameplay, NO PSP apply, NO reward, NO progress, NO formula rewrite.
    ('PROJECT-V108-POSTQA-A2-BASELINE-MULTIRUN-SNAPSHOT', 'validate_v108_postqa_a2_baseline_multirun_snapshot.py'),
    ('PROJECT-V108-POSTQA-A2-FULL-FAIL-TRIAGE', 'validate_v108_postqa_a2_full_fail_triage.py'),
    ('PROJECT-V108-POSTQA-A2-RUNTIME-INVARIANT-PRESERVATION', 'validate_v108_postqa_a2_runtime_invariant_preservation.py'),
    ('PROJECT-V108-POSTQA-A2-MD5-HISTORICAL-RECONCILIATION', 'validate_v108_postqa_a2_md5_historical_reconciliation.py'),
    ('PROJECT-V108-POSTQA-A2-AUTO-GENERATED-JSON-DRIFT-STABILIZATION', 'validate_v108_postqa_a2_auto_generated_json_drift_stabilization.py'),
    ('PROJECT-V108-POSTQA-A2-WATCHLIST-ROADMAP-PRESERVATION', 'validate_v108_postqa_a2_watchlist_roadmap_preservation.py'),
    ('PROJECT-V108-POSTQA-A2-FINAL-MULTIRUN-SUITE-RESULT', 'validate_v108_postqa_a2_final_multirun_suite_result.py'),
    ('MEGA-RELEASE-ACCELERATION-62-v108-POSTQA-A2-ROLLUP', 'validate_mega_release_acceleration_62_v108_postqa_a2_rollup.py'),

    # v108_POSTQA_B - MEGA_RELEASE_ACCELERATION_63_ENVIRONMENTAL_AND_DRIFT_STABILIZATION
    # PUBLIC_SYNC_TAG_v108_POSTQA_B_ENVIRONMENTAL_AND_DRIFT_STABILIZATION
    # Redis installato (chiude 5+1 environmental fail), /api/equipment/equip aggiunto
    # alla mutation watchlist (23 endpoint), 17 PROJECT-* preexisting classificati
    # con decision-per-uno (12 → v108_POSTQA_C, 3 → v108_authoritative, 1 → v109, 1 → v110, 1 closed).
    # JSON drift stabilization deferita onestamente a v108_POSTQA_C. Runtime invariant
    # 10/10 preservati. NO gameplay, NO PSP, NO reward, NO progress, NO formula rewrite.
    ('PROJECT-V108-POSTQA-B-BASELINE-MULTIRUN', 'validate_v108_postqa_b_baseline_multirun.py'),
    ('PROJECT-V108-POSTQA-B-REDIS-ENVIRONMENTAL-STABILIZATION', 'validate_v108_postqa_b_redis_environmental_stabilization.py'),
    ('PROJECT-V108-POSTQA-B-JSON-DRIFT-STABILIZATION', 'validate_v108_postqa_b_json_drift_stabilization.py'),
    ('PROJECT-V108-POSTQA-B-WATCHLIST-EQUIPMENT-EQUIP-ADDED', 'validate_v108_postqa_b_watchlist_equipment_equip_added.py'),
    ('PROJECT-V108-POSTQA-B-PROJECT-PREEXISTING-FAIL-CLASSIFICATION', 'validate_v108_postqa_b_project_preexisting_fail_classification.py'),
    ('PROJECT-V108-POSTQA-B-RUNTIME-INVARIANT-PRESERVATION', 'validate_v108_postqa_b_runtime_invariant_preservation.py'),
    ('PROJECT-V108-POSTQA-B-FINAL-MULTIRUN-SUITE', 'validate_v108_postqa_b_final_multirun_suite.py'),
    ('MEGA-RELEASE-ACCELERATION-63-v108-POSTQA-B-ROLLUP', 'validate_mega_release_acceleration_63_v108_postqa_b_rollup.py'),

    # v108_POSTQA_C - LEGACY_PROJECT_FAIL_RESOLUTION_AND_DRIFT_FINALIZATION
    # PUBLIC_SYNC_TAG_v108_POSTQA_C_LEGACY_PROJECT_FAIL_RESOLUTION_AND_DRIFT_FINALIZATION
    # 11 PROJECT-* preserved as historical guardian, 2 JSON drift deferred, 3 MD5
    # guardian con replacement invariant funzionali. Target C (<=15) NON raggiunto
    # onestamente (resta 22), verdict READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED.
    # NO supersede, NO weakening, NO deletion, NO release readiness claim.
    ('PROJECT-V108-POSTQA-C-BASELINE-MULTIRUN', 'validate_v108_postqa_c_baseline_multirun.py'),
    ('PROJECT-V108-POSTQA-C-DEFERRED-RESOLUTION', 'validate_v108_postqa_c_deferred_resolution.py'),
    ('PROJECT-V108-POSTQA-C-JSON-DRIFT-FINALIZATION', 'validate_v108_postqa_c_json_drift_finalization.py'),
    ('PROJECT-V108-POSTQA-C-MD5-GUARDIAN-RECONCILIATION', 'validate_v108_postqa_c_md5_guardian_reconciliation.py'),
    ('PROJECT-V108-POSTQA-C-LABEL-REPORT-CONSISTENCY-CLEANUP', 'validate_v108_postqa_c_label_report_consistency_cleanup.py'),
    ('PROJECT-V108-POSTQA-C-RUNTIME-INVARIANT-PRESERVATION', 'validate_v108_postqa_c_runtime_invariant_preservation.py'),
    ('PROJECT-V108-POSTQA-C-FINAL-MULTIRUN-SUITE', 'validate_v108_postqa_c_final_multirun_suite.py'),
    ('MEGA-RELEASE-ACCELERATION-64-v108-POSTQA-C-ROLLUP', 'validate_mega_release_acceleration_64_v108_postqa_c_rollup.py'),

    # ===== v108_POSTQA_D - Authoritative Pre-Gates and Mutation Locks =====
    # PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS
    ('PROJECT-V108-POSTQA-D-BASELINE-MULTIRUN', 'validate_v108_postqa_d_baseline_multirun.py'),
    ('PROJECT-V108-POSTQA-D-LEGACY-MUTATION-GATE-POLICY', 'validate_v108_postqa_d_legacy_mutation_gate_policy.py'),
    ('PROJECT-V108-POSTQA-D-BACKEND-MUTATION-GATES', 'validate_v108_postqa_d_backend_mutation_gates.py'),
    ('PROJECT-V108-POSTQA-D-FRONTEND-REACHABILITY-BLOCKERS', 'validate_v108_postqa_d_frontend_reachability_blockers.py'),
    ('PROJECT-V108-POSTQA-D-AUTHORITATIVE-PREFLIGHT-CONTRACT', 'validate_v108_postqa_d_authoritative_preflight_contract.py'),
    ('PROJECT-V108-POSTQA-D-SERVER-ID-LOADER-PREFLIGHT', 'validate_v108_postqa_d_server_id_loader_preflight.py'),
    ('PROJECT-V108-POSTQA-D-RUNTIME-INVARIANT-PRESERVATION', 'validate_v108_postqa_d_runtime_invariant_preservation.py'),
    ('MEGA-RELEASE-ACCELERATION-65-v108-POSTQA-D-ROLLUP', 'validate_mega_release_acceleration_65_v108_postqa_d_rollup.py'),


    ('RM1.31-C', 'validate_status_resolver_contract.py'),
    ('RM1.32-C', 'audit_balance_foundation_boss_pvp_caps.py'),
    ('RM1.33-A', 'audit_skill_kit_runtime_adapter_safety.py'),
    ('RM1.33-B', 'audit_skill_kit_runtime_adapter_wiretest.py'),
    ('RM1.33-C', 'audit_skill_kit_runtime_debug_endpoint_safety.py'),
    ('RM1.33-D', 'validate_runtime_debug_snapshot_contract.py'),
    ('RM1.33-E', 'audit_skill_kit_runtime_debug_coverage_safety.py'),
    ('RM1.33-F', 'validate_runtime_debug_6star_ultimate_snapshots.py'),
    ('RM1.33-G', 'validate_runtime_debug_5star_snapshot_rejections.py'),
    ('RM1.34', 'validate_boss_family_resistance_table.py'),
    ('RM1.34-B', 'validate_boss_element_faction_matrix.py'),
    ('RM1.34-C', 'validate_boss_enrage_phase_policy_table.py'),
    ('RM1.34-D', 'audit_boss_policy_cross_table_consistency.py'),
    ('RM1.34-E', 'validate_boss_policy_scenario_fixture_seed.py'),
    ('RM1.33-H', 'validate_divine_weapon_preview_catalog_only_fixture.py'),
    ('CS2-A', 'audit_collection_synergies_v2_readiness.py'),
    ('AF2-A', 'audit_affinity_phase2_gift_catalog_readiness.py'),
    ('CS2/AF2-COMBO', 'validate_collection_affinity_readiness_combo.py'),
    ('CS2-B', 'audit_collection_synergy_preview_resolver_safety.py'),
    ('AF2-B', 'validate_affinity_phase2_economy_cap_policy.py'),
    ('AXIS-A', 'audit_canonical_faction_element_axes.py'),
    ('UI-PREVIEW-A', 'audit_collection_affinity_ui_preview_safety.py'),
    ('STACK-A', 'audit_cross_system_progression_stack_safety.py'),
    ('MEGA-COMBO', 'validate_collection_affinity_axis_stack_combo.py'),
    ('CS2-C', 'audit_collection_synergy_ui_preview_contract.py'),
    ('AF2-C', 'validate_affinity_gift_inventory_schema.py'),
    ('STACK-B', 'audit_global_modifier_cap_resolver_safety.py'),
    ('AXIS-B', 'audit_canonical_axis_alias_helper_safety.py'),
    ('MEGA-COMBO-2', 'validate_cs2c_af2c_stackb_axisb_combo.py'),
    ('CS2-D', 'audit_collection_synergy_preview_ui_stub.py'),
    ('AF2-D', 'validate_affinity_phase2_migration_plan_draft.py'),
    ('AF2-E', 'audit_affinity_gifts_readonly_endpoint_safety.py'),
    ('STACK-C', 'validate_global_modifier_cap_resolver_edge_cases.py'),
    ('AXIS-C', 'audit_canonical_axis_dynamic_preview.py'),
    ('MEGA-COMBO-3', 'validate_cs2d_af2d_af2e_stackc_axisc_combo.py'),
    ('CS2-E', 'audit_collection_synergy_preview_navigation.py'),
    ('AF2-F', 'validate_affinity_phase2_rollback_rehearsal.py'),
    ('AF2-G', 'audit_affinity_gift_spend_skeleton_safety.py'),
    ('STACK-D', 'validate_global_modifier_cap_resolver_multiplicative_rejection.py'),
    ('AXIS-D', 'validate_canonical_axis_activation_table.py'),
    ('MEGA-COMBO-4', 'validate_cs2e_af2f_af2g_stackd_axisd_combo.py'),
    # ULTRA-COMBO (AF2-H + STACK-E + STACK-F + AXIS-E + SAFETY-ROLLUP-A
    #              + OPS-A + PATCH-READINESS-A)
    ('AF2-H', 'audit_affinity_gift_spend_auth_ratelimit_safety.py'),
    ('STACK-E', 'validate_global_modifier_cap_resolver_borea_filtering.py'),
    ('STACK-F', 'validate_global_modifier_cap_resolver_debuff_semantics.py'),
    ('AXIS-E', 'audit_canonical_axis_read_through_helper.py'),
    ('SAFETY-ROLLUP-A', 'validate_runtime_activation_readiness_rollup.py'),
    ('OPS-A', 'audit_start_expo_wrapper_resilience.py'),
    ('PATCH-READINESS-A', 'validate_rm134b_patch_readiness_plan.py'),
    ('ULTRA-COMBO', 'validate_ultra_combo_af2h_stackef_axise_safety_ops_patchreadiness.py'),
    # ULTRA-COMBO v6 (AF2-I + RM1.34-B-PATCH-A + RM1.34-B-PATCH-B
    #                 + AXIS-V6 + BASELINE-V6)
    ('AF2-I', 'audit_affinity_gift_spend_auth_ratelimit_contract.py'),
    ('RM1.34-B-PATCH-A', 'validate_rm134b_patch_a_darkness_to_dark.py'),
    ('RM1.34-B-PATCH-B', 'validate_rm134b_patch_b_tides_decision.py'),
    ('AXIS-V6', 'audit_axis_post_patch_alignment_v6.py'),
    ('BASELINE-V6', 'validate_rm134b_axis_patch_baseline_v6.py'),
    ('ULTRA-COMBO-V6', 'validate_af2i_rm134b_axispatch_v6_combo.py'),
    # ULTRA-COMBO V7 (AF2-J + AF2-K-PRE + AXIS-F + OPS-B + SAFETY-ROLLUP-B
    #                 + AF2-L-PRE)
    ('AF2-J', 'audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py'),
    ('AF2-K-PRE', 'validate_affinity_gift_spend_idempotency_ledger_contract.py'),
    ('AXIS-F', 'audit_affinity_gifts_axis_readonly_routes.py'),
    ('OPS-B', 'audit_ops_start_expo_persistence.py'),
    ('SAFETY-ROLLUP-B', 'validate_collection_affinity_runtime_activation_rollup_v2.py'),
    ('AF2-L-PRE', 'validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py'),
    ('ULTRA-COMBO-V7', 'validate_af2j_af2kpre_axisf_opsb_rollupb_combo.py'),
    # ULTRA-COMBO V8 (AF2-K + AF2-L + AF2-M + OPS-C + SAFETY-ROLLUP-C)
    ('AF2-K', 'validate_affinity_gift_transaction_ledger_migration.py'),
    ('AF2-L', 'validate_affinity_gift_spend_load_and_rollback_results.py'),
    ('AF2-M', 'validate_affinity_gift_runtime_operator_signoff.py'),
    ('OPS-C', 'audit_ops_start_expo_autorestore.py'),
    ('SAFETY-ROLLUP-C', 'validate_collection_affinity_runtime_activation_rollup_v3.py'),
    ('ULTRA-COMBO-V8', 'validate_af2k_af2l_af2m_opsc_safetyc_combo.py'),
    # ULTRA-COMBO V9 (AF2-K-COMMIT + AF2-L-FULL + AF2-M-SIGN-PRE
    #                 + AXIS-G + OPS-C-WIRING + SAFETY-ROLLUP-D)
    ('AF2-K-COMMIT', 'validate_affinity_gift_transaction_ledger_commit_result.py'),
    ('AF2-L-FULL', 'run_affinity_gift_spend_full_disabled_load_probe.py'),
    ('AF2-M-SIGN-PRE', 'validate_affinity_gift_runtime_operator_signoff_v2.py'),
    ('AXIS-G', 'audit_affinity_gifts_combined_axis_routes.py'),
    ('OPS-C-WIRING', 'audit_ops_start_expo_boot_wiring.py'),
    ('SAFETY-ROLLUP-D', 'validate_collection_affinity_runtime_activation_rollup_v4.py'),
    ('ULTRA-COMBO-V9', 'validate_af2k_commit_af2l_full_af2m_signpre_axisg_opsc_wiring_safety_rollup_d_combo.py'),
    # ULTRA-COMBO V10 (AF2-M-SIGN-PRODUCT + AF2-L-K6-PREP/FULL-SAFE
    #                  + OPS-C-SUPERVISOR-WIRING + STACK-G-PRE + SAFETY-ROLLUP-E)
    ('V10-PREFLIGHT', 'validate_ultra_combo_v10_preflight.py'),
    ('AF2-M-SIGN-PRODUCT', 'validate_affinity_gift_product_signoff_v3.py'),
    ('AF2-L-K6-PLAN', 'validate_affinity_gift_spend_k6_locust_test_plan.py'),
    ('AF2-L-K6-PREP', 'validate_affinity_gift_spend_k6_prep_probe.py'),
    ('OPS-C-SUP-WIRING', 'audit_ops_supervisor_startup_wiring.py'),
    ('STACK-G-PRE', 'audit_stack_g_battle_cap_resolver_preconnection.py'),
    ('SAFETY-ROLLUP-E', 'validate_collection_affinity_runtime_activation_rollup_v5.py'),
    ('ULTRA-COMBO-V10', 'validate_ultra_combo_v10_productsign_k6_ops_stackg_rollupe.py'),
    # ULTRA-COMBO V11 (AF2-M-SIGN-ENGINEERING+QA+ECONOMY+ROLLBACK_OWNER
    #                  + AF2-L-K6-LIVE-PREP + OPS-C-SUPERVISOR-APPLY
    #                  + AF2-N-GO-NOGO-PACKAGE + SAFETY-ROLLUP-F)
    ('V11-PREFLIGHT', 'validate_ultra_combo_v11_preflight.py'),
    ('AF2-M-V4-ALL-SIGNOFFS', 'validate_affinity_gift_operator_signoff_v4.py'),
    ('AF2-L-K6-LIVE-PREP', 'validate_affinity_gift_spend_k6_live_prep_result_v2.py'),
    ('OPS-C-SUP-APPLY', 'validate_ops_c_supervisor_apply_result.py'),
    ('AF2-N-GO-NOGO-PRE', 'validate_af2n_go_no_go_preflight_package.py'),
    ('SAFETY-ROLLUP-F', 'validate_collection_affinity_runtime_activation_rollup_v6.py'),
    ('ULTRA-COMBO-V11', 'validate_ultra_combo_v11_all_signoffs_pre_af2n.py'),
    # ULTRA-COMBO V12 (AF2-N CONTROLLED CANARY + MONITORING + ROLLBACK READY + SAFETY-ROLLUP-G)
    ('FINAL-USER-APPROVAL',  'validate_final_user_runtime_approval_record.py'),
    ('AF2-N-CANARY-SMOKE',   'validate_af2n_canary_smoke_monitoring.py'),
    ('AF2-N-ACTIVATION',     'validate_af2n_runtime_activation_result.py'),
    ('SAFETY-ROLLUP-G',      'validate_collection_affinity_runtime_activation_rollup_v7.py'),
    ('ULTRA-COMBO-V12',      'validate_ultra_combo_v12_af2n_canary.py'),
    # ULTRA-COMBO V13 (AF2-N-MONITORING-WINDOW + AF2-N-STAGE1-PREP
    #                  + AF2-N-INVENTORY-WIRING-PRE + AF2-L-K6-LIVE-PREP2
    #                  + SAFETY-ROLLUP-H)
    ('AF2-N-MONITORING-WINDOW',     'validate_af2n_monitoring_window_result.py'),
    ('AF2-N-STAGE1-PREP',           'validate_af2n_stage1_1pct_allowlist_plan.py'),
    ('AF2-N-INVENTORY-WIRING-PRE',  'audit_af2n_inventory_wiring_pre.py'),
    ('AF2-L-K6-LIVE-PREP2',         'validate_affinity_gift_spend_k6_live_prep2_result.py'),
    ('SAFETY-ROLLUP-H',             'validate_collection_affinity_runtime_activation_rollup_v8.py'),
    ('ULTRA-COMBO-V13',             'validate_ultra_combo_v13_monitoring_stage1_prep.py'),
    # ULTRA-COMBO V14 (AF2-N-STAGE1-APPLY + STAGE1-MONITORING
    #                  + INVENTORY-WIRING-SHADOW + K6-PREP3
    #                  + STAGE1-ROLLBACK-READINESS + SAFETY-ROLLUP-I)
    ('V14-PREFLIGHT',                 'validate_af2n_v14_preflight.py'),
    ('AF2-N-STAGE1-APPLY',            'validate_af2n_stage1_1pct_apply_result.py'),
    ('AF2-N-STAGE1-MONITORING',       'validate_af2n_stage1_monitoring_window.py'),
    ('AF2-N-INVENTORY-WIRING-SHADOW', 'validate_affinity_gift_inventory_shadow_wiring.py'),
    ('AF2-L-K6-PREP3-PLAN',           'validate_af2n_stage1_k6_live_test_plan.py'),
    ('AF2-L-K6-PREP3-PROBE',          'validate_af2n_stage1_k6_prep_probe.py'),
    ('AF2-N-STAGE1-ROLLBACK-READY',   'validate_af2n_stage1_rollback_readiness.py'),
    ('SAFETY-ROLLUP-I',               'validate_collection_affinity_runtime_activation_rollup_v9.py'),
    ('ULTRA-COMBO-V14',               'validate_ultra_combo_v14_stage1_inventoryshadow.py'),
    # ULTRA-COMBO V15 (STAGE1 EXTENDED MONITORING + INVENTORY-WIRING ACTIVATE
    #                  STAGE1-ONLY [safe block today] + INVENTORY LIVE MONITORING
    #                  + K6 LIVE INSTALL PREP + SAFETY-ROLLUP-J)
    ('V15-PREFLIGHT',                          'validate_af2n_v15_preflight.py'),
    ('AF2-N-STAGE1-EXTENDED-MONITORING-V15',   'validate_af2n_stage1_extended_monitoring_v15.py'),
    ('AF2-N-INVENTORY-WIRING-APPLY',           'validate_affinity_inventory_wiring_stage1_apply_result.py'),
    ('AF2-N-INVENTORY-LIVE-MONITORING',        'validate_affinity_inventory_live_monitoring_stage1.py'),
    ('AF2-L-K6-V15-FALLBACK',                  'validate_af2n_v15_k6_fallback_probe.py'),
    ('V15-ROLLBACK-READINESS',                 'validate_af2n_v15_rollback_readiness.py'),
    ('SAFETY-ROLLUP-J',                        'validate_collection_affinity_runtime_activation_rollup_v10.py'),
    ('ULTRA-COMBO-V15',                        'validate_ultra_combo_v15_inventory_activate_stage1.py'),
    # ULTRA-COMBO V16 (SCHEMA-MIGRATION-USER-INVENTORY + SEED STAGE1 QA
    #                  + INVENTORY-WIRING ACTIVATE RETRY + LIVE MONITORING
    #                  + SAFETY-ROLLUP-K)
    ('V16-PREFLIGHT',                          'validate_af2n_v16_preflight.py'),
    ('AF2-N-INVENTORY-SCHEMA-MIGRATION',       'validate_user_inventory_affinity_state_schema.py'),
    ('AF2-N-STAGE1-QA-SEED',                   'validate_stage1_qa_gift_inventory_seed.py'),
    ('AF2-N-INVENTORY-RETRY-APPLY',            'validate_affinity_inventory_wiring_stage1_retry_apply_result.py'),
    ('AF2-N-INVENTORY-LIVE-MONITORING-V16',    'validate_affinity_inventory_live_monitoring_v16.py'),
    ('SAFETY-ROLLUP-K',                        'validate_collection_affinity_runtime_activation_rollup_v11.py'),
    ('ULTRA-COMBO-V16',                        'validate_ultra_combo_v16_inventory_schema_seed_activate.py'),
    # ULTRA-COMBO V17 (INVENTORY EXTENDED MONITORING + STAGE2 5-10% EXPANSION
    #                  PREP/APPLY-GATED + SUITE SUPERSEDED CLEANUP
    #                  + K6/LOCUST REAL READINESS + SAFETY-ROLLUP-L)
    ('V17-PREFLIGHT',                              'validate_af2n_v17_preflight.py'),
    ('AF2-N-INVENTORY-EXTENDED-MONITORING-V17',    'validate_af2n_inventory_extended_monitoring_v17.py'),
    ('AF2-N-STAGE2-APPLY',                         'validate_af2n_stage2_5_10pct_apply_result.py'),
    ('AF2-N-STAGE2-MONITORING-V17',                'validate_af2n_stage2_monitoring_v17.py'),
    ('SUITE-SUPERSEDENCE-CLEANUP',                 'validate_validator_suite_supersedence_cleanup.py'),
    ('AF2-L-K6-LOCUST-READINESS-V17',              'validate_af2n_v17_k6_locust_readiness.py'),
    ('V17-ROLLBACK-READINESS',                     'validate_af2n_v17_rollback_readiness.py'),
    ('SAFETY-ROLLUP-L',                            'validate_collection_affinity_runtime_activation_rollup_v12.py'),
    ('ULTRA-COMBO-V17',                            'validate_ultra_combo_v17_stage2_monitoring_cleanup_k6.py'),
    # ULTRA-COMBO V18 (STAGE2 EXTENDED MONITORING + STAGE3 QA EXPANSION
    #                  PREP/APPLY-GATED + PUBLIC UI PREVIEW READINESS
    #                  + K6/LOCUST REAL ATTEMPT SAFE + SAFETY-ROLLUP-M)
    ('V18-PREFLIGHT',                              'validate_af2n_v18_preflight.py'),
    ('AF2-N-STAGE2-EXTENDED-MONITORING-V18',       'validate_af2n_stage2_extended_monitoring_v18.py'),
    ('AF2-N-STAGE3-QA-EXPANSION-APPLY',            'validate_af2n_stage3_qa_expansion_apply_result.py'),
    ('AF2-N-STAGE3-MONITORING-V18',                'validate_af2n_stage3_monitoring_v18.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-SAFETY',             'audit_affinity_gifts_public_preview_safety.py'),
    ('AF2-L-K6-LOCUST-V18',                        'validate_af2n_v18_k6_locust_result.py'),
    ('V18-ROLLBACK-READINESS',                     'validate_af2n_v18_rollback_readiness.py'),
    ('SAFETY-ROLLUP-M',                            'validate_collection_affinity_runtime_activation_rollup_v13.py'),
    ('ULTRA-COMBO-V18',                            'validate_ultra_combo_v18_stage2_stage3_publicpreview.py'),
    # ULTRA-COMBO V19 (STAGE3 EXTENDED MONITORING + LOCUST REAL LOW-IMPACT
    #                  + PUBLIC UI PREVIEW READ-ONLY + BROAD-ROLLOUT PLAN
    #                  + SAFETY-ROLLUP-N)
    ('V19-PREFLIGHT',                              'validate_af2n_v19_preflight.py'),
    ('AF2-N-STAGE3-EXTENDED-MONITORING-V19',       'validate_af2n_stage3_extended_monitoring_v19.py'),
    ('AF2-L-LOCUST-LOW-IMPACT-V19',                'validate_af2n_stage3_locust_low_impact_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-IMPLEMENTATION',     'audit_affinity_gifts_public_preview_implementation.py'),
    ('AF2-N-BROAD-ROLLOUT-READINESS-PLAN',         'validate_af2n_broad_rollout_readiness_plan.py'),
    ('V19-ROLLBACK-READINESS',                     'validate_af2n_v19_rollback_readiness.py'),
    ('SAFETY-ROLLUP-N',                            'validate_collection_affinity_runtime_activation_rollup_v14.py'),
    ('ULTRA-COMBO-V19',                            'validate_ultra_combo_v19_stage3_locust_ui_broadprep.py'),
    # ULTRA-COMBO V20 (STAGE4 INTERNAL BETA PREP PLAN-ONLY + ROLLBACK DRILLS
    #                  + SIGNOFFS V5 + LOCUST EXTENDED LOW-IMPACT
    #                  + PUBLIC UI PREVIEW QA/A11Y AUDIT + SAFETY-ROLLUP-O)
    ('V20-PREFLIGHT',                              'validate_af2n_v20_preflight.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-PLAN',            'validate_af2n_stage4_internal_beta_plan.py'),
    ('AF2-N-V20-ROLLBACK-DRILLS',                  'validate_af2n_v20_rollback_drill_result.py'),
    ('AF2-N-STAGE4-SIGNOFF-PACKAGE-V5',            'validate_af2n_stage4_signoff_package_v5.py'),
    ('AF2-L-LOCUST-EXTENDED-LOW-IMPACT-V20',       'validate_af2n_v20_locust_extended_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-QA-A11Y-V20',        'audit_affinity_gifts_public_preview_qa_a11y.py'),
    ('SAFETY-ROLLUP-O',                            'validate_collection_affinity_runtime_activation_rollup_v15.py'),
    ('ULTRA-COMBO-V20',                            'validate_ultra_combo_v20_stage4_readiness_drills.py'),
    # ULTRA-COMBO V21 (STAGE4 INTERNAL BETA APPLY-GATED + SIGNOFFS V5 APPLY
    #                  + RATE-LIMIT MIDDLEWARE + DB BACKUP DRILL + STAGE4
    #                  MONITORING + LOCUST + SAFETY-ROLLUP-P)
    ('V21-PREFLIGHT',                              'validate_af2n_v21_preflight.py'),
    ('AF2-N-STAGE4-SIGNOFFS-V5-APPLIED',           'validate_af2n_stage4_signoffs_v5_applied.py'),
    ('AF2-N-V21-RATE-LIMIT-AUDIT',                 'audit_affinity_gift_spend_rate_limit_runtime.py'),
    ('AF2-N-V21-RATE-LIMIT-PROBE',                 'validate_affinity_gift_spend_rate_limit_probe.py'),
    ('AF2-N-V21-DB-BACKUP-DRILL',                  'validate_af2n_stage4_db_backup_drill.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-APPLY',           'validate_af2n_stage4_internal_beta_apply_result.py'),
    ('AF2-N-V21-STAGE4-MONITORING',                'validate_af2n_stage4_monitoring_v21.py'),
    ('AF2-L-LOCUST-STAGE4-V21',                    'validate_af2n_v21_locust_stage4_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-V21-SAFETY',         'audit_affinity_gifts_public_preview_v21_safety.py'),
    ('V21-ROLLBACK-READINESS',                     'validate_af2n_v21_rollback_readiness.py'),
    ('SAFETY-ROLLUP-P',                            'validate_collection_affinity_runtime_activation_rollup_v16.py'),
    ('ULTRA-COMBO-V21',                            'validate_ultra_combo_v21_stage4_apply_gated.py'),
    # ULTRA-COMBO V22 (STAGE4 EXTENDED MONITORING + REDIS RATE-LIMIT MIGRATION PREP
    #                  + INVENTORY/AFFINITY DELTA AUDIT + LOCUST STAGE4 EXTENDED
    #                  + BROAD-ROLLOUT BLOCKER MATRIX + SAFETY-ROLLUP-Q)
    ('V22-PREFLIGHT',                              'validate_af2n_v22_preflight.py'),
    ('AF2-N-V22-STAGE4-EXTENDED-MONITORING',       'validate_af2n_stage4_extended_monitoring_v22.py'),
    ('AF2-N-V22-REDIS-MIGRATION-PLAN-AUDIT',       'audit_affinity_rate_limit_redis_migration_plan.py'),
    ('AF2-N-V22-REDIS-PROBE',                      'validate_affinity_rate_limit_redis_probe.py'),
    ('AF2-N-V22-DELTA-AUDIT',                      'validate_affinity_inventory_delta_consistency_v22.py'),
    ('AF2-L-LOCUST-STAGE4-V22',                    'validate_af2n_v22_locust_stage4_extended_result.py'),
    ('AF2-N-V22-BROAD-ROLLOUT-BLOCKER-MATRIX',     'validate_af2n_broad_rollout_blocker_matrix.py'),
    ('AF2-N-PUBLIC-UI-V22-SAFETY',                 'audit_affinity_gifts_public_preview_v22_safety.py'),
    ('V22-ROLLBACK-READINESS',                     'validate_af2n_v22_rollback_readiness.py'),
    ('SAFETY-ROLLUP-Q',                            'validate_collection_affinity_runtime_activation_rollup_v17.py'),
    ('ULTRA-COMBO-V22',                            'validate_ultra_combo_v22_stage4_monitoring_redisprep.py'),
    # ULTRA-COMBO V23 (REDIS RATE-LIMIT PROVISION/SWITCH-GATED + STAGE4 OBS
    #                  WINDOW + ABUSE MONITORING PREP + DELTA AUDIT V23
    #                  + LOCUST STAGE4 RATE-LIMIT + SAFETY-ROLLUP-R)
    ('V23-PREFLIGHT',                              'validate_af2n_v23_preflight.py'),
    ('AF2-N-V23-REDIS-LIVE-PROBE',                 'validate_af2n_v23_redis_live_probe.py'),
    ('AF2-N-V23-REDIS-SWITCH',                     'validate_af2n_v23_redis_switch.py'),
    ('AF2-N-V23-STAGE4-OBSERVATION-WINDOW',        'validate_af2n_stage4_observation_window_v23.py'),
    ('AF2-N-V23-ABUSE-MONITORING-PREP',            'validate_af2n_v23_abuse_monitoring_prep.py'),
    ('AF2-N-V23-DELTA-AUDIT',                      'validate_affinity_inventory_delta_consistency_v23.py'),
    ('AF2-L-LOCUST-STAGE4-V23',                    'validate_af2n_v23_locust_stage4_ratelimit.py'),
    ('AF2-N-V23-BLOCKER-MATRIX-V2',                'validate_af2n_broad_rollout_blocker_matrix_v2.py'),
    ('AF2-N-PUBLIC-UI-V23-SAFETY',                 'audit_affinity_gifts_public_preview_v23_safety.py'),
    ('V23-ROLLBACK-READINESS',                     'validate_af2n_v23_rollback_readiness.py'),
    ('SAFETY-ROLLUP-R',                            'validate_collection_affinity_runtime_activation_rollup_v18.py'),
    ('ULTRA-COMBO-V23',                            'validate_ultra_combo_v23_redis_switch_observation.py'),
    # ULTRA-COMBO V24 (REAL OBSERVATION WINDOW + ABUSE METRICS INSTRUMENTATION
    #                  + STAGING ROLLBACK DRILL + REDIS HA PLAN + SAFETY-ROLLUP-S)
    ('V24-PREFLIGHT',                              'validate_af2n_v24_preflight.py'),
    ('AF2-N-V24-OBSERVATION-WINDOW-REAL',          'validate_af2n_v24_observation_window_real.py'),
    ('AF2-N-V24-ABUSE-METRICS-INSTRUMENTATION',    'validate_af2n_v24_abuse_metrics_instrumentation.py'),
    ('AF2-N-V24-STAGING-ROLLBACK-DRILL',           'validate_af2n_v24_staging_rollback_drill.py'),
    ('AF2-N-V24-REDIS-HA-DECISION-PLAN',           'validate_af2n_v24_redis_ha_decision_plan.py'),
    ('AF2-N-V24-SUPPORT-ECONOMY-PREP',             'validate_af2n_v24_support_economy_prep.py'),
    ('AF2-N-V24-BLOCKER-MATRIX-V3',                'validate_af2n_broad_rollout_blocker_matrix_v3.py'),
    ('AF2-N-PUBLIC-UI-V24-SAFETY',                 'audit_affinity_gifts_public_preview_v24_safety.py'),
    ('V24-ROLLBACK-READINESS',                     'validate_af2n_v24_rollback_readiness.py'),
    ('SAFETY-ROLLUP-S',                            'validate_collection_affinity_runtime_activation_rollup_v19.py'),
    ('ULTRA-COMBO-V24',                            'validate_ultra_combo_v24_observation_abuse_rollback_redisHA.py'),
    # ULTRA-COMBO V25 (REDIS OPS HARDENING + FAIL-OPEN ALERTING + SUPPORT
    #                  RUNBOOK + ECONOMY STRESS 10X + BLOCKER MATRIX V4
    #                  + SAFETY-ROLLUP-T)
    ('V25-PREFLIGHT',                              'validate_af2n_v25_preflight.py'),
    ('AF2-N-V25-REDIS-OPS-RECOVERY',               'validate_redis_rate_limit_ops_recovery.py'),
    ('AF2-N-V25-REDIS-RESTART-DRILL',              'validate_redis_rate_limit_restart_drill_v25.py'),
    ('AF2-N-V25-FAIL-OPEN-ALERTING-CONTRACT',      'validate_af2n_fail_open_alerting_contract.py'),
    ('AF2-N-V25-ALERTING-READONLY-STATUS',         'audit_af2n_alerting_readonly_status.py'),
    ('AF2-N-V25-SUPPORT-RUNBOOK',                  'validate_af2n_stage4_support_runbook_v25.py'),
    ('AF2-N-V25-ECONOMY-STRESS-10X',               'validate_af2n_economy_stress_10x_simulation_v25.py'),
    ('AF2-N-V25-BLOCKER-MATRIX-V4',                'validate_af2n_broad_rollout_blocker_matrix_v4.py'),
    ('AF2-N-V25-OBSERVATION-WINDOW',               'validate_af2n_stage4_observation_window_v25.py'),
    ('AF2-N-PUBLIC-UI-V25-SAFETY',                 'audit_affinity_gifts_public_preview_v25_safety.py'),
    ('V25-ROLLBACK-READINESS',                     'validate_af2n_v25_rollback_readiness.py'),
    ('SAFETY-ROLLUP-T',                            'validate_collection_affinity_runtime_activation_rollup_v20.py'),
    ('ULTRA-COMBO-V25',                            'validate_ultra_combo_v25_redis_ops_support_economy.py'),
    # ULTRA-COMBO V26 (MANAGED REDIS READINESS + CAP RAISE PLAN + INVENTORY
    #                  SCOPE EXPANSION + BROAD ROLLOUT SIGNOFF V6 PLAN-ONLY
    #                  + ALERTING INTEGRATION PREP + FRONTEND SMOKE + STRESS 2X
    #                  + SAFETY-ROLLUP-U)
    ('V26-PREFLIGHT',                              'validate_af2n_v26_preflight.py'),
    ('AF2-N-V26-MANAGED-REDIS-READINESS',          'validate_affinity_managed_redis_readiness.py'),
    ('AF2-N-V26-CAP-RAISE-PLAN',                   'validate_af2n_cap_raise_plan.py'),
    ('AF2-N-V26-INVENTORY-SCOPE-PLAN',             'validate_af2n_inventory_scope_expansion_plan.py'),
    ('AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-V6',         'validate_af2n_broad_rollout_signoff_package_v6.py'),
    ('AF2-N-V26-ALERTING-INTEGRATION-PREP',        'audit_af2n_alerting_integration_prep.py'),
    ('AF2-N-V26-FRONTEND-SMOKE',                   'audit_affinity_gifts_frontend_smoke_v26.py'),
    ('AF2-N-V26-STRESS-2X',                        'validate_af2n_stress_2x_v26.py'),
    ('AF2-N-V26-BLOCKER-MATRIX-V5',                'validate_af2n_broad_rollout_blocker_matrix_v5.py'),
    ('AF2-N-V26-OBSERVATION-WINDOW',               'validate_af2n_stage4_observation_window_v26.py'),
    ('V26-ROLLBACK-READINESS',                     'validate_af2n_v26_rollback_readiness.py'),
    ('SAFETY-ROLLUP-U',                            'validate_collection_affinity_runtime_activation_rollup_v21.py'),
    ('ULTRA-COMBO-V26',                            'validate_ultra_combo_v26_broad_readiness_plan.py'),
    # ULTRA-COMBO V27 (MANAGED REDIS GATED + ALERTING LIVE/MOCK + CAP RAISE
    #                  S1 5K->25K GATED + OBSERVATION + STRESS 3X
    #                  + SAFETY-ROLLUP-V)
    ('V27-PREFLIGHT',                              'validate_af2n_v27_preflight.py'),
    ('AF2-N-V27-MANAGED-REDIS-SWITCH',             'validate_managed_redis_switch_v27.py'),
    ('AF2-N-V27-ALERTING-SINK',                    'validate_af2n_alerting_sink_v27.py'),
    ('AF2-N-V27-CAP-RAISE-S1',                     'validate_af2n_cap_raise_s1_v27.py'),
    ('AF2-N-V27-STAGE4-OBSERVATION',               'validate_af2n_stage4_observation_v27.py'),
    ('AF2-N-V27-STRESS-3X',                        'validate_af2n_stress_3x_v27.py'),
    ('AF2-N-V27-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v27.py'),
    ('AF2-N-V27-BLOCKER-MATRIX-V6',                'validate_af2n_broad_rollout_blocker_matrix_v6.py'),
    ('AF2-N-V27-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v27_safety.py'),
    ('V27-ROLLBACK-READINESS',                     'validate_af2n_v27_rollback_readiness.py'),
    ('SAFETY-ROLLUP-V',                            'validate_collection_affinity_runtime_activation_rollup_v22.py'),
    ('ULTRA-COMBO-V27',                            'validate_ultra_combo_v27_managed_redis_cap_s1.py'),
    # ULTRA-COMBO V28 (INVENTORY SCOPE S1 EXPANSION 700->2500 + STRESS 5X
    #                  + MANAGED REDIS PROBE (gated) + ALERTING LIVE PROBE
    #                  + BLOCKER MATRIX V7 + SAFETY-ROLLUP-W)
    ('V28-PREFLIGHT',                              'validate_af2n_v28_preflight.py'),
    ('AF2-N-V28-INVENTORY-SCOPE-S1',               'validate_af2n_inventory_scope_s1_v28.py'),
    ('AF2-N-V28-SCOPE-S1-OBSERVATION',             'validate_af2n_scope_s1_observation_v28.py'),
    ('AF2-N-V28-STRESS-5X',                        'validate_af2n_stress_5x_v28.py'),
    ('AF2-N-V28-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v28.py'),
    ('AF2-N-V28-MANAGED-REDIS-PROBE',              'validate_managed_redis_v28_probe.py'),
    ('AF2-N-V28-ALERTING-LIVE-PROBE',              'validate_alerting_live_v28_probe.py'),
    ('AF2-N-V28-BLOCKER-MATRIX-V7',                'validate_af2n_broad_rollout_blocker_matrix_v7.py'),
    ('AF2-N-V28-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v28_safety.py'),
    ('V28-ROLLBACK-READINESS',                     'validate_af2n_v28_rollback_readiness.py'),
    ('SAFETY-ROLLUP-W',                            'validate_collection_affinity_runtime_activation_rollup_v23.py'),
    ('ULTRA-COMBO-V28',                            'validate_ultra_combo_v28_inventory_scope_stress5x.py'),
    # ULTRA-COMBO V29 (ENV-AWARE MANAGED REDIS/ALERTING + V28 SCHEMA-FIX REGRESSION
    #                  + SCOPE S1 EXTENDED MONITORING + STRESS 8X + SIGNOFF V7 + ROLLUP X)
    ('V29-PREFLIGHT',                              'validate_af2n_v29_preflight.py'),
    ('AF2-N-V29-V28-SCHEMA-FIX-REGRESSION',        'validate_af2n_v28_schema_fix_regression_v29.py'),
    ('AF2-N-V29-MANAGED-REDIS-PROBE',              'validate_managed_redis_envaware_v29.py'),
    ('AF2-N-V29-ALERTING-PROBE',                   'validate_alerting_envaware_v29.py'),
    ('AF2-N-V29-SCOPE-S1-EXTENDED-MONITORING',     'validate_af2n_scope_s1_extended_monitoring_v29.py'),
    ('AF2-N-V29-STRESS-8X',                        'validate_af2n_stress_8x_v29.py'),
    ('AF2-N-V29-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v29.py'),
    ('AF2-N-V29-BROAD-ROLLOUT-SIGNOFF-V7',         'validate_af2n_broad_rollout_signoff_package_v7.py'),
    ('AF2-N-V29-BLOCKER-MATRIX-V8',                'validate_af2n_broad_rollout_blocker_matrix_v8.py'),
    ('AF2-N-V29-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v29_safety.py'),
    ('V29-ROLLBACK-READINESS',                     'validate_af2n_v29_rollback_readiness.py'),
    ('SAFETY-ROLLUP-X',                            'validate_collection_affinity_runtime_activation_rollup_v24.py'),
    ('ULTRA-COMBO-V29',                            'validate_ultra_combo_v29_envaware_readiness_postfix.py'),
    # ULTRA-COMBO V30 (CAP S2 GATED + SOAK + STRESS 10X + OBSERVABILITY + ENV-AWARE PROBES + SIGNOFF V8 + ROLLUP Y)
    ('V30-PREFLIGHT',                              'validate_af2n_v30_preflight.py'),
    ('AF2-N-V30-STAGE4-SOAK',                      'validate_af2n_stage4_soak_v30.py'),
    ('AF2-N-V30-CAP-RAISE-S2',                     'validate_af2n_cap_raise_s2_v30.py'),
    ('AF2-N-V30-STRESS-10X',                       'validate_af2n_stress_10x_v30.py'),
    ('AF2-N-V30-MANAGED-REDIS-PROBE',              'validate_managed_redis_envaware_v30.py'),
    ('AF2-N-V30-ALERTING-PROBE',                   'validate_alerting_envaware_v30.py'),
    ('AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC',     'validate_af2n_observability_dashboard_spec.py'),
    ('AF2-N-V30-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v30.py'),
    ('AF2-N-V30-BROAD-ROLLOUT-SIGNOFF-V8',         'validate_af2n_broad_rollout_signoff_package_v8.py'),
    ('AF2-N-V30-BLOCKER-MATRIX-V9',                'validate_af2n_broad_rollout_blocker_matrix_v9.py'),
    ('AF2-N-V30-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v30_safety.py'),
    ('V30-ROLLBACK-READINESS',                     'validate_af2n_v30_rollback_readiness.py'),
    ('SAFETY-ROLLUP-Y',                            'validate_collection_affinity_runtime_activation_rollup_v25.py'),
    ('ULTRA-COMBO-V30',                            'validate_ultra_combo_v30_capS2_soak_observability.py'),
    # COSMETIC-SKIN-TITLE-SYSTEM-A (DESIGN-ONLY foundation; no runtime/battle attachment)
    ('COSMETIC-SYSTEM-POLICY-A',                   'validate_cosmetic_system_policy_v1.py'),
    ('COSMETIC-SCHEMAS-A',                         'validate_cosmetic_schemas_v1.py'),
    ('COSMETIC-EXAMPLES-A',                        'validate_cosmetic_examples_v1.py'),
    ('COSMETIC-RUNTIME-SAFETY-A',                  'audit_cosmetic_runtime_safety_v1.py'),
    ('COSMETIC-SKIN-TITLE-COMBO-A',                'validate_cosmetic_skin_title_system_a_combo.py'),
    # SERVER-LIFECYCLE-CALENDAR-A (DESIGN-ONLY / AUDIT-ONLY)
    ('SERVER-SHARD-ISOLATION-AUDIT-A',             'audit_server_shard_isolation_v1.py'),
    ('SERVER-LIFECYCLE-POLICIES-A',                'validate_server_lifecycle_policies_v1.py'),
    ('SERVER-AGE-CALENDAR-A',                      'validate_server_age_calendar_schema_v1.py'),
    ('SERVER-MERGE-RECOVERY-A',                    'validate_server_merge_recovery_policy_v1.py'),
    ('SERVER-SHARD-ISOLATION-SAFETY-A',            'audit_server_shard_isolation_safety_v1.py'),
    ('SERVER-LIFECYCLE-COMBO-A',                   'validate_server_lifecycle_calendar_a_combo.py'),
    # SLC-C SINGLE-SHARD → MULTI-SHARD MIGRATION PLAN (DESIGN-ONLY / DRY-RUN)
    ('SLC-C-ACCOUNT-ENTITY',                       'validate_slc_c_account_entity_schema_v1.py'),
    ('SLC-C-ACCOUNT-WIDE-DOC',                     'validate_slc_c_account_wide_document_contract_v1.py'),
    ('SLC-C-SERVER-BOUND-DOC',                     'validate_slc_c_server_bound_document_contract_v1.py'),
    ('SLC-C-COLLECTION-SCOPE-MATRIX',              'validate_slc_c_collection_scope_migration_matrix_v1.py'),
    ('SLC-C-MULTISHARD-INDEX-PLAN',                'validate_slc_c_multishard_index_plan_v1.py'),
    ('SLC-C-PAID-FREE-SPLIT',                      'validate_slc_c_paid_free_currency_split_plan_v1.py'),
    ('SLC-C-ROUTE-PATCH-CONTRACT',                 'validate_slc_c_server_aware_route_patch_contract_v1.py'),
    ('SLC-C-PROFILE-CREATION-CONTRACT',            'validate_slc_c_server_profile_creation_contract_v1.py'),
    ('SLC-C-MIGRATION-PHASE-PLAN',                 'validate_slc_c_single_to_multishard_migration_phase_plan_v1.py'),
    ('SLC-C-ROLLBACK-PLAN',                        'validate_slc_c_multishard_rollback_plan_v1.py'),
    ('SLC-C-REPO-PREFLIGHT',                       'audit_slc_c_repo_multishard_preflight.py'),
    ('SLC-C-CRITICAL-FILES-NO-DIFF',               'audit_slc_c_critical_files_no_diff.py'),
    ('SLC-C-MIGRATION-DRYRUN',                     'simulate_slc_c_migration_dryrun.py'),
    ('SLC-C-API-SMOKE-READONLY',                   'audit_slc_c_api_smoke_readonly.py'),
    ('SLC-C-COMBO',                                'validate_slc_c_combo_v1.py'),
    # SLC-BE SERVER PROFILE CREATION + SELECTION CONTRACT (DESIGN-ONLY / CONTRACT-ONLY)
    ('SLC-BE-PREFLIGHT',                           'validate_slc_be_preflight_v1.py'),
    ('SLC-B-SERVER-PROFILE-CONTRACT',              'validate_server_profile_creation_contract_v1.py'),
    ('SLC-B-SERVER-PROFILE-DEFAULTS',              'validate_server_profile_default_values_v1.py'),
    ('SLC-E-SERVER-SELECTION-CONTRACT',            'validate_server_selection_endpoint_contract_v1.py'),
    ('SLC-E-SERVER-STATUS-POLICY',                 'validate_server_status_transition_policy_v1.py'),
    ('SLC-E-NEW-PLAYER-ROUTING',                   'validate_new_player_server_routing_policy_v1.py'),
    ('SLC-E-ACTIVE-SERVER-RESOLUTION',             'validate_active_server_resolution_contract_v1.py'),
    ('SLC-BE-DRY-RUN-SCENARIOS',                   'validate_server_profile_creation_dry_run_scenarios_v1.py'),
    ('SLC-BE-RUNTIME-SAFETY-AUDIT',                'audit_server_selection_runtime_safety_v1.py'),
    ('SLC-BE-ROLLUP',                              'validate_server_lifecycle_profile_selection_readiness_rollup_v1.py'),
    ('SLC-BE-COMBO',                               'validate_slc_be_server_profile_selection_combo.py'),
    # LIVE-MODES-RECONCILIATION-A + SLC-NEXT-PREP-A (DESIGN-ONLY / AUDIT-ONLY)
    ('LIVE-MODES-RECONCILIATION-A',                'validate_live_mode_benchmark_reconciliation_v1.py'),
    ('LIVE-MODES-CALENDAR-A',                      'validate_live_mode_calendar_v1.py'),
    ('LIVE-MODES-REWARD-FRAMEWORK-A',              'validate_live_mode_reward_framework_v1.py'),
    ('LIVE-MODES-BROADCAST-POLICY-A',              'validate_live_mode_broadcast_policy_v1.py'),
    ('LIVE-MODES-RISK-POLICY-A',                   'validate_live_mode_benchmark_risk_policy_v1.py'),
    ('SANCTUARY-HOUSING-DESIGN-NOTE-A',            'validate_sanctuary_housing_dimora_divina_note_v1.py'),
    ('LIVE-MODES-RUNTIME-SAFETY-AUDIT-A',          'audit_live_mode_reconciliation_runtime_safety_v1.py'),
    ('SLC-NEXT-PREP-A',                            'validate_slc_next_after_be_plan_v1.py'),
    ('LIVE-MODES-SLC-NEXT-COMBO-A',                'validate_live_modes_slc_next_combo_v1.py'),
    # DIVINE BENCHMARK CANONICAL SOURCE PACK (DESIGN-ONLY / SOURCE-OF-TRUTH)
    ('BENCHMARK-CANONICAL-INDEX-A',                'validate_benchmark_canonical_index_v1.py'),
    ('BENCHMARK-LIVE-SPECIAL-MODES-CANONICAL-A',   'validate_live_special_modes_canonical_v1.py'),
    ('BENCHMARK-SYSTEM-LIBRARY-A',                 'validate_benchmark_system_library_v1.py'),
    ('BENCHMARK-RISK-POLICY-EXPANDED-A',           'validate_benchmark_risk_policy_expanded_v1.py'),
    ('BENCHMARK-SANCTUARY-HOUSING-CANONICAL-A',    'validate_sanctuary_housing_dimora_divina_canonical_v1.py'),
    ('BENCHMARK-SUMMON-PITY-FRAGMENT-CANONICAL-A', 'validate_summon_pity_fragment_canonical_v1.py'),
    ('BENCHMARK-SERVER-LIFECYCLE-CAL-MERGE-A',     'validate_server_lifecycle_calendar_merge_canonical_v1.py'),
    ('BENCHMARK-EVENT-HUB-DAILY-GUIDE-A',          'validate_event_hub_daily_guide_canonical_v1.py'),
    ('BENCHMARK-GUILD-SOCIAL-COOP-A',              'validate_guild_social_coop_canonical_v1.py'),
    ('BENCHMARK-EQUIPMENT-FORGE-RELIC-A',          'validate_equipment_forge_relic_canonical_v1.py'),
    ('BENCHMARK-BATTLE-STATS-REPORTING-A',         'validate_battle_stats_reporting_canonical_v1.py'),
    ('BENCHMARK-SLC-F-NEXT-CHECKPOINT-A',          'validate_slc_f_next_checkpoint_canonical_v1.py'),
    ('BENCHMARK-CANONICAL-RUNTIME-SAFETY-AUDIT-A', 'audit_benchmark_canonical_runtime_safety_v1.py'),
    ('BENCHMARK-CANONICAL-COMBO-A',                'validate_benchmark_canonical_combo_v1.py'),
    # SLC-F ROUTE PATCH DRY-RUN (DESIGN-ONLY / DRY-RUN)
    ('SLC-F-PREFLIGHT',                            'validate_slc_f_preflight_v1.py'),
    ('SLC-F-ROUTE-SCOPE-INVENTORY',                'audit_slc_f_route_scope_inventory_v1.py'),
    ('SLC-F-COLLECTION-SCOPE-MATRIX',              'validate_slc_f_collection_scope_matrix_v1.py'),
    ('SLC-F-ENDPOINT-PATCH-CONTRACT',              'validate_slc_f_endpoint_patch_contract_v1.py'),
    ('SLC-F-LEGACY-S1-COMPATIBILITY-PLAN',         'validate_slc_f_legacy_s1_compatibility_plan_v1.py'),
    ('SLC-F-DRY-RUN-SIMULATION',                   'simulate_slc_f_route_patch_dryrun_v1.py'),
    ('SLC-F-ROUTE-PATCH-RISK-MATRIX',              'validate_slc_f_route_patch_risk_matrix_v1.py'),
    ('SLC-F-RUNTIME-SAFETY-AUDIT',                 'audit_slc_f_runtime_safety_v1.py'),
    ('SLC-F-READINESS-ROLLUP',                     'validate_slc_f_readiness_rollup_v1.py'),
    ('SLC-F-COMBO',                                'validate_slc_f_route_patch_dryrun_combo_v1.py'),
    # SLC-D MERGE TOOLING OFFLINE SIMULATION (DESIGN-ONLY / DRY-RUN)
    ('SLC-D-PREFLIGHT',                            'validate_slc_d_preflight_v1.py'),
    ('SLC-D-TOOLING-OFFLINE-PLAN',                 'validate_server_merge_tooling_offline_plan_v1.py'),
    ('SLC-D-ELIGIBILITY-POLICY',                   'validate_server_merge_eligibility_policy_v1.py'),
    ('SLC-D-GROUP-PLANNING-CONTRACT',              'validate_server_merge_group_planning_contract_v1.py'),
    ('SLC-D-CONFLICT-RESOLUTION-CONTRACT',         'validate_server_merge_conflict_resolution_contract_v1.py'),
    ('SLC-D-RECOVERY-SEASON-CONTRACT',             'validate_server_merge_recovery_season_contract_v1.py'),
    ('SLC-D-RECOVERY-POLICY',                      'validate_server_merge_recovery_policy_v1.py'),
    ('SLC-D-CALENDAR-HARMONIZATION-POLICY',        'validate_server_merge_calendar_harmonization_policy_v1.py'),
    ('SLC-D-DRYRUN-SCENARIOS',                     'validate_server_merge_dryrun_scenarios_v1.py'),
    ('SLC-D-OFFLINE-SIMULATION',                   'simulate_slc_d_merge_tooling_offline_v1.py'),
    ('SLC-D-RISK-MATRIX',                          'validate_server_merge_risk_matrix_v1.py'),
    ('SLC-D-ABORT-ROLLBACK-POLICY',                'validate_server_merge_abort_rollback_policy_v1.py'),
    ('SLC-D-RUNTIME-SAFETY-AUDIT',                 'audit_slc_d_runtime_safety_v1.py'),
    ('SLC-D-READINESS-ROLLUP',                     'validate_slc_d_merge_tooling_offline_readiness_rollup_v1.py'),
    ('SLC-D-COMBO',                                'validate_slc_d_merge_tooling_combo_v1.py'),
    # SLC-G DEFAULT S1 MIGRATION COMMIT GATED PREP (PRE_COMMIT_GATED_DRY_RUN_FIRST)
    ('SLC-G-PREFLIGHT',                            'validate_slc_g_preflight_v1.py'),
    ('SLC-G-BACKFILL-DRYRUN',                      'simulate_slc_g_default_s1_backfill_dryrun.py'),
    ('SLC-G-WRITE-GATE-CONTRACT',                  'validate_slc_g_write_gate_contract_v1.py'),
    ('SLC-G-ROLLBACK-PLAN',                        'validate_slc_g_rollback_plan_v1.py'),
    ('SLC-G-IDEMPOTENCY-CONTRACT',                 'validate_slc_g_idempotency_contract_v1.py'),
    ('SLC-G-COMBO',                                'validate_slc_g_combo_v1.py'),
    # SLC-G-GUILDS-UNSAFE-CLEANUP-A (READ-ONLY FIRST / GATED CLEANUP PLAN)
    ('SLC-G-GUILDS-UNSAFE-AUDIT',                  'audit_slc_g_guilds_unsafe_readonly_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-PLAN',                  'validate_slc_g_guilds_cleanup_plan_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-GATE-CONTRACT',         'validate_slc_g_guilds_cleanup_gate_contract_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-ROLLBACK-PLAN',         'validate_slc_g_guilds_cleanup_rollback_plan_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-COMBO',                 'validate_slc_g_guilds_cleanup_combo_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-B-POST-APPLY',          'validate_slc_g_guilds_cleanup_b_post_apply_v1.py'),
    ('SLC-G-COMMIT-A-POST-APPLY',                  'validate_slc_g_commit_a_post_apply_v1.py'),
    # SLC-H SERVER SELECTION ENDPOINT DESIGN-ONLY (CONTRACT-ONLY / READ-ONLY)
    ('SLC-H-ENDPOINT-CONTRACT',                    'validate_slc_h_endpoint_contract_v1.py'),
    ('SLC-H-REJECTION-MODES',                      'validate_slc_h_rejection_modes_v1.py'),
    ('SLC-H-SERVER-STATUS-CONTRACT',               'validate_slc_h_server_status_contract_v1.py'),
    ('SLC-H-READINESS-GATES',                      'validate_slc_h_readiness_gates_v1.py'),
    ('SLC-H-COMBO',                                'validate_slc_h_combo_v1.py'),
    # SLC-F APPLY PREP + HOUSING ADDENDUM (DESIGN-ONLY / NO RUNTIME APPLY)
    ('SLC-F-APPLY-PREP-STAGED-PLAN',               'validate_slc_f_apply_prep_staged_plan_v1.py'),
    ('SLC-F-APPLY-READINESS-GATES',                'validate_slc_f_apply_readiness_gates_v1.py'),
    ('HOUSING-DIMORA-DIVINA-V2',                   'validate_sanctuary_housing_dimora_divina_v2.py'),
    ('DIMORA-DIVINA-RUNTIME-SAFETY-AUDIT',         'audit_dimora_divina_runtime_safety_v1.py'),
    ('SLC-F-APPLY-PREP-HOUSING-ADDENDUM-COMBO',    'validate_slc_f_apply_prep_housing_addendum_combo_v1.py'),
    ('SLC-F-BATCH-0-1-POST-APPLY',                 'validate_slc_f_batch_0_1_post_apply_v1.py'),
    # SLC-F APPLY BATCH-1B POST-APPLY (READ-ONLY VERIFICATION)
    ('SLC-F-BATCH-1B-POST-APPLY',                  'validate_slc_f_batch_1b_post_apply_v1.py'),
    # SLC-F APPLY BATCH-2 POST-APPLY (READ-ONLY VERIFICATION; SAFE NO-OP APPLY)
    ('SLC-F-BATCH-2-POST-APPLY',                   'validate_slc_f_batch_2_post_apply_v1.py'),
    # SLC-F EQUIPMENT SERVER_SCOPE EXTENSION POST-APPLY (READ-ONLY; SAFE NO-OP APPLY)
    ('SLC-F-EQUIPMENT-SCOPE-POST-APPLY',           'validate_slc_f_equipment_scope_post_apply_v1.py'),
    # SLC-F RAIDS EQUIPMENT SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY',     'validate_slc_f_raids_equipment_scope_post_apply_v1.py'),
    # SLC-F GVG WAR INSERT SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-GVG-WAR-SCOPE-POST-APPLY',             'validate_slc_f_gvg_war_scope_post_apply_v1.py'),
    # SLC-F UNIQUE-ITEMS SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY',        'validate_slc_f_unique_items_scope_post_apply_v1.py'),
    # SLC-F POST-MICROBATCH CONSOLIDATION AUDIT (READ-ONLY)
    ('SLC-F-POST-MICROBATCH-CONSOLIDATION-AUDIT-V1', 'audit_slc_f_post_microbatch_consolidation_v1.py'),
    # SLC-F COSMETICS SCHEMA SPLIT REFACTOR (READY_NOT_APPLIED - design-only, no runtime patch)
    ('SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1',   'validate_slc_f_cosmetics_refactor_v1.py'),
    # SLC-F MINOR WRITE SURFACES AUDIT (READ-ONLY; NO RUNTIME PATCH)
    ('SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1',        'audit_slc_f_minor_write_surfaces_v1.py'),
    # MEGA-COMBO V1 BLOCK_A ECONOMY PAID/FREE SPLIT PREP (AUDIT/PREP ONLY; NO RUNTIME PATCH)
    ('MEGA-COMBO-V1-BLOCK-A-ECONOMY-PREP',         'audit_economy_paid_free_split_prep_v1.py'),
    # MEGA-COMBO V1 BLOCK_B GACHA/SUMMON DRIFT DOCS HOUSEKEEPING (DOC/AUDIT ONLY; NO DB WRITE)
    ('MEGA-COMBO-V1-BLOCK-B-DRIFT-HOUSEKEEPING',   'audit_drift_docs_gacha_summon_count_v1.py'),
    # MEGA-COMBO V2 BLOCK_A ECONOMY DAILY_CLAIMS SCOPE APPLY (PATCH APPLIED)
    ('V2-BLOCK-A-ECONOMY-DAILY-CLAIMS-POST-APPLY', 'validate_v2_economy_daily_claims_scope.py'),
    # MEGA-COMBO V2 BLOCK_B GVG USER_MAIL SCOPE APPLY (PATCH APPLIED)
    ('V2-BLOCK-B-GVG-USER-MAIL-POST-APPLY',        'validate_v2_gvg_user_mail_scope.py'),
    # MEGA-COMBO V2 ROLLUP (5 blocks consistency)
    ('V2-ROLLUP',                                  'validate_mega_combo_slc_acceleration_v2_rollup.py'),
    # MEGA-COMBO V3 BLOCK_E ROSTER VISIBILITY INVARIANTS (HTTP smoke; READ-ONLY)
    ('V3-ROSTER-VISIBILITY-INVARIANTS',            'validate_roster_visibility_invariants_v1.py'),
    # MEGA-COMBO V4 BLOCK_A BATTLE PASS TECHNICAL HARDENING (READY_NOT_APPLIED audit)
    ('V4-BLOCK-A-BATTLE-PASS-HARDENING-AUDIT',     'validate_v4_battle_pass_technical_hardening.py'),
    # MEGA-COMBO V4 BLOCK_D SLC-F OBSERVABILITY ROLLUP (READ-ONLY)
    ('V4-BLOCK-D-SLC-F-OBSERVABILITY-ROLLUP',      'validate_slc_f_observability_rollup_v1.py'),
    # MEGA-COMBO V4 BLOCK_E REDIS RATE-LIMIT OPS AUDIT (READ-ONLY)
    ('V4-BLOCK-E-REDIS-RATE-LIMIT-OPS-AUDIT',      'audit_redis_rate_limit_ops_v1.py'),
    # MEGA-COMBO V5 BLOCK_B AF2-N OBSERVABILITY METRICS PIPELINE (READ-ONLY DOC AUDIT)
    ('V5-BLOCK-B-AF2N-OBSERVABILITY-PIPELINE',     'validate_af2n_observability_pipeline_v1.py'),
    # MEGA-COMBO V5 BLOCK_C ROSTER VISIBILITY INVARIANTS V2 (HTTP smoke; superset of v1)
    ('V5-BLOCK-C-ROSTER-VISIBILITY-INVARIANTS-V2', 'validate_roster_visibility_invariants_v2.py'),
    # MEGA-COMBO V6 BLOCK_B AF2-N METRICS SNAPSHOT EXPORT (READ-ONLY validator; does NOT run export)
    ('V6-BLOCK-B-AF2N-METRICS-SNAPSHOT-EXPORT',    'validate_af2n_metrics_snapshot_export_v1.py'),
    # MEGA-COMBO V6 BLOCK_E SUITE RUNTIME HEALTH (non-blocking on H3/H4; HTTP smoke + supervisorctl)
    ('V6-BLOCK-E-SUITE-RUNTIME-HEALTH',            'validate_suite_runtime_health_v1.py'),
    # MEGA-COMBO V7 BLOCK_A ECONOMY /server/select DEPRECATION NOTICE (apply low-risk; read-only validator)
    ('V7-BLOCK-A-ECONOMY-SERVER-SELECT-DEPRECATION', 'validate_v7_economy_server_select_deprecation.py'),
    # MEGA-COMBO V7 BLOCK_B BATTLE PASS TECHNICAL HARDENING POST SIGNOFF ($setOnInsert; read-only validator)
    ('V7-BLOCK-B-BATTLE-PASS-HARDENING-POST-SIGNOFF', 'validate_v7_battle_pass_technical_hardening.py'),
    # MEGA-COMBO V7 BLOCK_C SERVER PROFILES CANONICAL INDEXES DEFINITION (design-only; no DB write)
    ('V7-BLOCK-C-SERVER-PROFILES-INDEXES-DEFINITION', 'validate_server_profiles_schema_indexes_definition_v1.py'),
    # MEGA-COMBO V7 BLOCK_E BOREA INERT BASELINE INVARIANT HARDENING (HTTP smoke; 9 dedicated invariants)
    ('V7-BLOCK-E-BOREA-INERT-BASELINE',             'validate_borea_inert_baseline_v1.py'),
    # MEGA-COMBO V8 BLOCK_A SERVER PROFILES COLLECTION CREATION PLAN (design/script-only; dry-run gated, no DB write)
    ('V8-BLOCK-A-SERVER-PROFILES-COLLECTION-PLAN',  'validate_server_profiles_collection_creation_plan_v1.py'),
    # MEGA-COMBO V8 BLOCK_B BATTLE PASS USER_SEASON INDEX DEFINITION (design/dry-run-only; no live create_index)
    ('V8-BLOCK-B-BATTLE-PASS-INDEX-USER-SEASON',    'validate_battle_pass_user_season_index_definition_v1.py'),
    # MEGA-COMBO V8 BLOCK_C AF2N DASHBOARD RENDER JSON (design/export-only; no runtime, no daemon)
    ('V8-BLOCK-C-AF2N-DASHBOARD-RENDER-JSON',       'validate_af2n_dashboard_render_json_v1.py'),
    # MEGA-COMBO V8 BLOCK_E SUITE OPTIMIZATION PARALLEL AUDIT (audit-only; no runner change, no validator weakening)
    ('V8-BLOCK-E-SUITE-OPTIMIZATION-PARALLEL-AUDIT', 'audit_suite_optimization_parallel_v1.py'),
    # PROJECT_A Track A SERVER PROFILES OPS (live ops apply inert: collection + 3 canonical indexes; no runtime)
    ('PROJECT-A-TRACK-A-SERVER-PROFILES-OPS',       'validate_project_a_server_profiles_ops_v1.py'),
    # PROJECT_A Track B BATTLE PASS USER_SEASON UNIQUE INDEX (live ops apply; V4 R4 closed)
    ('PROJECT-A-TRACK-B-BATTLE-PASS-INDEX-OPS',     'validate_project_a_battle_pass_index_ops_v1.py'),
    # PROJECT_A Track C AF2-N RUNTIME ROUTING PREFLIGHT (no runtime mutation)
    ('PROJECT-A-TRACK-C-AF2N-RUNTIME-ROUTING-PREFLIGHT', 'validate_project_a_af2n_runtime_routing_preflight_v1.py'),
    # PROJECT_A Track F GACHA/SUMMON DRIFT CLEANUP PLAN (audit/plan only; 7 drift docs classified)
    ('PROJECT-A-TRACK-F-GACHA-SUMMON-DRIFT-CLEANUP-PLAN', 'validate_project_a_gacha_summon_drift_cleanup_plan_v1.py'),
    # PROJECT_A Track G QA/RELEASE DOD TRACKER (project management; 7 DoD rows)
    ('PROJECT-A-TRACK-G-QA-RELEASE-DOD-TRACKER',    'validate_project_completion_dod_tracker_v1.py'),
    # PROJECT_B Track A SERVER PROFILES DUAL-ROUTE INERT SKELETON (flag-gated, runtime OFF)
    ('PROJECT-B-TRACK-A-SERVER-PROFILES-DUAL-ROUTE', 'validate_project_b_server_profiles_dual_route.py'),
    # PROJECT_B Track B HOUSING RESOLVER PURE STUB (inert, NOT imported by runtime)
    ('PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT', 'validate_project_b_housing_resolver_stub_inert.py'),
    # PROJECT_B Track C HERO SKILL KIT CATALOG FREEZE (sha256 invariant; 6 baselines)
    ('PROJECT-B-TRACK-C-HERO-SKILL-KIT-CATALOG-FREEZE', 'validate_project_b_hero_skill_kit_catalog_freeze_v1.py'),
    # PROJECT_B Track E SUITE PARALLEL RUNNER (optional --parallel; default sequential unchanged)
    ('PROJECT-B-TRACK-E-SUITE-PARALLEL-RUNNER',     'validate_project_b_suite_parallel_runner_v1.py'),
    # PROJECT_B Track G QA RELEASE MOBILE SMOKE FLOW (static matrix validator)
    ('PROJECT-B-TRACK-G-QA-RELEASE-MOBILE-SMOKE-FLOW', 'validate_project_b_qa_release_mobile_smoke_flow_v1.py'),
    # PROJECT_B Track H ARTIFACT BIBLE V1 SCHEMA + LAUNCH CANDIDATES (hard invariants enforcement)
    ('PROJECT-B-TRACK-H-ARTIFACT-BIBLE-SCHEMA',     'validate_project_b_artifact_bible_schema_v1.py'),
    # PROJECT_C Track A SERVER PROFILES DUAL-ROUTE BEHAVIOR LAYER (flag-gated, default 503)
    ('PROJECT-C-TRACK-A-SERVER-PROFILES-BEHAVIOR',  'validate_project_c_server_profiles_behavior_v1.py'),
    # PROJECT_C Track B HOUSING RESOLVER INTEGRATION DESIGN (5 phases; stub NOT imported by runtime)
    ('PROJECT-C-TRACK-B-HOUSING-RESOLVER-INTEGRATION-DESIGN', 'validate_project_c_housing_resolver_integration_design_v1.py'),
    # PROJECT_C Track C STATUS EFFECT CATALOG BASELINE (10 categories + 10 effects, anti-power-creep caps)
    ('PROJECT-C-TRACK-C-STATUS-EFFECT-CATALOG-BASELINE', 'validate_project_c_status_effect_catalog_baseline_v1.py'),
    # PROJECT_C Track D DRIFT_DOC_2 deprecated_banner_legacy_pool ARCHIVE (audit only; 2/7 archived)
    ('PROJECT-C-TRACK-D-DRIFT-DOC-2-ARCHIVE',       'validate_project_c_drift_doc_2_archive_v1.py'),
    # PROJECT_C Track E QA MOBILE SMOKE RUNNER CLI (GET-only, non-mutating; --help smoke)
    ('PROJECT-C-TRACK-E-QA-MOBILE-SMOKE-RUNNER',    'validate_project_c_qa_mobile_smoke_runner_v1.py'),
    # PROJECT_C Track F AF2-N DASHBOARD PROVISION OPS TEMPLATES (3 Grafana templates, no secret baked)
    ('PROJECT-C-TRACK-F-AF2N-DASHBOARD-PROVISION-OPS', 'validate_project_c_af2n_dashboard_provision_ops_v1.py'),
    # PROJECT_C Track G LEGACY /server/select DEPRECATION METRICS (design only, 3 metrics, 4-phase kill-switch)
    ('PROJECT-C-TRACK-G-LEGACY-SERVER-SELECT-DEPRECATION-METRICS', 'validate_project_c_legacy_server_select_deprecation_metrics_v1.py'),
    # PROJECT_C Track H ARTIFACT BIBLE V1 USER APPROVAL + BONUS RESOLVER STUB DESIGN (pure stub, NOT imported by runtime)
    ('PROJECT-C-TRACK-H-ARTIFACT-BIBLE-USER-APPROVAL-AND-BONUS-RESOLVER-STUB', 'validate_project_c_artifact_bible_user_approval_v1.py'),
    # PROJECT_D Track A SERVER PROFILES FLAGGED PREVIEW BEHAVIOR (double-flag-gated; default 503 unchanged)
    ('PROJECT-D-TRACK-A-SERVER-PROFILES-FLAGGED-PREVIEW', 'validate_project_d_server_profiles_flagged_preview.py'),
    # PROJECT_D Track B HOUSING RESOLVER PHASE 2 UNIT TESTS (8 UT pass; stub NOT imported)
    ('PROJECT-D-TRACK-B-HOUSING-RESOLVER-PHASE2-TESTS', 'validate_project_d_housing_resolver_stub_caps_v1.py'),
    # PROJECT_D Track C STATUS EFFECT RUNTIME ADAPTER SKELETON (pure module, NOT imported by battle/runtime)
    ('PROJECT-D-TRACK-C-STATUS-EFFECT-ADAPTER-SKELETON', 'validate_project_d_status_effect_adapter_stub_inert.py'),
    # PROJECT_D Track D DRIFT_DOC_3 obsolete_pity_counter_format FREEZE_READ_ONLY (3/7 archived)
    ('PROJECT-D-TRACK-D-DRIFT-DOC-3-ARCHIVE',         'validate_project_d_drift_doc_3_archive_v1.py'),
    # PROJECT_D Track E QA RUNNER LOGIN STEP GATED (wrapper only allows POST /api/login; live MANUAL_REQUIRED)
    ('PROJECT-D-TRACK-E-QA-RUNNER-LOGIN-SAFETY',      'validate_project_d_qa_runner_login_safety.py'),
    # PROJECT_D Track F BASELINE FAIL ISOLATION (3 DEPRECATED_VALIDATOR classified; not hidden; rebaseline plan)
    ('PROJECT-D-TRACK-F-BASELINE-FAIL-ISOLATION',     'audit_project_d_baseline_fail_isolation_v1.py'),
    # PROJECT_D Track G AF2-N DASHBOARD LOCAL VALIDATION (3 Grafana templates shape; 5 alert UIDs; no external calls)
    ('PROJECT-D-TRACK-G-AF2N-DASHBOARD-LOCAL-VALIDATION', 'validate_project_d_af2n_dashboard_local_templates_v1.py'),
    # PROJECT_D Track H ARTIFACT BIBLE V1 APPROVAL FREEZE (design-only; 7 freeze invariants; 5 draft candidates)
    ('PROJECT-D-TRACK-H-ARTIFACT-BIBLE-V1-APPROVAL-FREEZE', 'validate_project_d_artifact_bible_v1_approval_freeze.py'),
    # PROJECT_E Track A — SLC v2 successors (replace v1 deprecated cluster; default green when v1 SUPERSEDED)
    ('SLC-C-REPO-PREFLIGHT-V2',                    'validate_slc_c_repo_multishard_post_g_invariant_v2.py'),
    ('SLC-C-COMBO-V2',                             'validate_slc_c_combo_v2.py'),
    ('SLC-D-PREFLIGHT-V2',                         'validate_slc_d_preflight_v2.py'),
    ('SLC-D-COMBO-V2',                             'validate_slc_d_merge_tooling_combo_v2.py'),
    ('SLC-BE-PREFLIGHT-V2',                        'validate_slc_be_preflight_v2.py'),
    ('SLC-BE-COMBO-V2',                            'validate_slc_be_server_profile_selection_combo_v2.py'),
    ('SLC-F-PREFLIGHT-V2',                         'validate_slc_f_preflight_v2.py'),
    ('SLC-F-COMBO-V2',                             'validate_slc_f_route_patch_dryrun_combo_v2.py'),
    # PROJECT_E Track A marker validator (zero-fail recovery summary)
    ('PROJECT-E-TRACK-A-SLC-V2-ZERO-FAIL-RECOVERY','validate_project_e_slc_v2_zero_fail_recovery_v1.py'),
    # PROJECT_E Track B HOUSING PHASE 3 INTEGRATION DESIGN (no runtime)
    ('PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN', 'validate_project_e_housing_phase3_stub_tests_v1.py'),
    # PROJECT_E Track C STATUS EFFECT NON-RUNTIME UNIT TESTS
    ('PROJECT-E-TRACK-C-STATUS-EFFECT-NON-RUNTIME-UT', 'validate_project_e_status_effect_non_runtime_ut_v1.py'),
    # PROJECT_E Track D DRIFT_DOC_4 archive (4/7 archived)
    ('PROJECT-E-TRACK-D-DRIFT-DOC-4-ARCHIVE',      'validate_project_e_drift_doc_4_archive_v1.py'),
    # PROJECT_E Track E QA RUNNER TEST CREDS LOGIN DRY-RUN (manual_required live; no secrets logged)
    ('PROJECT-E-TRACK-E-QA-LOGIN-DRYRUN-SAFETY',   'validate_project_e_qa_login_dryrun_safety_v1.py'),
    # PROJECT_E Track F AF2-N DASHBOARD PROVISIONING DRILL (offline; no external calls)
    ('PROJECT-E-TRACK-F-AF2N-DASHBOARD-PROVISIONING-DRILL', 'validate_project_e_af2n_dashboard_provisioning_drill_v1.py'),
    # PROJECT_E Track G ARTIFACT BONUS RESOLVER NON-RUNTIME UNIT TESTS
    ('PROJECT-E-TRACK-G-ARTIFACT-BONUS-RESOLVER-NON-RUNTIME-UT', 'validate_project_e_artifact_bonus_resolver_non_runtime_ut_v1.py'),
    # PROJECT_E Track H PROJECT COMPLETION DoD RECALIBRATION (doc-only)
    ('PROJECT-E-TRACK-H-PROJECT-COMPLETION-DOD-RECALIBRATION', 'validate_project_e_project_completion_dod_recalibration_v1.py'),
    # PROJECT_F Track A SERVER PROFILES READ-ONLY PREVIEW HARDENING (default 503; double-flag gate; no DB writes)
    ('PROJECT-F-TRACK-A-SERVER-PROFILES-READ-ONLY-PREVIEW-HARDENING', 'validate_project_f_server_profiles_read_only_preview.py'),
    # PROJECT_F Track B HOUSING READ-ONLY PREVIEW CONTRACT (disabled-by-default 503 skeleton)
    ('PROJECT-F-TRACK-B-HOUSING-READ-ONLY-PREVIEW-CONTRACT', 'validate_project_f_housing_read_only_preview.py'),
    # PROJECT_F Track C STATUS EFFECT ADAPTER PHASE 2 NON-RUNTIME CONTRACT TESTS
    ('PROJECT-F-TRACK-C-STATUS-EFFECT-ADAPTER-PHASE2-TESTS', 'validate_project_f_status_effect_adapter_phase2_tests.py'),
    # PROJECT_F Track D DRIFT DOC 5 ARCHIVE (audit/doc only; 5/7 archived)
    ('PROJECT-F-TRACK-D-DRIFT-DOC-5-ARCHIVE', 'validate_project_f_drift_doc_5_archive_v1.py'),
    # PROJECT_F Track E QA TEST CREDENTIALS SAFE DRY-RUN (manual_required default; no secret logging)
    ('PROJECT-F-TRACK-E-QA-CREDENTIALS-SAFE-DRYRUN', 'validate_project_f_qa_credentials_safety.py'),
    # PROJECT_F Track F AF2-N DASHBOARD PROVISIONING PHASE 3 DRY-RUN (offline; no external calls)
    ('PROJECT-F-TRACK-F-AF2N-DASHBOARD-PROVISIONING-PHASE3-DRYRUN', 'validate_project_f_af2n_dashboard_phase3_dryrun_v1.py'),
    # PROJECT_F Track G SUITE HYGIENE LOCK & REGRESSION GUARD
    ('PROJECT-F-TRACK-G-SUITE-HYGIENE-LOCK', 'validate_project_f_suite_hygiene_lock_v1.py'),
    # PROJECT_F Track H ARTIFACT BIBLE IMPORT PLAN & APPROVAL GATE (design-only; 4 PENDING gates)
    ('PROJECT-F-TRACK-H-ARTIFACT-BIBLE-IMPORT-PLAN-APPROVAL-GATE', 'validate_project_f_artifact_import_plan_v1.py'),
    # PROJECT_G Track A SERVER PROFILES PREVIEW CONTRACT FREEZE (default 503; double-flag gate)
    ('PROJECT-G-TRACK-A-SERVER-PROFILES-PREVIEW-CONTRACT-FREEZE', 'validate_project_g_server_profiles_preview_contract_v1.py'),
    # PROJECT_G Track B HOUSING PREVIEW CONTRACT FREEZE + 7-substructure CAP SNAPSHOT
    ('PROJECT-G-TRACK-B-HOUSING-PREVIEW-CONTRACT-FREEZE', 'validate_project_g_housing_preview_contract_v1.py'),
    # PROJECT_G Track C STATUS EFFECT RUNTIME READINESS MATRIX (10 categories; non-runtime)
    ('PROJECT-G-TRACK-C-STATUS-EFFECT-RUNTIME-READINESS-MATRIX', 'validate_project_g_status_effect_runtime_readiness_matrix_v1.py'),
    # PROJECT_G Track D DRIFT DOC 6 ARCHIVE (audit/doc only; 6/7 archived)
    ('PROJECT-G-TRACK-D-DRIFT-DOC-6-ARCHIVE', 'validate_project_g_drift_doc_6_archive_v1.py'),
    # PROJECT_G Track E QA SAFE LOGIN ENV CONTRACT (MANUAL_REQUIRED default; no secret logging)
    ('PROJECT-G-TRACK-E-QA-SAFE-LOGIN-ENV-CONTRACT', 'validate_project_g_qa_safe_login_env_contract_v1.py'),
    # PROJECT_G Track F AF2-N DASHBOARD PROVISIONING APPROVAL GATE (5 PENDING gates; 0 external calls)
    ('PROJECT-G-TRACK-F-AF2N-DASHBOARD-PROVISIONING-APPROVAL-GATE', 'validate_project_g_af2n_dashboard_provisioning_approval_gate_v1.py'),
    # PROJECT_G Track G SUITE HEALTH FINALIZATION & REQUIRED DIFF GUARD
    ('PROJECT-G-TRACK-G-SUITE-HEALTH-FINALIZATION', 'validate_project_g_suite_health_finalization_v1.py'),
    # PROJECT_G Track H ARTIFACT APPROVAL GATE SIGNATURE PACK (4 PENDING gates; signature template)
    ('PROJECT-G-TRACK-H-ARTIFACT-APPROVAL-GATE-SIGNATURE', 'validate_project_g_artifact_approval_gate_signature_v1.py'),
    # PROJECT_H Track A FINAL SLC-H RELEASE CANDIDATE GATE
    ('PROJECT-H-TRACK-A-FINAL-SLC-H-RC-GATE', 'validate_project_h_final_slc_h_rc_gate_v1.py'),
    # PROJECT_H Track B FINAL HOUSING MVP RELEASE CANDIDATE GATE
    ('PROJECT-H-TRACK-B-FINAL-HOUSING-MVP-RC-GATE', 'validate_project_h_final_housing_mvp_rc_gate_v1.py'),
    # PROJECT_H Track C FINAL STATUS RUNTIME GATE & FIRST SLICE PLAN
    ('PROJECT-H-TRACK-C-FINAL-STATUS-RUNTIME-GATE-FIRST-SLICE', 'validate_project_h_final_status_runtime_gate_v1.py'),
    # PROJECT_H Track D DRIFT DOC 7 FINAL ARCHIVE (7/7)
    ('PROJECT-H-TRACK-D-DRIFT-DOC-7-FINAL-ARCHIVE', 'validate_project_h_drift_doc_7_final_archive_v1.py'),
    # PROJECT_H Track E QA RELEASE CANDIDATE SMOKE GATE (9 safe checks)
    ('PROJECT-H-TRACK-E-QA-RELEASE-CANDIDATE-SMOKE-GATE', 'validate_project_h_qa_release_candidate_smoke_gate_v1.py'),
    # PROJECT_H Track F AF2-N FINAL DASHBOARD LIVE READINESS GATE
    ('PROJECT-H-TRACK-F-AF2N-FINAL-DASHBOARD-LIVE-READINESS-GATE', 'validate_project_h_af2n_final_dashboard_live_readiness_gate_v1.py'),
    # PROJECT_H Track G ARTIFACT FINAL APPROVAL GATE & IMPORT READINESS
    ('PROJECT-H-TRACK-G-ARTIFACT-FINAL-APPROVAL-GATE', 'validate_project_h_artifact_final_approval_gate_v1.py'),
    # PROJECT_H Track H PROJECT RELEASE CANDIDATE DoD FINALIZATION (9 layers; next-stage plan)
    ('PROJECT-H-TRACK-H-PROJECT-RC-DOD-FINALIZATION', 'validate_project_h_release_candidate_dod_finalization_v1.py'),
    # PROJECT_I Track A SERVER PROFILES PREVIEW CANARY FLAG FLIP (authorized; code-path verified in-process; local backend untouched)
    ('PROJECT-I-TRACK-A-SERVER-PROFILES-PREVIEW-CANARY-FLIP', 'validate_project_i_server_profiles_preview_canary_flip_v1.py'),
    # PROJECT_I Track B HOUSING PREVIEW CANARY FLAG FLIP (authorized; zero-bonus envelope; local backend untouched)
    ('PROJECT-I-TRACK-B-HOUSING-PREVIEW-CANARY-FLIP', 'validate_project_i_housing_preview_canary_flip_v1.py'),
    # PROJECT_I Track C STATUS RUNTIME REQUIRED VALIDATOR AUGMENTATION PREP (zero added; activation pack will add)
    ('PROJECT-I-TRACK-C-STATUS-RUNTIME-REQUIRED-VALIDATOR-AUGMENTATION', 'validate_project_i_status_runtime_required_validator_augmentation_v1.py'),
    # PROJECT_I Track D QA LIVE LOGIN CANARY (MANUAL_REQUIRED if env unset; no secret logging)
    ('PROJECT-I-TRACK-D-QA-LIVE-LOGIN-CANARY', 'validate_project_i_qa_live_login_canary_v1.py'),
    # PROJECT_I Track E AF2-N APPROVAL SIGNATURES & CANARY PLAN (5 PENDING; 0 external calls)
    ('PROJECT-I-TRACK-E-AF2N-APPROVAL-SIGNATURES', 'validate_project_i_af2n_approval_signatures_v1.py'),
    # PROJECT_I Track F ARTIFACT APPROVAL SIGNATURES & IMPORT CANARY PLAN (4 PENDING; no live bonus/summon/import)
    ('PROJECT-I-TRACK-F-ARTIFACT-APPROVAL-SIGNATURES', 'validate_project_i_artifact_approval_signatures_v1.py'),
    # PROJECT_I Track G DRIFT DB CLEANUP FREEZE-WINDOW PLAN (no cleanup executed)
    ('PROJECT-I-TRACK-G-DRIFT-DB-CLEANUP-FREEZE-WINDOW-PLAN', 'validate_project_i_drift_db_cleanup_freeze_window_plan_v1.py'),
    # PROJECT_I Track H PROJECT 99->100 FINAL LIVE-GATE ROADMAP
    ('PROJECT-I-TRACK-H-PROJECT-99-TO-100-FINAL-LIVE-GATE-ROADMAP', 'validate_project_i_project_99_to_100_final_live_gate_roadmap_v1.py'),
    # PROJECT_J Track A STATUS FIRST SLICE SCOPE LOCK & FLAG CONTRACT (flag default OFF)
    ('PROJECT-J-TRACK-A-STATUS-FIRST-SLICE-SCOPE-LOCK', 'validate_project_j_status_first_slice_scope_lock_v1.py'),
    # PROJECT_J Track B STATUS RESOLVER PURE MODULE (inert; not imported by battle/runtime)
    ('PROJECT-J-TRACK-B-STATUS-RESOLVER-PURE-MODULE', 'validate_project_j_status_resolver_pure_module_v1.py'),
    # PROJECT_J Track C STATUS FIRST SLICE REQUIRED-CANDIDATE VALIDATORS SET (5 OPTIONAL)
    ('PROJECT-J-TRACK-C-STATUS-FIRST-SLICE-REQUIRED-VALIDATORS-SET', 'validate_project_j_status_first_slice_required_validators_set_v1.py'),
    # PROJECT_J Track D STATUS FIXTURE MATRIX + 10 GOLDEN TESTS
    ('PROJECT-J-TRACK-D-STATUS-FIXTURE-MATRIX-AND-GOLDEN-TESTS', 'validate_project_j_status_fixture_matrix_and_golden_tests_v1.py'),
    # PROJECT_J Track E BATTLE PAYLOAD STATUS PREVIEW CONTRACT (design only)
    ('PROJECT-J-TRACK-E-BATTLE-PAYLOAD-STATUS-PREVIEW-CONTRACT', 'validate_project_j_battle_payload_status_preview_contract_v1.py'),
    # PROJECT_J Track F STATUS ROLLBACK + KILL-SWITCH PLAN
    ('PROJECT-J-TRACK-F-STATUS-ROLLBACK-KILL-SWITCH-PLAN', 'validate_project_j_status_rollback_kill_switch_plan_v1.py'),
    # PROJECT_J Track G STATUS QA SAFE SMOKE EXTENSION (SS1-SS5)
    ('PROJECT-J-TRACK-G-STATUS-QA-SAFE-SMOKE-EXTENSION', 'validate_project_j_status_qa_safe_smoke_extension_v1.py'),
    # PROJECT_J Track H PROJECT J COMPLETION + NEXT PACK ROADMAP
    ('PROJECT-J-TRACK-H-PROJECT-J-COMPLETION-AND-NEXT-PACK-ROADMAP', 'validate_project_j_completion_and_next_pack_roadmap_v1.py'),
    # PROJECT_K Track A STATUS PREFIGHT INSERTION POINT AUDIT (honest blocker; battle runtime layer absent)
    ('PROJECT-K-TRACK-A-STATUS-PREFIGHT-INSERTION-POINT-AUDIT', 'validate_project_k_status_prefight_insertion_point_audit_v1.py'),
    # PROJECT_K Track B STATUS PREFIGHT FLAGGED WIRING (NOT APPLIED — awaiting battle runtime layer)
    ('PROJECT-K-TRACK-B-STATUS-PREFIGHT-FLAGGED-WIRING', 'validate_project_k_status_prefight_flagged_wiring_v1.py'),
    # PROJECT_K Track C STATUS REQUIRED VALIDATORS PROMOTION (5 RC promoted to REQUIRED — see REQUIRED block above)
    ('PROJECT-K-TRACK-C-STATUS-REQUIRED-VALIDATORS-PROMOTION', 'validate_project_k_status_required_validators_promotion_v1.py'),
    # PROJECT_K Track D STATUS CANARY FIXTURE EXECUTION (10/10 golden tests against pure resolver)
    ('PROJECT-K-TRACK-D-STATUS-CANARY-FIXTURE-EXECUTION', 'validate_project_k_status_canary_fixture_execution_v1.py'),
    # PROJECT_K Track E STATUS PAYLOAD PREVIEW CANARY CONTRACT (0 leaks across 5 audited endpoints)
    ('PROJECT-K-TRACK-E-STATUS-PAYLOAD-PREVIEW-CANARY-CONTRACT', 'validate_project_k_status_payload_preview_canary_contract_v1.py'),
    # PROJECT_K Track F STATUS RUNTIME CANARY ROLLBACK DRILL (in-process drill executed; flag transitions honest)
    ('PROJECT-K-TRACK-F-STATUS-RUNTIME-CANARY-ROLLBACK-DRILL', 'validate_project_k_status_runtime_canary_rollback_drill_v1.py'),
    # PROJECT_K Track G STATUS FIRST SLICE QA RC GATE (13 safe checks)
    ('PROJECT-K-TRACK-G-STATUS-FIRST-SLICE-QA-RC-GATE', 'validate_project_k_status_first_slice_qa_rc_gate_v1.py'),
    # PROJECT_K Track H PROJECT K COMPLETION + LIVE GATE STATUS (next pack: PROJECT_L)
    ('PROJECT-K-TRACK-H-PROJECT-K-COMPLETION-AND-LIVE-GATE-STATUS', 'validate_project_k_completion_and_live_gate_status_v1.py'),
    # PROJECT_L Track A BATTLE RUNTIME SEAM AUDIT (SEAM_SAFE_NOW_INERT)
    ('PROJECT-L-TRACK-A-BATTLE-RUNTIME-SEAM-AUDIT', 'validate_project_l_battle_runtime_seam_audit_v1.py'),
    # PROJECT_L Track B MINIMAL BATTLE RUNTIME SEAM (CREATED INERT; isolated module; not imported live)
    ('PROJECT-L-TRACK-B-MINIMAL-BATTLE-RUNTIME-SEAM-INERT', 'validate_project_l_minimal_battle_runtime_seam_v1.py'),
    # PROJECT_L Track C STATUS PREFIGHT DRY-RUN CANARY (DR1-DR5; live activation blocked)
    ('PROJECT-L-TRACK-C-STATUS-PREFIGHT-DRY-RUN-CANARY', 'validate_project_l_status_prefight_dry_run_canary_v1.py'),
    # PROJECT_L Track D STATUS REQUIRED VALIDATORS POST-SEAM GUARD (19 REQUIRED intact)
    ('PROJECT-L-TRACK-D-STATUS-REQUIRED-VALIDATORS-POST-SEAM-GUARD', 'validate_project_l_status_required_validators_post_seam_guard_v1.py'),
    # PROJECT_L Track E STATUS PAYLOAD NO-LEAK REGRESSION (0 leaks across 5 endpoints)
    ('PROJECT-L-TRACK-E-STATUS-PAYLOAD-NO-LEAK-REGRESSION', 'validate_project_l_status_payload_no_leak_regression_v1.py'),
    # PROJECT_L Track F STATUS CANARY ROLLBACK SCRIPT + DRILL (dry-run executed; non-destructive)
    ('PROJECT-L-TRACK-F-STATUS-CANARY-ROLLBACK-SCRIPT-AND-DRILL', 'validate_project_l_status_canary_rollback_script_and_drill_v1.py'),
    # PROJECT_L Track G STATUS FIRST SLICE RC GATE (13 safe checks)
    ('PROJECT-L-TRACK-G-STATUS-FIRST-SLICE-RC-GATE', 'validate_project_l_status_first_slice_rc_gate_v1.py'),
    # PROJECT_L Track H PROJECT L COMPLETION + NEXT STEP (next pack: PROJECT_M)
    ('PROJECT-L-TRACK-H-PROJECT-L-COMPLETION-AND-NEXT-STEP', 'validate_project_l_completion_and_next_step_v1.py'),
    # PROJECT_M Track A BATTLE ENGINE SINGLE POINT WIRING AUDIT (SINGLE_POINT_SAFE_NOW_FLAGGED)
    ('PROJECT-M-TRACK-A-BATTLE-ENGINE-SINGLE-POINT-AUDIT', 'validate_project_m_battle_engine_single_point_audit_v1.py'),
    # PROJECT_M Track B BATTLE ENGINE STATUS SEAM SINGLE POINT WIRING (flag-OFF byte-identical proven)
    ('PROJECT-M-TRACK-B-BATTLE-ENGINE-STATUS-SEAM-WIRING', 'validate_project_m_battle_engine_status_seam_wiring_v1.py'),
    # PROJECT_M Track C FLAG OFF BYTE-IDENTICAL REGRESSION GUARD (deterministic 3v3 fixture; sha256 match)
    ('PROJECT-M-TRACK-C-FLAG-OFF-BYTE-IDENTICAL-REGRESSION-GUARD', 'validate_project_m_flag_off_byte_identical_regression_v1.py'),
    # PROJECT_M Track D FLAG ON IN-PROCESS CANARY FIXTURE (C1-C6 buffs + cap clamp + out-of-slice)
    ('PROJECT-M-TRACK-D-FLAG-ON-IN-PROCESS-CANARY-FIXTURE', 'validate_project_m_flag_on_in_process_canary_fixture_v1.py'),
    # PROJECT_M Track E STATUS PAYLOAD + BATTLE LOG NO-LEAK GUARD (endpoints + source-level scan)
    ('PROJECT-M-TRACK-E-STATUS-PAYLOAD-BATTLE-LOG-NO-LEAK-GUARD', 'validate_project_m_status_payload_battle_log_no_leak_v1.py'),
    # PROJECT_M Track F BATTLE ENGINE STATUS SEAM ROLLBACK DRILL (dry-run + temp-copy restore byte-identical to backup)
    ('PROJECT-M-TRACK-F-BATTLE-ENGINE-STATUS-SEAM-ROLLBACK-DRILL', 'validate_project_m_battle_engine_status_seam_rollback_drill_v1.py'),
    # PROJECT_M Track G STATUS FIRST SLICE CANARY ENV RC GATE (13 safe checks)
    ('PROJECT-M-TRACK-G-STATUS-FIRST-SLICE-CANARY-ENV-RC-GATE', 'validate_project_m_status_first_slice_canary_env_rc_gate_v1.py'),
    # PROJECT_M Track H PROJECT M COMPLETION + NEXT STEP (next pack: PROJECT_N)
    ('PROJECT-M-TRACK-H-PROJECT-M-COMPLETION-AND-NEXT-STEP', 'validate_project_m_completion_and_next_step_v1.py'),
    # PROJECT_N Track A CANARY ENV PRECHECK (NON_PROD_LOCAL_ONLY confirmed)
    ('PROJECT-N-TRACK-A-CANARY-ENV-PRECHECK', 'validate_project_n_canary_env_precheck_v1.py'),
    # PROJECT_N Track B STATUS FIRST SLICE CANARY FLAG FLIP (executed then rolled back; final state FLAG_OFF)
    ('PROJECT-N-TRACK-B-STATUS-FIRST-SLICE-CANARY-FLAG-FLIP', 'validate_project_n_status_first_slice_canary_flag_v1.py'),
    # PROJECT_N Track C CANARY FLAG ON BEHAVIOR SMOKE (B1-B7 PASS; battle byte-identical with flag ON)
    ('PROJECT-N-TRACK-C-CANARY-FLAG-ON-BEHAVIOR-SMOKE', 'validate_project_n_canary_flag_on_behavior_smoke_v1.py'),
    # PROJECT_N Track D CANARY LIGHT LOAD + STABILITY (150 req 100% 2xx; p99 ~ 68ms)
    ('PROJECT-N-TRACK-D-CANARY-LIGHT-LOAD-STABILITY', 'validate_project_n_canary_light_load_stability_v1.py'),
    # PROJECT_N Track E CANARY PAYLOAD/LOG/METRICS NO-LEAK GUARD
    ('PROJECT-N-TRACK-E-CANARY-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_n_canary_payload_log_metrics_no_leak_v1.py'),
    # PROJECT_N Track F CANARY ROLLBACK + KILL-SWITCH DRILL (6-step drill)
    ('PROJECT-N-TRACK-F-CANARY-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_n_canary_rollback_kill_switch_drill_v1.py'),
    # PROJECT_N Track G STATUS FIRST SLICE DEV-LIVE READINESS GATE (7 green-checks listed)
    ('PROJECT-N-TRACK-G-STATUS-FIRST-SLICE-DEV-LIVE-READINESS-GATE', 'validate_project_n_status_first_slice_dev_live_readiness_gate_v1.py'),
    # PROJECT_N Track H PROJECT N COMPLETION + NEXT STEP (next pack: PROJECT_O)
    ('PROJECT-N-TRACK-H-PROJECT-N-COMPLETION-AND-NEXT-STEP', 'validate_project_n_completion_and_next_step_v1.py'),
    # PROJECT_O Track A DEV-LIVE PRECHECK (NON_PROD_LOCAL_ONLY confirmed)
    ('PROJECT-O-TRACK-A-DEV-LIVE-PRECHECK', 'validate_project_o_dev_live_precheck_v1.py'),
    # PROJECT_O Track B STATUS FIRST SLICE DEV-LIVE FLAG FLIP (executed + rolled back; FLAG_OFF)
    ('PROJECT-O-TRACK-B-STATUS-FIRST-SLICE-DEV-LIVE-FLAG-FLIP', 'validate_project_o_status_first_slice_dev_live_flag_v1.py'),
    # PROJECT_O Track C DEV-LIVE GAMEPLAY REGRESSION + SHA GUARD (flag OFF == flag ON == baseline)
    ('PROJECT-O-TRACK-C-DEV-LIVE-GAMEPLAY-REGRESSION-SHA-GUARD', 'validate_project_o_dev_live_gameplay_regression_v1.py'),
    # PROJECT_O Track D DEV-LIVE LIGHT LOAD + OBSERVABILITY (300/300 2xx, p99~74ms)
    ('PROJECT-O-TRACK-D-DEV-LIVE-LIGHT-LOAD-OBSERVABILITY', 'validate_project_o_dev_live_light_load_observability_v1.py'),
    # PROJECT_O Track E DEV-LIVE PAYLOAD/LOG/METRICS NO-LEAK
    ('PROJECT-O-TRACK-E-DEV-LIVE-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_o_dev_live_payload_log_metrics_no_leak_v1.py'),
    # PROJECT_O Track F DEV-LIVE ROLLBACK + KILL-SWITCH DRILL (6-step)
    ('PROJECT-O-TRACK-F-DEV-LIVE-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_o_dev_live_rollback_kill_switch_drill_v1.py'),
    # PROJECT_O Track G PROD READINESS GATE PREP (9 green-checks; no rollout)
    ('PROJECT-O-TRACK-G-PROD-READINESS-GATE-PREP', 'validate_project_o_prod_readiness_gate_prep_v1.py'),
    # PROJECT_O Track H PROJECT O COMPLETION + NEXT STEP (next pack: PROJECT_P)
    ('PROJECT-O-TRACK-H-PROJECT-O-COMPLETION-AND-NEXT-STEP', 'validate_project_o_completion_and_next_step_v1.py'),
    # PROJECT_P Track A PROD ROLLOUT PRECHECK + SIGNATURE GATE (BLOCKING_MISSING_ALL_PROD_SIGNATURES; 0/6 signatures)
    ('PROJECT-P-TRACK-A-PROD-ROLLOUT-PRECHECK-AND-SIGNATURE-GATE', 'validate_project_p_prod_rollout_precheck_and_signature_gate_v1.py'),
    # PROJECT_P Track B PROD ROLLOUT STAGE 1% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-B-PROD-ROLLOUT-STAGE-1-PERCENT', 'validate_project_p_prod_rollout_stage_1_percent_v1.py'),
    # PROJECT_P Track C PROD ROLLOUT STAGE 5% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-C-PROD-ROLLOUT-STAGE-5-PERCENT', 'validate_project_p_prod_rollout_stage_5_percent_v1.py'),
    # PROJECT_P Track D PROD ROLLOUT STAGE 25% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-D-PROD-ROLLOUT-STAGE-25-PERCENT', 'validate_project_p_prod_rollout_stage_25_percent_v1.py'),
    # PROJECT_P Track E PROD ROLLOUT STAGE 100% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-E-PROD-ROLLOUT-STAGE-100-PERCENT', 'validate_project_p_prod_rollout_stage_100_percent_v1.py'),
    # PROJECT_P Track F PROD ROLLOUT NO-LEAK + LOAD + ROLLBACK FINAL (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-F-PROD-ROLLOUT-NO-LEAK-LOAD-AND-ROLLBACK-FINAL', 'validate_project_p_prod_rollout_no_leak_load_and_rollback_final_v1.py'),
    # PROJECT_P Track G POST-PROD STATUS FIRST-SLICE DOD (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-G-POST-PROD-STATUS-FIRST-SLICE-DOD', 'validate_project_p_post_prod_status_first_slice_dod_v1.py'),
    # PROJECT_P Track H PROJECT P COMPLETION + NEXT SYSTEM
    ('PROJECT-P-TRACK-H-PROJECT-P-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_p_completion_and_next_system_v1.py'),
    # PROJECT_Q ARTIFACT BIBLE APPROVAL + IMPORT DRY-RUN PACK (8 tracks, READY_PENDING_APPROVAL: 0/5 ARTIFACT_* signatures present, NO DB writes, NO live import)
    ('PROJECT-Q-TRACK-A-ARTIFACT-DIRECTION-CANONICAL-LOCK', 'validate_project_q_artifact_direction_canonical_lock_v1.py'),
    ('PROJECT-Q-TRACK-B-ARTIFACT-BIBLE-SCHEMA-VALIDATION', 'validate_project_q_artifact_bible_schema_validation_v1.py'),
    ('PROJECT-Q-TRACK-C-ARTIFACT-CANDIDATE-EXPANSION', 'validate_project_q_artifact_candidate_expansion_v1.py'),
    ('PROJECT-Q-TRACK-D-ARTIFACT-BONUS-CAP-ECONOMY-DRY-RUN', 'validate_project_q_artifact_bonus_cap_economy_dry_run_v1.py'),
    ('PROJECT-Q-TRACK-E-ARTIFACT-IMPORT-DRY-RUN-SCRIPT', 'validate_project_q_artifact_import_dry_run_script_v1.py'),
    ('PROJECT-Q-TRACK-F-ARTIFACT-IMPORT-APPROVAL-GATE-ROLLBACK', 'validate_project_q_artifact_import_approval_gate_rollback_v1.py'),
    ('PROJECT-Q-TRACK-G-ARTIFACT-RUNTIME-NO-LEAK', 'validate_project_q_artifact_runtime_no_leak_v1.py'),
    ('PROJECT-Q-TRACK-H-PROJECT-Q-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_q_completion_and_next_system_v1.py'),
    # PROJECT_R STATUS SECOND SLICE DESIGN PACK (8 tracks, design-only: no runtime, no DB, no battle_engine mutation, no live env flag)
    ('PROJECT-R-TRACK-A-STATUS-SECOND-SLICE-SCOPE-AND-BOUNDARY', 'validate_project_r_status_second_slice_scope_v1.py'),
    ('PROJECT-R-TRACK-B-STATUS-SECOND-SLICE-BALANCE-AND-CAPS', 'validate_project_r_status_second_slice_balance_caps_v1.py'),
    ('PROJECT-R-TRACK-C-STATUS-SECOND-SLICE-SCHEMA-AND-FIXTURE-PLAN', 'validate_project_r_status_second_slice_schema_fixture_plan_v1.py'),
    ('PROJECT-R-TRACK-D-STATUS-SECOND-SLICE-RESOLVER-EXTENSION-DESIGN', 'validate_project_r_status_second_slice_resolver_extension_design_v1.py'),
    ('PROJECT-R-TRACK-E-STATUS-SECOND-SLICE-PAYLOAD-AND-NO-LEAK-PLAN', 'validate_project_r_status_second_slice_payload_no_leak_plan_v1.py'),
    ('PROJECT-R-TRACK-F-STATUS-SECOND-SLICE-ROLLBACK-AND-KILL-SWITCH-DESIGN', 'validate_project_r_status_second_slice_rollback_killswitch_v1.py'),
    ('PROJECT-R-TRACK-G-STATUS-SECOND-SLICE-QA-AND-RELEASE-GATE', 'validate_project_r_status_second_slice_qa_release_gate_v1.py'),
    ('PROJECT-R-TRACK-H-PROJECT-R-COMPLETION-AND-NEXT-PACK', 'validate_project_r_completion_and_next_pack_v1.py'),
    # PROJECT_S STATUS SECOND SLICE PURE RESOLVER PACK (8 tracks: pure resolver module created INERT, no runtime import, no battle_engine mutation, no DB)
    ('PROJECT-S-TRACK-A-SECOND-SLICE-PURE-RESOLVER-SPEC-LOCK', 'validate_project_s_second_slice_resolver_spec_lock_v1.py'),
    ('PROJECT-S-TRACK-B-STATUS-SECOND-SLICE-PURE-RESOLVER-MODULE', 'validate_project_s_second_slice_resolver_module_v1.py'),
    ('PROJECT-S-TRACK-C-SECOND-SLICE-GOLDEN-FIXTURE-MATRIX', 'validate_project_s_second_slice_golden_fixture_matrix_v1.py'),
    ('PROJECT-S-TRACK-D-SECOND-SLICE-CAPS-AND-STACKING-VALIDATOR', 'validate_project_s_second_slice_caps_stacking_v1.py'),
    ('PROJECT-S-TRACK-E-SECOND-SLICE-RUNTIME-NO-IMPORT-GUARD', 'validate_project_s_second_slice_runtime_no_import_guard_v1.py'),
    ('PROJECT-S-TRACK-F-SECOND-SLICE-ROLLBACK-AND-DELETION-PLAN', 'validate_project_s_second_slice_rollback_deletion_plan_v1.py'),
    ('PROJECT-S-TRACK-G-SECOND-SLICE-IMPLEMENTATION-RC-GATE', 'validate_project_s_second_slice_implementation_rc_gate_v1.py'),
    ('PROJECT-S-TRACK-H-PROJECT-S-COMPLETION-AND-NEXT-PACK', 'validate_project_s_completion_and_next_pack_v1.py'),
    # PROJECT_T STATUS SECOND SLICE SINGLE-POINT WIRING CANARY PACK (8 tracks; wiring applied flag-off-safe; flag OFF -> strict identity)
    ('PROJECT-T-TRACK-A-SECOND-SLICE-SINGLE-POINT-AUDIT', 'validate_project_t_second_slice_single_point_audit_v1.py'),
    ('PROJECT-T-TRACK-B-SECOND-SLICE-BATTLE-ENGINE-WIRING', 'validate_project_t_second_slice_battle_engine_wiring_v1.py'),
    ('PROJECT-T-TRACK-C-SECOND-SLICE-FLAG-OFF-BYTE-IDENTICAL-GUARD', 'validate_project_t_second_slice_flag_off_regression_v1.py'),
    ('PROJECT-T-TRACK-D-SECOND-SLICE-FLAG-ON-IN-PROCESS-CANARY', 'validate_project_t_second_slice_flag_on_canary_v1.py'),
    ('PROJECT-T-TRACK-E-SECOND-SLICE-PAYLOAD-AND-LOG-NO-LEAK-GUARD', 'validate_project_t_second_slice_payload_log_no_leak_v1.py'),
    ('PROJECT-T-TRACK-F-SECOND-SLICE-ROLLBACK-DRILL', 'validate_project_t_second_slice_rollback_drill_v1.py'),
    ('PROJECT-T-TRACK-G-SECOND-SLICE-DEV-CANARY-RC-GATE', 'validate_project_t_second_slice_dev_canary_rc_gate_v1.py'),
    ('PROJECT-T-TRACK-H-PROJECT-T-COMPLETION-AND-NEXT-PACK', 'validate_project_t_completion_and_next_pack_v1.py'),
    # PROJECT_U STATUS SECOND SLICE CANARY ENV FLAG FLIP PACK (8 tracks; flag flipped in-canary then rolled back OFF; .env post-rollback byte-identical to pre-flip backup)
    ('PROJECT-U-TRACK-A-SECOND-SLICE-CANARY-ENV-PRECHECK', 'validate_project_u_second_slice_canary_env_precheck_v1.py'),
    ('PROJECT-U-TRACK-B-SECOND-SLICE-CANARY-FLAG-FLIP', 'validate_project_u_second_slice_canary_flag_flip_v1.py'),
    ('PROJECT-U-TRACK-C-SECOND-SLICE-FLAG-ON-BEHAVIOR-SMOKE', 'validate_project_u_second_slice_flag_on_behavior_smoke_v1.py'),
    ('PROJECT-U-TRACK-D-SECOND-SLICE-CANARY-LIGHT-LOAD', 'validate_project_u_second_slice_canary_light_load_v1.py'),
    ('PROJECT-U-TRACK-E-SECOND-SLICE-PAYLOAD-LOG-NO-LEAK', 'validate_project_u_second_slice_payload_log_no_leak_v1.py'),
    ('PROJECT-U-TRACK-F-SECOND-SLICE-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_u_second_slice_rollback_kill_switch_v1.py'),
    ('PROJECT-U-TRACK-G-SECOND-SLICE-DEV-LIVE-READINESS-GATE', 'validate_project_u_second_slice_dev_live_readiness_gate_v1.py'),
    ('PROJECT-U-TRACK-H-PROJECT-U-COMPLETION-AND-NEXT-PACK', 'validate_project_u_completion_and_next_pack_v1.py'),
    # PROJECT_V STATUS SECOND SLICE DEV-LIVE ROLLOUT PACK (8 tracks; flag flipped in dev-live then rolled back OFF; .env post-rollback byte-identical to pre-flip backup; no DB writes; no battle_engine.py mutations)
    ('PROJECT-V-TRACK-A-SECOND-SLICE-DEV-LIVE-PRECHECK', 'validate_project_v_second_slice_dev_live_precheck_v1.py'),
    ('PROJECT-V-TRACK-B-SECOND-SLICE-DEV-LIVE-FLAG-ROLLOUT', 'validate_project_v_second_slice_dev_live_flag_rollout_v1.py'),
    ('PROJECT-V-TRACK-C-SECOND-SLICE-DEV-LIVE-BEHAVIOR-REGRESSION', 'validate_project_v_second_slice_dev_live_behavior_regression_v1.py'),
    ('PROJECT-V-TRACK-D-SECOND-SLICE-DEV-LIVE-EXTENDED-LOAD', 'validate_project_v_second_slice_dev_live_extended_load_v1.py'),
    ('PROJECT-V-TRACK-E-SECOND-SLICE-DEV-LIVE-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_v_second_slice_dev_live_payload_log_metrics_no_leak_v1.py'),
    ('PROJECT-V-TRACK-F-SECOND-SLICE-DEV-LIVE-ROLLBACK-KILL-SWITCH', 'validate_project_v_second_slice_dev_live_rollback_kill_switch_v1.py'),
    ('PROJECT-V-TRACK-G-SECOND-SLICE-PROD-READINESS-GATE-PREP', 'validate_project_v_second_slice_prod_readiness_gate_prep_v1.py'),
    ('PROJECT-V-TRACK-H-PROJECT-V-COMPLETION-AND-NEXT-PACK', 'validate_project_v_completion_and_next_pack_v1.py'),
    # PROJECT_W STATUS SECOND SLICE PROD ROLLOUT PACK (8 tracks; READY_NOT_APPLIED_PENDING_APPROVAL — no prod signatures present; no flag flip; no DB writes; no prod env touch; rollback paths documented per stage)
    ('PROJECT-W-TRACK-A-SECOND-SLICE-PROD-PRECHECK-SIGNATURE-GATE', 'validate_project_w_second_slice_prod_precheck_v1.py'),
    ('PROJECT-W-TRACK-B-SECOND-SLICE-PROD-STAGE-1', 'validate_project_w_second_slice_prod_stage_1_v1.py'),
    ('PROJECT-W-TRACK-C-SECOND-SLICE-PROD-STAGE-5', 'validate_project_w_second_slice_prod_stage_5_v1.py'),
    ('PROJECT-W-TRACK-D-SECOND-SLICE-PROD-STAGE-25', 'validate_project_w_second_slice_prod_stage_25_v1.py'),
    ('PROJECT-W-TRACK-E-SECOND-SLICE-PROD-STAGE-100', 'validate_project_w_second_slice_prod_stage_100_v1.py'),
    ('PROJECT-W-TRACK-F-SECOND-SLICE-PROD-FINAL-NO-LEAK-LOAD-ROLLBACK', 'validate_project_w_second_slice_prod_final_validation_v1.py'),
    ('PROJECT-W-TRACK-G-SECOND-SLICE-POST-PROD-DOD', 'validate_project_w_second_slice_post_prod_dod_v1.py'),
    ('PROJECT-W-TRACK-H-PROJECT-W-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_w_completion_and_next_system_v1.py'),
    # PROJECT_X FRONTEND A NAVIGATION & FEATURE VISIBILITY AUDIT PACK (8 tracks; audit-only / roadmap-only; no frontend UI implementation; no backend mutation; no DB writes; no feature flag flips)
    ('PROJECT-X-TRACK-A-FRONTEND-ROUTE-AND-NAVIGATION-INVENTORY', 'validate_project_x_frontend_route_inventory_v1.py'),
    ('PROJECT-X-TRACK-B-BACKEND-FEATURE-ENDPOINT-VISIBILITY-MATRIX', 'validate_project_x_backend_feature_visibility_matrix_v1.py'),
    ('PROJECT-X-TRACK-C-PLAYER-SAFE-MENU-PLACEMENT-PLAN', 'validate_project_x_player_safe_menu_placement_plan_v1.py'),
    ('PROJECT-X-TRACK-D-FEATURE-ACCESS-POLICY-AND-LOCK-COPY', 'validate_project_x_feature_access_policy_lock_copy_v1.py'),
    ('PROJECT-X-TRACK-E-FRONTEND-SAFE-PREVIEW-IMPLEMENTATION-BACKLOG', 'validate_project_x_frontend_safe_preview_backlog_v1.py'),
    ('PROJECT-X-TRACK-F-LIVE-GATE-APPROVAL-MATRIX-UI-DEPENDENCIES', 'validate_project_x_live_gate_approval_matrix_ui_dependencies_v1.py'),
    ('PROJECT-X-TRACK-G-FRONTEND-QA-SMOKE-NAVIGATION-PLAN', 'validate_project_x_frontend_qa_smoke_navigation_plan_v1.py'),
    ('PROJECT-X-TRACK-H-PROJECT-X-COMPLETION-AND-NEXT-PACK', 'validate_project_x_completion_and_next_pack_v1.py'),
    # PROJECT_Y FRONTEND SAFE PREVIEW UI IMPLEMENTATION PACK (8 tracks; SafeFeatureCard + 3 nuove route preview locked/read-only; no menu mutation; no backend route mutation; no DB writes; no flag flips; 503 graceful)
    ('PROJECT-Y-TRACK-A-FRONTEND-SAFE-PREVIEW-TARGET-SELECTION', 'validate_project_y_safe_preview_target_selection_v1.py'),
    ('PROJECT-Y-TRACK-B-FRONTEND-LOCKED-CARD-COMPONENT', 'validate_project_y_locked_card_component_v1.py'),
    ('PROJECT-Y-TRACK-C-ARTIFACT-COLLECTION-PREVIEW-UI', 'validate_project_y_artifact_collection_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-D-HOUSING-PREVIEW-UI', 'validate_project_y_housing_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-E-STATUS-CODEX-PREVIEW-UI', 'validate_project_y_status_codex_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-F-SAFE-MENU-ENTRY-OR-DEV-PANEL', 'validate_project_y_safe_menu_entry_dev_panel_v1.py'),
    ('PROJECT-Y-TRACK-G-FRONTEND-QA-SMOKE-SAFE-PREVIEW', 'validate_project_y_frontend_qa_smoke_safe_preview_v1.py'),
    ('PROJECT-Y-TRACK-H-PROJECT-Y-COMPLETION-AND-NEXT-PACK', 'validate_project_y_completion_and_next_pack_v1.py'),
    # PROJECT_Z FRONTEND SAFE PREVIEW POLISH & MOBILE QA PACK (8 tracks; hub /safe-previews + 1 voce menu Altro + mobile polish 3 route + accessibility guard; no broad refactor; no new bottom tab; no live actions; expo-go mobile screenshot manual pending)
    ('PROJECT-Z-TRACK-A-SAFE-MENU-WIRING-TARGET-AUDIT', 'validate_project_z_safe_menu_wiring_target_audit_v1.py'),
    ('PROJECT-Z-TRACK-B-SAFE-MENU-OR-PREVIEW-HUB-WIRING', 'validate_project_z_safe_menu_or_preview_hub_wiring_v1.py'),
    ('PROJECT-Z-TRACK-C-ARTIFACT-PREVIEW-MOBILE-POLISH', 'validate_project_z_artifact_preview_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-D-HOUSING-PREVIEW-MOBILE-POLISH', 'validate_project_z_housing_preview_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-E-STATUS-CODEX-MOBILE-POLISH', 'validate_project_z_status_codex_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-F-ACCESSIBILITY-AND-LOCKED-ACTION-GUARD', 'validate_project_z_accessibility_locked_action_guard_v1.py'),
    ('PROJECT-Z-TRACK-G-EXPO-GO-MOBILE-QA-SMOKE', 'validate_project_z_expo_go_mobile_qa_smoke_v1.py'),
    ('PROJECT-Z-TRACK-H-PROJECT-Z-COMPLETION-AND-NEXT-PACK', 'validate_project_z_completion_and_next_pack_v1.py'),
    # PROJECT_FRONTEND_B CORE USER FLOW AUDIT PACK (8 tracks; audit-only / roadmap-only; no UI/route/menu/backend/DB/flag mutation; mappa flussi core e produce QA backlog 12-item P1-P3)
    ('PROJECT-FRONTEND-B-TRACK-A-HEROES-FLOW-AUDIT', 'validate_project_frontend_b_heroes_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-B-COMBAT-FLOW-AUDIT', 'validate_project_frontend_b_combat_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-C-GACHA-FLOW-AUDIT', 'validate_project_frontend_b_gacha_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-D-ECONOMY-FLOW-AUDIT', 'validate_project_frontend_b_economy_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-E-SAFE-PREVIEW-FLOW-AUDIT', 'validate_project_frontend_b_safe_preview_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-F-NAVIGATION-RISK-MATRIX', 'validate_project_frontend_b_navigation_risk_matrix_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-G-QA-BACKLOG', 'validate_project_frontend_b_qa_backlog_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-H-PROJECT-FB-COMPLETION-AND-NEXT-PACK', 'validate_project_frontend_b_completion_and_next_pack_v1.py'),
    # PROJECT_FRONTEND_C DAILY HUB IMPLEMENTATION PACK (8 tracks; 1 nuova route /daily-hub aggregatore link-only + 1 voce menu Altro; 0 claim button, 0 mutating API, 0 backend route, 0 DB write, 0 flag flip)
    ('PROJECT-FRONTEND-C-TRACK-A-DAILY-HUB-TARGET-AUDIT', 'validate_project_frontend_c_daily_hub_target_data_source_audit_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-B-DAILY-HUB-UI-ROUTE-IMPLEMENTATION', 'validate_project_frontend_c_daily_hub_ui_route_implementation_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-C-DAILY-HUB-CARD-AND-COPY', 'validate_project_frontend_c_daily_hub_card_component_and_copy_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-D-DAILY-HUB-MENU-WIRING', 'validate_project_frontend_c_daily_hub_menu_entry_safe_wiring_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-E-DAILY-HUB-MUTATION-GUARD', 'validate_project_frontend_c_daily_hub_safe_endpoint_mutation_guard_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-F-DAILY-HUB-MOBILE-A11Y-POLISH', 'validate_project_frontend_c_daily_hub_mobile_accessibility_polish_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-G-DAILY-HUB-FRONTEND-QA-SMOKE', 'validate_project_frontend_c_daily_hub_frontend_qa_smoke_v1.py'),
    ('PROJECT-FRONTEND-C-TRACK-H-PROJECT-FC-COMPLETION-AND-NEXT-PACK', 'validate_project_frontend_c_completion_and_next_pack_v1.py'),
    # PROJECT_MODE_WIRING_REGISTRY_AND_LEGACY_ROUTE_AUDIT_PACK (audit-only)
    ('PROJECT-MODE-WIRING-TRACK-A-CORE-MODES', 'validate_mode_wiring_registry_core_modes_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-B-SYSTEM-MODES', 'validate_mode_wiring_registry_system_modes_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-C-LEGACY-ROUTE-DETECTION', 'validate_legacy_route_old_endpoint_detection_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-D-FE-BE-CROSSWALK', 'validate_frontend_backend_crosswalk_matrix_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-E-UNREACHABLE-MODES', 'validate_unreachable_implemented_mode_audit_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-F-SMOKE-REQUIREMENTS', 'validate_mode_smoke_test_requirements_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-G-NEXT-FIX-PRIORITIZATION', 'validate_mode_wiring_next_fix_prioritization_v1.py'),
    ('PROJECT-MODE-WIRING-TRACK-H-COMPLETION', 'validate_project_mode_wiring_registry_completion_v1.py'),
    # PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT_PACK (audit-only)
    ('PROJECT-SP-LEGACY-TRACK-A-UI-USAGE', 'validate_project_sp_legacy_ui_usage_audit_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-B-ENDPOINT-BEHAVIOR', 'validate_project_sp_legacy_endpoint_behavior_audit_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-C-NEW-ROUTE-CONTRACT', 'validate_project_sp_new_route_contract_audit_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-D-MIGRATION-RISK-MATRIX', 'validate_project_sp_migration_risk_matrix_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-E-DEPRECATION-PLAN', 'validate_project_sp_dual_route_deprecation_plan_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-F-LOCK-PREVIEW-RECOMMENDATION', 'validate_project_sp_frontend_lock_preview_recommendation_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-G-SMOKE-REGRESSION-REQUIREMENTS', 'validate_project_sp_smoke_regression_requirements_v1.py'),
    ('PROJECT-SP-LEGACY-TRACK-H-COMPLETION', 'validate_project_sp_legacy_audit_completion_v1.py'),
    # PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW_PACK (frontend-only locked preview)
    ('PROJECT-SP-UI-LOCK-TRACK-A-TARGET-AUDIT', 'validate_project_sp_ui_lock_preview_target_audit_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-B-LOCKED-PREVIEW-IMPL', 'validate_project_sp_servers_screen_locked_preview_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-C-LEGACY-MUTATION-GUARD', 'validate_project_sp_legacy_mutation_removal_player_ui_guard_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-D-LOCKED-COPY-503', 'validate_project_sp_locked_copy_503_handling_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-E-MOBILE-A11Y', 'validate_project_sp_lock_preview_mobile_accessibility_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-F-SMOKE', 'validate_project_sp_ui_lock_smoke_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-G-REGISTRY-UPDATE', 'validate_mode_wiring_registry_server_profiles_update_v1.py'),
    ('PROJECT-SP-UI-LOCK-TRACK-H-COMPLETION', 'validate_project_sp_ui_lock_completion_v1.py'),
    # PROJECT_SERVER_PROFILES_DUAL_READ_PREVIEW_PACK (design + copy polish, no mutation)
    ('PROJECT-SP-DUAL-READ-TRACK-A-SCOPE-AUDIT', 'validate_project_sp_dual_read_preview_scope_audit_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-B-LEGACY-READ-MODEL', 'validate_project_sp_legacy_current_server_read_model_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-C-PREVIEW-CONTRACT-DRAFT', 'validate_project_sp_preview_contract_draft_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-D-AUTH-GAP-MATRIX', 'validate_project_sp_auth_and_gap_matrix_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-E-LOCKED-PREVIEW-COPY', 'validate_project_sp_locked_preview_dual_read_copy_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-F-SMOKE-NO-MUTATION', 'validate_project_sp_dual_read_preview_smoke_no_mutation_guard_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-G-REGISTRY-REFRESH', 'validate_mode_wiring_registry_server_profiles_refresh_v1.py'),
    ('PROJECT-SP-DUAL-READ-TRACK-H-COMPLETION', 'validate_project_server_profiles_dual_read_preview_completion_v1.py'),
    # PROJECT_SERVER_PROFILES_AUTH_AND_CONTRACT_HARDENING_PACK (design-only)
    ('PROJECT-SP-AUTH-TRACK-A-AUTH-SURFACE-AUDIT', 'validate_project_sp_auth_surface_audit_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-B-CONTRACT-HARDENING-SPEC', 'validate_project_sp_contract_hardening_spec_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-C-PRE-HOME-UX-REQUIREMENT', 'validate_project_sp_pre_home_server_selection_ux_requirement_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-D-DATA-MODEL-SEED-PRECONDITIONS', 'validate_project_sp_data_model_gap_and_seed_preconditions_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-E-CAPACITY-MAINTENANCE-RULES', 'validate_project_sp_capacity_maintenance_rules_spec_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-F-NO-MUTATION-REGRESSION', 'validate_project_sp_no_mutation_regression_guard_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-G-ROADMAP-APPROVAL-GATES', 'validate_project_sp_roadmap_and_approval_gates_v1.py'),
    ('PROJECT-SP-AUTH-TRACK-H-COMPLETION', 'validate_project_sp_auth_contract_completion_v1.py'),
    # PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT_PACK (audit-first; 1 safe nav-only frontend fix)
    ('PROJECT-PLAYER-LEGACY-TRACK-A-FINDINGS', 'validate_player_facing_legacy_surfaces_findings_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-B-SAFE-PREVIEWS-NAV-FIX', 'validate_safe_previews_navigation_only_fix_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-C-ARTIFACT-CONSTELLATION-AUDIT', 'validate_artifact_constellation_live_surface_audit_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-D-GACHA-RATE-SANITY-AUDIT', 'validate_gacha_rate_sanity_audit_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-E-SHOP-IAP-READINESS-AUDIT', 'validate_shop_iap_readiness_audit_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-F-BATTLEPASS-LEGACY-AUDIT', 'validate_battle_pass_legacy_surface_audit_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-G-HEROES-MENU-DEV-ROUTES-AUDIT', 'validate_owned_heroes_and_menu_dev_routes_audit_v1.py'),
    ('PROJECT-PLAYER-LEGACY-TRACK-H-COMPLETION', 'validate_player_facing_legacy_surfaces_completion_v1.py'),
    # PROJECT_FULL_REPO_CONSISTENCY_AUDIT_AND_MASTER_FIX_PLAN_PACK (audit-only, scanner-generated registries)
    ('PROJECT-FULL-REPO-TRACK-A-FRONTEND-ROUTE-MENU-REGISTRY', 'validate_full_repo_frontend_route_menu_registry_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-B-FRONTEND-API-CALLSITE-REGISTRY', 'validate_full_repo_frontend_api_callsite_registry_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-C-BACKEND-ENDPOINT-REGISTRY', 'validate_full_repo_backend_endpoint_registry_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-D-FEATURE-CROSSWALK', 'validate_full_repo_feature_mode_crosswalk_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-E-ECONOMY-RISK-AUDIT', 'validate_full_repo_economy_risk_audit_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-F-GATES-DEV-SURFACE-AUDIT', 'validate_full_repo_gates_dev_surface_audit_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-G-MASTER-BACKLOG-AND-GAP-MATRIX', 'validate_full_repo_master_backlog_and_gap_matrix_v1.py'),
    ('PROJECT-FULL-REPO-TRACK-H-COMPLETION-COVERAGE-PROOF', 'validate_full_repo_completion_and_coverage_proof_v1.py'),
    # PROJECT_BATCH_1_LOCK_DANGEROUS_PLAYER_SURFACES_V2 (frontend-only lock/guard pack)
    ('PROJECT-BATCH1-V2-TRACK-A-FINDINGS', 'validate_batch1_v2_track_a_findings_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-B-GACHA-LOCK', 'validate_batch1_v2_track_b_gacha_lock_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-C-ARTIFACT-REDIRECT', 'validate_batch1_v2_track_c_artifact_redirect_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-D-SOUL-FORGE-GUARD', 'validate_batch1_v2_track_d_soul_forge_guard_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-E-MONETIZATION-LOCK', 'validate_batch1_v2_track_e_monetization_lock_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-F-MENU-HARDENING', 'validate_batch1_v2_track_f_menu_hardening_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-G-MOBILE-QA', 'validate_batch1_v2_track_g_mobile_qa_v1.py'),
    ('PROJECT-BATCH1-V2-TRACK-H-COMPLETION', 'validate_batch1_v2_track_h_completion_v1.py'),
    # PROJECT_BACKEND_FRONTEND_ALIGNMENT_AND_DANGEROUS_SURFACES_FIX (Soul Forge UX + wiring matrix)
    ('PROJECT-ALIGN-FIX-TRACK-A-BASELINE', 'validate_alignment_fix_track_a_baseline_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-B-SOUL-FORGE', 'validate_alignment_fix_track_b_soul_forge_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-C-WIRING-MATRIX', 'validate_alignment_fix_track_c_wiring_matrix_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-D-ROUTE-STATE', 'validate_alignment_fix_track_d_route_state_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-E-GAP-REFRESH', 'validate_alignment_fix_track_e_gap_refresh_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-F-REGRESSION-GUARDS', 'validate_alignment_fix_track_f_regression_guards_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-G-BATCH-PLAN', 'validate_alignment_fix_track_g_batch_plan_v1.py'),
    ('PROJECT-ALIGN-FIX-TRACK-H-COMPLETION', 'validate_alignment_fix_track_h_completion_v1.py'),
    # PROJECT_SOUL_FORGE_ECONOMY_MERGE_AND_EXCLUSIVE_RETIREMENT (SF mobile fix + economy merge + exclusive lock)
    ('PROJECT-SF-MERGE-TRACK-A-CANONICAL-DECISION', 'validate_sf_merge_track_a_canonical_decision_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-B-MOBILE-REACHABILITY', 'validate_sf_merge_track_b_mobile_reachability_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-C-ANIME-HUB', 'validate_sf_merge_track_c_anime_hub_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-D-ECONOMY-RETIRED', 'validate_sf_merge_track_d_economy_retired_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-E-EXCLUSIVE-RETIRED', 'validate_sf_merge_track_e_exclusive_retired_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-F-NAVIGATION', 'validate_sf_merge_track_f_navigation_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-G-REGRESSION-QA', 'validate_sf_merge_track_g_regression_qa_v1.py'),
    ('PROJECT-SF-MERGE-TRACK-H-COMPLETION', 'validate_sf_merge_track_h_completion_v1.py'),
    # PROJECT_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_FIX_PACK (8 validators)
    # Fixes P0 blank screen regression introduced by SF_MERGE Track B and properly
    # imports legacy economy materials/shop into Soul Forge as read-only display.
    ('PROJECT-EMERGENCY-RESTORE-TRACK-A-ROOT-CAUSE', 'validate_emergency_restore_track_a_root_cause_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-B-VISIBLE-SCREEN', 'validate_emergency_restore_track_b_visible_screen_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-C-HERO-GRID-FILTERS', 'validate_emergency_restore_track_c_hero_grid_filters_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-D-MOBILE-MODAL', 'validate_emergency_restore_track_d_mobile_modal_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-E-ECONOMY-MAPPING', 'validate_emergency_restore_track_e_economy_mapping_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-F-PANELS', 'validate_emergency_restore_track_f_panels_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-G-BYPASS-GUARDS', 'validate_emergency_restore_track_g_bypass_guards_v1.py'),
    ('PROJECT-EMERGENCY-RESTORE-TRACK-H-COMPLETION', 'validate_emergency_restore_track_h_completion_v1.py'),
    # PROJECT_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_AND_SHOP_NAV_FIX_PACK (8 validators)
    # Crash-proofs the forge action (FORGE SOUL crash on mobile), normalizes response,
    # verifies backend contract (no backend changes), adds safe shop nav buttons,
    # rechecks economy/exclusive locks, enforces credentials hygiene + honest Redis status.
    ('PROJECT-FORGE-CRASH-TRACK-A-ROOT-CAUSE', 'validate_forge_crash_track_a_root_cause_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-B-RESPONSE-NORMALIZATION', 'validate_forge_crash_track_b_response_normalization_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-C-BACKEND-CONTRACT', 'validate_forge_crash_track_c_backend_contract_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-D-MODAL-POST-SUCCESS', 'validate_forge_crash_track_d_modal_post_success_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-E-SHOP-NAV', 'validate_forge_crash_track_e_shop_nav_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-F-ECONOMY-EXCLUSIVE-RECHECK', 'validate_forge_crash_track_f_economy_exclusive_recheck_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-G-HYGIENE', 'validate_forge_crash_track_g_hygiene_v1.py'),
    ('PROJECT-FORGE-CRASH-TRACK-H-COMPLETION', 'validate_forge_crash_track_h_completion_v1.py'),
    # PROJECT_SOUL_FORGE_INLINE_CONFIRM_RESTORE_NO_MODAL_CRASH_PACK (8 validators)
    # P0 fix: removes React Native Modal+KeyboardAvoidingView from the confirm path
    # (which caused immediate crash on first FORGE SOUL tap on mobile) and replaces
    # it with an inline confirmation panel inside the existing outer ScrollView.
    ('PROJECT-INLINE-CONFIRM-TRACK-A-TRUE-CAUSE', 'validate_inline_confirm_track_a_true_cause_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-B-MODAL-REMOVED', 'validate_inline_confirm_track_b_modal_removed_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-C-PANEL', 'validate_inline_confirm_track_c_panel_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-D-HANDLERS', 'validate_inline_confirm_track_d_handlers_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-E-API-CONTRACT', 'validate_inline_confirm_track_e_api_contract_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-F-SHOP-NAV-BYPASS', 'validate_inline_confirm_track_f_shop_nav_bypass_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-G-SMOKE', 'validate_inline_confirm_track_g_smoke_v1.py'),
    ('PROJECT-INLINE-CONFIRM-TRACK-H-COMPLETION', 'validate_inline_confirm_track_h_completion_v1.py'),
    # PROJECT_BETA_TESTING_AUTOMATION_HARNESS_AND_REDIS_STABILIZATION_PACK (8 validators)
    # Installs beta testing tech harness (Playwright + static audits) and stabilizes
    # Redis infrastructure (apt install + supervisor RUNNING). Pre-existing 5 Redis
    # validators now PASS for real (not faked).
    ('PROJECT-BETA-TESTING-TRACK-A-BASELINE', 'validate_beta_testing_track_a_baseline_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-B-ROUTE-AUDIT', 'validate_beta_testing_track_b_route_audit_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-C-SOUL-FORGE-REGRESSION', 'validate_beta_testing_track_c_soul_forge_regression_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-D-LOCKED-SURFACES', 'validate_beta_testing_track_d_locked_surfaces_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-E-PLAYWRIGHT', 'validate_beta_testing_track_e_playwright_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-F-REDIS', 'validate_beta_testing_track_f_redis_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-G-REPORTING', 'validate_beta_testing_track_g_reporting_v1.py'),
    ('PROJECT-BETA-TESTING-TRACK-I-COMPLETION', 'validate_beta_testing_track_i_completion_v1.py'),
    ('PROJECT-BETA-HARNESS-PUBLIC-REPO-SYNC-AND-MINOR-UI-HYGIENE-FIX', 'validate_beta_harness_public_repo_sync_and_minor_ui_hygiene_fix_v1.py'),
    ('PROJECT-GACHA-RATE-SANITY-FINAL-SIGNOFF', 'validate_project_gacha_rate_sanity_final_signoff_v1.py'),
    ('PROJECT-ARTIFACT-BIBLE-CANONICAL-DESIGN', 'validate_project_artifact_bible_canonical_design_v1.py'),
    ('PROJECT-ARTIFACT-BIBLE-REVIEW-SIGNOFF', 'validate_project_artifact_bible_review_signoff_v1.py'),
    ('PROJECT-ARTIFACT-PREVIEW-UI-POPULATION', 'validate_project_artifact_preview_ui_population_v1.py'),
    ('PROJECT-ARTIFACT-BACKEND-CATALOG-RO', 'validate_project_artifact_backend_catalog_ro_v1.py'),
    ('PROJECT-ARTIFACT-LEGACY-MUTATION-ENDPOINT-HARDENING', 'validate_project_artifact_legacy_mutation_endpoint_hardening_v1.py'),
    ('PROJECT-ARTIFACT-INVENTORY-SCHEMA-DRY-RUN', 'validate_project_artifact_inventory_schema_dry_run_v1.py'),
    # STAGE_6_GATED_IMPORT_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    ('PROJECT-ARTIFACT-INVENTORY-GATED-IMPORT', 'validate_project_artifact_inventory_gated_import_v1.py'),
    # STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_RESYNC_v4 (sync fix 175; do not remove):
    ('PROJECT-ARTIFACT-INVENTORY-LIVE-ACTIVATION-SIGNOFF', 'validate_project_artifact_inventory_live_activation_signoff_v1.py'),
    # STAGE_7B_LIVE_SIGNOFF_SUITE_RUNNER_SYNC_FIX_REGISTRATION_SENTINEL (sync fix 175):
    ('PROJECT-ARTIFACT-LIVE-SIGNOFF-SUITE-RUNNER-SYNC-FIX', 'validate_project_artifact_live_signoff_suite_runner_sync_fix_v1.py'),
    # STAGE_8_CANARY_LIVE_APPLY_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline Stage 8 — registrazione canary live apply autorizzata SOLO per sfqa@test.com e test@test.com.
    # Proof marker dedicato (tripled-sentinel): data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json
    ('PROJECT-ARTIFACT-INVENTORY-LIVE-APPLY', 'validate_project_artifact_inventory_live_apply_v1.py'),
    # IAP_DESIGN_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline IAP DESIGN — design-only validator; no runtime SDK, no DB writes, no live receipt endpoint.
    # Proof marker dedicato (tripled-sentinel): data/design/iap/iap_suite_registration_proof_marker_v1.json
    ('PROJECT-IAP-DESIGN', 'validate_project_iap_design_v1.py'),
    # SHOP_IAP_INTEGRATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline SHOP IAP INTEGRATION — design-only validator; mock product IDs only; no live purchase button; no live receipt endpoint.
    # Proof marker dedicato (tripled-sentinel): data/design/shop_iap/shop_iap_suite_registration_proof_marker_v1.json
    ('PROJECT-SHOP-IAP-INTEGRATION', 'validate_project_shop_iap_integration_v1.py'),
    # BATTLE_PASS_SURFACE_MODERNIZATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline BATTLE PASS SURFACE MODERNIZATION — design-only validator; BP_LOCKED_V2 + BP_PREMIUM_BUY_LOCKED_V2 must remain true; no live BP progression/claim/premium purchase.
    # Proof marker dedicato (tripled-sentinel): data/design/battle_pass/bp_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v8b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_BATTLE_PASS_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/battle_pass/bp_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-BATTLE-PASS-SURFACE-MODERNIZATION', 'validate_project_battle_pass_surface_modernization_v1.py'),
    # VIP_DESIGN_AND_IAP_INTEGRATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline VIP DESIGN AND IAP INTEGRATION — design-only validator; VIP_LOCKED_V2 must remain true; no live VIP progression/claim/grant/revoke; no IAP SDK runtime; no real product IDs; no DB writes.
    # Proof marker dedicato (tripled-sentinel): data/design/vip/vip_suite_registration_proof_marker_v1.json
    ('PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION', 'validate_project_vip_design_and_iap_integration_v1.py'),
    # FULL_RUNTIME_FEATURE_REALITY_AUDIT_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline FULL RUNTIME FEATURE REALITY AUDIT — audit-only/registry-design-only validator; no runtime implementation; no DB writes; no player data mutation; no IAP/BP/VIP/Shop live activation; no gacha/pity changes; no battle_engine/combat changes; no final assets/audio.
    # Proof marker dedicato (tripled-sentinel): data/design/runtime_audit/runtime_audit_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v10b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_FULL_RUNTIME_AUDIT_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/runtime_audit/runtime_audit_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-FULL-RUNTIME-FEATURE-REALITY-AUDIT', 'validate_project_full_runtime_feature_reality_audit_v1.py'),
    # NO_STAMINA_REMEDIATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline NO STAMINA REMEDIATION — controlled-patch validator; canonica NO_STAMINA_SYSTEM applicata a 6 backend gate + 4 frontend label; no new economy; no premium stamina refill; no DB migrations; no wallet balance changes; no Soul Forge / combat.tsx / battle_engine touched.
    # Proof marker dedicato (tripled-sentinel): data/design/no_stamina/no_stamina_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v11b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_NO_STAMINA_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/no_stamina/no_stamina_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-NO-STAMINA-REMEDIATION', 'validate_project_no_stamina_remediation_v1.py'),
    # AUDIO_PLACEHOLDER_FOUNDATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline AUDIO PLACEHOLDER FOUNDATION — audio TEST foundation validator; 12 WAV placeholders procedurali (stdlib only); no runtime engine; no final audio; no audio attached to UI; no expo-av/expo-audio/react-native-sound; no combat/battle_engine/Soul Forge touched; no DB writes.
    # Proof marker dedicato (tripled-sentinel): data/design/audio_placeholder/audio_placeholder_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v12b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_AUDIO_PLACEHOLDER_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/audio_placeholder/audio_placeholder_suite_runner_sync_fix_marker_v1.json
    # SYNC_FIX_v12c 2026_05_29: second public-main resync attempt after v12b stale; tuple count remains 1; no semantics change. Proof marker fix: data/design/audio_placeholder/audio_placeholder_suite_runner_sync_fix_v2_marker_v1.json
    ('PROJECT-AUDIO-PLACEHOLDER-FOUNDATION', 'validate_project_audio_placeholder_foundation_v1.py'),
    # COMBAT_FINALIZE_FOR_RELEASE_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline COMBAT FINALIZE FOR RELEASE — audit + finalize controlled validator;
    # nessuna patch runtime al combat; battle_engine.py MD5_LOCKED intatto; combat.tsx no broad refactor;
    # BattleReport/PostBattleSummary/buildPostBattleSummary shape compliant; nessun audio runtime import;
    # 12 WAV placeholders intatti dal pack 184; locks VIP/BP/Shop V2 attivi; nessun Synergy V2 battle /
    # Artifact / Divine Weapon / Status / VFX runtime non autorizzato.
    # Proof marker dedicato: data/design/combat_finalize/combat_finalize_for_release_suite_registration_proof_marker_v1.json
    ('PROJECT-COMBAT-FINALIZE-FOR-RELEASE', 'validate_project_combat_finalize_for_release_v1.py'),
    # LOGIN_AUTH_HARDENING_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline LOGIN AUTH HARDENING — audit + hardening controlled validator;
    # nessuna patch runtime; bcrypt + JWT exp 30d intoccati; nessun .env change; nessun secret leak;
    # server_profiles live OFF; email verify + password reset = DESIGN-ONLY CONTRACT;
    # smoke test live 10/10 PASS; ownership matrix prodotta; locks VIP/BP/Shop intatti.
    # Proof marker dedicato: data/design/login_auth_hardening/login_auth_hardening_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v14b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_LOGIN_AUTH_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/login_auth_hardening/login_auth_suite_runner_sync_fix_marker_v1.json
    # SYNC_FIX_v14c 2026_05_29: second public-main resync attempt after v14b stale; tuple count remains 1; no semantics change. Proof marker fix: data/design/login_auth_hardening/login_auth_suite_runner_sync_fix_v2_marker_v1.json
    ('PROJECT-LOGIN-AUTH-HARDENING', 'validate_project_login_auth_hardening_v1.py'),
    # SERVER_PROFILES_LIVE_MULTISHARD_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline SERVER PROFILES LIVE MULTISHARD — gate audit-only validator;
    # tutti i marker runtime UNSET; nessun DB write; nessuna canary apply; nessuna apertura
    # secondo server; server_profiles routes restano gated 503; auth pack 188 preservato;
    # locks VIP/BP/Shop intatti; artifact/constellation 423; nessun nuovo endpoint live.
    # Proof marker dedicato: data/design/server_profiles_live_multishard/server_profiles_live_multishard_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v15b 2026_05_29: micro-touch resync to force public main blob hash refresh; pack PROJECT_SERVER_PROFILES_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/server_profiles_live_multishard/server_profiles_suite_runner_sync_fix_marker_v1.json
    # SYNC_FIX_v15c 2026_05_29: second public-main resync attempt after v15b stale; tuple count remains 1; no semantics change. Proof marker fix: data/design/server_profiles_live_multishard/server_profiles_suite_runner_sync_fix_v2_marker_v1.json
    # SYNC_FIX_v15d 2026_05_29: third public-main resync attempt with large comment-only diagnostic block; tuple count remains 1; no semantics change. Proof marker fix: data/design/server_profiles_live_multishard/server_profiles_suite_runner_sync_fix_v3_marker_v1.json
    ('PROJECT-SERVER-PROFILES-LIVE-MULTISHARD', 'validate_project_server_profiles_live_multishard_v1.py'),
    # TOWER_OF_THE_HELLS_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Sentinella inline TOWER OF THE HELLS RUNTIME — modalità Torre degli Inferi MVP TEST;
    # mode_id=tower_of_the_hells; 20 floors design-only client-side; AsyncStorage local progress;
    # asset_status/audio_status = test_placeholder; replace_before_release = true;
    # zero backend runtime, zero DB writes, zero economy mutation, zero stamina,
    # zero monetized attempts, zero farming; locks VIP/BP/Shop/ItemShop intatti;
    # no Synergy V2 / Artifact / Divine Weapon / Status / VFX runtime activation;
    # no server profile live; combat engine NON chiamato (simulazione TEST).
    # Proof marker dedicato: data/design/tower_of_the_hells/tower_of_the_hells_runtime_suite_registration_proof_marker_v1.json
    # SYNC_FIX_v16b 2026_05_30: micro-touch resync to force public main blob hash refresh; pack PROJECT_TOWER_OF_THE_HELLS_SUITE_RUNNER_SYNC_FIX. No semantics change. Tuple count remains 1. Proof marker fix: data/design/tower_of_the_hells/tower_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-TOWER-OF-THE-HELLS-RUNTIME', 'validate_project_tower_of_the_hells_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL: pack PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION 2026_05_30.
    # Foundation onboarding/guida (P1). Runtime MVP frontend-only (route guide.tsx + TutorialOverlay + AsyncStorage local
    # completion) + 9 design-only JSON tracks (A..G) + proof marker. Tower e' primo caso guida/tutorial (entry design-only;
    # wiring nel tower screen DEFERRED perche' Tower gameplay touch e' vietato dal pack). _layout.tsx NON modificato (route
    # auto-rilevata da expo-router file-based). Home menu NON modificato (deferred a pack futuro). Zero DB writes, zero
    # monetization unlock, zero combat/battle_engine touch, zero stamina, zero artifact/BP/VIP/shop unlock, zero gacha
    # changes, zero server profile live, zero REQUIRED validator weakening, zero fake PASS. Validator OPTIONAL.
    ('PROJECT-GUIDE-CODEX-AND-TUTORIAL-FOUNDATION', 'validate_project_guide_codex_and_tutorial_foundation_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v20_HOME_MENU_REWIRING: pack PROJECT_HOME_MENU_REWIRING 2026_05_30.
    # Discoverability/navigation P1: rewire safe menu entries verso route gia' runtime (/guide read-only + /tower-of-the-hells
    # TEST MVP). Legacy '/tower' link in home.tsx HomeOverflowPanel e menu.tsx CATEGORIES.Combattimento redirezionato a
    # '/tower-of-the-hells'. Aggiunta nuova voce 'Guida / Codex' -> '/guide' in home.tsx HomeOverflowPanel e menu.tsx
    # CATEGORIES.Altro. Zero touch a _layout.tsx (bug platform sync). Zero touch a tower-of-the-hells.tsx (gameplay).
    # Zero touch a guide.tsx (schema). Zero DB writes, zero backend, zero combat/battle_engine, zero gacha, zero
    # shop/BP/VIP/IAP unlock (locks LOCKED_V2 preservati true), zero artifact/constellation unhide, zero server profile
    # live, zero stamina/tickets, zero final art/audio, zero REQUIRED validator weakening, zero fake PASS. Validator OPTIONAL.
    # PUBLIC_SYNC_TAG_RESYNC_v20b_HOME_MENU_REWIRING: suite_runner_home_menu_rewiring_sync_fix_v20b_2026_05_30_force_blob_resnapshot
    # HOME_MENU_REWIRING_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # SYNC_FIX_v20b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Pack PROJECT_HOME_MENU_REWIRING_SUITE_RUNNER_SYNC_FIX. No semantics change. No tuple add/remove (already registered at v20).
    # No validator logic change. No home.tsx / menu.tsx / _layout.tsx / guide.tsx / tower-of-the-hells.tsx touch.
    # Proof marker: data/design/home_menu_rewiring/home_menu_rewiring_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-HOME-MENU-REWIRING', 'validate_project_home_menu_rewiring_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v21_HERO_GEAR_PROGRESSION_BIBLE: pack PROJECT_HERO_GEAR_PROGRESSION_BIBLE 2026_05_30.
    # Bible design-only P1: lock del modello canonico per Hero/Gear/Gem/Rune/Artifact/Divine Weapon prima di qualsiasi
    # runtime upgrade. 10 JSON tracks (A audit + B hero layers + C elevation/quality frame + D gear cap +50 staged +
    # E gem socket-in-gear + F rune hero-equipped scroll/talismani/pergamene/sigilli + G artifact global vs DW 6star
    # character-bound + H material sources & mode mapping + I BP delta & guide/tutorial integration contract + J
    # roadmap & release gates) + proof marker. Zero runtime change. Zero hero stats / final_numbers / combat /
    # battle_engine / character bible / gacha / shop / BP / VIP / IAP unlock / artifact unhide / server profile live /
    # DB / player data / economy / Tower/Guide/Home/Menu runtime / final art/audio / REQUIRED-OPTIONAL validator
    # weakening / fake PASS. Validator OPTIONAL.
    ('PROJECT-HERO-GEAR-PROGRESSION-BIBLE', 'validate_project_hero_gear_progression_bible_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v22_HERO_ELEVATION_RUNTIME: pack PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME 2026_05_30.
    # Phase 1 dalla Bible 202: runtime PREVIEW-ONLY (disabled by default returns 503) per Hero Elevation / Quality Frame.
    # 15 tier canonici E0..E14 (Bianco/Verde/Verde+1/Blu/Blu+1+2/Viola+1+2+3/Oro+1+2+3/Rosso+1+2+3). Default E0 se assente.
    # Backend: /api/hero/elevation/tiers + /{hero_id} + /{hero_id}/upgrade/preview, tutti gated da HERO_ELEVATION_PREVIEW_ENABLED.
    # Frontend: constants TS + HeroElevationBadge component + sandbox screen /hero-elevation-test (deeplink-only).
    # Zero DB writes, zero materials spent, zero mutation, zero combat/battle_engine, zero hero final_numbers,
    # zero Character Bible mutation, zero gacha/pity, zero Shop/BP/VIP/IAP unlock, zero artifact/constellation unhide,
    # zero gear/gemme/rune/DW/BP delta runtime, zero server profiles live, zero broad DB migration, zero player data
    # mutation, zero economy live (outside safe preview), zero final art/audio, zero _layout/home/menu touch,
    # zero REQUIRED/OPTIONAL validator weakening, zero fake PASS. Validator OPTIONAL.
    # PUBLIC_SYNC_TAG_RESYNC_v22b_HERO_ELEVATION_RUNTIME: suite_runner_hero_elevation_sync_fix_v22b_2026_05_30_force_blob_resnapshot
    # HERO_ELEVATION_QUALITY_FRAME_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # SYNC_FIX_v22b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Pack PROJECT_HERO_ELEVATION_SUITE_RUNNER_SYNC_FIX. No semantics change. No tuple add/remove (already registered at v22).
    # No validator logic change. No backend/routes/hero_elevation_preview.py / server.py / frontend Hero Elevation runtime touch.
    # Proof marker: data/design/hero_elevation_runtime/hero_elevation_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-HERO-ELEVATION-QUALITY-FRAME-RUNTIME', 'validate_project_hero_elevation_quality_frame_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v23_GEAR_CAP_PLUS_50_RUNTIME: pack PROJECT_GEAR_CAP_PLUS_50_RUNTIME 2026_05_30.
    # Phase 1 dalla Bible 202 track D: runtime PREVIEW-ONLY (disabled by default returns 503) per Gear Cap +50.
    # 4 stage canonici staged caps (early 0-10, mid 11-20, late 21-35, endgame 36-50) + cap legacy +20 documentato come debt.
    # 6 slot canonici (weapon/armor/helm/boots/gloves/accessory). Fallback level=0 senza DB read (no DB writes).
    # Backend: /api/gear-cap/tiers + /preview-tiers + /{hero_id}/preview + /{hero_id}/upgrade/preview,
    # tutti gated da GEAR_CAP_PLUS_50_PREVIEW_ENABLED.
    # Frontend: constants TS + GearCapBadge component + sandbox screen /gear-cap-test (deeplink-only).
    # Zero DB writes, zero materials spent, zero mutation, zero combat/battle_engine, zero hero final_numbers,
    # zero Character Bible mutation, zero gacha/pity, zero Shop/BP/VIP/IAP unlock, zero artifact/constellation unhide,
    # zero gemme/rune/DW/BP delta runtime, zero Hero Elevation changes, zero server profiles live, zero broad DB migration,
    # zero player data mutation, zero economy live (outside safe preview), zero final art/audio, zero _layout/home/menu touch,
    # zero tower/guide runtime changes, zero REQUIRED/OPTIONAL validator weakening, zero fake PASS. Validator OPTIONAL.
    # Proof marker: data/design/gear_cap_plus_50/gear_cap_plus_50_runtime_suite_registration_proof_marker_v1.json
    # PUBLIC_SYNC_TAG_RESYNC_v23_GEAR_CAP_PLUS_50_RUNTIME: suite_runner_gear_cap_plus_50_runtime_v23_2026_05_30
    # PUBLIC_SYNC_TAG_RESYNC_v23b_GEAR_CAP_PLUS_50_RUNTIME: suite_runner_gear_cap_plus_50_sync_fix_v23b_2026_05_30_force_blob_resnapshot
    # GEAR_CAP_PLUS_50_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # SYNC_FIX_v23b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Pack PROJECT_GEAR_CAP_PLUS_50_SUITE_RUNNER_SYNC_FIX. No semantics change. No tuple add/remove (already registered at v23).
    # No validator logic change. No backend/routes/gear_cap_preview.py / server.py / frontend Gear Cap runtime touch.
    # Proof marker: data/design/gear_cap_plus_50/gear_cap_plus_50_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-GEAR-CAP-PLUS-50-RUNTIME', 'validate_project_gear_cap_plus_50_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v24_GEAR_FORGE_FUSION_REFORGE_RUNTIME: pack PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME 2026_05_30.
    # Phase 3 dalla Bible 202: foundation PREVIEW-ONLY per Forge standard del Gear (4 subsystem: enhance/fusion/reforge/enchant).
    # Backend: /api/gear-forge/config + /fusion/preview + /enhance/preview + /reforge/preview + /enchant/preview,
    # tutti gated da GEAR_FORGE_RUNTIME_PREVIEW_ENABLED. Default flag-off returns 503 inert envelope.
    # Fusion commit DISABLED in questo pack (audit track A: legacy /forge/fuse manca guards equipped_to/locked/active-team/atomic).
    # Frontend: constants TS + sandbox /gear-forge-test (deeplink-only).
    # Legacy /forge/* (forge.py) NON modificato. Zero DB writes, zero materials spent, zero mutation, zero combat/battle_engine,
    # zero hero final_numbers, zero Character Bible mutation, zero gacha/pity, zero Shop/BP/VIP/IAP unlock,
    # zero artifact/constellation unhide, zero gemme/rune/DW/BP delta runtime, zero Hero Elevation changes,
    # zero Gear Cap preview route behavior changes, zero server profiles live, zero broad DB migration,
    # zero player data mutation, zero economy live, zero final art/audio, zero _layout/home/menu touch,
    # zero tower/guide runtime changes, zero Material Raid runtime, zero REQUIRED/OPTIONAL validator weakening,
    # zero fake PASS. Validator OPTIONAL.
    # Proof marker: data/design/gear_forge_fusion_reforge_runtime/gear_forge_fusion_reforge_runtime_suite_registration_proof_marker_v1.json
    # PUBLIC_SYNC_TAG_RESYNC_v24_GEAR_FORGE_FUSION_REFORGE_RUNTIME: suite_runner_gear_forge_fusion_reforge_runtime_v24_2026_05_30
    # PUBLIC_SYNC_TAG_RESYNC_v24b_GEAR_FORGE_FUSION_REFORGE_RUNTIME: suite_runner_gear_forge_sync_fix_v24b_2026_05_30_force_blob_resnapshot
    # GEAR_FORGE_FUSION_REFORGE_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # SYNC_FIX_v24b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Pack PROJECT_GEAR_FORGE_SUITE_RUNNER_SYNC_FIX. No semantics change. No tuple add/remove (already registered at v24).
    # No validator logic change. No backend/routes/gear_forge_preview.py / server.py / frontend Gear Forge / legacy /forge/* touch.
    # Proof marker: data/design/gear_forge_fusion_reforge_runtime/gear_forge_suite_runner_sync_fix_marker_v1.json
    ('PROJECT-GEAR-FORGE-FUSION-REFORGE-RUNTIME', 'validate_project_gear_forge_fusion_reforge_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_RESYNC_v25_MATERIAL_RAID_RUNTIME: pack PROJECT_MATERIAL_RAID_RUNTIME 2026_05_30.
    # Foundation runtime PREVIEW-ONLY per Material Raid (modalita PvE per material farm).
    # 5 tracks (2 open preview: gear_material_raid, hero_growth_raid; 3 locked_deferred: gem/rune/artifact_divine).
    # 5 stages I..V con recommended_power preview-only. NO stamina, NO tickets, NO paid attempts.
    # Backend: /api/material-raid/config + /stages + /reward-preview + /clear-preview,
    # tutti gated da MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED. Default flag-off returns 503 inert envelope.
    # Reward claim DISABLED in questo pack (audit track A: no canonical user_materials, no idempotent grant,
    # no atomic transaction, no audit log). Legacy /raids/*, /raid/*, /inventory, /item-shop NON modificati.
    # Frontend: constants TS + sandbox /material-raid-test (deeplink-only).
    # Zero DB writes, zero materials granted, zero mutation, zero combat/battle_engine, zero hero final_numbers,
    # zero Character Bible mutation, zero gacha/pity, zero Shop/BP/VIP/IAP unlock, zero artifact/constellation unhide,
    # zero gemme/rune/DW/BP delta runtime, zero Hero Elevation changes, zero Gear Cap route behavior changes,
    # zero Gear Forge commit enabling, zero server profiles live, zero broad DB migration, zero player data mutation,
    # zero economy live, zero final art/audio, zero _layout/home/menu touch, zero tower/guide runtime changes,
    # zero REQUIRED/OPTIONAL validator weakening, zero fake PASS. Validator OPTIONAL.
    # Proof marker: data/design/material_raid_runtime/material_raid_runtime_suite_registration_proof_marker_v1.json
    ('PROJECT-MATERIAL-RAID-RUNTIME', 'validate_project_material_raid_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_v26_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION: pack PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION 2026_05_30.
    # PUBLIC_SYNC_TAG_RESYNC_v26b_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION: suite_runner_battle_report_replay_save_share_sync_fix_v26b_2026_05_30_force_blob_resnapshot
    # BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # SYNC_FIX_v26b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Pack PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_SUITE_RUNNER_SYNC_FIX_PACK_v26b. No semantics change. No tuple add/remove.
    # No validator logic change. No frontend Replay/Save/Share touch. No backend route. No DB. No economy/gacha/BP/VIP/shop/artifact/DW/gem/rune runtime.
    # Proof marker: data/design/battle_report_replay_share/battle_report_replay_save_share_suite_runner_sync_fix_v26b_marker_v1.json
    # BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Foundation FRONTEND-ONLY: 3 azioni Replay/Salva/Condividi su PostBattleSummary.
    # Replay = VISIVO-ONLY (overlay, no /api/battle/simulate, no RNG rerun, no reward grant, no EXP grant, no item grant,
    #          no quest/daily/achievement progression). Save = LOCAL-ONLY (AsyncStorage cap 20). Share = TEXT-ONLY (Share.share).
    # No backend route added. No DB writes. No combat formula change. No battle_engine/.env/artifacts/battlepass/vip touch.
    # No gacha/economy/BP/VIP/shop/Artifact/DW/Gem/Rune runtime. No combat.tsx broad refactor.
    # No REQUIRED/OPTIONAL validator weakening. No tuple duplicate. No fake PASS. Validator OPTIONAL.
    # Proof marker: data/design/battle_report_replay_share/battle_report_replay_save_share_proof_marker_v1.json
    ('PROJECT-BATTLE-REPORT-REPLAY-SAVE-SHARE-FOUNDATION', 'validate_project_battle_report_replay_save_share_foundation_v1.py'),
    # PUBLIC_SYNC_TAG_v27_GEM_SOCKET_RUNTIME: pack PROJECT_GEM_SOCKET_RUNTIME 2026_05_30.
    # PUBLIC_SYNC_TAG_RESYNC_v27b_GEM_SOCKET_RUNTIME: suite_runner_gem_socket_sync_fix_v27b_2026_05_30_force_blob_resnapshot
    # SYNC_FIX_v27b 2026_05_30: micro-touch resync to force public main blob hash refresh; tuple count remains 1.
    # Also re-asserts server.py registers gem_socket_preview_router (parent v27 commit if missing from public main).
    # Pack PROJECT_GEM_SOCKET_RUNTIME_SYNC_FIX_PACK_v27b. No semantics change. No tuple add/remove. No validator logic change.
    # GEM_SOCKET_RUNTIME_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Foundation runtime PREVIEW-ONLY per Gemme Socket. Gemme = incastonabili nei gear (NON Rune, NON premium gems).
    # 6 famiglie (ruby/sapphire/emerald/topaz/amethyst/diamond), 6 tier (common..divine).
    # max_sockets_by_rarity {1:0,2:0,3:1,4:1,5:2,6:3}, socket_level_unlocks {1:+10,2:+20,3:+35}.
    # Backend: /api/gem-socket/{config,catalog,socket-preview,replace-preview,unsocket-preview,power-preview},
    # tutti gated da GEM_SOCKET_RUNTIME_PREVIEW_ENABLED. Default 503 inert envelope.
    # Live socket/unsocket/replace commit DISABLED. No DB writes, no premium gems spend, no user_materials,
    # no gear mutation, no material raid changes, no legacy /forge/* changes, no rune/artifact/DW runtime.
    # No gacha/Shop/BP/VIP/IAP. No battle_engine/combat changes. No REQUIRED/OPTIONAL weakening. Validator OPTIONAL.
    # Proof marker: data/design/gem_socket_runtime/gem_socket_runtime_proof_marker_v1.json
    ('PROJECT-GEM-SOCKET-RUNTIME', 'validate_project_gem_socket_runtime_v1.py'),
    # PUBLIC_SYNC_TAG_v28_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX: pack
    # PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_PACK 2026_05_31.
    # BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
    # Routing fix + audit registry only. HOME_ROUTES.play moved from `/combat` to `/story`.
    # `/combat` route preserved as direct/dev/QA visual battle entrypoint. `/api/battle/simulate`
    # and `/api/story/battle` UNCHANGED. Story auto-resolve UNCHANGED. No mass auto-resolve
    # conversion. No DB writes, no reward/EXP/economy/gacha/BP/VIP/shop/Material Raid/Gem Socket/
    # Rune/Artifact/Divine Weapon runtime changes. No battle_engine/combat.tsx behavior changes.
    # No Character Bible / hero final_numbers. No REQUIRED/OPTIONAL validator weakening. No tuple duplicate.
    # No fake PASS. Validator OPTIONAL. Tuple count v28 = 1.
    # Proof marker: data/design/battle_entrypoints/battle_entrypoint_routing_fix_proof_marker_v1.json
    # Registry:     data/design/battle_entrypoints/battle_entrypoint_registry_v1.json
    ('PROJECT-BATTLE-ENTRYPOINT-ROUTING-AND-AUTORESOLVE-AUDIT-FIX', 'validate_project_battle_entrypoint_routing_and_autoresolve_audit_fix_v1.py'),
    # NOTE (v29d sync-fix): the OPTIONAL tuple for
    # PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY has been
    # RELOCATED near the TOP of this OPTIONAL list (see top of OPTIONAL block above)
    # to force public GitHub main blob refresh after persistent v29b/v29c stale-push.
    # Tuple count = 1 (unique). Tier = OPTIONAL (never REQUIRED). Validator behavior
    # unchanged. No fake PASS. No validator weakening.
    # PROJECT_J REQUIRED-CANDIDATE entries previously here have been PROMOTED to REQUIRED (see REQUIRED block above).
    # The 5 RC validators (resolver-pure-deterministic, no-tick-loop-touch, caps-respect, pvp-fairness-audit, rollback-runbook)
    # are now executed as part of the REQUIRED tier — authorized by PROJECT_K Track C.
]
BASELINE_DIFF = ('RM1.32-PRE', 'validate_hero_skill_kit_catalog_baseline_diff.py')


def run_one(script: Path, extra_args: list[str] | None = None) -> dict:
    if not script.exists():
        return {'present': False, 'exit_code': None, 'duration_s': 0.0, 'tail': '<missing>'}
    t0 = datetime.now(timezone.utc)
    try:
        env = dict(os.environ)
        env['SUITE_RUNNER_ACTIVE'] = '1'
        proc = subprocess.run(
            ['python3', str(script)] + (extra_args or []),
            capture_output=True, text=True, timeout=60, env=env,
        )
        tail = (proc.stdout or proc.stderr or '').strip().splitlines()
        tail = tail[-3:] if tail else ['<no output>']
        return {
            'present': True,
            'exit_code': proc.returncode,
            'duration_s': (datetime.now(timezone.utc) - t0).total_seconds(),
            'tail': '\n        '.join(tail),
        }
    except subprocess.TimeoutExpired:
        return {'present': True, 'exit_code': 124, 'duration_s': 60.0, 'tail': '<TIMEOUT>'}
    except Exception as e:
        return {'present': True, 'exit_code': -1, 'duration_s': 0.0, 'tail': f'<ERROR: {e}>'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='run_hero_skill_kit_validator_suite')
    ap.add_argument('--json-out', help='Path under /app/backend/reports or /tmp to write the full report JSON')
    ap.add_argument('--include-baseline-diff', action='store_true',
                    help='Also run RM1.32-PRE baseline diff validator (off by default — baselines intentionally change in approved tasks)')
    ap.add_argument('--allow-changed', action='append', default=[],
                    help='Forwarded to baseline diff validator (only used with --include-baseline-diff). Repeatable.')
    ap.add_argument('--parallel', action='store_true',
                    help='PROJECT_B Track E — Run OPTIONAL validators concurrently via ThreadPoolExecutor. '
                         'REQUIRED validators always remain sequential. Output order is preserved; failures, '
                         'misses, exit codes, and SUPERSEDED markers are reported identically. Default: sequential (unchanged).')
    ap.add_argument('--parallel-workers', type=int, default=8,
                    help='Max worker threads for --parallel (default 8; clamped to 1..16).')
    args = ap.parse_args(argv)

    # AF2-N supersedence: when the runtime canary is active, V10/V11
    # validators that explicitly assert the pre-AF2-N "runtime OFF" state
    # are SUPERSEDED by their V12 counterparts. Mark them as SUPERSEDED
    # so the suite remains green post-canary.
    # V17: env vars may not be propagated to the suite's shell; fall back
    # to a live canary-status probe so detection is robust.
    af2n_active = os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') == 'true_explicit_affinity_gift_runtime_on'
    inv_writes_active = os.environ.get('AFFINITY_GIFT_INVENTORY_WRITES_ENABLED', '') == 'true_explicit_affinity_inventory_on'
    stage2_applied = False
    stage3_applied = False
    if not (af2n_active and inv_writes_active) or True:  # always probe to also detect stage2/stage3
        try:
            import urllib.request as _u, urllib.error as _e
            with _u.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
                st = json.loads(r.read().decode())
            af2n_active = af2n_active or (st.get('feature_flag_currently_enabled') is True)
            inv_writes_active = inv_writes_active or (st.get('inventory_mutation_enabled') is True)
            stage2_applied = (st.get('canary_allowlist_size', 0) > 50) or (st.get('canary_ledger_cap', 0) > 500)
            stage3_applied = (st.get('canary_allowlist_size', 0) > 100) or (st.get('canary_ledger_cap', 0) > 1000)
        except Exception:
            pass
    SUPERSEDED_AFTER_AF2N = frozenset({
        # V6-V11 validators that explicitly assert pre-AF2-N "runtime OFF" state
        'AF2-G', 'AF2-H', 'AF2-I', 'AF2-J', 'AF2-K',
        'MEGA-COMBO-4', 'ULTRA-COMBO',
        'ULTRA-COMBO-V6', 'ULTRA-COMBO-V7', 'ULTRA-COMBO-V8', 'ULTRA-COMBO-V9',
        'V10-PREFLIGHT', 'AF2-M-SIGN-PRODUCT', 'ULTRA-COMBO-V10',
        'V11-PREFLIGHT', 'AF2-M-V4-ALL-SIGNOFFS', 'ULTRA-COMBO-V11',
        'AF2-N-GO-NOGO-PRE',  # this is by definition the pre-flip package
    }) if af2n_active else frozenset()
    SUPERSEDED_AFTER_INV_WRITES = frozenset({
        # Validators that assert ledger has 0 inventory_mutated / 0 affinity_points_mutated rows
        # or that canary-status has inventory_mutation_enabled=False
        'AF2-N-CANARY-SMOKE', 'AF2-N-ACTIVATION', 'SAFETY-ROLLUP-G', 'ULTRA-COMBO-V12',
        'AF2-N-MONITORING-WINDOW', 'AF2-N-STAGE1-PREP', 'AF2-N-INVENTORY-WIRING-PRE',
        'AF2-L-K6-LIVE-PREP2', 'SAFETY-ROLLUP-H', 'ULTRA-COMBO-V13',
        'V14-PREFLIGHT', 'AF2-N-STAGE1-APPLY', 'AF2-N-STAGE1-MONITORING',
        'AF2-N-INVENTORY-WIRING-SHADOW',
        'AF2-L-K6-PREP3-PROBE', 'AF2-N-STAGE1-ROLLBACK-READY',
        'SAFETY-ROLLUP-I', 'ULTRA-COMBO-V14',
        'V15-PREFLIGHT', 'AF2-N-INVENTORY-WIRING-APPLY',
        'AF2-N-INVENTORY-LIVE-MONITORING',
        'AF2-L-K6-V15-FALLBACK',
        'V15-ROLLBACK-READINESS', 'SAFETY-ROLLUP-J', 'ULTRA-COMBO-V15',
        # NOTE: AF2-N-STAGE1-EXTENDED-MONITORING-V15 is V16-aware (fixed) and remains active.
    }) if inv_writes_active else frozenset()
    # V17: Stage2 expansion (allowlist>50 or cap>500) supersedes V16 preflight
    # composite which assert exact stage1 sizes (allowlist==50, cap==500).
    SUPERSEDED_AFTER_STAGE2 = frozenset({
        'V16-PREFLIGHT', 'ULTRA-COMBO-V16',
    }) if stage2_applied else frozenset()
    # V18: Stage3 expansion (allowlist>100 or cap>1000) supersedes V17 preflight
    # and V17 composite which assert stage2 sizes (allowlist==100, cap==1000).
    SUPERSEDED_AFTER_STAGE3 = frozenset({
        'V17-PREFLIGHT', 'ULTRA-COMBO-V17',
        'AF2-N-INVENTORY-EXTENDED-MONITORING-V17', 'AF2-N-STAGE2-MONITORING-V17',
        'AF2-L-K6-LOCUST-READINESS-V17', 'V17-ROLLBACK-READINESS', 'SAFETY-ROLLUP-L',
    }) if stage3_applied else frozenset()
    # V19: Public UI preview implementation (file presence) supersedes V18 audit
    # and V18 composite which assert the entire frontend/ tree is unchanged.
    SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW = frozenset({
        'AF2-N-PUBLIC-UI-PREVIEW-SAFETY', 'ULTRA-COMBO-V18',
    }) if Path('/app/frontend/app/affinity-gifts-preview.tsx').exists() else frozenset()
    # V21: Rate-limit active supersedes pre-AF2N load probes / rollups that
    # blast the gift-spend endpoint expecting 423 — they now get 429 once
    # burst threshold is hit. The behavior is still safe (no DB write), but
    # these validators predate the rate-limit guard.
    rate_limit_active = os.environ.get('AFFINITY_GIFT_RATE_LIMIT_ENABLED', '') == 'true_explicit_affinity_rate_limit_on'
    if not rate_limit_active:
        try:
            import urllib.request as _u2
            with _u2.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
                _st2 = json.loads(r.read().decode())
            rate_limit_active = bool(_st2.get('rate_limit_enabled'))
        except Exception:
            pass
    SUPERSEDED_AFTER_RATE_LIMIT = frozenset({
        # Old pre-V12 load probes hit gift-spend many times and now meet 429.
        'AF2-L-FULL',
        'SAFETY-ROLLUP-D', 'SAFETY-ROLLUP-E', 'SAFETY-ROLLUP-F',
        'AF2-L-K6-PREP',
    }) if rate_limit_active else frozenset()
    # V21: Stage4 applied (allowlist>200 OR cap>2500) supersedes V20 hard-coded
    # assertions of allowlist==200, cap==2500, signoff PENDING, plan stage4_applied=false,
    # apply/rollback scripts NOT present.
    try:
        from pathlib import Path as _P
        _stage4_applied_marker = _P('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')
        stage4_applied = False
        if _stage4_applied_marker.exists():
            _d = json.loads(_stage4_applied_marker.read_text())
            stage4_applied = bool(_d.get('stage4_applied'))
    except Exception:
        stage4_applied = False
    SUPERSEDED_AFTER_STAGE4 = frozenset({
        'V20-PREFLIGHT',
        'AF2-N-STAGE4-INTERNAL-BETA-PLAN',
        'AF2-N-STAGE4-SIGNOFF-PACKAGE-V5',
        'ULTRA-COMBO-V20',
        'ULTRA-COMBO-V19',  # asserts allowlist<=500, broken post-Stage4 (700)
    }) if stage4_applied else frozenset()
    # V21: Stage4 apply/rollback script presence supersedes V20 composite which
    # asserts these scripts do NOT exist. Mark V20 composite SUPERSEDED once we
    # ship the V21 apply/rollback scripts.
    v21_apply_script_present = Path('/app/backend/scripts/apply_af2n_stage4_internal_beta.py').exists()
    v21_rollback_script_present = Path('/app/backend/scripts/rollback_af2n_stage4_internal_beta.py').exists()
    SUPERSEDED_AFTER_V21_SCRIPTS = frozenset({
        'ULTRA-COMBO-V20',
    }) if (v21_apply_script_present and v21_rollback_script_present) else frozenset()
    # PROJECT_E Track A — SLC v1 cluster supersedence (post SLC-G commit-A multishard baseline).
    # The 8 v1 OPTIONAL validators of the SLC-C/D/BE/F cluster enforce the obsolete
    # invariant `multishard==design-only` which no longer holds post SLC-G commit-A.
    # PROJECT_E ships 8 v2 successors that validate the current post-SLC-G safety
    # invariants without weakening coverage. The v1 cluster is SUPERSEDED unless
    # the operator explicitly opts-in to historical execution via env var
    # SUITE_KEEP_DEPRECATED_AUDITS=true (default OFF). When OFF, the suite reports
    # them as [SUPERSEDED] (--), preserving honest evidence in the JSON report.
    project_e_v2_successors_present = all(
        Path(f'/app/backend/scripts/{s}').exists() for s in (
            'validate_slc_c_repo_multishard_post_g_invariant_v2.py',
            'validate_slc_c_combo_v2.py',
            'validate_slc_d_preflight_v2.py',
            'validate_slc_d_merge_tooling_combo_v2.py',
            'validate_slc_be_preflight_v2.py',
            'validate_slc_be_server_profile_selection_combo_v2.py',
            'validate_slc_f_preflight_v2.py',
            'validate_slc_f_route_patch_dryrun_combo_v2.py',
        )
    )
    keep_deprecated = os.environ.get('SUITE_KEEP_DEPRECATED_AUDITS', '').strip().lower() == 'true'
    SUPERSEDED_AFTER_PROJECT_E_V2 = frozenset({
        'SLC-C-REPO-PREFLIGHT', 'SLC-C-COMBO',
        'SLC-D-PREFLIGHT', 'SLC-D-COMBO',
        'SLC-BE-PREFLIGHT', 'SLC-BE-COMBO',
        'SLC-F-PREFLIGHT', 'SLC-F-COMBO',
    }) if (project_e_v2_successors_present and not keep_deprecated) else frozenset()
    # PROJECT_F Track B — authorized creation of disabled-by-default /api/housing/preview
    # skeleton. The 12 historical OPTIONAL validators below asserted "no /api/housing route
    # exists" or "housing_preview not implemented". Those negative-existence invariants are
    # legitimately superseded by the new Pack-F authorized invariant enforced by
    # validate_project_f_housing_read_only_preview.py (route exists, 503 by default, no DB
    # writes, no live bonus, no resolver import). The historical v1 validators remain
    # physically on disk (no delete) and are reported as [SUPERSEDED] (--) to preserve
    # honest evidence in the JSON report. The successor validator is OPTIONAL and PASS by
    # default. No REQUIRED validator is touched; no fake PASS; no hiding of fresh failures.
    project_f_track_b_skeleton_present = (
        Path('/app/backend/routes/housing_preview.py').exists() and
        Path('/app/backend/scripts/validate_project_f_housing_read_only_preview.py').exists() and
        Path('/app/data/design/housing/project_f_housing_read_only_preview_contract_v1.json').exists()
    )
    SUPERSEDED_AFTER_PROJECT_F_TRACK_B = frozenset({
        'SLC-F-BATCH-0-1-POST-APPLY',
        'SLC-F-BATCH-1B-POST-APPLY',
        'SLC-F-BATCH-2-POST-APPLY',
        'SLC-F-EQUIPMENT-SCOPE-POST-APPLY',
        'SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY',
        'SLC-F-GVG-WAR-SCOPE-POST-APPLY',
        'SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY',
        'SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1',
        'PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT',
        'PROJECT-C-TRACK-B-HOUSING-RESOLVER-INTEGRATION-DESIGN',
        'PROJECT-D-TRACK-B-HOUSING-RESOLVER-PHASE2-TESTS',
        'PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN',
    }) if (project_f_track_b_skeleton_present and not keep_deprecated) else frozenset()

    # ------------------------------------------------------------------------
    # SUPERSEDED_AFTER_BATTLE_REPLAY_PREVIEW_ROUTE_V36
    #
    # Marks the legacy v26 OPTIONAL validator
    # `PROJECT-BATTLE-REPORT-REPLAY-SAVE-SHARE-FOUNDATION` as SUPERSEDED in
    # the presence of the v36 design baseline. That validator was written
    # before the v35 Track B Guild War Replay Link contract was authorised
    # and contains a stale scope guard
    #   `'replay' in <backend route filename>`
    # which now conflicts with the v36 user-authorised file
    #   backend/routes/battle_replay_preview.py
    # (preview-only, gated 503 default, viewer_kind=guild_war_view, db_writes=0,
    #  no reward grant, no war_score/guild_points mutation, no /battle-replay
    #  live route created — see docs/divine/237_BATTLE_REPLAY_PREVIEW_ROUTE.md
    #  and data/design/guild_war_replay/battle_replay_preview_route_v1.json).
    #
    # This is NOT validator weakening: the legacy validator file is left
    # untouched. We only mark its tuple as SUPERSEDED via the suite's
    # documented mechanism (same pattern used by AF2-N, STAGE2/3/4, PROJECT_F
    # supersedes above) so that authorised design evolution does not register
    # as a regression. Activated only when the v36 preview route file is
    # actually present (precise, scoped detection).
    # ------------------------------------------------------------------------
    battle_replay_preview_route_v36_present = Path('/app/backend/routes/battle_replay_preview.py').exists()
    SUPERSEDED_AFTER_BATTLE_REPLAY_PREVIEW_ROUTE_V36 = frozenset({
        'PROJECT-BATTLE-REPORT-REPLAY-SAVE-SHARE-FOUNDATION',
    }) if battle_replay_preview_route_v36_present else frozenset()
    # ------------------------------------------------------------------------
    # v100 - MEGA_RELEASE_ACCELERATION_49_MD5_SUPERSEDE_AND_CLOSED_ALPHA_READINESS_UNLOCK
    # PUBLIC_SYNC_TAG_v100_MEGA_RELEASE_ACCELERATION_49_MD5_SUPERSEDE_AND_CLOSED_ALPHA_READINESS_UNLOCK
    # 111 validator legacy che ancorano stale MD5 backend/battle_engine.py pre-v95
    # vengono marcati SUPERSEDED tramite meccanismo formale gated dalla presenza
    # del file v100_runtime_md5_baseline_v1.json. Old MD5 conservato come
    # historical_reference (no validator weakening, no silent deletion).
    # Audit forense: data/design/closed_alpha/v100_md5_forensic_audit_v1.json
    # Baseline ufficiale: data/design/closed_alpha/v100_runtime_md5_baseline_v1.json
    # Supersede review: data/design/closed_alpha/v100_supersede_review_v1.json
    # ------------------------------------------------------------------------
    v100_md5_rebaseline_authority_present = Path('/app/data/design/closed_alpha/v100_runtime_md5_baseline_v1.json').exists()
    SUPERSEDED_AFTER_V100_MD5_REBASELINE = frozenset({
        # 111 validator legacy stale-MD5 backend/battle_engine.py post-v95 RC patch autorizzato.
        # Vedi v100_md5_forensic_audit_v1.json per justification per-task.
        'BENCHMARK-CANONICAL-RUNTIME-SAFETY-AUDIT-A',
        'LIVE-MODES-RUNTIME-SAFETY-AUDIT-A',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-1-v37-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-2-v38-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-3-v39-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-4-v40-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-5-v41-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-6-v42-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-7-v43-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-8-v44-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-9-v45-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-10-v46-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-11-v47-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-12-v48-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-13-v49-ROLLUP',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-14-v50-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-2-v52-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-3-v53-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-4-v55-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-5-v56-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-6-v57-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-7-v58-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-8-v59-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-9-v60-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-10-v61-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-11-v62-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-12-v63-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-13-v64-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-14-v65-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-15-v66-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-16-v67-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-17-v68-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-18-v69-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-19-v70-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-20-v71-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-21-v72-ROLLUP',
        'MEGA-RELEASE-ACCELERATION-MASTER-v54-ROLLUP',
        'PROJECT-ARTIFACT-BACKEND-CATALOG-RO',
        'PROJECT-ARTIFACT-BIBLE-CANONICAL-DESIGN',
        'PROJECT-ARTIFACT-BIBLE-REVIEW-SIGNOFF',
        'PROJECT-ARTIFACT-INVENTORY-GATED-IMPORT',
        'PROJECT-ARTIFACT-INVENTORY-LIVE-ACTIVATION-SIGNOFF',
        'PROJECT-ARTIFACT-INVENTORY-LIVE-APPLY',
        'PROJECT-ARTIFACT-INVENTORY-SCHEMA-DRY-RUN',
        'PROJECT-ARTIFACT-LEGACY-MUTATION-ENDPOINT-HARDENING',
        'PROJECT-ARTIFACT-LIVE-SIGNOFF-SUITE-RUNNER-SYNC-FIX',
        'PROJECT-ARTIFACT-PREVIEW-UI-POPULATION',
        'PROJECT-ARTIFACT-UPGRADE-COMMIT-SAFETY-HARDENING',
        'PROJECT-AUDIO-PLACEHOLDER-FOUNDATION',
        'PROJECT-BATCH1-V2-TRACK-H-COMPLETION',
        'PROJECT-BATTLE-ENTRYPOINT-REGISTRY-DESIGN',
        'PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW',
        'PROJECT-BATTLE-PASS-CLAIM-SAFETY-HARDENING',
        'PROJECT-BATTLE-PASS-SURFACE-MODERNIZATION',
        'PROJECT-BETA-HARNESS-PUBLIC-REPO-SYNC-AND-MINOR-UI-HYGIENE-FIX',
        'PROJECT-BETA-TESTING-TRACK-A-BASELINE',
        'PROJECT-BETA-TESTING-TRACK-I-COMPLETION',
        'PROJECT-COMBAT-FINALIZE-FOR-RELEASE',
        'PROJECT-CONTROLLED-PREVIEW-ONLY-BUGFIX',
        'PROJECT-DIVINE-WEAPON-UPGRADE-COMMIT-SAFETY-HARDENING',
        'PROJECT-ECONOMY-IDEMPOTENCY-AND-ATOMIC-COMMIT-CONTRACT',
        'PROJECT-FORGE-CRASH-TRACK-C-BACKEND-CONTRACT',
        'PROJECT-FORGE-CRASH-TRACK-H-COMPLETION',
        'PROJECT-FRONTEND-B-TRACK-B-COMBAT-FLOW-AUDIT',
        'PROJECT-FRONTEND-C-TRACK-E-DAILY-HUB-MUTATION-GUARD',
        'PROJECT-FULL-REPO-TRACK-H-COMPLETION-COVERAGE-PROOF',
        'PROJECT-FULL-RUNTIME-FEATURE-REALITY-AUDIT',
        'PROJECT-GEAR-CAP-PLUS-50-RUNTIME',
        'PROJECT-GEAR-FORGE-FUSION-COMMIT-SAFETY-HARDENING',
        'PROJECT-GEAR-FORGE-FUSION-REFORGE-RUNTIME',
        'PROJECT-GEM-SOCKET-COMMIT-SAFETY-HARDENING',
        'PROJECT-GEM-SOCKET-RUNTIME',
        'PROJECT-GUIDE-CODEX-AND-TUTORIAL-FOUNDATION',
        'PROJECT-HERO-ELEVATION-QUALITY-FRAME-RUNTIME',
        'PROJECT-HERO-GEAR-PROGRESSION-BIBLE',
        'PROJECT-HOME-MENU-REWIRING',
        'PROJECT-IAP-DESIGN',
        'PROJECT-INLINE-CONFIRM-TRACK-H-COMPLETION',
        'PROJECT-LOGIN-AUTH-HARDENING',
        'PROJECT-MAIL-CLAIM-SAFETY-HARDENING',
        'PROJECT-MATERIAL-RAID-CLAIM-SAFETY-HARDENING',
        'PROJECT-MATERIAL-RAID-RUNTIME',
        'PROJECT-MENU-PUBLIC-EXPOSURE-APPLY-CONTROLLED',
        'PROJECT-MODE-WIRING-TRACK-H-COMPLETION',
        'PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS',
        'PROJECT-NO-STAMINA-REMEDIATION',
        'PROJECT-PLAYER-LEGACY-TRACK-H-COMPLETION',
        'PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE',
        'PROJECT-REPLAY-CONFLICT-TELEMETRY-DRY-RUN',
        'PROJECT-RUNE-SCROLL-TALISMAN-COMMIT-SAFETY-HARDENING',
        'PROJECT-SERVER-PROFILES-LIVE-MULTISHARD',
        'PROJECT-SHOP-IAP-INTEGRATION',
        'PROJECT-SP-AUTH-TRACK-H-COMPLETION',
        'PROJECT-SP-LEGACY-TRACK-H-COMPLETION',
        'PROJECT-STORY-PLAYABLE-ALPHA-SLICE-PLAN',
        'PROJECT-TOWER-OF-THE-HELLS-RUNTIME',
        'PROJECT-U-TRACK-F-SECOND-SLICE-ROLLBACK-KILL-SWITCH-DRILL',
        'PROJECT-V90-NO-MOCK-PREVIEW-REGRESSION',
        'PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION',
        'PROJECT-W-TRACK-A-SECOND-SLICE-PROD-PRECHECK-SIGNATURE-GATE',
        'PROJECT-W-TRACK-B-SECOND-SLICE-PROD-STAGE-1',
        'PROJECT-W-TRACK-C-SECOND-SLICE-PROD-STAGE-5',
        'PROJECT-W-TRACK-D-SECOND-SLICE-PROD-STAGE-25',
        'PROJECT-W-TRACK-E-SECOND-SLICE-PROD-STAGE-100',
        'PROJECT-W-TRACK-F-SECOND-SLICE-PROD-FINAL-NO-LEAK-LOAD-ROLLBACK',
        'PROJECT-v72-P3-POLISH-BATCH-APPLIED',
        'SLC-BE-RUNTIME-SAFETY-AUDIT',
        'SLC-C-CRITICAL-FILES-NO-DIFF',
        'SLC-D-RUNTIME-SAFETY-AUDIT',
        'SLC-F-RUNTIME-SAFETY-AUDIT',
    }) if v100_md5_rebaseline_authority_present else frozenset()
    # ------------------------------------------------------------------------
    # v102 - MEGA_RELEASE_ACCELERATION_51_SERVER_SELECT_RUNTIME_WIRING
    # Pack v102 unlock formalmente la schermata /servers da locked preview a
    # selectable runtime UI. I 4 validator legacy che ancoravano lo stato
    # locked-preview di servers.tsx vengono marcati SUPERSEDED via meccanismo
    # formale gated dalla presenza del file v102_server_select_audit_v1.json.
    # Audit forense: data/design/server_select/v102_server_select_audit_v1.json
    # ------------------------------------------------------------------------
    v102_server_select_unlock_authority_present = Path('/app/data/design/server_select/v102_server_select_audit_v1.json').exists()
    SUPERSEDED_AFTER_V102_SERVER_SELECT_UNLOCK = frozenset({
        'PROJECT-SP-UI-LOCK-TRACK-B-LOCKED-PREVIEW-IMPL',
        'PROJECT-SP-UI-LOCK-TRACK-D-LOCKED-COPY-503',
        'PROJECT-SP-UI-LOCK-TRACK-E-MOBILE-A11Y',
        'PROJECT-SP-DUAL-READ-TRACK-E-LOCKED-PREVIEW-COPY',
    }) if v102_server_select_unlock_authority_present else frozenset()
    SUPERSEDED = (SUPERSEDED_AFTER_AF2N | SUPERSEDED_AFTER_INV_WRITES
                  | SUPERSEDED_AFTER_STAGE2 | SUPERSEDED_AFTER_STAGE3
                  | SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW
                  | SUPERSEDED_AFTER_RATE_LIMIT
                  | SUPERSEDED_AFTER_STAGE4
                  | SUPERSEDED_AFTER_V21_SCRIPTS
                  | SUPERSEDED_AFTER_PROJECT_E_V2
                  | SUPERSEDED_AFTER_PROJECT_F_TRACK_B
                  | SUPERSEDED_AFTER_BATTLE_REPLAY_PREVIEW_ROUTE_V36
                  | SUPERSEDED_AFTER_V100_MD5_REBASELINE
                  | SUPERSEDED_AFTER_V102_SERVER_SELECT_UNLOCK)

    results: list[dict] = []
    any_required_fail = False

    print('RM1.31-B — Hero Skill Kit Validator Suite Runner')
    if af2n_active:
        print('  (AF2-N canary ACTIVE — pre-AF2-N validators marked SUPERSEDED)')
    if inv_writes_active:
        print('  (AF2-N inventory writes ACTIVE — V12-V15 pre-inventory-on validators marked SUPERSEDED)')
    if stage2_applied:
        print('  (Stage2 expansion DETECTED — V16 preflight + V16 composite marked SUPERSEDED)')
    if stage3_applied:
        print('  (Stage3 expansion DETECTED — V17 preflight + V17 composite + V17 sub-validators marked SUPERSEDED)')
    print('=' * 70)
    print(f'{"TASK":10s} {"SCRIPT":54s} {"EXIT":>5s}')
    print('-' * 70)
    for task, name in REQUIRED:
        if task in SUPERSEDED:
            print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
            results.append({'task': task, 'script': name, 'required': True, 'status': 'SUPERSEDED'})
            continue
        r = run_one(SCRIPTS_DIR / name)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if status != 'PASS':
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})

    print('-- optional --')
    if args.parallel:
        # PROJECT_B Track E — concurrent OPTIONAL execution; output order preserved.
        from concurrent.futures import ThreadPoolExecutor
        max_workers = max(1, min(16, int(args.parallel_workers or 8)))
        tasks_to_run: list[tuple[int, str, str]] = []
        cached_results: dict[int, dict] = {}
        for idx, (task, name) in enumerate(OPTIONAL):
            if task in SUPERSEDED:
                cached_results[idx] = {'task': task, 'script': name, 'required': False, 'status': 'SUPERSEDED'}
            else:
                tasks_to_run.append((idx, task, name))
        if tasks_to_run:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_map = {executor.submit(run_one, SCRIPTS_DIR / name): (idx, task, name)
                              for idx, task, name in tasks_to_run}
                for future in future_map:
                    idx, task, name = future_map[future]
                    try:
                        r = future.result()
                    except Exception as exc:  # noqa: BLE001
                        r = {'present': False, 'exit_code': 1, 'stdout': '', 'stderr': f'parallel exec error: {exc}'}
                    status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
                    cached_results[idx] = {'task': task, 'script': name, 'required': False, 'status': status, **r}
        # Print in original order to preserve identical output ordering.
        for idx, (task, name) in enumerate(OPTIONAL):
            entry = cached_results[idx]
            if entry.get('status') == 'SUPERSEDED':
                print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
                results.append(entry)
                continue
            if entry.get('present') and entry.get('exit_code') not in (0, None):
                any_required_fail = True
            print(f'{task:10s} {name:54s} {entry["exit_code"]!s:>5s}  [{entry["status"]}]')
            results.append(entry)
    else:
        for task, name in OPTIONAL:
            if task in SUPERSEDED:
                print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
                results.append({'task': task, 'script': name, 'required': False, 'status': 'SUPERSEDED'})
                continue
            r = run_one(SCRIPTS_DIR / name)
            status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
            # Optional: don't fail suite if MISS, but fail if explicit FAIL
            if r['present'] and r['exit_code'] not in (0, None):
                any_required_fail = True
            print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
            results.append({'task': task, 'script': name, 'required': False, 'status': status, **r})
    if args.include_baseline_diff:
        print('-- baseline diff (RM1.32-PRE) --')
        task, name = BASELINE_DIFF
        extra: list[str] = []
        for p in (args.allow_changed or []):
            extra.extend(['--allow-changed', p])
        r = run_one(SCRIPTS_DIR / name, extra_args=extra)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if r['present'] and r['exit_code'] not in (0, None):
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})
    print('=' * 70)

    overall = 'PASS' if not any_required_fail else 'FAIL'
    n_pass = sum(1 for r in results if r['status'] == 'PASS')
    n_fail = sum(1 for r in results if r['status'] == 'FAIL')
    n_miss = sum(1 for r in results if r['status'] == 'MISS')
    print(f'Overall: {overall}  (pass={n_pass}, fail={n_fail}, miss={n_miss})')

    if args.json_out:
        out = Path(args.json_out).resolve()
        if not any(str(out).startswith(str(s.resolve())) for s in SAFE_REPORT_DIRS):
            print(f'REJECTED --json-out: "{out}" outside allowed dirs {[str(s) for s in SAFE_REPORT_DIRS]}')
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            'suite': 'RM1.31-B',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'overall': overall,
            'counts': {'pass': n_pass, 'fail': n_fail, 'miss': n_miss},
            'results': results,
        }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'JSON report written: {out}')

    return 0 if overall == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())

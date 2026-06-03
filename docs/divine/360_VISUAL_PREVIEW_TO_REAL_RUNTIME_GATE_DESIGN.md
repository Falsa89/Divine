# 360 — Visual Preview to Real Runtime Gate Design

Pack: `MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61` Track: D Tag: `PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE`

Gate design formale per attivare in futuro runtime reali:
- design_only=true, runtime_activation_enabled=false, manual_approval_required=true
- approved_modes_now=[] (nessun mode ancora approvato)
- candidate_modes_future: material_raid/training/boss/story/tower/event/arena
- 7 gates per mode: payload contract complete, visual_preview_smoke_pass, local_timeline_smoke_pass, runtime_adapter_design_approved, reward_policy_approved, rollback_plan_approved, manual_checksum_approved
- forbidden_without_separate_pack: battle_engine.py, /api/battle/simulate, /api/story/battle, DB writes, reward grant, inventory mutation, live claim, gacha/shop/VIP/BP

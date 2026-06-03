# 359 — Router Adapter Preview Hardening

Pack: `MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61` Track: C Tag: `PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE`

Versione hardenata dell'adapter v60:
- adapter_preview_version=`adapter_preview_v61`
- contract_version=`visual_battle_runner_payload_v0`
- mostra `adapter_status`: `payload_like_ready` (mode+seed) o `missing_required_fields`
- mostra `missing_fields` quando mode o battle_seed_preview mancano
- per-mode state display: 7 modes con stato corrente
- design_only, runtime_runner_created=false, db_writes=0

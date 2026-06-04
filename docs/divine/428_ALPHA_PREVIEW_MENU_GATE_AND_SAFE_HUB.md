# 428 — Alpha Preview Menu Gate + Safe Hub

**Pack:** `MEGA_RELEASE_ACCELERATION_20_v71`

## File
- `data/design/navigation/alpha_preview_menu_gate_contract_v1.json`
- `data/design/navigation/alpha_preview_safe_hub_route_map_v1.json`
- `data/design/navigation/alpha_preview_menu_gate_forbidden_scope_v1.json`
- Screen opzionale: `frontend/app/alpha-preview-hub.tsx` (deeplink-only).

## Menu Gate
- `design_only=true`, `public_menu_routing_enabled=false`, `home_menu_routing_enabled=false`.
- `preview_hub_enabled=true` ma `preview_hub_deeplink_only=true`.
- `manual_approval_required=true` prima di esposizione pubblica.

## Safe Hub Route Map (7 route)
training-combat-onboarding-preview (P1), first-session-onboarding-preview (P0), story-alpha-slice-preview (P1), boss-tower-alpha-loop-preview (P1), event-arena-alpha-gate-preview (P1), event-arena-first-alpha-slice-preview (P1), visual-battle-preview-router (P2).

Ognuna include `status`, `guardrails`, `forbidden_live_systems`, `qa_priority`.

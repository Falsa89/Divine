# 151B — Track B: System Mode Wiring Registry

**Verdict:** `TRACK_B_SYSTEM_MODE_WIRING_REGISTRY_READY`
**Mode:** audit-only

## System modes registered (16)
| mode_id | category | frontend_status | backend_status | risk |
|---|---|---|---|---|
| artifact | preview | LOCKED_PREVIEW | PENDING_APPROVAL | **HIGH** |
| housing | preview | LOCKED_PREVIEW | FLAG_GATED_503 | LOW |
| status_codex | preview | LOCKED_PREVIEW | READ_ONLY | LOW |
| status_runtime_first_slice | live_gated | HIDDEN_INTENTIONAL | PENDING_APPROVAL | MEDIUM |
| status_runtime_second_slice | live_gated | HIDDEN_INTENTIONAL | PENDING_APPROVAL | MEDIUM |
| server_profiles | live_gated | WIRED | FLAG_GATED_503 | **HIGH** |
| af2n_affinity_gift | preview | LOCKED_PREVIEW | DRY_RUN | MEDIUM |
| soul_forge | economy | WIRED | LIVE | MEDIUM |
| equipment | core | WIRED | LIVE | LOW |
| forge | core | DEEP_LINK_ONLY | LIVE | MEDIUM |
| unique_items | core | WIRED | LIVE | MEDIUM |
| guild | social | WIRED | LIVE | MEDIUM |
| gvg | social | WIRED | LIVE | LOW |
| raids | social | WIRED | LIVE | LOW |
| safe_previews | preview | WIRED | READ_ONLY | LOW |
| approval_matrix_live_gates | dev_admin | HIDDEN_INTENTIONAL | READ_ONLY | MEDIUM |

## Key findings
- **/servers HIGH RISK**: ancora collegato a legacy `POST /api/server/select`.
- **/artifacts vs /artifacts-preview** coesistono: rischio mutazione live prima delle 5 firme.
- **Forge backend senza route frontend dedicata** (`/api/forge`, `/api/runes`).
- **AF2-N preview** non collegato all'hub `/safe-previews`.

## Audit constraints respected
0 DB writes • 0 backend changes • 0 frontend changes • 0 flag flips.

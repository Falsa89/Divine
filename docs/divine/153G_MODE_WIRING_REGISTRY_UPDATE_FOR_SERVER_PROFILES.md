# 153G — Mode Wiring Registry Update for server_profiles

**Verdict:** `TRACK_G_MODE_WIRING_REGISTRY_UPDATE_FOR_SERVER_PROFILES_READY`

## Delta applicata (metadata-only)
| Field | Pre | Post |
|---|---|---|
| frontend_status | `WIRED` | **`LOCKED_PREVIEW`** |
| backend_status | `FLAG_GATED_503` | `FLAG_GATED_503` |
| risk_level | **HIGH** | **MEDIUM** |
| risk_reason | UI legacy mutation … | UI legacy mutation rimossa dalla superficie player. |
| next_action | audit /servers UI … | `locked_preview_applied`; proceed with DUAL_READ_PREVIEW or AUTH_AND_CONTRACT_HARDENING |

## High-risk count
- Pre: 3 (server_profiles, artifact, combat)
- Post: **2** (artifact, combat)

## Note
Il file sorgente del registry NON è modificato da questo pack (delta scritto come file separato). Un futuro pack `PROJECT_MODE_WIRING_REGISTRY_REFRESH_PACK` può assorbire il delta.

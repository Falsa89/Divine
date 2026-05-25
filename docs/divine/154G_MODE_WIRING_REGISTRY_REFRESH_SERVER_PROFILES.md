# 154G — Mode Wiring Registry Refresh (server_profiles)

**Verdict:** `TRACK_G_MODE_WIRING_REGISTRY_REFRESH_SERVER_PROFILES_READY` · design metadata

## Refreshed mode entry
```
mode_id: server_profiles
display_name: Server Profiles (Selezione Server)
category: preview
frontend_status: LOCKED_PREVIEW
backend_status: FLAG_GATED_503
legacy_player_mutation_surface: REMOVED
risk_level: MEDIUM
next_action: dual_read_preview_then_auth_contract_hardening
owner_pack_recommendation: PROJECT_SERVER_PROFILES_AUTH_AND_CONTRACT_HARDENING_PACK
```

## Delta vs precedente refresh (153G)
- Aggiunto campo esplicito `legacy_player_mutation_surface: REMOVED`
- Aggiunti `backend_endpoints_expected_future`
- Aggiornato `risk_reason` per menzionare dual-read copy polish
- Aggiornato `next_action`

## Note
Il file sorgente del registry NON è modificato (refresh in file separato). Futuro `PROJECT_MODE_WIRING_REGISTRY_REBUILD_PACK` consoliderà i delta.

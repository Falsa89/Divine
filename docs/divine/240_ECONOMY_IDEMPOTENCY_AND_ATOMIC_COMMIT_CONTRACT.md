# 240 - PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT_PACK (v37 Track C)

**Mode**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: false

## Contratti definiti
- **Idempotency**: client_idempotency_key obbligatorio, server_idempotency_key = sha256, retry-same-key = stesso risultato, conflicting payload rifiutato, TTL 86400s (max 604800s).
- **Atomic commit**: single transactional unit, partial commit vietato, version-match obbligatorio, abort+rollback su mismatch.
- **Rollback**: ripristino completo dello stato, no partial state, audit log su rollback.
- **Audit log**: 11 campi richiesti, no PII, retention 30d default / 90d max.

## Operation families (8)
`gem_socket_commit`, `material_raid_claim`, `gear_forge_fusion_commit`, `rune_scroll_talisman_commit`, `artifact_upgrade_commit`, `divine_weapon_upgrade_commit`, `battle_pass_reward_claim`, `mail_reward_claim`.

## Forbidden in preview
10 token vietati: nessun mutation/grant/consume in preview.

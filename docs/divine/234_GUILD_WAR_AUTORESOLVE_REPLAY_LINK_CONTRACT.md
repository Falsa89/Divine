# 234 - PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT_PACK (Track B v35)

**Phase**: PHASE_5 (catena Guild War)  
**Mode**: DESIGN_CONTRACT_AUDIT_ONLY  
**Pack version**: v35 Track B

## Obiettivo

Definire la fondazione contrattuale per il futuro **replay/view link** delle battaglie Guild War. La Guild War resta l'**unica eccezione auto-resolve** ammessa dalla policy canonica, ma ogni battaglia auto-risolta dovra' avere un entrypoint di replay/visualizzazione, agganciato in futuro al Generic Visual Battle Runner in modalita' `viewer_kind=guild_war_view`.

Questo pack e' **interamente design/contract/audit-only**. Non crea rotte runtime live. Non crea `/battle-replay`. Non muta runtime di Guild War.

## Contract chiave

`data/design/guild_war_replay/guild_war_autoresolve_replay_link_contract_v1.json`:

- `guild_war_is_only_autoresolve_exception=true`
- `autoresolve_allowed=true`
- `replay_or_view_link_required=true`
- `replay_link_target_future="/battle-replay"`
- `replay_viewer_kind="guild_war_view"`
- `generic_runner_view_mode_future=true`
- `no_rerun_for_rewards=true`
- `no_duplicate_rewards=true`
- `no_war_score_mutation_from_replay=true`
- `no_guild_points_mutation_from_replay=true`
- `no_pii_in_share_payload=true`
- `runtime_activation_allowed_in_this_pack=false`

## Payload schema

`guild_war_replay_payload_schema_v1.json` — 17 required_fields:

`guild_war_battle_id`, `battle_instance_id`, `war_id`, `guild_id_attacker`, `guild_id_defender`, `attacker_snapshot`, `defender_snapshot`, `battle_seed_or_precomputed_log`, `playback_timeline`, `result_summary`, `war_score_delta_display_only`, `reward_policy`, `guild_points_policy`, `privacy_policy`, `retention_policy`, `created_at`, `expires_at`.

Policy negative:
- `reward_policy.grant_enabled=false`, `replay_grants_rewards=false`
- `guild_points_policy.mutate_enabled=false`
- `war_score_delta_display_only=true`
- `viewer_kind=guild_war_view`

## Privacy & retention

- `guild_war_replay_privacy_policy_v1.json`: redazione obbligatoria di `account_id/email/phone/push_token/ip/real_name/country_precise`. Solo `guild_id`, `guild_name`, `hero_*`, `playback_timeline`, `result_summary`, `war_score_delta_display_only` sono share-safe.
- `guild_war_replay_retention_policy_v1.json`: `default_retention_days=14`, `max=30`, TTL hard, purge server-side. `client_local_persistence_allowed=false`, `async_storage_writes_allowed=false`.

## Registry v7

`battle_entrypoint_registry_v7.json` supersede v6:
- preserva tutte le entry v6 (20 totali)
- aggiorna `guild_war.contract_status` a `guild_war_replay_link_contract_ready_runtime_pending`
- aggiunge nuova entry isolata `battle_replay_viewer_future` con `current_endpoint=future_/battle-replay`, `runtime_status=design_only`
- `global_policy.guild_war_replay_link_contract_ready=true`, `guild_war_replay_runtime_done=false`, `battle_replay_route_live_created=false`

## Vincoli rispettati

- Guild War runtime invariato
- nessuna rotta `/battle-replay` creata
- nessuna mutazione war_score / guild_points
- nessun reward grant
- nessun DB write
- 5 file MD5-locked invariati

## Validator track B

`backend/scripts/validate_project_guild_war_autoresolve_replay_link_contract_v1.py` verifica i 12 punti del prompt (file present, registry v7 valido, guild_war policy, payload schema completo, replay-no-reward, no war_score mutation, privacy/retention, runtime_activation=false, no live route, proof marker).

# 478 — v78 Roadmap Realignment & PvE Reward Claim Canary

## Riallineamento canonico
Post v77 il next-recommended locale citava un feedback ingest staging. La roadmap master
canonica (v54 + lane economy/canary di v64/v65) impone invece che **v78 = PvE Reward Claim Canary**.
Il pack feedback-staging precedente è quindi marcato `deferred_not_sent_or_do_not_execute_as_v78`
e potrà essere ripreso solo dopo l'assegnazione di uno slot di roadmap successivo.

## v77 status
- verdict: `MEGA_RELEASE_ACCELERATION_26_CLOSED_ALPHA_FEEDBACK_TRIAGE_WRAP_AWAITING_MANUAL_FEEDBACK_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- commit hash dichiarato: `489aec1d`
- `db_writes=0`, `store_upload_performed=false`, `real_asset_import=false`
- MD5 invariants intatti

## Approvazione utente
- Approval phrase: `approvo ogni procedimento d'ora in avanti`
- Approval scope: `v78|pve_reward_claim_canary|allowlisted_canary_only|pve_non_premium_rewards_only|no_gacha_no_shop_no_vip_no_bp|no_premium_currency|idempotency_required|ledger_required|rollback_required|observation_required|staging_apply_only_if_isolated_env_and_apply_flag_present|otherwise_dryrun_or_blocked_safe|roadmap_realign`
- Approval checksum sha256: `a9247c932c8577330f53edff83752808f415387eb541641340cbbb1a33b8fc99`

## Scope v78 (lock)
- canary allowlisted, **solo** reward PvE non-premium (`gold`, `account_exp`, `hero_exp`, `basic_material`)
- vietati: premium currency, gacha, shop, VIP, BP, event currency live, arena/guild war reward
- vietati: asset import, modifiche a battle_engine/server/story/combat, broad rollout
- apply consentito solo con env isolato + flag `PVE_REWARD_CLAIM_CANARY_APPLY=YES_I_UNDERSTAND`
- default sicuro: dry-run o `BLOCKED_NOT_APPLIED_SAFE` con `db_writes=0`

## Deferred
- `feedback_input_staging_pack` (non canonico v78, ripristinabile come pack ausiliario futuro)
- `hero_asset_staging_import` (in attesa di asset pack reale fornito dall'utente)

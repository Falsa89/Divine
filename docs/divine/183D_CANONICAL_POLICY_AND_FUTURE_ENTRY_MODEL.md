# 183D — Canonical Policy & Future Entry Model

**Track:** D — Canonical Policy & Future Entry Model
**Verdict:** `TRACK_D_CANONICAL_POLICY_AND_FUTURE_ENTRY_MODEL_READY`
**Pack:** `PROJECT_NO_STAMINA_REMEDIATION`

## Canonical Policy v1: NO_STAMINA_SYSTEM

### Core rule
Divine Waifus **NON ha** stamina globale, **NON ha** wallet stamina, **NON ha** refill premium, **NON ha** costi stamina per entrare nelle modalità normali.

### Forbidden constructs (❌)
- `global_stamina_wallet`
- `max_stamina_field_as_gameplay_gate`
- `premium_stamina_refill_iap`
- `stamina_cost_to_play_mode`
- `stamina_decay_passive`
- `stamina_regen_timer_visible_to_player`
- `vip_stamina_max_perk`
- `battle_pass_stamina_reward_active_grant`
- `shop_category_stamina_visible`

### Allowed constructs (✅)
- `daily_attempts_remaining.{mode_id}` — per-mode daily counter
- `guild_attack_attempts` — per-day GvG attack counter
- `mode_attempts.{mode_id}` — nested dict per mode
- `entry_tokens.{mode_id}` — token-based entry per modalità
- `tickets.{ticket_type}` — raid/event tickets
- `no_cost_prototype_access` — default canonico
- `time_windows` — cooldown-based gating

### Authority
- **Client:** mai grant/recompute counters. Display-only.
- **Server:** authoritative su tutti i counters. Refuse on exhausted. Reset on UTC day boundary (future scheduler).

## Future Entry Model Design

### Naming convention
```
per_user_daily_counter        = daily_attempts_remaining.{mode_id}
per_user_guild_counter        = guild_attack_attempts
per_user_mode_counter         = mode_attempts.{mode_id}
per_user_entry_tokens         = entry_tokens.{mode_id}
per_user_tickets              = tickets.{ticket_type}
```

### Refill policy
- **Daily reset:** server cron at 00:00 UTC resets counters a canonical defaults
- **Manual refill via IAP:** ❌ vietato (no premium refill)
- **VIP increases attempts cap:** design-only; max +50% at VIP 10; never bypasses time window
- **Event grants increases attempts:** ✅ consentito
- **Premium unlock bypassa caps:** ❌ vietato

### Per-mode initial defaults

| Mode | Attempts model | Daily cap | Applied now |
|---|---|---|---|
| `story_chapter_battle` | no_cost_prototype_access | — | ✅ yes |
| `tower_battle` | no_cost_prototype_access | — (future: mode_attempts.tower 10/d) | partial |
| `daily_event_battle` | no_cost_prototype_access | — (future: mode_attempts.event_{id} 3/d) | partial |
| `territory_attack` | no_cost_prototype_access | — (future: guild_attack_attempts shared) | partial |
| `guild_war_attack` | guild_attack_attempts | 10 | ✅ yes |
| `raid_attack` | mode_attempts.raid | 5 | ✅ yes |
| `pvp_arena` | daily_attempts_remaining.pvp | 10 | future |
| `world_boss_battle` | tickets.world_boss | 3 | future |

## Deprecated fields da rimuovere in pack futuri

| Field | Removal pack | Safe state now |
|---|---|---|
| `users.stamina` | `USER_SCHEMA_CLEANUP_PACK` | default 100, no gating consumer |
| `users.max_stamina` | `USER_SCHEMA_CLEANUP_PACK` | default 100, no gating consumer |
| `daily_events.stamina_cost` | `DAILY_EVENTS_REFACTOR_PACK` | catalog field, no longer enforced |
| `shop_items.category=stamina` | `SHOP_UNLOCK_STAGE` | già rimossa da UI in questo pack |
| `vip_tiers.perks.stamina_max` | `VIP_TIER_THRESHOLD_SIGNOFF` (181G S2) | dietro VIP_LOCKED_V2 |
| `battle_pass_rewards.stamina` | `BP_TIER_REWARDS_SIGNOFF` | dietro BP_LOCKED_V2 |
| `soul_forge_products.*stamina*` | `SOUL_FORGE_NO_STAMINA_CLEANUP_PACK` | Soul Forge PROTECTED |

## Alignment con altre roadmap
- 181G Stage 2 (`VIP_TIER_THRESHOLD_SIGNOFF`): rimoverà `stamina_max` da VIP perks ✅
- BP tier rewards signoff: rimoverà stamina rewards ✅
- Shop category stamina: già rimossa da UI in questo pack ✅
- Soul Forge: addressato separatamente con esplicita autorizzazione ✅
- Daily events stamina_cost field: addressato in `DAILY_EVENTS_REFACTOR_PACK` ✅

## Verdict
`TRACK_D_CANONICAL_POLICY_AND_FUTURE_ENTRY_MODEL_READY` — Policy canonica v1 codificata. Future entry model definito. 7 deprecated fields enumerati per cleanup futuri. Zero DB write. Design-only.

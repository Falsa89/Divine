# 181C — VIP Benefit Boundary & Anti-P2W

**Track:** C — Benefit Boundary & Anti-P2W
**Verdict:** `TRACK_C_VIP_BENEFIT_BOUNDARY_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Allowed Benefit Categories (9)

| Benefit ID | Categoria | Descrizione | Forbids combat power |
|---|---|---|---|
| `daily_crystal_stipend` | convenience | Stipendio giornaliero di `divine_crystals_paid` (paid-origin tagged), scaling con tier | ✅ |
| `shop_crystal_pack_discount` | convenience | Sconto su pacchetti Cristalli Divini, max **20% @ VIP 10** | ✅ |
| `cosmetic_flair_per_tier` | cosmetic | Profile badge / nameplate / chat color per tier | ✅ |
| `profile_title` | cosmetic | Titolo tier mostrato su profilo (es. "VIP 5 — Asceta") | ✅ |
| `daily_login_priority` | convenience | Faster server queue / priority login slot a tier alti | ✅ |
| `customer_support_priority` | convenience | Higher support response priority a VIP 5+ | — |
| `mailbox_expansion` | convenience | Mailbox slot expansion / longer retention a tier alti | — |
| `friend_list_expansion` | convenience | Più friend slots a tier alti | — |
| `daily_summon_qol` | convenience | Storico pull esteso. **No extra summons. No pity skip.** | ✅ (forbid_pity_skip, forbid_extra_pulls) |

## Forbidden Benefits (12 — hard list)

| Benefit | Reason |
|---|---|
| `combat_stat_boost` | P2W combat power |
| `artifact_direct_grant` | artifact internal-only canary |
| `constellation_direct_grant` | banner hidden |
| `hero_direct_grant` | heroes must remain gacha |
| `premium_targeted_sigilli` | banners locked |
| `pity_skip` | pity is design-protected |
| `pvp_rank_skip` | breaks competitive ladder |
| `battle_pass_premium_auto_grant` | BP premium must be purchased separately |
| `unlock_locked_systems_via_tier` | locked surfaces require their own signoff packs |
| `discount_on_premium_or_targeted_summon` | banners locked, no discount lever |
| `reduced_cost_for_paid_artifact_or_pity` | forbidden product categories |
| `surprise_random_charge_for_tier_upgrade` | predatory |

## Boundary Summary
```
vip_only_grants                    = [cosmetic flair, convenience UX, daily paid Divine Crystal stipend,
                                       shop discount on Divine Crystal packs (max 20%),
                                       badge/title display, support priority, mailbox/friend slots]
vip_forbids_combat_power_grant     = true
vip_forbids_artifact_grant         = true
vip_forbids_pity_change            = true
vip_forbids_targeted_unlock        = true
vip_forbids_bp_premium_auto_unlock = true
vip_can_accelerate                 = true
vip_can_bypass_progression         = false
vip_can_break_balance              = false
```

## Runtime
- `applies_to_vip_endpoints_runtime`: `false`
- `endpoints_remain_gated_by_VIP_LOCKED_V2`: `true`

## Verdict
`TRACK_C_VIP_BENEFIT_BOUNDARY_READY` — VIP accelera, non sblocca. Solo cosmetic + convenience. Zero P2W. Zero runtime.

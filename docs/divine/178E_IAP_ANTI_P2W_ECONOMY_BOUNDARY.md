# 178E — IAP ANTI-P2W & ECONOMY BOUNDARY (Track E)

## Verdict
`TRACK_E_IAP_ANTI_P2W_ECONOMY_BOUNDARY_READY`

## Principi core
- **Desire** sopra coercizione
- **Devotion** sopra FOMO
- **Immersion** sopra interruzione
- **Conquest** sopra surprise charge
- **Premium collection identity** sopra P2W shortcut

## Limiti potere paid (tutti vietati)
```
paid_combat_stat_boost:         ❌
paid_artifact_grant:            ❌
paid_constellation_grant:       ❌
paid_hero_direct_grant:         ❌
paid_pity_skip:                 ❌
paid_premium_or_targeted_sigilli: ❌
paid_battle_outcome_reroll:     ❌
paid_xp_potion_max_levels_skip: ❌
paid_cooldown_skip_for_pvp:     ❌
```

## Limiti gacha premium
IAP **non** può: sbloccare Premium banner, sbloccare Targeted banner, mostrare Artifact banner, mostrare Constellation banner.

## Limiti VIP (design-only)
VIP concede solo: **cosmetic flair, convenience UX, daily Divine Crystal stipend, shop discount su crystal packs (max 20%), badge/title display**.
VIP **mai** combat power, artifact, pity change, targeted unlock.

## Limiti Battle Pass (design-only)
BP track concede solo cosmetic + currency. Mai artifact, mai premium/targeted sigilli, mai pity skip, mai combat stat.

## Cosmetici
Nessun grant di stats/heroes/combat power. Refund revoke entitlement.

## Artifact IAP prohibition (strict)
IAP NON tocca artifact ownership in alcun product family. Stage 8 canary internal-only — IAP non vi accede.

## First-time purchase bonus
- Consentito, per Apple ID / Google account.
- Max multiplier 2.0× su starter pack.
- Disclosure obbligatorio.
- Riproponibile dopo 180 giorni (reset visibile al player).

## Offer reset rules
- Daily: UTC daily boundary.
- Weekly: UTC weekly.
- Event: a event end.
- Limited lifetime: mai reset.

## Player communication
- Loot box odds visibili nel banner + linkati in IAP purchase screen.
- Pricing in valuta locale.
- Terms + refund link in IAP purchase screen.
- **No dark patterns**, **no aggressive modals**, **no pressure countdown < 60s**.

## Economy boundary summary
```
iap_can_accelerate:            ✅
iap_can_bypass_progression:    ❌
iap_can_break_balance:         ❌
iap_can_change_pity:           ❌
iap_can_unhide_locked_banners: ❌
iap_can_inject_artifact_state: ❌
```

Output JSON: `data/design/iap/iap_anti_p2w_economy_boundary_v1.json`

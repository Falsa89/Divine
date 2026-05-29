# 181B — VIP Canonical Tier Design

**Track:** B — Canonical Tier Design
**Verdict:** `TRACK_B_VIP_CANONICAL_TIER_DESIGN_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Naming
- **Nome canonico:** `VIP`
- **Label IT raccomandata:** `VIP — Aura Divina`
- **Candidati alternativi:** `Vergine Divina`, `Anima Privilegiata`, `Aura Divina`

## Modello
- **Tipo:** spend-based progression (account-wide accumulated IAP spend in tagged `paid` Divine Crystals)
- **Metric:** `vip_points`
- **Source autorizzati:**
  - IAP purchases di prodotti `dw_real_*` (mappati su mock IDs interni)
  - Grant esplicito via system endpoint (admin/refund-reverse correction)
- **Source proibiti:** gameplay grind, free Divine Crystals spend, event currency conversion, social rewards
- **Decay:** `false` (decay penalizza paying players legittimi; tier sticky)

## Tier Ladder (11 tier: 0..10)

| Tier | Label IT | Spend Threshold | Locked | Live |
|---|---|---|---|---|
| 0 | VIP 0 — Visitatore | 0 | false (baseline) | false |
| 1 | VIP 1 — Devoto | `<<VIP_TIER_1>>` | true | false |
| 2 | VIP 2 — Iniziato | `<<VIP_TIER_2>>` | true | false |
| 3 | VIP 3 — Custode | `<<VIP_TIER_3>>` | true | false |
| 4 | VIP 4 — Sacerdote | `<<VIP_TIER_4>>` | true | false |
| 5 | VIP 5 — Asceta | `<<VIP_TIER_5>>` | true | false |
| 6 | VIP 6 — Eletto | `<<VIP_TIER_6>>` | true | false |
| 7 | VIP 7 — Mistico | `<<VIP_TIER_7>>` | true | false |
| 8 | VIP 8 — Saggio | `<<VIP_TIER_8>>` | true | false |
| 9 | VIP 9 — Veggente | `<<VIP_TIER_9>>` | true | false |
| 10 | VIP 10 — Aura Divina | `<<VIP_TIER_10>>` | true | false |

> Le soglie reali saranno definite nello Stage 2 della roadmap (TIER_THRESHOLD_SIGNOFF), dopo review economy team + recheck anti-P2W.

## Principi di progression
1. VIP 0 è lo stato di default per non-paying e nuovi player (NON locked, baseline).
2. VIP 1-10 richiedono paid spend; tutti locked finché VIP_LOCKED_V2 non viene flipped.
3. Progression monotonica (mai demote eccetto refund/chargeback).
4. Benefit cumulativi (tier superiori ereditano benefit inferiori).
5. Refund di un acquisto riduce `vip_points`; tier ricalcolato on next read.

## Vincoli anti-P2W (hard rules)
- `no_live_amounts_in_this_pack`: `true`
- `no_combat_power_unlock_via_tier`: `true`
- `no_artifact_constellation_via_tier`: `true`
- `no_premium_targeted_sigilli_via_tier`: `true`
- `no_pity_skip_via_tier`: `true`

## Verdict
`TRACK_B_VIP_CANONICAL_TIER_DESIGN_READY` — 11 tier definiti, soglie placeholder, spend-based, no P2W via tier, design-only.

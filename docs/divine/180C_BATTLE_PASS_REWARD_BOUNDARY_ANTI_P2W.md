# 180C — BATTLE PASS REWARD BOUNDARY & ANTI-P2W (Track C)

## Verdict
`TRACK_C_BATTLE_PASS_REWARD_BOUNDARY_READY`

## Allowed rewards (design-only, caps placeholder)
- `divine_crystals_free` (tutti i track)
- `divine_crystals_paid` (premium + deluxe; tagged paid origin, refundable)
- `gold` / risorse base (tutti)
- `sigilli_standard` (tutti, cap limitato)
- `sigilli_elemental` (premium/deluxe + free in limited milestone)
- `sigilli_selective` (premium/deluxe; free solo come one-time milestone, molto limitato)
- Cosmetics (tutti; deluxe = exclusive frame/title/nameplate)
- QoL/catch-up materials (premium/deluxe, soft cap)
- Titles / profile frames (tutti)

## Forbidden rewards (hard list)
| Reward | Motivo |
|--------|--------|
| Direct 6★ hero grant | P2W; hero acquisition deve restare gacha |
| `artifact_id` direct grant | Artifact internal-only canary; IAP/BP mai grant |
| Constellation direct grant | Banner hidden; design-protected |
| Combat stat boost (permanent/seasonal) | P2W combat power |
| Exclusive meta-hero combat power | P2W; meta hero deve restare gacha-reachable |
| Uncapped progression material | Rompe balance + forza purchase |
| Paid-only mandatory resource | Predatorio (forced purchase) |
| PvP rank/elo skip | Rompe ladder competitivo |
| `sigilli_premium` / `sigilli_targeted` | Banner locked |
| Pity skip | Pity è lever economy design-protected |

## Paid vs free value boundary
- Max ratio paid:free = **3:1** (paid track mai > 3× free per evitare coercion).
- Deluxe vs Premium delta deve essere cosmetic/QoL only.
- Deluxe **mai** combat power extra rispetto a Premium.
- Free track deve essere meaningfully rewarding (non solo "crumbs").
- Premium track **mai** unlock di sistemi locked.

## Fairness policy
- Tutti i meta heroes reachable via gacha ✅
- Premium pass **accelera**, non sblocca ✅
- Missioni doable senza paid resources ✅
- Login window grace: 3 giorni post-period

## Communication policy
- Reward table visibile **prima** del purchase
- Paid track disclosed chiaramente
- Cosmetics marked exclusive chiaramente
- **Vietato** loot box dentro pass track (doppia monetization)
- **Vietato** pressure countdown < 60s
- Refund/revoke aligned con 178D

## Runtime impact
- `applies_to_bp_endpoints_runtime`: **false**
- BP endpoints rimangono gated da `BP_LOCKED_V2`.

Output JSON: `data/design/battle_pass/bp_reward_boundary_anti_p2w_v1.json`

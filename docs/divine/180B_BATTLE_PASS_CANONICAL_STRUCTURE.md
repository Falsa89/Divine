# 180B — BATTLE PASS CANONICAL STRUCTURE (Track B)

## Verdict
`TRACK_B_BATTLE_PASS_CANONICAL_STRUCTURE_READY`

**Design-only**. Nessun reward live, nessun amount finale, nessun DB write.

## Nome
- Candidati: **Divine Pass**, Patto Divino, Cammino degli Eroi
- Raccomandato: **Divine Pass** (en) / **Patto Divino** (it)

## Track
| Track    | Label IT                              | Locked | Note                                                          |
|----------|---------------------------------------|--------|---------------------------------------------------------------|
| FREE     | Cammino del Devoto (Free)             | ❌     | Accessibile a tutti, reward base preview-safe                 |
| PREMIUM  | Patto Divino Premium                  | ✅     | `BP_PREMIUM_BUY_LOCKED_V2`; richiede future IAP integration   |
| DELUXE   | Patto Divino Eterno (Deluxe)          | ✅     | Cosmetic/QoL only; **mai** combat power                       |

## Stagione
- Raccomandato: **42 giorni** (6 settimane) — compromesso retention/burnout.
- Range: 28-56 giorni.
- Max levels: 50.
- Reset: hard reset a fine season; unclaimed expire.
- Catch-up policy: XP scaled boost limitato (max 30%); **vietato** skip pagato a livello max.

## Modello XP/Missioni
- Daily: 3 missioni, <10 minuti, **no stamina**.
- Weekly: 5 missioni, PvE/PvP/social.
- Season: 10 long-arc obiettivi narrativi.
- Login bonus: max 10% XP stagione (per non penalizzare casual).
- **Vietato**: paid mandatory daily chores, stamina dependency.

## Reward themes consentiti
- Profile cosmetic frames / nameplates / titoli
- Sticker emote / avatar accessories
- Sigilli **standard / elemental / selective** limitati
- Cristalli Divini (free per Free track; paid stipend per Premium)
- Gold / risorse base
- Materials catch-up entro caps

## Reward themes vietati
Direct 6★ hero grant, premium/targeted sigilli, artifact, constellation, combat stat boost, PvP rank skip, meta hero exclusive power, uncapped progression materials, paid-only mandatory resources, pity skip.

## Placeholders (no live amounts)
```
divine_crystals_free_track:        <<TIER_BASE_CRYSTALS>>
divine_crystals_paid_premium_track: <<TIER_PREMIUM_CRYSTALS>>
sigilli_per_season_free:           <<TIER_BASE_SIGILLI>>
sigilli_per_season_premium:        <<TIER_PREMIUM_SIGILLI>>
gold_per_season_free:              <<TIER_BASE_GOLD>>
cosmetic_count_deluxe:             <<TIER_DELUXE_COSMETIC>>
```

## Benchmark
Ispirazione HSR/Genshin free/premium/deluxe accettata SOLO come pattern. Deluxe sicuro = solo cosmetic/QoL. Anti-burnout: missioni completabili senza paid items.

Output JSON: `data/design/battle_pass/bp_canonical_structure_v1.json`

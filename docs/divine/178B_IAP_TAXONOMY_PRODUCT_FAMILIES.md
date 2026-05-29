# 178B — IAP TAXONOMY & PRODUCT FAMILIES (Track B)

## Verdict
`TRACK_B_IAP_TAXONOMY_PRODUCT_FAMILIES_READY`

**Design-only**. Nessun product ID reale registrato su App Store Connect o Google Play Console in questo pack.

## Convenzione di naming
```
dw_<family>_<variant>_<size>_v1
```
Prefisso riservato per ID reali futuri: `dw_real_…` (Stage 2 della Roadmap, Track F).

## Famiglie autorizzate

| Famiglia              | Tipo piattaforma                 | Note                                                                                  |
|-----------------------|----------------------------------|----------------------------------------------------------------------------------------|
| `divine_crystal_pack` | consumable                       | Acquisto diretto di Cristalli Divini paid. Bonus first-time consentito.                |
| `summon_pack`         | consumable                       | Sigilli per **standard / elemental / selective**. **Mai** premium/targeted/artifact.   |
| `launch_support_pack` | consumable                       | Una sola volta per account-lifetime. Mix di crystals + sigilli standard + cosmetico.   |
| `monthly_pass`        | non_renewing → futuro auto-renew | Devotion Pass: daily stipend crystals + cosmetic. **No combat power**, **no artifact**.|
| `cosmetic_pack`       | non_consumable                   | Skin/title/banner-frame. Mai potere combat. Refund revoke entitlement.                 |
| `battle_pass`         | non_renewing per stagione        | Design-only, `BP_LOCKED_V2`. Future pack dedicato.                                     |
| `vip_tier`            | non_consumable progression       | Design-only, `VIP_LOCKED_V2`. Future pack dedicato.                                    |
| `offer_code_promo`    | server-redeemed non-IAP          | Codici promo. Mai artifact. Mai premium/targeted sigilli.                              |

## Famiglie vietate
- `artifact_direct_purchase` — artifact internal-only.
- `constellation_direct_purchase` — banner hidden.
- `premium_sigilli_direct_purchase` — banner locked.
- `targeted_sigilli_direct_purchase` — banner locked.
- `stat_boost_consumable` — no paid combat power.
- `hero_direct_grant` — solo gacha.
- `pity_skip` — pity protetto.
- `surprise_random_charge` — predatorio.

## Placeholder pricing
Nessun prezzo reale. Stage 9 della roadmap (Pricing/Localization Signoff) compila i placeholder.

Output JSON: `data/design/iap/iap_taxonomy_product_families_v1.json`

# 179B — SHOP IAP MOCK PRODUCT CATALOG (Track B)

## Verdict
`TRACK_B_SHOP_IAP_MOCK_PRODUCT_CATALOG_READY`

**Mock-only**. Nessun real Apple/Google product ID registrato. Nessun prezzo finale.

## Regole di naming
- Prefisso obbligatorio: `mock.divinewaifus.`
- Formato: `mock.divinewaifus.<family>.<variant_or_size>`
- Lower-case, dot-separated.
- Real store IDs (`dw_real_…`) allocati solo allo Stage 2 della roadmap 178F.

## Catalogo mock (sintesi)
| mock_id                                                  | Famiglia               | Piattaforma futura            | Prezzo (placeholder) | live_buyable |
|----------------------------------------------------------|------------------------|-------------------------------|----------------------|--------------|
| `mock.divinewaifus.crystals.starter`                     | divine_crystal_pack    | consumable                    | `<<TIER_LOW>>`       | ❌           |
| `mock.divinewaifus.crystals.small`                       | divine_crystal_pack    | consumable                    | `<<TIER_S>>`         | ❌           |
| `mock.divinewaifus.crystals.medium`                      | divine_crystal_pack    | consumable                    | `<<TIER_M>>`         | ❌           |
| `mock.divinewaifus.crystals.large`                       | divine_crystal_pack    | consumable                    | `<<TIER_L>>`         | ❌           |
| `mock.divinewaifus.crystals.mega`                        | divine_crystal_pack    | consumable                    | `<<TIER_XL>>`        | ❌           |
| `mock.divinewaifus.summon.standard.10x`                  | summon_pack (standard) | consumable                    | `<<TIER_M>>`         | ❌           |
| `mock.divinewaifus.summon.elemental.10x`                 | summon_pack (elemental)| consumable                    | `<<TIER_M>>`         | ❌           |
| `mock.divinewaifus.summon.selective.10x`                 | summon_pack (selective)| consumable                    | `<<TIER_L>>`         | ❌           |
| `mock.divinewaifus.launchpack.devoted`                   | launch_support_pack    | consumable                    | `<<TIER_L>>`         | ❌           |
| `mock.divinewaifus.launchpack.eternal`                   | launch_support_pack    | consumable                    | `<<TIER_XL>>`        | ❌           |
| `mock.divinewaifus.monthlypass.devotion`                 | monthly_pass           | non_renewing → auto_renewable | `<<TIER_SUB_M>>`     | ❌           |

## Banner scope per summon pack
- **Consentiti**: `standard`, `elemental`, `selective`
- **Vietati**: `premium`, `targeted`, `artifact`, `constellation`

## Contenuti vietati nel catalogo
artifact, constellation, sigilli_premium, sigilli_targeted, pity_skip, combat_stat, hero_direct, surprise random charge, hidden odds.

## Source of truth futura
`GET /api/iap/products` (design-only, vedi Track E).

Output JSON: `data/design/shop_iap/shop_iap_mock_product_catalog_v1.json`

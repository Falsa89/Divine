# 178A — IAP MONETIZATION SURFACE AUDIT (Track A)

## Verdict
`TRACK_A_IAP_MONETIZATION_SURFACE_AUDIT_READY`

Questo documento riassume l'audit completo delle surface di monetizzazione attuali, **prima** di qualunque integrazione IAP.

## Markers di approvazione
```
PROJECT_IAP_DESIGN_APPROVAL = true
PROJECT_ACCELERATION_MODE   = IAP_DESIGN_ONLY
```

## Frontend surface classificate

| Route                              | Classe         | Stato lock                                                          |
|------------------------------------|----------------|---------------------------------------------------------------------|
| `frontend/app/shop.tsx`            | locked         | `SHOP_LOCKED_V2 = true` — buy disabled, daily disabled               |
| `frontend/app/item-shop.tsx`       | locked         | `ITEM_SHOP_LOCKED_V2 = true`                                         |
| `frontend/app/treasury.tsx`        | preview-only   | wallet snapshot read-only                                            |
| `frontend/app/economy.tsx`         | redirect-only  | reindirizza a `/soul-forge` (SF_MERGE Track D)                       |
| `frontend/app/exclusive.tsx`       | locked         | legacy lock notice (Divine Weapons non craftabili)                   |
| `frontend/app/(tabs)/gacha.tsx`    | live           | Premium/Targeted **locked**, Artifact/Constellation **hidden**      |
| `frontend/app/battlepass.tsx`      | locked         | `BP_LOCKED_V2 = true`, `BP_PREMIUM_BUY_LOCKED_V2 = true`             |
| `frontend/app/vip.tsx`             | locked         | `VIP_LOCKED_V2 = true`                                               |
| `frontend/app/soul-forge.tsx`      | live, do_not_touch | Anime Hub, inline confirmation, crash-proof                      |
| `frontend/app/cosmetics.tsx`       | preview-only   | nessun acquisto live                                                 |

## Backend
- Nessun route IAP/payment/receipt presente in `backend/routes/`.
- Nessun SDK pagamento integrato.
- `.env` contiene solo `DB_NAME`, `EMERGENT_LLM_KEY`, `JWT_SECRET`, `MONGO_URL` — nessun secret IAP.

## Locks verificati
```
premium_banner_locked:        ✅
targeted_banner_locked:       ✅
artifact_banner_hidden:       ✅
constellation_banner_hidden:  ✅
shop_locked:                  ✅
item_shop_locked:             ✅
battlepass_locked:            ✅
vip_locked:                   ✅
legacy_post_artifact_423:     ✅
```

## Invarianti MD5
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
```

Output JSON: `data/design/iap/iap_monetization_surface_audit_v1.json`

# 182A — Project Context Revalidation

**Track:** A — Project Context Revalidation
**Verdict:** `TRACK_A_PROJECT_CONTEXT_REVALIDATION_READY`
**Pack:** `PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY`

## Scope
Dimostrare che l'audit ha riletto tutto il contesto canonico del progetto prima di valutare lo stato reale del runtime.

## Contesto rivalidato

### Benchmark Canonical (16 modalità live/special)
- Source-of-truth: `data/design/benchmark_canonical/*`
- Documenti master: `96_BENCHMARK_CANONICAL_SOURCE_OF_TRUTH.md`, `96_LIVE_SPECIAL_MODES_CANONICAL.md`
- Modalità mappate: 16 canoniche

### Monetization Locks 178/179/180/181
| Pack | Doc | Status | Frontend Lock |
|---|---|---|---|
| 178 IAP Design | `178_IAP_DESIGN.md` | `COMPLETE_PUBLIC_REPO_VERIFIED` | n/a |
| 179 Shop IAP | `179_SHOP_IAP_INTEGRATION.md` | `COMPLETE_PUBLIC_REPO_VERIFIED` | `SHOP_LOCKED_V2`, `ITEM_SHOP_LOCKED_V2` |
| 180 Battle Pass | `180_BATTLE_PASS_SURFACE_MODERNIZATION.md` | `COMPLETE_PUBLIC_REPO_VERIFIED` | `BP_LOCKED_V2`, `BP_PREMIUM_BUY_LOCKED_V2` |
| 181 VIP | `181_VIP_DESIGN_AND_IAP_INTEGRATION.md` | `READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING` | `VIP_LOCKED_V2` |

### Artifact Stage 8 — Internal Canary Only
- Doc: `176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`
- Public exposure: `false`
- Frontend banner state: `hidden`
- Legacy POST endpoints: locked HTTP **423**
- `backend/routes/artifacts.py` MD5: `893f244d85fd45cbe825996463995293`

### SLC / Server Lifecycle
- Docs: 92, 93, 94, 97, 99
- Status: `DESIGN_AND_PARTIAL_RUNTIME`
- Multi-shard live: NON ancora attivo (gated)

### Housing / Dimora Divina
- Design state: `DESIGN_ONLY_PREVIEW`
- Frontend: `housing-preview.tsx`

### Gacha Rate Sanity
- Standard 5★+6★ combined: **1.5%**
- Elemental: **2.5%**
- Selective: **3.5%**
- Premium/Targeted: **5% LOCKED**
- Artifact/Constellation: **hidden**
- Pity: **design-only**

### Soul Forge
- State: `FUNCTIONAL_INLINE_PANEL` (modal rimosso)
- Do not touch unless auditing

### No Stamina Decision
- Decisione canonica: `NO_STAMINA_SYSTEM`
- Compliance status runtime: **`VIOLATED_LEGACY_CODE_STILL_PRESENT`**
- File backend in violazione: `combat.py`, `cosmetics.py`, `economy.py`, `gvg.py`, `raids.py`
- File frontend in violazione: `events.tsx`, `gvg.tsx`, `shop.tsx`, `tower.tsx`, `treasury.tsx`
- ⚠️ Audit-only finding. NOT remediated in this pack. See Track D.

### Homepage currencies
- Allowed: **Oro**, **Cristalli Divini**, **EXP Account**
- Deeper currencies: `treasury.tsx`

### Summon currency order
- First: **Sigilli**
- Then: **Cristalli Divini**
- Requires explicit confirmation: `true`

### Asset/Audio Placeholder Pipeline Rule (NEW canonical)
Introdotto da questo pack: ogni placeholder TEST deve essere registrato con 7 metadata keys:
`mode_id`, `screen_id`, `asset_key`, `asset_status`, `audio_key`, `audio_status`, `replace_before_release`.

## Forbidden compliance (tutti True ✅)
- `no_runtime_implementation`, `no_db_writes`, `no_player_data_mutation`
- `no_unlock_locked_systems`, `no_gacha_or_pity_changes`
- `no_iap_bp_vip_shop_live_activation`, `no_artifact_public_activation`
- `no_battle_engine_or_combat_changes`, `no_character_bible_mutation`
- `no_hero_kit_final_numbers_change`, `no_final_assets_or_audio_added`
- `no_paid_product_ids_added`, `no_env_secrets_added`
- `no_required_validator_weakening`

## Verdict
`TRACK_A_PROJECT_CONTEXT_REVALIDATION_READY` — Tutto il contesto pre-esistente riletto e mappato. 14/14 forbidden compliance True. Zero DB writes, zero runtime changes.

# 181 — PROJECT VIP DESIGN AND IAP INTEGRATION — DIVINE WAIFUS

## Verdetto locale
**`PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo che l'utente ha eseguito **Save to GitHub → branch `main` → PUSH** e verificato manualmente la repo pubblica.

---

## Obiettivo
Disegnare il sistema **VIP** come **spend-based progression** legato al `purchase_ledger` di PROJECT_SHOP_IAP_INTEGRATION (179D), mantenendo la superficie VIP **completamente locked** e senza alcuna mutazione live. Nessun VIP attivato, nessun tier sbloccato, nessun privilegio runtime, nessun receipt verifier live, nessuna scrittura DB. La UI `vip.tsx` non viene modificata in questo pack.

## Markers
```
PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_APPROVAL = true
PROJECT_ACCELERATION_MODE                       = VIP_DESIGN_AND_IAP_INTEGRATION_LOCKED_ONLY
```

---

## Track summary

| Track | Output JSON                                                                | Output Doc                                                       | Verdict                                                          |
|-------|----------------------------------------------------------------------------|------------------------------------------------------------------|------------------------------------------------------------------|
| **A** | `data/design/vip/vip_surface_lock_audit_v1.json`                           | `docs/divine/181A_VIP_SURFACE_AND_LOCK_AUDIT.md`                 | `TRACK_A_VIP_SURFACE_AND_LOCK_AUDIT_READY`                       |
| **B** | `data/design/vip/vip_canonical_tier_design_v1.json`                        | `docs/divine/181B_VIP_CANONICAL_TIER_DESIGN.md`                  | `TRACK_B_VIP_CANONICAL_TIER_DESIGN_READY`                        |
| **C** | `data/design/vip/vip_benefit_boundary_anti_p2w_v1.json`                    | `docs/divine/181C_VIP_BENEFIT_BOUNDARY_ANTI_P2W.md`              | `TRACK_C_VIP_BENEFIT_BOUNDARY_READY`                             |
| **D** | `data/design/vip/vip_iap_entitlement_wallet_mapping_v1.json`               | `docs/divine/181D_VIP_IAP_ENTITLEMENT_AND_WALLET_MAPPING.md`     | `TRACK_D_VIP_IAP_ENTITLEMENT_AND_WALLET_MAPPING_READY`           |
| **E** | `data/design/vip/vip_locked_ui_preview_policy_v1.json`                     | `docs/divine/181E_VIP_LOCKED_UI_PREVIEW_POLICY.md`               | `TRACK_E_VIP_LOCKED_UI_PREVIEW_POLICY_READY`                     |
| **F** | `data/design/vip/vip_future_api_backend_contract_v1.json`                  | `docs/divine/181F_VIP_FUTURE_API_BACKEND_CONTRACT.md`            | `TRACK_F_VIP_FUTURE_API_BACKEND_CONTRACT_READY`                  |
| **G** | `data/design/vip/vip_future_implementation_roadmap_v1.json` + validator     | `docs/divine/181G_VIP_FUTURE_IMPLEMENTATION_ROADMAP.md`           | `TRACK_G_VIP_FUTURE_IMPLEMENTATION_ROADMAP_READY`                |

---

## Highlights

### Track A — Surface & Lock Audit
- `frontend/app/vip.tsx` MD5 `45fcc9890b6b128c37088bc33aa54caf` — classificazione **locked**.
- `VIP_LOCKED_V2 = true` ✅, `claim_disabled = true`, `buy_button_visible = false`, `lock_banner_visible = true`.
- Nessun IAP SDK importato (StoreKit / Google Play Billing / RevenueCat / react-native-iap / expo-in-app-purchases tutti `false`).
- Backend endpoint legacy VIP esistenti (`GET /api/vip`, `POST /api/vip/claim-daily`) ma **gated dal frontend lock** — nessuna `apiCall` parte mai.
- Related surfaces locked: `shop.tsx` (SHOP_LOCKED_V2), `item-shop.tsx` (ITEM_SHOP_LOCKED_V2), `battlepass.tsx` (BP_LOCKED_V2 + BP_PREMIUM_BUY_LOCKED_V2).
- 0 DB writes, 0 runtime changes.

### Track B — Canonical Tier Design
- Nome canonico: **VIP** (label IT: **VIP — Aura Divina**).
- 11 tier (0..10): VIP 0 (Visitatore, baseline, non locked) + VIP 1..10 (Devoto/Iniziato/Custode/Sacerdote/Asceta/Eletto/Mistico/Saggio/Veggente/Aura Divina), tutti `locked: true`, `live: false`.
- Progression: **spend-based**, metric `vip_points`. Solo IAP `dw_real_*` (mock-tagged) contribuiscono.
- Forbidden sources: gameplay grind, free Divine Crystals spend, event/social currency.
- No decay. Sticky tiers. Demotion solo su refund/chargeback.
- Tutti gli importi soglia sono **placeholder** (`<<VIP_TIER_X>>`).
- Vietato: combat power via tier, artifact/constellation via tier, premium/targeted sigilli via tier, pity skip via tier.

### Track C — Benefit Boundary & Anti-P2W
- 9 allowed benefit categories: daily crystal stipend (paid), shop crystal pack discount (max 20% @ VIP 10), cosmetic flair/title, login priority, customer support priority, mailbox/friend slots, summon QoL (no extra pulls, no pity skip).
- 12 forbidden benefits: combat stat boost, artifact/constellation/hero direct grant, premium/targeted sigilli, pity skip, PvP rank skip, BP premium auto-grant, unlock locked systems via tier, summon discount on premium/targeted, paid artifact/pity reduced cost, surprise charges.
- `vip_can_accelerate = true`, `vip_can_bypass_progression = false`, `vip_can_break_balance = false`.
- `applies_to_vip_endpoints_runtime = false`, `endpoints_remain_gated_by_VIP_LOCKED_V2 = true`.

### Track D — IAP Entitlement & Wallet Mapping
- Accrual: **1 paid Divine Crystal granted via verified IAP = 1 vip_point** (placeholder `<<VIP_POINTS_PER_PAID_CRYSTAL>>`).
- Product family mapping: `divine_crystal_pack` ✅, `launch_support_pack` ✅ (paid crystals component), `monthly_pass` ✅ (daily stipend), `summon_pack` ❌, `cosmetic_pack` ❌, `battle_pass` ❌, `vip_tier` ❌ (no direct purchase), `offer_code_promo` ❌.
- Ledger design: `vip_points_ledger` collection (future), append-only, server-authoritative, indici `ix_uniq_vip_idempotency` (unique) + `ix_user_time`.
- Refund/Revoke: Apple ASSN + Google RTDN + manual support → append revoke entry, tier ricalcolato on next read.
- Wallet separation: `vip_points` NON spendable, marker progression only.
- Server authority assoluta: client mai grant/recompute; server valida tutti i receipt prima del grant.

### Track E — Locked UI Preview Policy
- `frontend/app/vip.tsx` **NON modificato** in questo pack (MD5 invariato).
- Allowed future changes: copy IT, tier ladder preview 0..10 con locked pills, benefit list per tier, placeholder pricing, link a `/shop` preview (locked), accessibility 44pt/48dp, SafeAreaView + ScrollView.
- Forbidden future changes: claim attivo, buy-tier attivo (VIP non è acquisto diretto), apiCall mentre VIP_LOCKED_V2, IAP SDK, real product IDs, ledger write client, countdown < 60s, hidden price/benefit, weakening VIP_LOCKED_V2.
- Copy IT pronto: "VIP — Aura Divina", "Bloccato — in preparazione", "Disponibile presto", ecc.

### Track F — Future API & Backend Contract
- 5 endpoint futuri **design-only**:
  - `GET /api/vip/status` (player, RO)
  - `POST /api/vip/claim-daily` (player, idempotency `<user_id>:<utc_day>`)
  - `POST /api/vip/grant` (system_only, idempotency `<user_id>:<linked_purchase_id>`)
  - `POST /api/vip/revoke` (system_only, idempotency `<user_id>:<linked_purchase_id>:REVOKE`)
  - `GET /api/vip/history` (player, RO)
- Feature flags forced off in design: `VIP_PROGRESSION_ENABLED=false`, `VIP_DAILY_CLAIM_ENABLED=false`, `VIP_BENEFITS_RUNTIME_ENABLED=false`, `VIP_GRANT_ENABLED=false`, `VIP_CANARY_ONLY=true`, `VIP_GLOBAL_DISABLED=true`.
- Forbidden grants in claim-daily response: `artifact_id`, `constellation_id`, `sigilli_premium`, `sigilli_targeted`, `hero_direct_grant`, `combat_stat_boost`, `pity_skip`.
- Premium entitlement source: `purchase_ledger` from PROJECT_SHOP_IAP_INTEGRATION (179D).

### Track G — Future Implementation Roadmap
- 9 stage espliciti con marker, blockers, rollback.
- Stage 6 + 7 canary internal-only (sfqa@test.com + test@test.com).
- Stage 9 (release gate) bloccato su 178F Stage 10 e 179 Stage 8.

---

## Validator & suite registration

### Validator OPTIONAL
- File: `backend/scripts/validate_project_vip_design_and_iap_integration_v1.py`
- Tupla suite: `('PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION', 'validate_project_vip_design_and_iap_integration_v1.py')`
- Risultato: **PASS**
- Asserts: 7 track JSON + 1 proof marker, lock tokens VIP/BP/Shop/Item-Shop presenti, no IAP SDK runtime, no real product IDs (`com.divinewaifus.*` / `dw_real_*` patterns bloccati), no live VIP/IAP/BP receipt route, MD5 invariants su 5 file (battle_engine, .env, artifacts.py, battlepass.tsx, vip.tsx), Track A locks_verified True ovunque + iap_sdk_imported=False, Track B 11 tier con 1..10 locked, Track C benefit_boundary_summary anti-P2W coerente, Track D server_authority + wallet_separation, Track E frontend_vip_modified_in_this_pack=False + lock invariants, Track F feature flags off + 5 endpoint, Track G 9 stage monotonici.

### Strategia tripled-sentinel
1. **Top sentinel**: `# PUBLIC_SYNC_TAG_RESYNC_v9: suite_runner_vip_design_and_iap_integration_v9_2026_05_29`
2. **Sentinel inline**: `# VIP_DESIGN_AND_IAP_INTEGRATION_REGISTRATION_SENTINEL`
3. **Proof marker JSON in directory dedicata**: `data/design/vip/vip_suite_registration_proof_marker_v1.json`

### Suite finale
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel \
  --json-out /tmp/vip_suite_report.json
```
```
Overall: PASS  (pass=711, fail=0, miss=0)
EXIT=0
```
🎯 **711/711 PASS** (710 baseline + 1 nuovo `PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION`). 84 entries SUPERSEDED post-AF2-N (atteso, non bloccante).

---

## 🔐 MD5 Invarianti (FINALI)

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅ UNCHANGED
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅ UNCHANGED
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx         ✅ UNCHANGED
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx                ✅ UNCHANGED
```

### Frontend lock token verificati
- `VIP_LOCKED_V2 = true` ✅
- `BP_LOCKED_V2 = true` + `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `SHOP_LOCKED_V2 = true` ✅ / `ITEM_SHOP_LOCKED_V2 = true` ✅
- Soul Forge / battle_engine / artifacts: invariati ✅

---

## ❌ Conferma scope NON violato

| Categoria forbidden | Status |
|---|---|
| VIP live activation / tier unlock | ❌ 0 |
| VIP daily claim live | ❌ 0 |
| VIP grant / revoke runtime | ❌ 0 |
| VIP privilege resolver runtime | ❌ 0 |
| VIP subscription / direct tier purchase | ❌ 0 |
| StoreKit / Google Play Billing / RevenueCat runtime | ❌ 0 |
| Real product IDs in code | ❌ 0 |
| Receipt endpoint live / fulfillment endpoint live | ❌ 0 |
| DB writes | ❌ 0 |
| Wallet balance changes | ❌ 0 |
| VIP status grant runtime | ❌ 0 |
| Unlock `VIP_LOCKED_V2` / `BP_LOCKED_V2` / `SHOP_LOCKED_V2` / `ITEM_SHOP_LOCKED_V2` | ❌ no |
| Premium/Targeted gacha unlock | ❌ 0 |
| Gacha rate / pity changes | ❌ 0 |
| Artifact/Constellation unhide / Artifact state changes | ❌ 0 |
| Soul Forge / battle_engine / Character Bible / `.env` changes | ❌ 0 |
| REQUIRED validator weakening / fake PASS | ❌ 0 |

---

## 📦 File creati / modificati

### Nuovi (17 file)
- 8 JSON in `data/design/vip/` (7 design tracks + 1 proof marker)
- 1 validator: `backend/scripts/validate_project_vip_design_and_iap_integration_v1.py`
- 8 doc: `docs/divine/181_VIP_DESIGN_AND_IAP_INTEGRATION.md` + `181A..181G`

### Modificati (solo comments + 1 tupla)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — header `PUBLIC_SYNC_TAG_RESYNC_v9` + sentinel inline + tupla `('PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION', ...)`

### Non modificati (esplicitamente)
- `frontend/app/vip.tsx` (per scelta design-only — MD5 invariato)
- `frontend/app/battlepass.tsx`, `shop.tsx`, `item-shop.tsx`, `(tabs)/gacha.tsx`, `soul-forge.tsx`, `treasury.tsx`
- `backend/battle_engine.py`, `backend/.env`, `backend/routes/artifacts.py`
- `backend/routes/economy.py` (endpoint VIP legacy intatti — gated dal frontend lock)
- Character Bible / hero stats / kits

---

## 🔄 Public Repo Sync Verification — PENDING

### Stato locale ✅
- Suite custom Python: **711/711 PASS** (baseline 710 + 1 VIP)
- Master validator VIP: **PASS**
- MD5 invarianti: ✅ tutti rispettati (5/5)
- DB live: ✅ 0 write
- Surface lock: ✅ tutti attivi

### Azione richiesta utente
1. **Pannello Emergent → "Save to GitHub"** → branch **`main`** → **PUSH**

### Verifica manuale su GitHub.com
- ✅ `data/design/vip/` con 8 file (7 design JSON + 1 proof marker)
- ✅ `backend/scripts/validate_project_vip_design_and_iap_integration_v1.py` presente
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` contiene:
  - `# PUBLIC_SYNC_TAG_RESYNC_v9: suite_runner_vip_design_and_iap_integration_v9_2026_05_29`
  - `# VIP_DESIGN_AND_IAP_INTEGRATION_REGISTRATION_SENTINEL`
  - `('PROJECT-VIP-DESIGN-AND-IAP-INTEGRATION', 'validate_project_vip_design_and_iap_integration_v1.py'),`
- ✅ `docs/divine/181_VIP_DESIGN_AND_IAP_INTEGRATION.md` + `181A..181G`

Solo dopo questa verifica → **`PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

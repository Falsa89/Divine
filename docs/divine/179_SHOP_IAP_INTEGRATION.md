# 179 — PROJECT SHOP IAP INTEGRATION — DIVINE WAIFUS

## Verdetto locale
**`PROJECT_SHOP_IAP_INTEGRATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `PROJECT_SHOP_IAP_INTEGRATION_COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo che l'utente ha eseguito **Save to GitHub → branch `main` → PUSH** e verificato manualmente la repo pubblica.

---

## Obiettivo
Definire il **contratto di integrazione Shop ↔ IAP** in modalità **design-only**: nessun acquisto live, nessun receipt endpoint live, nessuna scrittura DB, nessun balance change. Tutto preserva i lock già attivi (`SHOP_LOCKED_V2`, `ITEM_SHOP_LOCKED_V2`, `BP_LOCKED_V2`, `VIP_LOCKED_V2`, gacha rates/pity, premium/targeted locked, artifact/constellation hidden, soul-forge intoccato).

## Markers
```
PROJECT_SHOP_IAP_INTEGRATION_APPROVAL = true
PROJECT_ACCELERATION_MODE             = SHOP_IAP_INTEGRATION_DESIGN_ONLY
```

---

## Track summary

| Track | Output JSON                                                                       | Output Doc                                                  | Verdict                                                            |
|-------|-----------------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------|
| **A** | `data/design/shop_iap/shop_iap_surface_revalidation_v1.json`                      | `docs/divine/179A_SHOP_IAP_SURFACE_REVALIDATION.md`         | `TRACK_A_SHOP_IAP_SURFACE_REVALIDATION_READY`                      |
| **B** | `data/design/shop_iap/shop_iap_mock_product_catalog_v1.json`                      | `docs/divine/179B_SHOP_IAP_MOCK_PRODUCT_CATALOG.md`         | `TRACK_B_SHOP_IAP_MOCK_PRODUCT_CATALOG_READY`                      |
| **C** | `data/design/shop_iap/shop_iap_ui_lock_preview_policy_v1.json`                    | `docs/divine/179C_SHOP_IAP_UI_LOCK_PREVIEW_POLICY.md`       | `TRACK_C_SHOP_IAP_UI_LOCK_PREVIEW_POLICY_READY`                    |
| **D** | `data/design/shop_iap/shop_iap_wallet_ledger_fulfillment_contract_v1.json`        | `docs/divine/179D_SHOP_IAP_WALLET_LEDGER_FULFILLMENT_CONTRACT.md` | `TRACK_D_SHOP_IAP_WALLET_LEDGER_FULFILLMENT_CONTRACT_READY` |
| **E** | `data/design/shop_iap/shop_iap_future_api_receipt_contract_v1.json`               | `docs/divine/179E_SHOP_IAP_FUTURE_API_RECEIPT_CONTRACT.md`  | `TRACK_E_SHOP_IAP_FUTURE_API_RECEIPT_CONTRACT_READY`               |
| **F** | `data/design/shop_iap/shop_iap_risk_compliance_roadmap_v1.json`                   | `docs/divine/179F_SHOP_IAP_RISK_COMPLIANCE_ROADMAP.md`      | `TRACK_F_SHOP_IAP_RISK_COMPLIANCE_ROADMAP_READY`                   |
| **G** | `data/design/shop_iap/shop_iap_suite_registration_proof_marker_v1.json` + validator `.py` | (vedi sezione validator)                            | `TRACK_G_SHOP_IAP_INTEGRATION_VALIDATOR_READY`                     |
| **H** | _(questo doc)_                                                                    | `docs/divine/179_SHOP_IAP_INTEGRATION.md`                   | `TRACK_H_SHOP_IAP_INTEGRATION_COMPLETION_READY`                    |

---

## Highlights

### Track A — Surface revalidation
- 7 surface monetization rivalidate vs baseline 178: **drift 0 su tutte**.
- Locks attivi confermati (shop/item-shop/BP/VIP locked, premium/targeted locked, artifact/constellation hidden, legacy POST 423).
- Homepage = Oro + Cristalli Divini + EXP Account. Tesoreria gestisce il resto.

### Track B — Mock product catalog
- 11 mock products definiti (5 crystal packs, 3 summon packs standard/elem/sel, 2 launch packs, 1 monthly pass).
- Prefisso obbligatorio `mock.divinewaifus.\*`.
- **Zero** real Apple/Google product IDs, **zero** prezzi finali.

### Track C — Shop UI lock & preview policy
- Buy/ACQUISTA disabilitato. Lock banner visibile. Daily disabled.
- Label consentite: "In preparazione", "Preview", "Non acquistabile ora", "Prezzi non finali", ecc.
- Loot box odds disclosure obbligatoria su card summon_pack.
- Refund/Restore UI **non visibili** (Stage 8 della roadmap futura).

### Track D — Wallet/Ledger/Fulfillment contract
- `divine_crystals_paid` account-wide refundable; `divine_crystals_free` server-bound.
- Summon: **Sigilli prima**, poi Cristalli; Cristalli: **FREE prima**, poi PAID.
- `wallet_ledger` + `purchase_ledger` append-only server-authoritative con index idempotency.
- Refund mai revoca gacha results già eseguiti.

### Track E — Future API & receipt contract
- 6 endpoint futuri definiti: `GET /api/iap/products`, `POST /api/iap/verify/apple`, `POST /api/iap/verify/google`, `POST /api/iap/fulfill`, `POST /api/iap/refund-reconcile`, `GET /api/iap/history`.
- Tutti i feature flag IAP a `false`; canary-only e global-disabled = `true`.
- Error modes: 401/200/400/403/410/409/423.

### Track F — Risk register & roadmap
- 10 risks registrati (R1-R10) con mitigation esplicita.
- Compliance checklist platform-aware (Apple StoreKit / Google Play Billing).
- Allineato con 178F roadmap: prossimo stage `PRODUCT_ID_MOCK_CATALOG`.

---

## Track G — Validator & suite registration

### Validator OPTIONAL
- File: `backend/scripts/validate_project_shop_iap_integration_v1.py`
- Tupla suite: `('PROJECT-SHOP-IAP-INTEGRATION', 'validate_project_shop_iap_integration_v1.py')`
- Risultato: **PASS**
- Asserts (sintesi): 6 JSON tracks + 1 proof marker validi, no runtime IAP SDK token in product code, **no real product IDs leaked** (`com.divinewaifus.*` / `dw_real_*` patterns blocked), no live receipt route, frontend locks present, gacha/banner state preserved.

### Strategia tripled-sentinel
1. **Top sentinel header**: `# PUBLIC_SYNC_TAG_RESYNC_v7: suite_runner_shop_iap_integration_v7_2026_05_29`
2. **Sentinel inline**: `# SHOP_IAP_INTEGRATION_REGISTRATION_SENTINEL (do not remove; required for public sync verification):`
3. **Proof marker JSON in directory separata**: `data/design/shop_iap/shop_iap_suite_registration_proof_marker_v1.json`

### Suite finale
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel \
  --json-out /app/backend/reports/shop_iap_integration_suite_run.json
```
```
Overall: PASS  (pass=709, fail=0, miss=0)
EXIT=0
```
🎯 **709/709 PASS** (708 baseline + 1 nuovo SHOP-IAP-INTEGRATION).

### Nota infrastructure
Container restart aveva rimosso Redis (binary mancante in `/usr/bin/redis-server`). Ripristinato con `apt-get install redis-server` + `supervisorctl restart redis`. Stessa procedura applicata in pack precedenti (Stage 8). 12 OPTIONAL fail Redis-correlati risolti contestualmente — **nessuno** legato a questo pack.

### Nota infrastructure — Expo (post-snapshot)
Dopo lo snapshot 709/709 PASS, un tentativo di restart di Expo (richiesto dal system reminder a fine task) ha rivelato un secondo problema infrastrutturale **PRE-ESISTENTE** e non legato al pack:
- `ENOSPC: System limit for number of file watchers reached` durante `metro-file-map/src/watchers/FallbackWatcher.js`
- Limit host kernel `/proc/sys/fs/inotify/max_user_watches = 12288` non modificabile dal container (`sysctl -w` → `permission denied`, manca `CAP_SYS_ADMIN`).
- Metro non usa Watchman 4.9.0 di Debian apt perché Watchman 4.9.0 manca della capability `suffix-set` richiesta da Metro recente; Metro fallback su `FallbackWatcher` che esplode su 6106 directory in `node_modules`.

Questo problema **NON è stato causato dal pack design** e **NON modifica il risultato della suite Python custom (709/709 PASS)**, che gira indipendentemente da Expo. Tuttavia, mentre Expo è BACKOFF, 6 validator OPTIONAL che dipendono dal frontend live (`OPS-A`, `OPS-B`, `OPS-C`, `OPS-C-WIRING`, `AF2-N-V26-FRONTEND-SMOKE`, `ULTRA-COMBO-V26`) tornano FAIL. Tutti sono OPTIONAL e pre-esistenti — non causati dal pack. Il fix infrastrutturale richiede aumento del `max_user_watches` host-level (azione fuori scope di questo pack design).

**Stato wrapper Expo**: `expo.conf` e `/usr/local/bin/start-expo.sh` riportati allo stato originale dopo i tentativi di workaround (rimosse `CHOKIDAR_USEPOLLING`, `WATCHPACK_POLLING`, `WATCHMAN_BINARY`, `.watchmanconfig`); nessun residuo del workaround.

---

## 🔐 MD5 Invarianti (FINALI, confermati)

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅ UNCHANGED (no secret injection)
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅ UNCHANGED
```

### Frontend lock token verificati
- `frontend/app/shop.tsx` → `SHOP_LOCKED_V2 = true` ✅
- `frontend/app/item-shop.tsx` → `ITEM_SHOP_LOCKED_V2 = true` ✅
- `frontend/app/battlepass.tsx` → `BP_LOCKED_V2 = true` ✅
- `frontend/app/vip.tsx` → `VIP_LOCKED_V2 = true` ✅
- Soul Forge → MD5 `b7659de11ac36f341e7a2f54fd29e6ed` `do_not_touch`

---

## ❌ Conferma scope NON violato

| Categoria forbidden | Status |
|---|---|
| StoreKit / Google Play Billing / RevenueCat runtime | ❌ 0 |
| Real product IDs in code | ❌ 0 |
| Live purchase buttons | ❌ 0 |
| Receipt endpoint live / fulfillment endpoint live | ❌ 0 |
| DB writes | ❌ 0 |
| Wallet balance changes | ❌ 0 |
| Shop live buys | ❌ 0 |
| Premium/Targeted unlock | ❌ 0 |
| Artifact/Constellation unhide | ❌ 0 |
| Gacha rate / pity changes | ❌ 0 |
| VIP / Battle Pass live | ❌ 0 |
| Soul Forge / battle_engine / battle_core changes | ❌ 0 |
| `backend/routes/artifacts.py` changes | ❌ 0 |
| Character Bible mutation | ❌ 0 |
| `.env` secrets | ❌ 0 |
| REQUIRED validator weakening / fake PASS | ❌ 0 |

---

## 📦 File creati / modificati

### Nuovi
- `data/design/shop_iap/shop_iap_surface_revalidation_v1.json` (Track A)
- `data/design/shop_iap/shop_iap_mock_product_catalog_v1.json` (Track B)
- `data/design/shop_iap/shop_iap_ui_lock_preview_policy_v1.json` (Track C)
- `data/design/shop_iap/shop_iap_wallet_ledger_fulfillment_contract_v1.json` (Track D)
- `data/design/shop_iap/shop_iap_future_api_receipt_contract_v1.json` (Track E)
- `data/design/shop_iap/shop_iap_risk_compliance_roadmap_v1.json` (Track F)
- `data/design/shop_iap/shop_iap_suite_registration_proof_marker_v1.json` (Track G proof marker)
- `backend/scripts/validate_project_shop_iap_integration_v1.py` (Track G validator)
- `docs/divine/179A_SHOP_IAP_SURFACE_REVALIDATION.md`
- `docs/divine/179B_SHOP_IAP_MOCK_PRODUCT_CATALOG.md`
- `docs/divine/179C_SHOP_IAP_UI_LOCK_PREVIEW_POLICY.md`
- `docs/divine/179D_SHOP_IAP_WALLET_LEDGER_FULFILLMENT_CONTRACT.md`
- `docs/divine/179E_SHOP_IAP_FUTURE_API_RECEIPT_CONTRACT.md`
- `docs/divine/179F_SHOP_IAP_RISK_COMPLIANCE_ROADMAP.md`
- `docs/divine/179_SHOP_IAP_INTEGRATION.md` (questo file)

### Modificati (solo comments + 1 tupla)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — header `PUBLIC_SYNC_TAG_RESYNC_v7` + sentinel inline + tupla `('PROJECT-SHOP-IAP-INTEGRATION', 'validate_project_shop_iap_integration_v1.py')`

---

## 🔄 Public Repo Sync Verification — PENDING

### Stato locale ✅
- Suite custom Python: **709/709 PASS**
- Master validator: **PASS**
- MD5 invarianti: ✅
- DB live: ✅ 0 write

### Azione richiesta all'utente
1. **Pannello Emergent → "Save to GitHub"**
2. Branch **`main`**
3. **PUSH**

### Su GitHub.com verifica:
- ✅ `data/design/shop_iap/` con tutti i 7 JSON (6 design + 1 proof marker)
- ✅ `backend/scripts/validate_project_shop_iap_integration_v1.py` presente
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` contiene:
  - `# PUBLIC_SYNC_TAG_RESYNC_v7: suite_runner_shop_iap_integration_v7_2026_05_29`
  - `# SHOP_IAP_INTEGRATION_REGISTRATION_SENTINEL`
  - `('PROJECT-SHOP-IAP-INTEGRATION', 'validate_project_shop_iap_integration_v1.py'),`
- ✅ `docs/divine/179_SHOP_IAP_INTEGRATION.md` + `179A..179F` presenti

Solo dopo questa verifica → **`PROJECT_SHOP_IAP_INTEGRATION_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_SHOP_IAP_INTEGRATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

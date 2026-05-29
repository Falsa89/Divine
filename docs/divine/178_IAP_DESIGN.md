# 178 — PROJECT IAP DESIGN — DIVINE WAIFUS

## Verdetto locale
**`PROJECT_IAP_DESIGN_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `PROJECT_IAP_DESIGN_COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo che l'utente ha eseguito **Save to GitHub → branch `main` → PUSH** e verificato manualmente la repo pubblica.

---

## Obiettivo (riassunto)
Definire il **design canonico** della monetizzazione/IAP di Divine Waifus, **senza** integrare alcuno store SDK, alcun receipt endpoint live, alcuna scrittura DB, alcun bottone d'acquisto live.

Lo Stage 8 Artifact canary apply resta **internal-only**: l'IAP non vi accede in nessun product family.

---

## Markers di approvazione
```
PROJECT_IAP_DESIGN_APPROVAL = true
PROJECT_ACCELERATION_MODE   = IAP_DESIGN_ONLY
```

---

## Track summary

| Track | Output JSON                                                                        | Output Doc                                                  | Verdict                                                                |
|-------|------------------------------------------------------------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------|
| **A** | `data/design/iap/iap_monetization_surface_audit_v1.json`                           | `docs/divine/178A_IAP_MONETIZATION_SURFACE_AUDIT.md`        | `TRACK_A_IAP_MONETIZATION_SURFACE_AUDIT_READY`                         |
| **B** | `data/design/iap/iap_taxonomy_product_families_v1.json`                            | `docs/divine/178B_IAP_TAXONOMY_PRODUCT_FAMILIES.md`         | `TRACK_B_IAP_TAXONOMY_PRODUCT_FAMILIES_READY`                          |
| **C** | `data/design/iap/iap_currency_wallet_contract_v1.json`                             | `docs/divine/178C_IAP_CURRENCY_WALLET_CONTRACT.md`          | `TRACK_C_IAP_CURRENCY_WALLET_CONTRACT_READY`                           |
| **D** | `data/design/iap/iap_compliance_security_receipt_architecture_v1.json`             | `docs/divine/178D_IAP_COMPLIANCE_SECURITY_RECEIPT_ARCHITECTURE.md` | `TRACK_D_IAP_COMPLIANCE_SECURITY_RECEIPT_ARCHITECTURE_READY` |
| **E** | `data/design/iap/iap_anti_p2w_economy_boundary_v1.json`                            | `docs/divine/178E_IAP_ANTI_P2W_ECONOMY_BOUNDARY.md`         | `TRACK_E_IAP_ANTI_P2W_ECONOMY_BOUNDARY_READY`                          |
| **F** | `data/design/iap/iap_future_implementation_gate_roadmap_v1.json`                   | `docs/divine/178F_IAP_FUTURE_IMPLEMENTATION_GATE_ROADMAP.md`| `TRACK_F_IAP_FUTURE_IMPLEMENTATION_GATE_ROADMAP_READY`                 |
| **G** | `data/design/iap/iap_suite_registration_proof_marker_v1.json` + validator `.py`   | (vedi sezione validator)                                    | `TRACK_G_IAP_DESIGN_VALIDATOR_READY`                                   |
| **H** | _(questo doc)_                                                                     | `docs/divine/178_IAP_DESIGN.md`                             | `TRACK_H_IAP_DESIGN_COMPLETION_READY`                                  |

---

## Audit surface (Track A) — riassunto
- 10 surface monetization frontend tutte classificate.
- 5 `locked`, 2 `preview-only`, 1 `redirect-only`, 2 `live functional` (gacha standard/elem/sel e Soul Forge — Soul Forge do_not_touch).
- 0 SDK pagamento in dipendenze.
- 0 route IAP/receipt nel backend.

## Taxonomy (Track B) — riassunto
- 8 famiglie autorizzate, 8 famiglie vietate.
- Naming `dw_<family>_<variant>_<size>_v1`. Real store IDs allocati solo allo Stage 2 della roadmap.

## Currency & wallet (Track C) — riassunto
- `divine_crystals_free` ≠ `divine_crystals_paid` (balance separati, FREE_FIRST).
- Conversione Crystals→Sigilli con conferma esplicita in banner (già approvata).
- Ledger append-only server-authoritative, idempotency key `<user>:<product>:<txid>`.
- Refund/revoke supportato; mai revocare gacha results spesi.

## Compliance & receipt (Track D) — riassunto
- Flussi iOS StoreKit / Android Google Play Billing design-only.
- Endpoint futuri: `POST /api/iap/verify_apple`, `POST /api/iap/verify_google`, refund webhooks.
- Fraud prevention, sandbox plan, compliance checklist (loot box odds disclosure inclusa).

## Anti-P2W & economy boundary (Track E) — riassunto
- 9 paid power tutti `false`.
- 4 premium gacha unlock tutti `false`.
- VIP limita a cosmetic/convenience + max 20% discount su crystal packs.
- BP limita a cosmetic + currency (no premium/targeted sigilli).
- Artifact IAP prohibition `strict=true`.
- No dark patterns. Pressure countdown ≥ 60s.

## Future implementation gate & roadmap (Track F) — riassunto
- 10 stage espliciti con marker, blockers, rollback.
- Stage 6 `INTERNAL_PURCHASE_FULFILLMENT_CANARY` replica pattern Stage 8 artifact (solo `sfqa@test.com` + `test@test.com`).

---

## Track G — Validator & suite registration

### Validator OPTIONAL
- File: `backend/scripts/validate_project_iap_design_v1.py`
- Tupla suite: `('PROJECT-IAP-DESIGN', 'validate_project_iap_design_v1.py')`
- Risultato: **PASS**

### Strategia tripled-sentinel anti stale-push
1. **Top sentinel header** in `run_hero_skill_kit_validator_suite.py`:
   ```
   # PUBLIC_SYNC_TAG_RESYNC_v6: suite_runner_iap_design_v6_2026_05_29
   ```
2. **Sentinella inline** sopra la riga di registrazione:
   ```
   # IAP_DESIGN_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
   ```
3. **Proof marker JSON** in directory separata:
   `data/design/iap/iap_suite_registration_proof_marker_v1.json`

### Suite runner — risultato finale
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel \
  --json-out /app/backend/reports/iap_design_suite_run.json
```
```
Overall: PASS  (pass=708, fail=0, miss=0)
EXIT=0
```
🎯 **708/708 PASS** (707 baseline post Stage 8 + 1 nuovo IAP-DESIGN validator).

---

## 🔐 MD5 Invarianti (FINALI, confermati)

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅ UNCHANGED (no secret injection)
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅ UNCHANGED
```

### Frontend lock verificati
- `frontend/app/shop.tsx` → `SHOP_LOCKED_V2 = true` ✅
- `frontend/app/item-shop.tsx` → `ITEM_SHOP_LOCKED_V2 = true` ✅
- `frontend/app/battlepass.tsx` → `BP_LOCKED_V2 = true`, `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `frontend/app/vip.tsx` → `VIP_LOCKED_V2 = true` ✅
- Soul Forge → MD5 invariato `b7659de11ac36f341e7a2f54fd29e6ed`, `do_not_touch`

---

## ❌ Conferma scope NON violato

| Categoria                                       | Status |
|-------------------------------------------------|--------|
| StoreKit runtime                                | ❌ no  |
| Google Play Billing runtime                     | ❌ no  |
| RevenueCat / 3rd-party SDK                      | ❌ no  |
| Real product IDs in code                        | ❌ no  |
| Live purchase buttons                           | ❌ no  |
| Receipt endpoint live                           | ❌ no  |
| Purchase fulfillment live                       | ❌ no  |
| DB writes                                       | ❌ 0   |
| Gacha rate changes                              | ❌ no  |
| Premium/Targeted unlock                         | ❌ no  |
| Artifact/Constellation unhide                   | ❌ no  |
| Pity changes                                    | ❌ no  |
| Paid artifact power                             | ❌ no  |
| Soul Forge changes                              | ❌ no  |
| `battle_engine` / `battle_core` changes         | ❌ no  |
| Character Bible mutation                        | ❌ no  |
| Wallet/economy live changes                     | ❌ no  |
| Shop live purchases                             | ❌ no  |
| VIP / Battle Pass live                          | ❌ no  |
| `.env` secrets                                  | ❌ no  |
| REQUIRED validator weakening                    | ❌ no  |
| fake PASS                                       | ❌ no  |

---

## 📦 File creati / modificati

### Nuovi
- ✅ `data/design/iap/iap_monetization_surface_audit_v1.json` (Track A)
- ✅ `data/design/iap/iap_taxonomy_product_families_v1.json` (Track B)
- ✅ `data/design/iap/iap_currency_wallet_contract_v1.json` (Track C)
- ✅ `data/design/iap/iap_compliance_security_receipt_architecture_v1.json` (Track D)
- ✅ `data/design/iap/iap_anti_p2w_economy_boundary_v1.json` (Track E)
- ✅ `data/design/iap/iap_future_implementation_gate_roadmap_v1.json` (Track F)
- ✅ `data/design/iap/iap_suite_registration_proof_marker_v1.json` (Track G proof marker)
- ✅ `backend/scripts/validate_project_iap_design_v1.py` (Track G validator)
- ✅ `docs/divine/178A_IAP_MONETIZATION_SURFACE_AUDIT.md`
- ✅ `docs/divine/178B_IAP_TAXONOMY_PRODUCT_FAMILIES.md`
- ✅ `docs/divine/178C_IAP_CURRENCY_WALLET_CONTRACT.md`
- ✅ `docs/divine/178D_IAP_COMPLIANCE_SECURITY_RECEIPT_ARCHITECTURE.md`
- ✅ `docs/divine/178E_IAP_ANTI_P2W_ECONOMY_BOUNDARY.md`
- ✅ `docs/divine/178F_IAP_FUTURE_IMPLEMENTATION_GATE_ROADMAP.md`
- ✅ `docs/divine/178_IAP_DESIGN.md` (questo file)

### Modificati (solo comments + 1 tupla)
- 🔧 `backend/scripts/run_hero_skill_kit_validator_suite.py` — header `PUBLIC_SYNC_TAG_RESYNC_v6` + sentinel inline `IAP_DESIGN_REGISTRATION_SENTINEL` + tupla `('PROJECT-IAP-DESIGN', 'validate_project_iap_design_v1.py')`

### Non modificati (esplicitamente)
- `backend/battle_engine.py`
- `backend/.env`
- `backend/routes/artifacts.py`
- `backend/routes/economy.py`, `items.py`, e tutti gli altri route backend
- `frontend/app/soul-forge.tsx`
- `frontend/app/(tabs)/gacha.tsx`
- `frontend/app/shop.tsx`, `item-shop.tsx`, `battlepass.tsx`, `vip.tsx`, `treasury.tsx`, `economy.tsx`, `exclusive.tsx`, `cosmetics.tsx`
- Tutti i file in `data/design/artifacts/`
- Character Bible / hero stats / kits

---

## 🔄 Public Repo Sync Verification — PENDING (azione utente)

### Stato locale ✅
- Suite custom Python: **708/708 PASS**
- IAP design master validator: **PASS**
- MD5 invarianti: ✅ tutti rispettati
- DB live: ✅ 0 write
- Surface lock: ✅ tutti attivi
- Lock token check: ✅ tutti presenti

### Azione richiesta all'utente
1. **Pannello Emergent → "Save to GitHub"**
2. Branch **`main`**
3. **PUSH**

### Verifica manuale su GitHub.com
- ✅ `data/design/iap/` contiene tutti i 7 JSON (6 design + 1 proof marker)
- ✅ `backend/scripts/validate_project_iap_design_v1.py` presente
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` contiene:
  - top sentinel: `# PUBLIC_SYNC_TAG_RESYNC_v6: suite_runner_iap_design_v6_2026_05_29`
  - inline sentinel: `# IAP_DESIGN_REGISTRATION_SENTINEL`
  - tupla: `('PROJECT-IAP-DESIGN', 'validate_project_iap_design_v1.py')`
- ✅ `docs/divine/178_IAP_DESIGN.md` + tutti i sub-doc 178A..178F presenti

Solo dopo questa verifica manuale → **`PROJECT_IAP_DESIGN_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_IAP_DESIGN_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

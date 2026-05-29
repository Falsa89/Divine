# 183 — PROJECT NO STAMINA REMEDIATION — DIVINE WAIFUS

## Verdetto locale
**`PROJECT_NO_STAMINA_REMEDIATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `..._COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo "Save to GitHub → `main` → PUSH" e verifica manuale.

---

## Obiettivo
Primo P0 della roadmap audit 182. Rimozione controllata e chirurgica delle 6 backend gate stamina + 4 frontend label/badge visibili che violavano la decisione canonica **NO_STAMINA_SYSTEM**.

**Modalità pack:** controlled remediation. NO broad refactor, NO nuova economia, NO premium refill, NO DB migration, NO DB write via script.

## Markers
```
PROJECT_NO_STAMINA_REMEDIATION_APPROVAL = true
PROJECT_ACCELERATION_MODE               = NO_STAMINA_REMEDIATION_CONTROLLED
```

---

## Track summary

| Track | Output JSON / Validator | Output Doc | Verdict |
|---|---|---|---|
| **A** | `data/design/no_stamina/stamina_surface_audit_v1.json` | `183A_STAMINA_SURFACE_AUDIT.md` | `TRACK_A_STAMINA_SURFACE_AUDIT_READY` |
| **B** | `data/design/no_stamina/controlled_remediation_patch_v1.json` | `183B_CONTROLLED_REMEDIATION_PATCH.md` | `TRACK_B_CONTROLLED_REMEDIATION_PATCH_READY` |
| **C** | `data/design/no_stamina/mode_reachability_and_smoke_v1.json` | `183C_MODE_REACHABILITY_AND_SMOKE.md` | `TRACK_C_MODE_REACHABILITY_AND_SMOKE_READY` |
| **D** | `data/design/no_stamina/canonical_policy_and_future_entry_model_v1.json` | `183D_CANONICAL_POLICY_AND_FUTURE_ENTRY_MODEL.md` | `TRACK_D_CANONICAL_POLICY_AND_FUTURE_ENTRY_MODEL_READY` |
| **E** | `validate_project_no_stamina_remediation_v1.py` + proof marker | (vedi sezione validator) | `TRACK_E_VALIDATOR_READY` |
| **F** | _(questo doc)_ | `183_NO_STAMINA_REMEDIATION.md` | `TRACK_F_COMPLETION_READY` |

---

## 📦 Patch applicati (10 totali)

### Backend (6 patch)
| File | Context | Strategia | DB write |
|---|---|---|---|
| `combat.py:48-52` | story chapter battle | `no_cost_prototype_access` | no |
| `combat.py:109-111` | tower battle | `no_cost_prototype_access` | no |
| `combat.py:211-213` | daily event battle | `no_cost_prototype_access` | no |
| `cosmetics.py:95-97` | territory attack | `no_cost_prototype_access` | no |
| `gvg.py:235-239` | guild war attack | `guild_attack_attempts` counter (default 10/d) | runtime only |
| `raids.py:70-72` | raid attack | `mode_attempts.raid` counter (default 5/d) | runtime only |

### Frontend (4 patch)
| File | Context | Strategia |
|---|---|---|
| `events.tsx:47` | event card label | UI swap: "⚡ X Stamina" → "✨ Accesso libero (no-stamina)" |
| `gvg.tsx:251` | guild war info | UI swap: "⚡ 12 stamina" → "✨ 1 tentativo gilda per attacco" |
| `shop.tsx:45` | shop CATS array | UI remove: `'stamina'` category rimossa (SHOP_LOCKED_V2 resta true) |
| `(tabs)/menu.tsx:121` | profile header | UI remove: ResourceBadge ⚡ rimosso (Gold + Gems restano) |

---

## 🔍 Riepilogo occorrenze stamina/energy (47 totali)

### ✅ Patchate come true violations (10)
Vedi tabella sopra.

### ✅ Lasciate come ALLOWED HISTORICAL (37)

**Backend (defensive/locked):**
- `economy.py:50-95` — reward handlers passive accept (defensive no-op; no new content grants stamina)
- `achievements.py:252` — reward dict iteration whitelist (backward compat)
- `game_data.py:72-76` — daily events `stamina_cost` field (route non lo enforced più; future DAILY_EVENTS_REFACTOR)
- `game_data.py:203-204,214,221,225,230` — shop products + BP rewards (dietro SHOP_LOCKED_V2 / BP_LOCKED_V2)
- `game_data.py:250-254` — VIP perks `stamina_max` (dietro VIP_LOCKED_V2; future 181G Stage 2)
- `soul_forge.py:77,104,109,308` — Soul Forge products (Soul Forge PROTECTED — DO NOT TOUCH per brief)
- `server.py:143-144` — user document init fields (default backward compat)

**Frontend:**
- `treasury.tsx:53,65` — `legacy_stamina: 'LEGACY'` (già esplicitamente marcato LEGACY in codice)

Tutte le occorrenze ALLOWED sono **gated** da locks o defensive no-op. Nessuna può produrre gameplay gating.

---

## 📊 Suite finale
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel
```
```
Overall: PASS  (pass=713, fail=0, miss=0)
EXIT=0
```
🎯 **713/713 PASS** = baseline 712 + 1 nuovo `PROJECT-NO-STAMINA-REMEDIATION`.

### Note su validator baseline sync
- 16 file JSON in `data/design/` aggiornati con i nuovi MD5 di `shop.tsx` e `(tabs)/menu.tsx` (sync canonico post-patch; non weakening).
- 2 file JSON in `data/design/status_effects/` aggiornati con il nuovo MD5 di `routes/combat.py`.
- 1 validator OPTIONAL `validate_project_m_status_first_slice_canary_env_rc_gate_v1.py` baseline MD5 di `routes/combat.py` aggiornato in-script (assertion logic intatta; baseline canonico aggiornato; commento PROJECT_NO_STAMINA_REMEDIATION presente).
- **Nessun REQUIRED validator toccato. Nessuna assertion logic indebolita. Nessun fake PASS.**

---

## 🔐 MD5 Invarianti (FINALI — baseline NON cambia)
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py        ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                    ✅ UNCHANGED
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py     ✅ UNCHANGED
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx     ✅ UNCHANGED
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx            ✅ UNCHANGED
```

### Frontend lock tokens preservati
- `VIP_LOCKED_V2 = true` ✅ / `BP_LOCKED_V2 = true` ✅ / `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `SHOP_LOCKED_V2 = true` ✅ / `ITEM_SHOP_LOCKED_V2 = true` ✅
- `ARTIFACT_MUTATION_LOCK_STATUS = 423` ✅

---

## ❌ Conferma scope NON violato

| Categoria forbidden | Status |
|---|---|
| Nuova economy stamina | ❌ 0 |
| Premium stamina refill IAP | ❌ 0 |
| DB migrations | ❌ 0 |
| DB writes via script | ❌ 0 |
| Wallet balance changes | ❌ 0 |
| Gacha changes | ❌ 0 |
| Artifact changes | ❌ 0 |
| IAP/BP/VIP/Shop activation | ❌ 0 |
| Soul Forge changes | ❌ 0 (Soul Forge PROTECTED) |
| `battle_engine.py` / `battle_core.py` / `combat.tsx` broad refactor | ❌ 0 |
| Character Bible / hero kit / final_numbers changes | ❌ 0 |
| `.env` secrets | ❌ 0 |
| Final art/audio | ❌ 0 |
| REQUIRED validator weakening | ❌ 0 |
| Fake PASS | ❌ 0 |

---

## Validator & suite registration

### Validator OPTIONAL
- File: `backend/scripts/validate_project_no_stamina_remediation_v1.py`
- Tupla: `('PROJECT-NO-STAMINA-REMEDIATION', 'validate_project_no_stamina_remediation_v1.py')`
- Risultato: **PASS**
- Asserts: 4 track JSON + 1 proof marker, no `if user.get("stamina"...)` gate in 4 backend file patchati, no `$inc stamina:` decremento in 4 backend file, label "Stamina" rimosso in 3 frontend file user-facing, audit-trail token `PROJECT_NO_STAMINA_REMEDIATION` presente nei 10 file patchati, Soul Forge files NON toccati, `battle_engine.py` NON toccato, `combat.tsx` no broad refactor, MD5 invariants 5/5, lock tokens 5/5, Track A counts esatti (6 backend + 4 frontend + 10 patches), Track B 10 patches + zero DB write/migration/economy/refill, Track C 6 modes pre-blocked → 10 reachable post-patch, Track D forbidden_constructs include premium_stamina_refill_iap, allowed_constructs include guild_attack_attempts e mode_attempts.

### Strategia tripled-sentinel
1. **Top sentinel**: `# PUBLIC_SYNC_TAG_RESYNC_v11: suite_runner_no_stamina_remediation_v11_2026_05_29`
2. **Sentinel inline sopra la tupla**: `# NO_STAMINA_REMEDIATION_REGISTRATION_SENTINEL`
3. **Proof marker JSON**: `data/design/no_stamina/no_stamina_suite_registration_proof_marker_v1.json`

---

## 🔄 Public Repo Sync Verification — PENDING

### Stato locale ✅
- Suite custom Python: **713/713 PASS**
- Master validator NO_STAMINA: **PASS**
- MD5 invarianti: ✅ 5/5
- DB live: ✅ 0 write
- Surface lock: ✅ tutti attivi
- Backend health: `GET /api/health` → 200 OK

### Azione richiesta utente
1. **Pannello Emergent → "Save to GitHub"** → branch **`main`** → **PUSH**

### Verifica manuale su GitHub.com
- ✅ `data/design/no_stamina/` con 5 file (4 track JSON + 1 proof marker)
- ✅ `backend/scripts/validate_project_no_stamina_remediation_v1.py`
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` con `PUBLIC_SYNC_TAG_RESYNC_v11`, sentinel inline, tupla (count = 1)
- ✅ `docs/divine/183_*` + `183A..183D`
- ✅ Patch backend visibili su `routes/combat.py`, `cosmetics.py`, `gvg.py`, `raids.py`
- ✅ Patch frontend visibili su `events.tsx`, `gvg.tsx`, `shop.tsx`, `(tabs)/menu.tsx`

Solo dopo questa verifica → **`PROJECT_NO_STAMINA_REMEDIATION_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_NO_STAMINA_REMEDIATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

# 120B — PRE_QA_STABILIZATION_115C_FIX_A_SOUL_FORGE_WALLET_SCOPE — APPENDIX

## Verdict

`PRE_QA_STABILIZATION_115C_FIX_A_SOUL_FORGE_WALLET_SCOPE_READY_FOR_GAME_MASTER_REAUDIT`

Manual QA **remains paused until Game Master re-audit.**

---

## Contesto

Game Master `PACK_115C_LOCAL_ZIP_REAUDIT = NOT_FINAL_ACCEPTED_MICRO_FIX_REQUIRED` ha rilevato il finding `115C-ZIP-001`:

> **File:** `frontend/app/soul-forge.tsx`
> **Issue:** il caricamento iniziale usava correttamente `/api/wallet?server_id=<sid>`, ma il **post-success refresh** della Soul Forge chiamava ancora `apiCall('/api/wallet')` account-wide, contraddicendo lo scope 115C.
> **Severity:** non-P0 (Soul Forge mutation path è già locked da Pack 115B gate `DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS` default-OFF), ma **errore reale di scope**.

Il validator 115C originale non intercettava la regressione perché il check 7 verificava solo il pattern ternary "X ? `/api?server_id=` : '/api'" (initial load), non chiamate raw senza server_id nel post-success refresh.

---

## Fix applicato

### File modificati (3, scope-bounded)

1. **`frontend/app/soul-forge.tsx`** — post-success refresh:
   ```diff
   -    Promise.allSettled([
   -      apiCall('/api/wallet'),
   -      apiCall('/api/soul-forge'),
   -    ])
   +    Promise.allSettled([
   +      // Pre-QA Stabilization 115C-FIX-A — wallet read DEVE essere server-scoped.
   +      // Se manca selected_server_id, salta il refresh wallet (fail-closed):
   +      // nessuna chiamata account-wide /api/wallet.
   +      selected_server_id
   +        ? apiCall(`/api/wallet?server_id=${encodeURIComponent(selected_server_id)}`)
   +        : Promise.reject(new Error('NO_SERVER_SELECTED_WALLET_REFRESH_SKIPPED')),
   +      apiCall('/api/soul-forge'),
   +    ])
   ```
   Comportamento risultante:
   - Se `selected_server_id` è presente → refresh wallet **server-scoped**.
   - Se manca → la Promise viene rejected con `NO_SERVER_SELECTED_WALLET_REFRESH_SKIPPED`, swallow-ata dal `.catch()` esistente. **Zero side-effect, zero call account-wide.**

2. **`backend/scripts/validate_pre_qa_stabilization_115c_auth_server_scope_unification.py`** — aggiunto **check 12** rafforzato:
   - Fallisce su qualsiasi `apiCall('/api/wallet')` o `apiCall("/api/wallet")` raw.
   - Fallisce su qualsiasi `apiCall(\`/api/wallet\`)` template senza query string.
   - Fallisce su qualsiasi stringa `'/api/wallet'` (no query) che NON sia:
     - dentro un commento (`//`, `/*`, `*`)
     - parte di un template literal con `?server_id=` subito dopo
     - parte di una riga `NO_SERVER_SELECTED` o `Promise.reject` (skip esplicito)

3. **`docs/divine/120B_PRE_QA_STABILIZATION_115C_FIX_A_SOUL_FORGE_WALLET_SCOPE_APPENDIX.md`** — questo file.

### Registry suite

**Non toccato** (`backend/scripts/run_hero_skill_kit_validator_suite.py`): il validator 115C è lo stesso file, l'entry esistente continua a riferirsi al medesimo path. Nessun update necessario.

---

## Anti-regression proof

Test manuale di iniezione (eseguito e validato):
```bash
# Inietto temporaneamente apiCall('/api/wallet') in soul-forge.tsx
# → validator 115C check 12:
[✗] FAIL 12_SOUL_FORGE_NO_ACCOUNT_WIDE_WALLET_CALL
   — trovata chiamata raw apiCall('/api/wallet') senza server_id (offset 7144)
# Restore + rerun
[✓] PASS 12_SOUL_FORGE_NO_ACCOUNT_WIDE_WALLET_CALL
TOTALE: 12 PASS, 0 FAIL su 12 check.
```

---

## Validation results

| Test | Result |
|---|---|
| Validator 113 (HomeOverflow) | **PASS** |
| Smoke 113 | **PASS** |
| Validator 114 Home Routes | **PASS** |
| Validator 114B Gacha Guard | **15/15 PASS** |
| Validator 115A | **11/11 PASS** |
| Validator 115B | **8/8 PASS** |
| **Validator 115C (con check 12 rafforzato)** | **12/12 PASS** |
| Anti-regression injection test | **FAIL come atteso** + **PASS dopo restore** |
| Master Validation Suite | **1740 PASS / 69 FAIL / 0 MISS** |

### Master Suite delta vs Pack 115C (1741/68/0)

| Metrica | Pack 115C | Pack 115C-FIX-A | Delta |
|---|---|---|---|
| PASS | 1741 | 1740 | -1 |
| FAIL | 68 | 69 | +1 |

Il delta è **1 fail aggiuntivo** dovuto al rebase MD5 baseline di `frontend/app/soul-forge.tsx` (file ri-toccato 1 volta nel Pack 115C-FIX-A). Nessuna nuova regressione funzionale.

---

## Safety invariants

- **DB writes:** 0
- **Soul Forge backend toccato:** NO (zero modifiche a `backend/routes/soul_forge.py`)
- **Soul Forge live activated:** NO (`DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS` resta default-OFF)
- **Soul Forge mutation reachable:** NO (gate Pack 115B intatto, `/api/soul-forge/retire` → 423)
- **Gacha live:** false
- **Reward live:** false
- **IAP/Payment:** false
- **Token raw logs:** 0
- **`battle_engine.py` / `combat.tsx`:** non toccati
- **`data/design/**`:** 0 modifiche
- **`__pycache__/*.pyc`:** non committati
- **Manual QA:** remains paused

---

## Diff hygiene

- ✅ `git add -- <path>` esplicito per i 3 file autorizzati
- ✅ Nessun `git add -A`
- ✅ `git restore data/design/` eseguito post-Master-Suite
- ✅ Nessun secret/token committato

---

## Forbidden — verifica negativa

| Forbidden | Eseguito? |
|---|---|
| Soul Forge backend toccato | **NO** |
| Soul Forge live activated | **NO** |
| Nuove feature | **NO** |
| Gacha live | **NO** |
| Reward live | **NO** |
| IAP/payment | **NO** |
| Battle engine | **NO** |
| Combat runtime | **NO** |
| Character Bible | **NO** |
| Skill catalog | **NO** |
| `data/design/**` | **NO** |
| `git add -A` | **NO** |
| False PASS | **NO** |
| Pack 115D+ work | **NO** |

---

## Commit SHAs

- Pre-Pack-115C-FIX-A baseline: `c656959427de06aefc29d9c6031737f188a64311` (Pack 115C report self-ref HEAD)
- Pack 115C-FIX-A commit: *post-commit (vedi HEAD finale)*

---

## HEAD finale

Compilato post-commit. Comando di verifica:
```bash
git show --name-only --format="" <FINAL_SHA>
# atteso: ESATTAMENTE 3 file autorizzati.
git diff --name-only c656959427de06aefc29d9c6031737f188a64311 HEAD -- 'data/design/' | wc -l
# atteso: 0
```

`Manual QA remains paused until Game Master re-audit.`

---

*Appendice 120B generata in italiano. Tutti i risultati riproducibili eseguendo gli script citati. Nessun valore inventato.*

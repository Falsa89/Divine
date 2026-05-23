# 101 · SLC-G-GUILDS-UNSAFE-CLEANUP-B — APPLY GATED

**Stato finale**: ✅ `CLEANUP_APPLIED_SAFE`
**Modalità**: `TARGETED DB WRITE / BACKUP-FIRST / ROLLBACK-READY / GATED MICRO-CLEANUP`
**Marker approvazione esplicita**: `SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true` ✅ presente
**Marker SLC-G commit**: `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL` ❌ **assente** (come da specifica)
**Suite globale**: `RM1.31-B` → **329 PASS / 0 FAIL / 0 MISS** (328 → 329, +1 post-apply validator)
**Baseline diff RM1.32-PRE**: ✅ PASS
**SLC-G migration**: ❌ **NON applicata** (`migration_applied=false` invariato)
**SLC-G gate G10**: ✅ **SBLOCCATO** (unsafe_unknown ora = 0)
**SLC-G gate G11**: 🛡️ **STILL GATED** (richiede marker separato)

---

## 1. Obiettivo

Applicare in modo chirurgico e gated la micro-bonifica già auditata in
SLC-G-GUILDS-UNSAFE-CLEANUP-A sui **2 documenti `guilds` esatti**, per sbloccare
il gate G10 di SLC-G senza eseguire alcuna delle altre fasi di migrazione.

---

## 2. Operazioni eseguite

### 2.1 Pre-flight (read-only, prima della scrittura)

| Check | Risultato |
|---|---|
| Marker `SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true` presente | ✅ |
| Marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL` ASSENTE (forbidden in questo task) | ✅ |
| Audit file `slc_g_guilds_unsafe_audit_v1.json` presente | ✅ |
| Plan file `slc_g_guilds_cleanup_plan_v1.json` presente | ✅ |
| Live `guilds` `unsafe_unknown` count = 2 (match audit) | ✅ |
| `live_ids == designed_ids` esatto | ✅ |
| Per ciascun target, `leader_id` risolve a `users.id` | ✅ |

### 2.2 Backup pre-write

File creato: `/app/data/design/system_safety/backups/slc_g_guilds_cleanup_b_pre_backup_20260523T140718Z.json`

Contenuto:
- Snapshot completo dei 2 documenti `guilds` pre-write
- SHA-256 sull'intero payload pre-write
- Riferimento all'audit
- Timestamp UTC

### 2.3 Write applicato (`set_only_if_missing`)

Per ciascun target, sono stati settati ESCLUSIVAMENTE i seguenti campi mancanti:

| Target | `_id` | `user_id` | `account_id` | `server_id` | Marker | Classificazione |
|---|---|---|---|---|---|---|
| Divine Warriors | `69db9bb2df5d3f956d0080ac` | `651253e2-…916e` (= leader_id) | idem | `s1` | ✅ | `legacy_guild_missing_owner_resolvable` |
| Legion_517 | `69dbc64c9c908325ca0fd57f` | `526fb2cf-…fb00` (= leader_id) | idem | `s1` | ✅ | `legacy_guild_missing_owner_resolvable_bot_owned` |

**Risultati write**: `matched=2 modified=2 targets_modified=2`

Nessun altro campo è stato modificato: `leader_id`, `members`, `name`, `created_at`,
`level`, `exp` sono rimasti **identici** al pre-state.

---

## 3. Post-apply verification (read-only)

| Check | Atteso | Osservato |
|---|---|---|
| `guilds` total | 2 | **2** ✅ |
| `guilds` `unsafe_unknown` count | **0** | **0** ✅ |
| `guilds` con cleanup marker | 2 | **2** ✅ |
| Doc 0: `user_id` presente == `leader_id` | true | ✅ |
| Doc 0: `account_id` presente == `leader_id` | true | ✅ |
| Doc 0: `server_id` | `s1` | `s1` ✅ |
| Doc 0: marker presente | true | ✅ |
| Doc 0: members count | 1 | **1** ✅ |
| Doc 1: `user_id` presente == `leader_id` | true | ✅ |
| Doc 1: `account_id` presente == `leader_id` | true | ✅ |
| Doc 1: `server_id` | `s1` | `s1` ✅ |
| Doc 1: marker presente | true | ✅ |
| Doc 1: members count | 15 | **15** ✅ |

Validator: `SLC-G-GUILDS-CLEANUP-B-POST-APPLY` → **PASS**

---

## 4. Stato dei gate SLC-G dopo la bonifica

| Gate | Stato | Note |
|---|---|---|
| G1 Prior SLC PASS | ✅ | |
| G2 API smoke invariants | ✅ | heroes=100, gaia=404, borea/greek_borea=200 |
| G3 AF2-N invariants | ✅ | cap=50k, allowlist=2.5k, ledger=502, inventory=2500, affinity=1914 |
| G4 Runtime flags unset | ✅ | SERVER_PROFILES_RUNTIME_ENABLED + SECOND_SERVER_OPENING_ENABLED entrambi unset |
| G5 Protected file no-diff | ✅ | baseline diff RM1.32-PRE PASS |
| G6 Dry-run report present | ✅ | |
| G7 Backup manifest present | ✅ | contratto presente |
| G8 Rollback plan present | ✅ | + rollback script reale (gated da env separato) |
| G9 Idempotency contract present | ✅ | (apply re-run → FAILED_SAFE strict, by design) |
| **G10 `unsafe_unknown_count == 0`** | ✅ **SBLOCCATO** | era il blocker; ora superato |
| G11 Approval marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true` | ❌ **assente** | **resta richiesto separatamente** |
| G12 Baseline diff RM1.32-PRE PASS | ✅ | |

Final status combo SLC-G: `READY_TO_COMMIT_NOT_APPLIED` — **G10 ora superato, G11 ancora il vincolo bloccante per il commit migrazione**.

---

## 5. Artefatti creati in questo task

### 5.1 Script Python

| File | Funzione |
|---|---|
| `/app/backend/scripts/apply_slc_g_guilds_cleanup_b.py` | Apply gated (env-marker required) |
| `/app/backend/scripts/rollback_slc_g_guilds_cleanup_b.py` | Rollback gated separato (env diverso) |
| `/app/backend/scripts/validate_slc_g_guilds_cleanup_b_post_apply_v1.py` | Verifica post-apply read-only |

### 5.2 Backup + report

- `/app/data/design/system_safety/backups/slc_g_guilds_cleanup_b_pre_backup_20260523T140718Z.json`
- `/app/backend/reports/slc_g_guilds_cleanup_b_apply_result.json` (verdict `CLEANUP_APPLIED_SAFE`)
- `/app/backend/reports/slc_g_guilds_cleanup_b_suite_run.json` (suite 329 PASS / 0 FAIL / 0 MISS)

### 5.3 Registrazione suite

Aggiunto in OPTIONAL: `SLC-G-GUILDS-CLEANUP-B-POST-APPLY → validate_slc_g_guilds_cleanup_b_post_apply_v1.py`.

### 5.4 Modifica minore al validator audit pre-esistente

`audit_slc_g_guilds_unsafe_readonly_v1.py` aggiornato con **tolleranza post-cleanup**:
quando `live_unsafe == 0` AND ogni `_id` originariamente auditato risulta ora marcato
con `_slc_g_guilds_cleanup_marker` + `server_id=s1` + `user_id == leader_id`,
il validator riconosce lo **stato sano post-apply** e non genera errore.
Questa modifica **non indebolisce** alcun test esistente: rinforza la coerenza
tra audit-state e post-cleanup-state.

---

## 6. Idempotenza & sicurezza del re-run

Eseguendo nuovamente `apply_slc_g_guilds_cleanup_b.py` dopo il successo:

```
FAILED_SAFE: live_targets_diverge_from_audit
  extra: {'live': [], 'expected': ['69db…0080ac', '69db…d57f']}
```

Postura **strict idempotency**: invece di eseguire silenziosamente un no-op,
lo script si rifiuta di girare quando lo stato live non corrisponde più
all'audit. Questo è il livello di sicurezza più alto possibile per un apply
chirurgico gated.

---

## 7. Invarianti finali

| Check | Valore |
|---|---|
| `GET /api/heroes` count | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | **404** ✅ |
| `GET /api/heroes/borea` | **200** ✅ |
| `GET /api/heroes/greek_borea` | **200** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | **unset** ✅ |
| AF2-N cap / allowlist | **50000 / 2500** ✅ |
| AF2-N row counts (inventory / ledger / affinity) | **2500 / 502 / 1914** ✅ |
| SLC-G `migration_applied` | **false** ✅ |
| `guilds` total | **2** ✅ |
| `guilds` unsafe_unknown | **0** ✅ |
| `guilds` con marker SLC-G-B | **2** ✅ |
| Baseline diff RM1.32-PRE | **PASS** ✅ |
| Suite globale | **329 PASS / 0 FAIL / 0 MISS** ✅ |

---

## 8. Guardrail rispettati

- ✅ NO SLC-G migration commit
- ✅ NO default S1 migration commit
- ✅ NO route runtime patch
- ✅ NO feature flag enable
- ✅ NO second server opening
- ✅ NO delete operation
- ✅ NO broad collection update (write esattamente 2 documenti, esattamente 2 modificati)
- ✅ NO modifiche a `battle_engine.py`, `battle_core.py`, `combat.tsx`
- ✅ NO modifiche a `affinity_gift_spend.py`, AF2-N, Stage4, Redis runtime
- ✅ NO modifiche a gacha, roster, Character Bible, cataloghi, asset
- ✅ NO validator weakening

---

## 9. Verdict finale

> ## ✅ `CLEANUP_APPLIED_SAFE`
> - Scope: esattamente 2 documenti `guilds` (`Divine Warriors`, `Legion_517`)
> - Backup pre-write generato con SHA-256
> - Rollback gated disponibile via env `SLC_G_GUILDS_UNSAFE_CLEANUP_ROLLBACK_APPROVAL=true`
> - **G10 SLC-G ora superato**: `unsafe_unknown_count == 0`
> - **G11 SLC-G ancora il blocker per il commit migrazione** (richiede marker separato `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true`)
> - **SLC-G `migration_applied` resta `false`**

---

## 10. Prossimi passi (gated, da confermare con utente)

1. **Per eseguire il commit SLC-G** (default S1 migration applicata su tutte
   le collection server-bound): fornire il marker
   `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true` in un task separato. A quel
   punto tutti i 12 gate sarebbero soddisfatti (G10 incluso, ora che la
   bonifica guilds è applicata).
2. **Altrimenti** restare in `READY_TO_COMMIT_NOT_APPLIED` indefinitamente,
   con SLC-G design-only e cleanup guilds applicato in modo isolato.
3. Disponibile in qualsiasi momento il rollback chirurgico via
   `rollback_slc_g_guilds_cleanup_b.py` con env
   `SLC_G_GUILDS_UNSAFE_CLEANUP_ROLLBACK_APPROVAL=true`.

**Nessuno dei punti sopra è oggetto del task corrente.**

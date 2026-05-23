# 100 · SLC-G-GUILDS-UNSAFE-CLEANUP-A — AUDIT & PIANO DI BONIFICA GATED

**Stato finale**: ✅ `READY_TO_CLEANUP_NOT_APPLIED`
**Modalità**: `READ-ONLY FIRST / GATED CLEANUP PLAN`
**Approvazione esplicita utente**: ❌ marker `SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true` **NON presente** nel prompt → nessuna scrittura DB eseguita
**Suite globale**: `RM1.31-B` → **328 PASS / 0 FAIL / 0 MISS** (323 → 328, +5 SLC-G-GUILDS-CLEANUP OPTIONAL)
**SLC-G migrazione**: **NON applicata** (resta `READY_TO_COMMIT_NOT_APPLIED`)

---

## 1. Obiettivo

Chiudere in modo sicuro il blocker **G10** di SLC-G (`unsafe_unknown_count == 0`)
provocato da 2 documenti in `guilds` che la dry-run di SLC-G aveva classificato
`unsafe_unknown` perché privi di `user_id` e `account_id`.

Questo task è **READ-ONLY**: produce solo audit, piano di cleanup, gate contract,
rollback plan e validator. Nessuna scrittura DB viene eseguita in assenza del
marker esplicito.

---

## 2. Risultato dell'audit live (READ-ONLY)

L'audit ha trovato **esattamente 2 documenti unsafe** in `guilds`. Entrambi i
documenti possiedono però un **`leader_id`** che è risolvibile contro la
collection `users` (chiave `users.id`).

| # | `_id` | Nome (red.) | Member count | `leader_id` → user | Tipo proprietario |
|---|---|---|---|---|---|
| 0 | `69db9bb2df5d3f956d0080ac` | Divine Warriors | 1 | `TestPlayer` | **human** (account reale, in tutorial) |
| 1 | `69dbc64c9c908325ca0fd57f` | Legion_517 | 15 | `OnyxShadow965` | **bot** (`is_bot=true`) |

Entrambi sono stati riclassificati: **NON sono veri orfani**. La SLC-G dry-run
li aveva marcati `unsafe_unknown` solo perché controllava `user_id` e `account_id`
ma non `leader_id` (la convenzione legacy single-shard storica).

### 2.1 Classificazioni assegnate

| Documento | Classificazione | Note |
|---|---|---|
| Divine Warriors | `legacy_guild_missing_owner_resolvable` | owner umano in tutorial |
| Legion_517 | `legacy_guild_missing_owner_resolvable_bot_owned` | owner bot di seed |

**Nessun documento è stato marcato `unsafe_do_not_touch`**: entrambi hanno
proprietario provabile e sicuro da risolvere via `leader_id`.

---

## 3. Piano di cleanup proposto (NON applicato)

Per ciascuno dei 2 documenti, set-only-if-missing dei seguenti campi:

| Campo | Valore | Override esistente? |
|---|---|---|
| `user_id` | `leader_id` (copia) | **mai** |
| `account_id` | `leader_id` (copia) | **mai** |
| `server_id` | `s1` | **mai** |
| `_slc_g_guilds_cleanup_marker` | `true` | (marker per rollback) |
| `_slc_g_guilds_cleanup_classification` | la classificazione assegnata | (marker per rollback) |

**Constraint di sicurezza assoluti** (validati):
- Solo i 2 `_id` target possono essere toccati
- Solo se il campo è assente
- Mai delete, mai drop collection, mai drop index
- Mai modifica di `leader_id`, `members`, `name`, `created_at`, `level`, `exp`
- Mai modifica a AF2-N (inventory/ledger/affinity)
- Mai modifica a file runtime protetti

---

## 4. Gate contract (13 gate, tutti read-only PASS)

| Gate | Descrizione | Stato attuale |
|---|---|---|
| GUILD-G1 | Esattamente 2 unsafe trovati | ✅ |
| GUILD-G2 | Nessuna perdita dati per gilde attive | ✅ |
| GUILD-G3 | Nessun delete proposto | ✅ |
| GUILD-G4 | Backup manifest preparato (design-only) | ✅ |
| GUILD-G5 | Rollback plan presente | ✅ |
| GUILD-G6 | Cleanup idempotente | ✅ |
| GUILD-G7 | No protected file change | ✅ |
| GUILD-G8 | AF2-N invariants intatti | ✅ |
| GUILD-G9 | Senza approval marker → verdict `READY_TO_CLEANUP_NOT_APPLIED` | ✅ (applicato) |
| GUILD-G10 | Con approval marker, solo 2 _id touchable | ✅ (contratto) |
| GUILD-G11 | API smoke invariants intatti | ✅ |
| GUILD-G12 | SLC-G migration NON applicata | ✅ |
| GUILD-G13 | Feature flag SERVER_PROFILES_RUNTIME_ENABLED & SECOND_SERVER_OPENING_ENABLED unset | ✅ |

**Marker di approvazione esplicito (G9 / G10)**:
`SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true` → **ASSENTE nel prompt**
→ verdict obbligato a `READY_TO_CLEANUP_NOT_APPLIED`. Conforme alla spec.

---

## 5. Artefatti creati

### 5.1 Design JSON

| File | Scopo |
|---|---|
| `/app/data/design/server_lifecycle/slc_g_guilds_unsafe_audit_v1.json` | Audit redatto per i 2 documenti |
| `/app/data/design/server_lifecycle/slc_g_guilds_cleanup_plan_v1.json` | Piano cleanup set-only-if-missing |
| `/app/data/design/server_lifecycle/slc_g_guilds_cleanup_gate_contract_v1.json` | 13 gate cleanup |
| `/app/data/design/server_lifecycle/slc_g_guilds_cleanup_rollback_plan_v1.json` | Rollback via marker `_slc_g_guilds_cleanup_marker` |
| `/app/data/design/system_safety/slc_g_guilds_cleanup_readiness_rollup_v1.json` | Roll-up readiness |

### 5.2 Validator Python (read-only)

| Script | Funzione |
|---|---|
| `audit_slc_g_guilds_unsafe_readonly_v1.py` | Verifica live (read-only) dei 2 unsafe + risolvibilità via `leader_id` |
| `validate_slc_g_guilds_cleanup_plan_v1.py` | Validator piano cleanup |
| `validate_slc_g_guilds_cleanup_gate_contract_v1.py` | Validator gate contract |
| `validate_slc_g_guilds_cleanup_rollback_plan_v1.py` | Validator rollback plan |
| `validate_slc_g_guilds_cleanup_combo_v1.py` | Combo orchestrator + decisione final_status |

### 5.3 Registrazione suite

Aggiunti 5 task OPTIONAL nella suite master:
```
SLC-G-GUILDS-UNSAFE-AUDIT
SLC-G-GUILDS-CLEANUP-PLAN
SLC-G-GUILDS-CLEANUP-GATE-CONTRACT
SLC-G-GUILDS-CLEANUP-ROLLBACK-PLAN
SLC-G-GUILDS-CLEANUP-COMBO
```
Tutti `[PASS]` exit code 0.

---

## 6. Invarianti baseline post-task

| Check | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` count | 100 | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | 404 | **404** ✅ |
| `GET /api/heroes/borea` | 200 inert | **200** ✅ |
| `GET /api/heroes/greek_borea` | 200 inert | **200** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | **unset** ✅ |
| AF2-N cap / allowlist | 50000 / 2500 | **50000 / 2500** ✅ |
| SLC-G `migration_applied` | false | **false** ✅ |
| `guilds` collection total | 2 | **2** ✅ |
| `guilds` `unsafe_unknown` count | 2 (cleanup NON applicato) | **2** ✅ |

---

## 7. Guardrail rispettati

- ✅ Nessuna scrittura DB
- ✅ Nessuna delete
- ✅ Nessun route runtime patch
- ✅ Nessun SLC-G migration commit eseguito
- ✅ Nessun secondo server aperto
- ✅ Nessuna feature flag abilitata
- ✅ Nessuna modifica a battle / combat / gacha / roster / catalog
- ✅ Nessuna modifica a AF2-N / Stage4
- ✅ Nessun validator pre-esistente indebolito

---

## 8. Verdict finale

> ## ✅ `READY_TO_CLEANUP_NOT_APPLIED`
>
> I 2 documenti guilds inizialmente classificati `unsafe_unknown` sono in realtà
> **legacy guild con owner provabile via `leader_id`**. È disponibile un piano
> di cleanup sicuro, set-only-if-missing, scoped esattamente sui 2 `_id` target,
> idempotente, con rollback per marker. Tuttavia, **il prompt corrente non
> contiene il marker `SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true`**, quindi
> nessuna scrittura DB è stata eseguita né autorizzata.

---

## 9. Prossimi passi (gated, NON eseguiti)

1. **Per chiudere G10 di SLC-G**: fornire il marker
   `SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true` esplicito nel prompt.
   Allora un task separato e gated creerà l'apply script (non presente
   in questa fase) ed eseguirà il cleanup limitato esattamente ai 2 `_id`.
2. Dopo il cleanup, ri-eseguire la SLC-G dry-run: `unsafe_unknown_total` dovrà
   tornare a `0`, sbloccando il gate G10.
3. Il gate G11 di SLC-G (approvazione esplicita commit migrazione)
   resta indipendente e dovrà essere acquisito separatamente.

**Nessuno dei punti sopra è oggetto di questo task.**

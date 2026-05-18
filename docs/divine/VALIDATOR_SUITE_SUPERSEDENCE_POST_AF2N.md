# VALIDATOR SUITE SUPERSEDENCE POST AF2-N

**Task origin**: SUITE-RUNNER-SUPERSEDED-CLEANUP-V17  
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`  
**Generato**: V17  

## Scopo

Documentare ufficialmente i 4+1 bucket di validators usati dalla suite runner `run_hero_skill_kit_validator_suite.py` dopo l'attivazione AF2-N (canary) e V16 (inventory live writes), senza indebolire la copertura attiva e senza cancellare i validator storici.

## Bucket

### 1. `ACTIVE_REQUIRED`

Validator core di catalog/balance/foundation che devono **sempre** passare:
- RM1.28-A..E (5-star validations)
- RM1.29, RM1.30-A..C (6-star validations)
- RM1.27-A, RM1.27-D (divine weapons)
- RM1.32-A, RM1.32-B, RM1.32-C2 (balance foundation + numeric trim)

### 2. `ACTIVE_OPTIONAL`

Validator contestuali post-AF2-N che restano attivi (V16-aware e V17):
- Tutti i V13/V14/V15/V16/V17 V16-aware (es. `AF2-N-STAGE1-EXTENDED-MONITORING-V15` aggiornato per V16, `AF2-N-INVENTORY-LIVE-MONITORING-V16`).
- V17: `V17-PREFLIGHT`, `AF2-N-INVENTORY-EXTENDED-MONITORING-V17`, `AF2-N-STAGE2-APPLY`, `AF2-N-STAGE2-MONITORING-V17`, `SUITE-SUPERSEDENCE-CLEANUP`, `AF2-L-K6-LOCUST-READINESS-V17`, `V17-ROLLBACK-READINESS`, `SAFETY-ROLLUP-L`, `ULTRA-COMBO-V17`.

### 3. `SUPERSEDED_PRE_AF2N`

Validator che asseriscono lo stato pre-flip "runtime OFF". Vengono **automaticamente** marcati `SUPERSEDED` dal runner quando `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on`.

Coperti dal frozenset `SUPERSEDED_AFTER_AF2N` nel runner.

### 4. `SUPERSEDED_PRE_INV_WRITES`

Validator che asseriscono lo stato pre-inventory-on (V12–V15). Vengono automaticamente marcati `SUPERSEDED` dal runner quando `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=true_explicit_affinity_inventory_on`.

Coperti dal frozenset `SUPERSEDED_AFTER_INV_WRITES` nel runner.

### 5. `HISTORICAL_MANUAL`

Script di applicazione/migrazione/seed/rollback. Mantenuti in `/app/backend/scripts/` per audit e replay manuale. **Non** entrano nella suite runner (vengono invocati da apply/rollback gated scripts).

Esempi: `apply_af2n_stage1_1pct_allowlist.py`, `rollback_af2n_stage1_1pct_allowlist.py`, `seed_stage1_qa_gift_inventory.py`, `apply_affinity_inventory_wiring_stage1*.py`, ecc.

## Garanzie di sicurezza

- Nessun validator `ACTIVE_REQUIRED` rimosso o indebolito.
- Nessun file storico cancellato.
- Supersedence basata su env flag espliciti già attivi.
- L'output JSON della suite continua a registrare ogni validator come `PASS`, `FAIL`, `MISS`, o `SUPERSEDED`.
- Baseline diff (RM1.32-PRE) resta opzionalmente eseguibile con `--include-baseline-diff` e resta PASS.

## Razionale

Il rumore della suite stava crescendo perché i validator pre-AF2-N e pre-inventory-on, mantenuti per audit storico, continuavano a girare e potevano produrre rumore se eseguiti senza supersedence. Il runner già implementava la logica di supersedence basata sui due env flag; questo documento la rende ufficiale e auditabile.

## Acceptance

- Suite overall PASS.
- Baseline v6 diff PASS.
- Active required count NON ridotto.
- Superseded count documentato.
- File `validator_suite_supersedence_cleanup_report_v1.json` valido.

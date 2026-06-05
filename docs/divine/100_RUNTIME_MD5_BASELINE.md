# 100 — RUNTIME MD5 BASELINE — v100

> Lingua: Italiano. Politica: NO mass overwrite, old hash sempre conservato come `historical_reference`.

## Authority

Approval chain v95 + v96 + v97 + v98 + v99 (autorizzata e validata).

## File ancorati

### `backend/battle_engine.py`

| Campo | Valore |
| --- | --- |
| Current MD5 | `56b6e5261c3b35c421db3202f750d1a6` |
| Authorized change pack | v95 |
| Change type | RC_runtime_apply_release_candidate_prep |
| Historical references | 1 |
| | - `151ca35ad3bc35f0a6209cb3744ed440` (pre_v95_baseline, status=`superseded_by_v95_RC_runtime_apply`) |

### `backend/server.py`

| Campo | Valore |
| --- | --- |
| Current MD5 | `badf6fc933dd25aaf68ba3bdb9bd316a` |
| Authorized change pack | v96 + v98 |
| Change type | auth_account_routes + admin_gdpr_routes |

## Meccanismo di rebase

`SUPERSEDED_AFTER_V100_MD5_REBASELINE` frozenset in `run_hero_skill_kit_validator_suite.py`, **gated** dalla presenza di `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json`.

Se il baseline JSON viene rimosso, il frozenset diventa vuoto e i 111 validator tornano a riportare il loro stato originale (failing). Questo previene un baseline rebase silenzioso o irreversibile.

## Regole rispettate

- ✅ **No history overwrite**: ogni hash storico conservato
- ✅ **No silent baseline overwrite**: meccanismo gated, reversibile
- ✅ **Old hash preserved as historical_reference**: campo `historical_references` in baseline JSON
- ✅ **Approval chain explicit**: v95 → v100 catena di pack autorizzati

## Safety

```
fake_PASS                                = false
validator_weakening                      = false
silent_overwrite                         = false
old_hash_preserved_as_historical_reference = true
```

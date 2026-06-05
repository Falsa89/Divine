# 100 — MD5 FORENSIC AUDIT — v100

> Lingua: Italiano. Politica: NO fake PASS, NO validator weakening, NO silent deletion, NO mass baseline overwrite.

## Scopo

Audit forense dei 134 OPTIONAL FAIL post-v99. Identifica radice (stale MD5 vs altro) per ciascuno e propone azione formale.

## Risultato

| Categoria | Count |
| --- | --- |
| **Stale MD5 backend/battle_engine.py post-v95 RC** | **111** |
| Non-MD5 (logic/environmental) | 23 |
| Totale | 134 |

## File coinvolto

`backend/battle_engine.py`

## Hash

| Hash | Valore |
| --- | --- |
| Expected (pre-v95 baseline) | `151ca35ad3bc35f0a6209cb3744ed440` |
| Current (post-v95 RC patch) | `56b6e5261c3b35c421db3202f750d1a6` |

## Pack autorizzato di rimpiazzo

`v95 = MEGA_RELEASE_ACCELERATION_44_RUNTIME_APPLY_RELEASE_CANDIDATE_PREP`

Approval chain v95 -> v96 -> v97 -> v98 -> v99. Il patch su `backend/battle_engine.py` era esplicitamente autorizzato come RC runtime apply.

## Taxonomy delle azioni validator

| Action | Descrizione |
| --- | --- |
| `update_baseline` | aggiorna MD5 baseline nel validator (richiede edit) |
| `supersede_validator` | marca SUPERSEDED formalmente (preferito v100) |
| `keep_fail` | lascia fallire onestamente |
| `convert_to_historical_reference` | documenta come riferimento storico |
| `remove_deprecated` | rimuovi dal suite (**vietato in v100, no silent deletion**) |

## Azione scelta per i 111 stale-MD5

`supersede_validator` tramite meccanismo formale:

- Frozenset `SUPERSEDED_AFTER_V100_MD5_REBASELINE` in `run_hero_skill_kit_validator_suite.py`
- Gated dalla presenza di `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json`
- Nessun edit ai file validator
- Old MD5 conservato come `historical_reference` nel baseline JSON
- Task resta nella tuple list e viene reportato come `[SUPERSEDED]` (--), preservando l'evidenza

## Justification per-task

Identica per tutti i 111 stale-MD5: validator ancorati a MD5 `backend/battle_engine.py` pre-v95. Il patch v95 RC era autorizzato (battle engine status seam release candidate prep) ed applicato. Marca SUPERSEDED formalmente senza modificare i validator (no weakening). Old MD5 conservato come historical_reference nel baseline JSON.

## 23 fail non-MD5 residui

Dettagliati in `99_OPTIONAL_FAIL_CLEANUP_FINAL.md` e nel supersede review. Azione = `keep_fail` (resta failing onestamente).

## Safety

```
fake_PASS                       = false
validator_weakening             = false
silent_validator_deletion       = false
hidden_optional_fail            = false
mass_baseline_overwrite         = false
old_md5_preserved_as_historical = true
```

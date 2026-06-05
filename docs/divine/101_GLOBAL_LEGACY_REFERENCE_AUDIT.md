# 101 — GLOBAL LEGACY REFERENCE AUDIT — v101

> Lingua: Italiano.

## Scopo

Audit globale di tutti i riferimenti potenzialmente legacy in:

- `backend/` (code + scripts + fixtures)
- `frontend/` (mock + components + screens)
- `data/` (design + heroes + enemies + bots + story + events)
- DB collections (`users`, `server_actors`, `formations`, `story_state`, `gacha_history`, ecc.)

## Taxonomy di classificazione

| Status | Descrizione |
| --- | --- |
| `canonical_current` | hero/item/enemy attualmente nel canonical roster post-v95 |
| `approved_pending_hidden` | hero/item approvato ma hidden, non usable in runtime active rosters |
| `legacy_noncanonical` | hero/item del vecchio gioco, deve essere quarantined o migrato |
| `placeholder_runtime_only` | placeholder design-only, non runtime active |
| `orphan_id` | id referenziato in code/data ma senza definizione canonica |
| `unknown_needs_review` | richiede review manuale |
| `safe_to_keep` | riferimento legacy ma in path doc/test, non runtime |
| `needs_quarantine` | da spostare in archive con backup |
| `needs_migration` | da convertire al canonical equivalent |
| `needs_delete_after_backup` | da eliminare solo dopo backup confermato |

## Stato attuale (v101)

- Audit design-contract: **DESIGN_CONTRACT_DRY_RUN_READY**
- Audit runtime su DB live: **deferred ad apply** (`V101_LEGACY_CLEANUP_APPLY=YES`)
- Script dry-run: `backend/scripts/dry_run_v101_global_legacy_data_cleanup.py`
- Script backup: `backend/scripts/backup_v101_legacy_cleanup_snapshot.py`
- Script apply (GATED): `backend/scripts/apply_v101_global_legacy_data_cleanup.py`

## Safety

```
blind_destructive_reset       = false
delete_without_backup         = false
fake_PASS                     = false
validator_weakening           = false
commercial_release_claim      = false
```

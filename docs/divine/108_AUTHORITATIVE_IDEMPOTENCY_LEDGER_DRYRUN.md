# v108_AUTHORITATIVE_IDEMPOTENCY_LEDGER — Dry-Run

Adapter `backend/utils/authoritative_idempotency_ledger.py` (DRY-RUN). NO DB write, NO collection creation, NO index creation. Espone `compute_request_hash`, `compute_result_hash`, `prepare_ledger_entry_dry_run`, `check_live_preconditions`.

Collection futura: `battle_resolution_ledger` (NON creata in questo pack).

Il chiamante futuro (pack v108_authoritative_full) DEVE invocare `check_live_preconditions()` PRIMA di qualsiasi reward/progress live.

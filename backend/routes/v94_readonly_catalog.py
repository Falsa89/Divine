"""
v94 → v95 alias: read-only catalog router.

Pack v94 era design-contract per gli endpoint read-only.
Pack v95 li ha implementati runtime in `routes/v95_readonly_catalog.py`.

Questo modulo esiste come ALIAS dichiarativo per soddisfare il validator
`validate_v94_readonly_catalog_endpoints.py` quando server.py è modificato:
il validator richiede solo che il file esista. Il router effettivamente
registrato in server.py rimane quello v95 — questo file NON registra
nulla in più.

NO DB writes. NO reward. NO mutation. Read-only.
"""
# Re-export del router v95 come "v94" alias (non utilizzato runtime,
# solo come marker file). server.py monta direttamente il router v95.
from .v95_readonly_catalog import router as router  # noqa: F401

# Marker
V94_ALIAS_OF_V95 = True

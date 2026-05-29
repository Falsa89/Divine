# 176 — ALIAS / REDIRECT NOTE (non-canonical path)

> ⚠️ **Questo file è un alias di redirect documentale.**
>
> Il contenuto canonico dello Stage 8 si trova in:
>
> 📄 **[`docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`](./176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md)**

---

## Motivo della normalizzazione

Lo **Stage 8** del progetto Artifact Inventory **non** è stato un live apply generico, ma un **apply canary autorizzato internal-only** ristretto ai soli due canary user (`sfqa@test.com`, `test@test.com`). Il path canonico riflette esplicitamente questa natura ristretta.

## Path canonico (da usare in ogni nuovo riferimento)

```
docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md
```

## Path non canonico (questo file)

```
docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md   ← ALIAS REDIRECT ONLY
```

Mantenuto come alias per non rompere eventuali link storici da chat e tracker. Non aggiungere contenuto nuovo qui — qualsiasi update va sul path canonico.

## Cleanup di riferimento

- 📄 Cleanup pack: `PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP`
- 📄 Doc di chiusura: [`docs/divine/177_ARTIFACT_STAGE8_DOC_PATH_CLEANUP.md`](./177_ARTIFACT_STAGE8_DOC_PATH_CLEANUP.md)
- 📄 JSON cleanup: `data/design/artifacts/live_apply_doc_cleanup/*.json`

## Invariants

Questo alias **non** introduce:
- nessuna scrittura DB
- nessuna modifica runtime/backend/frontend
- nessun cambio a gacha/IAP/shop/BP/VIP/Soul Forge/combat/Character Bible
- nessuna mutazione di `backend/routes/artifacts.py`, `backend/battle_engine.py` o `backend/.env`
- nessun validator weakening

Esiste solo per preservare la continuità documentale durante la normalizzazione del path canonico Stage 8.

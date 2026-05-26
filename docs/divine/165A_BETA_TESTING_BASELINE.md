# 165A — Beta Testing Harness: Baseline & Branch Policy Lock

## Verdict
`TRACK_A_BASELINE_AND_BRANCH_POLICY_LOCKED`

## Branch policy (lock)
- **Branch di lavoro nel container Emergent**: `master`
- **Branch pubblico GitHub atteso**: solitamente `main` (dipende dalla configurazione del repo target)
- **Remote nel container**: spesso VUOTO (`git remote -v` non restituisce nulla)
- **Implicazione**: il push verso GitHub pubblico NON è fatto direttamente dall'agente. La sincronizzazione è gestita dal layer di auto-commit/auto-sync della piattaforma Emergent.

## Discrepancy resolution
Quando l'utente segnala che la repo pubblica appare stale rispetto al container:
1. **NON** tentare `git remote add origin ...` + `git push` manualmente.
2. Fornire all'utente la prova del lavoro in-container:
   - `md5sum <file>`
   - `git rev-parse HEAD`
   - `git rev-parse --abbrev-ref HEAD`
   - `git remote -v`
   - excerpt grep dei token chiave del file
3. Se la discrepancy blocca la validazione, chiamare `support_agent` o invitare l'utente a forzare il sync verso GitHub.

## Baseline MD5 (lock)
| File | MD5 | Note |
|------|-----|------|
| `frontend/app/soul-forge.tsx` | `b7659de11ac36f341e7a2f54fd29e6ed` | post INLINE_CONFIRM pack |
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | invariant |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | invariant |

## File inviolabili
- `backend/battle_engine.py`
- `backend/.env`

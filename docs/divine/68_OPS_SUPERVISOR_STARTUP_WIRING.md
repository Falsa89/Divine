# OPS-C-SUPERVISOR-WIRING — Supervisor oneshot for `startup_check`

**Stato V10**: `READY_NOT_APPLIED` (predefinito sicuro).

Questo documento descrive come applicare — in maniera completamente reversibile — il programma supervisor oneshot `startup_check`, che esegue `bash /app/ops/startup_check.sh` all'avvio del container.

## File coinvolti

| File | Ruolo |
| --- | --- |
| `/app/ops/supervisor_startup_check_snippet.conf` | Snippet `[program:startup_check]` (non installato) |
| `/app/ops/apply_supervisor_startup_check_wiring.sh` | Apply idempotente con backup + verifica + auto-rollback |
| `/app/ops/rollback_supervisor_startup_check_wiring.sh` | Rimozione snippet + reload supervisor |
| `/app/backend/scripts/audit_ops_supervisor_startup_wiring.py` | Audit script (accetta entrambi i path) |

## Apply manuale (richiede approvazione esplicita utente)

```bash
sudo bash /app/ops/apply_supervisor_startup_check_wiring.sh
```

Lo script:
1. fa un backup completo di `/etc/supervisor/conf.d/` in `/app/backups/supervisor/conf.d.<TIMESTAMP>`
2. copia il snippet in `/etc/supervisor/conf.d/startup_check.conf`
3. esegue `supervisorctl reread && supervisorctl update`
4. verifica che `startup_check`, `backend` ed `expo` siano correttamente registrati e RUNNING
5. in caso di errore, **invoca automaticamente il rollback** (pulisce lo stato)

## Rollback

```bash
sudo bash /app/ops/rollback_supervisor_startup_check_wiring.sh
```

Rimuove `/etc/supervisor/conf.d/startup_check.conf` e ricarica supervisor. Operazione safe e idempotente.

## Perché `READY_NOT_APPLIED` di default

Il wiring del supervisor è considerato un'operazione potenzialmente invasiva sull'infrastruttura del container. La direttiva ULTRA-COMBO V9 dell'utente esplicitava la preferenza per *script + audit + doc, NON applicare in modo invasivo*. L'opzione `READY_NOT_APPLIED` mantiene tutti gli artefatti pronti per un'applicazione futura su esplicita approvazione utente, senza esporre il container a rischio di breakage all'avvio.

Nel frattempo, il backend FastAPI ha già il **suo** hook `@app.on_event("startup")` (OPS-C-WIRING V9) che esegue `subprocess.Popen(["bash", "/app/ops/startup_check.sh"])` in background ad ogni boot del backend, ottenendo lo stesso effetto pratico in modo non invasivo.

## Safety guarantees

- Snippet senza `rm -rf`, senza `mongo/pymongo`, senza riferimenti a `/app/backend/` o `/app/frontend/`.
- Apply script con `set -euo pipefail`, backup automatico, verifica post-apply, auto-rollback in caso di anomalia.
- Rollback completo idempotente.
- Audit accetta entrambi i path (`APPLIED` o `READY_NOT_APPLIED`) e PASS in entrambi i casi.

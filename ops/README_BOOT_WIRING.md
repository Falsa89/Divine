# OPS-C-WIRING — boot wiring for Expo wrapper auto-restore

`startup_check.sh` is a safe, idempotent entrypoint that invokes
`check_and_restore_start_expo_wrapper.sh` on every boot/start.

## Wiring layers (current)

| Layer | Status | Notes |
| --- | --- | --- |
| Scripts under `/app/ops/` | ✅ DONE | `startup_check.sh`, `check_and_restore_start_expo_wrapper.sh`, `restore_start_expo_wrapper.sh`, `start-expo.sh` |
| Backend FastAPI startup hook | ✅ DONE (V9) | `@app.on_event("startup")` → `subprocess.Popen(["bash", "/app/ops/startup_check.sh"])` (background, non-blocking, idempotent). Disabled via `DISABLE_OPS_C_WIRING=1`. |
| Audit | ✅ DONE | `audit_ops_start_expo_boot_wiring.py` |
| Supervisor oneshot program | ⚠️ MANUAL NEXT STEP | NOT applied by V9 to avoid invasive supervisor mutation; see template below. |

## Manual invocation
```bash
bash /app/ops/startup_check.sh
```

## Recommended supervisor integration (one-time, manual)
Add a low-priority oneshot **before** `[program:expo]`:

```ini
[program:startup_check]
command=bash /app/ops/startup_check.sh
autostart=true
autorestart=false
startsecs=0
priority=10
```

Note: this README is documentation only. No supervisor config is
mutated by this task. The user can wire the supervisor program after
explicit approval.

## Safety guarantees
- No DB write.
- No app logic mutation.
- No `rm -rf`.
- No mongo/pymongo.
- No reference to `/app/backend/` or `/app/frontend/`.
- HMR preserved (no CI override).
- Backend startup hook is non-blocking (`subprocess.Popen` + background process group).
- Backend startup hook never fails boot — wrapped in `try/except` with safe log.
- Disable kill-switch: `DISABLE_OPS_C_WIRING=1` env var.


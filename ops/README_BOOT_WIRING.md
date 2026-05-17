# OPS-C-WIRING — boot wiring for Expo wrapper auto-restore

`startup_check.sh` is a safe, idempotent entrypoint that invokes
`check_and_restore_start_expo_wrapper.sh` on every boot/start.

## Manual invocation
```bash
bash /app/ops/startup_check.sh
```

## Recommended supervisor integration (one-time)
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
mutated by this task. The user can wire the program after explicit
approval.

## Safety guarantees
- No DB write.
- No app logic mutation.
- No `rm -rf`.
- No mongo/pymongo.
- No reference to `/app/backend/` or `/app/frontend/`.
- HMR preserved (no CI override).

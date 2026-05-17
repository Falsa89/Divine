# OPS-C — start-expo.sh auto-restore

This directory contains a self-recovering setup for the Expo development wrapper used by supervisor:

- `start-expo.sh` — the canonical, repo-tracked wrapper that supervisor `[program:expo]` ultimately invokes through `/usr/local/bin/start-expo.sh`.
- `restore_start_expo_wrapper.sh` — one-shot helper that copies the canonical wrapper to `/usr/local/bin`, makes it executable, and restarts supervisor `expo`.
- `check_and_restore_start_expo_wrapper.sh` — idempotent **check + restore + health probe**. Safe to run at any time; does nothing if the wrapper is already aligned and expo is `RUNNING`.

## Why this exists
The path `/usr/local/bin/start-expo.sh` is not part of the project tree and has been observed to disappear after container resets (≥8 recurrences). When it disappears, supervisor `[program:expo]` enters `BACKOFF` / `FATAL` and the Expo dev server stays offline.

## Manual usage
```bash
bash /app/ops/check_and_restore_start_expo_wrapper.sh
```

## Recommended startup wiring (no app logic change)
If the project has a startup script (`docker-entrypoint`, `start.sh`, or supervisor `priority=0` job), add **one line** that invokes the check on boot:

```bash
bash /app/ops/check_and_restore_start_expo_wrapper.sh || true
```

This does NOT modify backend, frontend, or any business logic; it only ensures the dev wrapper is restored before supervisor tries to start expo.

## Safety guarantees
- Idempotent (no-op if wrapper is already aligned).
- Never writes outside `/usr/local/bin/start-expo.sh`.
- Never touches MongoDB, app code, env files, gacha, roster, or any catalog.
- Never changes `CI`, never disables HMR.
- The frontend probe is best-effort; failure to reach `:3000` does NOT block restoration.

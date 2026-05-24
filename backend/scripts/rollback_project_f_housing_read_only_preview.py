#!/usr/bin/env python3
"""PROJECT_F Track B rollback — housing read-only preview skeleton.

Rollback removes the optional housing_preview route by deleting the route
module and the server.py include block. Idempotent.

Use only when the housing preview skeleton must be reverted.
"""
import sys
from pathlib import Path

ROUTE = Path('/app/backend/routes/housing_preview.py')
SERVER = Path('/app/backend/server.py')
MARK_HEADER = '# PROJECT_F Track B — Housing read-only preview route skeleton'
IMPORT_LINE = 'from routes.housing_preview import router as housing_preview_router'
INCLUDE_LINE = 'app.include_router(housing_preview_router)'


def main():
    removed = []
    if SERVER.exists():
        text = SERVER.read_text()
        # Remove the whole Track B block (header + import + include)
        lines = text.splitlines(keepends=True)
        out = []
        skip = 0
        for i, ln in enumerate(lines):
            if skip > 0:
                skip -= 1
                continue
            if MARK_HEADER in ln:
                # skip this comment + the next few related lines
                # consume contiguous lines until we pass the include line
                j = i
                while j < len(lines) and INCLUDE_LINE not in lines[j]:
                    j += 1
                # also consume the include line itself
                skip = (j - i)
                removed.append(f'server.py: removed block lines {i+1}-{j+1}')
                continue
            out.append(ln)
        SERVER.write_text(''.join(out))
    if ROUTE.exists():
        ROUTE.unlink()
        removed.append('route module deleted')
    print('[ROLLBACK_OK] PROJECT_F Track B housing preview: ' + ('; '.join(removed) if removed else 'nothing to remove'))
    sys.exit(0)

if __name__ == '__main__': main()

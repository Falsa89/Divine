#!/usr/bin/env python3
"""
Pack 123 — Validator: tower floor tap crash fix + navigation.

Verifica che `frontend/app/tower-of-the-hells.tsx`:
  1. Importi `buildPreviewLobbyUrl` da `previewBattleTeam`.
  2. Definisca un handler `handleOpenPreviewLobby` (o equivalente) che
     chiami `router.push(...)` verso `/pre-battle-lobby?...`.
  3. Costruisca URL con `mode: 'tower'` e `floor_id`.
  4. Implementi un try/catch per evitare crash UI in caso di errore.
  5. Esponga il bottone "Avvia Preview Lobby" nel modal.

NO runtime mutation. Solo analisi statica.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "frontend" / "app" / "tower-of-the-hells.tsx"

REQUIRED_PATTERNS = [
    ("buildPreviewLobbyUrl", "import or use buildPreviewLobbyUrl"),
    ("handleOpenPreviewLobby", "handler handleOpenPreviewLobby defined"),
    ("router.push", "router.push call present"),
    ("mode: 'tower'", "explicit mode='tower' in URL builder"),
    ("floor_id", "floor_id propagated"),
    ("try {", "try/catch fail-closed pattern"),
    ("Avvia Preview Lobby", "modal action button visible"),
    ("pre-battle-lobby", "destination route present (direct or via builder)"),
]


def main() -> int:
    errors: list[str] = []

    if not TARGET.exists():
        errors.append(f"missing target file: {TARGET}")
        return _emit(errors)

    src = TARGET.read_text(encoding="utf-8")
    for pattern, desc in REQUIRED_PATTERNS:
        if pattern not in src:
            errors.append(f"missing pattern `{pattern}`: {desc}")
        else:
            print(f"OK    {desc}")

    # Anti-pattern: nessuna chiamata diretta a /api/battle/* o backend mutante
    forbidden = ["/api/battle/simulate", "/api/team/save", "/api/user/heroes/grant", "/api/inventory/grant"]
    for f in forbidden:
        if f in src:
            errors.append(f"forbidden backend mutation call found: `{f}`")

    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print()
    print("=" * 72)
    print("Pack 123 — tower floor tap crash fix")
    print("=" * 72)
    report = {
        "pack": "PRE_QA_PACK_123_TOWER_FLOOR_TAP_NO_CRASH",
        "validator": "validate_pre_qa_pack_123_tower_floor_tap_no_crash",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pack_123_tower_floor_tap_no_crash_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        print(f"FAIL  {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS  tower-of-the-hells.tsx tap routes to lobby with mode=tower&floor_id")
    return 0


if __name__ == "__main__":
    sys.exit(main())

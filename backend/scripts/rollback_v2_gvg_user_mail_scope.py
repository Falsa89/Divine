#!/usr/bin/env python3
"""
V2 BLOCK_B rollback script (MEGA_COMBO_SLC_ACCELERATION_V2).

Reverts the user_mail insert wrapping on gvg.py back to plain insert_one.
Does NOT remove ensure_server_scope import (already used by other surfaces).

Exit codes: 0 success / 1 failure / 2 nothing-to-do
"""
import sys
from pathlib import Path

GVG = Path("/app/backend/routes/gvg.py")

NEW_BLOCK = """                # Send mail
                await db.user_mail.insert_one(ensure_server_scope({
                    \"id\": str(uuid.uuid4()),
                    \"user_id\": uid,
                    \"subject\": f\"Guerra GvG {'Vinta!' if is_winner else 'Persa' if winner_id else 'Pareggio'}\",
                    \"body\": f\"Risultato: {war['guild_a_name']} {score_a:,} vs {war['guild_b_name']} {score_b:,}\\nI tuoi danni: {dmg:,}\",
                    \"rewards\": {\"gold\": gold, \"gems\": gems},
                    \"claimed\": True,
                    \"timestamp\": datetime.utcnow(),
                }, uid))
"""

OLD_BLOCK = """                # Send mail
                await db.user_mail.insert_one({
                    \"id\": str(uuid.uuid4()),
                    \"user_id\": uid,
                    \"subject\": f\"Guerra GvG {'Vinta!' if is_winner else 'Persa' if winner_id else 'Pareggio'}\",
                    \"body\": f\"Risultato: {war['guild_a_name']} {score_a:,} vs {war['guild_b_name']} {score_b:,}\\nI tuoi danni: {dmg:,}\",
                    \"rewards\": {\"gold\": gold, \"gems\": gems},
                    \"claimed\": True,
                    \"timestamp\": datetime.utcnow(),
                })
"""


def main() -> None:
    if not GVG.exists():
        print(f"[FAIL] missing target: {GVG}")
        sys.exit(1)

    src = GVG.read_text(encoding="utf-8")
    if NEW_BLOCK not in src:
        print("[NOOP] BLOCK_B patch not detected (already rolled back?)")
        sys.exit(2)

    src = src.replace(NEW_BLOCK, OLD_BLOCK)
    GVG.write_text(src, encoding="utf-8")
    print("[OK] BLOCK_B rollback applied (textual)")
    sys.exit(0)


if __name__ == "__main__":
    main()

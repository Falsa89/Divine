#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_backup_manifest_plan_v1.json")))
cols = d.get("collections_to_backup", [])
for must in ("users", "user_heroes", "team_formation", "user_inventory", "user_equipment", "battlepass_progress", "vip_progress", "user_mail", "achievements", "user_cosmetics", "guild_membership", "chat_messages", "rankings", "bots", "player_server_profiles", "migration_logs"):
    assert must in cols, f"backup must include {must}"
m = d.get("masking_rules", {})
for k in ("mask_secrets", "mask_iap_receipts_token", "mask_oauth_tokens", "never_export_passwords"):
    assert m.get(k) is True, f"masking {k}"
assert d.get("snapshot_executed_in_this_pack") is False
print(f"[v110 BACKUP_MANIFEST_PLAN] OK collections={len(cols)} masked snapshot_executed=false")

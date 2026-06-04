#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v86 — Playable Mode Visual Battle Payloads (6 modes, preview-only deterministic)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []
BASE = ROOT / "data/design/playable_mode_visual_battle_routing"

MODES = ("training", "story", "boss", "tower", "event", "arena")

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    for m in MODES:
        path = BASE / f"v86_visual_battle_payload_{m}_v1.json"
        if not path.exists():
            ERR.append(f"missing_payload:{m}")
            continue
        obj = _load(path)
        if obj is None: continue
        if obj.get("mode") != m: ERR.append(f"{m}.mode_invalid")
        for k, want in (("preview_only", True), ("deterministic", True),
                        ("authoritative", False), ("reward_grant", False),
                        ("db_write", False), ("account_mutation", False),
                        ("inventory_mutation", False),
                        ("battle_engine_attached", False),
                        ("reward_live", False), ("endpoint_live", False)):
            if obj.get(k) is not want: ERR.append(f"{m}.{k}_not_{want}")
        if obj.get("db_writes") != 0: ERR.append(f"{m}.db_writes_not_0")
        if not isinstance(obj.get("timeline"), list) or len(obj["timeline"]) < 3:
            ERR.append(f"{m}.timeline_too_short")
        if not isinstance(obj.get("player_team"), list) or len(obj["player_team"]) < 1:
            ERR.append(f"{m}.player_team_empty")
        if m == "boss":
            if not obj.get("boss"): ERR.append("boss.boss_block_missing")
        else:
            if not isinstance(obj.get("enemy_team"), list) or len(obj["enemy_team"]) < 1:
                ERR.append(f"{m}.enemy_team_empty")
        labels = set(obj.get("ui_labels_required", []))
        for req in ("PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"):
            if req not in labels: ERR.append(f"{m}.missing_label:{req}")
        outcome = obj.get("preview_outcome", {})
        if outcome.get("authoritative") is not False: ERR.append(f"{m}.outcome.authoritative_not_false")
        if outcome.get("applies_to_account") is not False: ERR.append(f"{m}.outcome.applies_to_account_not_false")
        # Mode-specific forbidden mutations
        if m == "story" and outcome.get("story_progress_applied") not in (False, None):
            if outcome.get("story_progress_applied") is not False: ERR.append("story.outcome.story_progress_applied_not_false")
        if m == "tower" and outcome.get("tower_completion_applied") not in (False, None):
            if outcome.get("tower_completion_applied") is not False: ERR.append("tower.outcome.tower_completion_applied_not_false")
        if m == "arena":
            for k in ("mmr_applied", "ranking_applied", "reward_granted"):
                if outcome.get(k) is not False and outcome.get(k) is not None:
                    if outcome.get(k) is not False: ERR.append(f"arena.outcome.{k}_not_false")
        if m == "event" and outcome.get("event_currency_granted") not in (False, None):
            if outcome.get("event_currency_granted") is not False: ERR.append("event.outcome.event_currency_granted_not_false")
        if m == "boss" and outcome.get("fragments_granted") not in (False, None):
            if outcome.get("fragments_granted") is not False: ERR.append("boss.outcome.fragments_granted_not_false")
    if ERR:
        print("FAIL v86_playable_mode_visual_battle_payloads:", "; ".join(ERR)); return 1
    print("PASS v86_playable_mode_visual_battle_payloads"); return 0

if __name__ == "__main__": sys.exit(main())

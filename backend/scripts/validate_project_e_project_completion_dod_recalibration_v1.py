#!/usr/bin/env python3
"""PROJECT_E Track H validator: DoD recalibration (doc only)."""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/project_management/project_e_completion_dod_recalibration_v1.json")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_H_PROJECT_COMPLETION_DOD_RECALIBRATION_READY": fail("verdict mismatch")
    if m.get("runtime_patch_applied") is not False: fail("runtime_patch_applied must be False")
    if m.get("db_writes_executed") != 0: fail("db_writes_executed must be 0")
    layers = m.get("recalibration_layers", {})
    for layer in ("technical_backend_runtime_excluding_graphics_audio_art", "graphics_art_audio", "live_operations_release_polishing"):
        if layer not in layers: fail(f"layer {layer} missing")
        if "global_aggregate" not in layers[layer]: fail(f"layer {layer} missing global_aggregate")
    eta = m.get("time_remaining_excluding_graphics_audio_art", {})
    for k in ("aggressive", "realistic", "prudent"):
        if k not in eta: fail(f"eta.{k} missing")
    forb = m.get("forbidden_in_track_h_respected", {})
    if forb.get("runtime_changes") is not False: fail("runtime_changes must be False")
    if forb.get("db_writes") is not False: fail("db_writes must be False")
    print("[PASS] PROJECT_E Track H DoD recalibration OK: 3 layers, global aggregate 95% technical, 20% graphics, 60% live-ops; ETA aggressive/realistic/prudent set")
    sys.exit(0)

if __name__ == "__main__": main()

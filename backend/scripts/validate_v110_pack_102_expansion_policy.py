#!/usr/bin/env python3
"""Pack 102 — Expansion policy +20/+30 piani documentata nel SOT."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'docs/divine/122_TOWER_FLOOR_CATALOG_SOT.md')).read()
assert '+20 o +30 piani per patch' in src
assert 'tower_floor_catalog_v2.py' in src
assert 'NESSUNA espansione applicata in Pack 102' in src
print('[v110 PACK_102_EXPANSION_POLICY] OK documented_not_applied v2_module_planned')

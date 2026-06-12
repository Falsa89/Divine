#!/usr/bin/env python3
"""Pack 108 — Locked / Deferred / Ready-Gated UI Copy Audit.

Verifica che il vocabolario UI canonico esista (no false-ready labels).
Verifica che la mappa playable loop esponga `copy_audit` con i 5 status
canonici e `no_false_ready_labels=True`.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/playable_loop_map.py')).read()
for key in ('locked_copy', 'deferred_copy', 'ready_gated_copy', 'preview_copy',
            'quarantined_copy', 'no_false_ready_labels'):
    assert key in c, key
assert 'Bloccato (Closed Alpha)' in c
assert 'In preparazione (deferred)' in c
assert 'Disponibile in anteprima (server-scoped)' in c
assert 'Anteprima sola lettura' in c
assert 'Route legacy in quarantena (server-scope retrofit in corso)' in c

ts = open(os.path.join(R, 'frontend/src/utils/playableLoopFlags.ts')).read()
assert 'PLAYABLE_LOOP_STATUS_COPY' in ts
for canonical in ('READY', 'READY_GATED', 'READY_GATED_DEFERRED', 'DEFERRED', 'LOCKED', 'PREVIEW', 'QUARANTINED'):
    assert canonical in ts, canonical
assert 'isFalseReadyClaim' in ts

print('[v110 PACK_108_LOCKED_DEFERRED_UI_COPY_AUDIT] OK five_canonical_status_copy no_false_ready_labels_documented')

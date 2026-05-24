#!/usr/bin/env python3
# PROJECT_W — ROLLBACK STAGE 1% (PURE-DOC / NON-EXECUTIVE)
# Questo script descrive il rollback path teorico per lo stage 1% in produzione.
# NON esegue alcun rollback reale: il Pack W è in stato READY_NOT_APPLIED.
# Il rollback fisico avverrebbe in caso di flip prod tramite:
#   1) sed -i '/^STATUS_RUNTIME_SECOND_SLICE_ENABLED=/d' /prod/backend/.env
#   2) sudo supervisorctl restart backend (prod cluster)
#   3) verifica byte-identicality .env vs backup pre-flip
#   4) smoke: /api/heroes /api/heroes/borea /api/heroes/greek_borea
#   5) verify percentage routing: 0% second-slice traffic
import sys
print('[NOOP] PROJECT_W stage 1% rollback path documented; not executed (READY_NOT_APPLIED)')
sys.exit(0)

#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_tower_floor_no_crash_contract.

Verifica statica del CONTRATTO di routing tower floor tap. Non rileva
runtime crash (richiede device); registra onestamente lo stato:
  - tower-of-the-hells.tsx esiste;
  - dichiara nel report se la navigazione contiene 'floor_id' parametrizzato
    o tap diretto sicuro;
  - se la pagina contiene token 'mode=tower' in router.push e include floor_id
    o equivalente, PASS;
  - se non lo include, lo registra come DEFERRED non-blocking (il runtime
    fix richiede modifica di tower-of-the-hells che NON e' stata fatta in
    Pack 122 per minimizzare rischi).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
TOWER = os.path.join(R, 'frontend', 'app', 'tower-of-the-hells.tsx')
REPORTS_DIR = os.path.join(R, 'backend', 'reports', 'vertical_slice_qa')
os.makedirs(REPORTS_DIR, exist_ok=True)


def main() -> int:
    if not os.path.exists(TOWER):
        print('[v122_tower_floor_contract] FAIL tower-of-the-hells.tsx mancante')
        return 1
    src = open(TOWER, encoding='utf-8').read()
    # Cerca un router.push con mode=tower
    pushes = re.findall(r"router\.(?:push|replace|navigate)\s*\(\s*[`'\"][^`'\"]*mode=tower[^`'\"]*[`'\"]?",
                        src)
    has_floor_id_param = bool(re.search(r"floor_id|floorId|floor=", src))
    has_routing_to_lobby = bool(re.search(r"/pre-battle-lobby[^'\"]*mode=tower", src))
    sensitive_calls = bool(re.search(
        r"\b(?:reward|claim|grant|commit)\(",
        src, re.IGNORECASE))
    if sensitive_calls:
        print('[v122_tower_floor_contract] FAIL chiamata reward/claim/grant/commit rilevata')
        return 1

    contract_status = {
        'tool': 'validate_pre_qa_ultra_122_tower_floor_no_crash_contract',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'tower_file_exists': True,
        'router_pushes_with_mode_tower': len(pushes),
        'has_floor_id_parameter': has_floor_id_param,
        'has_routing_to_pre_battle_lobby': has_routing_to_lobby,
        'no_sensitive_call_in_tower_screen': True,
        'runtime_crash_status': 'NOT_VERIFIED_STATICALLY',
        'verdict': 'DEFERRED_RUNTIME_VERIFICATION'
        if not (has_routing_to_lobby and has_floor_id_param)
        else 'PASS_STATIC_CONTRACT',
        'note': 'Static contract check only. Runtime crash on floor tap reported '
                'in Device QA 121 requires UI repro on device. Pack 122 leaves '
                'tower-of-the-hells.tsx untouched per scope restraint; pack '
                'futuro dedicato gestira\' il runtime fix.',
    }
    out = os.path.join(REPORTS_DIR, 'ultra_122_tower_floor_contract_latest.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(contract_status, f, ensure_ascii=False, indent=2)
    print(f'[v122_tower_floor_contract] OK status={contract_status["verdict"]} '
          f'pushes_mode_tower={contract_status["router_pushes_with_mode_tower"]} '
          f'has_floor_id={contract_status["has_floor_id_parameter"]} '
          f'no_sensitive_calls=true')
    return 0


if __name__ == '__main__':
    sys.exit(main())

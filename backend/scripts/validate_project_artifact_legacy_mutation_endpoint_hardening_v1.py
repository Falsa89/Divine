#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_LEGACY_MUTATION_ENDPOINT_HARDENING master validator.

Verifica STATICA + smoke runtime opzionale (no fake PASS):
  - Track A: audit endpoint inventory presente e coerente.
  - Track B: tutti i 7 POST mutativi nel modulo sono hard-lockati:
      * nessuna dipendenza da get_current_user,
      * nessun request body,
      * nessuna chiamata DB (insert/update/find_one/find/delete),
      * nessun random/spend/grant.
  - Track C: contratto envelope corretto (codici 423, codici stringa lock).
  - Track D: frontend e gacha guards intatti, artifacts-preview MD5 stabile.
  - Track E: invarianti MD5 su battle_engine.py e backend/.env.
  - Track H: completion JSON coerente.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
HARD_DIR = ROOT / 'data/design/artifacts/hardening'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'

LOCKED_POST_PATHS = [
    "/artifacts/fuse",
    "/artifacts/pull",
    "/artifacts/pull10",
    "/constellations/equip",
    "/constellations/fuse",
    "/constellations/pull",
    "/constellations/pull10",
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def extract_handler_body(route_src: str, post_path: str) -> str:
    """
    Estrae il corpo del handler per @router.post("<post_path>"). Ritorna
    il blocco di codice fino al prossimo decoratore @router.post/get o
    alla riga di chiusura della funzione.
    """
    pattern = re.compile(
        rf'@router\.post\("{re.escape(post_path)}"\).*?\n((?:    .*\n)+)',
        re.MULTILINE,
    )
    m = pattern.search(route_src)
    assert m, f"handler block not found for {post_path}"
    return m.group(0)


def main():
    # ---- Source files exist
    src = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in src, "RO catalog must remain"
    assert '@router.get("/artifacts/catalog/preview")' in src, "RO preview must remain"
    assert 'ARTIFACT_MUTATION_LOCK_ENVELOPE' in src
    assert 'CONSTELLATION_MUTATION_LOCK_ENVELOPE' in src
    assert 'ARTIFACT_MUTATION_LOCK_STATUS = 423' in src
    assert 'ARTIFACT_MUTATION_ENDPOINTS_LOCKED_V1 = True' in src
    assert 'from fastapi.responses import JSONResponse' in src

    # ---- Track A
    a = load('data/design/artifacts/hardening/artifact_legacy_mutation_endpoint_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_LEGACY_MUTATION_ENDPOINT_AUDIT_READY'
    locked_in_audit = {
        e['path'] for e in a['endpoints_inventory']
        if e.get('locked_in_this_pack') is True
    }
    expected_locked = {f"/api{p}" for p in LOCKED_POST_PATHS}
    assert locked_in_audit == expected_locked, \
        f"audit locked set mismatch: missing={expected_locked - locked_in_audit}, extra={locked_in_audit - expected_locked}"
    # GET catalog endpoints preserved in audit
    preserved = {
        e['path'] for e in a['endpoints_inventory']
        if e.get('preserved') is True
    }
    assert "/api/artifacts/catalog" in preserved
    assert "/api/artifacts/catalog/preview" in preserved
    # Frontend audit: no new mutation buttons + preview not modified
    fa = a['frontend_audit']
    assert fa['references_reachable_by_player'] is False
    assert fa['new_mutation_buttons_added_this_pack'] is False
    assert fa['artifacts_preview_tsx_modified'] is False

    # ---- Track B: ogni handler locked deve essere strutturalmente safe
    forbidden_db_patterns = [
        '.insert_one(', '.insert_many(',
        '.update_one(', '.update_many(',
        '.delete_one(', '.delete_many(',
        '.find_one(', '.find({',
        '.find_one_and_update(', '.find_one_and_replace(',
        'await db.', 'random.', 'ensure_server_scope(',
    ]
    for path in LOCKED_POST_PATHS:
        body = extract_handler_body(src, path)
        # No auth dependency
        assert 'Depends(get_current_user)' not in body, \
            f"{path} still depends on get_current_user"
        # No request body model
        assert 'BaseModel' not in body
        assert 'ArtifactFuseRequest' not in body, \
            f"{path} still consumes ArtifactFuseRequest body"
        assert 'EquipConstellationRequest' not in body, \
            f"{path} still consumes EquipConstellationRequest body"
        # No DB / random / scope helper
        for fp in forbidden_db_patterns:
            assert fp not in body, \
                f"{path} handler contains forbidden pattern '{fp}'"
        # Must return JSONResponse with lock status
        assert 'JSONResponse(' in body, f"{path} must return JSONResponse"
        assert 'ARTIFACT_MUTATION_LOCK_STATUS' in body, \
            f"{path} must use ARTIFACT_MUTATION_LOCK_STATUS"
        # Envelope choice per system
        if path.startswith('/artifacts/'):
            assert 'ARTIFACT_MUTATION_LOCK_ENVELOPE' in body, \
                f"{path} must use ARTIFACT_MUTATION_LOCK_ENVELOPE"
        elif path.startswith('/constellations/'):
            assert 'CONSTELLATION_MUTATION_LOCK_ENVELOPE' in body, \
                f"{path} must use CONSTELLATION_MUTATION_LOCK_ENVELOPE"

    # ---- Track C: response contract
    c = load('data/design/artifacts/hardening/artifact_mutation_lock_response_contract_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_LOCK_RESPONSE_CONTRACT_READY'
    assert c['http_status_used'] == 423
    env_a = c['artifact_lock_envelope']
    env_c = c['constellation_lock_envelope']
    assert env_a['code'] == 'ARTIFACT_MUTATION_ENDPOINT_LOCKED'
    assert env_a['locked'] is True and env_a['success'] is False
    assert env_a['system'] == 'artifacts'
    assert "GET /api/artifacts/catalog" in env_a['allowed_now']
    assert "GET /api/artifacts/catalog/preview" in env_a['allowed_now']
    assert env_c['code'] == 'CONSTELLATION_MUTATION_ENDPOINT_LOCKED'
    assert env_c['locked'] is True and env_c['success'] is False
    assert env_c['system'] == 'constellations'
    inv = c['handler_implementation_invariants']
    assert inv['depends_on_get_current_user'] is False
    assert inv['accepts_request_body'] is False
    assert inv['calls_db_module'] is False
    assert inv['returns_status_code'] == 423

    # ---- Track D: frontend / gacha guard recheck
    d = load('data/design/artifacts/hardening/artifact_frontend_gacha_guard_recheck_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_FRONTEND_AND_GACHA_GUARD_RECHECK_READY'
    chk = d['checks']
    assert chk['gacha_hidden_banners_v2_contains_artifact_and_constellation'] is True
    assert chk['artifacts_preview_tsx_unchanged_this_pack'] is True
    assert chk['new_mutation_buttons_added'] is False
    # Live re-check on actual files
    gacha = (ROOT / 'frontend/app/(tabs)/gacha.tsx').read_text()
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in gacha
    assert "if (HIDDEN_BANNERS_V2.has(banner)) {" in gacha
    assert "if (isActiveBannerLocked)" in gacha
    art_legacy = (ROOT / 'frontend/app/artifacts.tsx').read_text()
    assert "router.replace('/artifacts-preview')" in art_legacy
    # MD5 frontend preview deve matchare l'audit
    actual_preview_md5 = md5('/app/frontend/app/artifacts-preview.tsx')
    assert actual_preview_md5 == chk['artifacts_preview_tsx_md5'], \
        f"artifacts-preview.tsx MD5 drift: expected {chk['artifacts_preview_tsx_md5']}, got {actual_preview_md5}"

    # ---- Track E: smoke summary coerente
    e = load('data/design/artifacts/hardening/artifact_backend_smoke_locked_mutation_tests_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_BACKEND_SMOKE_LOCKED_MUTATION_TESTS_READY'
    inv2 = e['invariants']
    assert inv2['battle_engine_md5_unchanged'] is True
    assert inv2['backend_env_md5_unchanged'] is True
    assert inv2['frontend_artifacts_preview_unchanged'] is True
    assert inv2['no_db_write_in_pack'] is True
    # Verifica che TUTTI i 7 endpoint mutativi siano nel report smoke
    smoke_paths = {it['endpoint'] for it in e['locked_mutation_smoke']}
    for p in LOCKED_POST_PATHS:
        assert f"POST /api{p}" in smoke_paths, f"smoke report missing {p}"
    # Tutte le risposte smoke devono essere 423
    for it in e['locked_mutation_smoke']:
        assert it['http_status'] == 423
        assert it['db_write_observed'] is False
    # GET catalog smoke 200 + 32/10
    assert e['ro_catalog_smoke']['GET /api/artifacts/catalog']['http_status'] == 200
    assert e['ro_catalog_smoke']['GET /api/artifacts/catalog']['count'] == 32
    assert e['ro_catalog_smoke']['GET /api/artifacts/catalog/preview']['http_status'] == 200
    assert e['ro_catalog_smoke']['GET /api/artifacts/catalog/preview']['count'] == 10

    # ---- Track H: completion
    h = load('data/design/artifacts/hardening/artifact_legacy_mutation_endpoint_hardening_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_LEGACY_MUTATION_HARDENING_COMPLETION_READY'
    assert h['endpoints_locked_count'] == 7
    assert set(h['endpoints_locked']) == {f"POST /api{p}" for p in LOCKED_POST_PATHS}
    assert h['endpoint_artifacts_equip_added_this_pack'] is False
    rc = h['runtime_changes_made']
    assert rc['frontend_ui_changes'] == 0
    assert rc['frontend_logic_changes'] == 0
    assert rc['db_writes_from_scripts'] == 0
    assert rc['battle_engine_changes'] == 0
    assert rc['gacha_rate_changes'] == 0
    assert rc['new_mutation_endpoint_added'] is False
    for kb in ('iap_implementation', 'artifact_banner_activation',
               'constellation_banner_activation', 'character_bible_mutation',
               'inventory_state_added', 'ownership_state_added'):
        assert rc[kb] is False, f"{kb} must be False"
    assert h['artifact_mutation_endpoints_locked_v1'] is True

    # ---- Invariants MD5
    inv3 = h['invariants']
    assert md5('/app/backend/battle_engine.py') == inv3['backend/battle_engine.py']
    assert md5('/app/backend/.env') == inv3['backend/.env']
    assert md5('/app/frontend/app/artifacts-preview.tsx') == inv3['frontend/app/artifacts-preview.tsx']
    assert md5('/app/frontend/app/artifacts.tsx') == inv3['frontend/app/artifacts.tsx']
    assert md5('/app/frontend/app/(tabs)/gacha.tsx') == inv3['frontend/app/(tabs)/gacha.tsx']

    print('[PASS] PROJECT_ARTIFACT_LEGACY_MUTATION_ENDPOINT_HARDENING master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())

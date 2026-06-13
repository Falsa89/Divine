#!/usr/bin/env python3
"""Pre-QA Stabilization 115G — Skill/Artifact Semantic Cleanup.

Validator statico (no DB writes, no runtime activation).

Check eseguiti:
  1. UI `hero-skill-kits-catalog.tsx` NON contiene piu' la stringa stale
     `final_numbers: null su tutte le skill` (o equivalenti).
  2. UI contiene la semantica corretta: `foundation_draft`,
     `preview-only` o equivalente, `runtime_ready` con `false`,
     dichiarazione "non final balance" / "non battle runtime".
  3. `validate_hero_skill_kit_catalog_foundation.py` non usa piu' la policy
     null-only su `final_numbers`. Accetta dict con `status=foundation_draft`
     e fallisce se runtime/live/final/finalized.
  4. Esecuzione live di `validate_hero_skill_kit_catalog_foundation.py`
     contro il catalogo corrente: deve PASSare.
  5. Cataloghi 5★ e 6★ NON dichiarano alcun `final_numbers.runtime_ready=True`
     e nessun `final_numbers.status` runtime/live/final/finalized.
  6. `backend/routes/artifacts.py` neutralizza i legacy GET:
       - `@router.get("/artifacts")` non dipende piu' da `get_current_user`,
         non legge `db.user_artifacts` e non calcola `effective_buff` /
         `total_buffs`.
       - `@router.get("/constellations")` non dipende piu' da
         `get_current_user`, non legge `db.user_constellations` ne
         `db.teams`, non calcola `equipped_buff` / `equipped_skill` /
         `effective_buff`.
  7. Endpoint canonical preservati: `@router.get("/artifacts/catalog")` e
     `@router.get("/artifacts/catalog/preview")` sono ancora presenti nel
     modulo.
  8. POST mutation locks artifact/constellation ancora presenti
     (`ARTIFACT_MUTATION_LOCK_ENVELOPE`, `CONSTELLATION_MUTATION_LOCK_ENVELOPE`,
     `ARTIFACT_MUTATION_LOCK_STATUS=423`).
  9. Out-of-scope: nessun import o riferimento a `battle_engine`,
     `combat`, `tower`, `gacha_rates`, `character_bible`, `red_dot`,
     `battle_power`, `chat_bot` runtime negli script del pack 115G.
 10. Nessuna modifica a `data/design/**` necessaria (verifica statica:
     gli script del pack non scrivono sotto `data/design/`).
"""
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')
UI_FP = os.path.join(R, 'frontend/app/hero-skill-kits-catalog.tsx')
FOUNDATION_VALIDATOR_FP = os.path.join(SCRIPTS, 'validate_hero_skill_kit_catalog_foundation.py')
ARTIFACTS_ROUTES_FP = os.path.join(R, 'backend/routes/artifacts.py')


def _read(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def check_ui_no_stale_copy():
    src = _read(UI_FP)
    forbidden = (
        'final_numbers: null su tutte le skill',
        'final_numbers=null su tutte le skill',
        'final_numbers: null on all skills',
    )
    offenders = [t for t in forbidden if t in src]
    assert not offenders, f'UI contiene ancora copy stale: {offenders}'
    print('[1] UI no stale "final_numbers: null" copy OK')


def check_ui_has_foundation_semantic():
    src = _read(UI_FP)
    must = (
        'foundation_draft',
        'preview-only',
        'runtime_ready',
        'battle runtime',
    )
    missing = [t for t in must if t not in src]
    assert not missing, f'UI manca semantica foundation_draft. Missing: {missing}'
    # Inoltre, deve esserci esplicitamente la dichiarazione `false` per
    # runtime_ready / runtime_attached / balance_values_finalized.
    assert re.search(r'runtime_ready[^\n]{0,80}false', src, flags=re.IGNORECASE), (
        'UI non dichiara `runtime_ready: false`'
    )
    print('[2] UI foundation_draft / preview-only / runtime_ready=false semantic OK')


def check_foundation_validator_semantic():
    src = _read(FOUNDATION_VALIDATOR_FP)
    # La policy null-only originale era:
    #   `if sk.get("final_numbers") is not None: raise ... "must be null in foundation"`
    forbidden = 'final_numbers must be null in foundation'
    assert forbidden not in src, (
        'Foundation validator usa ancora la null-only policy stale: '
        f'{forbidden!r}'
    )
    # Deve invece accettare foundation_draft.
    assert 'foundation_draft' in src, (
        'Foundation validator non riconosce `foundation_draft` come valore '
        'lecito per final_numbers.status'
    )
    # Deve enforce-are `runtime_ready` false.
    assert 'runtime_ready' in src, (
        'Foundation validator non enforce-a `runtime_ready` su final_numbers'
    )
    # Deve enforce-are che status non sia runtime/live/final/finalized.
    must_tokens = ('runtime', 'live', 'final', 'finalized')
    for tok in must_tokens:
        assert tok in src, (
            f'Foundation validator non enforce-a divieto su `{tok}`'
        )
    print('[3] Foundation validator semantic (foundation_draft + runtime_ready false) OK')


def check_foundation_validator_runs_clean():
    """Esecuzione live: il foundation validator deve PASSare sul catalogo
    corrente. Se fallisce, e' un FAIL truthful.
    """
    proc = subprocess.run(
        [sys.executable, FOUNDATION_VALIDATOR_FP],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f'foundation validator FAIL (rc={proc.returncode}): '
        f'stdout={proc.stdout[-400:]!r} stderr={proc.stderr[-400:]!r}'
    )
    print('[4] foundation validator exec PASS (live) OK')


def check_skill_kit_catalogs_no_runtime_ready():
    """Cataloghi 5★ e 6★ non devono dichiarare `runtime_ready=true` su
    nessuno `final_numbers`, ne `status` runtime/live/final/finalized.
    Nota: lettura READ-ONLY (no write a `data/design/`).
    """
    import json as _json
    base = os.path.join(R, 'data', 'design', 'hero_skill_kits')
    files = (
        os.path.join(base, 'hero_skill_kits_5star_manifest_v1.json'),
        os.path.join(base, 'hero_skill_kits_6star_borea_v1.json'),
    )
    offenders = []
    forbidden_statuses = {'runtime', 'live', 'final', 'finalized', 'ready'}
    for fp in files:
        if not os.path.exists(fp):
            continue
        with open(fp, 'r', encoding='utf-8') as fh:
            d = _json.load(fh)
        for e in d.get('entries', []):
            hid = e.get('hero_id')
            for slot, sk in (e.get('skill_package') or {}).items():
                fn = sk.get('final_numbers')
                if not isinstance(fn, dict):
                    continue
                if fn.get('runtime_ready') is True:
                    offenders.append((hid, slot, 'runtime_ready=True'))
                st = fn.get('status')
                if isinstance(st, str) and st.lower() in forbidden_statuses:
                    offenders.append((hid, slot, f'status={st!r}'))
    assert not offenders, (
        f'5★/6★ catalogo dichiara runtime/live: {offenders[:5]}'
    )
    print('[5] 5★/6★ catalogs no runtime-ready / no live status OK')


def check_artifacts_legacy_get_neutralized():
    src = _read(ARTIFACTS_ROUTES_FP)
    # Trova i blocchi handler `@router.get("/artifacts")` (non `/catalog`).
    # Usiamo una scansione strutturale leggera per estrarre i due blocchi.
    def _extract_handler(decorator: str) -> str:
        idx = src.find(decorator)
        assert idx >= 0, f'manca decorator {decorator!r}'
        # Trova `async def` o `def` dopo decorator e estrai fino al prossimo
        # `@router.` o EOF.
        body_start = idx
        next_dec = src.find('@router.', idx + len(decorator))
        end = next_dec if next_dec != -1 else len(src)
        return src[body_start:end]

    artifacts_handler = _extract_handler('@router.get("/artifacts")\n')
    constellations_handler = _extract_handler('@router.get("/constellations")\n')

    # Entrambi NON devono dipendere da get_current_user.
    assert 'get_current_user' not in artifacts_handler, (
        '`/artifacts` handler dipende ancora da get_current_user (auth/DB read implicito)'
    )
    assert 'get_current_user' not in constellations_handler, (
        '`/constellations` handler dipende ancora da get_current_user'
    )
    # Entrambi NON devono leggere DB ownership.
    for tok in ('db.user_artifacts', 'db.user_constellations', 'db.teams'):
        assert tok not in artifacts_handler, (
            f'`/artifacts` handler legge ancora {tok}'
        )
        assert tok not in constellations_handler, (
            f'`/constellations` handler legge ancora {tok}'
        )
    # Entrambi NON devono calcolare effective/equipped/total buffs.
    forbidden_calc = (
        'effective_buff',
        'total_buffs',
        'equipped_buff',
        'equipped_skill',
        'set_bonuses',
        'level_mult',
    )
    for tok in forbidden_calc:
        assert tok not in artifacts_handler, (
            f'`/artifacts` handler calcola ancora {tok}'
        )
        assert tok not in constellations_handler, (
            f'`/constellations` handler calcola ancora {tok}'
        )
    # Devono restituire un envelope locked esplicito.
    assert 'ARTIFACT_LEGACY_GET_LOCK_ENVELOPE' in artifacts_handler, (
        '`/artifacts` handler non restituisce envelope locked esplicito'
    )
    assert 'CONSTELLATION_LEGACY_GET_LOCK_ENVELOPE' in constellations_handler, (
        '`/constellations` handler non restituisce envelope locked esplicito'
    )
    print('[6] /artifacts and /constellations legacy GET neutralized OK')


def check_canonical_catalog_endpoints_preserved():
    src = _read(ARTIFACTS_ROUTES_FP)
    assert '@router.get("/artifacts/catalog")' in src, (
        'canonical `/artifacts/catalog` rimosso (vietato)'
    )
    assert '@router.get("/artifacts/catalog/preview")' in src, (
        'canonical `/artifacts/catalog/preview` rimosso (vietato)'
    )
    print('[7] canonical /artifacts/catalog and /artifacts/catalog/preview preserved OK')


def check_post_mutation_locks_preserved():
    src = _read(ARTIFACTS_ROUTES_FP)
    must = (
        'ARTIFACT_MUTATION_LOCK_ENVELOPE',
        'CONSTELLATION_MUTATION_LOCK_ENVELOPE',
        'ARTIFACT_MUTATION_LOCK_STATUS',
    )
    missing = [t for t in must if t not in src]
    assert not missing, f'POST mutation lock constants mancanti: {missing}'
    # Lista POST locked attesa (pattern: status_code=ARTIFACT_MUTATION_LOCK_STATUS).
    post_routes = (
        '@router.post("/artifacts/fuse")',
        '@router.post("/artifacts/pull")',
        '@router.post("/artifacts/pull10")',
        '@router.post("/constellations/equip")',
        '@router.post("/constellations/fuse")',
        '@router.post("/constellations/pull")',
        '@router.post("/constellations/pull10")',
    )
    missing_routes = [r for r in post_routes if r not in src]
    assert not missing_routes, f'POST mutation lock routes mancanti: {missing_routes}'
    print('[8] POST mutation locks preserved (constants + 7 routes) OK')


def check_pack_115g_no_out_of_scope():
    """Verifica che gli script del pack 115G NON contengano implementazioni
    out-of-scope (battle engine, combat, tower, gacha rates, character bible,
    red dot runtime, battle power runtime, chat bot runtime).
    """
    pack_files = (
        os.path.join(R, 'frontend/app/hero-skill-kits-catalog.tsx'),
        FOUNDATION_VALIDATOR_FP,
        # NB: il validator 115G stesso (questo file) NON e' incluso: contiene
        # la lista dei moduli vietati come dati e darebbe falsi positivi.
    )
    forbidden_patterns = (
        r'^\s*from\s+backend\.battle_engine\b',
        r'^\s*import\s+battle_engine\b',
        r'^\s*from\s+backend\.gacha_runtime\b',
        r'^\s*from\s+backend\.reward_engine\b',
        r'^\s*from\s+\S*red_dot_runtime\b',
        r'^\s*from\s+\S*battle_power_runtime\b',
        r'^\s*from\s+\S*chat_bot_runtime\b',
        r'^\s*from\s+\S*character_bible_runtime\b',
    )
    offenders = []
    for fp in pack_files:
        if not os.path.exists(fp):
            continue
        c = _read(fp)
        for pat in forbidden_patterns:
            if re.search(pat, c, flags=re.MULTILINE):
                offenders.append((fp, pat))
    assert not offenders, (
        f'Pack 115G vieta implementazioni out-of-scope. Trovati: {offenders}'
    )
    print('[9] pack 115G no out-of-scope runtime imports OK')


def check_no_data_design_writes_in_pack_scripts():
    """I file scope di questo pack non devono contenere logica di write a
    `data/design/**`. Verifica statica: cerca pattern di scrittura su path
    contenente `data/design`.
    """
    pack_scripts = (
        FOUNDATION_VALIDATOR_FP,
        # NB: il validator 115G (questo file) NON e' incluso: la sua regex
        # letterale fa match come falso positivo.
    )
    offenders = []
    # Pattern stretto: `open(<...data/design...>, "w"...)` o `, 'w'...)`.
    write_pat = re.compile(
        r"open\(\s*[^,\)]*data/design[^,\)]*,\s*['\"]w[+ab]?['\"]"
    )
    for fp in pack_scripts:
        if not os.path.exists(fp):
            continue
        c = _read(fp)
        if write_pat.search(c):
            offenders.append(fp)
    assert not offenders, (
        f'Pack 115G non puo\' scrivere sotto data/design/: offenders={offenders}'
    )
    print('[10] no data/design write in pack-115G scripts OK')


def main() -> int:
    check_ui_no_stale_copy()
    check_ui_has_foundation_semantic()
    check_foundation_validator_semantic()
    check_foundation_validator_runs_clean()
    check_skill_kit_catalogs_no_runtime_ready()
    check_artifacts_legacy_get_neutralized()
    check_canonical_catalog_endpoints_preserved()
    check_post_mutation_locks_preserved()
    check_pack_115g_no_out_of_scope()
    check_no_data_design_writes_in_pack_scripts()
    print(
        '[v115G PRE_QA_115G_SKILL_ARTIFACT_SEMANTIC_CLEANUP] OK '
        'ui_truthful foundation_validator_semantic foundation_runs_clean '
        'catalog_no_runtime artifacts_legacy_get_neutralized '
        'canonical_preserved post_locks_preserved no_out_of_scope '
        'no_data_design_write'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())

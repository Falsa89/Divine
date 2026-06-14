#!/usr/bin/env python3
"""Pre-QA Stabilization 116A-EXT — Hero Card Power + Bible Source Map validator.

Validator statico + (opzionale) curl-evidence live.

Check eseguiti (almeno):
  1. Source map JSON presente e parsabile:
        `data/design/battle_power/battle_power_bonus_source_map_v1.json`
  2. Source map contiene le 4 sezioni canoniche
       (`active_power_sources_now`, `deferred_canonical_power_sources`,
        `non_power_or_display_only_sources`, `unknown_requires_source_confirmation`)
     ed e' `design_only_read_only`.
  3. Source map cita le Bible richieste:
       - data/design/hero_stats_schema.json
       - hero_gear_progression_bible/B, D, E, F, G, I, J
       - artifacts/* + divine_weapons/* + cosmetics/* + team_synergies_v2 +
         synergy_codex_ui_requirements
  4. `backend/utils/battle_power.py` espone i nuovi simboli active/deferred
     e li include nei metadata builder.
  5. `backend/server.py` `/api/user/heroes` arricchisce con `power` 116A,
     usa batch-load `db.heroes.find({"id": {"$in": ...}})` (no N+1).
  6. `backend/routes/hero_progression.py` `hero/full-detail` usa
     `compute_hero_battle_power_v1` come fonte di `power`.
  7. `frontend/app/(tabs)/heroes.tsx` rende un badge `⚡ <power>` con
     fallback `—` per power assente/0, e NON introduce chiamate N+1
     (`apiCall` non e' invocata DENTRO il render map della card).
  8. Pre-QA safety suite include il validator 116A-EXT.
  9. Out-of-scope: nessun import/touch a battle_engine, combat runtime,
     gacha rates, character_bible runtime, red_dot runtime, chat_bot runtime,
     gear runtime activation, etc. negli script del pack.
 10. Source map non viene scritto a runtime: nessun `open(... 'w' ...)` con
     path `data/design/battle_power/` negli script del pack (read-only).
 11. (live) `GET /api/battle-power/metadata` mostra active/deferred
     semantics (campi `active_power_sources_now` e
     `deferred_canonical_power_sources` presenti). Skip
     SKIPPED_BACKEND_DOWN se backend non e' up.
"""
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')

SOURCE_MAP_FP = os.path.join(R, 'data', 'design', 'battle_power', 'battle_power_bonus_source_map_v1.json')
UTIL_FP = os.path.join(R, 'backend', 'utils', 'battle_power.py')
SERVER_FP = os.path.join(R, 'backend', 'server.py')
HERO_PROGRESSION_FP = os.path.join(R, 'backend', 'routes', 'hero_progression.py')
HEROES_TSX_FP = os.path.join(R, 'frontend', 'app', '(tabs)', 'heroes.tsx')
SUITE_FP = os.path.join(SCRIPTS, 'run_pre_qa_safety_validator_suite.py')

METADATA_URL = 'http://127.0.0.1:8001/api/battle-power/metadata'


def _read(fp: str) -> str:
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


# ---- [1] Source map exists + valid JSON ------------------------------------
def check_source_map_exists():
    assert os.path.exists(SOURCE_MAP_FP), f'manca {SOURCE_MAP_FP}'
    try:
        data = json.loads(_read(SOURCE_MAP_FP))
    except json.JSONDecodeError as e:
        raise AssertionError(f'source map JSON non valido: {e}')
    assert isinstance(data, dict), 'source map non e\' un dict'
    meta = data.get('_meta', {})
    assert meta.get('scope') == 'design_only_read_only', (
        'source map._meta.scope deve essere `design_only_read_only`'
    )
    assert meta.get('is_runtime') is False, (
        'source map._meta.is_runtime deve essere False'
    )
    assert meta.get('battle_power_formula_version') == 'battle_power_v1_preqa_derived', (
        'source map._meta.battle_power_formula_version inatteso'
    )
    print('[1] source map present + valid JSON OK')


# ---- [2] Source map 4 sections present -------------------------------------
def check_source_map_sections():
    data = json.loads(_read(SOURCE_MAP_FP))
    required_sections = (
        'active_power_sources_now',
        'deferred_canonical_power_sources',
        'non_power_or_display_only_sources',
        'unknown_requires_source_confirmation',
    )
    for sect in required_sections:
        assert sect in data, f'source map manca sezione {sect!r}'
        assert isinstance(data[sect], list), f'sezione {sect!r} non e\' una lista'
        # Active e deferred devono essere non-vuote.
        if sect in ('active_power_sources_now', 'deferred_canonical_power_sources'):
            assert len(data[sect]) > 0, f'sezione {sect!r} e\' vuota (non accettabile)'
        for entry in data[sect]:
            assert isinstance(entry, dict), f'entry malformata in {sect}'
            for required_field in (
                'source_id', 'display_name_it', 'category', 'scope',
                'battle_power_role', 'runtime_state',
                'active_in_formula_116a_ext', 'requires_future_resolver',
                'notes',
            ):
                assert required_field in entry, (
                    f'entry {entry.get("source_id")!r} in {sect} manca campo {required_field!r}'
                )
            # active section: active_in_formula_116a_ext deve essere True.
            if sect == 'active_power_sources_now':
                assert entry['active_in_formula_116a_ext'] is True, (
                    f'entry {entry["source_id"]!r} in active section deve avere '
                    f'active_in_formula_116a_ext=true'
                )
            # deferred section: active_in_formula_116a_ext deve essere False
            # e requires_future_resolver=True.
            if sect == 'deferred_canonical_power_sources':
                assert entry['active_in_formula_116a_ext'] is False, (
                    f'entry deferred {entry["source_id"]!r} deve avere active=false'
                )
                assert entry['requires_future_resolver'] is True, (
                    f'entry deferred {entry["source_id"]!r} deve avere requires_future_resolver=true'
                )
    print('[2] source map has 4 canonical sections with required fields OK')


# ---- [3] Source map cites required Bibles ---------------------------------
def check_source_map_cites_bibles():
    data = json.loads(_read(SOURCE_MAP_FP))
    # Raccogli TUTTE le source_refs.
    all_refs = []
    for sect_name in (
        'active_power_sources_now',
        'deferred_canonical_power_sources',
        'non_power_or_display_only_sources',
        'unknown_requires_source_confirmation',
    ):
        for entry in data.get(sect_name, []):
            for r in entry.get('source_refs', []):
                all_refs.append(r)
    # Bible che DEVONO essere citate almeno una volta nel source map.
    required_bibles = (
        'data/design/hero_stats_schema.json',
        'data/design/hero_gear_progression_bible/B_hero_progression_layer_bible_v1.json',
        'data/design/hero_gear_progression_bible/D_gear_progression_bible_v1.json',
        'data/design/hero_gear_progression_bible/E_gem_socket_system_bible_v1.json',
        'data/design/hero_gear_progression_bible/F_rune_scroll_talisman_system_bible_v1.json',
        'data/design/hero_gear_progression_bible/G_artifact_divine_weapon_separation_rules_v1.json',
        'data/design/hero_gear_progression_bible/I_bp_delta_and_guide_tutorial_integration_v1.json',
        'data/design/artifacts/artifact_system_direction_v1.json',
        'data/design/artifacts/artifact_bible_schema_v1.json',
        'data/design/artifacts/artifact_bible_launch_draft_v1.json',
        'data/design/divine_weapons/divine_weapon_requirements_v1.json',
        'data/design/divine_weapons/divine_weapon_schema_v1.json',
        'data/design/divine_weapons/divine_weapons_catalog_v1.json',
        'data/design/team_synergies_v2_initial_10.json',
        'data/design/synergy_codex_ui_requirements.json',
        'data/design/cosmetics/cosmetic_system_policy_v1.json',
        'data/design/cosmetics/cosmetic_bonus_schema_v1.json',
        'data/design/cosmetics/cosmetic_power_cap_policy_v1.json',
        'data/design/cosmetics/cosmetic_rarity_bonus_table_v1.json',
        'data/design/cosmetics/title_catalog_schema_v1.json',
        'data/design/cosmetics/skin_catalog_schema_v1.json',
    )
    missing = [b for b in required_bibles if b not in all_refs]
    assert not missing, f'source map non cita: {missing}'
    # Verifica che ognuno dei file Bible citati esista veramente sul disco.
    referenced_files = set(all_refs) | {data.get('implementation_roadmap_ref'), data.get('bp_delta_guide_ref')}
    referenced_files.discard(None)
    referenced_files.discard('')
    for ref in referenced_files:
        # Skip non-data refs (e.g. backend/utils/*) for the existence check.
        full = os.path.join(R, ref)
        assert os.path.exists(full), f'source map cita un file inesistente: {ref}'
    print('[3] source map cites all required Bibles + all references resolvable OK')


# ---- [4] battle_power.py exposes active/deferred --------------------------
def check_util_active_deferred():
    c = _read(UTIL_FP)
    must = (
        'BATTLE_POWER_ACTIVE_POWER_SOURCES_NOW',
        'BATTLE_POWER_DEFERRED_CANONICAL_POWER_SOURCES',
        'BATTLE_POWER_EXCLUDED_FROM_CURRENT_FORMULA_ONLY',
        'BATTLE_POWER_BONUS_SOURCE_MAP_PATH',
    )
    missing = [m for m in must if m not in c]
    assert not missing, f'utility manca simboli 116A-EXT: {missing}'
    # build_battle_power_metadata deve esporre i nuovi campi.
    must_keys = (
        '"active_power_sources_now"',
        '"deferred_canonical_power_sources"',
        '"excluded_from_current_formula_only"',
        '"bonus_source_map_path"',
    )
    missing_keys = [k for k in must_keys if k not in c]
    assert not missing_keys, f'metadata builder non espone: {missing_keys}'
    # Compat preserved.
    assert 'BATTLE_POWER_EXCLUDED_SOURCES' in c, (
        'compatibility-break: BATTLE_POWER_EXCLUDED_SOURCES non piu\' esposto'
    )
    print('[4] utility battle_power.py exposes active/deferred + bonus_source_map_path OK')


# ---- [5] /api/user/heroes enriches with power + batch load ----------------
def check_user_heroes_endpoint_enriched():
    c = _read(SERVER_FP)
    # Localizza il blocco server-scoped (dopo `Filtro REALE su {user_id, server_id}`).
    idx = c.find('Filtro REALE su {user_id, server_id}')
    assert idx >= 0, 'server.py non contiene il blocco server-scoped atteso'
    block = c[idx:idx + 4000]
    # 1) batch load (no N+1).
    assert 'db.heroes.find({"id": {"$in"' in block, (
        '`/api/user/heroes` server-scoped NON usa batch-load `db.heroes.find({"id": {"$in": ...}})`'
    )
    # 2) NON deve esserci `await db.heroes.find_one(...)` DENTRO il for loop
    #    server-scoped (sarebbe N+1). Cerca dentro il blocco.
    # Strict regex: `for uh in user_heroes:` seguito da `await db.heroes.find_one`.
    if re.search(r'for\s+uh\s+in\s+user_heroes:.*?await\s+db\.heroes\.find_one', block, re.DOTALL):
        # Solo errore se il match e' DENTRO il primo for (server-scoped).
        first_for = block.find('for uh in user_heroes:')
        next_for = block.find('for uh in user_heroes:', first_for + 1) if first_for >= 0 else -1
        # Server-scoped block: from first_for to next_for (or end of block).
        end = next_for if next_for != -1 else len(block)
        server_scoped_segment = block[first_for:end]
        if 'await db.heroes.find_one' in server_scoped_segment:
            raise AssertionError(
                'N+1: `/api/user/heroes` server-scoped chiama `db.heroes.find_one` dentro il for-loop'
            )
    # 3) Arricchimento power presente nel result.
    assert '"power": ' in block or "'power': " in block, (
        '`/api/user/heroes` server-scoped non arricchisce con `power`'
    )
    assert 'battle_power_formula_version' in block, (
        '`/api/user/heroes` non dichiara battle_power_formula_version nell\'envelope'
    )
    assert 'compute_hero_battle_power_v1' in block, (
        '`/api/user/heroes` non usa compute_hero_battle_power_v1'
    )
    print('[5] /api/user/heroes server-scoped enriched with power (batch-load, no N+1) OK')


# ---- [6] hero/full-detail uses 116A helper --------------------------------
def check_hero_full_detail_uses_116a_helper():
    c = _read(HERO_PROGRESSION_FP)
    # Deve importare il helper.
    assert 'compute_hero_battle_power_v1' in c, (
        'hero_progression.py non importa compute_hero_battle_power_v1'
    )
    # Deve usarlo per `power` nel return di hero/full-detail.
    idx = c.find('@router.get("/hero/full-detail/{user_hero_id}")')
    assert idx >= 0, 'hero_progression.py non ha hero/full-detail'
    block = c[idx:idx + 3500]
    # Non deve usare piu' `calculate_hero_power(hero, uh)` come fonte finale di
    # `power` in questa route (il legacy resta solo come parametro disponibile).
    final_power_legacy = re.search(r'"power":\s*calculate_hero_power\s*\(', block)
    assert not final_power_legacy, (
        'hero/full-detail usa ancora calculate_hero_power come fonte finale di power'
    )
    assert re.search(r'"power":\s*_compute_hero_bp_v1\s*\(', block), (
        'hero/full-detail non usa _compute_hero_bp_v1 come fonte di power'
    )
    print('[6] hero/full-detail uses compute_hero_battle_power_v1 as power source OK')


# ---- [7] heroes.tsx card power badge + no N+1 ------------------------------
def check_heroes_tsx_card_badge():
    c = _read(HEROES_TSX_FP)
    # Badge ⚡ + fallback `—`.
    assert re.search(r"['\"]?\\u26A1['\"]?", c) or '\u26A1' in c, (
        'heroes.tsx non rende l\'icona ⚡ (\\u26A1)'
    )
    assert 'h.power' in c, 'heroes.tsx non legge `h.power` dal payload'
    assert '\\u2014' in c or '\u2014' in c, (
        'heroes.tsx non mostra il fallback `—` (\\u2014) per power assente'
    )
    # NIENTE chiamate N+1 dentro il render della card.
    # Cerca apiCall DENTRO la chiusura del `filtered.map`.
    map_start = c.find('filtered.map')
    assert map_start >= 0, 'heroes.tsx non contiene filtered.map (render della card)'
    # Trova la fine del map: contiamo bracket matching.
    depth = 0
    end = map_start
    in_map = False
    for i in range(map_start, len(c)):
        ch = c[i]
        if ch == '(' :
            depth += 1
            in_map = True
        elif ch == ')':
            depth -= 1
            if in_map and depth == 0:
                end = i
                break
    map_block = c[map_start:end + 1]
    # Vietato: `apiCall(` ovunque dentro il map block.
    if re.search(r'\bapiCall\s*\(', map_block):
        raise AssertionError(
            'heroes.tsx: chiamata apiCall N+1 dentro filtered.map (render della card)'
        )
    print('[7] heroes.tsx card: ⚡ badge + fallback `—` + no N+1 OK')


# ---- [8] suite registers 116A-EXT ------------------------------------------
def check_suite_registration():
    c = _read(SUITE_FP)
    must = 'validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py'
    assert must in c, f'pre-QA safety suite non registra 116A-EXT: manca {must!r}'
    print('[8] pre-QA safety suite registers 116A-EXT validator OK')


# ---- [9] no out-of-scope ---------------------------------------------------
def check_no_out_of_scope():
    # NB: `backend/server.py` e' un file legacy multi-thousand-line con import
    # storici (es. `battle_engine`) preesistenti a questo pack. La regola
    # "no out-of-scope" qui vale per le UNITA' che 116A-EXT introduce/scope-
    # bounded: helper, validator (auto-escluso), source map, heroes.tsx,
    # hero_progression.py. Per server.py la regola si applica solo al BLOCCO
    # `/api/user/heroes` server-scoped (vedi check_user_heroes_endpoint_enriched).
    pack_files = (
        UTIL_FP,
        HERO_PROGRESSION_FP,
        HEROES_TSX_FP,
        SOURCE_MAP_FP,
    )
    forbidden_patterns = (
        r'^\s*from\s+\S*battle_engine\b',
        r'^\s*import\s+\S*battle_engine\b',
        r'^\s*from\s+\S*combat_runtime\b',
        r'^\s*from\s+\S*gacha_rates_runtime\b',
        r'^\s*from\s+\S*character_bible_runtime\b',
        r'^\s*from\s+\S*red_dot_runtime\b',
        r'^\s*from\s+\S*battle_power_runtime\b',
        r'^\s*from\s+\S*chat_bot_runtime\b',
        r'^\s*from\s+\S*gear_runtime\b',
        r'^\s*from\s+\S*divine_weapon_runtime\b',
    )
    offenders = []
    for fp in pack_files:
        if not os.path.exists(fp):
            continue
        c = _read(fp)
        for pat in forbidden_patterns:
            if re.search(pat, c, flags=re.MULTILINE):
                offenders.append((os.path.basename(fp), pat))
    assert not offenders, f'out-of-scope import detected: {offenders}'
    # Sanity sul blocco `/api/user/heroes` server-scoped di server.py:
    # deve importare SOLO `utils.battle_power` (no battle_engine, etc.).
    c_server = _read(SERVER_FP)
    server_scoped_idx = c_server.find('Filtro REALE su {user_id, server_id}')
    if server_scoped_idx >= 0:
        block = c_server[server_scoped_idx:server_scoped_idx + 4000]
        for pat in forbidden_patterns:
            if re.search(pat, block, flags=re.MULTILINE):
                raise AssertionError(
                    f'/api/user/heroes server-scoped block contiene out-of-scope import {pat!r}'
                )
    print('[9] no out-of-scope imports across pack-116A-EXT scoped files OK')


# ---- [10] no runtime writes to source map ----------------------------------
def check_no_runtime_writes_to_source_map():
    write_pat = re.compile(
        r"open\(\s*[^,\)]*battle_power_bonus_source_map[^,\)]*,\s*['\"]w[+ab]?['\"]"
    )
    files_to_audit = (UTIL_FP, SERVER_FP, HERO_PROGRESSION_FP, HEROES_TSX_FP)
    offenders = []
    for fp in files_to_audit:
        if not os.path.exists(fp):
            continue
        c = _read(fp)
        if write_pat.search(c):
            offenders.append(fp)
    assert not offenders, f'runtime write a source map vietato: {offenders}'
    print('[10] no runtime writes to battle_power_bonus_source_map OK')


# ---- [11] runtime metadata semantics (active/deferred) --------------------
def _backend_up() -> bool:
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/health', timeout=2) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
        return False


def check_runtime_metadata_active_deferred():
    if not _backend_up():
        print('[11] SKIPPED_BACKEND_DOWN — runtime metadata semantics check skipped')
        return 'skipped'
    try:
        with urllib.request.urlopen(METADATA_URL, timeout=3) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            assert resp.status == 200, f'HTTP={resp.status}'
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
        raise AssertionError(f'metadata endpoint unreachable: {e}')
    d = json.loads(body)
    for k in ('active_power_sources_now', 'deferred_canonical_power_sources',
              'excluded_from_current_formula_only', 'bonus_source_map_path'):
        assert k in d, f'metadata endpoint non espone {k!r}'
    assert isinstance(d['active_power_sources_now'], list) and len(d['active_power_sources_now']) > 0
    assert isinstance(d['deferred_canonical_power_sources'], list) and len(d['deferred_canonical_power_sources']) > 0
    assert d['bonus_source_map_path'].endswith('battle_power_bonus_source_map_v1.json')
    print('[11] runtime metadata endpoint shows active/deferred semantics OK')
    return 'ok'


def main() -> int:
    check_source_map_exists()
    check_source_map_sections()
    check_source_map_cites_bibles()
    check_util_active_deferred()
    check_user_heroes_endpoint_enriched()
    check_hero_full_detail_uses_116a_helper()
    check_heroes_tsx_card_badge()
    check_suite_registration()
    check_no_out_of_scope()
    check_no_runtime_writes_to_source_map()
    rt = check_runtime_metadata_active_deferred()
    suffix = ' (runtime SKIPPED_BACKEND_DOWN)' if rt == 'skipped' else ''
    print(
        '[v116A_EXT PRE_QA_116A_EXT_HERO_CARD_POWER_AND_BIBLE_SOURCE_MAP] OK '
        'source_map_present sections_valid bibles_cited util_semantic '
        'user_heroes_enriched hero_detail_116a heroes_card_badge '
        'suite_registered no_out_of_scope no_runtime_writes_source_map '
        'runtime_metadata_active_deferred'
        + suffix
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())

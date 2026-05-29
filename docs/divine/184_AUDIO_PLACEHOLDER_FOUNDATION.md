# 184 — PROJECT AUDIO PLACEHOLDER FOUNDATION — DIVINE WAIFUS

## Verdetto locale
**`PROJECT_AUDIO_PLACEHOLDER_FOUNDATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `..._COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo "Save to GitHub → `main` → PUSH" e verifica manuale.

---

## Obiettivo
Secondo P0 della roadmap audit 182. Fornire una **foundation audio TEST minima** tracciabile e sostituibile, senza audio finale e senza broad runtime audio engine. Risolve `Audio/SFX/Music globale = NOT_FOUND / HIGH blocker` dell'audit 182.

**Modalità pack:** audio TEST placeholder foundation only. NO audio finale, NO voice acting, NO runtime engine, NO refactor combat/audio runtime.

## Markers
```
PROJECT_AUDIO_PLACEHOLDER_FOUNDATION_APPROVAL = true
PROJECT_ACCELERATION_MODE                     = AUDIO_TEST_PLACEHOLDER_FOUNDATION_ONLY
```

---

## Track summary

| Track | Output JSON | Output Doc | Verdict |
|---|---|---|---|
| **A** | `data/design/audio_placeholder/audio_surface_audit_v1.json` | `184A_AUDIO_SURFACE_AUDIT.md` | `TRACK_A_AUDIO_SURFACE_AUDIT_READY` |
| **B** | `test_audio_registry_and_manifest_v1.json` + `frontend/assets/audio/test_placeholders/manifest.json` | `184B_TEST_AUDIO_REGISTRY_AND_MANIFEST.md` | `TRACK_B_TEST_AUDIO_REGISTRY_AND_MANIFEST_READY` |
| **C** | `placeholder_audio_asset_generation_v1.json` + generator script + 12 WAV files | `184C_PLACEHOLDER_AUDIO_ASSET_GENERATION.md` | `TRACK_C_PLACEHOLDER_AUDIO_ASSET_GENERATION_READY` |
| **D** | `audio_runtime_attachment_policy_v1.json` | `184D_AUDIO_RUNTIME_ATTACHMENT_POLICY.md` | `TRACK_D_AUDIO_RUNTIME_ATTACHMENT_POLICY_READY` |
| **E** | `final_audio_replacement_audit_policy_v1.json` | `184E_FINAL_AUDIO_REPLACEMENT_AUDIT_POLICY.md` | `TRACK_E_FINAL_AUDIO_REPLACEMENT_AUDIT_POLICY_READY` |
| **F** | `validate_project_audio_placeholder_foundation_v1.py` + proof marker | (vedi sezione validator) | `TRACK_F_VALIDATOR_READY` |
| **G** | _(questo doc)_ | `184_AUDIO_PLACEHOLDER_FOUNDATION.md` | `TRACK_G_COMPLETION_READY` |

---

## 🎧 Audit audio (Track A)
- Pre-pack: **0** audio refs, **0** file audio, **0** librerie audio runtime in `package.json`
- Audit status `NOT_FOUND` da 182: **risolto** con foundation TEST (audio finale resta P3)

## 📜 Registry + Manifest (Track B)
- 12 audio entries registrate con tutti i 13 metadata keys richiesti
- Manifest `frontend/assets/audio/test_placeholders/manifest.json` con 12 entries
- 100% `audio_status=test_placeholder`
- 100% `replace_before_release=true`
- 100% `runtime_attached=false`
- 100% `final_audio_expected=true`
- 1 entry con `loop=true` (ambient placeholder)

## 🎶 Generazione audio (Track C)
12 file WAV generati proceduralmente con **Python stdlib only** (`wave` + `struct` + `math`). Mono 16kHz 16-bit PCM. AR envelope su tutti per anti-click.

| File | Size | Duration | Placeholder description |
|---|---|---|---|
| `test_ui_click.wav` | 1.6 KiB | 50ms | 1500Hz exponential decay click |
| `test_ui_confirm.wav` | 3.8 KiB | 120ms | 880Hz tone |
| `test_ui_back_cancel.wav` | 3.2 KiB | 100ms | descending chirp 660→330Hz |
| `test_ui_error_locked.wav` | 9.4 KiB | 300ms | dissonant 220+233Hz |
| `test_reward_basic.wav` | 15.7 KiB | 500ms | ascending chirp 440→880Hz |
| `test_notification_basic.wav` | 7.9 KiB | 250ms | B5+E6 chord |
| `test_mode_enter.wav` | 12.5 KiB | 400ms | ascending chirp 220→880Hz |
| `test_battle_start.wav` | 21.9 KiB | 700ms | 3-note C4-E4-G4 arpeggio |
| `test_battle_hit_soft.wav` | 2.5 KiB | 80ms | LFSR pseudo-noise pulse |
| `test_battle_victory_stinger.wav` | 46.9 KiB | 1500ms | 4-note ascending C5→C6 |
| `test_battle_defeat_stinger.wav` | 46.9 KiB | 1500ms | A4→A3 descending |
| `test_ambient_placeholder_loop.wav` | 125.0 KiB | 4000ms | 110Hz+110.7Hz detuned drone w/ fade-edges |
| **TOTAL** | **297.4 KiB** | | |

**Safety properties:** amplitude capped at 0.4 max int16, AR envelope anti-click, ambient loop fade-edges, deterministic procedural (no copyright). Chiaramente percepibili come placeholder durante QA.

## 🔌 Runtime attachment policy (Track D) — DESIGN-ONLY
- **Runtime engine selezionato:** NONE_INSTALLED (engine selection deferred to future pack)
- **Engine candidates:** expo-audio (preferred), expo-av (deprecated), react-native-sound (fallback)
- **`AUDIO_ENGINE_ENABLED = false`** | **`AUDIO_GLOBAL_DISABLED = true`** | **`AUDIO_CANARY_INTERNAL = false`**
- **`runtime_attached_in_this_pack = false`** | **`runtime_engine_implementation_in_this_pack = false`**
- Surface NON attached: tutte (home, battle, gacha, combat, soul-forge, locked surfaces)

### Safety constraints (per future runtime engine)
- Mai autoplay senza user interaction
- Mai play audio mentre VIP/BP/SHOP/ITEM_SHOP_LOCKED_V2 attivi
- Mai caricare placeholder in production (`replace_before_release` check)
- Mai hardcoded path (sempre via manifest + audio_key)
- Fail-safe: missing audio_key = silent no-op (mai crash)

### Roadmap futura (7 stage)
1. `AUDIO_RUNTIME_ENGINE_SELECTION_PACK`
2. `AUDIO_LOADER_AND_MANIFEST_CONSUMER_PACK`
3. `AUDIO_SETTINGS_UI_PACK`
4. `AUDIO_UI_HOOKS_CANARY_PACK`
5. `AUDIO_BATTLE_HOOKS_CANARY_PACK`
6. `AUDIO_AMBIENT_LOOPS_CANARY_PACK`
7. `FINAL_AUDIO_BGM_SFX_KIT_PACK`

## 🔄 Final audio replacement policy (Track E)
**Core rule:** Nessun build production se qualsiasi entry ha `replace_before_release=true` AND `audio_status != 'final_ready'`.

### Release gate blocking rules
- BLOCK se qualsiasi `replace_before_release=true`
- BLOCK se qualsiasi `audio_status` ∈ {`test_placeholder`, `placeholder_dev`}
- BLOCK se `frontend/assets/audio/test_placeholders/` ancora contiene file
- ALLOW solo se 100% `final_ready` + 100% `replace_before_release=false` + directory placeholders vuota/rimossa

### QA acceptance criteria pre-release (10 checks)
Vedi `184E` doc.

---

## 📊 Suite finale
```
Overall: PASS  (pass=714, fail=0, miss=0)
EXIT=0
```
🎯 **714/714 PASS** = baseline 713 + 1 nuovo `PROJECT-AUDIO-PLACEHOLDER-FOUNDATION`.

---

## 🔐 MD5 Invarianti (5/5 ✅)
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py        ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                    ✅ UNCHANGED
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py     ✅ UNCHANGED
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx     ✅ UNCHANGED
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx            ✅ UNCHANGED
```

### Frontend lock tokens preservati
- `VIP_LOCKED_V2` / `BP_LOCKED_V2` / `BP_PREMIUM_BUY_LOCKED_V2` / `SHOP_LOCKED_V2` / `ITEM_SHOP_LOCKED_V2` ✅
- `ARTIFACT_MUTATION_LOCK_STATUS = 423` ✅

---

## ❌ Conferma scope NON violato

| Categoria forbidden | Status |
|---|---|
| Audio finale / musica definitiva / voice acting | ❌ 0 |
| File audio grandi (>1.5MB cap) | ❌ 297 KiB totali |
| Audio copyrighted | ❌ 0 (stdlib procedural) |
| Broad audio engine / runtime audio import | ❌ 0 |
| `expo-av` / `expo-audio` / `react-native-sound` in package.json | ❌ 0 |
| Audio runtime attached a UI | ❌ 0 |
| Refactor combat / battle_engine / combat.tsx | ❌ 0 |
| Soul Forge changes | ❌ 0 (PROTECTED) |
| DB writes / Gacha / IAP/BP/VIP/Shop / Artifact / Character Bible changes | ❌ 0 |
| `.env` secrets | ❌ 0 |
| REQUIRED validator weakening / fake PASS | ❌ 0 |

---

## Validator & suite registration

### Validator OPTIONAL
- File: `backend/scripts/validate_project_audio_placeholder_foundation_v1.py` (286 righe)
- Tupla: `('PROJECT-AUDIO-PLACEHOLDER-FOUNDATION', 'validate_project_audio_placeholder_foundation_v1.py')`
- Risultato: **PASS**
- Asserts: 5 track JSON + 1 proof marker, 12 audio entries con 13 required metadata keys, 12 WAV file (header mono 16kHz 16-bit valid) totale <1.5MB, manifest.json 12 entries, generator script presente, no expo-av/expo-audio/react-native-sound in package.json, no audio runtime imports in product code, Soul Forge / battle_engine / combat.tsx NON toccati, MD5 invariants 5/5, lock tokens 5/5, Track A baseline `frontend_audio_directory_present=false`, Track C `external_audio_files_used=0` + `copyrighted_content_used=false` + `audio_engine_modifications=0`, Track D `runtime_attached_in_this_pack=false` + `AUDIO_ENGINE_ENABLED=false` + `AUDIO_GLOBAL_DISABLED=true`, Track E release gate blocking rules + QA acceptance.

### Strategia tripled-sentinel v12
1. **Top sentinel** (riga 14): `# PUBLIC_SYNC_TAG_RESYNC_v12: suite_runner_audio_placeholder_foundation_v12_2026_05_29`
2. **Sentinel inline**: `# AUDIO_PLACEHOLDER_FOUNDATION_REGISTRATION_SENTINEL`
3. **Proof marker JSON**: `data/design/audio_placeholder/audio_placeholder_suite_registration_proof_marker_v1.json`

---

## 📦 File creati / modificati

### Nuovi (21 file)
- 6 JSON in `data/design/audio_placeholder/` (5 track + 1 proof marker)
- 12 WAV in `frontend/assets/audio/test_placeholders/` (297 KiB totali)
- 1 manifest JSON in `frontend/assets/audio/test_placeholders/manifest.json`
- 1 generator script: `backend/scripts/generate_audio_test_placeholders_v1.py`
- 1 validator: `backend/scripts/validate_project_audio_placeholder_foundation_v1.py`
- 6 doc Italiano: `184_*` + `184A` + `184B` + `184C` + `184D` + `184E`

### Modificati (solo comments + 1 tupla)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+12 righe header v12 + 4 righe inline sentinel + tupla)

### Non modificati
- Tutti i file critici (battle_engine, .env, artifacts.py, battlepass.tsx, vip.tsx, combat.tsx, soul-forge.tsx, gacha.tsx, shop.tsx, item-shop.tsx, soul_forge.py, artifacts.tsx)
- Tutte le UI surfaces (no audio runtime attachment)
- `package.json` (no audio library aggiunta)

---

## 🔄 Public Repo Sync Verification — PENDING

### Stato locale ✅
- Suite custom Python: **714/714 PASS**
- Master validator audio: **PASS**
- MD5 invarianti: ✅ 5/5
- DB live: ✅ 0 write
- Surface lock: ✅ tutti attivi
- Audio runtime engine: ✅ NESSUNO installato
- Audio attached to UI: ✅ zero

### Azione richiesta utente
1. **Pannello Emergent → "Save to GitHub"** → branch **`main`** → **PUSH**

### Verifica manuale su GitHub.com
- ✅ `data/design/audio_placeholder/` con 6 file (5 design + 1 proof marker)
- ✅ `frontend/assets/audio/test_placeholders/` con 12 WAV + `manifest.json`
- ✅ `backend/scripts/generate_audio_test_placeholders_v1.py`
- ✅ `backend/scripts/validate_project_audio_placeholder_foundation_v1.py`
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` con sentinella v12, inline sentinel, tupla (count=1)
- ✅ `docs/divine/184_*` + `184A..184E`

Solo dopo conferma push → **`PROJECT_AUDIO_PLACEHOLDER_FOUNDATION_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_AUDIO_PLACEHOLDER_FOUNDATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

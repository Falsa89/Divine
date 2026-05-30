# 203 — PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME

**Pack ID:** `PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PACK`
**Sentinella:** `v22`
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v22_HERO_ELEVATION_RUNTIME`
**Data UTC:** 2026-05-30
**Phase:** 1 della roadmap Bible 202
**Verdict locale:** `PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## ✅ Runtime mode: **PREVIEW-ONLY** (NON mutation-enabled)

**Rationale**: Materiali/inventory non sono ancora pronti per spend sicuro (i 4 materiali `elevation_dust_common`, `elevation_crystal_rare`, `elevation_essence_epic`, `elevation_orb_legendary` non esistono in produzione). Policy: niente mutation runtime in questo pack.

## 📊 Risposte dirette

| Domanda | Risposta |
|---|---|
| Preview-only o mutation-enabled? | **PREVIEW-ONLY** ✅ |
| DB writes = ? | **0** (zero, in nessun punto) |
| Default E0? | **SÌ** via `DEFAULT_TIER_ID = "E0"` (backend) + `resolveHeroElevationTier(undefined)` → E0 (frontend) |
| UI badge appare dove? | `/hero-elevation-test` (sandbox deeplink-only). Hero list, hero detail, combat team panel → **DEFERRED** ad altro pack |
| Elevation separata da Star Up e Ascension? | **SÌ** (locked nel proof marker `separation_from_other_layers`) |
| Niente Gear/Gemme/Rune/Artifact/DW/BP Delta runtime? | **SÌ confermato** (locked nei `constraints_honored`) |

## 🎨 15 Tier canonici (E0..E14)

| tier_id | Colore | Label IT | Quality | Frame hex |
|---|---|---|---|---|
| E0 | Bianco | Bianco | 0 | `#e0e0ea` |
| E1 | Verde | Verde | 0 | `#3ddc84` |
| E2 | Verde | Verde +1 | 1 | `#3ddc84` |
| E3 | Blu | Blu | 0 | `#4a90e2` |
| E4 | Blu | Blu +1 | 1 | `#4a90e2` |
| E5 | Blu | Blu +2 | 2 | `#4a90e2` |
| E6 | Viola | Viola +1 | 1 | `#a96bff` |
| E7 | Viola | Viola +2 | 2 | `#a96bff` |
| E8 | Viola | Viola +3 | 3 | `#a96bff` |
| E9 | Oro | Oro +1 | 1 | `#ffb84a` |
| E10 | Oro | Oro +2 | 2 | `#ffb84a` |
| E11 | Oro | Oro +3 | 3 | `#ffb84a` |
| E12 | Rosso | Rosso +1 | 1 | `#ff5470` |
| E13 | Rosso | Rosso +2 | 2 | `#ff5470` |
| E14 | Rosso | Rosso +3 | 3 | `#ff5470` |

## 🛠️ Backend (preview-only, disabled-by-default)

**Router**: `backend/routes/hero_elevation_preview.py`
**Feature flag**: `HERO_ELEVATION_PREVIEW_ENABLED` (default `false` → HTTP 503)
**Server registration**: `backend/server.py` include `hero_elevation_preview_router`

| Endpoint | Behavior |
|---|---|
| `GET /api/hero/elevation/tiers` | 503 se flag off; altrimenti lista canonica dei 15 tier |
| `GET /api/hero/elevation/{hero_id}` | 503 se flag off; altrimenti `current_tier_id=E0` (no DB read in preview) |
| `POST /api/hero/elevation/{hero_id}/upgrade/preview` | 503 se flag off; altrimenti next tier + cost preview. **NO DB write, NO mutation, NO materiale speso** |

## 🖼️ Frontend (read-only)

| File | Ruolo |
|---|---|
| `frontend/constants/heroElevation.ts` | 15 tier + `resolveHeroElevationTier()` fallback E0 |
| `frontend/components/HeroElevationBadge.tsx` | Badge UI riusabile con cornice colore + label + quality `+1/+2/+3` |
| `frontend/app/hero-elevation-test.tsx` | Sandbox screen (`/hero-elevation-test` deeplink-only) mostra tutti i 15 tier |

## 🛡️ Vincoli onorati (tutti ✅)
- 🚫 No Gear +50 runtime / Forge / Fusion runtime
- 🚫 No Gemme runtime / Rune scroll/talisman runtime
- 🚫 No Artifact live bonus / unhide
- 🚫 No Divine Weapon runtime / Costellazioni / Reincarnation runtime
- 🚫 No BP Delta overlay runtime
- 🚫 No combat formula / battle_engine.py / combat.tsx changes
- 🚫 No Character Bible mutation / hero final_numbers
- 🚫 No gacha/pity, Shop/BP/VIP/IAP unlock, server profiles live
- 🚫 No broad DB migration / broad player data mutation / economy live changes
- 🚫 No final art/audio
- 🚫 No `_layout.tsx` / home / menu touch
- 🚫 No modifiche ai 5 file MD5-locked
- 🚫 No REQUIRED/OPTIONAL validator weakening
- 🚫 No fake PASS

## 📦 File creati (12) / modificato (1)
**Creati:**
- 6 JSON design tracks A→F + 1 proof marker in `data/design/hero_elevation_runtime/`
- `backend/routes/hero_elevation_preview.py`
- `backend/scripts/validate_project_hero_elevation_quality_frame_runtime_v1.py`
- `frontend/constants/heroElevation.ts`
- `frontend/components/HeroElevationBadge.tsx`
- `frontend/app/hero-elevation-test.tsx`
- `docs/divine/203_HERO_ELEVATION_QUALITY_FRAME_RUNTIME.md`

**Modificati:**
- `backend/server.py` (+5 righe: include router preview)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (tupla v22 OPTIONAL aggiunta, count = 1)

## ⚠️ Risk / Debt
1. **Mutation upgrade endpoint deferred**: nessun `POST /api/hero/elevation/{hero_id}/upgrade` (non `/preview`) implementato. Future pack `PROJECT_HERO_ELEVATION_QUALITY_FRAME_FULL_RUNTIME_MUTATION_PACK` quando materiali pronti.
2. **DB field `elevation_tier_id`** non scritto né letto. Future schema in `user_heroes`.
3. **Badge non integrato** in `/heroes` o combat team panel — deferred a pack futuro con autorizzazione esplicita.
4. **Guide Codex entry / Tutorial entry** non wirati in questo pack — deferred a `PROJECT_GUIDE_CODEX_FILL_GAPS_PACK` + `PROJECT_TUTORIAL_FIRST_UNLOCK_WIRING_PACK`.
5. **9 OPTIONAL validator legacy MD5-invariant** ancora falliscono (preesistenti dal pack home menu rewiring autorizzato, NON regressioni).

## 🚀 Istruzioni Save to GitHub
1. Premere "Save to GitHub"
2. Verificare:
   - 7 JSON in `data/design/hero_elevation_runtime/`
   - `backend/routes/hero_elevation_preview.py` + include in `server.py`
   - 3 file frontend (constants + badge + sandbox)
   - tupla `PROJECT-HERO-ELEVATION-QUALITY-FRAME-RUNTIME` nel suite runner
   - validator OPTIONAL
   - doc `203_HERO_ELEVATION_QUALITY_FRAME_RUNTIME.md`
3. Dopo verifica → promuovere a `PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PREVIEW_COMPLETE_PUBLIC_REPO_VERIFIED`

## 🔜 Next Recommended Pack
**`PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK`** (Phase 2 della Bible 202)

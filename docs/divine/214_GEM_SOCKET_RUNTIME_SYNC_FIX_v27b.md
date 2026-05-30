# 214 — PROJECT_GEM_SOCKET_RUNTIME_SYNC_FIX (v27b)

**Verdict locale**: `PROJECT_GEM_SOCKET_RUNTIME_SYNC_FIX_v27b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Verdict post-verifica GitHub main** (atteso, parent): `PROJECT_GEM_SOCKET_RUNTIME_PREVIEW_COMPLETE_PUBLIC_REPO_VERIFIED`

**Timestamp UTC**: 2026-05-30T18:00:00Z

---

## Motivo

Il parent `PROJECT_GEM_SOCKET_RUNTIME_PACK` è arrivato solo parzialmente su main:
- File `backend/routes/gem_socket_preview.py`, frontend, design JSON, validator, doc 213 → OK.
- `backend/server.py` non risultava registrare `gem_socket_preview_router` sul blob pubblico.
- `backend/scripts/run_hero_skill_kit_validator_suite.py` non risultava esporre sentinel v27 + tupla sul blob pubblico.

## Cosa fa questo pack

Micro-fix di **resync** mirato:

1. **`backend/scripts/run_hero_skill_kit_validator_suite.py`**: aggiunge solo commenti sentinella v27b
   sopra la tupla esistente (`PROJECT-GEM-SOCKET-RUNTIME` count rimane = 1).
2. **`backend/server.py`**: aggiunge solo commenti sentinella v27 + v27b sopra l'`include_router`
   già presente (force blob resnapshot). Nessuna logica modificata.

## Cosa NON fa

- **NO** edit a `backend/routes/gem_socket_preview.py` (route parent).
- **NO** edit al validator parent `validate_project_gem_socket_runtime_v1.py`.
- **NO** edit a frontend `gemSocket.ts`, `gem-socket-test.tsx`.
- **NO** edit a Material Raid, Forge legacy, Rune runtime.
- **NO** edit a `battle_engine.py`, `combat.tsx`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx`.
- **NO** edit a economy, gacha, BP/VIP/shop, Artifact, Divine Weapon.
- **NO** DB writes. **NO** nuova backend route. **NO** validator weakening.
- **NO** fake PASS. Tuple count parent = 1.

## Verifiche locali

- `grep` su `run_hero_skill_kit_validator_suite.py` per `v27` / `v27b` / `SYNC_FIX_v27b` / tupla → OK.
- `grep` su `server.py` per `PUBLIC_SYNC_TAG_v27_GEM_SOCKET_RUNTIME` / `RESYNC_v27b` / `include_router(gem_socket_preview_router)` → OK.
- Conteggio tupla parent = **1**.
- `py_compile` suite runner + server → OK.
- Validator parent (`validate_project_gem_socket_runtime_v1.py`) → **PASS**.
- Suite completa: `pass=709 fail=18 miss=0` (baseline OPTIONAL invariato).
- MD5 invarianti sui 5 file protetti → intatti.
- File route parent + validator parent + frontend Gem Socket + Material Raid + Forge + combat → **0 diff lines**.

## Rollback

Rimuovere i commenti sentinella v27b aggiunti a `server.py` e a `run_hero_skill_kit_validator_suite.py`.
La tupla e l'`include_router` esistenti non vanno toccati.

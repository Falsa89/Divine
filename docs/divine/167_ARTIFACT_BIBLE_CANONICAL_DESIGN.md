# 167 — PROJECT ARTIFACT BIBLE CANONICAL DESIGN

**Verdict locale container:** `PROJECT_ARTIFACT_BIBLE_CANONICAL_DESIGN_READY`
**Verdict sync pubblico:** `PROJECT_ARTIFACT_BIBLE_CANONICAL_DESIGN_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
(da promuovere a `COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo verifica branch `main` su GitHub `Falsa89/Divine`)

## Sommario

Pack **design-only** che fissa il canone degli Artefatti prima di qualunque
import, UI live, gacha, equip, craft o bonus. Nessuna attivazione, nessun
DB write, nessun cambiamento runtime.

## Track Verdicts

| Track | Verdict |
|---|---|
| A — Audit superfici esistenti | `TRACK_A_EXISTING_ARTIFACT_SURFACE_AUDIT_READY` |
| B — Taxonomy canonica | `TRACK_B_ARTIFACT_CANONICAL_TAXONOMY_READY` |
| C — Bible launch draft (32 entries) | `TRACK_C_ARTIFACT_BIBLE_LAUNCH_DRAFT_READY` |
| D — Boundary 5 sistemi | `TRACK_D_CONSTELLATION_AND_RELIC_BOUNDARY_READY` |
| E — Preview UI copy + lock policy | `TRACK_E_ARTIFACT_PREVIEW_UI_COPY_AND_LOCK_POLICY_READY` |
| F — Migration plan 10 stage | `TRACK_F_ARTIFACT_MIGRATION_AND_IMPORT_PLAN_READY` |
| G — Static guard + harness | `TRACK_G_ARTIFACT_STATIC_GUARD_BETA_HARNESS_READY` |
| H — Repo sync verification | `TRACK_H_ARTIFACT_BIBLE_PUBLIC_REPO_SYNC_READY` (pending push) |
| I — Completion | `TRACK_I_ARTIFACT_BIBLE_COMPLETION_READY` |

## Decisioni canoniche

1. **Artefatti** = collezione divina account-wide / prestige, **non** equipment.
2. **Costellazioni** = star-up / dupe / reincarnation, **separate** dagli artefatti.
3. **Divine Weapons** ≠ Artefatti; restano sistema separato hero-specific.
4. **Equipment / Runes** sono ortogonali agli artefatti.
5. Bible v1 launch draft: **32 entries**, nessuna stat P2W, nessun nome implica un eroe playable non in roster.
6. Placeholder backend legacy (Santo Graal, Occhio di Ra, Mjolnir, Yata, Idunn) **non vengono mostrati in /artifacts-preview**: la preview pesca solo dalla Bible canonica quando attiveremo la lettura design.

## Boundary (5 sistemi ortogonali)

| Sistema | Scope | Combat |
|---|---|---|
| Artifacts | account-wide collection | none ora; capped future |
| Constellations | per-hero star-up / dupe | hero growth (futuro) |
| Divine Weapons | hero signature | power expression |
| Equipment | per-hero gear | base stats |
| Runes | socket modifier | modifier per equip |

## Lock policy

- `/artifacts` → redirect a `/artifacts-preview`
- `/artifacts-preview` → read-only, no pull/equip/fuse/craft
- `gacha.tsx` → `HIDDEN_BANNERS_V2 = {'artifact','constellation'}` ✅

## Migration plan (10 stage)

Attualmente **STAGE 1: DESIGN_ONLY_NOW**. Prossimo stage: `ARTIFACT_BIBLE_REVIEW_SIGNOFF`.

## Static guards documentati (6)

1. `HIDDEN_BANNERS_V2` deve contenere `artifact` e `constellation`
2. `artifacts.tsx` deve solo fare redirect, mai `apiCall/fetch`
3. `artifacts-preview.tsx` non chiama endpoint `/api/artifacts/*` o `/api/constellations/*` mutativi
4. `battle_engine.py` / `battle_core.py` non leggono `user_artifacts` / `user_constellations`
5. Flag `ARTIFACT_LIVE_BONUS_ENABLED` resta unset (validator esistente PROJECT_M Track G)
6. `run_player_route_static_audit.py` già copre `/artifacts` e `/artifacts-preview`

## Invariants

| File | MD5 atteso | MD5 corrente | Stato |
|---|---|---|---|
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | `151ca35ad3bc35f0a6209cb3744ed440` | ✅ |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | `ff60bbb79efa329b71aa8ed351ea89b3` | ✅ |

## Suite

`python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel`
→ target **698 PASS / 0 FAIL / 0 MISS**

## Prossimo pack consigliato

- Primary: `PROJECT_ARTIFACT_BIBLE_REVIEW_SIGNOFF_PACK` (stage 2)
- Alternativa: `PROJECT_IAP_DESIGN_PACK` (P1 monetization)

# 200 — PROJECT_HOME_MENU_REWIRING

**Pack ID:** `PROJECT_HOME_MENU_REWIRING_PACK`
**Sentinella:** `v20`
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v20_HOME_MENU_REWIRING`
**Data UTC:** 2026-05-30
**Priorità:** P1 (discoverability)
**Verdict locale:** `PROJECT_HOME_MENU_REWIRING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Obiettivo
Aumentare la discoverability delle route già runtime `/guide` (Codex MVP) e `/tower-of-the-hells` (Torre TEST MVP) senza toccare `_layout.tsx`, senza toccare gameplay, senza unlock economie.

## Mapping route/link prima e dopo

| Surface | Prima | Dopo |
|---|---|---|
| `home.tsx` HomeOverflowPanel → "Torre" | `router.push('/tower')` ❌ stale | `router.push('/tower-of-the-hells')` ✅ |
| `home.tsx` HomeOverflowPanel → "Guida" | _assente_ | `router.push('/guide')` ✅ aggiunto |
| `menu.tsx` Combattimento → "Torre" | `route: '/tower'` ❌ stale | `route: '/tower-of-the-hells'` (label `Torre degli Inferi (TEST)`) ✅ |
| `menu.tsx` Altro → "Guida / Codex" | _assente_ | `route: '/guide'` ✅ aggiunto |
| `frontend/app/_layout.tsx` | invariato | invariato (UNTOUCHED ✅) |
| `frontend/app/tower-of-the-hells.tsx` | invariato | invariato (UNTOUCHED ✅) |
| `frontend/app/guide.tsx` | invariato | invariato (UNTOUCHED ✅) |

## Risposte dirette
- **Guida raggiungibile sì/no:** **SÌ** — HomeOverflowPanel + Menu.Altro
- **Torre raggiungibile sì/no:** **SÌ** — HomeOverflowPanel + Menu.Combattimento (entrambi → `/tower-of-the-hells`)
- **`_layout.tsx` untouched sì/no:** **SÌ** (git diff vuoto)

## Tracks completati

| Track | Status |
|---|---|
| A — NAVIGATION_SURFACE_AUDIT | ✅ 2 legacy finding + 1 missing-entry finding |
| B — SAFE_MENU_REWIRING_IMPLEMENTATION | ✅ 4 diff applicati (2 redirect + 2 add) |
| C — MODE_DISCOVERABILITY_REGISTRY_UPDATE | ✅ guide/tower/tower_legacy registrati |
| D — GUIDE_AND_TOWER_SMOKE_CHECKS | ✅ 9 check verified |
| E — MOBILE_QA_AND_UI_POLICY | ✅ checklist + label `(TEST)` policy |
| F — VALIDATOR_AND_SUITE_REGISTRATION | ✅ tupla `PROJECT-HOME-MENU-REWIRING` OPTIONAL |
| G — COMPLETION_AND_PUBLIC_SYNC | ✅ vedi commit nel report |

## Vincoli onorati (tutti ✅)
- 🚫 zero `_layout.tsx` edit
- 🚫 zero Tower gameplay/progress/AsyncStorage/rewards changes
- 🚫 zero Guide content schema rewrites
- 🚫 zero tutorial first-unlock wiring
- 🚫 zero backend routes/endpoints
- 🚫 zero DB writes/migrations
- 🚫 zero combat/battle_engine changes
- 🚫 zero gacha/pity changes
- 🚫 zero Shop/BP/VIP/IAP unlock (locks LOCKED_V2 preservati true)
- 🚫 zero Artifact/Constellation unhide
- 🚫 zero server profiles live
- 🚫 zero stamina/tickets/paid attempts
- 🚫 zero final art/audio
- 🚫 zero broad home/menu redesign
- 🚫 zero modifiche ai 5 file MD5-locked
- 🚫 zero REQUIRED validator weakening
- 🚫 zero fake PASS

## Locks preservati (verificati nel validator)
- `SHOP_LOCKED_V2 = true` ✅
- `ITEM_SHOP_LOCKED_V2 = true` ✅
- `BP_LOCKED_V2 = true` ✅
- `BP_PREMIUM_BUY_LOCKED_V2 = true` ✅
- `VIP_LOCKED_V2 = true` ✅

## File modificati / creati
**Modificati (3):**
- `frontend/app/(tabs)/home.tsx` — redirect `/tower`→`/tower-of-the-hells` + entry `/guide`
- `frontend/app/(tabs)/menu.tsx` — redirect `/tower`→`/tower-of-the-hells` (label `(TEST)`) + entry `/guide`
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — tupla `PROJECT-HOME-MENU-REWIRING` aggiunta (v20 sentinel)

**Creati (8):**
- `data/design/home_menu_rewiring/navigation_surface_audit_v1.json` (A)
- `data/design/home_menu_rewiring/safe_menu_rewiring_implementation_v1.json` (B)
- `data/design/home_menu_rewiring/mode_discoverability_registry_update_v1.json` (C)
- `data/design/home_menu_rewiring/guide_and_tower_smoke_checks_v1.json` (D)
- `data/design/home_menu_rewiring/mobile_qa_and_ui_policy_v1.json` (E)
- `data/design/home_menu_rewiring/home_menu_rewiring_suite_registration_proof_marker_v1.json` (proof)
- `backend/scripts/validate_project_home_menu_rewiring_v1.py` (validator OPTIONAL)
- `docs/divine/200_HOME_MENU_REWIRING.md` (questo doc)

## Rischi residui
1. **`frontend/app/tower.tsx` orphan**: il file legacy esiste ancora in repo ma non è più player-facing dopo il rewire. Removal/archive deferred a pack futuro.
2. **Platform sync bug `_layout.tsx`**: ancora pendente (non rilevante per questo pack).
3. **Tutorial first-unlock Tower**: ancora non wirato (deferred a `PROJECT_TUTORIAL_FIRST_UNLOCK_WIRING_PACK`).
4. **Coverage gap (7 modalità)**: ancora aperto (deferred a `PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`).

## Istruzioni Save to GitHub
1. Premere "Save to GitHub" per pushare il commit su `main`
2. Verificare pubblicamente:
   - `frontend/app/(tabs)/home.tsx` mostra `router.push('/tower-of-the-hells')` e `router.push('/guide')`
   - `frontend/app/(tabs)/menu.tsx` mostra `route: '/tower-of-the-hells'` (label `Torre degli Inferi (TEST)`) e `route: '/guide'` (label `Guida / Codex`)
   - 6 JSON in `data/design/home_menu_rewiring/`
   - tupla `PROJECT-HOME-MENU-REWIRING` nel suite runner
   - validator `validate_project_home_menu_rewiring_v1.py`
   - doc `200_HOME_MENU_REWIRING.md`
3. Dopo verifica → promuovere a `PROJECT_HOME_MENU_REWIRING_COMPLETE_PUBLIC_REPO_VERIFIED`.

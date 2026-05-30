# 199 — PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION

**Pack ID:** `PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK`
**Sentinella:** `v19`
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL`
**Data UTC:** 2026-05-30
**Priorità:** P1 (onboarding-critical)
**Verdict locale:** `PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Obiettivo

Introdurre il sistema canonico **Guida/Codex + Tutorial first-unlock** come foundation onboarding, con regola: ogni nuova modalità deve avere route/screen, mode_id, registry wiring, asset/audio registry (se placeholder), guida Codex, tutorial first-unlock, mobile QA checklist. La Torre degli Inferi è il primo caso applicato.

## Cosa è runtime vs design-only

| Layer | Stato in questo pack |
|---|---|
| Route/screen Guida `frontend/app/guide.tsx` | **RUNTIME** ✅ (read-only, deeplink-only) |
| Componente `TutorialOverlay.tsx` | **RUNTIME** ✅ (riusabile, NON wirato in alcuna schermata) |
| AsyncStorage completion locale (`tutorialStorage.ts`) | **RUNTIME** ✅ (solo locale, no server DB) |
| Constants TS `guideCodex.ts` + `tutorials.ts` | **RUNTIME** ✅ (read-only registry) |
| Wiring overlay nella schermata Torre | **DESIGN-ONLY DEFERRED** ⏸ (vietato toccare Tower gameplay) |
| Wiring overlay onboarding nella home | **DESIGN-ONLY DEFERRED** ⏸ (vietato touch home menu) |
| Route `_layout.tsx` registration di `guide` | **NON TOCCATO** ⛔ (bug platform sync; route auto-rilevata da expo-router file-based) |
| Menu entry home → Guida | **DESIGN-ONLY DEFERRED** ⏸ (deferred a `PROJECT_HOME_MENU_REWIRING_PACK`) |
| Endpoint backend tutorial completion server-side | **DESIGN-ONLY DEFERRED** ⏸ (no DB writes in questo pack) |

## Risposta diretta alle domande richieste

- **Route/screen guida sì/no:** **SÌ** — `frontend/app/guide.tsx` runtime (deeplink only)
- **Tutorial overlay sì/no:** **SÌ** componente runtime; **NO** wiring schermate (deferred)
- **Completion state sì/no:** **SÌ** via AsyncStorage locale (`@project_t/tutorial/v1/completion/<id>`); **NO** server-side

## Tracks completati

| Track | Nome | Stato |
|---|---|---|
| A | GUIDE_CODEX_SURFACE_AUDIT | ✅ READY |
| B | GUIDE_CONTENT_AND_TUTORIAL_SCHEMA | ✅ READY (13 categorie, 11 entries) |
| C | GUIDE_CODEX_RUNTIME_MVP_OR_DESIGN | ✅ RUNTIME MVP |
| D | TUTORIAL_RUNTIME_FOUNDATION | ✅ READY (4 entries design + overlay runtime) |
| E | TOWER_GUIDE_AND_FIRST_UNLOCK_TUTORIAL | ✅ READY (guide runtime; tutorial wiring deferred) |
| F | MODE_GUIDE_TUTORIAL_COVERAGE_REGISTRY | ✅ READY (13 modi audited; 7 coverage gaps) |
| G | MOBILE_QA_AND_RELEASE_GATE_POLICY | ✅ READY |
| H | VALIDATOR_AND_SUITE_REGISTRATION | ✅ READY (tupla `PROJECT-GUIDE-CODEX-AND-TUTORIAL-FOUNDATION` aggiunta OPTIONAL) |
| I | COMPLETION_AND_PUBLIC_SYNC | ✅ Commit locale (vedi report finale) |

## Coverage registry (Track F)

| mode_id | guide_entry | tutorial_entry | status |
|---|---|---|---|
| tower_of_the_hells | `guide_tower_of_the_hells` | `tutorial_tower_of_the_hells_first_unlock_v1` | DESIGN+GUIDE READY |
| combat | `guide_combat_basics` | — | GUIDE READY, tutorial gap |
| guild_war_fronti_del_valhalla | `guide_guild_war_fronti_del_valhalla` | — | placeholder futuro |
| artifacts | `guide_artifacts` | — | guide ready, tutorial gap |
| home_avatars | `guide_home_avatars` | — | future feature |
| economy_shop_bp_vip_iap | `guide_shop_bp_vip_iap` | — | locked surfaces |
| events / plaza / raid / pvp / territory / rankings / soul_forge | — | — | **COVERAGE GAP (7)** |

Future packs richiesti: `PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`, `PROJECT_TUTORIAL_FIRST_UNLOCK_WIRING_PACK`.

## Contenuti futuri canonicalizzati nei contracts

- **Colonne squadra**: Avanguardia / DPS / Support (entry `guide_team_columns_positioning` + tutorial dedicato)
- **Active Battle Power (POWER)**: entry `guide_active_battle_power`
- **BP delta overlay futuro (+BP/-BP)**: FUTURE_FEATURE_DESIGN_ONLY in `guide_active_battle_power` + `tutorial_active_battle_power_delta_v1`
- **Avatar systems**: Avatar HD serio / War Avatar chibi/tattico / Hero Room Avatar → entry `guide_home_avatars` (FUTURE_FEATURE_DESIGN_ONLY)

## Vincoli onorati

- 🚫 zero combat formula / battle_engine changes
- 🚫 zero broad navigation / menu / home refactor
- 🚫 zero server profiles live / second server
- 🚫 zero Shop/BP/VIP/IAP unlock
- 🚫 zero Artifact/Constellation unhide
- 🚫 zero gacha rate/pity changes
- 🚫 zero DB migrations / writes
- 🚫 zero broad user data mutation
- 🚫 zero final art/audio
- 🚫 zero monetization
- 🚫 zero stamina/tickets
- 🚫 zero Tower gameplay/progress changes
- 🚫 zero `_layout.tsx` change
- 🚫 zero REQUIRED validator weakening
- 🚫 zero fake PASS
- ✅ MD5 invarianti 5 file protetti ALL_OK

## Mobile QA / Smoke

- Schermata Guida: read-only, scroll smooth, touch target ≥ 44pt iOS / 48dp Android.
- Safe area top/bottom via `useSafeAreaInsets`.
- Back navigation tramite `router.back()`.
- Nessun input keyboard richiesto.
- Badge "CONTENUTO DI TEST" + "SOSTITUIRE PRIMA DEL RILASCIO" visibili.

## Rischi residui

1. **Discoverability bassa**: la route `/guide` è raggiungibile solo via deeplink in questo pack. Va aggiunto un menu entry in un pack futuro (sicuro: non tocca _layout).
2. **Tutorial first-unlock Tower**: definito ma non wirato. Richiede pack futuro autorizzato a toccare `tower-of-the-hells.tsx` (sicuro: insertion non gameplay).
3. **Coverage gap (7 modalità)**: documentato in F. Future pack `PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`.
4. **Platform sync bug `_layout.tsx`**: blocker non risolto. Non rilevante per questo pack (route auto-rilevata).

## Istruzioni Save to GitHub

1. Premere "Save to GitHub".
2. Verificare presenza pubblica di:
   - `frontend/app/guide.tsx`
   - `frontend/components/TutorialOverlay.tsx`
   - `frontend/utils/tutorialStorage.ts`
   - `frontend/constants/guideCodex.ts`, `frontend/constants/tutorials.ts`
   - 9 JSON design + 1 proof marker in `data/design/guide_codex/` e `data/design/tutorial/`
   - tupla `PROJECT-GUIDE-CODEX-AND-TUTORIAL-FOUNDATION` nel suite runner
   - doc `199_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION.md`
3. Dopo verifica positiva → promuovere a `PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_COMPLETE_PUBLIC_REPO_VERIFIED`.

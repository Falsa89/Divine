# 187 — PROJECT_COMBAT_FINALIZE_FOR_RELEASE

**Pack:** `PROJECT_COMBAT_FINALIZE_FOR_RELEASE`
**Tipo:** Audit + finalize controllato del combat (NO rewrite)
**Data esecuzione locale:** 2026-05-29
**Lingua report:** Italiano
**Verdict locale:** `PROJECT_COMBAT_FINALIZE_FOR_RELEASE_AUDIT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Sintesi esecutiva

Il combat è stato sottoposto ad audit canonico controllato in 7 track (A–G).
**Nessuna patch runtime è stata applicata**, perché il combat rispetta già
tutte le regole canoniche definite nel pack Runtime Audit (182). L'unica
variance osservata (speed profile) è stata classificata come finding
informativo non-bloccante, in quanto modificare i valori rientra nella
categoria esplicitamente vietata "formula/balance change".

Sono stati prodotti **solo** artefatti design-only + validator OPTIONAL +
proof marker + documentazione di release readiness.

---

## 2. Cosa è davvero release-ready

| Area | Stato | Note |
|---|---|---|
| battle engine | ✅ RELEASE_READY | MD5_LOCKED `151ca35a…`; nessuna mutazione |
| combat.tsx UI | ✅ RELEASE_READY | 3x3 grid, facing right/left, drawer, HUD splash, speed mid-battle, no flicker |
| BattleReport | ✅ RELEASE_READY | allies/enemies, damage_dealt, damage_received, healing_done, MVP highlight |
| PostBattleSummary | ✅ RELEASE_READY | rewards row compatta, EXP per hero animato, level up, account level up |
| buildPostBattleSummary | ✅ RELEASE_READY | MVP robust (match per nome backend → fallback top damage_dealt) |
| Audio runtime | ✅ NOT_ATTACHED_BY_DESIGN | policy pack 184; 12 WAV TEST intoccati |
| Locks VIP/BP/Shop/ItemShop | ✅ RELEASE_READY | V2 attivi |
| Synergy V2 battle | ✅ INTENTIONALLY_OFF | non in scope di questo pack |
| Artifact/Divine Weapon runtime | ✅ INTENTIONALLY_OFF | non in scope di questo pack |

## 3. Cosa resta P0/P1

### P0
- `PROJECT_LOGIN_AUTH_HARDENING_PACK` (email verify + password reset)
- `PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_PACK` (SLC_H gate)

### P1
- `PROJECT_TOWER_OF_THE_HELLS_RUNTIME_PACK`
- `COMBAT_SPEED_PROFILE_ALIGNMENT` (opzionale; se UX richiede esattamente 1700/950/580)
- `COMBAT_UI_REFACTOR` (decomposition `combat.tsx` 1848 LOC → componenti)

---

## 4. Eventuali patch eseguite e perché

**Nessuna patch runtime eseguita.** Il pack vieta espressamente:

- rewrite battle engine
- rewrite combat.tsx broad
- cambio formule/balance/final_numbers
- cambio hero kits
- Character Bible mutation
- Synergy V2 battle activation
- Artifact bonus / Divine Weapon / Status / VFX runtime
- final art/audio import
- broad audio engine

L'unica variance osservata (`SPEED_BASE = {1: 1500, 2: 650, 3: 300}` vs
canonical `{1: 1700, 2: 950, 3: 580}`) ricade nella categoria "formula/balance
change" e quindi **non è stata patchata**. Documentata come finding nel
Track B con flag `VARIANCE_NOTED_NO_PATCH`. Una futura `COMBAT_SPEED_PROFILE_ALIGNMENT_PACK`
P1 potrà allineare i valori se l'UX lo richiede.

---

## 5. Track artefatti prodotti

| Track | File | Verdict |
|---|---|---|
| A | `data/design/combat_finalize/combat_surface_audit_v1.json` | `TRACK_A_COMBAT_SURFACE_AUDIT_READY` |
| B | `data/design/combat_finalize/combat_canonical_alignment_audit_v1.json` | `TRACK_B_COMBAT_CANONICAL_ALIGNMENT_AUDIT_READY` |
| C | `data/design/combat_finalize/surgical_release_patch_v1.json` | `TRACK_C_SURGICAL_RELEASE_PATCH_READY` (no_patch_required=true) |
| D | `data/design/combat_finalize/post_battle_report_and_audio_qa_policy_v1.json` | `TRACK_D_POST_BATTLE_REPORT_AND_AUDIO_QA_POLICY_READY` |
| E | `data/design/combat_finalize/mobile_qa_and_release_readiness_matrix_v1.json` | `TRACK_E_MOBILE_QA_AND_RELEASE_READINESS_MATRIX_READY` |
| F | `data/design/combat_finalize/validator_and_suite_registration_v1.json` | `TRACK_F_VALIDATOR_AND_SUITE_REGISTRATION_READY` |
| G | `data/design/combat_finalize/completion_and_public_sync_v1.json` | `TRACK_G_COMPLETION_AND_PUBLIC_SYNC_READY` |
| Proof marker | `data/design/combat_finalize/combat_finalize_for_release_suite_registration_proof_marker_v1.json` | ✅ |
| Validator | `backend/scripts/validate_project_combat_finalize_for_release_v1.py` | OPTIONAL |
| Suite runner | sentinel `v13` + tupla `PROJECT-COMBAT-FINALIZE-FOR-RELEASE` | ✅ |
| Doc | `docs/divine/187_COMBAT_FINALIZE_FOR_RELEASE.md` | ✅ (questo file) |

---

## 6. Suite result

```
$ python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel
...
PROJECT-AUDIO-PLACEHOLDER-FOUNDATION  validate_project_audio_placeholder_foundation_v1.py  0  [PASS]
PROJECT-COMBAT-FINALIZE-FOR-RELEASE   validate_project_combat_finalize_for_release_v1.py   0  [PASS]
======================================================================
Overall: PASS  (pass=715, fail=0, miss=0)
```

(+1 rispetto al baseline 714: il nuovo validator OPTIONAL Combat Finalize.)

---

## 7. MD5 invarianti

```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py
54568b8cb75a07033f78ef6593aba839  frontend/app/battlepass.tsx
45fcc9890b6b128c37088bc33aa54caf  frontend/app/vip.tsx
```

✅ **Tutti** combaciano con la baseline.

---

## 8. Nessuna attivazione runtime non autorizzata

Verificato programmaticamente nel validator (sez. 12):

- ❌ `SYNERGY_V2_BATTLE_ACTIVE` non presente in `battle_engine.py` né `combat.tsx`
- ❌ `ARTIFACT_BONUS_RUNTIME_ACTIVE` non presente
- ❌ `DIVINE_WEAPON_RUNTIME_ACTIVE` non presente
- ❌ `STATUS_EFFECT_RUNTIME_ACTIVE` non presente
- ❌ `VFX_RUNTIME_ACTIVE` non presente
- ❌ nessun import `expo-av` / `expo-audio` / `react-native-sound` / `react-native-track-player`
  in `combat.tsx`, `BattleSprite.tsx`, `RuntimeSheetSprite.tsx`,
  `BattleReport.tsx`, `PostBattleSummary.tsx`, `buildPostBattleSummary.ts`,
  `motionSystem.ts`, `heroBattleAnimations.ts`
- ❌ nessuna dipendenza audio runtime in `frontend/package.json`
- ❌ nessun marker `PROJECT_COMBAT_FINALIZE_FOR_RELEASE` iniettato in
  `battle_engine.py`, `combat.tsx`, `BattleReport.tsx`, `PostBattleSummary.tsx`,
  `buildPostBattleSummary.ts` (zero broad refactor)

---

## 9. Mobile QA checklist (15 voci)

| ID | Area | Check | Atteso |
|---|---|---|---|
| MQA-01 | Grid | 3x3 grid renders correctly both teams | tutte 9 celle disponibili |
| MQA-02 | Facing | Team A → right, Team B → left | facing right vs left |
| MQA-03 | HUD | top HUD portrait cards use splash art | HeroCard portrait splash |
| MQA-04 | Field | field sprites use combat pose runtime sheet | RuntimeSheetSprite |
| MQA-05 | Drawer | battle log drawer toggleable bottom-left | non invasivo |
| MQA-06 | Speed | speed buttons 1x/2x/3x respondono mid-battle | speedRef applica subito |
| MQA-07 | NoFlicker | no flicker/remount/source swap | chatDrawerNode memoized |
| MQA-08 | PostBattle | victory: rewards + EXP per hero + level up | PostBattleSummary completo |
| MQA-09 | Report | battle report allies/enemies + damage/heal/MVP | BattleReport completo |
| MQA-10 | NoStamina | no stamina gate pre-battle | NO_STAMINA_SYSTEM |
| MQA-11 | Audio | nessun import audio runtime | audio TEST only |
| MQA-12 | Locks | VIP/BP/Shop locks attivi | V2 rispettati |
| MQA-13 | SafeArea | HUD safe-area iPhone notch + Android | SafeAreaView |
| MQA-14 | Keyboard | chat composer + keyboard non invasivo | KeyboardAvoidingView |
| MQA-15 | Touch | target touch HUD ≥44pt iOS / 48dp Android | HUD_HIT_SLOP |

---

## 10. Vincoli rispettati

- ✅ Zero rewrite battle engine
- ✅ Zero rewrite combat.tsx broad
- ✅ Zero cambio formule/balance/final_numbers
- ✅ Zero cambio hero kits / Character Bible
- ✅ Zero Synergy V2 battle activation
- ✅ Zero Artifact bonus / Divine Weapon / Status / VFX runtime
- ✅ Zero final art/audio import
- ✅ Zero broad audio engine
- ✅ Zero gacha/pity/IAP/BP/VIP/Shop change
- ✅ Zero DB writes / migrations / .env secret change
- ✅ Zero REQUIRED/OPTIONAL validator weakening
- ✅ Zero fake-PASS, zero tupla duplicata
- ✅ MD5 invarianti 5 file protetti intatti

---

## 11. Verdict locale

```
PROJECT_COMBAT_FINALIZE_FOR_RELEASE_AUDIT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

(Variante "audit_ready" perché nessuna patch runtime è stata applicata,
come autorizzato dalle specifiche del pack.)

---

## 12. Istruzioni per l'utente — Public Repo Sync Verification

1. Premere **"Save to GitHub"** nell'interfaccia Emergent.
2. Verificare push su `main`.
3. Su GitHub controllare la presenza di:
   - `# PUBLIC_SYNC_TAG_RESYNC_v13: suite_runner_combat_finalize_for_release_v13_2026_05_29` in `backend/scripts/run_hero_skill_kit_validator_suite.py`
   - sentinella inline `COMBAT_FINALIZE_FOR_RELEASE_REGISTRATION_SENTINEL`
   - tupla `('PROJECT-COMBAT-FINALIZE-FOR-RELEASE', 'validate_project_combat_finalize_for_release_v1.py')` (esattamente 1 volta)
   - `backend/scripts/validate_project_combat_finalize_for_release_v1.py`
   - `data/design/combat_finalize/` con 7 JSON tracks + proof marker
   - `docs/divine/187_COMBAT_FINALIZE_FOR_RELEASE.md`

Solo a quel punto:

```
PROJECT_COMBAT_FINALIZE_FOR_RELEASE_COMPLETE_PUBLIC_REPO_VERIFIED
```

---

*Fine report 187.*

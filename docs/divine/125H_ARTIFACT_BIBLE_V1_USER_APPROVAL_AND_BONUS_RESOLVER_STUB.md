# 125H — PROJECT_C Track H — ARTIFACT BIBLE V1 USER APPROVAL + BONUS RESOLVER STUB DESIGN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_C`  
**Track**: H  
**Mode**: `user_approval_marker_plus_pure_resolver_stub_no_runtime`  
**Verdict**: 🟢 `TRACK_H_ARTIFACT_BIBLE_V1_USER_APPROVAL_AND_BONUS_RESOLVER_STUB_DESIGN_READY`  
**Rollback**: eliminare `/app/backend/game_logic/artifact_bonus_resolver_stub.py` (mai importato a runtime)

---

## 1. Scopo

Formalizzare il **marker di approvazione utente** dello schema Artifact Bible V1 (V_B Track H) e introdurre il primo **resolver stub puro** (`artifact_bonus_resolver_stub.py`). Tutto inerte: nessun bonus live, nessun cambio summon behavior, nessuna mutazione DB.

## 2. User approval marker

| Aspetto | Valore |
|---|---|
| `artifact_bible_v1_approved` | `true` |
| Approval source | `user_chat_authorization_v_c` |
| Approval token | `MEGA_COMBO_PROJECT_ACCELERATION_C_APPROVAL=true` |
| Scope approvato | schema_freeze, launch_candidates_set, hard_invariants |
| **NON** approvato | live_bonus_application, summon_behavior_change, db_migration, frontend_ui_rollout |

## 3. Bonus resolver stub

File: `/app/backend/game_logic/artifact_bonus_resolver_stub.py`

```python
resolve_artifact_bonus(user_artifacts) -> {
  hp_pct: 0, atk_pct: 0, def_pct: 0, crit_pct: 0,
  source: 'resolver_stub_inert'
}
validate_caps_definition() -> True
```

- **Pure**: nessun side effect, ritorno stabile indipendente dall'input.
- **Caps documentate**: ±50% su tutte le componenti (anti-power-creep), MAI applicate live in V_C.
- **Runtime import**: ❌ (validator esegue scan su `server.py` + `routes/*.py`).

## 4. Integration phases

| Phase | Nome | Status |
|---|---|---|
| 1 | USER_APPROVAL_MARKER | DONE_V_C |
| 2 | PURE_RESOLVER_STUB | DONE_V_C |
| 3 | NON_RUNTIME_UNIT_TEST_PACK | PLANNED |
| 4 | INTEGRATION_POINT_DESIGN (in `GET /api/user/me`) | PLANNED |
| 5 | FEATURE_FLAG_GATED_LIVE_IMPORT (`ARTIFACT_RESOLVER_RUNTIME_ENABLED`) | PLANNED |
| 6 | LIVE_BONUS_APPLICATION | 🚫 `FORBIDDEN_OUT_OF_SCOPE_PROJECT_C` |

## 5. Hard invariants acknowledged

- ❌ Nessun artifact summon behavior change
- ❌ Nessun artifact live bonus su battle/account stats
- ✅ Resolver stub ritorna **zero-bonus envelope** stabile
- ✅ Resolver stub **NON** importato dal runtime

## 6. Forbidden scope rispettato

Artifact live bonus ❌, artifact summon behavior change ❌, DB migration ❌, frontend UI rollout ❌, runtime import of stub ❌.

## 7. Validator

`/app/backend/scripts/validate_project_c_artifact_bible_user_approval_v1.py` — verifica marker, scope user_approval, integrità stub (import + contract test), assenza di import runtime in `server.py` e `routes/*.py`.

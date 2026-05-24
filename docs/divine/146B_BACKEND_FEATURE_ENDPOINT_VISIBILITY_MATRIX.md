# 146B — BACKEND FEATURE / ENDPOINT VISIBILITY MATRIX

## Track B — `PROJECT_X_TRACK_B`

**Verdict:** `TRACK_B_BACKEND_FEATURE_ENDPOINT_VISIBILITY_MATRIX_READY`

## 1. Obiettivo

Classificare ogni feature backend in una delle 8 classi di visibilità:

```
VISIBLE_READY | READ_ONLY_PREVIEW_READY | FLAG_GATED_DISABLED_503 | DRY_RUN_ONLY
ADMIN_DEV_ONLY | BLOCKED_PENDING_APPROVAL | DO_NOT_SHOW_PLAYER | LEGACY_DEPRECATED
```

## 2. Totale endpoint backend auditati: 220

## 3. Matrice di visibilità (15 feature)

| Feature | Classe | Endpoint chiave | Player-facing |
|---|---|---|---|
| Hero Collection | `VISIBLE_READY` | `/api/heroes`, `/api/user/heroes` | ✅ |
| Combat / Battle | `VISIBLE_READY` | `/api/battle/simulate`, `/api/story/battle`, `/api/tower/battle`, `/api/pvp/battle` | ✅ |
| Gacha / Summon | `VISIBLE_READY` | `/api/gacha/*` | ✅ |
| Economy / Battle Pass | `VISIBLE_READY` | `/api/shop`, `/api/battlepass`, `/api/vip`, `/api/mail` | ✅ |
| Status Codex / Catalog | `READ_ONLY_PREVIEW_READY` | `/api/skill-status-vfx-catalogs/*`, `/api/hero-skill-kits/catalogs/*` | ✅ |
| Divine Weapons Catalog | `READ_ONLY_PREVIEW_READY` | `/api/divine-weapons/catalogs/*` | ✅ |
| Hero Skill Kits Catalog | `READ_ONLY_PREVIEW_READY` | `/api/hero-skill-kits/catalogs/*` | ✅ |
| Server Profiles Preview | `FLAG_GATED_DISABLED_503` | `/api/server-profiles/select` | ❌ (503) |
| Housing Preview | `FLAG_GATED_DISABLED_503` | `/api/housing/preview` | ❌ (503) |
| Artifact Bible Dry-Run | `DRY_RUN_ONLY` | `/api/artifacts (catalog)`, `/api/constellations` | parz. |
| Status First-Slice | `BLOCKED_PENDING_APPROVAL` | resolver inert | dev/admin only |
| Status Second-Slice | `BLOCKED_PENDING_APPROVAL` | resolver pure, flag OFF | dev/admin only |
| AF2-N Canary | `ADMIN_DEV_ONLY` | `/api/affinity/gift-spend/*` | ❌ |
| QA Mobile Smoke / Dev Tools | `ADMIN_DEV_ONLY` | `/api/admin/bots/*` | ❌ |
| Health | `DO_NOT_SHOW_PLAYER` | `/api/health` | ❌ |

## 4. Vincoli

- Nessun endpoint modificato
- Nessun flag flippato
- Nessuna mutazione backend

## 5. Validator

`validate_project_x_backend_feature_visibility_matrix_v1.py` → **PASS**.

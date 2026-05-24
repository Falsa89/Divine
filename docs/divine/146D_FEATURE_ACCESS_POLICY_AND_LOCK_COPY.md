# 146D — FEATURE ACCESS POLICY & LOCK COPY

## Track D — `PROJECT_X_TRACK_D`

**Verdict:** `TRACK_D_FEATURE_ACCESS_POLICY_AND_LOCK_COPY_READY`

## 1. Obiettivo

Definire le politiche di accesso alle feature e i copy associati ai vari stati di lock, **senza alcuna implementazione player-facing**.

## 2. Classi di policy

| Classe | Descrizione | Applies to |
|---|---|---|
| `visible_locked` | Card visibile in UI, non interagibile sul percorso live, modal con copy on press | Artifact Collection Preview, Housing Preview, Server Profile Preview |
| `hidden_until_approved` | Non renderizzata finché firme di approvazione assenti | AF2-N public rollout, Borea activation, Second server, Phase 11, Artifact live summon/bonus, Housing live bonus, Status prod rollouts |
| `dev_only` | Visibile solo in modalità dev/admin | `/dev-combat-qa-lab`, `/sprite-test`, future `/dev-readiness-panel`, `/dev-approval-matrix` |
| `read_only_preview` | Visibile + navigabile, solo GET, no mutating action | Status Codex, Hero Skill Kits Catalog, Divine Weapons Catalog, Synergy Codex, Affinity Gifts Preview, Collection Synergies Preview |
| `live_feature` | Feature pienamente attiva | Heroes, Combat (story/tower/pvp/raid/gvg), Gacha, Battle Pass, Shop, VIP, Mail, Equipment, Cosmetics, Achievements, Guild |

## 3. Button policy (strict)

- ❌ No fake functionality
- ❌ No "claim/summon/upgrade" su feature non approved
- ❌ No "purchase" se endpoint economy non live
- ❌ No flag flip da UI

## 4. Catalogo copy lock (IT)

| Chiave | Copy |
|---|---|
| `generic_coming_soon` | "In arrivo — Resta sintonizzato!" |
| `awaiting_approval` | "In attesa di approvazione del team" |
| `server_profiles` | "Prossimamente: Profili Server" |
| `housing` | "Prossimamente: Dimora" |
| `artifact_live` | "Prossimamente: Artefatti Live" |
| `af2n_public` | "Prossimamente: AF2-N Public" |
| `phase_11` | "Prossimamente: Fase 11" |

## 5. Validator

`validate_project_x_feature_access_policy_lock_copy_v1.py` → **PASS**.

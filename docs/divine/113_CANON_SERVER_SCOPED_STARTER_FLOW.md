# 113 — CANON: Server-Scoped Starter Flow (Pack 87)

**Pack:** `MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP`
**Authorization:** `AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87`
**Generated UTC:** 2026-06-08

## Decisione canonica

> Gli starter heroes del player sono **SERVER-SCOPED**. La registrazione account NON
> assegna roster globale operativo (preservato da Pack 86). Lo starter roster viene
> assegnato **SOLO** nel contesto `(authenticated_user_id, selected_server_id)`,
> idempotentemente, **una sola volta per server**.

## Schema starter flow

1. L'utente entra in un server (`servers.tsx::onEnter`).
2. Il frontend chiama `POST /api/psp/ensure?server_id=<sid>` (Pack 85/86) → PSP fresh-start
   (`player_level=1`, `player_exp=0`, `team_formation=[]`).
3. Il frontend chiama `POST /api/psp/starter/claim?server_id=<sid>` (Pack 87) → assegna
   idempotentemente lo starter roster server-scoped (3 heroes) se non ancora reclamato.
4. Il team viene inizializzato **SOLO** se vuoto, e **SOLO** con i `user_hero` appena creati.

## Starter roster (3 heroes, low-rarity, non-premium, catalogati)

| Slot | Hero ID | Nome | Rarity | Element | Ruolo |
|------|---------|------|--------|---------|-------|
| 1 | `greek_phalanx_recruit`    | Recluta di Falange     | 1★ | earth | tank      |
| 2 | `celtic_forest_archer`     | Arciera di Bosco       | 1★ | wind  | dps       |
| 3 | `angelic_sanctuary_acolyte`| Accolita del Santuario | 1★ | light | support   |

## Invarianti garantiti

- Starter `user_heroes` includono **MANDATORY** `server_id` (no account-wide).
- `claim_once_per_server`: marker `_slc_pack_87_starter_claim_marker` su PSP.
- `level=1`, `experience=0`, `stars=rarity_from_catalog` (no escalation).
- **NO** premium currency, hard currency, inventory, equipment, story reward.
- **NO** player_level mutation.
- **NO** copy S1→S2.
- **NO** overwrite team esistente (init solo se vuoto).
- **NO** Borea / 5★ / 6★ starter.
- **NO** legacy cleanup.
- **NO** reward/progress live.
- **NO** release readiness claim.

## Idempotency

- Re-call `POST /api/psp/starter/claim` per stesso `(user_id, server_id)` → `already_claimed=true`, `created=false`, 0 writes.
- Marker su PSP: `_slc_pack_87_starter_claim_marker: true`, `onboarding_state: "starter_claimed"`.

## Audit refuse-by-default

Se un hero ID configurato non esiste / non è catalogato / è premium / è high-rarity:
blocker esplicito (no silent invention):
- `STARTER_ROSTER_NOT_CATALOGED`
- `STARTER_ROSTER_HIGH_RARITY`
- `STARTER_ROSTER_NOT_OFFICIAL`
- `STARTER_ROSTER_NOT_OBTAINABLE`
- `STARTER_ROSTER_NOT_CATALOG_VISIBLE`
- `STARTER_ROSTER_DEACTIVATED`
- `STARTER_ROSTER_PREMIUM_FORBIDDEN`

## Statement espliciti

1. Starter heroes are **server-scoped**.
2. **No account-wide** starter `user_heroes`.
3. New server starts **level 1**.
4. **No S1→S2 copy**.
5. **No premium/currency/equipment/story rewards**.
6. **Reward/progress live OFF**.
7. **Legacy cleanup NOT executed**.

## Endpoint contratto

- **Path:** `POST /api/psp/starter/claim?server_id=<sid>`
- **Auth:** Bearer (JWT, `v96_auth_token`).
- **Server_id:** required.
- **PSP:** must exist (chiama prima `/api/psp/ensure`).
- **Idempotent:** yes.
- **Headers di risposta:**
  - `X-Starter-Claim-Mode` ∈ {`starter_claimed_first_time`, `already_claimed_no_write`, `psp_required`, `roster_not_cataloged`}
  - `X-Server-Id`

## Riferimenti

- `backend/server.py::psp_starter_claim`
- `frontend/app/servers.tsx::onEnter` (chiamata post-ensure)
- `data/design/v110_pack_87_server_scoped_starter_flow/` (design JSONs)
- `backend/scripts/validate_v110_pack_87_*.py` (validators)

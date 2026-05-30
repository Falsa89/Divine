# 213 — PROJECT_GEM_SOCKET_RUNTIME

**Verdict**: `PROJECT_GEM_SOCKET_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Timestamp UTC**: 2026-05-30T17:00:00Z

**Runtime mode**: `PREVIEW_ONLY` (DISABLED-BY-DEFAULT — HTTP 503 inert envelope)

**Feature flag**: `GEM_SOCKET_RUNTIME_PREVIEW_ENABLED`

**Live socket commit**: **NO** (deferred a safety hardening pack)

---

## Separazione canonica (Bible 202)

| Layer | Cosa è | Dove vive |
|---|---|---|
| **Gear** | Equip classico, cap +50 | `weapon/armor/helm/boots/gloves/accessory` |
| **Gemme** | Pietre **incastonabili nei gear** (socket) | Slot interni al gear |
| **Rune** | Scroll/talismani/pergamene/sigilli | Equipaggiati sull'eroe |
| **Artifact** | Collezione globale roster/account | Account-bound |
| **Divine Weapon** | Arma personale 6★ | Character-bound |

**ATTENZIONE**: "Gemme" ≠ valuta premium `gems`. Naming socket: `socket_gem_*`.

## Endpoint pubblicati

| Method | Path | DB writes | Mutation | Status flag-off |
|---|---|---|---|---|
| GET  | `/api/gem-socket/config`           | **0** | NO | 503 |
| GET  | `/api/gem-socket/catalog`          | **0** | NO | 503 |
| POST | `/api/gem-socket/socket-preview`   | **0** | NO | 503 |
| POST | `/api/gem-socket/replace-preview`  | **0** | NO | 503 |
| POST | `/api/gem-socket/unsocket-preview` | **0** | NO | 503 |
| POST | `/api/gem-socket/power-preview`    | **0** | NO | 503 |

Tutti gated da `GEM_SOCKET_RUNTIME_PREVIEW_ENABLED`. **Zero DB lookup** (input JSON di sample, non DB ids).

## Socket rules canonici v1

**Max sockets by rarity**: `{1:0, 2:0, 3:1, 4:1, 5:2, 6:3}`

**Socket level unlocks**: `{socket1:+10, socket2:+20, socket3:+35}`

## 6 Famiglie Gemme

`ruby` (attack) · `sapphire` (defense) · `emerald` (hp) · `topaz` (speed) · `amethyst` (crit_chance) · `diamond` (all_stat, max 1/item)

## 6 Tier

`common`, `uncommon`, `rare`, `epic`, `legendary`, `divine`. Delta preview non-final.

## Perché NIENTE premium `gems`

Il progetto usa già `users.gems` come valuta premium (Divine Crystals).
Per evitare collisioni:

- Naming socket: `socket_gem_*`.
- Materiali raid: `gem_dust_common`, `gem_shard_rare` (track Material Raid locked).
- **MAI** `user.gems`, `$inc.gems`, `users.update.gems`.

## Perché NIENTE live commit

- Manca canonical `user_socket_gems` inventory.
- Manca canonical `user_materials` collection.
- Manca idempotent commit con `request_id`.
- Manca atomic transaction.
- Manca audit log.
- Manca ownership/active-team/locked checks.
- Manca BP Delta runtime integration.

## Crosslink Material Raid

- `gem_material_raid` resta **`locked_deferred`** (Material Raid runtime intoccato).
- Stato dopo questo pack: `preview_ready_after_gem_socket_foundation`.
- Future pack: `PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_PACK` (opzionale).

## Future work richiesto per commit live

1. Canonical `user_socket_gems` inventory.
2. Canonical `user_materials` (con `gem_dust_common`/`gem_shard_rare`).
3. Idempotent socket commit con `request_id`.
4. Audit log per ogni socket/unsocket/replace.
5. Gear mutation lock/ownership checks.
6. BP Delta integration (recompute power).
7. Real gear UI integration (forge/equipment screens).
8. Material Raid gem track unlock.
9. Guide/Codex entry.

## Sandbox frontend

- Route deeplink-only: **`/gem-socket-test`** → `frontend/app/gem-socket-test.tsx`.
- Constants: `frontend/constants/gemSocket.ts`.
- **NO** wiring in `home.tsx`, `menu.tsx`, `_layout.tsx`.

## Validator

- `backend/scripts/validate_project_gem_socket_runtime_v1.py` (OPTIONAL).
- Suite runner: 1 tupla aggiunta in blocco OPTIONAL con sentinels v27.

## Forbidden scope confirmation

- ✅ Zero modifiche a `battle_engine.py` / `combat.tsx` / `.env` / `artifacts.py` / `battlepass.tsx` / `vip.tsx`
- ✅ Zero modifiche a `forge.py` (legacy Rune/Forge intoccato)
- ✅ Zero modifiche a `material_raid_preview.py` (Material Raid unchanged)
- ✅ Zero gem socket commit / unsocket commit / replace commit
- ✅ Zero premium `gems` currency spend/mutate
- ✅ Zero `user_materials` / material spend
- ✅ Zero gacha/economy/Shop/BP/VIP/IAP
- ✅ Zero Artifact/Divine Weapon/Rune runtime changes
- ✅ Zero Material Raid live gem drops
- ✅ Zero REQUIRED/OPTIONAL validator weakening
- ✅ Zero tuple duplicate
- ✅ Zero fake PASS

## Prossimo pack consigliato

1. **`PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_PACK`** — surface gem track in Material Raid preview.
2. **`PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK`** — ownership/locks/active-team/idempotency/material spend/audit log.
3. **`PROJECT_RUNE_SCROLL_TALISMAN_RUNTIME_PACK`** — layer ortogonale hero-bound.
4. **`PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`** — spiega Gear/Gemme/Rune/Forge/Material Raid al giocatore.

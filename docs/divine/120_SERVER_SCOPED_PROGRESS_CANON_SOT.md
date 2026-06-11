# 120 — Server-Scoped Progress Canon SOT (Pack 100)

Documento canonico che formalizza la regola di scoping per tutte le progressioni di gioco. Introdotto dal Pack 100.

## Regola canonica

Ogni progressione di gioco è chiusa nello scope `(user_id, server_id, feature_scope)`. Nessun salvataggio è account-wide salvo che sia già stato classificato come *legacy non-player-facing path* e quarantined.

### Conseguenze

- **Daily quest** su S1 NON sono completate su S2.
- **Story** su S1 NON sblocca story su S2.
- **Tower** floor 20 su S1 NON significa floor 20 su S2.
- Modalità, eventi, raid, arena, guild, shop, forge **devono** essere server-scoped.
- Un nuovo server = progressione fresca.

### Esclusioni esplicite (auto-rifiutate)

- `users.gold / users.gems / users.experience` mutate da path attivo player-facing.
- Document write con sola chiave `user_id` (senza `server_id`) emesso da route attiva player-facing.
- Hardcoded `server_id="s1"` in path attivo daily/story/tower/reward.

## Audit Pack 100 (snapshot)

| Sistema | Path attivo | Stato server-scope | Note |
|---|---|---|---|
| Daily Login Claim | `POST /api/daily-login/claim` | **OK** | Pack 97 PSP `soft_currencies` scoped. |
| Daily Quest Claim | `POST /api/daily-quest/claim` | **OK** | Pack 98+99 PSP scoped, tracker scoped, claim_key per (user,server,quest,day). |
| Daily Quest Progress Tracker | `GET/POST /api/daily-quest/progress*` | **OK** | Pack 99 chiave canonica `(user_id, server_id, quest_id, day_iso)`. |
| Story Battle | `POST /api/story/battle` con `server_id` | **OK** | Pack 95 strict path: scrive su `psp.story_progress`. Legacy path senza `server_id` rimane `account-wide` ma marcato non-player-facing. |
| Story Battle (legacy senza server_id) | `POST /api/story/battle` no `server_id` | **DEFERRED / LEGACY-QUARANTINE** | Path account-wide. Non chiamato dalla UI player-facing supportata. Reward live general resta `false`. |
| Tower Battle | `POST /api/tower/battle` | **LEAK PLAYER-FACING (DEFERRED)** | Muta `users.gold/users.gems/users.experience` e `tower_progress` solo per `user_id`. **Marker: `TOWER_PROGRESS_SERVER_SCOPE_DEFERRED`.** No reward live attivato in Pack 100. Da sanare in pack futuro. |
| Tower Status | `GET /api/tower/status` | **LEAK PLAYER-FACING (DEFERRED)** | Read account-wide solo `user_id`. Marker invariato. |
| Tower Rankings | `GET /api/rankings/tower` | **DEFERRED** | Aggregato account-wide read-only. |
| PVP / Arena / Guild / Mail / Achievements / Battlepass / Events / AFK Rewards | varie | **DEFERRED / NOT-LIVE** | Nessun reward live attivato, nessuna scrittura attiva.

## Daily Task Loop Pack 100 (NUOVO)

Il Pack 100 introduce il primo **Daily Task Loop reale server-scoped**:

1. `POST /api/daily-login/claim?server_id=S1` (success).
2. **Trigger interno**: l'endpoint emette evento `daily_login_claim_success` sul **Daily Quest Event Bus** (`utils/daily_quest_events.py`) **solo per lo stesso `(user_id, server_id, day_iso)`**.
3. Event Bus mappa il `event_type` alla `quest_id` in allowlist e scrive sul tracker `daily_quest_progress` (collection Pack 99) con `state=completed`. Nessun reward grant. Nessun client trust.
4. `POST /api/daily-quest/claim?server_id=S1&quest_id=daily_quest_1` (success): consulta tracker (state=completed), grant `+15 mc / +8 honor` su PSP S1, transizione tracker `claimed`.
5. Replay claim S1 stesso giorno → `idempotent_replay=true`, nessun secondo grant.
6. `POST /api/daily-quest/claim?server_id=S2` (no completion) → 409 `DAILY_QUEST_COMPLETION_REQUIRED` (S1 NON contamina S2).

## First Real Daily Quest Event Mapping (Pack 100)

| event_type | trigger | quest_id | stato | note |
|---|---|---|---|---|
| `daily_login_claim_success` | post-success `daily_login_claim` | `daily_quest_1` | **REAL_COMPLETION_EVENT_READY** | Path attivato. |
| `story_strict_progress_success` | non integrato in Pack 100 | `daily_quest_2` | **COMPLETION_RUNTIME_DEFERRED** | Source potenzialmente safe, ma non collegata in questo pack. Resta test-only via `pack_99_test_artifact`. |
| (nessun evento safe identificato) | — | `daily_quest_3` | **COMPLETION_RUNTIME_DEFERRED** | Nessuna azione gameplay sufficientemente sicura per attivare la quest. Resta test-only via `pack_99_test_artifact`. |

## Vincoli (non negoziabili)

- NO reward live general.
- NO mail/achievement/battlepass/event/AFK rewards live.
- NO premium/hard currency grant.
- NO IAP/store/payment change.
- NO gacha change.
- NO broad production grants.
- NO unmarked test writes.
- NO legacy cleanup general execute.
- NO destructive migration.
- NO account-wide server-bound reward/currency grant.
- NO hardcoded `server_id="s1"` in active path.
- NO double daily reward grant.
- NO release readiness claim.
- NO `/api/battle/simulate` call from staging/live.
- NO battle_engine formula rewrite.

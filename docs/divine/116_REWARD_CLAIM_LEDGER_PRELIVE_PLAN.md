# 116 — Reward Claim Ledger Pre-Live Plan (Pack 93)

> Sentinella: `PUBLIC_SYNC_TAG_v110_ECONOMY_PROGRESS_WRITE_PATHS_MEGAPACK`
> Pack di emissione: `MEGA_RELEASE_ACCELERATION_93_ECONOMY_PROGRESS_WRITE_PATHS_MEGAPACK`
> Stato: **DESIGN PRE-LIVE** — nessun reward live attivato.

## Obiettivo

Definire il ledger di idempotency richiesto per promuovere live (futuro pack autorizzato) i seguenti reward claim path:

- mail rewards
- achievements claim
- daily login
- battlepass tiers
- shop / IAP claim entitlements
- story/battle reward (gold/gems/equipment drop)
- AFK / progress increments
- event rewards

## Schema ledger (collection: `reward_claim_ledger`)

```json
{
  "id": "<uuid>",
  "user_id": "<user_uuid>",
  "server_id": "<sid>",
  "claim_source": "mail|achievement|daily|battlepass|shop|story|battle|afk|event",
  "claim_key": "<es: 'mail_<mail_id>', 'achievement_<id>', 'daily_2026_06_09'>",
  "idempotency_token": "<client-generated uuid, REQUIRED non-empty min 8 char>",
  "rewards": {
    "server_scoped": {"honor": 100, "prana": 5, "items": [...], "hero_fragments": [...]},
    "account_wide": {"gold": 1000, "gems": 50}
  },
  "applied_at": "<utc>",
  "applied_balances_after": {"psp.soft_currencies": {...}, "users.gold": ..., "users.gems": ...},
  "_slc_pack_93_reward_claim_ledger": true,
  "audit": {
    "request_ip": "<masked>",
    "user_agent": "<masked>"
  }
}
```

Indici richiesti:
- `{user_id: 1, server_id: 1, claim_key: 1}` UNIQUE — impedisce double-claim per chiave.
- `{user_id: 1, server_id: 1, idempotency_token: 1}` UNIQUE — replay idempotente.
- `{applied_at: 1}` per cleanup TTL futuro (deferito).

## Invarianti runtime per ogni claim

1. `server_id` REQUIRED in query.
2. PSP existence check obbligatorio.
3. `claim_key` deterministico per origine + risorsa (es: `daily_<YYYY_MM_DD>` per daily login).
4. `idempotency_token` client-generated, REQUIRED non-empty, min 8 char.
5. Server-scoped rewards (soft currencies, story progress, inventory) → mutano `psp.soft_currencies` / `psp.story_progress` / `inventory` con selector `(user_id, server_id, ...)`.
6. Account-wide rewards (gold, gems) → mutano `users` ma SOLO se reward source approvato global (mail/IAP/battlepass entitlements account-wide).
7. Tutti i mutation operano in transazione/sequenza atomica con ledger insert. Ledger insert PRIMA del payout per idempotency.
8. Replay (stesso token o stesso `claim_key`) → ritorna l'esito originale senza re-payout.
9. NESSUN reward live finché approval futura non ricevuta.

## Path pre-live (non eseguite in Pack 93)

| Path                                   | Stato in Pack 93                                       | Approval futura richiesta                                           |
|----------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------|
| `POST /api/story/battle?server_id=...` | `STORY_PROGRESS_WRITE_SERVER_SCOPE_DEFERRED`           | `AUTORIZZO_V110_STORY_PROGRESS_WRITE_STRICT_SCOPE_EXECUTE`          |
| `POST /api/mail/claim`                 | UI/route locked dietro POSTQA_D, ledger non implementato | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |
| `POST /api/achievements/claim`         | UI/route locked, ledger non implementato                | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |
| `POST /api/daily/claim`                | locked, ledger non implementato                         | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |
| `POST /api/battlepass/claim`           | locked, ledger non implementato                         | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |
| `POST /api/shop/buy` (entitlements)    | preservato Pack 90 (inventory item-shop), ledger non esteso | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                |
| `POST /api/events/*/claim`             | locked, ledger non implementato                         | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |
| `POST /api/afk/claim`                  | locked, ledger non implementato                         | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`                   |

## Path live in Pack 93 (test-only-safe)

| Path                                              | Stato in Pack 93                  | Ledger collection            |
|---------------------------------------------------|-----------------------------------|-------------------------------|
| `POST /api/wallet/spend?server_id=...` (NEW)      | LIVE, test-only-safe (server-scoped spend strict, idempotency token required) | `wallet_spend_ledger`         |

Il path `wallet_spend` opera **solo come spend** (decremento). Nessun reward grant. Il test-only-safe deriva dal fatto che è un endpoint NUOVO senza consumer di produzione esistenti; può essere chiamato solo da test marker o futuro frontend opt-in.

## Rollout plan (futuro autorizzato)

1. Pack `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`: implementa `reward_claim_ledger` collection + indici, smoke E2E test-only.
2. Pack per claim path specifico (es. mail) con guard + ledger integration.
3. Frontend opt-in per chiamare il nuovo path con `server_id` + idempotency token.
4. Rollout live progressivo per claim source.

## Safety

- `reward_live = false` in Pack 93.
- `progress_live = false` in Pack 93.
- `release_readiness_claimed = false` in Pack 93.
- Nessun reward grant, nessun premium grant, nessun IAP/store/payment change.

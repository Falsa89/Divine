# 504 — Reward Claim UI Summary Preview Shell (v81)

## File creato
`frontend/app/reward-claim-summary-preview.tsx`

## Garanzie
- **deeplink-only** — nessuna esposizione home/tab pubblica
- **no backend fetch / no API call / no AsyncStorage**
- **no account mutation / no DB / no real claim button**
- **no import** da `battle_engine`, `story.tsx`, `combat.tsx`
- Dati statici locali derivati dai contratti v80/v81
- Labels obbligatori presenti: `PREVIEW`, `STAGING`, `CANARY_LOCAL`, `NOT LIVE REWARD`
- Stile premium mobile-friendly compatto + dettagli espandibili
- **TypeScript pass** sul nuovo file

## Sezioni
1. Reward Preview (grid con cap hint)
2. Claim Result (sample tx)
3. Idempotency Status (sample)
4. Rollback State (sample)
5. Blocked / Rejected Examples (5 scenari)
6. Local Ledger Summary

## Alpha Menu Patch
`frontend/app/alpha-menu-preview.tsx` aggiornato: aggiunta entry `reward-claim-summary-preview`
con guardrails (`deeplink_only`, `db_writes=0`, `no_real_claim_button`, `no_live_reward`,
`no_backend_fetch`, `no_account_mutation`, `no_asyncstorage`, `static_local_preview_data_only`,
labels). Nessun fetch/account/reward/progress aggiunto.

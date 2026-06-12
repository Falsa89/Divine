# Closed Alpha Mobile QA Checklist (Pack 109)

Questa checklist guida il QA manuale di Closed Alpha. **NON e' un
release readiness claim**. Tutti i passi che modificano stato sono
limitati a utenti test marcati (`pack_108_test_artifact`, ecc.).

## A. Auth / Server selection / Logout

- [ ] App parte senza crash su iOS + Android.
- [ ] Login funziona con credenziali test seed.
- [ ] Logout pulisce token e riporta a Login screen.
- [ ] Selezione server S1/S2 visibile; `no_silent_s1_fallback` (nessun server preselezionato di default a `s1` senza azione utente).
- [ ] Cambio server (S1 -> S2) invalida cache locale playable loop (`refreshToken` bump).
- [ ] Re-login dopo logout NON conserva PSP del precedente utente.

## B. Home / Lobby / Playable loop

- [ ] Home shell renderizza correttamente con `safe area` sia top sia bottom.
- [ ] Lobby pre-battle entrypoint visibile (anche se locked).
- [ ] PlayableLoopConsumer renderizza solo se `EXPO_PUBLIC_PLAYABLE_LOOP_MAP_UI_ENABLED=true` (default off in produzione closed alpha).
- [ ] Mappa Alpha mostra 11 surface; nessuna marcata `READY` se `reward_live=false`.
- [ ] Status copy italiana coerente: `Bloccato (Closed Alpha)`, `In preparazione (deferred)`, etc.

## C. Tower / Story / Battle preview

- [ ] Story preview path non chiama `battle_engine` runtime.
- [ ] Tower strict screen renderizza preflight/preview senza claim live.
- [ ] Nessun `/api/battle/simulate` invocato da staging/live.

## D. Daily / Daily quest / Controlled rewards

- [ ] Daily entrypoint visibile, locked se kill switch OFF.
- [ ] Reward Center mostra `In preparazione (deferred)` per achievements/mail/weekly se non live.
- [ ] Doppio claim su stesso slot e' idempotente (no double-grant).

## E. Shop / Forge / Rewards

- [ ] Shop strict mostra catalogo read-only; spend NON modifica `users.gold/gems`.
- [ ] Forge/Upgrade/Fusion usa solo PSP material ledger; nessuna mutation a `users.*`.
- [ ] Rewards center conferma `reward_live_general=false` in health.

## F. Guild

- [ ] Guild strict search/status accessibili in preview; nessun reward grant.
- [ ] Tentativo `POST /api/guild/create` legacy -> 423 `GUILD_LEGACY_QUARANTINED`.
- [ ] S1 membership invisibile su S2 (cross-server isolation).

## G. Arena / PvP / Event

- [ ] Arena/PvP/Event mostrano blocker `*_REWARD_LIVE_DISABLED`.
- [ ] Nessun preflight invoca ranking live o reward live.

## H. Permessi mobili

- [ ] Nessuna richiesta di permission non necessaria al primo avvio.
- [ ] Permission richieste contestualmente (camera/microfono/storage solo se l'utente attiva la feature corrispondente).
- [ ] Settings deep link disponibile se permission negata 2 volte (handle_permissions_contract).

## I. Performance & UX mobile

- [ ] Touch target >= 44px (iOS) / 48px (Android).
- [ ] Safe area top/bottom rispettata su notch e gestures bar.
- [ ] Pull-to-refresh dove rilevante (catalog/inventory).
- [ ] Activity indicator durante fetch >300ms.
- [ ] Nessun crash su rotation/foreground/background.

## J. Invarianti di sicurezza esplicite

- [ ] `reward_live_general=false` su ogni health endpoint.
- [ ] `release_readiness_claimed=false` su ogni health endpoint.
- [ ] Nessuna mutation `users.gold/gems/experience` dopo flusso QA completo (verificato server-side).
- [ ] Nessuna activazione IAP/store/payment/gacha durante QA.
- [ ] Nessun grant Guild/Arena/PvP/Event/Battlepass/AFK reward live.

## K. Smoke automatico

- [ ] `backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py` ritorna `SMOKE PACK 109 CLOSED ALPHA RC OK`.

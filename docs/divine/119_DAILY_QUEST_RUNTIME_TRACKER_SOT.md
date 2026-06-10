# 119 — Daily Quest Runtime Tracker SOT (Pack 99)

Documento SOT del runtime tracker server-side per il completamento delle daily quest, introdotto dal `MEGA_RELEASE_ACCELERATION_99_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_CONTROLLED_UNLOCK`.

## Identificazione

- Tracker id: `daily_quest_completion_runtime_tracker`
- Pack di origine: `pack_99`
- Stringa di autorizzazione: `AUTORIZZO_V110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_UNLOCK_PACK_99`

## Storage

Collection MongoDB dedicata e server-scoped: `daily_quest_progress`.

Chiave canonica (unica): `(user_id, server_id, quest_id, day_iso)`.

Indice unico parziale: `ux_user_server_quest_day_pack99` con `partialFilterExpression={"_slc_pack_99_tracker": true}`. Tutti i documenti emessi da Pack 99 sono marcati `_slc_pack_99_tracker=true`.

## Stati

- `not_started` — nessun documento o documento inizializzato.
- `in_progress` — opzionale; non usato dall'endpoint MVP, riservato per futura espansione gameplay reale.
- `completed` — completion confermata server-side (test-only via marker `pack_99_test_artifact` finché non esiste un runtime di gameplay reale).
- `claimed` — claim eseguito: l'endpoint `daily_quest_claim` ha aggiornato `claimed_at` e bloccato il replay reward.

## Whitelist

Unico set ammesso: `{daily_quest_1, daily_quest_2, daily_quest_3}` (coerente con Pack 98). Qualunque altro `quest_id` → HTTP 422 `QUEST_ID_NOT_WHITELISTED`.

## Endpoint progress

- `GET /api/daily-quest/progress?server_id=<sid>` — restituisce lo stato corrente di tutte le quest in whitelist per il giorno UTC corrente; documenti mancanti sono normalizzati come `not_started`.
- `POST /api/daily-quest/progress/complete?server_id=<sid>&quest_id=<qid>` — segna lo stato a `completed` SOLO se l'utente è marcato `pack_99_test_artifact=true` (test-only) o per i futuri runtime gameplay-authoritative. NESSUN reward viene concesso.

## Sicurezza

- Server-side only: il client non può impostare lo stato `completed` direttamente.
- Idempotency: completion ripetuta è idempotente, non crea duplicati, non concede reward.
- Server scoping stretto: nessun documento cross-server, no fallback s1, no PSP-less write.
- Kill switch: `DAILY_QUEST_TRACKER_ENABLED` (default OFF). Quando OFF l'endpoint progress GET resta consultabile per health/dry-run, ma il POST/complete è bloccato.
- Test marker: `pack_99_test_artifact=true` su `users` e `player_server_profiles` autorizza l'uso del completion endpoint per smoke E2E.
- Nessun client payload viene applicato al reward (rimane `{mission_coins: 15, honor: 8}` fisso server-side).

## Collegamento con il claim (Pack 98 → Pack 99)

L'endpoint `POST /api/daily-quest/claim` consulta il tracker prima di concedere reward:

- Se `state != completed` → HTTP 409 `DAILY_QUEST_COMPLETION_REQUIRED`.
- Se `state == completed` → grant + transizione a `claimed` con timestamp `claimed_at`.
- Replay nello stesso giorno → idempotent_replay=true, nessun secondo grant, balance PSP invariato.
- Bypass legacy Pack 98 `test_completion_proof=true`+`pack_98_test_artifact=true` è mantenuto come fallback compatibilità ma è ora preferibile passare attraverso il tracker.

## Vincoli (non negoziabili)

- NO reward live general — `reward_live_general=false`.
- NO premium/hard currency grant.
- NO mail/achievements/battlepass/event/AFK rewards.
- NO grant fuori PSP.soft_currencies.
- NO scrittura a users.gold/gems.
- NO hardcoded server_id="s1" sul path attivo daily.
- NO release readiness claim.

# 211 — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION

**Verdict locale**: `PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Timestamp UTC**: 2026-05-30T15:00:00Z

**Mode**: `FRONTEND_FOUNDATION_LOCAL_ONLY`

---

## Scopo

Aggiunge al PostBattle Summary 3 azioni accessory:

- **▶ Replay** — overlay visivo-only sulla timeline gia' calcolata.
- **💾 Salva** — snapshot locale via AsyncStorage (max 20 entries).
- **↗ Condividi** — `Share.share` con testo summary only.

La foundation è **frontend-only**. NESSUN endpoint backend nuovo. NESSUN DB write.
NESSUN reward grant. NESSUN RNG rerun. NESSUNA chiamata a `/api/battle/simulate`.

## File aggiunti

- `frontend/components/battle/battleReplayTypes.ts` (tipi snapshot + storage key + cap)
- `frontend/components/battle/BattleReplayPreview.tsx` (overlay play/pause/step/restart/close)
- `frontend/utils/buildBattleReplaySnapshot.ts` (builder puro)
- `frontend/utils/battleReplayStorage.ts` (AsyncStorage helper)
- `frontend/utils/battleShareText.ts` (text builder)

## File modificati

- `frontend/components/battle/PostBattleSummary.tsx` (+3 bottoni mini + overlay wiring)

## File NON modificati (vincoli assoluti)

- `backend/battle_engine.py`
- `backend/.env`
- `backend/routes/artifacts.py`
- `frontend/app/battlepass.tsx`
- `frontend/app/vip.tsx`
- nessuna nuova route backend per replay/save/share
- nessun broad refactor di `combat.tsx`

## Replay behavior

- Apre overlay sopra `PostBattleSummary` con timeline gia' calcolata dal `battle_report` ricevuto.
- Etichette esplicite: `REPLAY VISIVO`, `NESSUNA RICOMPENSA`, `NESSUN EXP`.
- Controlli: Play / Pausa / Step / Riavvia / Chiudi.
- **NON** chiama `/api/battle/simulate` né alcun endpoint di reward/claim.
- **NON** altera stato di battaglia né conta turni.

## Save behavior

- Storage: `AsyncStorage` con chiave `divinewaifus.saved_battle_replays.v1`.
- Max 20 entries, eviction oldest-first.
- Sanitize: rimuove qualsiasi campo sensibile (token, email, account id, reward claim state).
- Flags forzati nello snapshot: `local_only: true`, `server_synced: false`, `rewards_disabled: true`,
  `exp_disabled: true`, `grants_disabled: true`, `no_rng_rerun: true`.
- Feedback UI inline: `Salvato (n/20)` / `Aggiornato (n/20)` / `Salvataggio fallito`.

## Share behavior

- API: React Native `Share.share({ message })`.
- Testo: `Divine Waifus — {Vittoria!|Sconfitta.} MVP: {nome}, Danni totali: {n}, Cure: {n}, Turni: {n}, Durata: {s}s.`
- **Nessun URL**, **nessun share code**, **nessun user/account/token id**.
- Fallback graceful in web/simulator (catch silenzioso).

## DB writes

**= 0**. Nessuna scrittura DB. Nessuna nuova route backend.

## Forbidden scope confirmation

- ✅ Replay non chiama `/api/battle/simulate`
- ✅ Replay non duplica reward / EXP / item / quest / daily / achievement
- ✅ Save è strettamente local AsyncStorage
- ✅ Share è strettamente plain text
- ✅ No server replay storage, no share code, no public URL
- ✅ No gacha/economy/BP/VIP/shop/Artifact/DW/Gem/Rune runtime touch
- ✅ No `combat.tsx` broad refactor
- ✅ No `battle_engine.py` / `.env` / `artifacts.py` / `battlepass.tsx` / `vip.tsx` mod
- ✅ No validator weakening, no fake PASS

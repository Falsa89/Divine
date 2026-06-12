# Closed Alpha Internal QA — Tester Feedback Form Template

Compila una copia per ogni sessione di test e invia al coordinatore QA.

## Tester info

- Tester ID / nickname:
- Tester ruolo (interno / esterno fidato):
- Device modello:
- OS / OS version (es. iOS 17.4, Android 14):
- App build / commit hash (fornito dal coordinatore):
- Server testato (S1 / S2 / S1->S2->S1):
- Account utilizzato (fresh / returning):
- Data e ora sessione:
- Durata sessione (minuti):

## Checklist sezioni A–O eseguite

- [ ] A Install / startup
- [ ] B Auth / logout
- [ ] C Server selection / server switch
- [ ] D Home / Lobby / navigation
- [ ] E Story / battle preview / staging
- [ ] F Tower strict loop
- [ ] G Daily login / daily quest
- [ ] H Controlled rewards
- [ ] I Economy strict shop/soul/equipment/forge/fusion
- [ ] J Inventory / equipment / material scope
- [ ] K Guild strict / legacy quarantine
- [ ] L Arena / PvP / Event locked/deferred state
- [ ] M Performance / loading / crash / memory
- [ ] N UI/UX mobile readability
- [ ] O Safety invariants

## Bug trovati

| Severità | Area (A–O) | Titolo breve | Steps to reproduce | Atteso | Osservato | Screenshot/video URL |
|----------|-----------|--------------|--------------------|--------|-----------|----------------------|
|          |           |              |                    |        |           |                      |
|          |           |              |                    |        |           |                      |
|          |           |              |                    |        |           |                      |

Legenda severità: P0 (blocker), P1 (alpha-blocker), P2 (workaround), P3 (polish).

## UX feedback (libero)

_(scrivi qui suggerimenti di copy, spacing, navigazione, naming)_

## Performance / crash notes

- Numero di crash osservati:
- Freeze >5s osservati (numero):
- Memory pressure warning (iOS / Android):
- Battery drain percepito:

## Verdict tester finale

- [ ] Usable for internal alpha (no blocker)
- [ ] Usable with blockers (P0 o P1 presenti)
- [ ] Not usable (impossibile completare la sessione)

## Safety invariants check (importante)

- [ ] Nessun grant inatteso a `gold/gems/experience`.
- [ ] Nessuna popup IAP/store/payment/gacha.
- [ ] Nessun reward live Guild/Arena/PvP/Event/Battlepass/AFK osservato.
- [ ] Nessuna label "Disponibile"/"Ready" su surface con reward live OFF.

Se almeno una delle voci sopra è violata: segnala con severità **P0** e
allega screenshot/video.

# Closed Alpha Internal QA — Tester Runbook (Italiano)

Questo runbook è lo strumento operativo per i tester della **Closed Alpha
interna**. NON è public launch. NON è production release. Tutti i
sistemi reward live sono `OFF` di default; eventuali grant non sono
attesi e devono essere segnalati come **P0**.

Fonte: Pack 109 Mobile QA Checklist + PROMPT_MAIN del Runbook QA.

## 0. Cosa ti serve prima di iniziare

- Device mobile (iOS o Android). Le builds Expo Go bastano per la maggior
  parte dei flussi; alcuni flussi push/audio richiedono development build
  (al momento non testati in questo ciclo).
- Account test (ti viene assegnato un username/password dal coordinatore QA
  via canale privato). Per ogni tester:
  - **almeno 1 account fresh** (creato durante il test);
  - **almeno 1 account returning** (esistente).
- 30-45 minuti di tempo continuativo.
- Connessione internet stabile.

## 1. Build / install

1. Apri Expo Go (iOS App Store / Google Play).
2. Scansiona il QR code di test fornito dal coordinatore (URL preview Pack 109).
3. Attendi il bundle Metro (max 60s su rete LAN).
4. **Atteso**: app entra nello splash, poi Login.
5. **Da segnalare**: crash al boot → **P0**.

## 2. Sezione A — Install / startup

- [ ] App si apre senza crash su prima esecuzione.
- [ ] Non vengono richieste permission inutili al primo boot.
- [ ] Splash/Login screen renderizza con safe area top/bottom corrette.
- [ ] No errore di rete in barra superiore dopo splash.

## 3. Sezione B — Auth / logout

- [ ] Login con credenziali test funziona.
- [ ] Logout dal menu profilo riporta a Login.
- [ ] Dopo logout, riapri l'app: NON deve auto-loggare con l'utente precedente.
- [ ] Re-login con altro account: PSP precedente non leakato.
- [ ] Wrong password → errore visibile (non crash).

## 4. Sezione C — Server selection / server switch

- [ ] Selezione server visibile prima/dopo login (a seconda del flow).
- [ ] Nessun server preselezionato di default a `s1` senza interazione utente.
- [ ] Cambio S1 → S2: dati lobby/home si aggiornano (no stale `s1` cache).
- [ ] Cambio S2 → S1: dati ritornano corretti, non mostrano S2.
- [ ] **Da segnalare**: dati di un server appaiono sull'altro → **P0** (server-scope leak).

## 5. Sezione D — Home / Lobby / Navigation

- [ ] Home renderizza correttamente, no overflow.
- [ ] Lobby pre-battle entrypoint visibile (anche se locked/gated).
- [ ] Bottom nav o tab navigation accessibile con pollice (44px target).
- [ ] Surface deferred mostrano copy `In preparazione (deferred)` o `Bloccato (Closed Alpha)`.
- [ ] **NESSUNA surface deve mostrare "READY"** se la reward live è OFF.

## 6. Sezione E — Story / Battle preview / staging

- [ ] Story map raggiungibile se UI flag attivo, altrimenti correttamente locked.
- [ ] Nessun click attiva `/api/battle/simulate` live (segnalare se ricevi result reward immediato → **P0**).
- [ ] Preview battle visibile read-only.

## 7. Sezione F — Tower strict loop

- [ ] Tower entrypoint mostra `READY_GATED` o `Bloccato`.
- [ ] Preflight/preview eventualmente accessibile come read-only.
- [ ] Tower piano corrente del PSP corretto (no leak S2 in S1).

## 8. Sezione G — Daily login / Daily quest

- [ ] Daily entrypoint visibile, locked se kill switch OFF.
- [ ] Tentativo claim NON deve mostrare success se backend ha kill switch OFF.
- [ ] Re-claim sullo stesso slot non duplica reward (idempotency).

## 9. Sezione H — Controlled rewards

- [ ] Mail / Achievements / Daily-Weekly: mostrano `deferred` o `gated`.
- [ ] Nessun grant accidentale.
- [ ] `users.gold/gems/experience` invariati dopo navigazione (verifica con coordinatore).

## 10. Sezione I — Economy strict

- [ ] Shop: catalogo visibile read-only, nessun acquisto live.
- [ ] Soul Forge: surface gated.
- [ ] Equipment / Forge / Upgrade / Fusion: gated; nessuna mutation `users.*`.
- [ ] PSP material count consistent dopo navigazione (no leak).

## 11. Sezione J — Inventory / Equipment / Material

- [ ] Inventory letta dal PSP corretto del server selezionato.
- [ ] Cambio server cambia inventory (no leak cross-server).
- [ ] Equip/Unequip locked o solo preview.

## 12. Sezione K — Guild strict / legacy quarantine

- [ ] Guild list/search funziona in preview (sola lettura).
- [ ] Nessuna creazione guild legacy: tentativo → errore 423 `GUILD_LEGACY_QUARANTINED`.
- [ ] Membership preview NON crea record reale.

## 13. Sezione L — Arena / PvP / Event

- [ ] Tutte e 3 le surface mostrano `Bloccato (Closed Alpha)` o `In preparazione (deferred)`.
- [ ] Tentativo di entrare in match: NON deve produrre reward live (segnalare se accade → **P0**).

## 14. Sezione M — Performance / loading / crash / memory

- [ ] Sessione di 20+ minuti senza crash.
- [ ] Nessun freeze >5s su scroll/navigazione.
- [ ] Loading indicator quando network >300ms.
- [ ] App resta usabile dopo foreground/background switch.

## 15. Sezione N — UI/UX mobile readability

- [ ] Testo leggibile in tutte le surface.
- [ ] Bottoni con target tappabile sufficiente.
- [ ] Safe area su notch/gesture bar rispettata.
- [ ] Copy italiana coerente (deferred/locked/preview).

## 16. Sezione O — Safety invariants (CRITICA)

- [ ] `users.gold/gems/experience` NON si modificano spontaneamente (chiedi al coordinatore di confermare lato server prima e dopo la sessione).
- [ ] Nessuna popup IAP/store/payment/gacha live.
- [ ] Nessun grant Guild/Arena/PvP/Event/Battlepass/AFK reward live.
- [ ] Nessuna label "Disponibile" su feature reward live OFF.

## 17. Compilazione feedback

Usa il template `/app/docs/divine/templates/qa_tester_feedback_form.md` (copia,
compila, invia al coordinatore). Inoltra screenshot/video di ogni bug.

## 18. Severità bug (riferimento rapido)

- **P0** — app cannot launch / login/server selection broken / server-scope leak / silent `s1` / reward live accidentale / users.* mutation imprevista / IAP/gacha accidentale / crash blocca loop.
- **P1** — core flow bloccato per molti tester / strict health unusable / layout mobile rotto / refresh inconsistente / crash ripetuto.
- **P2** — feature non-critica rotta con workaround / label gated/deferred confusing / preview inconsistente senza mutation / UI/loading intermittente.
- **P3** — copy / spacing / minor UX.

## 19. Cosa NON è in scope (NON segnalare come bug)

- Reward live disabilitati (atteso, deferred).
- Arena/PvP/Event rewards `OFF` (atteso, deferred).
- IAP/Gacha/Battlepass/AFK assenti (atteso, deferred).
- Guild chat/war non funzionanti (atteso, `DEFERRED`).
- Push notifications (atteso: richiede development build).

## 20. Dopo la sessione

- Compila il feedback form.
- Includi screenshot/video per ogni bug.
- Indica device, OS, build commit (fornito dal coordinatore).
- Indica server testato (S1, S2, o entrambi).

# RM1.24-A — Player Faction V2 Selection UI Foundation

## Perché ora

I test bilanciati delle Team Synergies V2 in battaglia sono rimandati alla fase pre-release.  
Gli avversari attuali sono placeholder e troppo deboli: testare ora i buff darebbe dati poco utili.

Il prossimo ramo utile è quindi l'identità account: **Player Faction V2**.

## Obiettivo

Creare una schermata dove il giocatore può vedere e scegliere la propria fazione/account identity.

La fazione player è un sistema identitario, sociale e live/event-oriented:
- identità mitologica dell'account;
- futura integrazione con gilda, eventi, ranking e war avatar;
- possibile uso in contenuti community/server;
- non deve essere subito un bonus combat importante.

## Source of truth

Usare prima di tutto il file esistente:

`backend/data/synergy_definitions_v2.py`

e in particolare:

`PLAYER_FACTION_DEFINITIONS_V2`

RM1.23-A aveva trovato 13 definizioni: 8 onboarding + 5 internal/future.  
Emergent deve ispezionare lo schema reale e adattarsi.

## UI richiesta

Route consigliata:

`/player-faction`

Titolo:

`Fazione del Giocatore`

Stati:

1. Nessuna fazione scelta
   - mostra lista fazioni disponibili;
   - CTA `Scegli fazione`;
   - nota: `Avrai 1 cambio gratuito`.

2. Fazione già scelta
   - mostra la fazione corrente;
   - mostra identità, tema, descrizione;
   - CTA secondaria `Cambia fazione`;
   - non implementare monetizzazione.

3. Fazione locked/future
   - mostra locked o nascondi, in base allo schema esistente.

## Entry point

Aggiungere entry point low-risk:
- Menu;
- Profilo/account panel se semplice;
- future onboarding solo come route pronta, senza forzare registrazione se rischioso.

## Regola sul cambio fazione

La prima scelta deve essere importante ma non punitiva.  
Concetto approvato:

`1 cambio fazione gratuito`

Per questa task, il token può essere:
- solo UI/read-only se si mantiene tutto foundation;
- oppure salvato in `users.faction_change_tokens = 1` solo se Emergent implementa un endpoint write sicuro.

## Scope consigliato

### Prima preferenza
Implementazione read-only/foundation:
- endpoint lista fazioni;
- endpoint stato utente;
- UI pagina;
- entry point.

### Scrittura opzionale solo se sicura
`POST /api/user/faction-v2/select`

Requisiti:
- auth required;
- tocca solo `users`;
- niente heroes, user_heroes, teams;
- initial select se empty;
- cambio solo se token gratuito disponibile;
- niente currency spend;
- report dettagliato.

## Vietato

- Non applicare bonus combat.
- Non cambiare gacha.
- Non cambiare battle engine.
- Non modificare Team Synergies V2.
- Non modificare Character Bible.
- Non modificare kit JSON.
- Non toccare asset.
- Non attivare Borea.
- Non fare live gacha pull.
- Non fare registrazione live.
- Non spendere valute.

## Validazione

Controllare:
- pagina rende su mobile;
- lista fazioni visibile;
- entry point menu/profilo;
- `/api/heroes=100`;
- summon eligible=100;
- starter eligible=20;
- Borea hidden;
- V2 battle flag resta false;
- nessun errore TS nei file modificati.

## Report richiesto

- file ispezionati;
- file modificati;
- endpoint aggiunti;
- stato write/read-only;
- smoke UI;
- safety checks.

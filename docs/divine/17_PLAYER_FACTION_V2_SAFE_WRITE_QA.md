# RM1.24-B — Player Faction V2 Selection Safe-Write QA

## Decisione di design

La prima scelta della fazione V2 **non consuma** il token gratuito.

Regola stabile:

- se l'utente non ha ancora `player_faction_v2`, la prima scelta è gratuita;
- dopo la prima scelta resta `player_faction_v2_change_tokens = 1`;
- il primo cambio successivo consuma 1 token;
- dopo quel cambio il token scende a 0;
- ulteriori cambi saranno futuri, tramite token/eventi/shop, ma non in questa task.

## Obiettivo

Validare e, se necessario, correggere l'endpoint:

`POST /api/user/faction-v2/select`

La task deve garantire che la scrittura sia sicura e limitata al documento utente.

## Campi consentiti

L'endpoint può scrivere solo:

- `users.player_faction_v2`
- `users.player_faction_v2_selected_at`
- `users.player_faction_v2_changed_at`
- `users.player_faction_v2_change_tokens`

Non deve toccare:

- `users.faction` legacy;
- `heroes`;
- `user_heroes`;
- `teams`;
- currencies;
- gacha;
- battle state.

## Stati da validare

### Nessuna fazione selezionata

Prima:
- `player_faction_v2` assente/null;
- token assente o 1.

POST con fazione onboarding valida.

Dopo:
- `player_faction_v2` impostata;
- `player_faction_v2_selected_at` impostato;
- token resta 1;
- `users.faction` invariato.

### Fazione già selezionata, token 1

POST con fazione diversa valida.

Dopo:
- `player_faction_v2` aggiornata;
- `player_faction_v2_changed_at` impostato;
- token diventa 0;
- `users.faction` invariato.

### Fazione già selezionata, token 0

POST con fazione diversa valida.

Risultato:
- reject 4xx;
- nessuna mutazione.

### Fazione locked/future

Risultato:
- reject 4xx;
- nessuna mutazione.

### Fazione sconosciuta

Risultato:
- reject 4xx;
- nessuna mutazione.

### Reselect stessa fazione

Risultato:
- no-op safe;
- token non consumato.

## Sicurezza

Non fare gacha, registrazione, spend currency, battle test o migrazioni.  
Se serve un test write, usare un utente disposable o snapshot/rollback chiaro.

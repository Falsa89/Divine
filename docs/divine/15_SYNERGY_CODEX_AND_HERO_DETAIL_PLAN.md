# RM1.23-C — Synergy Codex + Hero Detail Synergy Palette

## Obiettivo
Creare una schermata dedicata allo studio delle sinergie, collegata alla Collezione Eroi e al dettaglio eroe.

Il giocatore deve poter capire quali sinergie esistono, quali sono attive, quali può attivare con gli eroi posseduti, quali gli mancano, quali eroi servono per completare una build, e come le stelle degli eroi migliorano la forza della sinergia.

## Concetto centrale
Questa task è UI/read-only. Non crea un sistema di upgrade con valuta.
Il potenziamento visibile della sinergia deriva automaticamente dalle stelle degli eroi coinvolti.

## Schermata dedicata
Nome consigliato: `Codex Sinergie`.

Entry point consigliati:
1. Collezione Eroi;
2. Menu;
3. Dettaglio eroe come sezione contestuale.

## Sezioni
- Sinergie Team: Team Synergies V2 canonical-ID based da RM1.23-B.
- Formazione: guida a bonus compositivi element/faction/role.
- Elementi: guida a elementi/affinità. Non correggere il bug lightning/dark in questa task.
- Collezione: placeholder futuro per collection synergies.

## Stati sinergia
- Attiva: requisiti nel team attivo.
- Disponibile: eroi richiesti posseduti ma non tutti nel team.
- Quasi attiva: parte degli eroi posseduta/in team.
- Non posseduta: mancano uno o più eroi.
- Futura: categoria non ancora live.

## Hero Detail
Aggiungere sezione `Sinergie` con tab:
- In team
- Attive
- Non attive

Ogni card mostra nome sinergia, eroi richiesti, badge owned/not-owned/in-team, bonus attuale, preview da stelle se possibile, lore breve.

## Sicurezza
Nessuna scrittura DB, nessuna migration, nessun apply, nessuna gacha pull, nessuna registrazione, non abilitare `SYNERGY_V2_BATTLE_ENABLED`, non attivare Borea, non modificare battle engine, Character Bible, kit JSON o asset.

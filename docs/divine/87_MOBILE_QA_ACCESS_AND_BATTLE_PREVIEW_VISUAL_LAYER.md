# 87 · Mobile QA Access & Battle Preview Visual Layer

## Obiettivo
1. **Sbloccare l'accesso QA mobile** alla preview v86 senza route manuali: hub diretto `/mobile-qa-battle-preview`.
2. **Aggiungere il primo visual layer** preview-only su `playable-mode-battle-preview`: portrait/silhouette placeholder, HP bar locali reattive, turn highlight, bersaglio del turno.

## Vincoli
- `preview_only=true`, `deterministic=true`, `authoritative=false`
- `reward_grant=false`, `db_write=false`, `account_mutation=false`
- `inventory_mutation=false`, `battle_engine_attached=false`
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`
- Nessun asset finale, nessun import battle_engine/story/combat, nessun fetch HTTP, nessun AsyncStorage
- MD5 lock dei file core invariato

## Percorso mobile diretto
1. Apri l'app (Expo Go o web preview).
2. Vai a: `/mobile-qa-battle-preview`.
3. Tocca una delle 6 modalità (Training, Story, Boss, Tower, Event, Arena).
4. Premi "Avvia battaglia preview ›" per scorrere la timeline turni con HP bar reattive.

In alternativa: dall'`/alpha-menu-preview` → entry **"Playable Mode Visual Battle Preview (v86)"** → si arriva alla stessa schermata.

## Visual layer applicato
- Portrait placeholder: prima lettera dell'alias + colore accent deterministico (8 colori, hash dell'alias).
- HP bar reattiva: HP locale aggiornato accumulando `preview_dmg`/`preview_heal` dello step corrente.
- Turn highlight: bordo `#22d3ee` su attore e target del turno.
- Bersaglio del turno: tag testuale sotto il portrait dell'unità colpita.

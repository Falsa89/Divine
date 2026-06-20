# Device QA Manual Checklist — PACK 133

> Checklist eseguibile da umano su device fisico o Expo Go.
> NESSUN passo di questa checklist viene auto-eseguito dall'harness Pack 133.
> Tutti i passi marcati MANUAL_REQUIRED restano tali finché un revisore non li esegue e firma.

---

## 0. Prerequisiti env

Verificare che le seguenti variabili d'ambiente siano valorizzate **solo nella sessione del revisore**:

- `QA_TEST_BASE_URL` — URL backend (es. `http://127.0.0.1:8001`)
- `QA_TEST_JWT` — JWT account QA **(NON committare, NON loggare raw)**
- `QA_TEST_SERVER_ID` — server QA (es. `s1`)
- `QA_TEST_USER_ID` — user ID QA
- `QA_DEVICE_PLATFORM` — `ios` | `android` | `expo-go`
- `QA_DEVICE_LABEL` — label leggibile (es. `iPhone 13 Expo Go`)
- `QA_EVIDENCE_DIR` — cartella locale per screenshot sanitizzati (es. `docs/divine/evidence/pack_133/<reviewer>`)

Secret redaction policy: l'harness usa solo fingerprint (sha256 12 char) del JWT, mai il JWT in chiaro.

## 1. Account QA

- account QA esistente, **NON shared con utenti reali**
- email QA dedicata (non personale del revisore)
- ruolo: utente normale (no admin) per testare flussi end-user

## 2. Server QA

- server QA esistente e operativo
- server scope = utente QA è bound al server QA
- nessun seed di reward / EXP / inventory aggiuntivi per test

## 3. JWT / Credenziali

- JWT ottenuto via login QA, mai loggato in raw
- mai screenshot del JWT
- mai paste del JWT in chat / report / commit
- al termine della sessione il JWT va invalidato lato backend (manual step)

## 4. Avvio backend

- backend FastAPI in esecuzione su `:8001`
- `/api/health` ritorna `200 OK`
- log backend pulito (no `5xx` non motivati, no error spam)

## 5. Avvio Expo

- Expo dev server (Metro) avviato senza errori
- bundle scaricato su device / Expo Go
- nessuna route deeplink lockdown violata (vedere Pack 128)

## 6. Test Home / Menu

- Home schermata si carica
- navigazione coerente
- nessuna richiesta mutativa parte allo startup (vedere Pack 127)

## 7. Test server selection

- selezione server QA possibile
- server scope correttamente propagato (vedere Pack 129)
- nessun fallback account-wide della formazione (vedere Pack 129)

## 8. Test pre-battle lobby

- pre-battle lobby si carica con il server QA
- nessuna mutazione DB osservata (vedere Pack 130)

## 9. Test launch context preview

- chiamata `GET /api/lobby/launch-context/preview?mode=training&server_id=<QA_TEST_SERVER_ID>` ritorna 200 + payload coerente
- `preview_only: true`, `authoritative: false`
- `team_a` proiettato dal real player snapshot (vedere Pack 130)
- nessun DB write osservato

## 10. Test combat preview

- chiamata `GET /api/combat/preview?mode=training&server_id=<QA_TEST_SERVER_ID>` ritorna 200 + payload coerente
- `combat_consumption_status: PACK_131_PREVIEW_ONLY`
- `battle_engine_execution_status: BATTLE_ENGINE_EXECUTION_DEFERRED`
- nessun DB write osservato

## 11. Test post-battle preview safe

- payload `post_battle_preview` espone:
  - `preview_only: true`
  - `authoritative: false`
  - `claim_enabled: false`
  - `claim_disabled: true`
  - `not_granted: true`
  - `reward_status: DISABLED`
  - `exp_status: DISABLED`
  - `progress_status: DISABLED`
  - `inventory_mutation: false`
  - `economy_mutation: false`
  - `hero_progression_mutation: false`
  - `potential_rewards_preview_only: []`

## 12. Verifica no reward / no EXP / no progress

Dopo i passi 9–11, verificare manualmente:

- **no reward** concesso al wallet
- **no EXP** aggiunto a hero o account
- **no progress** aggiornato (stage, mission, season)
- **no inventory mutation**
- **no economy spend/grant**
- **no hero progression mutation**

Qualunque mutazione osservata = **BLOCKED**, fermarsi e segnalare.

## 13. Screenshot richiesti

Il revisore raccoglie e salva in `$QA_EVIDENCE_DIR` (sanitizzati: niente JWT, niente email, niente dati personali):

- screenshot Home / Menu
- screenshot Server selection
- screenshot Pre-battle lobby
- screenshot Combat preview
- screenshot Post-battle preview safe
- log backend (estratto pulito) del run autenticato
- log frontend / Expo (estratto pulito) del run autenticato

Criteri di sanitizzazione:
- redigere Authorization header
- redigere JWT raw
- redigere email personali
- redigere ID che possono essere PII

## 14. Log richiesti

- log backend con timestamp inizio/fine sessione
- log frontend Expo con timestamp inizio/fine sessione
- entrambi sanitizzati come sopra

## 15. Criteri PASS

- tutti i passi §4–§12 superati senza errori
- tutti gli screenshot §13 raccolti e sanitizzati
- tutti i log §14 raccolti e sanitizzati
- nessuna mutazione DB / reward / EXP / progress osservata
- nessun endpoint vietato chiamato
- signoff §17 firmato

Anche con PASS pieno, il massimo verdetto Pack 133 dichiarabile è:
`READY_FOR_MANUAL_DEVICE_QA_REVIEW`. Non release-ready.

## 16. Criteri FAIL / BLOCKED

**Criteri FAIL:**

- uno o più passi §4–§12 falliti

**Criteri BLOCKED:**

- osservata mutazione DB / reward / EXP / progress / economy / inventory durante GET preview
- osservato leak di JWT / password / secret in screenshot o log
- endpoint mutativo chiamato accidentalmente
- forbidden area runtime toccata in delta repo

## 17. Signoff manuale

Il revisore compila in fondo a questa checklist (in una propria copia locale, non sul file repo):

```
Reviewer: <iniziali>
Data (UTC): <YYYY-MM-DDTHH:MM:SSZ>
Device: <platform / label>
Build: <commit SHA Pack 133>
Risultato: <PASS / FAIL / BLOCKED>
Note: <breve descrizione>
Firma: <firma manuale o hash>
```

Il signoff manuale NON è auto-generabile. Senza signoff firmato, lo stato resta:

```
MANUAL_SIGNOFF_STATUS = MANUAL_REQUIRED
```

---

> Questa checklist è uno strumento di lavoro umano. La sua presenza nel repo NON implica che sia stata eseguita. L'esecuzione e il signoff devono essere tracciati separatamente (issue tracker / docs/divine/evidence/pack_133/).

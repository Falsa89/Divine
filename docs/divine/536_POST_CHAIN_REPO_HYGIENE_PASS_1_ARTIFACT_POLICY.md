# POST_CHAIN_REPO_HYGIENE_PASS_1 — ARTIFACT POLICY (docs + `.emergent` noise)

> Documento di policy. Non modifica codice runtime, validatori o suite Pack 127→133.
> Stato: **`DOCUMENTED`** (consultivo).
> Lingua: italiano.

## Artifact policy — overview

L'obiettivo è distinguere chiaramente, nei range git futuri, tra:

1. **Tracked audit artifacts** — file dichiarativi del modello di sicurezza/audit (marker, report MD, validatori).
2. **Runtime / build artifacts** — file rigenerati automaticamente dall'esecuzione di suite e harness (report JSON in `backend/scripts/reports/`).
3. **Non-functional noise** — file `.emergent/emergent.yml` auto-timestamped da Emergent.

La policy NON cancella file. NON modifica `.gitignore`. È una guida di **contabilizzazione** per gli audit Codex/Game Master.

---

## Tracked audit artifacts (rilevanti per Pack scope)

| Categoria | Path | Note |
| --- | --- | --- |
| Marker JSON di sicurezza | `data/design/system_safety/*.json` | dichiarativi, scope Pack, **inclusi nel conteggio Pack** |
| Report MD finali | `docs/divine/52*_*FINAL_REPORT.md`, `53*_*FINAL_REPORT.md` | narrativa Pack, **inclusi nel conteggio Pack** |
| Validator Python | `backend/scripts/validate_pack_*.py`, `backend/scripts/validate_post_chain_*.py` | logica audit, **inclusi nel conteggio Pack** |
| Harness e builder | `backend/scripts/device_qa_evidence_harness.py`, `backend/scripts/device_qa_evidence_manifest_builder.py`, `backend/scripts/pre_device_qa_authenticated_smoke_harness.py` | strumenti audit, **inclusi nel conteggio Pack** |
| Suite runner | `backend/scripts/run_pack_*_safety_suite.py`, `backend/scripts/run_post_chain_*_suite.py` | orchestrazione, **inclusi nel conteggio Pack** |
| Checklist e manifest MD | `docs/divine/device_qa_manual_checklist_PACK_*.md`, `docs/divine/device_qa_evidence_manifest_PACK_*.md` | strumenti umani, **inclusi nel conteggio Pack** |

Policy: questi file restano **tracked** in git, hanno scope dichiarato per ogni Pack, e devono essere contabilizzati negli audit Codex/Game Master.

---

## Runtime / build artifacts (rumore di esecuzione)

| Path | Origine | Conteggio audit |
| --- | --- | --- |
| `backend/scripts/reports/*.json` | scritti automaticamente dai validatori a ogni esecuzione (`pack_NNN_*_report.json`, `pre_device_qa_*_report.json`, ecc.) | **esclusi dal conteggio Pack scope**, **inclusi nel range pubblico** come build artifacts |
| `backend/reports/pack_*_safety_suite_*.json`, `*_latest.json` | rotazione output suite runner (per-run + latest) | idem |

Classificazione: questi file sono **tracked** ma rappresentano **artefatti runtime**. Nei range git fra Pack consecutivi, possono comparire modifiche a questi file SOLO perché la suite è stata eseguita.

### Conteggi audit (regola di contabilizzazione)

Negli audit Codex/Game Master di un Pack `N`, fra i SHA `[baseline_N-1 .. final_N]`:

- **Pack scope (file dichiarati nel Pack)** = `(file aggiunti)` + `(file modificati funzionali)`.
- **Range pubblico completo** = Pack scope + `(report JSON runtime/build artifacts modificati)` + `(.emergent/emergent.yml se toccato)`.
- I report JSON runtime/build artifacts NON sono considerati feature drift, NON sono DB write, NON sono Pack 134+ leak.
- Vanno comunque scansionati per evidenza di leak segreti (vedi `validate_post_chain_no_secret_leak_in_reports.py`).

### No secret leak

Tutti i report JSON runtime devono essere periodicamente scansionati per:

- JWT real-looking (`eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}`)
- `Authorization: Bearer <real JWT>`
- assegnazioni letterali `password=...` / `access_token=...` / `refresh_token=...` (≥8 char)

Il validator `validate_post_chain_no_secret_leak_in_reports.py` esegue questa scansione su tutti i `backend/scripts/reports/*.json`.

### Proposta opzionale (non eseguita)

Potrebbe essere proposto in futuro:

- aggiungere `backend/scripts/reports/*.json` a `.gitignore` per ridurre il rumore git—
MA solo se accettato dal Game Master e dopo migrazione delle baseline (le `truth_sync` Pack precedenti referenziano alcuni report JSON come fonte di verità).
- **In questo pass non viene modificato `.gitignore`** né cancellato alcun file.

---

## `.emergent` timestamp / noise policy

Il file `.emergent/emergent.yml` viene aggiornato automaticamente da Emergent ad ogni job/run, modificando solo il campo `created_at` (ISO 8601 UTC).

### Quando cambia

- ad ogni avvio container Emergent.
- ad ogni auto-commit `Auto-generated changes`.
- non cambia per modifiche utente al codice.

### Perché compare nei range

Compare nei range git audit fra due Pack consecutivi semplicemente perché è stato aggiornato durante l'esecuzione automatica dell'ambiente Emergent. Non rappresenta una decisione di progettazione o un cambiamento funzionale.

### Come contabilizzarlo nei futuri audit

- **Pack scope**: ESCLUDERE.
- **Range pubblico completo**: INCLUDERE come `1 file non-funzionale`, con etichetta `.emergent/emergent.yml (timestamp Emergent)`.
- Negli audit Codex/Game Master, dichiarare esplicitamente che il delta su `.emergent/emergent.yml` è limitato a `created_at` ed è non-funzionale.

### Distinguere modifica funzionale

Se in futuro il file dovesse contenere modifiche **diverse** da `created_at` (es. nuove voci di configurazione, nuove env), allora va trattato come modifica funzionale e ispezionato. Per ora resta puro timestamp.

---

## Pack 134 / Future chain

- Pack 134 NON è iniziato.
- Il validator `validate_post_chain_future_pack_leak_guard.py` blocca file con nomi `pack_134..pack_999` / `v134_..v999_` / `536_PACK_134_..6\d{2}_PACK_999`.
- Menzioni testuali di "Pack 134" sono consentite nei report (es. roadmap, recommendation) ma NON file reali.
- Se in futuro viene autorizzato Pack 134, basta aggiornare la regex del leak guard per spostare la soglia.

---

## Recommendation

1. Lasciare `backend/scripts/reports/*.json` tracked per ora (i Pack precedenti li referenziano come baseline di verità).
2. Negli audit Codex/Game Master, contabilizzarli come **runtime/build artifacts** ESCLUSI dal Pack scope ma INCLUSI nel range pubblico.
3. Eseguire periodicamente `validate_post_chain_no_secret_leak_in_reports.py` per verificare assenza di leak segreti negli artefatti.
4. `.emergent/emergent.yml`: contabilizzare sempre come `1 file non-funzionale (timestamp)`.
5. Non autorizzare Pack 134 senza esplicito ok Game Master. Il leak guard è attivo.
6. Mantenere Device QA `MANUAL_REQUIRED`. Nessun release-ready / commercial-ready / public-ready / production-ready.

---

> Fine policy. Documento consultivo. NON modifica codice runtime né catena Pack 127→133.

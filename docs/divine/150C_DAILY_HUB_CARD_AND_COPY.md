# 150C — DAILY HUB CARD COMPONENT & COPY

## Track C — `PROJECT_FRONTEND_C_TRACK_C`

**Verdict:** `TRACK_C_DAILY_HUB_CARD_COMPONENT_AND_COPY_READY`

## Strategia componente

`inline_card_in_daily_hub_tsx_no_separate_component` — l'aggregatore ha sole 5 entry e non giustifica un componente separato. SafeFeatureCard (Pack Y) ha pattern diverso (locked-first).

## Copy italiana

### Banner
- **Titolo:** "La tua giornata in un colpo d'occhio"
- **Sottotitolo:** "Apri le sezioni per consultare e gestire le tue attività quotidiane. Nessuna ricompensa viene riscattata da qui."

### Footer
*"Questa schermata è un aggregatore. Nessun claim avviene qui: per riscattare ricompense usa direttamente la sezione dedicata (Posta, Eventi, Achievement, Battle Pass, Negozio)."*

### Entries (5)
- **Posta:** "Apri la posta per visualizzare e gestire i messaggi e le ricompense in arrivo."
- **Eventi Giornalieri:** "Sfide e attività a tempo. Apri la sezione eventi per vedere lo stato."
- **Achievement:** "Traguardi a lungo termine. Apri la sezione per consultare il progresso."
- **Battle Pass:** "Progressione stagionale. Apri il Battle Pass per i tier sbloccati."
- **Negozio:** "Bundle e offerte. Le ricompense giornaliere gratuite si trovano nel negozio."

## Vincoli

- ❌ No fake availability claim
- ❌ No countdown timer
- ✅ Copy chiara sul redirect alla sezione dedicata

## Validator

`validate_project_frontend_c_daily_hub_card_component_and_copy_v1.py` → **PASS**.

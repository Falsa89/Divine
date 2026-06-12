# Closed Alpha QA — Bug Triage Matrix (template)

Questa matrice raccoglie tutti i bug segnalati durante la Closed Alpha
interna. Una riga per bug. Aggiornata dal coordinatore QA.

## Tabella triage

| ID       | Severity | Sezione | Area              | Titolo | Tester (anonimo) | Device     | OS         | Steps to reproduce | Expected | Actual | Owner | Status | Pack target |
|----------|----------|---------|-------------------|--------|------------------|------------|------------|--------------------|----------|--------|-------|--------|-------------|
| P0-001   | P0       |         |                   |        |                  |            |            |                    |          |        |       | Open   | Pack 110    |
| P1-001   | P1       |         |                   |        |                  |            |            |                    |          |        |       | Open   | Pack 110/111|
| P2-001   | P2       |         |                   |        |                  |            |            |                    |          |        |       | Open   | Pack 111+   |
| P3-001   | P3       |         |                   |        |                  |            |            |                    |          |        |       | Open   | backlog     |

## Severity policy

- **P0** — must be fixed BEFORE any further alpha distribution. Pack 110 obbligato.
- **P1** — alpha-blocker per molti tester. Pack 110 o 111 dedicato.
- **P2** — workaround disponibile. Inseribile in pack di polish.
- **P3** — polish, non bloccante. Backlog.

## Decision tree (post-triage)

- Se P0 > 0: Pack 110 = P0 bugfix pack.
- Se P0 = 0 e P1 > 0: Pack 110 = P1 alpha-blocker cleanup pack.
- Se P0 = 0 e P1 = 0: Pack 110 candidate fra:
  - Daily Login claim live controlled rollout (richiede review economy/reward invariant).
  - Achievements authoritative completion.
  - Soul Forge live controlled rollout (richiede review).
  - Guild live runtime pack (richiede `AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT`).
  - Story / Tower UX polish pack (raccomandato come default safest).

Non raccomandare reward live se anche una sola economy/reward invariant è incerta
dopo i test.

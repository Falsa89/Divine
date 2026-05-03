# RM1.23-B — Team Synergies V2 ID-Based Plan

## Direzione approvata
Implementare una foundation V2 basata su canonical hero IDs, senza migrare i dati utente e senza rompere V1.

## Decisioni
- Usare `backend/data/synergy_definitions_v2.py` esistente.
- Installare le 10 definizioni approvate come first wave.
- V1 resta intatto.
- Team legacy vengono ignorati dal V2 senza errore.
- Team canonical possono attivare V2.
- Battle application dietro flag: `SYNERGY_V2_BATTLE_ENABLED=false` default.
- Endpoint read-only separato: `/api/synergies/team_v2`.

## Calculator behavior
1. Load active team.
2. Resolve formation slot → user_hero → hero DB record.
3. Determine canonical ID:
   - `hero.canonical_id` if valid in Character Bible;
   - fallback `hero.id` if it is in Character Bible.
4. Skip legacy/non-canonical heroes.
5. Deduplicate by canonical ID.
6. For each enabled V2 synergy:
   - required IDs present?
   - min_required satisfied?
   - optional IDs present?
   - compute stars from `user_heroes.stars`;
   - compute effects with modest star scaling.
7. Return active synergies, near-complete hints, aggregated modifiers.

## Edge case rules
- Duplicate hero copies count once.
- Legacy heroes are skipped.
- Missing user_hero or hero docs are skipped.
- Hidden/pending heroes only count if actually owned and in active team.
- No DB writes.

## Battle integration
Battle integration may be prepared but must be disabled by default:
`SYNERGY_V2_BATTLE_ENABLED=false`.

When enabled later:
- apply modifiers before battle starts;
- do not alter turn logic;
- add result telemetry for active V2 synergies.

## Safety invariants
- `/api/heroes` remains 100.
- Summon eligible remains 100.
- Starter eligible remains 20.
- `greek_borea` remains hidden.
- legacy heroes remain non-summonable.

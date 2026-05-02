# Roster Import and Legacy Policy

Status: Draft companion to RM1.20-A/B.

## Principles

- Character Bible / heroes_master is source of truth.
- Never delete legacy heroes blindly.
- Never orphan user_heroes.
- Never break active teams.
- Migrate by addition, not subtraction.
- Official heroes can be inserted hidden/pending only when endpoint visibility is safe.
- Legacy placeholders should become non-obtainable before any cleanup.
- Owned legacy can remain owned-only until migration strategy exists.

## Staging

1. Audit official vs legacy.
2. Plan soft-deactivation.
3. Plan official insert.
4. Add endpoint visibility filters.
5. Apply import with hidden/pending flags.
6. Validate QA.
7. Gradual activation by asset/contract readiness.

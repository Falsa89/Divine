# Emergent Tasking Protocol

Status: Draft.

## Rule

Do not send huge ambiguous chat prompts when a file can be referenced.

## Good Task Format

1. Read specific docs/data files.
2. State exact task name.
3. State allowed files.
4. State forbidden files.
5. Require audit before modification.
6. Require dry-run before apply.
7. Require report.
8. Require validation commands.

## Never

- Apply DB writes without explicit confirmation.
- Mix unrelated work streams.
- Touch battle/runtime when doing UI.
- Touch UI when doing DB audit.
- Interpret missing data; ask or stop.

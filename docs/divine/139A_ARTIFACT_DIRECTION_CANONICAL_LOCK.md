# 139A — PROJECT_Q Track A: Artifact Direction Canonical Lock

## Verdict
`TRACK_A_ARTIFACT_DIRECTION_CANONICAL_LOCK_READY`

## Marker JSON
`/app/data/design/artifacts/project_q_artifact_direction_canonical_lock_v1.json`

## Validator
`/app/backend/scripts/validate_project_q_artifact_direction_canonical_lock_v1.py` → **[PASS]**

## Cosa è bloccato canonicamente
- **Artifacts ARE:** *account-wide / roster-wide collectibles* che concedono un bonus globale all'account/roster con cap master a 5.0%.
- **Artifacts ARE NOT:** equipment, hero gear slot, divine weapon, unique 6-star weapon.
- **Artifacts CAN:** essere summonati (banner artifact-only), essere potenziati, essere tematicamente collegati a un eroe senza buffare solo quell'eroe.
- **Policy di introduzione:** Gli artifact devono essere introdotti insieme all'eroe / patch tematicamente correlato.
- **Esempio tematico:** Arthur potrà avere Excalibur come arma divina unica 6★; l'artifact collegato è la Sacred Cup (Holy Grail) — bonus roster-wide, **non** equipment per Arthur.

## Hard invariants bloccati nello schema
- `is_equipment == false`
- `occupies_gear_slot == false`
- `is_divine_weapon == false`
- `global_roster_account_bonus.value_pct <= 5.0`
- `obtainment_source != 'hero_summon_banner'`

## Side effects
Nessuno. Nessun runtime, nessun DB, nessun frontend toccato.

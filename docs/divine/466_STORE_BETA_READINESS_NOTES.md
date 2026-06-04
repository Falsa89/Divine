# 466 — Store Beta Readiness Notes (v76)

Pack: `MEGA_RELEASE_ACCELERATION_25_v76`

## Scope

NOTES e CHECKLIST only. Nessun upload, nessuna modifica console/store.

- applied: false
- store_upload_performed: false
- play_console_changes_performed: false
- appstore_connect_changes_performed: false
- testflight_changes_performed: false
- build_generation_performed: false

## Google Play (closed_testing)

Per certi account personali serve closed test con minimo 12 tester opt-in per 14 giorni continui prima dell'accesso a produzione.

Step (solo quando autorizzato esplicitamente):
- creare app + signing key
- creare release closed testing track
- creare tester group + opt-in link
- upload AAB con metadata + content rating
- compliance (privacy + data safety + content rating)

Azione v76: `no_action`.

## Apple TestFlight (external_testing)

Review required for external. Steps (solo quando autorizzato):
- creare app in App Store Connect
- caricare build IPA
- creare tester group internal/external
- external testing richiede Beta App Review
- export compliance + privacy + content review

Azione v76: `no_action`.

## Forbidden in v76

store_upload, play_console_changes, appstore_connect_changes, testflight_changes, build_generation, signing_key_handling, privacy_policy_publication.

`db_writes=0`, `broad_commercial_release=false`.

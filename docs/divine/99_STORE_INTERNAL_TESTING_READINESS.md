# 99 — STORE INTERNAL TESTING READINESS — v99

> Lingua: Italiano. Scope: **closed_alpha_internal_testing_NOT_commercial_release**.

## Google Play Internal Testing

| Item | Status |
| --- | --- |
| Bundle identifier | NOT READY |
| App icon | NOT READY |
| Splash | READY |
| Privacy disclosures | NOT READY |
| Data safety form | NOT READY |
| Login provider requirement | `google_signin_credentials_required` |
| Age rating target | PEGI 12 / ESRB TEEN |
| Content rating form | NOT READY |
| IAP | **DISABLED** |
| Push notifications | **DISABLED** |
| Ads | **DISABLED** |

## Apple TestFlight

| Item | Status |
| --- | --- |
| Bundle identifier | NOT READY |
| App icon | NOT READY |
| Splash | READY |
| Sign in with Apple requirement | required (se altri provider third-party presenti) |
| Sign in with Apple credentials | NOT READY |
| Privacy disclosures | NOT READY |
| Data safety form | NOT READY |
| Age rating target | 4+/12+ TBD |
| IAP | **DISABLED** |
| Push notifications | **DISABLED** |
| Ads | **DISABLED** |

## Expo / EAS Build

| Item | Status |
| --- | --- |
| `eas.json` | NOT READY |
| Profile internal_testing | NOT READY |
| Profile testflight | NOT READY |
| Keystore Android | deferred user |
| AppStore Connect API key | NOT READY |

## Safety

```
iap_active                = false
push_active               = false
ads_active                = false
commercial_release_claim  = false
fake_store_readiness      = false
```

## Checklist per l'utente

1. Decidere bundle identifier definitivo (es. `com.<azienda>.<gioco>`).
2. Preparare app icon + splash hi-res (1024x1024, 2048x2732).
3. Compilare Data Safety form di Google Play (no PII raccolta oltre auth).
4. Compilare Privacy questionnaire di App Store Connect.
5. Generare Apple Sign In Services ID + Key ID + Team ID.
6. Creare Google OAuth client Android+iOS (firma SHA-1 release).
7. Configurare `eas.json` profili internal/testflight.
8. Caricare keystore Android su EAS o gestire manualmente.
9. Caricare AppStore Connect API key per EAS submit.

## Verdict

`BLOCKER_FOR_CLOSED_ALPHA_STORE_INTERNAL_TESTING_CREDENTIALS_AND_BUNDLE_REQUIRED`

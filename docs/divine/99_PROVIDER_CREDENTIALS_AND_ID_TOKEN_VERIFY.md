# 99 — PROVIDER CREDENTIALS AND ID_TOKEN VERIFY — v99

> Lingua: Italiano.

## Stato credentials

| Provider | Status |
| --- | --- |
| Google (Android+iOS+Web) | **`CREDENTIALS_REQUIRED_FOR_STORE_BUILD`** |
| Apple Sign In | **`CREDENTIALS_REQUIRED_FOR_STORE_BUILD`** |

Nessun secret in repo. Nessun raw OAuth token log. Nessuna verifica production-ready dichiarata.

## Env vars verificate (tutte assenti)

- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_ID_ANDROID`, `GOOGLE_CLIENT_ID_IOS`, `GOOGLE_WEB_CLIENT_ID`
- `APPLE_CLIENT_ID`, `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY`

## Design contract (presente, non production-ready)

- Google JWKS endpoint: `https://www.googleapis.com/oauth2/v3/certs`
- Apple JWKS endpoint: `https://appleid.apple.com/auth/keys`
- Audience/issuer/expiry check: **design only** (rinviato a credenziali reali)
- Raw token logging: **false** (mai)

## Checklist per l'utente

1. Creare Google OAuth Client ID Android (firma SHA-1 release).
2. Creare Google OAuth Client ID iOS (bundle id reale).
3. Creare Google OAuth Web Client ID per audience check backend.
4. Creare Apple Sign In App ID + Services ID + Team ID + Key ID + Private Key.
5. Configurare le env `GOOGLE_CLIENT_ID*`, `APPLE_*` sul backend (NON committare in repo).
6. Configurare expo `app.json` plugin per `@react-native-google-signin/google-signin` e `expo-apple-authentication` con i client_id.
7. Validare flusso end-to-end su build TestFlight + Google Play Internal Testing.

## Verdict

`BLOCKER_FOR_CLOSED_ALPHA_PROVIDER_CREDENTIALS_REQUIRED`

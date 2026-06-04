# 96 — Google / Apple Login Implementation

## Pack

`MEGA_RELEASE_ACCELERATION_45_v96`

## Google

- **Frontend button**: `frontend/app/login.tsx` → "Continua con Google" (testo neutro per pre-store).
- **Backend endpoint**: `POST /api/auth/google` (`backend/routes/v96_auth.py`).
- **Library raccomandata**: `@react-native-google-signin/google-signin` (richiede expo dev build).
- **Status**: `STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD`.
- **Sandbox path**: attivo finché `GOOGLE_CLIENT_ID` env non è configurato. Subject simulato genera account con `provider_sandbox=true`.
- **Production verify path**: placeholder. Quando GOOGLE_CLIENT_ID è configurato, integrare `google.oauth2.id_token.verify_oauth2_token`.
- **Branding**: testo placeholder; per store reale richiede asset ufficiali Google Sign-In + rispetto branding guidelines.

## Apple

- **Frontend button**: visibile solo su `Platform.OS === 'ios'` (regola Apple).
- **Backend endpoint**: `POST /api/auth/apple`.
- **Library raccomandata**: `expo-apple-authentication` (iOS-only, non Android/web).
- **Status**: `STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD`.
- **App Store Guideline 4.8**: Sign in with Apple richiesto quando si offrono altri login third-party. Da implementare prima dello store review.
- **Production verify path**: placeholder; richiede `APPLE_CLIENT_ID` + verifica JWT identity_token + JWKS Apple.

## Guest

- **Backend endpoint**: `POST /api/auth/guest`.
- **Gated**: env `V96_AUTH_GUEST_ENABLED=true` (default).
- **Account creato con 0 reward**: nessun exploit possibile.
- **Raccomandazione**: disabilitare in build store.

## Account linking

- Idempotent: stessa coppia `(provider, subject_hash)` → stesso account.
- `provider_user_id` memorizzato SOLO come `sha256(provider:subject)`, mai raw.

## Refresh token

- `POST /api/auth/refresh` esiste come CONTRACT.
- Runtime `DEFERRED`: access token 7 giorni sufficiente per alpha/closed alpha.
- Rotation completa implementata in v97+.

## Cosa serve per Store Build

1. `GOOGLE_CLIENT_ID` (Google Cloud Console OAuth 2.0 Client ID).
2. `APPLE_CLIENT_ID` (Apple Developer → Services ID + Sign in with Apple capability).
3. Apple Service: dominio + return URL configurati.
4. Branding ufficiale Google/Apple sui pulsanti.
5. Privacy Policy URL pubblico.
6. Native libraries installate: `@react-native-google-signin/google-signin`, `expo-apple-authentication`.
7. Expo dev build (non sufficient Expo Go).

# 97 — Provider Token Verification Gate

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Stato attuale

Google e Apple sono in **modalità sandbox**: nessuna verifica reale dei provider id_token.

Marker: `STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD` (closed alpha blocker).

## Google

### Env required
- `GOOGLE_CLIENT_ID`

### Library required
- `google-auth>=2.0.0` (per `google.oauth2.id_token.verify_oauth2_token`)

### Steps per attivazione produzione
1. Configurare `GOOGLE_CLIENT_ID` come env var.
2. `pip install google-auth`.
3. In `routes/v96_auth.py` integrare:
   ```python
   from google.oauth2 import id_token
   from google.auth.transport import requests as g_requests
   idinfo = id_token.verify_oauth2_token(req.id_token, g_requests.Request(), GOOGLE_CLIENT_ID)
   subject = idinfo['sub']
   ```
4. Rimuovere fallback sandbox quando credentials presenti.

## Apple

### Env required
- `APPLE_CLIENT_ID` (Services ID, es. `com.divinegame.signin`)
- `APPLE_TEAM_ID`
- `APPLE_KEY_ID`

### Library required
- `PyJWT` (già presente) + Apple JWKS endpoint `https://appleid.apple.com/auth/keys`

### Client constraint

**iOS-only** (policy ufficiale Apple).

### Steps per attivazione produzione
1. Apple Developer → Services ID + Sign in with Apple capability.
2. Configurare `APPLE_CLIENT_ID` env var.
3. Integrare verify JWT con JWKS Apple rotation.
4. Test su iOS device con TestFlight build.

## App Store Guideline 4.8

**Required** quando si offrono altri third-party logins. Sign in with Apple deve essere presente.

## Safety

- No fake production readiness (sandbox label sempre visibile).
- No raw id_token logged.
- No provider secret in repo.

## Verdict

`PROVIDER_TOKEN_VERIFICATION_GATE_DESIGN_READY_CREDENTIALS_REQUIRED`

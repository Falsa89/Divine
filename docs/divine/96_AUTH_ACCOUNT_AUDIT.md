# 96 — Auth/Account Audit

## Pack

`MEGA_RELEASE_ACCELERATION_45_v96`

## Pre-esistente

- `PyJWT==2.12.1`, `bcrypt==5.0.0` già in `backend/requirements.txt`.
- `POST /api/register`, `POST /api/login` legacy (email/password) in `backend/server.py`.
- `get_current_user` dependency funzionante (JWT HS256, secret env `JWT_SECRET`).
- MongoDB `users` collection con campi base.
- `frontend/context/AuthContext.tsx` legacy (email/password, AsyncStorage NON sicuro).

## v96 nuove implementazioni

### Backend
- `backend/routes/v96_auth.py`: router con `POST /api/auth/google`, `/apple`, `/guest`, `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/auth/refresh` (CONTRACT, DEFERRED), `GET /api/auth/provider-status`.
- `backend/routes/v96_team_formation.py`: `GET /api/team/get-formation` (chiude blocker v95).
- Provider verify path è placeholder; in modalità sandbox subject è simulato. Marker `CREDENTIALS_REQUIRED_FOR_STORE_BUILD` quando `GOOGLE_CLIENT_ID` / `APPLE_CLIENT_ID` mancano.

### Frontend
- `frontend/src/auth/AuthContext.tsx`: AuthProvider v96, `expo-secure-store` per token, session restore, login/logout, refreshMe.
- `frontend/app/login.tsx`: schermata login Google/Apple/Guest con status banner.
- `frontend/app/_layout.tsx`: integrato `<V96AuthProvider>`.

## Classificazione

| Categoria | Elementi |
|-----------|----------|
| Implemented | backend auth router, team-formation, frontend auth context, login screen, secure storage, sandbox guest, alias-safe model, JWT issuance, session restore, logout |
| Missing | google id_token verify runtime, apple identity_token verify runtime, native google-signin client lib, native apple-authentication client lib, refresh token rotation |
| Blocked_by_env_provider_credentials | google production flow, apple production flow |
| Safe_fallback | sandbox guest, sandbox google, sandbox apple |

## Safety

- `raw_oauth_token_logged = false`
- `provider_secret_in_repo = false`
- `plain_token_storage = false` (expo-secure-store)
- `alias_only_in_logs = true`
- `real_pii_in_logs = false`

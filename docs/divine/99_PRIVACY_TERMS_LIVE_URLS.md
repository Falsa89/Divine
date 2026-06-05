# 99 — PRIVACY / TERMS / ACCOUNT DELETION LIVE URLS — v99

> Lingua: Italiano.

## Stato URLs

| URL | Valore | Status |
| --- | --- | --- |
| Privacy Policy | `null` | **MISSING** |
| Terms of Service | `null` | **MISSING** |
| Account Deletion | `null` | **MISSING** |
| Support Contact | `null` | **MISSING** |
| Support Email | `null` | **MISSING** |

## Env vars verificate (tutte assenti)

- `PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL`, `ACCOUNT_DELETION_URL`, `SUPPORT_CONTACT_URL`, `SUPPORT_EMAIL`

## Frontend / Backend

- Frontend login/settings links: `PLACEHOLDER_READY_AWAITS_LIVE_URLS`
- Backend `/api/auth/provider-status`: safe exposure, **non espone secret**.

## Checklist per l'utente

1. Hostare Privacy Policy su dominio legale (es. `https://<dominio>/privacy`).
2. Hostare Terms of Service su dominio legale (es. `https://<dominio>/terms`).
3. Hostare istruzioni Account Deletion (GDPR Art.17) su dominio legale.
4. Configurare `PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL`, `ACCOUNT_DELETION_URL` nelle env del backend.
5. Configurare expo `app.json` con i link in settings / login.

## Verdict

`BLOCKER_FOR_CLOSED_ALPHA_EXTERNAL_URLS_REQUIRED`

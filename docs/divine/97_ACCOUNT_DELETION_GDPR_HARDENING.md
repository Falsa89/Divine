# 97 — Account Deletion / GDPR Hardening

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Endpoints implementati

### POST /api/auth/delete-account-request

- Soft-delete con grace period 14 giorni.
- Marca `pending_deletion=true`, `scheduled_deletion_at=now+14d`.
- Revoca tutti i refresh token (logout-all implicito).
- Reversibile entro la grace period.
- Hard delete runtime: **DEFERRED A V98** (COMMERCIAL_NEEDS_REVIEW).

### POST /api/auth/logout-all

- Revoca tutti i refresh token attivi dell'utente.
- Stateless logout client.

### GET /api/auth/privacy-status

- Restituisce stato privacy: data_minimization, hashed provider id, no PII in logs, pending_deletion status, retention policy.

## Retention

| Item | Days |
|------|------|
| Active account | 365 |
| Inactive account | 730 |
| Deletion request grace | 14 |
| Log retention | 90 |

## GDPR alignment

- Right to be Forgotten: **SOFT_DELETE_ALPHA, hard delete DEFERRED**
- Data portability: CONTRACT_DEFERRED_TO_V98
- Consent mechanism: DESIGN_REQUIRED_FOR_CLOSED_ALPHA

## PII minimization

- No raw provider user ID stored (sha256 hash)
- No raw OAuth token logged
- Email optional
- No real name / phone / address collected

## Verdict

`ACCOUNT_DELETION_GDPR_HARDENING_INTERNAL_ALPHA_READY_HARD_DELETE_DEFERRED`

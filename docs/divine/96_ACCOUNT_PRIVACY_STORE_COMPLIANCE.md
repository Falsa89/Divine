# 96 — Account Privacy / Store Compliance

## Pack

`MEGA_RELEASE_ACCELERATION_45_v96`

## Privacy Policy (DRAFT — required for store build)

Dati raccolti:
- `provider_subject_hash` (sha256, non reversibile)
- `email` (opzionale, per alias)
- `alias` (qa_alias / username)
- `created_at`, `last_login`
- `team_formation` (progresso gioco)

Dati NON raccolti:
- real name PII raw
- physical address
- phone number
- raw OAuth token

## Terms of Service

Status: `DRAFT_REQUIRED_FOR_STORE_BUILD`.

## Account deletion

- Endpoint pianificato: `POST /api/auth/account/delete`.
- Status: `CONTRACT_ONLY_DEFERRED_TO_POST_V96`.
- Obbligatorio per GDPR (Right to be Forgotten) e CCPA.

## Account linking / unlinking

- Linking: implementato (idempotent via subject_hash).
- Unlinking: CONTRACT ONLY.
- Multi-provider per account: DEFERRED a v97+.

## Branding

- Google: branding guidelines da rispettare (asset ufficiali per store).
- Apple: Sign in with Apple button HIG-compliant required.

## Logging policy

- **NO PII** nei log.
- **NO raw OAuth token** nei log.
- Alias-only.

## GDPR / CCPA checklist

- Data collected disclosed: ok (in privacy policy)
- Right to be forgotten: CONTRACT ONLY
- Data export: CONTRACT ONLY
- Consent mechanism: required
- Do not sell data: applicabile

## App Store / Play Console checklist

- Apple guideline 4.8 Sign in with Apple: REQUIRED quando si offrono other third-party logins
- Privacy Policy URL: REQUIRED
- App Privacy questionnaire: REQUIRED
- Data collection disclosure: REQUIRED
- Google Play Data Safety section: REQUIRED
- Sensitive permissions disclosure: REQUIRED

## QA announcements

- `real_pii_in_qa_broadcasts = false`
- `alias_only = true`

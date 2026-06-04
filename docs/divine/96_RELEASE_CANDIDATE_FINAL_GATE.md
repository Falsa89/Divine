# 96 — Release Candidate Final Gate

## Pack

`MEGA_RELEASE_ACCELERATION_45_v96`

## Gate matrix per tier

| Categoria | Internal Alpha | Closed Alpha | Commercial Release |
|-----------|----------------|--------------|---------------------|
| auth_account | READY_WITH_SANDBOX_PROVIDERS | CONDITIONAL_REQUIRES_REAL_GOOGLE_APPLE_CREDENTIALS | BLOCKED_REQUIRES_REAL_CREDENTIALS_AND_STORE_REVIEW |
| engine | READY | READY | READY |
| formation | READY | READY | READY |
| modes | READY | CONDITIONAL | CONDITIONAL |
| rewards | READY_CANARY_SANDBOX | CONDITIONAL | BLOCKED |
| live_guild | READY_GATED | CONDITIONAL | CONDITIONAL |
| announcements | READY_SANDBOX | CONDITIONAL | BLOCKED |
| mobile_qa | CONDITIONAL_REQUIRES_PHYSICAL_DEVICE_RUN | BLOCKED_UNTIL_QA_RUN | BLOCKED |
| performance | READY_LOW_IMPACT_SMOKE | CONDITIONAL_REQUIRES_LOAD_LOCUST | BLOCKED |
| optional_fail_baseline | READY_RECONCILED | CONDITIONAL_NEEDS_CLEANUP | BLOCKED_REQUIRES_<=30 |
| store_readiness | NOT_REQUIRED | BLOCKED | BLOCKED |
| art_audio_readiness | CONDITIONAL_PLACEHOLDERS | BLOCKED | BLOCKED |
| compliance_privacy | DESIGN_READY | BLOCKED | BLOCKED |
| known_issues | ACCEPTABLE_CAVEAT_DOCUMENTED | CONDITIONAL | CONDITIONAL |

## Overall verdict

- **READY_FOR_INTERNAL_ALPHA**: true
- **CONDITIONAL_FOR_CLOSED_ALPHA**: true
- **BLOCKED_FOR_RELEASE_CANDIDATE**: false
- **BLOCKED_FOR_COMMERCIAL_RELEASE**: true

## Blockers

### Per Internal Alpha
1. Physical device QA run (Android/iOS).

### Per Closed Alpha
1. Real Google/Apple credentials.
2. Physical device QA run.
3. Load/locust performance test.
4. Live privacy/terms URLs.
5. Cleanup ~110 stale_proof + deprecated OPTIONAL FAIL.

### Per Commercial Release
1. Tutti i blockers Closed Alpha.
2. Store readiness (App Store / Play Console).
3. Art/audio final assets.
4. Monetization (IAP) live activation.
5. final_numbers balance lock (fuori scope v96).

# Acceptance Checklist — Pack 97

- [ ] Approval string present.
- [ ] Daily login SOT created.
- [ ] daily_login_claim added to registry only.
- [ ] Reward payload small, server-scoped, non-premium.
- [ ] Daily endpoint or rewards/claim integration safe.
- [ ] Frontend consumer passes server_id and idempotency_token.
- [ ] Kill switch default safe and restored after smoke.
- [ ] First claim succeeds.
- [ ] Same-day replay/different-token cannot double grant.
- [ ] Cross-server no leak.
- [ ] Premium/hard grants blocked.
- [ ] Other real claim sources remain deferred.
- [ ] Runtime smoke E2E green.
- [ ] Reward live general false.
- [ ] Release readiness not claimed.
- [ ] Final suite REQUIRED=0 MISS=0.
- [ ] fake_PASS=false.
- [ ] validator_weakening=false.

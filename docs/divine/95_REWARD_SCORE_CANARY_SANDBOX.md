# 95 — Reward / Score Canary Sandbox

## Pack

`MEGA_RELEASE_ACCELERATION_44_v95`

## Scope

Design + risultato sandbox per UNA singola modalità test (`qa_canary_pve_sandbox_mode`).

## Regole

- Allowlist alias-only: `qa_alias_canary_001`.
- Dry-run by default.
- Canary apply solo in sandbox; nessun account reale toccato.
- Storage canary: solo in-memory.
- Idempotency: dedupe finestra 60s + rate limit 3/min per alias.
- Rollback drill verificato: flip canary OFF + purge in-memory state.

## Forbidden

- broad live reward grant;
- reward per utenti non-canary;
- currency grant reale;
- MMR live;
- guild score live;
- event currency live;
- boss fragment grant;
- inventory grant;
- cosmetic unlock;
- monetization;
- production broadcast;
- push notification live;
- random opponents;
- Character Bible mutation;
- hero roster mutation;
- final asset import;
- final_numbers balance lock.

## Verdict

`REWARD_SCORE_CANARY_SANDBOX_DESIGNED_AND_SCOPED_NO_LIVE_APPLY`

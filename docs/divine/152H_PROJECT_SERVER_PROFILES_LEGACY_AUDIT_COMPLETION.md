# 152H — Track H: Project Server Profiles Legacy Audit Completion

**Global Verdict:** `PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT_READY`
**Track H:** `TRACK_H_PROJECT_SERVER_PROFILES_LEGACY_AUDIT_COMPLETION_READY`

## Suite + invariants
| metric | pre | post |
|---|---|---|
| Suite serial | 591/0 | **599 PASS / 0 FAIL** |
| Suite parallel | 591/0 | **599 PASS / 0 FAIL** |
| battle_engine.py MD5 | `151ca35a…` | invariato ✅ |
| .env MD5 | `ff60bbb7…` | invariato ✅ |
| servers.tsx MD5 | `26f5c796…` | invariato ✅ |
| server_profiles.py MD5 | `7c12a8d1…` | invariato ✅ |
| economy.py MD5 | `b3afb526…` | invariato ✅ |
| DB writes | — | 0 ✅ |
| Backend changes | — | 0 ✅ |
| Frontend changes | — | 0 ✅ |
| Flag flips | — | 0 ✅ |
| Server changes | — | 0 ✅ |

## Readiness
- Server profile wiring readiness: **45% → 62%** (+17pp)
- Frontend integration readiness: 81% → 82%
- Suite hygiene: **100%**

## Recommended immediate action
Lock `/servers` UI come `SafeFeatureCard` (locked-preview) **PRIMA** di qualsiasi seed/migration di `server_profiles` per prevenire scritture concorrenti su `users.server`.

## Recommended next pack
- **Primary:** `PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW_PACK`
- Secondary: `PROJECT_SERVER_PROFILES_DUAL_READ_PREVIEW_PACK`
- Tertiary: `PROJECT_SERVER_PROFILES_SEED_AND_ROLLBACK_PLAN_PACK`

## Progress
67.4% → **67.4%** (audit-only)

## Time remaining (excl. graphics/audio/art)
- Aggressive: 4-6 weeks · Realistic: 8-12 weeks · Prudent: 16-20 weeks

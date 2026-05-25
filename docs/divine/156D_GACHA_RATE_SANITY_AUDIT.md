# 156D — Gacha Rate Sanity Audit (Track D)

Verdetto: `TRACK_D_GACHA_RATE_SANITY_AND_BANNER_GUARD_AUDIT_READY`

## Rate attuali (frontend == backend)
- standard: 5★ 6% / 6★ 2%
- elemental: 5★ 10% / 6★ 4%
- premium: **5★ 20% / 6★ 10%** (30% combinato — dev/test-like)
- selective: 5★ 13% / 6★ 5%
- targeted: **5★ 20% / 6★ 10%**
- artifact: 5★ 10% / 6★ 4%
- constellation: 5★ 17% / 6★ 8%

## Plausibilità x10 (4 mitici + 3 leggendari)
Ipotizzando banner premium/targeted (p6★=0.10, p5★=0.20):
- P(≥4 di 6★ in 10) ≈ 0.0128
- P(≥3 di 5★ in 10) ≈ 0.3222
- P(congiunta) ≈ 0.0041

L'evento è raro ma non impossibile sul banner premium. Su standard sarebbe ~0.00001 (praticamente impossibile).

## Conclusione
Le rate premium/targeted appaiono dev/test e non sono state firmate da economy. **Raccomandato lock pubblico del gacha** finché non c'è signoff economy.

Prossimo pack: `PROJECT_GACHA_RATE_SANITY_FIX_OR_LOCK_PACK`.

## Vincoli rispettati
- Nessuna modifica a rate / pity / pool / DB.

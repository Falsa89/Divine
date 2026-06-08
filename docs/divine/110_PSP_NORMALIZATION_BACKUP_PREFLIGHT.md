# 110 — PSP Normalization Backup Preflight — Manifest checksum

**Mode:** `MANIFEST_CHECKSUM_NO_SECRETS`
**Pack:** Pack 83 (PREFLIGHT, NO writes)

## Strategia di backup

L'approccio scelto e' **manifest checksum in-place** dei 1690 PSP correnti.
NESSUN export di dati sensibili. NESSUN secret in plaintext.
NESSUN copy fisico in collezione duplicata (per evitare scritture DB).

Il rollback usa il campo marker `_slc_psp_user_id_legacy_objectid_backup`
che sara' scritto dal future execute con il valore ObjectId-string
legacy PRIMA della normalizzazione. Cioe' il backup vive nei PSP stessi
e viene rimosso solo dal rollback script.

## Manifest

- File JSON: `data/design/v110_psp_normalization_preflight/v110_psp_normalization_backup_preflight_v1.json`
- Manifest hash sha256: `e12b15aa0e45c3a388310b74b8d24473affde0697282d7f30d8781554986b4a2`
- Entries: 1690 PSP
- Ogni entry: `psp_id`, `server_id`, `legacy_user_id_objectid_string`, `pre_normalization_checksum_sha256` (su `user_id`, `server_id`, `profile_id`, `player_level`, `player_exp`)
- Niente email, password, token (PSP non li contiene comunque; doppia verifica).

## Sufficiente per rollback?

**Si.** Il rollback non richiede di reinserire campi al di fuori di `user_id`
perche' il normalize tocca SOLO `user_id`. La presenza del marker
`_slc_psp_user_id_legacy_objectid_backup` (che il future execute scrive)
basta a ripristinare lo stato precedente.

La checksum del manifest fornisce verifica di integrita' anti-tampering
sui dati pre-normalization.

## Bloccanti se manifesto insufficiente

Se in futuro un audit dimostrasse insufficienza, il future execute script
rifiutera' tramite gate `--backup-manifest-hash-pin` mismatch.

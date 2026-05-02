# Roster Import & Legacy Policy

> **Stato:** RM1.20-A — framework di audit + piano di soft-deactivation. **Nessuna scrittura DB applicata.**
> **Source of truth:** `backend/data/character_bible.py`.

---

## 1. Principi non negoziabili

1. **La Character Bible è l'unica fonte di verità ufficiale del roster.**
   Il roster ufficiale al lancio è composto da **100 eroi `launch_base` + Borea (`greek_borea`) come `launch_extra_premium`**, fuori dal conteggio dei 100.
2. **I placeholder legacy non vanno mai cancellati alla cieca.**
   Niente `DELETE` su `heroes`, `user_heroes`, `teams`, `users`. Mai. In nessuna circostanza, neppure in cleanup.
3. **Niente orfanizzazione di `user_heroes`.**
   Ogni `user_hero` esistente deve continuare a riferirsi a un documento `heroes` valido, anche se `is_legacy_placeholder=True`.
4. **Niente rottura di `active_team`.**
   Se una formazione attiva contiene un legacy, l'eroe deve restare giocabile per quel giocatore finché non viene definita una strategia di team-migration per-utente.
5. **Tutte le decisioni di visibilità sono *soft* (flag `show_in_*`)**, non distruttive.

---

## 2. Glossario operativo

| Termine | Significato |
| --- | --- |
| **Eroe ufficiale** | Slug presente in `CHARACTER_BIBLE_BY_ID`. Marcato con `is_official=True`. |
| **Legacy placeholder** | Documento `heroes` con `id` non presente nella Character Bible. Marcato con `is_legacy_placeholder=True` e `legacy_status="deprecated_placeholder"`. |
| **Soft-deactivation** | Set di flag (`obtainable=False`, `show_in_catalog=False`, `show_in_summon=False`, `show_in_hero_collection="owned_only"`, `show_in_battle_picker="owned_only"`, `do_not_delete=True`). **Nessuna cancellazione.** |
| **Hard-delete** | **VIETATO** in qualsiasi fase. |
| **Team migration** | Procedura per-utente (futura) che propone un eroe ufficiale equivalente al legacy in slot di `active_team`. Niente sostituzioni silenziose. |

---

## 3. Schema dei flag DB

### 3.1 Eroi ufficiali (canonicalizzazione)
```json
{
  "is_official": true,
  "is_legacy_placeholder": false,
  "legacy_status": null,
  "release_group": "launch_base" | "launch_extra_premium",
  "native_rarity": 1..6,
  "max_stars": 4|6|8|10|12|15,
  "canonical_element": "water|fire|earth|wind|lightning|light|dark",
  "canonical_role": "tank|dps_melee|dps_ranged|mage_aoe|assassin_burst|support_buffer|healer|control_debuff|hybrid_special",
  "canonical_faction": "greek|norse|egyptian|japanese_yokai|celtic|angelic|demonic|creature_beast|cursed|arcane|mesopotamian|primordial|tides",
  "obtainable": true,
  "show_in_catalog": true,
  "show_in_summon": true,
  "show_in_hero_collection": true,
  "show_in_battle_picker": true,
  "do_not_delete": true
}
```

### 3.2 Legacy placeholder (soft-deactivation)
```json
{
  "is_official": false,
  "is_legacy_placeholder": true,
  "legacy_status": "deprecated_placeholder",
  "obtainable": false,
  "show_in_catalog": false,
  "show_in_summon": false,
  "show_in_hero_collection": "owned_only",
  "show_in_battle_picker": "owned_only",
  "do_not_delete": true,
  "deactivation_reason": "legacy_placeholder_pre_official_roster",
  "deactivated_at_planned": "<ISO-8601 UTC>"
}
```

I valori `"owned_only"` sono interpretati dagli helper in `backend/utils/hero_visibility.py` (puri, no-op finché non cablati).

---

## 4. Procedura di import ufficiale (sequenza approvata)

### Fase 0 — Preparazione (RM1.20-A, **questa task**)
- ✅ Audit read-only: `python backend/scripts/audit_roster_against_character_bible.py`.
- ✅ Piano dry-run: `python backend/scripts/plan_legacy_soft_deactivation.py`.
- ✅ Documento policy (questo file).
- ✅ Helper `hero_visibility.py` import-safe, NON cablato in endpoint.
- ❌ **`--apply` NON eseguito.** Nessuna scrittura DB.

### Fase 1 — Soft-deactivation legacy (task futura)
1. Re-run audit per snapshot pre-migration.
2. Run `plan_legacy_soft_deactivation.py --apply` (richiede `ROSTER_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_WRITE_DB`).
3. Update di `db.heroes` con i flag della §3.2 sui legacy. **Nessun DELETE.**
4. Update di `db.heroes` con i flag della §3.1 sugli ufficiali già presenti.
5. Backup MongoDB pre-write in `backend/backups/` (escluso da git).

### Fase 2 — Import ufficiali mancanti (task futura)
1. INSERT in `db.heroes` per gli `id` della Character Bible non presenti.
2. Asset binding: variants, rig, frame metadata via `HERO_CONTRACTS` frontend.
3. Validazione `Combat QA Lab` per ogni nuovo eroe (idle/skill/death frames).
4. Smoke test endpoint `/api/heroes`, `/api/user/heroes`, `/api/team`.

### Fase 3 — Filtri runtime (task futura)
1. `/api/heroes` (catalog) → filtra per `should_show_in_catalog`.
2. Gacha/summon → filtra per `should_show_in_summon` (anche `obtainable`).
3. Hero collection → filtra per `should_show_in_collection(owned=True)` per i legacy posseduti.
4. Battle picker → `should_show_in_battle_picker(owned=True)` solo dopo team-migration per-utente.

### Fase 4 — Team migration (task futura, opzionale)
- Pop-up in-app per ogni utente con legacy in active team: propone uno o più eroi ufficiali equivalenti come sostituzione (solo su consenso).
- Niente swap automatico silenzioso.

---

## 5. Cosa **NON** fa RM1.20-A

- ❌ Non importa nuovi eroi.
- ❌ Non importa o tocca immagini/sprite.
- ❌ Non cancella eroi.
- ❌ Non cancella `user_heroes`.
- ❌ Non cancella `teams`.
- ❌ Non modifica banner gacha né rate.
- ❌ Non modifica hero collection / battle picker / catalog.
- ❌ Non modifica gli endpoint `/api/heroes`, `/api/user/heroes`, `/api/team`.
- ❌ Non resetta o modifica account esistenti.
- ❌ Non esegue `--apply`.

---

## 6. Garanzie sui report

I report JSON vengono scritti in `backend/reports/` (escluso da git):

- `roster_audit_<timestamp>.json` — output di `audit_roster_against_character_bible.py`.
- `legacy_soft_deactivation_plan_<timestamp>.json` — output di `plan_legacy_soft_deactivation.py`.

Ogni report contiene:
- Sezione `safety`: tutti i flag a `False` (nessuna scrittura).
- Sezione `summary`: contatori aggregati.
- Plan dettagliato per ogni eroe.
- Distribuzioni per fazione/elemento/ruolo/rarità.

---

## 7. Checklist per ogni nuovo eroe ufficiale (futuro)

Quando si aggiunge un nuovo eroe ufficiale al roster, l'eroe deve passare **tutti** questi gate prima di considerarsi pronto al lancio:

1. ✅ Entry in `backend/data/character_bible.py` con `id`, `native_rarity`, `element`, `role`, `faction`, `release_group`.
2. ✅ Entry in `HERO_CONTRACTS` (`frontend/components/ui/hopliteAssets.ts`) con UI framing per portrait/grid/header/full.
3. ✅ Battle contract: idle, skill, hit, death sprite (rig completa).
4. ✅ Asset contract: variants registrati e accessibili tramite resolver.
5. ✅ Validazione manuale nel **Combat QA Lab** (`/dev-combat-qa-lab`) su tutte le animazioni.
6. ✅ Rispetto della naming convention canonical (vedere § §2 e §3).
7. ✅ Verifica `validate_character_bible.py` PASS.
8. ✅ Run dell'audit script: nuovo eroe deve risultare in `official_present`.

---

## 8. Comandi rapidi

```bash
# Audit read-only (sempre safe)
cd /app && python backend/scripts/audit_roster_against_character_bible.py

# Piano dry-run (sempre safe, NON tocca il DB)
cd /app && python backend/scripts/plan_legacy_soft_deactivation.py

# Validazione strutturale Character Bible
cd /app && python backend/scripts/validate_character_bible.py
```

> Il flag `--apply` di `plan_legacy_soft_deactivation.py` **non va eseguito in RM1.20-A**. È predisposto per la task successiva e richiede inoltre la variabile d'ambiente `ROSTER_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_WRITE_DB`.

---

## 9. Riepilogo della filosofia

> *Nessun giocatore deve mai vedere il proprio team rotto, il proprio inventario decimato o la propria collezione resettata a causa di una migrazione di roster.*
> Migrate per **somma**, non per sottrazione. Add, hide-from-new, never delete.

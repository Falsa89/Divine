#!/usr/bin/env python3
"""
Pack 124 — QA Team Seed: assegna 10 eroi canonici launch_base ad un account
test specifico per consentire il device QA del team editor / formation /
team save.

GUARDRAIL ASSOLUTI (fail-closed):

1. SOLO esecuzione manuale da dev: NON e' un endpoint HTTP, NON e'
   raggiungibile dal client. Va lanciato via shell dentro il container.
2. Gate: env var `QA_SEED_ENABLED=true` DEVE essere settata, altrimenti
   il programma esce con codice 2.
3. Allowlist: l'account deve essere passato via `--allow-account <user_id>`;
   non c'e' default. Se omesso → exit 2.
4. Idempotente: per ogni hero_id viene fatto un upsert in `user_heroes`
   solo se l'account NON ha gia' quell'eroe (livello base 1, no upgrade).
5. NO premium currency, NO gacha pull, NO paid odds, NO reward claim,
   NO shop transaction, NO VIP, NO BP, NO IAP.
6. Hero pool: ESCLUSIVAMENTE 10 eroi canonici launch_base 3*/4* da
   `heroes_master.json`. Vietati Borea, 6*, hidden, pending/placeholder.
7. Output: report JSON dettagliato in
   `backend/scripts/reports/pack_124_qa_team_seed_<timestamp>.json`.
8. Rollback: script complementare `qa_team_seed_clear.py` (vedi sotto)
   rimuove SOLO gli eroi seed (matching su un flag `_qa_seed: true`).

QUESTO SCRIPT NON E' EREDITABILE IN PRODUZIONE. Il database in produzione
non avra' `QA_SEED_ENABLED=true`. Il programma e' read-write solo verso
la collezione `user_heroes` (no economy/gacha/shop/VIP/BP/IAP).

Usage:
  QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_canonical_heroes.py \\
      --allow-account <user_id> [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# 10 eroi canonici per QA team seed.
# Tutti presenti in `heroes_master.json`, launch_base, rarity 3* o 4*.
# Composizione bilanciata per ruolo ed elemento, no Borea, no 6*, no hidden.
QA_TEAM_SEED_HERO_IDS: list[str] = [
    # 6 eroi dal preview team (consistenza con frontend previewBattleTeam.ts).
    "greek_hoplite",                  # Tank      / 3* / Terra
    "norse_berserker",                # DPS Melee / 3* / Fuoco
    "celtic_archer",                  # DPS Range / 3* / Vento
    "arcane_lightning_enchantress",   # Mage AoE  / 3* / Fulmine
    "greek_sanctuary_muse",           # Support   / 3* / Luce
    "angelic_priestess",              # Healer    / 3* / Luce
    # +4 eroi addizionali per consentire team rotation / formation editing.
    "creature_coral_guardian",        # Tank      / 3* / Acqua
    "norse_thunder_spear",            # DPS Melee / 3* / Fulmine
    "celtic_moor_druidess",           # Support   / 3* / Terra
    "egyptian_nile_healer",           # Healer    / 3* / Acqua
]

FORBIDDEN_KEYWORDS = ["borea", "hidden", "placeholder", "test_only", "internal"]


def _fail(msg: str, code: int = 2) -> None:
    print(f"FAIL  {msg}")
    sys.exit(code)


def _load_roster() -> dict:
    p = REPO_ROOT / "data" / "design" / "heroes_master.json"
    if not p.exists():
        _fail(f"missing roster file: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_hero_pool(by_id: dict) -> list[str]:
    """Restituisce la lista di errori (vuota se OK)."""
    errors: list[str] = []
    for hid in QA_TEAM_SEED_HERO_IDS:
        if hid not in by_id:
            errors.append(f"hero_id `{hid}` NOT in heroes_master.json")
            continue
        h = by_id[hid]
        lo = hid.lower()
        for kw in FORBIDDEN_KEYWORDS:
            if kw in lo:
                errors.append(f"hero_id `{hid}` contains forbidden keyword `{kw}`")
        if h.get("rarity") == 6:
            errors.append(f"hero_id `{hid}` is 6* (premium) — vietato")
        if h.get("release_group") not in ("launch_base", None):
            errors.append(
                f"hero_id `{hid}` release_group=`{h.get('release_group')}` non launch_base"
            )
        name_lo = str(h.get("name", "")).lower()
        if "borea" in name_lo:
            errors.append(f"hero_id `{hid}` (name=`{h.get('name')}`) — Borea VIETATO")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack 124 QA team seed (dev manual).")
    parser.add_argument("--allow-account", dest="account", default=None,
                        help="ID account allowlisted (obbligatorio)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Non scrive su DB, solo valida e logga.")
    parser.add_argument("--validate-only", action="store_true",
                        help="Solo validazione struttura: nessuna connessione DB.")
    args = parser.parse_args()

    # Gate 1: env flag
    if os.environ.get("QA_SEED_ENABLED", "").lower() != "true":
        _fail("QA_SEED_ENABLED env var must be 'true' (gate fail-closed)")

    # Gate 2: allowlist account (a meno di --validate-only)
    if not args.validate_only and not args.account:
        _fail("--allow-account <user_id> obbligatorio (allowlist fail-closed)")

    # Hero pool validation
    roster_data = _load_roster()
    heroes = roster_data.get("heroes", [])
    by_id = {h["id"]: h for h in heroes if isinstance(h, dict) and h.get("id")}
    pool_errors = _validate_hero_pool(by_id)
    if pool_errors:
        for e in pool_errors:
            print(f"  ERR  {e}")
        _fail("hero pool validation failed")

    print(f"OK    hero pool ({len(QA_TEAM_SEED_HERO_IDS)} canonici) validato")

    if args.validate_only:
        print("OK    --validate-only: skip DB ops.")
        return 0

    # DB ops (solo se non validate-only)
    try:
        from pymongo import MongoClient  # type: ignore
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        _fail("pymongo / python-dotenv non installati")

    load_dotenv(REPO_ROOT / "backend" / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    if not mongo_url:
        _fail("MONGO_URL non trovato in backend/.env")

    client = MongoClient(mongo_url)  # type: ignore[arg-type]
    db = client.get_default_database()
    if db is None:
        # Fallback al primo db disponibile
        names = client.list_database_names()
        db_name = next((n for n in names if n not in ("admin", "local", "config")), None)
        if not db_name:
            _fail("nessun database disponibile")
        db = client[db_name]  # type: ignore[index]

    user_heroes_col = db["user_heroes"]

    granted: list[dict] = []
    skipped: list[dict] = []
    ts = int(time.time())

    for hid in QA_TEAM_SEED_HERO_IDS:
        hero_def = by_id[hid]
        existing = user_heroes_col.find_one({"user_id": args.account, "hero_id": hid})
        if existing:
            skipped.append({"hero_id": hid, "reason": "already_owned"})
            continue
        doc = {
            "_id": f"qa_seed_{args.account}_{hid}_{uuid.uuid4().hex[:8]}",
            "user_id": args.account,
            "hero_id": hid,
            "name": hero_def.get("name"),
            "rarity": hero_def.get("rarity"),
            "element": hero_def.get("element"),
            "role": hero_def.get("role"),
            "level": 1,
            "stars": hero_def.get("rarity", 3),
            "power": 0,
            "exp": 0,
            "_qa_seed": True,
            "_qa_seed_ts": ts,
            "_qa_seed_pack": "pack_124",
        }
        if args.dry_run:
            granted.append({"hero_id": hid, "dry_run": True})
        else:
            user_heroes_col.insert_one(doc)
            granted.append({"hero_id": hid, "doc_id": doc["_id"]})

    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "pack": "PRE_QA_PACK_124_QA_TEAM_SEED",
        "validator": "qa_team_seed_canonical_heroes",
        "status": "PASS",
        "account": args.account,
        "dry_run": args.dry_run,
        "ts": ts,
        "hero_pool_size": len(QA_TEAM_SEED_HERO_IDS),
        "granted": granted,
        "skipped": skipped,
        "guardrails": {
            "qa_seed_enabled": True,
            "no_premium_currency": True,
            "no_gacha": True,
            "no_paid_odds": True,
            "no_reward_claim": True,
            "no_shop": True,
            "no_vip": True,
            "no_battlepass": True,
            "no_iap": True,
            "idempotent": True,
            "manual_dev_only": True,
        },
    }
    out_path = out_dir / f"pack_124_qa_team_seed_{ts}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK    seed completato: granted={len(granted)} skipped={len(skipped)}")
    print(f"OK    report: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

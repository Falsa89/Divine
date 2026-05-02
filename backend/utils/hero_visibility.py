"""
RM1.20-A — Helpers di visibilità eroi (PURE / NO-OP)
═══════════════════════════════════════════════════════════════════════
Funzioni pure di policy per stabilire se un eroe debba essere mostrato in
catalog/summon/collection/battle_picker dopo l'eventuale soft-deactivation.

CONTRATTO IMPORTANTE:
  • Questo modulo è IMPORT-SAFE e SENZA side-effect.
  • NON è cablato in nessun endpoint runtime in RM1.20-A.
  • Sarà usato in una fase futura (post --apply) per filtrare le query.
  • Tollera DB legacy in cui i flag `is_official` / `is_legacy_placeholder` /
    `obtainable` / `show_in_*` non esistono ancora: in tal caso assume
    visibilità "legacy default = mostrato" per non rompere il runtime.

Tutte le funzioni accettano un `hero` dict (documento heroes nel DB) e
ritornano un boolean. Possono accettare anche un `owned: bool` per le
visibilità di tipo "owned-only".
"""
from __future__ import annotations
from typing import Any, Dict, Optional


# ════════════════════════════════════════════════════════════════════════
# Helpers di lettura tolleranti (default safe per DB pre-migration)
# ════════════════════════════════════════════════════════════════════════

def _flag(hero: Dict[str, Any], key: str, default: Any) -> Any:
    if not isinstance(hero, dict):
        return default
    val = hero.get(key)
    return default if val is None else val


def is_official_hero(hero: Dict[str, Any]) -> bool:
    """True se l'eroe è ufficiale secondo il flag DB. Default: True
    (compat retro: heroes pre-migration considerati official finché non
    marcati esplicitamente legacy)."""
    return bool(_flag(hero, "is_official", True))


def is_legacy_placeholder(hero: Dict[str, Any]) -> bool:
    """True se l'eroe è un placeholder legacy soft-deactivato. Default: False."""
    return bool(_flag(hero, "is_legacy_placeholder", False))


def is_obtainable(hero: Dict[str, Any]) -> bool:
    """True se l'eroe è ottenibile (gacha/quest/event). Default: True."""
    return bool(_flag(hero, "obtainable", True))


# ════════════════════════════════════════════════════════════════════════
# Policy di visibilità (pure)
# ════════════════════════════════════════════════════════════════════════

def should_show_in_catalog(hero: Dict[str, Any], owned: bool = False) -> bool:
    """Catalog/encyclopedia: legacy hidden, official sempre visibile.
    Modalità `show_in_catalog`:
      • True/None  → mostra
      • False      → nascondi
      • "owned_only" → mostra solo se posseduto
    """
    mode = _flag(hero, "show_in_catalog", True)
    if mode == "owned_only":
        return bool(owned)
    return bool(mode)


def should_show_in_summon(hero: Dict[str, Any]) -> bool:
    """Pool gacha: rispetta `show_in_summon` E `obtainable`."""
    if not is_obtainable(hero):
        return False
    mode = _flag(hero, "show_in_summon", True)
    return bool(mode) and mode != "owned_only"


def should_show_in_collection(hero: Dict[str, Any], owned: bool = False) -> bool:
    """Hero collection del giocatore: i legacy posseduti restano visibili.
    Modalità `show_in_hero_collection`:
      • True/None    → mostra
      • False        → nascondi
      • "owned_only" → mostra solo se posseduto (default safe per legacy)
    """
    mode = _flag(hero, "show_in_hero_collection", True)
    if mode == "owned_only":
        return bool(owned)
    return bool(mode)


def should_show_in_battle_picker(hero: Dict[str, Any], owned: bool = False) -> bool:
    """Battle picker: i legacy possono comparire SOLO se posseduti, per
    non rompere active teams che li contengono."""
    mode = _flag(hero, "show_in_battle_picker", True)
    if mode == "owned_only":
        return bool(owned)
    return bool(mode)


__all__ = [
    "is_official_hero",
    "is_legacy_placeholder",
    "is_obtainable",
    "should_show_in_catalog",
    "should_show_in_summon",
    "should_show_in_collection",
    "should_show_in_battle_picker",
]

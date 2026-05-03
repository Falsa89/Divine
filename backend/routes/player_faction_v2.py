"""
Divine Waifus — Player Faction V2 Routes (RM1.24-A)
─────────────────────────────────────────────────────────────────────────
Endpoints separati da V1 `users.faction` (V1 in routes/guild.py invariato).

V2 storage (campo separato — ZERO conflitti con V1):
  - users.player_faction_v2          str | None  (canonical id, es. 'greek')
  - users.player_faction_v2_selected_at  ISO datetime str | None
  - users.player_faction_v2_changed_at   ISO datetime str | None
  - users.player_faction_v2_change_tokens int  (default 1 if missing)

Endpoints:
  - GET  /api/player-factions/v2/all       (public)
  - GET  /api/user/faction-v2/status       (auth)
  - POST /api/user/faction-v2/select       (auth, safe-write)

Regole sicurezza:
  • Nessuna mutazione fuori da `users` (no heroes/user_heroes/teams).
  • V1 `users.faction` mai toccato.
  • Initial select consentito solo se `player_faction_v2` è None.
  • Cambio consentito solo se `player_faction_v2_change_tokens >= 1`.
  • Decremento token e timestamp aggiornati transazionalmente in $set.
  • Nessuna currency spend; nessun monetization gate.
  • Foundation: NESSUN buff applicato in battle (definitions hanno
    `is_enabled=False`).
  • Solo fazioni con `allowed_at_onboarding=True` sono selezionabili
    al lancio.

Read-only by default per UI smoke; il POST richiede payload esplicito
e validation rigorosa.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from data.synergy_definitions_v2 import (
    PLAYER_FACTION_DEFINITIONS_V2,
    PLAYER_FACTION_CHANGE_TOKEN_ID,
)


# ── Visual theme defaults (UI helper, no DB) ────────────────────────────
# Mappa identity_theme → palette frontend-friendly (gold + deep blue base).
# Niente immagini hardcoded: il frontend renderizza con SVG/icone Unicode.
_THEME_VISUALS: Dict[str, Dict[str, str]] = {
    "olympian_glory":      {"crest": "🏛", "primary": "#FFD700", "accent": "#3D5AFE"},
    "ragnarok_fury":       {"crest": "⚔️", "primary": "#FF6B35", "accent": "#1A237E"},
    "nile_solar":          {"crest": "🪶", "primary": "#FFB300", "accent": "#0277BD"},
    "shinto_yokai":        {"crest": "⛩️", "primary": "#E91E63", "accent": "#311B92"},
    "druidic_mists":       {"crest": "🍃", "primary": "#7CB342", "accent": "#1B5E20"},
    "celestial_choir":     {"crest": "✨", "primary": "#FFE082", "accent": "#1976D2"},
    "infernal_pact":       {"crest": "🔥", "primary": "#FF1744", "accent": "#3E2723"},
    "cursed_omens":        {"crest": "🩸", "primary": "#9C27B0", "accent": "#1A0033"},
    "mythic_beasts":       {"crest": "🐉", "primary": "#5D4037", "accent": "#0D47A1"},
    "primordial_chaos":    {"crest": "🌀", "primary": "#26C6DA", "accent": "#311B92"},
    "arcane_magic":        {"crest": "🔮", "primary": "#AB47BC", "accent": "#1A237E"},
    "mesopotamian_primordial": {"crest": "🏺", "primary": "#FBC02D", "accent": "#3E2723"},
    "tides_corsair":       {"crest": "🌊", "primary": "#0288D1", "accent": "#01579B"},
}

_RECOMMENDED_PLAYSTYLE: Dict[str, str] = {
    "greek": "Strategia bilanciata · Magic & Speed",
    "norse": "Aggressivo melee · Penetration",
    "egyptian": "Burst critico · CRIT damage",
    "japanese_yokai": "Combo veloce · Speed/Combo",
    "celtic": "Tank/Evasion · Defense + Dodge",
    "angelic": "Support/Heal · Healing + Magic Defense",
    "demonic": "DPS aggressivo · Attack + Lifesteal",
    "cursed": "Anti-control · Penetration + CC Resist",
}


def _faction_card(d: Dict[str, Any]) -> Dict[str, Any]:
    """Trasforma una definition V2 in una card UI (read-only enrichment)."""
    fid = d.get("id")
    visual = _THEME_VISUALS.get(d.get("identity_theme") or "", {
        "crest": "✦", "primary": "#FFD700", "accent": "#1A237E",
    })
    return {
        "id": fid,
        "display_name": d.get("display_name"),
        "description": d.get("description"),
        "identity_theme": d.get("identity_theme"),
        "allowed_at_onboarding": bool(d.get("allowed_at_onboarding")),
        "is_enabled": bool(d.get("is_enabled")),
        "buff_preview": d.get("buff_preview"),
        "future_event_hooks": list(d.get("future_event_hooks") or []),
        "change_token_id": d.get("change_token_id"),
        "notes": d.get("notes"),
        # UI helpers (read-only, derivati):
        "visual_theme": {
            "crest": visual["crest"],
            "primary_color": visual["primary"],
            "accent_color": visual["accent"],
        },
        "recommended_playstyle": _RECOMMENDED_PLAYSTYLE.get(fid or "", None),
        "category": (
            "onboarding" if d.get("allowed_at_onboarding")
            else "internal_or_future"
        ),
    }


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def register_player_faction_v2_routes(router, db, get_current_user):
    """Registra GET pubbliche + GET status auth + POST select auth."""

    # ── Public list ─────────────────────────────────────────────────────
    @router.get("/player-factions/v2/all")
    async def get_player_factions_v2_all():
        """Lista pubblica di tutte le fazioni player V2.

        Split in due gruppi:
         - onboarding   → selezionabili al lancio (8)
         - internal_or_future → locked/hidden (5)

        NESSUN auth richiesto. NESSUNA mutazione DB.
        """
        all_cards = [_faction_card(d) for d in PLAYER_FACTION_DEFINITIONS_V2]
        onboarding = [c for c in all_cards if c["allowed_at_onboarding"]]
        internal = [c for c in all_cards if not c["allowed_at_onboarding"]]
        return {
            "version": 2,
            "task": "RM1.24-A",
            "total": len(all_cards),
            "onboarding_count": len(onboarding),
            "internal_count": len(internal),
            "onboarding": onboarding,
            "internal_or_future": internal,
            "change_token_id": PLAYER_FACTION_CHANGE_TOKEN_ID,
            "free_change_concept": {
                "default_tokens_on_first_select": 1,
                "monetized": False,
                "notes": "1 cambio gratuito offerto al primo select. Dopo, paid/event token (non implementato).",
            },
            "battle_bonus_active": False,
            "notes": "Foundation read-only. Nessun buff applicato in battle. is_enabled=false su tutte le fazioni V2.",
        }

    # ── Auth status ─────────────────────────────────────────────────────
    @router.get("/user/faction-v2/status")
    async def get_user_faction_v2_status(current_user: dict = Depends(get_current_user)):
        """Stato fazione V2 dell'utente corrente.

        Non interferisce con V1 `users.faction`. Read-only.
        """
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid}, {"_id": 0}) or {}
        selected_id = user.get("player_faction_v2")
        tokens = int(user.get("player_faction_v2_change_tokens", 1))

        selected_card: Optional[Dict[str, Any]] = None
        if selected_id:
            for d in PLAYER_FACTION_DEFINITIONS_V2:
                if d.get("id") == selected_id:
                    selected_card = _faction_card(d)
                    break

        ui_state = (
            "selected" if selected_card
            else "not_selected"
        )
        can_change = bool(selected_card) and tokens >= 1
        can_select_initial = not selected_card

        return {
            "version": 2,
            "user_id": uid,
            "player_faction_v2": selected_id,
            "player_faction_v2_selected_at": user.get("player_faction_v2_selected_at"),
            "player_faction_v2_changed_at": user.get("player_faction_v2_changed_at"),
            "change_tokens": tokens,
            "ui_state": ui_state,
            "can_select_initial": can_select_initial,
            "can_change": can_change,
            "selected_card": selected_card,
            # Esposizione esplicita: la fazione V1 NON è la stessa.
            "v1_faction_legacy": user.get("faction"),
            "v1_faction_locked": bool(user.get("faction_locked", False)),
            "battle_bonus_active": False,
            "notes": "V2 separata da V1. Nessun bonus battle applicato. 1 free change disponibile dopo il primo select.",
        }

    # ── Auth select (safe-write) ───────────────────────────────────────
    class FactionV2SelectRequest(BaseModel):
        faction_id: str = Field(..., min_length=1, max_length=64)
        confirm: bool = Field(True, description="UI confirmation flag (defaults True)")

    @router.post("/user/faction-v2/select")
    async def select_user_faction_v2(
        req: FactionV2SelectRequest,
        current_user: dict = Depends(get_current_user),
    ):
        """Seleziona o cambia la fazione player V2 dell'utente corrente.

        REGOLE:
         - Auth obbligatoria.
         - Solo `allowed_at_onboarding=True` selezionabili.
         - Initial select: consentito se `player_faction_v2` è None.
         - Cambio: richiede `change_tokens >= 1`. Decremento idempotente
           a max(0, tokens-1).
         - NESSUNA currency spend.
         - Mutation set ESCLUSIVAMENTE su campi `player_faction_v2*`
           dentro doc users. ZERO touch su heroes/user_heroes/teams.

        Ritorna: status before/after esplicito per audit.
        """
        if not req.confirm:
            raise HTTPException(400, "Confirmazione UI richiesta")

        # Lookup definition + onboarding gate
        definition = next(
            (d for d in PLAYER_FACTION_DEFINITIONS_V2 if d.get("id") == req.faction_id),
            None,
        )
        if not definition:
            raise HTTPException(404, f"Fazione '{req.faction_id}' non trovata")
        if not definition.get("allowed_at_onboarding"):
            raise HTTPException(
                403,
                f"Fazione '{req.faction_id}' non disponibile al lancio "
                "(internal/future).",
            )

        uid = current_user["id"]
        user = await db.users.find_one({"id": uid}, {"_id": 0})
        if not user:
            raise HTTPException(404, "User non trovato")

        before = {
            "player_faction_v2": user.get("player_faction_v2"),
            "change_tokens": int(user.get("player_faction_v2_change_tokens", 1)),
            "selected_at": user.get("player_faction_v2_selected_at"),
            "changed_at": user.get("player_faction_v2_changed_at"),
        }

        now = _now_iso()

        # ── RM1.24-B: Same-faction reselect → no-op safe ───────────────
        # Se l'utente seleziona di nuovo la fazione che già possiede, NON
        # consumare token e NON aggiornare timestamps. Ritorna success
        # esplicito con action='no_change'. Nessuna mutation DB.
        if (
            before["player_faction_v2"] is not None
            and before["player_faction_v2"] == req.faction_id
        ):
            return {
                "success": True,
                "action": "no_change",
                "before": before,
                "after": before,
                "selected_card": _faction_card(definition),
                "battle_bonus_active": False,
                "notes": (
                    "Stessa fazione già selezionata. Nessuna mutation, "
                    "token cambio invariato."
                ),
                "audit": {
                    "fields_written": [],
                    "collections_touched": [],
                },
            }

        update_set: Dict[str, Any] = {
            "player_faction_v2": req.faction_id,
        }

        if before["player_faction_v2"] is None:
            # Initial select — RM1.24-B: GRATUITO, NON consuma token.
            update_set["player_faction_v2_selected_at"] = now
            # Garantisce 1 token cambio gratuito presente, idempotente
            # (previene drift se field mancante o anomalmente <1).
            current_tokens = before["change_tokens"]
            if (
                "player_faction_v2_change_tokens" not in user
                or current_tokens < 1
            ):
                update_set["player_faction_v2_change_tokens"] = 1
            action = "initial_select"
            tokens_after = update_set.get(
                "player_faction_v2_change_tokens",
                current_tokens,
            )
        else:
            # Change → consuma 1 token (devono essere >=1)
            if before["change_tokens"] < 1:
                raise HTTPException(
                    402,
                    "Nessun token di cambio fazione disponibile. "
                    "Token futuri richiederanno evento/premium (non disponibile).",
                )
            update_set["player_faction_v2_changed_at"] = now
            update_set["player_faction_v2_change_tokens"] = max(
                0, before["change_tokens"] - 1,
            )
            action = "change"
            tokens_after = update_set["player_faction_v2_change_tokens"]

        # Mutation IN-PLACE solo su users.{player_faction_v2*}.
        # NIENTE update su heroes/user_heroes/teams/inventory/wallet.
        await db.users.update_one({"id": uid}, {"$set": update_set})

        # Re-fetch per audit pulito
        updated = await db.users.find_one({"id": uid}, {"_id": 0}) or {}

        return {
            "success": True,
            "action": action,
            "before": before,
            "after": {
                "player_faction_v2": updated.get("player_faction_v2"),
                "change_tokens": int(updated.get("player_faction_v2_change_tokens", tokens_after)),
                "selected_at": updated.get("player_faction_v2_selected_at"),
                "changed_at": updated.get("player_faction_v2_changed_at"),
            },
            "selected_card": _faction_card(definition),
            "battle_bonus_active": False,
            "notes": (
                "V2 selection saved. Nessuna currency spesa. Nessun bonus "
                "battle applicato. V1 users.faction invariato."
            ),
            "audit": {
                "fields_written": list(update_set.keys()),
                "collections_touched": ["users"],
            },
        }

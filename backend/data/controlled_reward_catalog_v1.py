"""Pack 106 — Controlled Reward Catalog v1 (server-side, deterministico).

Tre cataloghi:
  1. MAIL_REWARD_CATALOG_V1 — mail_id → server-side reward.
  2. ACHIEVEMENT_REWARD_CATALOG_V1 — achievement_id → server-side reward.
  3. DAILY_WEEKLY_REWARD_CATALOG_V1 — task_id → {period, server-side reward}.

Tutte le reward sono SERVER-SIDE. Client payload IGNORATO.

Regole rigide:
  * Reward keys ∈ ALLOWED_PACK_106_REWARDS (soft_currencies whitelisted + materials Pack 105).
  * Forbidden: gems, premium, pull tickets, hero/equipment grant.
  * Amount cap conservativo per ciascuna chiave.
  * Catalog non muta cross-server: stesso payload identico per S1, S2, ecc.
"""
from typing import Any, Dict, List, Optional

CATALOG_VERSION = "controlled_reward_catalog_v1.0.0-pack_106"

ALLOWED_PACK_106_REWARDS = {
    # PSP soft_currencies safe
    "mission_coins", "honor",
    # PSP materials introdotti Pack 105
    "steel_ore", "magic_dust", "ancient_relic", "phoenix_feather", "crystal_shard",
}

FORBIDDEN_PACK_106_REWARDS = {
    "gems", "premium_pull", "standard_pull", "stamina", "experience",
    "gold",  # NON in scope Pack 106 — gold non e' tra le source canonicali
}


# ============ MAIL REWARD CATALOG ============
MAIL_REWARD_CATALOG_V1: Dict[str, Dict[str, Any]] = {
    "welcome_pack_mail": {
        "mail_id": "welcome_pack_mail",
        "title": "Benvenuto nel server",
        "body": "Ricevi un pacchetto di benvenuto server-bound.",
        "reward": {
            "soft_currencies": {"mission_coins": 50, "honor": 20},
            "materials": {"steel_ore": 5},
        },
    },
    "server_event_announce_mail": {
        "mail_id": "server_event_announce_mail",
        "title": "Annuncio Evento Server",
        "body": "Premio commemorativo server-bound per gli annunci.",
        "reward": {
            "soft_currencies": {"honor": 30},
            "materials": {"magic_dust": 3, "crystal_shard": 1},
        },
    },
}


# ============ ACHIEVEMENT REWARD CATALOG ============
ACHIEVEMENT_REWARD_CATALOG_V1: Dict[str, Dict[str, Any]] = {
    "first_login_achievement": {
        "achievement_id": "first_login_achievement",
        "title": "Primo Accesso",
        "description": "Hai effettuato il primo accesso al server.",
        "reward": {
            "soft_currencies": {"mission_coins": 30, "honor": 10},
            "materials": {},
        },
    },
    "first_battle_achievement": {
        "achievement_id": "first_battle_achievement",
        "title": "Prima Battaglia",
        "description": "Hai completato la prima battaglia sul server.",
        "reward": {
            "soft_currencies": {"mission_coins": 50},
            "materials": {"steel_ore": 3, "magic_dust": 1},
        },
    },
}


# ============ DAILY / WEEKLY REWARD CATALOG ============
DAILY_WEEKLY_REWARD_CATALOG_V1: Dict[str, Dict[str, Any]] = {
    "daily_login_reward_task": {
        "task_id": "daily_login_reward_task",
        "period": "daily",  # UTC day
        "title": "Accesso Quotidiano",
        "reward": {
            "soft_currencies": {"mission_coins": 15, "honor": 5},
            "materials": {},
        },
    },
    "daily_battle_task": {
        "task_id": "daily_battle_task",
        "period": "daily",
        "title": "Battaglia Quotidiana",
        "reward": {
            "soft_currencies": {"mission_coins": 25, "honor": 10},
            "materials": {"steel_ore": 1},
        },
    },
    "weekly_consistency_task": {
        "task_id": "weekly_consistency_task",
        "period": "weekly",  # UTC ISO week
        "title": "Costanza Settimanale",
        "reward": {
            "soft_currencies": {"mission_coins": 100, "honor": 50},
            "materials": {"magic_dust": 5, "crystal_shard": 2},
        },
    },
}


def get_mail_reward(mail_id: str) -> Optional[Dict[str, Any]]:
    m = MAIL_REWARD_CATALOG_V1.get(mail_id)
    if not m:
        return None
    return {
        "mail_id": m["mail_id"], "title": m["title"], "body": m["body"],
        "reward": {
            "soft_currencies": dict(m["reward"]["soft_currencies"]),
            "materials": dict(m["reward"]["materials"]),
        },
    }


def get_achievement_reward(achievement_id: str) -> Optional[Dict[str, Any]]:
    a = ACHIEVEMENT_REWARD_CATALOG_V1.get(achievement_id)
    if not a:
        return None
    return {
        "achievement_id": a["achievement_id"], "title": a["title"], "description": a["description"],
        "reward": {
            "soft_currencies": dict(a["reward"]["soft_currencies"]),
            "materials": dict(a["reward"]["materials"]),
        },
    }


def get_daily_weekly_task(task_id: str) -> Optional[Dict[str, Any]]:
    t = DAILY_WEEKLY_REWARD_CATALOG_V1.get(task_id)
    if not t:
        return None
    return {
        "task_id": t["task_id"], "period": t["period"], "title": t["title"],
        "reward": {
            "soft_currencies": dict(t["reward"]["soft_currencies"]),
            "materials": dict(t["reward"]["materials"]),
        },
    }


def list_catalog_summary() -> Dict[str, Any]:
    return {
        "mail_rewards": [get_mail_reward(k) for k in MAIL_REWARD_CATALOG_V1.keys()],
        "achievement_rewards": [get_achievement_reward(k) for k in ACHIEVEMENT_REWARD_CATALOG_V1.keys()],
        "daily_weekly_tasks": [get_daily_weekly_task(k) for k in DAILY_WEEKLY_REWARD_CATALOG_V1.keys()],
    }


def _validate_catalog_on_import() -> None:
    """Validazione bloccante al load time."""
    def _check_reward(label: str, reward: Dict[str, Any]) -> None:
        for k, v in reward.get("soft_currencies", {}).items():
            assert k in ALLOWED_PACK_106_REWARDS, f"{label} forbidden soft: {k}"
            assert k not in FORBIDDEN_PACK_106_REWARDS, f"{label} forbidden soft: {k}"
            assert isinstance(v, int) and 0 < v <= 500, f"{label} soft amount oob: {k}={v}"
        for k, v in reward.get("materials", {}).items():
            assert k in ALLOWED_PACK_106_REWARDS, f"{label} forbidden material: {k}"
            assert k not in FORBIDDEN_PACK_106_REWARDS, f"{label} forbidden material: {k}"
            assert isinstance(v, int) and 0 < v <= 50, f"{label} material amount oob: {k}={v}"
    for mid, m in MAIL_REWARD_CATALOG_V1.items():
        assert mid == m["mail_id"]
        _check_reward(f"mail.{mid}", m["reward"])
    for aid, a in ACHIEVEMENT_REWARD_CATALOG_V1.items():
        assert aid == a["achievement_id"]
        _check_reward(f"achievement.{aid}", a["reward"])
    for tid, t in DAILY_WEEKLY_REWARD_CATALOG_V1.items():
        assert tid == t["task_id"]
        assert t["period"] in ("daily", "weekly")
        _check_reward(f"task.{tid}", t["reward"])


_validate_catalog_on_import()


__all__ = [
    "CATALOG_VERSION", "ALLOWED_PACK_106_REWARDS", "FORBIDDEN_PACK_106_REWARDS",
    "MAIL_REWARD_CATALOG_V1", "ACHIEVEMENT_REWARD_CATALOG_V1", "DAILY_WEEKLY_REWARD_CATALOG_V1",
    "get_mail_reward", "get_achievement_reward", "get_daily_weekly_task",
    "list_catalog_summary",
]
